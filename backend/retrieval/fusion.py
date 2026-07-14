from collections import defaultdict


def reciprocal_rank_fusion(
    result_lists,
    k: int = 60
):
    """
    Reciprocal Rank Fusion.

    Formula:

        RRF score = Σ 1 / (k + rank)

    Chunks appearing in multiple retrieval
    strategies get boosted.
    """

    scores = defaultdict(float)

    documents = {}


    for results in result_lists:

        for rank, result in enumerate(
            results,
            start=1
        ):

            chunk_id = result.chunk_id


            scores[chunk_id] += (
                1 / (k + rank)
            )


            documents[chunk_id] = result



    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


    final_results = []


    for chunk_id, score in ranked:

        item = documents[chunk_id]

        item.score = score

        final_results.append(
            item
        )


    return final_results