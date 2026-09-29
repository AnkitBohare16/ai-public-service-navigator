from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import DocumentVersion
from app.rag.reranker import Reranker
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService | None = None,
        reranker: Reranker | None = None,
    ):
        self.db = db

        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.reranker = (
            reranker
            or Reranker()
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0"
            )

        query_embedding = self.embedding_service.embed(
            query
        )

        distance = Chunk.embedding.cosine_distance(
            query_embedding
        )

        # Retrieve more candidates than the final
        # number of results so the reranker has
        # additional evidence to evaluate.
        candidate_k = max(top_k * 2, 10)

        statement = (
            select(
                Chunk,
                distance.label("distance"),
            )
            .join(
                DocumentVersion,
                Chunk.document_version_id
                == DocumentVersion.id,
            )
            .where(
                Chunk.embedding.is_not(None),
                DocumentVersion.is_current.is_(True),
            )
            .order_by(distance)
            .limit(candidate_k)
        )

        rows = self.db.execute(statement).all()

        candidates = []

        for chunk, chunk_distance in rows:
            similarity = 1.0 - float(chunk_distance)

            candidates.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_version_id": str(
                        chunk.document_version_id
                    ),
                    "content": chunk.content,
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number,
                    "similarity": similarity,
                }
            )

        return self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=top_k,
        )