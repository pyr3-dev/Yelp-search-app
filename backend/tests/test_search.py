from services.search import normalize_query


def test_normalize_lowercases():
    assert normalize_query("AI Farming") == "ai farming"


def test_normalize_sorts_words():
    assert normalize_query("Farming AI") == normalize_query("AI Farming")


def test_normalize_strips_whitespace():
    assert normalize_query("  machine learning  ") == "learning machine"


def test_normalize_consistent_for_synonymous_order():
    assert normalize_query("rice AI farming") == normalize_query("farming rice AI")
