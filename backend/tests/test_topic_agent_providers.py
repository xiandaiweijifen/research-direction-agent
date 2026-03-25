import pytest

from app.services.topic_agent.providers import (
    MockTopicAgentEvidenceProvider,
    build_topic_agent_provider_registry,
)
from app.services.topic_agent.topic_agent_runtime import _pipeline_provider


def test_topic_agent_provider_registry_registers_mock_provider():
    registry = build_topic_agent_provider_registry()

    assert registry.list_names() == ["mock"]
    assert isinstance(registry.get("mock"), MockTopicAgentEvidenceProvider)


def test_topic_agent_runtime_rejects_unknown_provider_name():
    with pytest.raises(ValueError, match="unknown_topic_agent_provider:unknown"):
        _pipeline_provider("unknown")
