import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentVersion
from app.models.source import Source

from app.ingestion.chunkers.text_chunker import TextChunker
from app.models.chunk import Chunk


class IngestionService:
    def __init__(
        self,
        db: Session,
        chunker: TextChunker | None = None,
    ):
        self.db = db
        self.chunker = chunker or TextChunker()

    def ingest(
        self,
        url: str,
        organization: str,
        title: str,
        source_type: str = "website",
        document_type: str = "webpage",
        is_official: bool = True,
        content: str = "",
    ) -> DocumentVersion:
        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        now = datetime.now(timezone.utc)

        source = self._get_or_create_source(
            organization=organization,
            title=f"{organization} Website",
            url=url,
            source_type=source_type,
            is_official=is_official,
            last_checked_at=now,
        )

        document = self._get_or_create_document(
            source_id=source.id,
            title=title,
            document_type=document_type,
            canonical_url=url,
        )

        current_version = self.db.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document.id,
                DocumentVersion.is_current.is_(True),
            )
        ).scalar_one_or_none()

        if (
            current_version is not None
            and current_version.content_hash == content_hash
        ):
            return current_version

        if current_version is not None:
            current_version.is_current = False

            next_version_number = (
                current_version.version_number + 1
            )
        else:
            next_version_number = 1

        new_version = DocumentVersion(
            document_id=document.id,
            version_number=next_version_number,
            content_hash=content_hash,
            content_text=content,
            retrieved_at=now,
            is_current=True,
        )

        self.db.add(new_version)

        source.last_checked_at = now

        self.db.commit()

        self.db.refresh(new_version)

        return new_version

    def _get_or_create_source(
        self,
        organization: str,
        title: str,
        url: str,
        source_type: str,
        is_official: bool,
        last_checked_at: datetime,
    ) -> Source:
        source = self.db.execute(
            select(Source)
            .where(Source.url == url)
        ).scalar_one_or_none()

        if source is None:
            source = Source(
                organization=organization,
                title=title,
                url=url,
                source_type=source_type,
                is_official=is_official,
                last_checked_at=last_checked_at,
            )

            self.db.add(source)
            self.db.flush()

        else:
            source.last_checked_at = last_checked_at

        return source

    def _get_or_create_document(
        self,
        source_id,
        title: str,
        document_type: str,
        canonical_url: str,
    ) -> Document:
        document = self.db.execute(
            select(Document)
            .where(
                Document.source_id == source_id,
                Document.canonical_url == canonical_url,
            )
        ).scalar_one_or_none()

        if document is None:
            document = Document(
                source_id=source_id,
                title=title,
                document_type=document_type,
                canonical_url=canonical_url,
            )

            self.db.add(document)
            self.db.flush()

        return document
    
    def create_chunks(
        self,
        document_version: DocumentVersion,
    ) -> list[Chunk]:
        existing_chunks = self.db.execute(
            select(Chunk)
            .where(
                Chunk.document_version_id
                == document_version.id
            )
            .order_by(Chunk.chunk_index)
        ).scalars().all()

        if existing_chunks:
            return existing_chunks

        text = document_version.content_text or ""

        chunk_texts = self.chunker.chunk(text)

        chunks = []

        for index, chunk_text in enumerate(chunk_texts):
            chunk = Chunk(
                document_version_id=document_version.id,
                chunk_index=index,
                content=chunk_text,
            )

            self.db.add(chunk)
            chunks.append(chunk)

        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks