import uuid
import pytest

from backend.database.connection import db
from backend.database.pipeline_repository import PipelineRepository
from backend.database.pipeline_run_repository import PipelineRunRepository
from backend.database.evaluation_repository import EvaluationRepository


@pytest.mark.asyncio
async def test_evaluation_repository():

    await db.connect()

    pipeline_repo = PipelineRepository()
    run_repo = PipelineRunRepository()
    evaluation_repo = EvaluationRepository()

    pipeline_id = await pipeline_repo.create(
        name=f"pipeline-{uuid.uuid4()}",
        config={"chunk_size": 512},
    )

    run_id = await run_repo.create(
        pipeline_id=pipeline_id,
        query="What is NeuroFlow?",
    )

    evaluation_id = await evaluation_repo.create(
        run_id=run_id,
        faithfulness=0.90,
        answer_relevance=0.88,
        context_precision=0.91,
        context_recall=0.87,
        overall_score=0.89,
        judge_model="gpt-4o",
        user_rating=5,
    )

    evaluation = await evaluation_repo.get(evaluation_id)

    assert evaluation is not None
    assert evaluation["judge_model"] == "gpt-4o"

    evaluations = await evaluation_repo.list()

    assert len(evaluations) >= 1

    await evaluation_repo.delete(evaluation_id)

    deleted = await evaluation_repo.get(evaluation_id)

    assert deleted is None

    await run_repo.delete(run_id)
    await pipeline_repo.delete(pipeline_id)

    await db.disconnect()