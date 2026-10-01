from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class AnswerGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate(
        self,
        prompt: str,
    ) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        answer = self.llm_client.generate(prompt)

        if not answer.strip():
            raise ValueError(
                "LLM returned an empty answer"
            )

        return answer.strip()