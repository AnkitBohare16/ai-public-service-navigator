from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post(
    "",
    response_model=SearchResponse,
)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
) -> SearchResponse:
    retrieval_service = RetrievalService(db)

    results = retrieval_service.search(
        query=request.query,
        top_k=request.top_k,
    )

    return SearchResponse(
        query=request.query,
        results=[
            SearchResult(**result)
            for result in results
        ],
    )