from app.services.embedding_service import EmbeddingService


def test_real_embedding_model_returns_384_dimensions():
    service = EmbeddingService()

    embedding = service.embed(
        "What documents are required to prove my address?"
    )

    assert isinstance(embedding, list)
    assert len(embedding) == 384

    assert all(
        isinstance(value, float)
        for value in embedding
    )