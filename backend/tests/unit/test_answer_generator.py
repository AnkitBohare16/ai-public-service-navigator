import pytest

from app.rag.answer_generator import AnswerGenerator


class FakeLLMClient:
    def __init__(self, response: str):
        self.response = response
        self.received_prompt = None

    def generate(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.response


def test_answer_generator_returns_llm_response():
    llm_client = FakeLLMClient(
        "Applicants must provide proof of address."
    )

    generator = AnswerGenerator(llm_client)

    answer = generator.generate(
        "Answer using the provided evidence."
    )

    assert answer == (
        "Applicants must provide proof of address."
    )


def test_answer_generator_strips_whitespace():
    llm_client = FakeLLMClient(
        "  Applicants must provide proof of address.  "
    )

    generator = AnswerGenerator(llm_client)

    answer = generator.generate(
        "Answer using the provided evidence."
    )

    assert answer == (
        "Applicants must provide proof of address."
    )


def test_answer_generator_passes_prompt_to_llm():
    llm_client = FakeLLMClient("Test answer")

    generator = AnswerGenerator(llm_client)

    prompt = "Use only this evidence."

    generator.generate(prompt)

    assert llm_client.received_prompt == prompt


def test_answer_generator_rejects_empty_prompt():
    llm_client = FakeLLMClient("Test answer")

    generator = AnswerGenerator(llm_client)

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        generator.generate("   ")


def test_answer_generator_rejects_empty_llm_response():
    llm_client = FakeLLMClient("   ")

    generator = AnswerGenerator(llm_client)

    with pytest.raises(
        ValueError,
        match="LLM returned an empty answer",
    ):
        generator.generate(
            "Use only this evidence."
        )