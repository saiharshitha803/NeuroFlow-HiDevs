import uuid

import pytest

from backend.database.connection import db
from backend.database.pipeline_repository import PipelineRepository


@pytest.mark.asyncio
async def test_pipeline_repository():

    await db.connect()

    repo = PipelineRepository()

    name = f"pipeline-{uuid.uuid4()}"

    pipeline_id = await repo.create(
        name=name,
        config={"chunk_size": 512},
    )

    pipeline = await repo.get(pipeline_id)

    assert pipeline is not None
    assert pipeline["name"] == name

    pipelines = await repo.list()

    assert len(pipelines) >= 1

    await repo.delete(pipeline_id)

    deleted = await repo.get(pipeline_id)

    assert deleted is None

    await db.disconnect()