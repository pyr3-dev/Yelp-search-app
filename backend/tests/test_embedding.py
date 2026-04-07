import pytest
from sentence_transformers import SentenceTransformer
from services.embedding import embed, load_model


@pytest.fixture(scope="module")
def model() -> SentenceTransformer:
    return load_model()


def test_embed_returns_384_floats(model):
    result = embed("AI in rice farming", model)
    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(v, float) for v in result)


def test_embed_different_texts_produce_different_vectors(model):
    v1 = embed("machine learning", model)
    v2 = embed("quantum physics", model)
    assert v1 != v2


def test_embed_similar_texts_produce_close_vectors(model):
    v1 = embed("AI in agriculture", model)
    v2 = embed("machine learning for farming", model)
    v_dissimilar = embed("ancient roman architecture", model)
    dot_similar = sum(a * b for a, b in zip(v1, v2))
    dot_dissimilar = sum(a * b for a, b in zip(v1, v_dissimilar))
    assert dot_similar > dot_dissimilar, (
        f"Expected similar pair ({dot_similar:.3f}) to score higher than dissimilar pair ({dot_dissimilar:.3f})"
    )
