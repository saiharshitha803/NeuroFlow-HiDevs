from typing import Any

from pydantic import BaseModel
from uuid import UUID


class EvaluationCreate(BaseModel):
    run_id: UUID
    faithfulness: float
    answer_relevance: float
    context_precision: float
    context_recall: float
    overall_score: float
    judge_model: str


class RatingUpdate(BaseModel):
    rating: int


class MetadataUpdate(BaseModel):
    metadata: dict[str, Any]