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


def run_evaluation() -> None:
    db = EvaluationSessionLocal()

    try:
        retrieval_service = RetrievalService(db)
        citation_service = CitationService(db)
        reliability_service = ReliabilityService()

        passed = 0
        total = len(EVALUATION_CASES)

        print()
        print("AI Public-Service Information Navigator")
        print("Evaluation Results")
        print("----------------------------------------")

        for case in EVALUATION_CASES:
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

            expected = case["expected_behavior"]

            if expected == "supported":
                case_passed = (
                    bool(evidence)
                    and reliability["status"] in {"medium", "high"}
                    and reliability["score"] >= 0.70
                )
            else:
                case_passed = (
                    reliability["status"] == "low"
                    and reliability["score"] < 0.70
                )

            if case_passed:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"

            print(
                f"[{status}] {case['id']} "
                f"| expected={expected} "
                f"| reliability={reliability['status']} "
                f"| score={reliability['score']:.2f}"
            )

        print("----------------------------------------")
        print(
            f"Overall: {passed}/{total} evaluation cases passed."
        )

        if passed != total:
            raise SystemExit(1)

    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation()