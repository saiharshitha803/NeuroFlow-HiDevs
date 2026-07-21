import asyncio
import time
from uuid import UUID

from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria

from backend.generation.prompt_builder import PromptBuilder
from backend.generation.citations import CitationParser

from backend.repositories.pipeline_run_repository import (
    PipelineRunRepository,
)

from backend.queue.evaluation_queue import (
    enqueue_evaluation,
)


class Generator:
    """
    LLM-backed response generator.
    """

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

        self.prompt_builder = PromptBuilder()

        self.citation_parser = CitationParser()

        self.pipeline_runs = PipelineRunRepository()

    async def generate(
        self,
        question: str,
        context: str,
        sources: list,
        pipeline_id: UUID | None = None,
        query_type: str = "factual",
    ) -> dict:

        messages = self.prompt_builder.build_messages(
            query=question,
            context=context,
            query_type=query_type,
        )

        prompt = "\n\n".join(
            message.content
            for message in messages
        )

        run_id = await self.pipeline_runs.create_run(
            pipeline_id=pipeline_id,
            query=question,
            prompt=prompt,
            retrieved_chunk_ids=[
                source["chunk_id"]
                for source in sources
            ],
        )

        start = time.perf_counter()

        try:

            result = await self.client.chat(
                messages=messages,
                routing_criteria=RoutingCriteria(
                    task_type="generation",
                ),
            )

            latency = (
                time.perf_counter()
                - start
            ) * 1000

            citations = self.citation_parser.parse(
                result.content,
                sources,
            )

            await self.pipeline_runs.update_run(
                run_id,
                generation=result.content,
                latency_ms=int(latency),
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                model_used=result.model,
                status="complete",
            )

            asyncio.create_task(
                enqueue_evaluation(run_id)
            )

            return {
                "run_id": str(run_id),
                "answer": result.content,
                "citations": citations,
            }

        except Exception:

            await self.pipeline_runs.update_run(
                run_id,
                status="failed",
            )

            raise

    async def stream_generate(
        self,
        question: str,
        context: str,
        sources: list,
        query_type: str = "factual",
        pipeline_id: UUID | None = None,
    ):
        """
        Stream the response token-by-token.
        """

        messages = self.prompt_builder.build_messages(
            query=question,
            context=context,
            query_type=query_type,
        )

        prompt = "\n\n".join(
            message.content
            for message in messages
        )

        run_id = await self.pipeline_runs.create_run(
            pipeline_id=pipeline_id,
            query=question,
            prompt=prompt,
            retrieved_chunk_ids=[
                s["chunk_id"]
                for s in sources
            ],
        )

        start = time.perf_counter()

        full_response = ""

        try:

            async for token in self.client.stream(
                messages=messages,
                routing_criteria=RoutingCriteria(
                    task_type="generation",
                ),
            ):

                full_response += token

                yield {
                    "type": "token",
                    "delta": token,
                }

            latency = (
                time.perf_counter()
                - start
            ) * 1000

            citations = self.citation_parser.parse(
                full_response,
                sources,
            )

            await self.pipeline_runs.update_run(
                run_id,
                generation=full_response,
                latency_ms=int(latency),
                status="complete",
            )

            asyncio.create_task(
                enqueue_evaluation(run_id)
            )

            yield {
                "type": "done",
                "run_id": str(run_id),
                "citations": citations,
            }

        except Exception:

            await self.pipeline_runs.update_run(
                run_id,
                status="failed",
            )

            raise