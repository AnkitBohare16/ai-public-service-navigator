from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentVersion
from app.models.source import Source
from app.services.freshness_service import FreshnessService


class CitationService:
    def __init__(
        self,
        db: Session,
        freshness_service: FreshnessService | None = None,
    ):
        self.db = db
        self.freshness_service = (
            freshness_service or FreshnessService()
        )

    def build_citations(
        self,
        evidence: list[dict],
    ) -> list[dict]:
        if not evidence:
            return []

        document_version_ids = [
            item["document_version_id"]
            for item in evidence
        ]

        statement = (
            select(
                DocumentVersion.id,
                DocumentVersion.version_number,
                DocumentVersion.retrieved_at,
                Document.id.label("document_id"),
                Source.organization,
                Source.title.label("source_title"),
                Source.url,
                Source.is_official,
            )
            .join(
                Document,
                DocumentVersion.document_id == Document.id,
            )
            .join(
                Source,
                Document.source_id == Source.id,
            )
            .where(
                DocumentVersion.id.in_(document_version_ids)
            )
        )

        rows = self.db.execute(statement).all()

        metadata_by_version = {
            str(row.id): row
            for row in rows
        }

        citations = []

        for item in evidence:
            document_version_id = item["document_version_id"]
            metadata = metadata_by_version.get(
                document_version_id
            )

            if metadata is None:
                continue

            freshness_status = (
                self.freshness_service.get_status(
                    metadata.retrieved_at
                )
            )

            age_days = (
                self.freshness_service.get_age_days(
                    metadata.retrieved_at
                )
            )

            citations.append(
                {
                    "chunk_id": item["chunk_id"],
                    "document_version_id": document_version_id,
                    "organization": metadata.organization,
                    "source_title": metadata.source_title,
                    "url": metadata.url,
                    "is_official": metadata.is_official,
                    "document_version": metadata.version_number,
                    "retrieved_at": metadata.retrieved_at,
                    "freshness_status": freshness_status,
                    "age_days": age_days,
                    "section_title": item["section_title"],
                    "page_number": item["page_number"],
                    "similarity": item["similarity"],
                }
            )

        return citations