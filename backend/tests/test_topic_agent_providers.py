import json

import httpx
import pytest

from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.providers import (
    OPENALEX_CACHE_SCHEMA_VERSION,
    ArxivEvidenceProvider,
    FallbackEvidenceProvider,
    MockTopicAgentEvidenceProvider,
    OpenAlexEvidenceProvider,
    _build_cache_key,
    _build_arxiv_query,
    _core_query_terms,
    _filter_ranked_records,
    _http_get_with_retries,
    _parse_openalex_response,
    _parse_arxiv_response,
    _rank_records,
    build_topic_agent_provider_registry,
)
from app.services.topic_agent.topic_agent_runtime import _pipeline_provider


def test_topic_agent_provider_registry_registers_mock_provider():
    registry = build_topic_agent_provider_registry()

    assert registry.list_names() == [
        "arxiv",
        "arxiv_or_mock",
        "mock",
        "openalex",
        "openalex_or_arxiv_or_mock",
    ]
    assert isinstance(registry.get("mock"), MockTopicAgentEvidenceProvider)
    assert isinstance(registry.get("arxiv"), ArxivEvidenceProvider)
    assert isinstance(registry.get("openalex"), OpenAlexEvidenceProvider)
    assert isinstance(registry.get("arxiv_or_mock"), FallbackEvidenceProvider)
    assert isinstance(registry.get("openalex_or_arxiv_or_mock"), FallbackEvidenceProvider)


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


def test_parse_openalex_response_maps_entries_to_topic_agent_records():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "display_name": "Benchmarking Grounded Medical Reasoning",
                "publication_year": 2025,
                "abstract_inverted_index": {
                    "Benchmark": [0],
                    "for": [1],
                    "grounded": [2],
                    "medical": [3],
                    "reasoning": [4],
                },
                "authorships": [
                    {"author": {"display_name": "Jane Doe"}},
                    {"author": {"display_name": "John Smith"}},
                ],
                "primary_location": {
                    "landing_page_url": "https://example.org/paper"
                },
            }
        ]
    }

    records = _parse_openalex_response(payload)

    assert len(records) == 1
    assert records[0].title == "Benchmarking Grounded Medical Reasoning"
    assert records[0].source_type == "benchmark"
    assert records[0].source_tier == "A"
    assert records[0].authors_or_publisher == "Jane Doe, John Smith"
    assert records[0].url == "https://example.org/paper"
    assert records[0].source_id == "openalex_w123"


def test_build_arxiv_query_prioritizes_interest_phrase_and_core_terms():
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )

    query = _build_arxiv_query(request)

    assert '"trustworthy multimodal reasoning in medical imaging"' in query
    assert "trustworthy" in query
    assert "multimodal" in query
    assert "reasoning" in query


def test_core_query_terms_are_derived_from_request_instead_of_fixed_keywords():
    request = TopicAgentExploreRequest(
        interest="causal representation learning for clinical time series",
        problem_domain="healthcare ML",
        constraints=TopicAgentConstraintSet(),
    )

    terms = _core_query_terms(request)

    assert "causal" in terms
    assert "representation" in terms
    assert "clinical" in terms
    assert "series" in terms


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
        _parse_arxiv_response(
            """
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <id>http://arxiv.org/abs/2501.00003v1</id>
                <updated>2025-01-20T00:00:00Z</updated>
                <published>2025-01-19T00:00:00Z</published>
                <title>Trustworthy Multimodal Medical Reasoning</title>
                <summary>Reasoning and trustworthiness analysis for multimodal medical models.</summary>
                <author><name>Alice Kim</name></author>
              </entry>
            </feed>
            """
        )[0],
    ]

    ranked_records = _rank_records(records, request, max_results=3)

    assert ranked_records[0].title == "Medical Multimodal Reasoning Benchmark"
    assert ranked_records[1].title == "Trustworthy Multimodal Medical Reasoning"


def test_filter_ranked_records_prefers_core_term_overlap():
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )
    records = _parse_arxiv_response(
        """
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2501.00001v1</id>
            <updated>2025-01-20T00:00:00Z</updated>
            <published>2025-01-19T00:00:00Z</published>
            <title>Trustworthy Multimodal Medical Reasoning Benchmark</title>
            <summary>Medical benchmark for trustworthy reasoning.</summary>
            <author><name>Jane Doe</name></author>
          </entry>
          <entry>
            <id>http://arxiv.org/abs/2501.00002v1</id>
            <updated>2025-01-20T00:00:00Z</updated>
            <published>2025-01-19T00:00:00Z</published>
            <title>Deep Learning for Medical Image Segmentation</title>
            <summary>Generic segmentation method in medical imaging.</summary>
            <author><name>John Smith</name></author>
          </entry>
        </feed>
        """
    )

    filtered_records = _filter_ranked_records(records, request, max_results=2)

    assert len(filtered_records) == 1
    assert filtered_records[0].title == "Trustworthy Multimodal Medical Reasoning Benchmark"


def test_arxiv_provider_uses_cache_when_query_key_is_present(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )
    cache_path = workspace_tmp_path / "topic_agent_arxiv_cache.json"
    provider = ArxivEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600)

    class FakeResponse:
        text = """
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2603.03437v1</id>
            <updated>2026-03-20T00:00:00Z</updated>
            <published>2026-03-19T00:00:00Z</published>
            <title>Trustworthy Multimodal Medical Reasoning Benchmark</title>
            <summary>Medical benchmark for trustworthy reasoning.</summary>
            <author><name>Jane Doe</name></author>
          </entry>
        </feed>
        """

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(),
    )
    first_result = provider.retrieve(request)
    assert first_result.diagnostics.cache_hit is False

    def fail_http_get(*args, **kwargs):
        raise AssertionError("httpx.get should not be called on cache hit")

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", fail_http_get)

    cached_result = provider.retrieve(request)

    assert cached_result.diagnostics.cache_hit is True
    assert cached_result.records


def test_openalex_provider_uses_cache_when_query_key_is_present(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600)

    class FakeResponse:
        def json(self):
            return {
                "results": [
                    {
                        "id": "https://openalex.org/W123",
                        "display_name": "Benchmarking Grounded Medical Reasoning",
                        "publication_year": 2025,
                        "abstract_inverted_index": {
                            "Benchmark": [0],
                            "for": [1],
                            "grounded": [2],
                            "medical": [3],
                            "reasoning": [4],
                        },
                        "authorships": [
                            {"author": {"display_name": "Jane Doe"}},
                        ],
                        "primary_location": {
                            "landing_page_url": "https://example.org/paper"
                        },
                    }
                ]
            }

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(),
    )
    first_result = provider.retrieve(request)
    assert first_result.diagnostics.cache_hit is False

    def fail_http_get(*args, **kwargs):
        raise AssertionError("httpx.get should not be called on cache hit")

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", fail_http_get)

    cached_result = provider.retrieve(request)

    assert cached_result.diagnostics.cache_hit is True
    assert cached_result.records[0].source_id == "openalex_w123"


def test_http_get_with_retries_retries_transient_connect_errors(monkeypatch):
    call_count = {"value": 0}

    class FakeResponse:
        def raise_for_status(self):
            return None

    def flaky_get(*args, **kwargs):
        call_count["value"] += 1
        if call_count["value"] < 3:
            raise httpx.ConnectError("temporary reset")
        return FakeResponse()

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", flaky_get)

    response = _http_get_with_retries(
        "https://example.org",
        params={"search": "test"},
        timeout_seconds=10.0,
        max_retries=2,
        user_agent="research-topic-copilot/0.1",
    )

    assert isinstance(response, FakeResponse)
    assert call_count["value"] == 3


def test_http_get_with_retries_raises_after_retry_budget(monkeypatch):
    def always_fail(*args, **kwargs):
        raise httpx.ReadTimeout("still timing out")

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", always_fail)

    with pytest.raises(httpx.ReadTimeout):
        _http_get_with_retries(
            "https://example.org",
            params={"search": "test"},
            timeout_seconds=10.0,
            max_retries=1,
            user_agent="research-topic-copilot/0.1",
        )


def test_openalex_provider_normalizes_legacy_cached_source_ids(workspace_tmp_path):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600)
    cache_key = (
        f"{OPENALEX_CACHE_SCHEMA_VERSION}::"
        "trustworthy multimodal reasoning medical imaging applied||"
        "trustworthy multimodal reasoning medical||"
        "multimodal reasoning medical benchmark||"
        "trustworthy reasoning medical evaluation::max=5"
    )
    cache_path.write_text(
        json.dumps(
            {
                cache_key: {
                    "saved_at": "2026-03-25T20:48:24.956512+08:00",
                    "records": [
                        {
                            "source_id": "openalex_2",
                            "title": "Building an Ethical and Trustworthy Biomedical AI Ecosystem",
                            "source_type": "paper",
                            "source_tier": "B",
                            "year": 2024,
                            "authors_or_publisher": "Author A",
                            "identifier": "https://openalex.org/W4402987506",
                            "url": "https://doi.org/10.3390/example",
                            "summary": "Summary A",
                            "relevance_reason": "Test",
                        },
                        {
                            "source_id": "openalex_2",
                            "title": "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology",
                            "source_type": "benchmark",
                            "source_tier": "A",
                            "year": 2025,
                            "authors_or_publisher": "Author B",
                            "identifier": "https://openalex.org/W4414530509",
                            "url": "https://arxiv.org/abs/2508.13192",
                            "summary": "Summary B",
                            "relevance_reason": "Test",
                        },
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    result = provider.retrieve(request)

    assert result.diagnostics.cache_hit is True
    assert [record.source_id for record in result.records] == [
        "openalex_w4414530509",
    ]
    normalized_cache = cache_path.read_text(encoding="utf-8")
    assert "openalex_w4414530509" in normalized_cache
    assert cache_key in normalized_cache


def test_openalex_cache_key_is_versioned():
    key = _build_cache_key(
        "trustworthy multimodal reasoning medical imaging applied",
        5,
        version=OPENALEX_CACHE_SCHEMA_VERSION,
    )

    assert key.startswith(f"{OPENALEX_CACHE_SCHEMA_VERSION}::")


def test_openalex_provider_ignores_legacy_unversioned_cache_key(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600)
    legacy_key = (
        "trustworthy multimodal reasoning medical imaging applied||"
        "trustworthy multimodal reasoning medical||"
        "multimodal reasoning medical benchmark||"
        "trustworthy reasoning medical evaluation::max=5"
    )
    cache_path.write_text(
        f"""
        {{
          "{legacy_key}": {{
            "saved_at": "2026-03-25T20:48:24.956512+08:00",
            "records": [
              {{
                "source_id": "openalex_2",
                "title": "Legacy Cached Result",
                "source_type": "paper",
                "source_tier": "B",
                "year": 2024,
                "authors_or_publisher": "Author A",
                "identifier": "https://openalex.org/W4402987506",
                "url": "https://doi.org/10.3390/example",
                "summary": "Legacy summary",
                "relevance_reason": "Test"
              }}
            ]
          }}
        }}
        """.strip(),
        encoding="utf-8",
    )

    class FakeResponse:
        def json(self):
            return {
                "results": [
                    {
                        "id": "https://openalex.org/W4414530509",
                        "display_name": "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology",
                        "publication_year": 2025,
                        "abstract_inverted_index": {
                            "Benchmarking": [0],
                            "multimodal": [1],
                            "medical": [2],
                            "reasoning": [3],
                            "radiology": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author B"}}],
                        "primary_location": {"landing_page_url": "https://example.org/benchmark"},
                    }
                ]
            }

        def raise_for_status(self):
            return None

    call_count = {"value": 0}

    def fake_http_get(*args, **kwargs):
        call_count["value"] += 1
        return FakeResponse()

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", fake_http_get)

    result = provider.retrieve(request)

    assert call_count["value"] >= 1
    assert result.diagnostics.cache_hit is False
    assert result.records[0].source_id == "openalex_w4414530509"


def test_openalex_provider_merges_multi_query_results_and_dedupes(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600, max_results=5)

    call_count = {"value": 0}

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

        def raise_for_status(self):
            return None

    def fake_http_get(*args, **kwargs):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return FakeResponse(
                {
                    "results": [
                        {
                            "id": "https://openalex.org/W123",
                            "display_name": "Medical Multimodal Reasoning Benchmark",
                            "publication_year": 2025,
                            "abstract_inverted_index": {
                                "Medical": [0],
                                "multimodal": [1],
                                "reasoning": [2],
                                "benchmark": [3],
                            },
                            "authorships": [{"author": {"display_name": "Jane Doe"}}],
                            "primary_location": {"landing_page_url": "https://example.org/paper1"},
                        }
                    ]
                }
            )
        return FakeResponse(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W123",
                        "display_name": "Medical Multimodal Reasoning Benchmark",
                        "publication_year": 2025,
                        "abstract_inverted_index": {
                            "Medical": [0],
                            "multimodal": [1],
                            "reasoning": [2],
                            "benchmark": [3],
                        },
                        "authorships": [{"author": {"display_name": "Jane Doe"}}],
                        "primary_location": {"landing_page_url": "https://example.org/paper1"},
                    },
                    {
                        "id": "https://openalex.org/W456",
                        "display_name": "Trustworthy Evaluation for Medical Reasoning",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "Trustworthy": [0],
                            "evaluation": [1],
                            "medical": [2],
                            "reasoning": [3],
                        },
                        "authorships": [{"author": {"display_name": "John Smith"}}],
                        "primary_location": {"landing_page_url": "https://example.org/paper2"},
                    },
                ]
            }
        )

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", fake_http_get)

    result = provider.retrieve(request)

    assert call_count["value"] >= 2
    assert len(result.records) == 2
    assert {record.source_id for record in result.records} == {"openalex_w123", "openalex_w456"}


def test_openalex_reranking_prefers_task_specific_benchmarks_over_generic_reviews(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600, max_results=5)

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

        def raise_for_status(self):
            return None

    payload = {
        "results": [
            {
                "id": "https://openalex.org/W4402987506",
                "display_name": "Building an Ethical and Trustworthy Biomedical AI Ecosystem for the Translational and Clinical Integration of Foundation Models",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "Ethical": [0],
                    "and": [1],
                    "trustworthy": [2],
                    "biomedical": [3],
                    "AI": [4],
                    "ecosystem": [5],
                    "for": [6],
                    "clinical": [7],
                    "integration": [8],
                },
                "authorships": [{"author": {"display_name": "Author A"}}],
                "primary_location": {"landing_page_url": "https://example.org/review"},
            },
            {
                "id": "https://openalex.org/W4414530509",
                "display_name": "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology",
                "publication_year": 2025,
                "abstract_inverted_index": {
                    "Benchmarking": [0],
                    "zero-shot": [1],
                    "multimodal": [2],
                    "medical": [3],
                    "reasoning": [4],
                    "radiology": [5],
                    "grounding": [6],
                },
                "authorships": [{"author": {"display_name": "Author B"}}],
                "primary_location": {"landing_page_url": "https://example.org/benchmark"},
            },
            {
                "id": "https://openalex.org/W4401863364",
                "display_name": "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "Multimodal": [0],
                    "benchmark": [1],
                    "medical": [2],
                    "document": [3],
                    "question": [4],
                    "answering": [5],
                    "clinical": [6],
                    "reasoning": [7],
                },
                "authorships": [{"author": {"display_name": "Author C"}}],
                "primary_location": {"landing_page_url": "https://example.org/docqa"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert ranked_titles[0] == "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology"
    assert ranked_titles[1] == "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning"
    assert "Building an Ethical and Trustworthy Biomedical AI Ecosystem for the Translational and Clinical Integration of Foundation Models" not in ranked_titles[:2]


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
