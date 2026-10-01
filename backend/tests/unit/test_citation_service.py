from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.citation_service import CitationService


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.executed_statement = None

    def execute(self, statement):
        self.executed_statement = statement
        return self

    def all(self):
        return self.rows


def test_citation_service_builds_citation_from_evidence():
    document_version_id = str(uuid4())
    chunk_id = str(uuid4())

    retrieved_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    row = SimpleNamespace(
        id=document_version_id,
        version_number=2,
        retrieved_at=retrieved_at,
        organization="Test Government Department",
        source_title="Address Change Guide",
        url="https://example.gov/address",
        is_official=True,
    )

    db = FakeSession([row])
    service = CitationService(db)

    evidence = [
        {
            "chunk_id": chunk_id,
            "document_version_id": document_version_id,
            "content": "Required documents include proof of address.",
            "section_title": "Required Documents",
            "page_number": 4,
            "similarity": 0.91,
        }
    ]

    citations = service.build_citations(evidence)

    assert len(citations) == 1

    citation = citations[0]

    assert citation["chunk_id"] == chunk_id
    assert citation["document_version_id"] == document_version_id
    assert citation["organization"] == "Test Government Department"
    assert citation["source_title"] == "Address Change Guide"
    assert citation["url"] == "https://example.gov/address"
    assert citation["is_official"] is True
    assert citation["document_version"] == 2
    assert citation["retrieved_at"] == retrieved_at
    assert citation["section_title"] == "Required Documents"
    assert citation["page_number"] == 4
    assert citation["similarity"] == 0.91


def test_citation_service_returns_empty_list_for_empty_evidence():
    db = FakeSession([])
    service = CitationService(db)

    citations = service.build_citations([])

    assert citations == []
    assert db.executed_statement is None


def test_citation_service_skips_missing_document_version():
    existing_document_version_id = str(uuid4())
    missing_document_version_id = str(uuid4())

    row = SimpleNamespace(
        id=existing_document_version_id,
        version_number=1,
        retrieved_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        organization="Test Government Department",
        source_title="Test Guide",
        url="https://example.gov/test",
        is_official=True,
    )

    db = FakeSession([row])
    service = CitationService(db)

    evidence = [
        {
            "chunk_id": str(uuid4()),
            "document_version_id": missing_document_version_id,
            "content": "Some evidence",
            "section_title": None,
            "page_number": None,
            "similarity": 0.80,
        }
    ]

    citations = service.build_citations(evidence)

    assert citations == []


def test_citation_service_preserves_multiple_evidence_items():
    first_version_id = str(uuid4())
    second_version_id = str(uuid4())

    rows = [
        SimpleNamespace(
            id=first_version_id,
            version_number=1,
            retrieved_at=datetime(
                2026,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            organization="Department A",
            source_title="Guide A",
            url="https://example.gov/a",
            is_official=True,
        ),
        SimpleNamespace(
            id=second_version_id,
            version_number=3,
            retrieved_at=datetime(
                2026,
                2,
                1,
                tzinfo=timezone.utc,
            ),
            organization="Department B",
            source_title="Guide B",
            url="https://example.gov/b",
            is_official=False,
        ),
    ]

    db = FakeSession(rows)
    service = CitationService(db)

    evidence = [
        {
            "chunk_id": str(uuid4()),
            "document_version_id": first_version_id,
            "content": "Evidence A",
            "section_title": "Section A",
            "page_number": 1,
            "similarity": 0.95,
        },
        {
            "chunk_id": str(uuid4()),
            "document_version_id": second_version_id,
            "content": "Evidence B",
            "section_title": "Section B",
            "page_number": 2,
            "similarity": 0.85,
        },
    ]

    citations = service.build_citations(evidence)

    assert len(citations) == 2

    assert citations[0]["organization"] == "Department A"
    assert citations[0]["document_version"] == 1

    assert citations[1]["organization"] == "Department B"
    assert citations[1]["document_version"] == 3
    assert citations[1]["is_official"] is False