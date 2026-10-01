from openai import OpenAI

from app.core.config import get_settings


class OpenAILLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        settings = get_settings()

        self.api_key = (
            api_key
            if api_key is not None
            else settings.llm_api_key
        )

        if not self.api_key:
            raise ValueError("LLM API key is not configured")
        
        self.model = model or settings.llm_model

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.llm_base_url,
        )

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        answer = response.output_text

        if not answer.strip():
            raise ValueError("LLM returned an empty answer")

        return answer.strip()