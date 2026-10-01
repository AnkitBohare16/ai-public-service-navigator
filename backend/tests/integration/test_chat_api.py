from fastapi.testclient import TestClient

from app.main import app
from app.services.generation_service import GenerationService


client = TestClient(app)


def test_chat_api_returns_grounded_answer(monkeypatch):
    def mock_init(
        self,
        db,
        retrieval_service=None,
        prompt_builder=None,
        answer_generator=None,
    ):
        pass

    def mock_generate(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict:
        return {
            "answer": (
                "Applicants must provide proof of address."
            ),
            "evidence": [
                {
                    "chunk_id": "chunk-1",
                    "document_version_id": "version-1",
                    "content": (
                        "Applicants must provide "
                        "proof of address."
                    ),
                    "section_title": "Required Documents",
                    "page_number": 4,
                    "similarity": 0.91,
                }
            ],
            "citations": [
                {
                    "chunk_id": "chunk-1",
                    "document_version_id": "version-1",
                    "organization": "Test Government Department",
                    "source_title": "Address Change Guide",
                    "url": "https://example.gov/address",
                    "is_official": True,
                    "document_version": 1,
                    "retrieved_at": "2026-01-01T00:00:00",
                    "freshness_status": "fresh",
                    "age_days": 0.0,
                    "section_title": "Required Documents",
                    "page_number": 4,
                    "similarity": 0.91,
                }
            ],
            "reliability": {
                "status": "high",
                "score": 0.91,
                "reason": (
                    "Reliability is based on source authority, "
                    "retrieval similarity, and source freshness."
                ),
            },
        }
        
    monkeypatch.setattr(
        GenerationService,
        "__init__",
        mock_init,
    )

    monkeypatch.setattr(
        GenerationService,
        "generate",
        mock_generate,
    )

    response = client.post(
        "/chat",
        json={
            "query": "What documents are required?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == (
        "What documents are required?"
    )

    assert data["answer"] == (
        "Applicants must provide proof of address."
    )

    assert len(data["evidence"]) == 1

    assert (
        data["evidence"][0]["content"]
        == "Applicants must provide proof of address."
    )

    assert (
        data["evidence"][0]["section_title"]
        == "Required Documents"
    )

    assert data["evidence"][0]["page_number"] == 4


def test_chat_api_validates_empty_query():
    response = client.post(
        "/chat",
        json={
            "query": "",
            "top_k": 5,
        },
    )

    assert response.status_code == 422