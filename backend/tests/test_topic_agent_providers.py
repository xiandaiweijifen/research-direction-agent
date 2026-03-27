import json
from datetime import datetime, timezone

import httpx
import pytest

from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.providers import (
    OPENALEX_CACHE_SCHEMA_VERSION,
    ArxivEvidenceProvider,
    FallbackEvidenceProvider,
    MockTopicAgentEvidenceProvider,
    OpenAlexEvidenceProvider,
    OpenAlexQueryRoute,
    _build_openalex_retrieval_plan,
    _build_openalex_query_routes,
    _build_openalex_queries,
    _build_cache_key,
    _build_arxiv_query,
    _core_query_terms,
    _filter_ranked_records,
    _http_get_with_retries,
    _infer_evidence_roles,
    _is_code_repair_query,
    _openalex_raw_pool_size,
    _truncate_openalex_query_routes,
    _parse_openalex_response,
    _parse_arxiv_response,
    _rank_records,
    _topic_relevance_label,
    _topic_fit_score,
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


def test_infer_evidence_roles_distinguishes_method_and_off_target_neighbor_for_modern_agent_queries():
    request = TopicAgentExploreRequest(
        interest="llm agents for software engineering",
        problem_domain="developer tools",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    method_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "display_name": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
                    "publication_year": 2024,
                    "abstract_inverted_index": {
                        "software": [0],
                        "engineering": [1],
                        "benchmark": [2],
                        "coding": [3],
                        "evaluation": [4],
                    },
                    "authorships": [{"author": {"display_name": "Author A"}}],
                    "primary_location": {"landing_page_url": "https://example.org/swebench"},
                }
            ]
        }
    )[0]
    legacy_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W2",
                    "display_name": "Capturing agent autonomy in roles and XML",
                    "publication_year": 2003,
                    "abstract_inverted_index": {
                        "agent": [0],
                        "autonomy": [1],
                        "roles": [2],
                        "xml": [3],
                    },
                    "authorships": [{"author": {"display_name": "Author B"}}],
                    "primary_location": {"landing_page_url": "https://example.org/xml"},
                }
            ]
        }
    )[0]

    assert "benchmark_evaluation" in _infer_evidence_roles(method_record, request)
    assert "method_framework" in _infer_evidence_roles(method_record, request)
    assert "off_target_neighbor" in _infer_evidence_roles(legacy_record, request)


def test_topic_fit_score_prefers_modern_agent_software_records_over_legacy_agent_neighbors():
    request = TopicAgentExploreRequest(
        interest="llm agents for software engineering",
        problem_domain="developer tools",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    modern_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "display_name": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
                    "publication_year": 2024,
                    "abstract_inverted_index": {
                        "software": [0],
                        "engineering": [1],
                        "benchmark": [2],
                        "coding": [3],
                        "evaluation": [4],
                        "developer": [5],
                    },
                    "authorships": [{"author": {"display_name": "Author A"}}],
                    "primary_location": {"landing_page_url": "https://example.org/swebench"},
                }
            ]
        }
    )[0]
    legacy_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W2",
                    "display_name": "Multi-Agent Systems",
                    "publication_year": 2010,
                    "abstract_inverted_index": {
                        "multi-agent": [0],
                        "systems": [1],
                        "autonomy": [2],
                    },
                    "authorships": [{"author": {"display_name": "Author B"}}],
                    "primary_location": {"landing_page_url": "https://example.org/legacy"},
                }
            ]
        }
    )[0]

    assert _topic_fit_score(modern_record, request) > _topic_fit_score(legacy_record, request)


def test_topic_relevance_label_distinguishes_topic_relevant_neighbor_and_lexical_match():
    request = TopicAgentExploreRequest(
        interest="program repair with llm agents",
        problem_domain="software engineering",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    relevant_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "display_name": "RepairAgent: An Autonomous, LLM-Based Agent for Program Repair",
                    "publication_year": 2025,
                    "abstract_inverted_index": {
                        "program": [0],
                        "repair": [1],
                        "agent": [2],
                        "github": [3],
                        "issues": [4],
                        "evaluation": [5],
                    },
                    "authorships": [{"author": {"display_name": "Author A"}}],
                    "primary_location": {"landing_page_url": "https://example.org/repairagent"},
                }
            ]
        }
    )[0]
    neighbor_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W2",
                    "display_name": "How to design a program repair bot?",
                    "publication_year": 2018,
                    "abstract_inverted_index": {
                        "program": [0],
                        "repair": [1],
                        "bot": [2],
                        "github": [3],
                        "projects": [4],
                    },
                    "authorships": [{"author": {"display_name": "Author B"}}],
                    "primary_location": {"landing_page_url": "https://example.org/repairnator"},
                }
            ]
        }
    )[0]
    lexical_record = _parse_openalex_response(
        {
            "results": [
                {
                    "id": "https://openalex.org/W3",
                    "display_name": "Technological Structure for Technology Integration in the Classroom, Inspired by the Maker Culture",
                    "publication_year": 2020,
                    "abstract_inverted_index": {
                        "technology": [0],
                        "integration": [1],
                        "classroom": [2],
                        "maker": [3],
                        "repair": [4],
                    },
                    "authorships": [{"author": {"display_name": "Author C"}}],
                    "primary_location": {"landing_page_url": "https://example.org/classroom"},
                }
            ]
        }
    )[0]

    assert _topic_relevance_label(relevant_record, request) == "topic_relevant"
    assert _topic_relevance_label(neighbor_record, request) in {"topic_relevant", "domain_neighbor"}
    assert _topic_relevance_label(lexical_record, request) == "lexical_match"


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

    response, metrics = _http_get_with_retries(
        "https://example.org",
        params={"search": "test"},
        timeout_seconds=10.0,
        max_retries=2,
        user_agent="research-topic-copilot/0.1",
    )

    assert isinstance(response, FakeResponse)
    assert call_count["value"] == 3
    assert metrics.attempt_count == 3
    assert metrics.latency_ms >= 0


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
    cache_key = _build_cache_key(
        "||".join(_build_openalex_queries(request)),
        provider.max_results,
        version=OPENALEX_CACHE_SCHEMA_VERSION,
    )
    cache_path.write_text(
        json.dumps(
                {
                    cache_key: {
                        "saved_at": datetime.now(timezone.utc).isoformat(),
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


def test_openalex_queries_expand_radiology_vqa_aliases():
    request = TopicAgentExploreRequest(
        interest="trustworthy visual question answering in radiology",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)
    joined_queries = " || ".join(queries).lower()

    assert "med-vqa" in joined_queries
    assert "medical vqa" in joined_queries
    assert "vqa-rad radiology" in joined_queries


def test_openalex_queries_expand_clinical_medical_reasoning_aliases():
    request = TopicAgentExploreRequest(
        interest="clinical medical reasoning",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)
    joined_queries = " || ".join(queries)

    assert "clinical reasoning benchmark" in joined_queries
    assert "clinical decision support reasoning evaluation" in joined_queries
    assert "medical reasoning metacognition benchmark" in joined_queries
    assert "free-response clinical reasoning evaluation" in joined_queries


def test_openalex_queries_expand_generic_medical_reasoning_aliases():
    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)
    joined_queries = " || ".join(queries).lower()

    assert "medical reasoning benchmark" in joined_queries
    assert "medical reasoning large language models" in joined_queries
    assert "clinical reasoning benchmark medical ai" in joined_queries


def test_openalex_queries_add_general_research_role_expansions_for_modern_topics():
    request = TopicAgentExploreRequest(
        interest="coding agents for software engineering",
        problem_domain="developer workflows",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)
    joined_queries = " || ".join(queries).lower()

    assert "coding agents for software engineering developer workflows benchmark evaluation" in joined_queries
    assert "coding agents for software engineering developer workflows method framework" in joined_queries
    assert "coding agents for software engineering developer workflows workflow reproducibility" in joined_queries
    assert "coding agents for software engineering developer workflows practical baseline adaptation" in joined_queries


def test_openalex_queries_are_capped_to_reduce_request_fan_out():
    request = TopicAgentExploreRequest(
        interest="trustworthy visual question answering in radiology",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)

    assert len(queries) <= 10


def test_openalex_query_routes_keep_base_alias_and_role_groups_explicit():
    request = TopicAgentExploreRequest(
        interest="trustworthy visual question answering in radiology",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    routes = _build_openalex_query_routes(request)
    route_names = [route.name for route in routes]
    flattened = _build_openalex_queries(request)

    assert route_names[0] == "base"
    assert "alias" in route_names
    assert "role_expansion" in route_names
    assert flattened == [query for route in routes for query in route.queries]


def test_openalex_queries_keep_software_agent_fan_out_small_for_interactive_use():
    request = TopicAgentExploreRequest(
        interest="llm repository repair workflows",
        problem_domain="software engineering evaluation",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    queries = _build_openalex_queries(request)

    assert len(queries) <= 6


def test_openalex_query_route_truncation_preserves_route_order_while_capping_total_queries():
    routes = [
        OpenAlexQueryRoute(name="base", queries=["q1"]),
        OpenAlexQueryRoute(name="alias", queries=["q2", "q3"]),
        OpenAlexQueryRoute(name="role_expansion", queries=["q4", "q5"]),
    ]

    truncated = _truncate_openalex_query_routes(routes, 3)

    assert [(route.name, route.queries) for route in truncated] == [
        ("base", ["q1"]),
        ("alias", ["q2", "q3"]),
    ]


def test_openalex_retrieval_plan_reuses_query_bundle_for_cache_key():
    request = TopicAgentExploreRequest(
        interest="llm repository repair workflows",
        problem_domain="software engineering evaluation",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    plan = _build_openalex_retrieval_plan(request, 5)

    assert plan.query_texts == _build_openalex_queries(request)
    assert plan.raw_pool_size == _openalex_raw_pool_size(5)
    assert plan.cache_key == _build_cache_key(
        "||".join(plan.query_texts),
        5,
        version=OPENALEX_CACHE_SCHEMA_VERSION,
    )


def test_code_repair_query_detection_handles_repository_repair_workflows():
    assert _is_code_repair_query("llm repository repair workflows software engineering evaluation")


def test_openalex_provider_reports_latency_and_query_diagnostics(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="repository-level bug-fixing agents",
        problem_domain="software engineering evaluation",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {
                        "id": "https://openalex.org/W4400582844",
                        "display_name": "CodePlan: Repository-Level Coding using LLMs and Planning",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "repository": [0],
                            "level": [1],
                            "coding": [2],
                            "planning": [3],
                        },
                        "authorships": [{"author": {"display_name": "Author A"}}],
                        "primary_location": {"landing_page_url": "https://example.org/codeplan"},
                    }
                ]
            }

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", lambda *args, **kwargs: FakeResponse())

    result = provider.retrieve(request)

    assert result.diagnostics.query_count >= 1
    assert result.diagnostics.provider_latency_ms is not None
    assert result.diagnostics.provider_latency_ms >= 0
    assert result.diagnostics.query_diagnostics
    assert result.diagnostics.slowest_query is not None
    assert result.diagnostics.slowest_query_latency_ms is not None
    assert all("route" in item for item in result.diagnostics.query_diagnostics)
    assert all("attempt_count" in item for item in result.diagnostics.query_diagnostics)


def test_openalex_provider_filters_off_target_repository_workflow_neighbors(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="llm repository repair workflows",
        problem_domain="software engineering evaluation",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600, max_results=5)

    class FakeResponse:
        def json(self):
            return {
                "results": [
                    {
                        "id": "https://openalex.org/W4403788984",
                        "display_name": "HyperAgent: Generalist Software Engineering Agents to Solve Coding Tasks at Scale",
                        "publication_year": 2024,
                        "type": "article",
                        "abstract_inverted_index": {
                            "repository-level": [0],
                            "program": [1],
                            "repair": [2],
                            "benchmark": [3],
                            "workflow": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author A"}}],
                        "primary_location": {"landing_page_url": "https://example.org/hyperagent"},
                    },
                    {
                        "id": "https://openalex.org/W4409724980",
                        "display_name": "Coding Agents: A Comprehensive Survey of Automated Bug Fixing Systems and Benchmarks",
                        "publication_year": 2025,
                        "type": "article",
                        "abstract_inverted_index": {
                            "automated": [0],
                            "bug": [1],
                            "fixing": [2],
                            "repository-level": [3],
                            "benchmark": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author B"}}],
                        "primary_location": {"landing_page_url": "https://example.org/coding-agents"},
                    },
                    {
                        "id": "https://openalex.org/W1497744507",
                        "display_name": "SAP R/3 business blueprint (2nd ed.): understanding enterprise supply chain management",
                        "publication_year": 1999,
                        "type": "book",
                        "abstract_inverted_index": {
                            "business": [0],
                            "blueprint": [1],
                            "workflow": [2],
                            "enterprise": [3],
                            "software": [4],
                            "engineering": [5],
                            "autonomous": [6],
                            "agents": [7],
                        },
                        "authorships": [{"author": {"display_name": "Author C"}}],
                        "primary_location": {"landing_page_url": "https://example.org/sap"},
                    },
                ]
            }

        def raise_for_status(self):
            return None

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", lambda *args, **kwargs: FakeResponse())

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert "SAP R/3 business blueprint (2nd ed.): understanding enterprise supply chain management" not in ranked_titles
    assert "HyperAgent: Generalist Software Engineering Agents to Solve Coding Tasks at Scale" in ranked_titles


def test_openalex_raw_pool_size_fetches_more_than_final_max_results():
    assert _openalex_raw_pool_size(5) == 20
    assert _openalex_raw_pool_size(3) == 15


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


def test_openalex_provider_fetches_larger_raw_pool_than_final_result_limit(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="coding agents for software engineering",
        problem_domain="developer workflows",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600, max_results=5)
    observed_per_page: list[int] = []

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

        def raise_for_status(self):
            return None

    def fake_http_get(*args, **kwargs):
        observed_per_page.append(kwargs["params"]["per-page"])
        return FakeResponse({"results": []})

    monkeypatch.setattr("app.services.topic_agent.providers.httpx.get", fake_http_get)

    provider.retrieve(request)

    assert observed_per_page
    assert all(value > provider.max_results for value in observed_per_page)


def test_openalex_provider_collapses_near_duplicate_title_versions(workspace_tmp_path, monkeypatch):
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
                "authorships": [{"author": {"display_name": "Author A"}}],
                "primary_location": {"landing_page_url": "https://doi.org/10.1145/example"},
            },
            {
                "id": "https://openalex.org/W4392181732",
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
                "authorships": [{"author": {"display_name": "Author B"}}],
                "primary_location": {"landing_page_url": "https://arxiv.org/abs/2402.14840"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)

    assert len(result.records) == 1
    assert result.records[0].source_id == "openalex_w4401863364"


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


def test_openalex_reranking_prefers_med_vqa_over_generic_multimodal_overview(workspace_tmp_path, monkeypatch):
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
                "id": "https://openalex.org/W4392881223",
                "display_name": "The application of multimodal large language models in medicine",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "multimodal": [0],
                    "large": [1],
                    "language": [2],
                    "models": [3],
                    "medicine": [4],
                    "overview": [5],
                },
                "authorships": [{"author": {"display_name": "Author A"}}],
                "primary_location": {"landing_page_url": "https://example.org/overview"},
            },
            {
                "id": "https://openalex.org/W3094950914",
                "display_name": "Medical Visual Question Answering via Conditional Reasoning",
                "publication_year": 2020,
                "abstract_inverted_index": {
                    "Medical": [0],
                    "visual": [1],
                    "question": [2],
                    "answering": [3],
                    "conditional": [4],
                    "reasoning": [5],
                    "vqa-rad": [6],
                },
                "authorships": [{"author": {"display_name": "Author B"}}],
                "primary_location": {"landing_page_url": "https://example.org/medvqa"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert ranked_titles[0] == "Medical Visual Question Answering via Conditional Reasoning"
    assert "The application of multimodal large language models in medicine" not in ranked_titles[:1]


def test_openalex_overview_records_are_backfill_only_when_task_specific_records_are_sufficient(workspace_tmp_path, monkeypatch):
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    cache_path = workspace_tmp_path / "topic_agent_openalex_cache.json"
    provider = OpenAlexEvidenceProvider(cache_path=cache_path, cache_ttl_seconds=3600, max_results=3)

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
                "id": "https://openalex.org/W4392881223",
                "display_name": "The application of multimodal large language models in medicine",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "multimodal": [0],
                    "large": [1],
                    "language": [2],
                    "models": [3],
                    "medicine": [4],
                    "overview": [5],
                },
                "authorships": [{"author": {"display_name": "Author A"}}],
                "primary_location": {"landing_page_url": "https://example.org/overview"},
            },
            {
                "id": "https://openalex.org/W4414530509",
                "display_name": "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology",
                "publication_year": 2025,
                "abstract_inverted_index": {
                    "benchmarking": [0],
                    "multimodal": [1],
                    "medical": [2],
                    "reasoning": [3],
                    "radiology": [4],
                    "grounding": [5],
                },
                "authorships": [{"author": {"display_name": "Author B"}}],
                "primary_location": {"landing_page_url": "https://example.org/benchmark"},
            },
            {
                "id": "https://openalex.org/W4401863364",
                "display_name": "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "multimodal": [0],
                    "benchmark": [1],
                    "medical": [2],
                    "document": [3],
                    "question": [4],
                    "answering": [5],
                    "clinical": [6],
                    "reasoning": [7],
                },
                "authorships": [{"author": {"display_name": "Author C"}}],
                "primary_location": {"landing_page_url": "https://example.org/meddqa"},
            },
            {
                "id": "https://openalex.org/W3094950914",
                "display_name": "Medical Visual Question Answering via Conditional Reasoning",
                "publication_year": 2020,
                "abstract_inverted_index": {
                    "medical": [0],
                    "visual": [1],
                    "question": [2],
                    "answering": [3],
                    "conditional": [4],
                    "reasoning": [5],
                    "vqa-rad": [6],
                    "trustworthy": [7],
                    "grounding": [8],
                    "multimodal": [9],
                },
                "authorships": [{"author": {"display_name": "Author D"}}],
                "primary_location": {"landing_page_url": "https://example.org/medvqa"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert ranked_titles == [
        "Benchmarking GPT-5 for Zero-Shot Multimodal Medical Reasoning in Radiology and Radiation Oncology",
        "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning",
        "Medical Visual Question Answering via Conditional Reasoning",
    ]


def test_openalex_reranking_prefers_modern_medical_ai_reasoning_over_legacy_reasoning_records(
    workspace_tmp_path,
    monkeypatch,
):
    request = TopicAgentExploreRequest(
        interest="medical reasoning",
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
                "id": "https://openalex.org/W2023211236",
                "display_name": "Case-based reasoning algorithms applied in a medical acquisition tool",
                "publication_year": 1993,
                "abstract_inverted_index": {
                    "case-based": [0],
                    "reasoning": [1],
                    "medical": [2],
                    "acquisition": [3],
                    "tool": [4],
                },
                "authorships": [{"author": {"display_name": "Legacy Author"}}],
                "primary_location": {"landing_page_url": "https://example.org/legacy"},
            },
            {
                "id": "https://openalex.org/W4406152279",
                "display_name": "Toward expert-level medical question answering with large language models",
                "publication_year": 2025,
                "abstract_inverted_index": {
                    "medical": [0],
                    "question": [1],
                    "answering": [2],
                    "large": [3],
                    "language": [4],
                    "models": [5],
                    "clinical": [6],
                    "reasoning": [7],
                },
                "authorships": [{"author": {"display_name": "Modern Author"}}],
                "primary_location": {"landing_page_url": "https://example.org/modern-qa"},
            },
            {
                "id": "https://openalex.org/W4410296683",
                "display_name": "Scaling Medical Reasoning Verification via Tool-Integrated Reinforcement Learning",
                "publication_year": 2026,
                "abstract_inverted_index": {
                    "medical": [0],
                    "reasoning": [1],
                    "verification": [2],
                    "reinforcement": [3],
                    "learning": [4],
                    "benchmark": [5],
                },
                "authorships": [{"author": {"display_name": "Modern Author B"}}],
                "primary_location": {"landing_page_url": "https://example.org/modern-verification"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert ranked_titles[0] == "Scaling Medical Reasoning Verification via Tool-Integrated Reinforcement Learning"
    assert ranked_titles[1] == "Toward expert-level medical question answering with large language models"
    assert ranked_titles[-1] == "Case-based reasoning algorithms applied in a medical acquisition tool"


def test_openalex_reranking_reduces_vqa_and_document_bias_for_clinical_medical_reasoning(
    workspace_tmp_path,
    monkeypatch,
):
    request = TopicAgentExploreRequest(
        interest="clinical medical reasoning",
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
                "id": "https://openalex.org/W1",
                "display_name": "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning",
                "publication_year": 2024,
                "abstract_inverted_index": {
                    "document": [0],
                    "question": [1],
                    "answering": [2],
                    "medical": [3],
                    "report": [4],
                    "clinical": [5],
                    "reasoning": [6],
                },
                "authorships": [{"author": {"display_name": "Author A"}}],
                "primary_location": {"landing_page_url": "https://example.org/rjua"},
            },
            {
                "id": "https://openalex.org/W2",
                "display_name": "Medical Visual Question Answering via Conditional Reasoning",
                "publication_year": 2020,
                "abstract_inverted_index": {
                    "medical": [0],
                    "visual": [1],
                    "question": [2],
                    "answering": [3],
                    "conditional": [4],
                    "reasoning": [5],
                    "vqa-rad": [6],
                },
                "authorships": [{"author": {"display_name": "Author B"}}],
                "primary_location": {"landing_page_url": "https://example.org/medvqa"},
            },
                {
                    "id": "https://openalex.org/W3",
                    "display_name": "Large Language Models lack essential metacognition for reliable medical reasoning",
                    "publication_year": 2025,
                    "abstract_inverted_index": {
                        "benchmark": [0],
                        "medical": [1],
                        "reasoning": [2],
                        "metacognition": [3],
                        "confidence": [4],
                        "reliable": [5],
                        "clinical": [6],
                        "evaluation": [7],
                    },
                "authorships": [{"author": {"display_name": "Author C"}}],
                "primary_location": {"landing_page_url": "https://example.org/metamedqa"},
            },
            {
                "id": "https://openalex.org/W4",
                "display_name": "Chatbot vs Medical Student Performance on Free-Response Clinical Reasoning Examinations",
                "publication_year": 2023,
                "abstract_inverted_index": {
                    "free-response": [0],
                    "clinical": [1],
                    "reasoning": [2],
                    "medical": [3],
                    "student": [4],
                    "evaluation": [5],
                },
                "authorships": [{"author": {"display_name": "Author D"}}],
                "primary_location": {"landing_page_url": "https://example.org/freeresponse"},
            },
        ]
    }

    monkeypatch.setattr(
        "app.services.topic_agent.providers.httpx.get",
        lambda *args, **kwargs: FakeResponse(payload),
    )

    result = provider.retrieve(request)
    ranked_titles = [record.title for record in result.records]

    assert set(ranked_titles[:2]) == {
        "Large Language Models lack essential metacognition for reliable medical reasoning",
        "Chatbot vs Medical Student Performance on Free-Response Clinical Reasoning Examinations",
    }
    assert "Medical Visual Question Answering via Conditional Reasoning" not in ranked_titles[:2]
    assert "RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning" not in ranked_titles[:2]


def test_rank_records_prefers_modern_software_agent_evidence_over_legacy_agent_neighbors():
    request = TopicAgentExploreRequest(
        interest="llm agents for software engineering",
        problem_domain="developer tools",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    records = [
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W1",
                        "display_name": "Prometheus: A Pragmatic Methodology for Engineering Intelligent Agents",
                        "publication_year": 2002,
                        "abstract_inverted_index": {
                            "methodology": [0],
                            "engineering": [1],
                            "intelligent": [2],
                            "agents": [3],
                        },
                        "authorships": [{"author": {"display_name": "Author A"}}],
                        "primary_location": {"landing_page_url": "https://example.org/prometheus"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W2",
                        "display_name": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "software": [0],
                            "engineering": [1],
                            "benchmark": [2],
                            "coding": [3],
                            "evaluation": [4],
                            "developer": [5],
                        },
                        "authorships": [{"author": {"display_name": "Author B"}}],
                        "primary_location": {"landing_page_url": "https://example.org/swebench"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W3",
                        "display_name": "An Empirical Study on Culture, Automation, Measurement, and Sharing of DevSecOps",
                        "publication_year": 2019,
                        "abstract_inverted_index": {
                            "developer": [0],
                            "tools": [1],
                            "automation": [2],
                            "devsecops": [3],
                            "software": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author C"}}],
                        "primary_location": {"landing_page_url": "https://example.org/devsecops"},
                    }
                ]
            }
        )[0],
    ]

    ranked_titles = [record.title for record in _rank_records(records, request, max_results=3)]

    assert ranked_titles[0] == "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    assert ranked_titles[-1] == "Prometheus: A Pragmatic Methodology for Engineering Intelligent Agents"


def test_rank_records_penalizes_software_library_neighbors_for_modern_agent_queries():
    request = TopicAgentExploreRequest(
        interest="coding agents for software engineering",
        problem_domain="developer workflows",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    records = [
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W1",
                        "display_name": "Explainable AI In Software Engineering: Enhancing Developer-AI Collaboration",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "software": [0],
                            "engineering": [1],
                            "developer": [2],
                            "collaboration": [3],
                            "ai": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author A"}}],
                        "primary_location": {"landing_page_url": "https://example.org/explainable-se"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W2",
                        "display_name": "AutoCodeRover: Autonomous Program Improvement",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "autonomous": [0],
                            "program": [1],
                            "improvement": [2],
                            "developer": [3],
                            "workflow": [4],
                            "coding": [5],
                        },
                        "authorships": [{"author": {"display_name": "Author B"}}],
                        "primary_location": {"landing_page_url": "https://example.org/autocoderover"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W3",
                        "display_name": "Array programming with NumPy",
                        "publication_year": 2020,
                        "abstract_inverted_index": {
                            "array": [0],
                            "programming": [1],
                            "numpy": [2],
                            "python": [3],
                            "library": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author C"}}],
                        "primary_location": {"landing_page_url": "https://example.org/numpy"},
                    }
                ]
            }
        )[0],
    ]

    ranked_titles = [record.title for record in _rank_records(records, request, max_results=3)]
    filtered_titles = [record.title for record in _filter_ranked_records(_rank_records(records, request, max_results=3), request, max_results=3)]

    assert ranked_titles[-1] == "Array programming with NumPy"
    assert "Array programming with NumPy" not in filtered_titles


def test_rank_records_penalizes_generic_autonomous_maintenance_neighbors_for_code_repair_queries():
    request = TopicAgentExploreRequest(
        interest="autonomous code repair agents",
        problem_domain="software maintenance",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )
    records = [
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W1",
                        "display_name": "AutoCodeRover: Autonomous Program Improvement",
                        "publication_year": 2024,
                        "abstract_inverted_index": {
                            "autonomous": [0],
                            "program": [1],
                            "improvement": [2],
                            "program": [3],
                            "repair": [4],
                            "github": [5],
                            "issues": [6],
                        },
                        "authorships": [{"author": {"display_name": "Author A"}}],
                        "primary_location": {"landing_page_url": "https://example.org/autocoderover"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W2",
                        "display_name": "Semi-autonomous visual inspection of vessels assisted by an unmanned Micro Aerial Vehicle",
                        "publication_year": 2012,
                        "abstract_inverted_index": {
                            "vessel": [0],
                            "maintenance": [1],
                            "inspection": [2],
                            "autonomous": [3],
                            "agent": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author B"}}],
                        "primary_location": {"landing_page_url": "https://example.org/vessel"},
                    }
                ]
            }
        )[0],
        _parse_openalex_response(
            {
                "results": [
                    {
                        "id": "https://openalex.org/W3",
                        "display_name": "Automating human based negotiation processes for autonomic logistics",
                        "publication_year": 2002,
                        "abstract_inverted_index": {
                            "autonomous": [0],
                            "maintenance": [1],
                            "logistics": [2],
                            "negotiation": [3],
                            "agent": [4],
                        },
                        "authorships": [{"author": {"display_name": "Author C"}}],
                        "primary_location": {"landing_page_url": "https://example.org/logistics"},
                    }
                ]
            }
        )[0],
    ]

    ranked_titles = [record.title for record in _rank_records(records, request, max_results=3)]
    filtered_titles = [
        record.title
        for record in _filter_ranked_records(
            _rank_records(records, request, max_results=3),
            request,
            max_results=3,
        )
    ]

    assert ranked_titles[0] == "AutoCodeRover: Autonomous Program Improvement"
    assert ranked_titles[-1] == "Automating human based negotiation processes for autonomic logistics"
    assert "AutoCodeRover: Autonomous Program Improvement" in filtered_titles


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
