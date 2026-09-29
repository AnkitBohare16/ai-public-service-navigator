from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language search query.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant chunks to return.",
    )


class SearchResult(BaseModel):
    chunk_id: str
    document_version_id: str
    content: str
    section_title: str | None
    page_number: int | None
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]