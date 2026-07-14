from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


from backend.pipeline.rag_pipeline import RAGPipeline



router = APIRouter(
    prefix="/api",
    tags=["Query"]
)



class QueryRequest(BaseModel):
    """
    User query payload.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="Question to ask NeuroFlow"
    )



class QueryResponse(BaseModel):

    query: str

    answer: str

    sources: list

    retrieved_chunks: int

    latency_ms: float




# Single pipeline instance

rag_pipeline = RAGPipeline()



@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query(
    request: QueryRequest,
):


    try:

        result = await rag_pipeline.run(
            query=request.question
        )


        return result



    except Exception as e:


        raise HTTPException(
            status_code=500,
            detail=str(e),
        )