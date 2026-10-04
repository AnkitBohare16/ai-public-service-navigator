import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.citation_service import CitationService
from app.services.reliability_service import ReliabilityService
from app.services.retrieval_service import RetrievalService

from tests.evaluation.test_cases import EVALUATION_CASES

EVALUATION_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5432/"
    "public_service_navigator"
)

evaluation_engine = create_engine(
    EVALUATION_DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
    ),
    pool_pre_ping=True,
)

EvaluationSessionLocal = sessionmaker(
    bind=evaluation_engine,
    autoflush=False,
    autocommit=False,
)

SUPPORTED_CASES = [
    case
    for case in EVALUATION_CASES
    if case["expected_behavior"] == "supported"
]

UNSUPPORTED_CASES = [
    case
    for case in EVALUATION_CASES
    if case["expected_behavior"] == "unsupported"
]


@pytest.mark.parametrize("case", SUPPORTED_CASES, ids=lambda case: case["id"])
def test_supported_questions_meet_reliability_threshold(case):
    db = EvaluationSessionLocal()

    try:
        retrieval_service = RetrievalService(db)
        citation_service = CitationService(db)
        reliability_service = ReliabilityService()

        evidence = retrieval_service.search(
            query=case["query"],
            top_k=5,
        )

        citations = citation_service.build_citations(
            evidence
        )

        reliability = reliability_service.evaluate(
            evidence=evidence,
            citations=citations,
        )

        assert evidence
        assert reliability["status"] in {"medium", "high"}
        assert reliability["score"] >= 0.70

    finally:
        db.close()


@pytest.mark.parametrize(
    "case",
    UNSUPPORTED_CASES,
    ids=lambda case: case["id"],
)
def test_unsupported_questions_fail_reliability_threshold(case):
    db = EvaluationSessionLocal()

    try:
        retrieval_service = RetrievalService(db)
        citation_service = CitationService(db)
        reliability_service = ReliabilityService()

        evidence = retrieval_service.search(
            query=case["query"],
            top_k=5,
        )

        citations = citation_service.build_citations(
            evidence
        )

        reliability = reliability_service.evaluate(
            evidence=evidence,
            citations=citations,
        )

        assert reliability["status"] == "low"
        assert reliability["score"] < 0.70

    finally:
        db.close()