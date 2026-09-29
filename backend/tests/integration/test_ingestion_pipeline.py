import httpx
from sqlalchemy import select

from app.db.database import SessionLocal
from app.ingestion.pipeline import IngestionPipeline
from app.models.chunk import Chunk
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

        # ---------------------------------------------------------
        # 1. Verify document version was created
        # ---------------------------------------------------------

        assert version.version_number == 1
        assert version.is_current is True

        # ---------------------------------------------------------
        # 2. Verify HTML was parsed correctly
        # ---------------------------------------------------------

        assert "Address Change" in version.content_text
        assert (
            "Applicants must provide proof of address."
            in version.content_text
        )

        assert "Navigation" not in version.content_text
        assert "console.log" not in version.content_text
        assert "Footer content" not in version.content_text

        # ---------------------------------------------------------
        # 3. Verify document version was persisted
        # ---------------------------------------------------------

        saved_version = db.execute(
            select(DocumentVersion).where(
                DocumentVersion.id == version.id
            )
        ).scalar_one()

        assert saved_version.content_hash == version.content_hash

        # ---------------------------------------------------------
        # 4. Verify chunks were created
        # ---------------------------------------------------------

        chunks = db.execute(
            select(Chunk)
            .where(
                Chunk.document_version_id == version.id
            )
            .order_by(Chunk.chunk_index)
        ).scalars().all()

        assert len(chunks) > 0

        # ---------------------------------------------------------
        # 5. Verify every chunk has an embedding
        # ---------------------------------------------------------

        for chunk in chunks:
            assert chunk.embedding is not None

        # ---------------------------------------------------------
        # 6. Verify embeddings have the expected dimensions
        # ---------------------------------------------------------

        for chunk in chunks:
            assert len(chunk.embedding) == 384

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