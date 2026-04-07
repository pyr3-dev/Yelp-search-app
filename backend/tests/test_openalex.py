import pytest
from services.openalex import reconstruct_abstract, _parse_paper


def test_reconstruct_abstract_empty():
    assert reconstruct_abstract(None) == ""
    assert reconstruct_abstract({}) == ""


def test_reconstruct_abstract_basic():
    inverted = {"Hello": [0], "world": [1], "from": [2], "OpenAlex": [3]}
    result = reconstruct_abstract(inverted)
    assert result == "Hello world from OpenAlex"


def test_reconstruct_abstract_out_of_order_keys():
    inverted = {"world": [1], "Hello": [0]}
    result = reconstruct_abstract(inverted)
    assert result == "Hello world"


def test_parse_paper_extracts_openalex_id():
    work = {
        "id": "https://openalex.org/W12345",
        "title": "Test Paper",
        "abstract_inverted_index": {"Test": [0], "abstract": [1]},
        "publication_year": 2023,
        "cited_by_count": 42,
        "authorships": [],
        "topics": [],
        "keywords": [],
        "primary_location": None,
        "open_access": {"is_oa": True, "oa_url": "https://example.com/paper.pdf"},
        "best_oa_location": {"pdf_url": "https://example.com/paper.pdf"},
    }
    result = _parse_paper(work)
    assert result["openalex_id"] == "W12345"
    assert result["title"] == "Test Paper"
    assert result["abstract"] == "Test abstract"
    assert result["year"] == 2023
    assert result["citation_count"] == 42
    assert result["is_open_access"] is True


def test_parse_paper_handles_missing_optional_fields():
    work = {
        "id": "https://openalex.org/W99",
        "title": "Minimal Paper",
        "abstract_inverted_index": {"x": [0]},
        "publication_year": 2024,
        "cited_by_count": 0,
        "authorships": [],
        "topics": [],
        "keywords": [],
        "primary_location": None,
        "open_access": None,
        "best_oa_location": None,
    }
    result = _parse_paper(work)
    assert result["doi"] is None
    assert result["journal_name"] is None
    assert result["oa_url"] is None
    assert result["is_open_access"] is False
