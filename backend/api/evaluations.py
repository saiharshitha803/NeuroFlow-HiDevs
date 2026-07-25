from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.repositories.evaluation_repository import EvaluationRepository
from backend.schemas.evaluation import (
    EvaluationCreate,
    RatingUpdate,
    MetadataUpdate,
)

router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
)

repository = EvaluationRepository()


@router.post("/")
async def create_evaluation(
    evaluation: EvaluationCreate,
):
    """
    Create an evaluation.
    """

    try:

        await repository.create_evaluation(
            run_id=evaluation.run_id,
            faithfulness=evaluation.faithfulness,
            answer_relevance=evaluation.answer_relevance,
            context_precision=evaluation.context_precision,
            context_recall=evaluation.context_recall,
            overall_score=evaluation.overall_score,
            judge_model=evaluation.judge_model,
        )

        return {
            "message": "Evaluation created successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{run_id}")
async def get_evaluation(
    run_id: UUID,
):
    """
    Get evaluation by run ID.
    """

    evaluation = await repository.get_evaluation(run_id)

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found.",
        )

    return evaluation


@router.patch("/{run_id}/rating")
async def update_rating(
    run_id: UUID,
    rating: RatingUpdate,
):
    """
    Update user rating.
    """

    try:

        await repository.update_user_rating(
            run_id,
            rating.rating,
        )

        return {
            "message": "Rating updated successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.patch("/{run_id}/metadata")
async def update_metadata(
    run_id: UUID,
    metadata: MetadataUpdate,
):
    """
    Update evaluation metadata.
    """

    try:

        await repository.update_metadata(
            run_id,
            metadata.metadata,
        )

        return {
            "message": "Metadata updated successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )