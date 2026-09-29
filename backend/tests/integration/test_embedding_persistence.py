from unittest.mock import Mock

from app.db.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document, DocumentVersion
from app.models.source import Source
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService


def test_generate_embeddings_for_document_version():
    db = SessionLocal()

    try:
        source = Source(
            organization="Test Organization",
            title="Test Website",
            url="https://example.com/embedding-test",
            source_type="website",
            is_official=True,
        )

        db.add(source)
        db.flush()

        document = Document(
            source_id=source.id,
            title="Test Document",
            document_type="webpage",
            canonical_url="https://example.com/embedding-test",
        )

        db.add(document)
        db.flush()

        document_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash="embedding-test-hash",
            content_text="Test document content",
            is_current=True,
        )

        db.add(document_version)
        db.flush()

        chunks = [
            Chunk(
                document_version_id=document_version.id,
                chunk_index=0,
                content="Proof of address is required.",
            ),
            Chunk(
                document_version_id=document_version.id,
                chunk_index=1,
                content="Submit the application online.",
            ),
            Chunk(
                document_version_id=document_version.id,
                chunk_index=2,
                content="The application fee is required.",
            ),
        ]

        db.add_all(chunks)
        db.commit()

        embedding_service = Mock(
            spec=EmbeddingService,
        )

        fake_embeddings = [
            [0.1] * 384,
            [0.2] * 384,
            [0.3] * 384,
        ]

        embedding_service.embed_many.return_value = fake_embeddings

        service = IngestionService(
            db,
            embedding_service=embedding_service,
        )

        updated_chunks = service.generate_embeddings(
            document_version
        )

        assert len(updated_chunks) == 3

        for chunk, expected_embedding in zip(
            updated_chunks,
            fake_embeddings,
        ):
            assert chunk.embedding is not None
            assert len(chunk.embedding) == 384
            assert chunk.embedding == expected_embedding

        embedding_service.embed_many.assert_called_once_with(
            [
                "Proof of address is required.",
                "Submit the application online.",
                "The application fee is required.",
            ]
        )

    finally:
        db.rollback()

        if "source" in locals() and source.id is not None:
            db.delete(source)
            db.commit()

        db.close()