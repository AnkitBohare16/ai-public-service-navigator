from datetime import datetime

from pydantic import BaseModel

class Citation(BaseModel):
    chunk_id: str
    document_version_id: str
    organization: str
    source_title: str
    url: str
    is_official: bool
    document_version: int
    retrieved_at: datetime
    freshness_status: str
    age_days: float | None
    section_title: str | None
    page_number: int | None
    similarity: float