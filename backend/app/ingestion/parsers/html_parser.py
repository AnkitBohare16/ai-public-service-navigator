from bs4 import BeautifulSoup


class HTMLParser:
    def parse(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(
            ["script", "style", "noscript", "nav", "footer"]
        ):
            element.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        return text