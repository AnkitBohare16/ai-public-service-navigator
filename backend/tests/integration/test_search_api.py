from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.database import SessionLocal
from app.main import app
from app.models.chunk import Chunk
from app.models.document import Document, DocumentVersion
from app.models.source import Source


client = TestClient(app)


def test_search_api_returns_relevant_results():
    db = SessionLocal()

    test_url = "https://example.gov/search-api-test"

    try:
        # Clean up previous test data
        existing_sources = (
            db.query(Source)
            .filter(Source.url == test_url)
            .all()
        )

        for existing_source in existing_sources:
            db.delete(existing_source)

        db.commit()

        # Create source
        source = Source(
            organization="Test Government Department",
            title="Test Government Website",
            url=test_url,
            source_type="website",
            is_official=True,
        )

        db.add(source)
        db.flush()

        # Create document
        document = Document(
            source_id=source.id,
            title="Address Change Guide",
            document_type="webpage",
            canonical_url=test_url,
        )

        db.add(document)
        db.flush()

        # Create current version
        document_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash="search-api-test-hash",
            content_text=(
                "Applicants must provide proof of address."
            ),
            is_current=True,
        )

        db.add(document_version)
        db.flush()

        # Create chunks with known embeddings
        chunks = [
            Chunk(
                document_version_id=document_version.id,
                chunk_index=0,
                content=(
                    "Applicants must provide proof of address."
                ),
                embedding=[1.0] + [0.0] * 383,
            ),
            Chunk(
                document_version_id=document_version.id,
                chunk_index=1,
                content=(
                    "Applications can be submitted online."
                ),
                embedding=[0.0, 1.0] + [0.0] * 382,
            ),
        ]

        db.add_all(chunks)
        db.commit()

        # Call the real API
        response = client.post(
            "/search",
            json={
                "query": "What documents prove my address?",
                "top_k": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["query"] == (
            "What documents prove my address?"
        )

        assert len(data["results"]) == 2

        returned_contents = [
            result["content"]
            for result in data["results"]
        ]

        assert (
            "Applicants must provide proof of address."
            in returned_contents
        )

        assert (
            "Applications can be submitted online."
            in returned_contents
        )

        assert "similarity" in data["results"][0]

    finally:
        source = db.execute(
            select(Source).where(
                Source.url == test_url
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()