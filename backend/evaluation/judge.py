import asyncio

from opentelemetry import trace

from backend.providers.client import NeuroFlowClient

from backend.evaluation.metrics.faithfulness import (
    FaithfulnessEvaluator,
)

from backend.evaluation.metrics.answer_relevance import (
    AnswerRelevanceEvaluator,
)

from backend.evaluation.metrics.context_precision import (
    ContextPrecisionEvaluator,
)

from backend.evaluation.metrics.context_recall import (
    ContextRecallEvaluator,
)

from backend.repositories.evaluation_repository import (
    EvaluationRepository,
)

from backend.repositories.training_pair_repository import (
    TrainingPairRepository,
)


class EvaluationJudge:
    """
    Runs all evaluation metrics and stores the result.
    """

    def __init__(
        self,
        client: NeuroFlowClient,
    ):

        self.client = client

        self.faithfulness = FaithfulnessEvaluator(client)

        self.answer_relevance = AnswerRelevanceEvaluator(client)

        self.context_precision = ContextPrecisionEvaluator(client)

        self.context_recall = ContextRecallEvaluator(client)

        self.evaluations = EvaluationRepository()

        self.training_pairs = TrainingPairRepository()

        self.tracer = trace.get_tracer("neuroflow")

    async def evaluate(
        self,
        run_id,
        query,
        answer,
        context,
    ):

        print("\n" + "=" * 70)
        print("STARTING EVALUATION")
        print("=" * 70)
        print("Run ID:", run_id)

        with self.tracer.start_as_current_span(
            "evaluation.judge"
        ) as span:

            (
                faithfulness,
                answer_relevance,
                context_precision,
                context_recall,
            ) = await asyncio.gather(

                self.faithfulness.evaluate(
                    query,
                    answer,
                    context,
                ),

                self.answer_relevance.evaluate(
                    query,
                    answer,
                ),

                self.context_precision.evaluate(
                    query,
                    answer,
                    context,
                ),

                self.context_recall.evaluate(
                    query,
                    answer,
                    context,
                ),
            )

            overall = (
                0.35 * faithfulness
                + 0.30 * answer_relevance
                + 0.20 * context_precision
                + 0.15 * context_recall
            )

            print("\nEvaluation Scores")
            print("-" * 70)
            print(f"Faithfulness      : {faithfulness}")
            print(f"Answer Relevance  : {answer_relevance}")
            print(f"Context Precision : {context_precision}")
            print(f"Context Recall    : {context_recall}")
            print(f"Overall Score     : {overall}")
            print("-" * 70)

            span.set_attribute(
                "faithfulness",
                faithfulness,
            )

            span.set_attribute(
                "answer_relevance",
                answer_relevance,
            )

            span.set_attribute(
                "context_precision",
                context_precision,
            )

            span.set_attribute(
                "context_recall",
                context_recall,
            )

            span.set_attribute(
                "overall_score",
                overall,
            )

            print("\nSaving evaluation to database...")

            await self.evaluations.create_evaluation(
                run_id=run_id,
                faithfulness=faithfulness,
                answer_relevance=answer_relevance,
                context_precision=context_precision,
                context_recall=context_recall,
                overall_score=overall,
                judge_model="evaluation-model",
            )

            print("Evaluation saved successfully.")

            if overall >= 0.80:

                print("\nOverall >= 0.80")
                print("Creating training pair...")

                try:

                    await self.training_pairs.create(
                        run_id=run_id,
                        system_prompt=context,
                        user_message=query,
                        assistant_message=answer,
                        quality_score=overall,
                    )

                    print("Training pair created successfully!")

                except Exception as e:

                    print("\nFAILED TO CREATE TRAINING PAIR")
                    print(type(e).__name__)
                    print(e)

            else:

                print(
                    f"\nOverall score ({overall:.3f}) is below 0.80."
                )
                print("Training pair NOT created.")

            print("=" * 70)
            print("EVALUATION FINISHED")
            print("=" * 70)

            return {
                "faithfulness": faithfulness,
                "answer_relevance": answer_relevance,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "overall_score": overall,
            }