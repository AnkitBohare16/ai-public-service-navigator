from sqlalchemy.orm import Session

from app.ingestion.loaders.web_loader import WebPageLoader
from app.ingestion.parsers.html_parser import HTMLParser
from app.models.document import DocumentVersion
from app.services.ingestion_service import IngestionService


class IngestionPipeline:
    def __init__(
        self,
        db: Session,
        ingestion_service: IngestionService | None = None,
    ):
        self.loader = WebPageLoader()
        self.parser = HTMLParser()

        self.ingestion_service = (
            ingestion_service
            or IngestionService(db)
        )

    def ingest_url(
        self,
        url: str,
        organization: str,
        title: str,
        source_type: str = "website",
        document_type: str = "webpage",
        is_official: bool = True,
    ) -> DocumentVersion:
        html = self.loader.load(url)

        text = self.parser.parse(html)

        document_version = self.ingestion_service.ingest(
            url=url,
            organization=organization,
            title=title,
            source_type=source_type,
            document_type=document_type,
            is_official=is_official,
            content=text,
        )

        self.ingestion_service.create_chunks(
            document_version
        )

        self.ingestion_service.generate_embeddings(
            document_version
        )

        return document_version