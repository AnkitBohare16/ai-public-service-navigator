from unittest.mock import Mock

from app.db.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document, DocumentVersion
from app.models.source import Source
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService


def test_retrieval_returns_most_similar_current_chunks():
    db = SessionLocal()

    test_url = "https://example.gov/retrieval-test"

    try:
        # ---------------------------------------------------------
        # Clean up data from previous failed test runs
        # ---------------------------------------------------------

        existing_sources = (
            db.query(Source)
            .filter(Source.url == test_url)
            .all()
        )

        for existing_source in existing_sources:
            db.delete(existing_source)

        db.commit()

        # ---------------------------------------------------------
        # Create test source
        # ---------------------------------------------------------

        source = Source(
            organization="Test Government Department",
            title="Test Government Website",
            url=test_url,
            source_type="website",
            is_official=True,
        )

        db.add(source)
        db.flush()

        # ---------------------------------------------------------
        # Create test document
        # ---------------------------------------------------------

        document = Document(
            source_id=source.id,
            title="Address Change Guide",
            document_type="webpage",
            canonical_url=test_url,
        )

        db.add(document)
        db.flush()

        # ---------------------------------------------------------
        # Create OLD document version
        # ---------------------------------------------------------

        old_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash="old-version-hash",
            content_text=(
                "Applicants must provide proof of address."
            ),
            is_current=False,
        )

        db.add(old_version)
        db.flush()

        # ---------------------------------------------------------
        # Create CURRENT document version
        # ---------------------------------------------------------

        current_version = DocumentVersion(
            document_id=document.id,
            version_number=2,
            content_hash="current-version-hash",
            content_text=(
                "Applications can be submitted online. "
                "The application fee must be paid."
            ),
            is_current=True,
        )

        db.add(current_version)
        db.flush()

        # ---------------------------------------------------------
        # Create chunks
        # ---------------------------------------------------------

        chunks = [
            Chunk(
                document_version_id=old_version.id,
                chunk_index=0,
                content=(
                    "Applicants must provide proof of address."
                ),
                embedding=[1.0] + [0.0] * 383,
            ),
            Chunk(
                document_version_id=current_version.id,
                chunk_index=0,
                content=(
                    "Applications can be submitted online."
                ),
                embedding=[0.0, 1.0] + [0.0] * 382,
            ),
            Chunk(
                document_version_id=current_version.id,
                chunk_index=1,
                content=(
                    "The application fee must be paid."
                ),
                embedding=[0.0, 0.0, 1.0] + [0.0] * 381,
            ),
        ]

        db.add_all(chunks)
        db.commit()

        # ---------------------------------------------------------
        # Mock the query embedding
        # ---------------------------------------------------------

        embedding_service = Mock(
            spec=EmbeddingService,
        )

        embedding_service.embed.return_value = (
            [1.0] + [0.0] * 383
        )

        # ---------------------------------------------------------
        # Create retrieval service
        # ---------------------------------------------------------

        service = RetrievalService(
            db,
            embedding_service=embedding_service,
        )

        # ---------------------------------------------------------
        # Execute semantic search
        # ---------------------------------------------------------

        results = service.search(
            query=(
                "What documents are required "
                "to prove my address?"
            ),
            top_k=3,
        )

        # ---------------------------------------------------------
        # Verify results were returned
        # ---------------------------------------------------------

        assert len(results) == 2

        # ---------------------------------------------------------
        # Verify ONLY current-version chunks were returned
        # ---------------------------------------------------------

        returned_version_ids = {
            result["document_version_id"]
            for result in results
        }

        assert str(old_version.id) not in returned_version_ids

        assert str(current_version.id) in returned_version_ids

        # ---------------------------------------------------------
        # Verify the old highly-relevant chunk was excluded
        # ---------------------------------------------------------

        returned_contents = [
            result["content"]
            for result in results
        ]

        assert (
            "Applicants must provide proof of address."
            not in returned_contents
        )

        # ---------------------------------------------------------
        # Verify current chunks were returned
        # ---------------------------------------------------------

        assert (
            "Applications can be submitted online."
            in returned_contents
        )

        assert (
            "The application fee must be paid."
            in returned_contents
        )

        # ---------------------------------------------------------
        # Verify embedding service received the query
        # ---------------------------------------------------------

        embedding_service.embed.assert_called_once_with(
            "What documents are required "
            "to prove my address?"
        )

    finally:
        # ---------------------------------------------------------
        # Remove all test data
        # ---------------------------------------------------------

        sources = (
            db.query(Source)
            .filter(Source.url == test_url)
            .all()
        )

        for test_source in sources:
            db.delete(test_source)

        db.commit()
        db.close()