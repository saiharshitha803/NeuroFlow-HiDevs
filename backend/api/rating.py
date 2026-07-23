from uuid import UUID

from fastapi import APIRouter

from pydantic import BaseModel, Field

from backend.repositories.evaluation_repository import (
    EvaluationRepository,
)


router = APIRouter(
    tags=["Evaluation"],
)


repo = EvaluationRepository()


class RatingRequest(BaseModel):

    rating: int = Field(
        ge=1,
        le=5,
    )


@router.patch("/runs/{run_id}/rating")
async def rate_run(
    run_id: UUID,
    body: RatingRequest,
):

    await repo.update_user_rating(
        run_id,
        body.rating,
    )

    return {
        "message": "Rating updated."
    }