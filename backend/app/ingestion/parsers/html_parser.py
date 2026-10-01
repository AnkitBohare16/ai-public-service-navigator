from bs4 import BeautifulSoup


class HTMLParser:
    def parse(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "button",
                "iframe",
                "svg",
            ]
        ):
            element.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)