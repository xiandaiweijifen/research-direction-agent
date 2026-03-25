from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.schemas.topic_agent import TopicAgentExploreRequest, TopicAgentSourceRecord


class TopicAgentEvidenceProvider(Protocol):
    def retrieve(self, request: TopicAgentExploreRequest) -> list[TopicAgentSourceRecord]:
        ...


@dataclass
class TopicAgentEvidenceProviderRegistry:
    providers: dict[str, TopicAgentEvidenceProvider] = field(default_factory=dict)

    def register(self, name: str, provider: TopicAgentEvidenceProvider) -> None:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("provider_name_must_not_be_empty")
        self.providers[normalized_name] = provider

    def get(self, name: str) -> TopicAgentEvidenceProvider:
        normalized_name = name.strip().lower()
        if normalized_name not in self.providers:
            raise KeyError(normalized_name)
        return self.providers[normalized_name]

    def list_names(self) -> list[str]:
        return sorted(self.providers.keys())


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class MockTopicAgentEvidenceProvider:
    def retrieve(self, request: TopicAgentExploreRequest) -> list[TopicAgentSourceRecord]:
        base_topic = request.interest.strip()
        domain = _normalize_optional(request.problem_domain) or "the target domain"
        return [
            TopicAgentSourceRecord(
                source_id="source_1",
                title=f"Recent Survey On {base_topic.title()}",
                source_type="survey",
                source_tier="A",
                year=2025,
                authors_or_publisher="Survey Authors",
                identifier="survey:source_1",
                url="https://example.org/survey/source_1",
                summary=f"A survey-style summary of methods, benchmarks, and open questions in {base_topic}.",
                relevance_reason="Provides a high-level map of the research landscape.",
            ),
            TopicAgentSourceRecord(
                source_id="source_2",
                title=f"Benchmarking Practical Methods For {domain.title()}",
                source_type="benchmark",
                source_tier="A",
                year=2024,
                authors_or_publisher="Benchmark Team",
                identifier="benchmark:source_2",
                url="https://example.org/benchmark/source_2",
                summary=f"Benchmark-oriented evidence describing evaluation patterns related to {base_topic}.",
                relevance_reason="Helps estimate feasibility and evaluation setup.",
            ),
            TopicAgentSourceRecord(
                source_id="source_3",
                title=f"Open Repository For {base_topic.title()} Experiments",
                source_type="code",
                source_tier="B",
                year=2024,
                authors_or_publisher="Open Source Maintainers",
                identifier="repo:source_3",
                url="https://example.org/code/source_3",
                summary=f"An implementation-oriented resource with reusable baselines for {base_topic}.",
                relevance_reason="Supports feasibility assessment for a first project iteration.",
            ),
        ]


def build_topic_agent_provider_registry() -> TopicAgentEvidenceProviderRegistry:
    registry = TopicAgentEvidenceProviderRegistry()
    registry.register("mock", MockTopicAgentEvidenceProvider())
    return registry
