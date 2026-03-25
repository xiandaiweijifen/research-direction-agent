import pytest

from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.providers import (
    ArxivEvidenceProvider,
    FallbackEvidenceProvider,
    MockTopicAgentEvidenceProvider,
    _parse_arxiv_response,
    _rank_records,
    build_topic_agent_provider_registry,
)
from app.services.topic_agent.topic_agent_runtime import _pipeline_provider


def test_topic_agent_provider_registry_registers_mock_provider():
    registry = build_topic_agent_provider_registry()

    assert registry.list_names() == ["arxiv", "arxiv_or_mock", "mock"]
    assert isinstance(registry.get("mock"), MockTopicAgentEvidenceProvider)
    assert isinstance(registry.get("arxiv"), ArxivEvidenceProvider)
    assert isinstance(registry.get("arxiv_or_mock"), FallbackEvidenceProvider)


def test_topic_agent_runtime_rejects_unknown_provider_name():
    with pytest.raises(ValueError, match="unknown_topic_agent_provider:unknown"):
        _pipeline_provider("unknown")


def test_parse_arxiv_response_maps_entries_to_topic_agent_records():
    xml_text = """
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2501.12345v1</id>
        <updated>2025-01-20T00:00:00Z</updated>
        <published>2025-01-19T00:00:00Z</published>
        <title>Benchmark Survey For Medical Imaging Reasoning</title>
        <summary>Survey and benchmark coverage for multimodal medical imaging reasoning.</summary>
        <author><name>Jane Doe</name></author>
        <author><name>John Smith</name></author>
      </entry>
    </feed>
    """

    records = _parse_arxiv_response(xml_text)

    assert len(records) == 1
    assert records[0].title == "Benchmark Survey For Medical Imaging Reasoning"
    assert records[0].source_type == "survey"
    assert records[0].source_tier == "A"
    assert records[0].year == 2025
    assert records[0].authors_or_publisher == "Jane Doe, John Smith"
    assert records[0].url == "http://arxiv.org/abs/2501.12345v1"


def test_arxiv_provider_ranking_prefers_records_with_query_term_overlap():
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )
    records = [
        _parse_arxiv_response(
            """
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2501.00001v1</id>
                <updated>2025-01-20T00:00:00Z</updated>
                <published>2025-01-19T00:00:00Z</published>
                <title>Medical Multimodal Reasoning Benchmark</title>
                <summary>Trustworthy reasoning benchmark for medical AI.</summary>
                <author><name>Jane Doe</name></author>
              </entry>
            </feed>
            """
        )[0],
        _parse_arxiv_response(
            """
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2501.00002v1</id>
                <updated>2025-01-20T00:00:00Z</updated>
                <published>2025-01-19T00:00:00Z</published>
                <title>Generic Image Segmentation</title>
                <summary>Segmentation method for natural images.</summary>
                <author><name>John Smith</name></author>
              </entry>
            </feed>
            """
        )[0],
    ]

    ranked_records = _rank_records(records, request, max_results=2)

    assert ranked_records[0].title == "Medical Multimodal Reasoning Benchmark"


def test_fallback_provider_returns_mock_records_when_primary_fails():
    class FailingProvider:
        provider_name = "primary"

        def retrieve(self, request: TopicAgentExploreRequest):
            raise RuntimeError("network down")

    request = TopicAgentExploreRequest(
        interest="medical imaging reasoning",
        constraints=TopicAgentConstraintSet(),
    )
    provider = FallbackEvidenceProvider(
        primary=FailingProvider(),
        fallback=MockTopicAgentEvidenceProvider(),
    )

    result = provider.retrieve(request)

    assert len(result.records) == 3
    assert result.records[0].source_id == "source_1"
    assert result.diagnostics.requested_provider == "primary"
    assert result.diagnostics.used_provider == "mock"
    assert result.diagnostics.fallback_used is True
    assert "RuntimeError:network down" == result.diagnostics.fallback_reason
