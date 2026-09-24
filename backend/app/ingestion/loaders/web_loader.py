import httpx


class WebPageLoader:
    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def load(self, url: str) -> str:
        response = httpx.get(
            url,
            timeout=self.timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        return response.text
