import httpx
from sqlalchemy import select

from app.db.database import SessionLocal
from app.ingestion.pipeline import IngestionPipeline
from app.models.document import DocumentVersion
from app.models.source import Source


def test_ingestion_pipeline_loads_parses_and_persists_html(
    monkeypatch,
):
    html = """
    <html>
        <head>
            <title>Address Change</title>
        </head>

        <body>
            <nav>Navigation</nav>

            <main>
                <h1>Address Change</h1>
                <p>Applicants must provide proof of address.</p>
            </main>

            <script>
                console.log("ignore this");
            </script>

            <footer>Footer content</footer>
        </body>
    </html>
    """

    def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=200,
            text=html,
            request=httpx.Request(
                "GET",
                "https://example.gov/address-change",
            ),
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    db = SessionLocal()

    try:
        pipeline = IngestionPipeline(db)

        version = pipeline.ingest_url(
            url="https://example.gov/address-change",
            organization="Test Government Department",
            title="Address Change Guide",
        )

        assert version.version_number == 1
        assert version.is_current is True

        assert "Address Change" in version.content_text
        assert (
            "Applicants must provide proof of address."
            in version.content_text
        )

        assert "Navigation" not in version.content_text
        assert "console.log" not in version.content_text
        assert "Footer content" not in version.content_text

        saved_version = db.execute(
            select(DocumentVersion).where(
                DocumentVersion.id == version.id
            )
        ).scalar_one()

        assert saved_version.content_hash == version.content_hash

    finally:
        source = db.execute(
            select(Source).where(
                Source.url == "https://example.gov/address-change"
            )
        ).scalar_one_or_none()

        if source is not None:
            db.delete(source)
            db.commit()

        db.close()