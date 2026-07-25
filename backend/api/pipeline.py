import traceback

from fastapi import APIRouter, HTTPException
from uuid import UUID
from backend.repositories.pipeline_repository import PipelineRepository
from backend.schemas.pipeline_config import PipelineConfig

router = APIRouter(
    prefix="/pipelines",
    tags=["Pipelines"],
)

repository = PipelineRepository()


@router.post("/")
async def create_pipeline(
    config: PipelineConfig,
):
    """
    Create a new pipeline.
    """

    try:

        print("=" * 60)
        print("CREATE PIPELINE REQUEST")
        print("=" * 60)
        print("Name:", config.name)
        print("Description:", config.description)
        print("Config:")
        print(config.model_dump())
        print("=" * 60)

        pipeline_id = await repository.create_pipeline(
            name=config.name,
            description=config.description,
            config=config.model_dump(),
        )

        return {
            "pipeline_id": str(pipeline_id),
            "message": "Pipeline created successfully.",
        }

    except Exception as e:

        print("\n")
        print("=" * 60)
        print("CREATE PIPELINE FAILED")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
@router.get("/")
async def list_pipelines():
    """
    List all pipelines.
    """

    pipelines = await repository.list_pipelines()

    return [
        {
            "id": str(p["id"]),
            "name": p["name"],
            "description": p["description"],
            "version": p["version"],
            "status": p["status"],
            "created_at": p["created_at"],
        }
        for p in pipelines
    ]

@router.get("/{pipeline_id}")
async def get_pipeline(
    pipeline_id: UUID,
):
    """
    Get a single pipeline.
    """

    pipeline = await repository.get_pipeline(
        pipeline_id,
    )

    if pipeline is None:
        raise HTTPException(
            status_code=404,
            detail="Pipeline not found.",
        )

    return {
        "id": str(pipeline["id"]),
        "name": pipeline["name"],
        "description": pipeline["description"],
        "config": pipeline["config"],
        "version": pipeline["version"],
        "status": pipeline["status"],
        "created_at": pipeline["created_at"],
        "updated_at": pipeline["updated_at"],
    }


@router.patch("/{pipeline_id}")
async def update_pipeline(
    pipeline_id: UUID,
    config: PipelineConfig,
):
    try:
        new_pipeline_id = await repository.update_pipeline(
            pipeline_id=pipeline_id,
            config=config.model_dump(),
        )

        return {
            "new_pipeline_id": str(new_pipeline_id),
            "message": "New pipeline version created.",
        }

    except Exception as e:
        traceback.print_exc()      # <-- add this
        print(e)                   # <-- add this

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.delete("/{pipeline_id}")
async def archive_pipeline(
    pipeline_id: UUID,
):
    """
    Archive a pipeline.
    """

    try:
        await repository.archive_pipeline(
            pipeline_id,
        )

        return {
            "message": "Pipeline archived successfully.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )