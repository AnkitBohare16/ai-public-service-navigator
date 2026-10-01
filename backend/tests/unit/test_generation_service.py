from app.services.generation_service import GenerationService


class FakeRetrievalService:
    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        return [
            {
                "chunk_id": "chunk-1",
                "document_version_id": "version-1",
                "content": (
                    "Applicants must provide proof of address."
                ),
                "section_title": "Required Documents",
                "page_number": 4,
                "similarity": 0.91,
            }
        ]


class FakePromptBuilder:
    def build(
        self,
        query: str,
        evidence: list[dict],
    ) -> str:
        return (
            f"QUESTION: {query}\n"
            f"EVIDENCE: {evidence[0]['content']}"
        )


class FakeAnswerGenerator:
    def generate(self, prompt: str) -> str:
        return (
            "Applicants must provide proof of address."
        )

class FakeCitationService:
    def build_citations(
        self,
        evidence: list[dict],
    ) -> list[dict]:
        return [
            {
                "chunk_id": "chunk-1",
                "document_version_id": "version-1",
                "organization": "Test Government Department",
                "source_title": "Test Government Website",
                "url": "https://example.gov/test",
                "is_official": True,
                "document_version": 1,
                "retrieved_at": "2026-01-01T00:00:00",
                "section_title": "Required Documents",
                "page_number": 4,
                "similarity": 0.91,
                "freshness_status": "fresh",
                "age_days": 5.0,
            }
        ]

def test_generation_service_orchestrates_rag_flow():
    service = GenerationService(
        db=None,
        retrieval_service=FakeRetrievalService(),
        prompt_builder=FakePromptBuilder(),
        answer_generator=FakeAnswerGenerator(),
        citation_service=FakeCitationService(),
    )

    result = service.generate(
        query="What documents are required?",
        top_k=5,
    )

    assert result["answer"] == (
        "Applicants must provide proof of address."
    )

    assert len(result["evidence"]) == 1

    assert (
        result["evidence"][0]["content"]
        == "Applicants must provide proof of address."
    )


def test_generation_service_returns_message_without_evidence():
    class EmptyRetrievalService:
        def search(
            self,
            query: str,
            top_k: int = 5,
        ) -> list[dict]:
            return []

    service = GenerationService(
        db=None,
        retrieval_service=EmptyRetrievalService(),
        prompt_builder=FakePromptBuilder(),
        answer_generator=FakeAnswerGenerator(),
        citation_service=FakeCitationService(),
    )

    result = service.generate(
        query="What is the application deadline?"
    )

    assert (
        "do not provide enough information"
        in result["answer"]
    )

    assert result["evidence"] == []


def test_generation_service_rejects_empty_query():
    service = GenerationService(
        db=None,
        retrieval_service=FakeRetrievalService(),
        prompt_builder=FakePromptBuilder(),
        answer_generator=FakeAnswerGenerator(),
        citation_service=FakeCitationService(),
    )

    try:
        service.generate("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Query cannot be empty"