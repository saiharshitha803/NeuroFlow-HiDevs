import uuid
import pytest

from backend.database.connection import db
from backend.database.pipeline_repository import PipelineRepository
from backend.database.pipeline_run_repository import PipelineRunRepository


@pytest.mark.asyncio
async def test_pipeline_run_repository():

    await db.connect()

    pipeline_repo = PipelineRepository()
    run_repo = PipelineRunRepository()

    pipeline_id = await pipeline_repo.create(
        name=f"pipeline-{uuid.uuid4()}",
        config={"chunk_size": 512},
    )

    run_id = await run_repo.create(
        pipeline_id=pipeline_id,
        query="What is NeuroFlow?",
    )

    run = await run_repo.get(run_id)

    assert run is not None
    assert run["query"] == "What is NeuroFlow?"

    runs = await run_repo.list()

    assert len(runs) >= 1

    await run_repo.update_status(
        run_id,
        "completed",
    )

    updated = await run_repo.get(run_id)

    assert updated["status"] == "completed"

    await run_repo.delete(run_id)

    deleted = await run_repo.get(run_id)

    assert deleted is None

    await pipeline_repo.delete(pipeline_id)

    await db.disconnect()