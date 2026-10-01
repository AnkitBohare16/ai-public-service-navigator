import pytest

from app.services.llm_client import OpenAILLMClient


def test_llm_client_requires_api_key():
    with pytest.raises(
        ValueError,
        match="LLM API key is not configured",
    ):
        OpenAILLMClient(
            api_key="",
            model="test-model",
        )


def test_llm_client_rejects_empty_prompt():
    client = OpenAILLMClient.__new__(
        OpenAILLMClient
    )

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        client.generate("   ")