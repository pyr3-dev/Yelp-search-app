import pytest
from services.llm import StubProvider, get_llm_provider


@pytest.mark.asyncio
async def test_stub_provider_returns_correct_shape():
    provider = StubProvider()
    papers = [
        {"openalex_id": "W001", "title": "Paper A", "abstract": "Abstract A"},
        {"openalex_id": "W002", "title": "Paper B", "abstract": "Abstract B"},
    ]
    result = await provider.generate_ideas(papers)

    assert "per_paper" in result
    assert "synthesis" in result
    assert isinstance(result["per_paper"], list)
    assert len(result["per_paper"]) >= 1
    assert "paper_id" in result["per_paper"][0]
    assert "result" in result["per_paper"][0]
    assert "gap" in result["per_paper"][0]
    assert "opportunity" in result["per_paper"][0]
    assert isinstance(result["synthesis"], list)
    assert len(result["synthesis"]) >= 1
    assert "title" in result["synthesis"][0]
    assert "rationale" in result["synthesis"][0]
    assert "confidence" in result["synthesis"][0]


@pytest.mark.asyncio
async def test_stub_provider_per_paper_max_3():
    provider = StubProvider()
    papers = [{"openalex_id": f"W00{i}", "title": f"Paper {i}", "abstract": "x"} for i in range(10)]
    result = await provider.generate_ideas(papers)
    assert len(result["per_paper"]) == 3


def test_get_llm_provider_default_returns_stub():
    provider = get_llm_provider()
    assert isinstance(provider, StubProvider)
