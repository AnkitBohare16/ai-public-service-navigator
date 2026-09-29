from unittest.mock import Mock, patch

import pytest

from app.services.embedding_service import EmbeddingService


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_returns_vector(mock_model_class):
    mock_model = Mock()

    mock_model.encode.return_value = Mock(
        tolist=lambda: [0.1, 0.2, 0.3]
    )

    mock_model_class.return_value = mock_model

    service = EmbeddingService()

    result = service.embed("proof of address")

    assert result == [0.1, 0.2, 0.3]

    mock_model.encode.assert_called_once_with(
        "proof of address",
        convert_to_numpy=True,
    )


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_many_returns_vectors(mock_model_class):
    mock_model = Mock()

    mock_model.encode.return_value = Mock(
        tolist=lambda: [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
    )

    mock_model_class.return_value = mock_model

    service = EmbeddingService()

    result = service.embed_many(
        [
            "proof of address",
            "application fee",
        ]
    )

    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_rejects_empty_text(mock_model_class):
    mock_model_class.return_value = Mock()

    service = EmbeddingService()

    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.embed("   ")


@patch("app.services.embedding_service.SentenceTransformer")
def test_embed_many_rejects_empty_text(mock_model_class):
    mock_model_class.return_value = Mock()

    service = EmbeddingService()

    with pytest.raises(
        ValueError,
        match="Texts cannot contain empty strings",
    ):
        service.embed_many(
            [
                "valid text",
                "   ",
            ]
        )