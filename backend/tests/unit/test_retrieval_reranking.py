from unittest.mock import Mock

from app.rag.reranker import Reranker


def test_reranker_can_change_result_order():
    reranker = Reranker()

    results = [
        {
            "chunk_id": "1",
            "document_version_id": "version-1",
            "content": (
                "The application can be submitted online."
            ),
            "similarity": 0.90,
        },
        {
            "chunk_id": "2",
            "document_version_id": "version-1",
            "content": (
                "Proof of address documents are required "
                "for this application."
            ),
            "similarity": 0.84,
        },
    ]

    reranked = reranker.rerank(
        query="What documents are required?",
        results=results,
        top_k=2,
    )

    assert reranked[0]["chunk_id"] == "2"
    assert reranked[1]["chunk_id"] == "1"

    assert (
        reranked[0]["rerank_score"]
        > reranked[1]["rerank_score"]
    )