import pytest

from app.rag.prompt_builder import PromptBuilder


def test_prompt_builder_includes_query_and_evidence():
    builder = PromptBuilder()

    prompt = builder.build(
        query="What documents are required?",
        evidence=[
            {
                "content": (
                    "Applicants must provide proof of address."
                ),
                "section_title": "Required Documents",
                "page_number": 4,
                "similarity": 0.91,
            }
        ],
    )

    assert "What documents are required?" in prompt
    assert (
        "Applicants must provide proof of address."
        in prompt
    )
    assert "Required Documents" in prompt
    assert "Page: 4" in prompt


def test_prompt_builder_contains_grounding_rules():
    builder = PromptBuilder()

    prompt = builder.build(
        query="How do I apply?",
        evidence=[
            {
                "content": "Applications can be submitted online.",
                "similarity": 0.88,
            }
        ],
    )

    assert "ONLY the evidence" in prompt
    assert "Do not invent" in prompt
    assert (
        "available\n   sources do not provide enough information"
        in prompt
    )


def test_prompt_builder_rejects_empty_query():
    builder = PromptBuilder()

    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        builder.build(
            query="   ",
            evidence=[
                {"content": "Some evidence."}
            ],
        )


def test_prompt_builder_rejects_empty_evidence():
    builder = PromptBuilder()

    with pytest.raises(
        ValueError,
        match="Evidence cannot be empty",
    ):
        builder.build(
            query="What documents are required?",
            evidence=[],
        )