from fastapi import APIRouter
from pydantic import BaseModel

from backend.pipeline.rag_pipeline import RAGPipeline
from backend.retrieval.retriever import Retriever
from backend.generation.generator import Generator

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


rag_pipeline = RAGPipeline(
    retriever=Retriever(),
    generator=Generator(),
)


@router.post("/query")
async def query(request: QueryRequest):
    result = await rag_pipeline.run(request.question)
    return result