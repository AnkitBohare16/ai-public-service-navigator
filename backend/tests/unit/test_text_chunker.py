import pytest

from app.ingestion.chunkers.text_chunker import TextChunker


def test_empty_text_returns_no_chunks():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    assert chunker.chunk("") == []


def test_short_text_returns_one_chunk():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    text = "This is a short document."

    chunks = chunker.chunk(text)

    assert chunks == [text]


def test_long_text_is_split_into_multiple_chunks():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    text = "A" * 250

    chunks = chunker.chunk(text)

    assert len(chunks) == 3

    assert len(chunks[0]) == 100
    assert len(chunks[1]) == 100
    assert len(chunks[2]) == 90


@pytest.mark.parametrize(
    "chunk_size, overlap",
    [
        (0, 10),
        (-1, 10),
        (100, -1),
        (100, 100),
        (100, 150),
    ],
)
def test_invalid_chunk_configuration(
    chunk_size,
    overlap,
):
    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )