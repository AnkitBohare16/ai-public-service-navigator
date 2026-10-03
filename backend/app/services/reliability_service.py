class ReliabilityService:
    """
    Evaluates the reliability of retrieved evidence using
    source authority, retrieval similarity, and freshness.
    """

    def __init__(
        self,
        minimum_similarity: float = 0.65,
    ):
        if not 0.0 <= minimum_similarity <= 1.0:
            raise ValueError(
                "minimum_similarity must be between 0 and 1"
            )

        self.minimum_similarity = minimum_similarity

    def evaluate(
        self,
        evidence: list[dict],
        citations: list[dict],
    ) -> dict:
        """
        Evaluate the reliability of retrieved evidence.

        Returns:
        - status
        - score
        - reason
        """

        if not evidence:
            return {
                "status": "low",
                "score": 0.0,
                "reason": "No supporting evidence was retrieved.",
            }

        if not citations:
            return {
                "status": "low",
                "score": 0.0,
                "reason": "No source citations are available.",
            }

        citation_by_chunk = {
            citation["chunk_id"]: citation
            for citation in citations
        }

        scores = []

        for item in evidence:
            citation = citation_by_chunk.get(item["chunk_id"])

            if citation is None:
                continue

            similarity = float(item["similarity"])

            if similarity < self.minimum_similarity:
                continue

            score = similarity

            if citation["is_official"]:
                score += 0.10

            freshness_status = citation["freshness_status"]

            if freshness_status == "fresh":
                score += 0.10
            elif freshness_status == "aging":
                score += 0.05
            elif freshness_status == "stale":
                score -= 0.10

            scores.append(
                min(max(score, 0.0), 1.0)
            )

        if not scores:
            return {
                "status": "low",
                "score": 0.0,
                "reason": (
                    "Retrieved evidence does not meet "
                    "the reliability threshold."
                ),
            }

        average_score = sum(scores) / len(scores)

        if average_score >= 0.85:
            status = "high"
        elif average_score >= 0.70:
            status = "medium"
        else:
            status = "low"

        return {
            "status": status,
            "score": round(average_score, 3),
            "reason": (
                "Reliability is based on source authority, "
                "retrieval similarity, and source freshness."
            ),
        }