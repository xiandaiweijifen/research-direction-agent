import pytest

from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.providers import (
    ArxivEvidenceProvider,
    FallbackEvidenceProvider,
    MockTopicAgentEvidenceProvider,
    _parse_arxiv_response,
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


def test_fallback_provider_returns_mock_records_when_primary_fails():
    class FailingProvider:
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

    records = provider.retrieve(request)

    assert len(records) == 3
    assert records[0].source_id == "source_1"
