from app.ingestion.parsers.html_parser import HTMLParser


def test_html_parser_removes_unwanted_elements():
    html = """
    <html>
        <body>
            <nav>Navigation</nav>

            <main>
                <h1>Address Change</h1>
                <p>Submit proof of address.</p>
            </main>

            <script>
                console.log("test");
            </script>

            <footer>Footer</footer>
        </body>
    </html>
    """

    parser = HTMLParser()

    text = parser.parse(html)

    assert "Address Change" in text
    assert "Submit proof of address." in text

    assert "Navigation" not in text
    assert "Footer" not in text
    assert "console.log" not in text