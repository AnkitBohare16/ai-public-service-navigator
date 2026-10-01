from sqlalchemy.orm import Session

from app.rag.answer_generator import AnswerGenerator
from app.rag.prompt_builder import PromptBuilder
from app.services.llm_client import OpenAILLMClient
from app.services.retrieval_service import RetrievalService


class GenerationService:
    def __init__(
        self,
        db: Session,
        retrieval_service: RetrievalService | None = None,
        prompt_builder: PromptBuilder | None = None,
        answer_generator: AnswerGenerator | None = None,
    ):
        self.retrieval_service = (
            retrieval_service
            or RetrievalService(db)
        )

        self.prompt_builder = (
            prompt_builder
            or PromptBuilder()
        )

        self.answer_generator = (
            answer_generator
            or AnswerGenerator(
                OpenAILLMClient()
            )
        )

    def generate(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict:
        if not query.strip():
            raise ValueError(
                "Query cannot be empty"
            )

        evidence = self.retrieval_service.search(
            query=query,
            top_k=top_k,
        )

        if not evidence:
            return {
                "answer": (
                    "The available sources do not "
                    "provide enough information to "
                    "answer this question."
                ),
                "evidence": [],
            }

        prompt = self.prompt_builder.build(
            query=query,
            evidence=evidence,
        )

        answer = self.answer_generator.generate(
            prompt
        )

        return {
            "answer": answer,
            "evidence": evidence,
        }