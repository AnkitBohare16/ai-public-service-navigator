import pytest

from app.services.reliability_service import ReliabilityService


def test_high_reliability_for_official_fresh_strong_evidence():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.90,
        }
    ]

    citations = [
        {
            "chunk_id": "chunk-1",
            "is_official": True,
            "freshness_status": "fresh",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "high"
    assert result["score"] == 1.0


def test_medium_reliability_for_aging_evidence():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.75,
        }
    ]

    citations = [
        {
            "chunk_id": "chunk-1",
            "is_official": True,
            "freshness_status": "aging",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "high"
    assert result["score"] == 0.9


def test_stale_evidence_reduces_reliability():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.75,
        }
    ]

    citations = [
        {
            "chunk_id": "chunk-1",
            "is_official": True,
            "freshness_status": "stale",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "medium"
    assert result["score"] == 0.75


def test_non_official_source_reduces_reliability():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.80,
        }
    ]

    citations = [
        {
            "chunk_id": "chunk-1",
            "is_official": False,
            "freshness_status": "fresh",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "high"
    assert result["score"] == 0.9


def test_low_similarity_evidence_is_not_reliable():
    service = ReliabilityService(
        minimum_similarity=0.70,
    )

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.50,
        }
    ]

    citations = [
        {
            "chunk_id": "chunk-1",
            "is_official": True,
            "freshness_status": "fresh",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "low"
    assert result["score"] == 0.0


def test_missing_evidence_returns_low_reliability():
    service = ReliabilityService()

    result = service.evaluate(
        evidence=[],
        citations=[],
    )

    assert result["status"] == "low"
    assert result["score"] == 0.0


def test_missing_citations_returns_low_reliability():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.90,
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=[],
    )

    assert result["status"] == "low"
    assert result["score"] == 0.0


def test_missing_citation_for_evidence_returns_low_reliability():
    service = ReliabilityService()

    evidence = [
        {
            "chunk_id": "chunk-1",
            "similarity": 0.90,
        }
    ]

    citations = [
        {
            "chunk_id": "different-chunk",
            "is_official": True,
            "freshness_status": "fresh",
        }
    ]

    result = service.evaluate(
        evidence=evidence,
        citations=citations,
    )

    assert result["status"] == "low"
    assert result["score"] == 0.0


def test_invalid_similarity_threshold_is_rejected():
    with pytest.raises(ValueError):
        ReliabilityService(
            minimum_similarity=1.5,
        )