from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.document import Document, DocumentVersion
from app.models.source import Source
from app.services.ingestion_service import IngestionService


def test_first_ingestion_creates_version_one():
    db = SessionLocal()

    try:
        service = IngestionService(db)

        version = service.ingest(
            url="https://example.gov/test-address",
            organization="Test Government Department",
            title="Address Change Guide",
            content="Applicants must provide proof of address.",
        )

        assert version.version_number == 1
        assert version.is_current is True

        assert (
            version.content_text
            == "Applicants must provide proof of address."
        )

    finally:
        source = db.execute(
            select(Source).where(
                Source.url == "https://example.gov/test-address"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()
        
def test_same_content_does_not_create_new_version():
    db = SessionLocal()

    try:
        service = IngestionService(db)

        first_version = service.ingest(
            url="https://example.gov/test-duplicate",
            organization="Test Government Department",
            title="Address Change Guide",
            content="Applicants must provide proof of address.",
        )

        second_version = service.ingest(
            url="https://example.gov/test-duplicate",
            organization="Test Government Department",
            title="Address Change Guide",
            content="Applicants must provide proof of address.",
        )

        assert first_version.id == second_version.id
        assert second_version.version_number == 1
        assert second_version.is_current is True

        versions = db.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id
                == second_version.document_id
            )
        ).scalars().all()

        assert len(versions) == 1

    finally:
        source = db.execute(
            select(Source).where(
                Source.url == "https://example.gov/test-duplicate"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()
        
def test_changed_content_creates_new_version():
    db = SessionLocal()

    try:
        service = IngestionService(db)

        first_version = service.ingest(
            url="https://example.gov/test-change",
            organization="Test Government Department",
            title="Address Change Guide",
            content="Applicants must provide proof of address.",
        )

        second_version = service.ingest(
            url="https://example.gov/test-change",
            organization="Test Government Department",
            title="Address Change Guide",
            content=(
                "Applicants must provide proof of address "
                "and a valid identification document."
            ),
        )

        assert first_version.version_number == 1

        assert second_version.version_number == 2
        assert second_version.is_current is True

        db.refresh(first_version)

        assert first_version.is_current is False

        versions = db.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id
                == second_version.document_id
            )
            .order_by(DocumentVersion.version_number)
        ).scalars().all()

        assert len(versions) == 2

        assert versions[0].version_number == 1
        assert versions[0].is_current is False

        assert versions[1].version_number == 2
        assert versions[1].is_current is True

    finally:
        source = db.execute(
            select(Source).where(
                Source.url == "https://example.gov/test-change"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()