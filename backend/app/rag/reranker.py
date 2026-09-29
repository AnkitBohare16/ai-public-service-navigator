from typing import Any


class Reranker:
    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0"
            )

        query_terms = self._normalize(query)

        scored_results = []

        for result in results:
            content_terms = self._normalize(
                result["content"]
            )

            overlap = len(
                query_terms.intersection(content_terms)
            )

            vector_similarity = float(
                result.get("similarity", 0.0)
            )

            # Vector similarity remains the primary signal.
            # Keyword overlap provides a lightweight
            # relevance adjustment.
            rerank_score = (
                vector_similarity
                + (0.05 * overlap)
            )

            reranked_result = dict(result)
            reranked_result["rerank_score"] = rerank_score

            scored_results.append(reranked_result)

        scored_results.sort(
            key=lambda result: result["rerank_score"],
            reverse=True,
        )

        return scored_results[:top_k]

    def _normalize(self, text: str) -> set[str]:
        return {
            word.strip(".,!?;:()[]{}\"'")
            for word in text.lower().split()
            if word.strip(".,!?;:()[]{}\"'")
        }