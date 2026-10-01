from sqlalchemy.orm import Session

from app.rag.answer_generator import AnswerGenerator
from app.rag.prompt_builder import PromptBuilder
from app.services.citation_service import CitationService
from app.services.llm_client import OpenAILLMClient
from app.services.reliability_service import ReliabilityService
from app.services.retrieval_service import RetrievalService


class GenerationService:
    def __init__(
        self,
        db: Session,
        retrieval_service: RetrievalService | None = None,
        prompt_builder: PromptBuilder | None = None,
        answer_generator: AnswerGenerator | None = None,
        citation_service: CitationService | None = None,
        reliability_service: ReliabilityService | None = None,
    ):
        self.retrieval_service = (
            retrieval_service or RetrievalService(db)
        )

        self.prompt_builder = (
            prompt_builder or PromptBuilder()
        )

        self.answer_generator = (
            answer_generator or AnswerGenerator(OpenAILLMClient())
        )

        self.citation_service = (
            citation_service or CitationService(db)
        )

        self.reliability_service = (
            reliability_service or ReliabilityService()
        )

    def generate(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        evidence = self.retrieval_service.search(
            query=query,
            top_k=top_k,
        )

        if not evidence:
            reliability = self.reliability_service.evaluate(
                evidence=[],
                citations=[],
            )

            return {
                "answer": (
                    "The available sources do not "
                    "provide enough information to "
                    "answer this question."
                ),
                "evidence": [],
                "citations": [],
                "reliability": reliability,
            }

        prompt = self.prompt_builder.build(
            query=query,
            evidence=evidence,
        )

        answer = self.answer_generator.generate(prompt)

        citations = self.citation_service.build_citations(
            evidence
        )

        reliability = self.reliability_service.evaluate(
            evidence=evidence,
            citations=citations,
        )

        return {
            "answer": answer,
            "evidence": evidence,
            "citations": citations,
            "reliability": reliability,
        }