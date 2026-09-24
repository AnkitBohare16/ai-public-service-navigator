import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document, DocumentVersion
from app.models.source import Source

import pytest
from sqlalchemy.exc import IntegrityError


def test_create_source_document_version_and_chunk():
    db = SessionLocal()

    source = None

    try:
        source = Source(
            organization="Test Government Department",
            title="Test Official Website",
            url="https://example.gov",
            source_type="website",
            is_official=True,
            last_checked_at=datetime.now(timezone.utc),
        )

        db.add(source)
        db.flush()

        document = Document(
            source_id=source.id,
            title="Test Address Change Guide",
            document_type="webpage",
            canonical_url="https://example.gov/address-change",
        )

        db.add(document)
        db.flush()

        document_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash=uuid.uuid4().hex,
            content_text="This is test government information.",
            published_at=datetime.now(timezone.utc),
            retrieved_at=datetime.now(timezone.utc),
            is_current=True,
        )

        db.add(document_version)
        db.flush()

        chunk = Chunk(
            document_version_id=document_version.id,
            chunk_index=0,
            content="Applicants must provide proof of address.",
            section_title="Required Documents",
            page_number=1,
        )

        db.add(chunk)
        db.commit()

        result = db.execute(
            select(Chunk).where(
                Chunk.id == chunk.id
            )
        )

        saved_chunk = result.scalar_one()

        assert saved_chunk.content == (
            "Applicants must provide proof of address."
        )

        assert saved_chunk.section_title == "Required Documents"
        assert saved_chunk.page_number == 1

    finally:
        if source is not None:
            db.delete(source)
            db.commit()

        db.close()
        
def test_document_version_number_must_be_unique():
    db = SessionLocal()

    source = None

    try:
        source = Source(
            organization="Test Government Department",
            title="Test Official Website",
            url="https://example.gov",
            source_type="website",
            is_official=True,
        )

        db.add(source)
        db.flush()

        document = Document(
            source_id=source.id,
            title="Test Document",
            document_type="webpage",
            canonical_url="https://example.gov/test",
        )

        db.add(document)
        db.flush()

        version_one = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash="hash-one",
            is_current=True,
        )

        db.add(version_one)
        db.commit()

        version_two = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content_hash="hash-two",
            is_current=False,
        )

        db.add(version_two)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()

    finally:
        if source is not None:
            db.delete(source)
            db.commit()

        db.close()