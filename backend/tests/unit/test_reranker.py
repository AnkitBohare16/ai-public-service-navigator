import pytest

from app.rag.reranker import Reranker


def test_reranker_prioritizes_keyword_overlap():
    reranker = Reranker()

    results = [
        {
            "content": "The application can be submitted online.",
            "similarity": 0.85,
        },
        {
            "content": (
                "Proof of address documents are required "
                "for the application."
            ),
            "similarity": 0.82,
        },
    ]

    reranked = reranker.rerank(
        query="What documents are required?",
        results=results,
        top_k=2,
    )

    assert (
        reranked[0]["content"]
        == (
            "Proof of address documents are required "
            "for the application."
        )
    )


def test_reranker_preserves_similarity_score():
    reranker = Reranker()

    results = [
        {
            "content": "Application fee information.",
            "similarity": 0.91,
        },
    ]

    reranked = reranker.rerank(
        query="application fee",
        results=results,
        top_k=1,
    )

    assert reranked[0]["similarity"] == 0.91
    assert "rerank_score" in reranked[0]


def test_reranker_respects_top_k():
    reranker = Reranker()

    results = [
        {
            "content": f"Document {index}",
            "similarity": 0.5,
        }
        for index in range(5)
    ]

    reranked = reranker.rerank(
        query="document",
        results=results,
        top_k=2,
    )

    assert len(reranked) == 2


def test_reranker_rejects_empty_query():
    reranker = Reranker()

    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        reranker.rerank(
            query="   ",
            results=[],
        )


def test_reranker_rejects_invalid_top_k():
    reranker = Reranker()

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0",
    ):
        reranker.rerank(
            query="address",
            results=[],
            top_k=0,
        )