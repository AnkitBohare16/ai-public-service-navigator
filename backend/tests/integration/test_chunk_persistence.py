from sqlalchemy import select

from app.db.database import SessionLocal
from app.ingestion.chunkers.text_chunker import TextChunker
from app.models.chunk import Chunk
from app.models.source import Source
from app.services.ingestion_service import IngestionService


def test_create_chunks_for_document_version():
    db = SessionLocal()

    try:
        service = IngestionService(
            db,
            chunker=TextChunker(
                chunk_size=100,
                overlap=0,
            ),
        )

        content = (
            "A" * 100
            + "B" * 100
            + "C" * 50
        )

        version = service.ingest(
            url="https://example.gov/chunk-test",
            organization="Test Government Department",
            title="Chunk Test Document",
            content=content,
        )

        chunks = service.create_chunks(version)

        assert len(chunks) == 3

        assert chunks[0].chunk_index == 0
        assert chunks[1].chunk_index == 1
        assert chunks[2].chunk_index == 2

        assert len(chunks[0].content) == 100
        assert len(chunks[1].content) == 100
        assert len(chunks[2].content) == 50

        saved_chunks = db.execute(
            select(Chunk)
            .where(
                Chunk.document_version_id == version.id
            )
            .order_by(Chunk.chunk_index)
        ).scalars().all()

        assert len(saved_chunks) == 3

    finally:
        source = db.execute(
            select(Source).where(
                Source.url
                == "https://example.gov/chunk-test"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()
        
def test_create_chunks_does_not_duplicate_existing_chunks():
    db = SessionLocal()

    try:
        service = IngestionService(db)

        content = "A" * 250

        version = service.ingest(
            url="https://example.gov/chunk-duplicate-test",
            organization="Test Government Department",
            title="Chunk Duplicate Test",
            content=content,
        )

        first_chunks = service.create_chunks(version)
        second_chunks = service.create_chunks(version)

        assert len(first_chunks) == len(second_chunks)

        assert [
            chunk.id for chunk in first_chunks
        ] == [
            chunk.id for chunk in second_chunks
        ]

        saved_chunks = db.execute(
            select(Chunk)
            .where(
                Chunk.document_version_id == version.id
            )
        ).scalars().all()

        assert len(saved_chunks) == len(first_chunks)

    finally:
        source = db.execute(
            select(Source).where(
                Source.url
                == "https://example.gov/chunk-duplicate-test"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()