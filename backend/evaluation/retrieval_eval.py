import asyncio
import json
from pathlib import Path

from backend.database.connection import db
from backend.retrieval.retriever import Retriever


# ==========================================================
# Retrieval Evaluation Dataset
# ==========================================================

TEST_SET = [

    {
        "query": "What is HNSW indexing?",
        "relevant_chunk_ids": [
            "b568de47-3ee1-4b61-8dc2-1bf00f1ebea9"
        ]
    },

    {
        "query": "Explain hierarchical navigable small world algorithm",
        "relevant_chunk_ids": [
            "b568de47-3ee1-4b61-8dc2-1bf00f1ebea9"
        ]
    },

    {
        "query": "How does transformer attention work?",
        "relevant_chunk_ids": [
            "701be48f-612c-406c-a7d3-a0af9bcf3295"
        ]
    },

    {
        "query": "What are attention weights?",
        "relevant_chunk_ids": [
            "701be48f-612c-406c-a7d3-a0af9bcf3295"
        ]
    },

    {
        "query": "What are vector embeddings?",
        "relevant_chunk_ids": [
            "3aec4f87-47e2-4e4e-8d18-c252db288c6f"
        ]
    },

    {
        "query": "How are embeddings used in semantic search?",
        "relevant_chunk_ids": [
            "3aec4f87-47e2-4e4e-8d18-c252db288c6f"
        ]
    },

]



# ==========================================================
# Evaluation Function
# ==========================================================

async def evaluate_retrieval():

    print("Starting retrieval evaluation...\n")


    await db.connect()


    retriever = Retriever()


    total_queries = len(TEST_SET)

    hits = 0

    reciprocal_rank_sum = 0


    evaluation_details = []


    for item in TEST_SET:


        query = item["query"]

        relevant_ids = item["relevant_chunk_ids"]


        print(
            f"Query: {query}"
        )


        results = await retriever.retrieve(
            query=query,
            top_k=10
        )


        retrieved_ids = []


        for result in results:


            if isinstance(result, dict):

                retrieved_ids.append(
                    str(result["id"])
                )

            else:

                retrieved_ids.append(
                    str(result.chunk_id)
                )



        hit = False

        rank = None



        for index, chunk_id in enumerate(
            retrieved_ids,
            start=1
        ):

            if chunk_id in relevant_ids:

                hit = True

                rank = index


                reciprocal_rank_sum += (
                    1 / index
                )

                break



        if hit:

            hits += 1



        evaluation_details.append(
            {
                "query": query,

                "hit": hit,

                "rank": rank,

                "retrieved_chunk_ids": retrieved_ids
            }
        )



    hit_rate = (
        hits / total_queries
        if total_queries
        else 0
    )


    mrr = (
        reciprocal_rank_sum / total_queries
        if total_queries
        else 0
    )



    final_result = {


        "total_queries": total_queries,


        "hits": hits,


        "hit_rate": round(
            hit_rate,
            4
        ),


        "mrr": round(
            mrr,
            4
        ),


        "details": evaluation_details

    }



    # Save evaluation result

    output_path = Path(
        "backend/evaluation/retrieval_results.json"
    )


    output_path.write_text(
        json.dumps(
            final_result,
            indent=4
        )
    )



    print("\n============================")
    print("Retrieval Evaluation Result")
    print("============================")


    print(
        json.dumps(
            final_result,
            indent=4
        )
    )



    await db.disconnect()



# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    asyncio.run(
        evaluate_retrieval()
    )