from app.rag.answer_generator import AnswerGenerator
from app.rag.prompt_builder import PromptBuilder


class FakeLLMClient:
    def __init__(self):
        self.received_prompt = None

    def generate(self, prompt: str) -> str:
        self.received_prompt = prompt

        return (
            "Applicants must provide proof of address."
        )


def test_grounded_generation_uses_prompt_builder_and_llm():
    prompt_builder = PromptBuilder()
    llm_client = FakeLLMClient()
    answer_generator = AnswerGenerator(llm_client)

    query = "What documents are required?"

    evidence = [
        {
            "content": (
                "Applicants must provide proof of address."
            ),
            "section_title": "Required Documents",
            "page_number": 4,
            "similarity": 0.91,
        }
    ]

    prompt = prompt_builder.build(
        query=query,
        evidence=evidence,
    )

    answer = answer_generator.generate(prompt)

    assert answer == (
        "Applicants must provide proof of address."
    )

    assert query in llm_client.received_prompt

    assert (
        "Applicants must provide proof of address."
        in llm_client.received_prompt
    )

    assert "Required Documents" in (
        llm_client.received_prompt
    )