from app.ingestion.parsers.html_parser import HTMLParser


def test_html_parser_removes_non_content_elements():
    html = """
    <html>
        <head>
            <title>Test Page</title>
            <script>alert("test")</script>
            <style>.hidden { display: none; }</style>
        </head>
        <body>
            <header>Header Navigation</header>
            <nav>Main Navigation</nav>

            <main>
                <h1>Government Services</h1>
                <p>Apply for public services online.</p>
                <button>Search</button>
            </main>

            <aside>Sidebar content</aside>
            <footer>Footer information</footer>
        </body>
    </html>
    """

    parser = HTMLParser()
    result = parser.parse(html)

    assert "Government Services" in result
    assert "Apply for public services online." in result

    assert "Header Navigation" not in result
    assert "Main Navigation" not in result
    assert "Sidebar content" not in result
    assert "Footer information" not in result
    assert "Search" not in result
    assert "alert" not in result
    assert "display: none" not in result


def test_html_parser_normalizes_whitespace():
    html = """
    <main>
        <p>
            Government    services
            are available
            online.
        </p>
    </main>
    """

    parser = HTMLParser()
    result = parser.parse(html)

    assert result == "Government services\nare available\nonline."