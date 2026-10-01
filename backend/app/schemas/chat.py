from pydantic import BaseModel, Field

from app.schemas.citation import Citation
from app.schemas.search import SearchResult


class ChatRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language public-service question.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of evidence chunks to retrieve.",
    )


class ChatResponse(BaseModel):
    query: str
    answer: str
    evidence: list[SearchResult]
    citations: list[Citation]