import httpx

from app.ingestion.loaders.web_loader import WebPageLoader


def test_web_page_loader_returns_html(monkeypatch):
    expected_html = """
    <html>
        <body>
            <h1>Address Change</h1>
            <p>Submit proof of address.</p>
        </body>
    </html>
    """

    def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=200,
            text=expected_html,
            request=httpx.Request("GET", "https://example.gov"),
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    loader = WebPageLoader()

    result = loader.load("https://example.gov")

    assert result == expected_html
    
def test_web_page_loader_raises_for_http_error(monkeypatch):
    def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=404,
            request=httpx.Request(
                "GET",
                "https://example.gov/missing",
            ),
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    loader = WebPageLoader()

    try:
        loader.load("https://example.gov/missing")
        assert False, "Expected HTTPStatusError"
    except httpx.HTTPStatusError:
        pass