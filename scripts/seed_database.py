from app.db.database import SessionLocal
from app.ingestion.pipeline import IngestionPipeline


SEED_SOURCES = [
    {
        "url": "https://www.india.gov.in/services",
        "organization": "National Portal of India",
        "title": "Services - National Portal of India",
        "source_type": "website",
        "document_type": "webpage",
        "is_official": True,
    },
]


def seed_database() -> None:
    db = SessionLocal()

    try:
        pipeline = IngestionPipeline(db)

        for source in SEED_SOURCES:
            print(f"Ingesting: {source['title']}")
            print(f"URL: {source['url']}")

            document_version = pipeline.ingest_url(
                url=source["url"],
                organization=source["organization"],
                title=source["title"],
                source_type=source["source_type"],
                document_type=source["document_type"],
                is_official=source["is_official"],
            )

            print(
                "Created/updated document version: "
                f"{document_version.version_number}"
            )

        print("Database seeding completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()