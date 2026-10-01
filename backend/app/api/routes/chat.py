from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.search import SearchResult
from app.services.generation_service import GenerationService


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    generation_service = GenerationService(db)

    result = generation_service.generate(
        query=request.query,
        top_k=request.top_k,
    )

    return ChatResponse(
        query=request.query,
        answer=result["answer"],
        evidence=[
            SearchResult(**item)
            for item in result["evidence"]
        ],
    )