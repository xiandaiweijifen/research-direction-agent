from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
from typing import Protocol

import httpx

from app.core.config import DATA_ROOT
from app.schemas.topic_agent import (
    TopicAgentEvidenceDiagnostics,
    TopicAgentExploreRequest,
    TopicAgentSourceRecord,
)
from app.services.agent.state_store import atomic_write_json


@dataclass
class TopicAgentEvidenceRetrievalResult:
    records: list[TopicAgentSourceRecord]
    diagnostics: TopicAgentEvidenceDiagnostics


class TopicAgentEvidenceProvider(Protocol):
    def retrieve(self, request: TopicAgentExploreRequest) -> TopicAgentEvidenceRetrievalResult:
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


ARXIV_API_URL = "https://export.arxiv.org/api/query"
OPENALEX_API_URL = "https://api.openalex.org/works"
ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}
TOPIC_AGENT_ARXIV_CACHE_PATH = DATA_ROOT / "tool_state" / "topic_agent_arxiv_cache.json"
TOPIC_AGENT_OPENALEX_CACHE_PATH = DATA_ROOT / "tool_state" / "topic_agent_openalex_cache.json"


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _load_cache(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    try:
        import json

        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _save_cache(path: Path, payload: dict[str, dict]) -> None:
    atomic_write_json(path, payload)


class MockTopicAgentEvidenceProvider:
    provider_name = "mock"

    def retrieve(self, request: TopicAgentExploreRequest) -> TopicAgentEvidenceRetrievalResult:
        base_topic = request.interest.strip()
        domain = _normalize_optional(request.problem_domain) or "the target domain"
        records = [
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
        return TopicAgentEvidenceRetrievalResult(
            records=records,
            diagnostics=TopicAgentEvidenceDiagnostics(
                requested_provider=self.provider_name,
                used_provider=self.provider_name,
                fallback_used=False,
                fallback_reason=None,
                record_count=len(records),
                cache_hit=False,
            ),
        )


class OpenAlexEvidenceProvider:
    provider_name = "openalex"

    def __init__(
        self,
        *,
        api_url: str = OPENALEX_API_URL,
        timeout_seconds: float = 5.0,
        max_results: int = 5,
        cache_path: Path = TOPIC_AGENT_OPENALEX_CACHE_PATH,
        cache_ttl_seconds: int = 60 * 60 * 12,
    ) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results
        self.cache_path = cache_path
        self.cache_ttl_seconds = cache_ttl_seconds

    def retrieve(self, request: TopicAgentExploreRequest) -> TopicAgentEvidenceRetrievalResult:
        query_texts = _build_openalex_queries(request)
        cache_key = _build_cache_key("||".join(query_texts), self.max_results)
        cached_records = _load_cached_records(
            self.cache_path,
            cache_key,
            self.cache_ttl_seconds,
        )
        if cached_records:
            return TopicAgentEvidenceRetrievalResult(
                records=cached_records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider=self.provider_name,
                    used_provider=self.provider_name,
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=len(cached_records),
                    cache_hit=True,
                ),
            )
        merged_records: list[TopicAgentSourceRecord] = []
        for query_text in query_texts:
            response = httpx.get(
                self.api_url,
                params={
                    "search": query_text,
                    "filter": "has_abstract:true",
                    "per-page": self.max_results,
                },
                timeout=self.timeout_seconds,
                follow_redirects=True,
                headers={"User-Agent": "research-topic-copilot/0.1"},
            )
            response.raise_for_status()
            payload = response.json()
            merged_records.extend(
                [_normalize_record(record) for record in _parse_openalex_response(payload)]
            )
        records = _rank_records(
            _dedupe_records(merged_records),
            request,
            self.max_results,
        )
        records = _filter_ranked_records(records, request, self.max_results)
        _save_cached_records(self.cache_path, cache_key, records)
        return TopicAgentEvidenceRetrievalResult(
            records=records,
            diagnostics=TopicAgentEvidenceDiagnostics(
                requested_provider=self.provider_name,
                used_provider=self.provider_name,
                fallback_used=False,
                fallback_reason=None,
                record_count=len(records),
                cache_hit=False,
            ),
        )


class ArxivEvidenceProvider:
    provider_name = "arxiv"

    def __init__(
        self,
        *,
        api_url: str = ARXIV_API_URL,
        timeout_seconds: float = 5.0,
        max_results: int = 3,
        cache_path: Path = TOPIC_AGENT_ARXIV_CACHE_PATH,
        cache_ttl_seconds: int = 60 * 60 * 12,
    ) -> None:
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results
        self.cache_path = cache_path
        self.cache_ttl_seconds = cache_ttl_seconds

    def retrieve(self, request: TopicAgentExploreRequest) -> TopicAgentEvidenceRetrievalResult:
        query_text = _build_arxiv_query(request)
        cache_key = _build_cache_key(query_text, self.max_results)
        cached_records = _load_cached_records(
            self.cache_path,
            cache_key,
            self.cache_ttl_seconds,
        )
        if cached_records:
            return TopicAgentEvidenceRetrievalResult(
                records=cached_records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider=self.provider_name,
                    used_provider=self.provider_name,
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=len(cached_records),
                    cache_hit=True,
                ),
            )
        response = httpx.get(
            self.api_url,
            params={
                "search_query": f"all:{query_text}",
                "start": 0,
                "max_results": self.max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            },
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "research-topic-copilot/0.1"},
        )
        response.raise_for_status()
        records = _rank_records(
            [_normalize_record(record) for record in _parse_arxiv_response(response.text)],
            request,
            self.max_results,
        )
        records = _filter_ranked_records(records, request, self.max_results)
        _save_cached_records(self.cache_path, cache_key, records)
        return TopicAgentEvidenceRetrievalResult(
            records=records,
            diagnostics=TopicAgentEvidenceDiagnostics(
                requested_provider=self.provider_name,
                used_provider=self.provider_name,
                fallback_used=False,
                fallback_reason=None,
                record_count=len(records),
                cache_hit=False,
            ),
        )


class FallbackEvidenceProvider:
    def __init__(
        self,
        primary: TopicAgentEvidenceProvider,
        fallback: TopicAgentEvidenceProvider,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    provider_name = "fallback"

    def retrieve(self, request: TopicAgentExploreRequest) -> TopicAgentEvidenceRetrievalResult:
        primary_name = getattr(self.primary, "provider_name", "primary")
        fallback_name = getattr(self.fallback, "provider_name", "fallback")
        try:
            primary_result = self.primary.retrieve(request)
            if primary_result.records:
                primary_result.diagnostics.requested_provider = primary_name
                primary_result.diagnostics.record_count = len(primary_result.records)
                return primary_result
            fallback_result = self.fallback.retrieve(request)
            fallback_used_provider = fallback_result.diagnostics.used_provider
            fallback_result.diagnostics.requested_provider = primary_name
            fallback_result.diagnostics.fallback_used = True
            fallback_result.diagnostics.fallback_reason = "primary_provider_returned_no_records"
            fallback_result.diagnostics.record_count = len(fallback_result.records)
            fallback_result.diagnostics.used_provider = fallback_used_provider
            return fallback_result
        except Exception as exc:
            fallback_result = self.fallback.retrieve(request)
            fallback_used_provider = fallback_result.diagnostics.used_provider
            fallback_result.diagnostics.requested_provider = primary_name
            fallback_result.diagnostics.fallback_used = True
            fallback_result.diagnostics.fallback_reason = f"{type(exc).__name__}:{exc}"
            fallback_result.diagnostics.record_count = len(fallback_result.records)
            fallback_result.diagnostics.used_provider = fallback_used_provider or fallback_name
            return fallback_result


def _build_arxiv_query(request: TopicAgentExploreRequest) -> str:
    interest = request.interest.strip()
    query_terms = list(_build_query_terms(request))
    core_terms = _core_query_terms(request)
    ordered_terms: list[str] = []
    for term in core_terms + query_terms:
        if term not in ordered_terms:
            ordered_terms.append(term)
    if not ordered_terms:
        return interest
    focused_terms = ordered_terms[:6]
    return " ".join([f"\"{interest}\"", *focused_terms])


def _build_openalex_query(request: TopicAgentExploreRequest) -> str:
    query_terms = _build_query_terms(request)
    core_terms = _core_query_terms(request)
    ordered_terms: list[str] = []
    for term in core_terms:
        if term not in ordered_terms:
            ordered_terms.append(term)
    for term in sorted(query_terms):
        if term not in ordered_terms:
            ordered_terms.append(term)
    return " ".join(ordered_terms[:8]) or request.interest.strip()


def _build_openalex_queries(request: TopicAgentExploreRequest) -> list[str]:
    base_query = _build_openalex_query(request)
    core_terms = _core_query_terms(request)
    domain_terms = [
        term
        for term in re.findall(r"[a-z0-9]+", (request.problem_domain or "").lower())
        if len(term) >= 4
    ]
    queries: list[str] = [base_query]
    if len(core_terms) >= 3:
        queries.append(" ".join(core_terms[:3] + domain_terms[:2]))
    if "multimodal" in core_terms and "reasoning" in core_terms:
        queries.append(" ".join(["multimodal", "reasoning", *domain_terms[:2], "benchmark"]))
    if "trustworthy" in core_terms:
        queries.append(" ".join(["trustworthy", "reasoning", *domain_terms[:2], "evaluation"]))
    deduped_queries: list[str] = []
    for query in queries:
        normalized = query.strip()
        if normalized and normalized not in deduped_queries:
            deduped_queries.append(normalized)
    return deduped_queries


def _build_cache_key(query_text: str, max_results: int) -> str:
    return f"{query_text.strip().lower()}::max={max_results}"


def _dedupe_records(records: list[TopicAgentSourceRecord]) -> list[TopicAgentSourceRecord]:
    deduped: list[TopicAgentSourceRecord] = []
    seen_keys: set[str] = set()
    for record in records:
        key = (record.identifier or record.url or record.title).strip().lower()
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(record)
    return deduped


def _build_query_terms(request: TopicAgentExploreRequest) -> set[str]:
    combined = " ".join(
        filter(
            None,
            [
                request.interest,
                request.problem_domain or "",
                request.constraints.preferred_style or "",
            ],
        )
    ).lower()
    return {
        term
        for term in re.findall(r"[a-z0-9]+", combined)
        if len(term) >= 4 and term not in {"and", "the", "for", "with", "using", "from", "into", "that"}
    }


def _core_query_terms(request: TopicAgentExploreRequest) -> list[str]:
    interest_terms = [
        term
        for term in re.findall(r"[a-z0-9]+", request.interest.lower())
        if len(term) >= 5 and term not in {"about", "using", "study", "based", "approach"}
    ]
    domain_terms = [
        term
        for term in re.findall(r"[a-z0-9]+", (request.problem_domain or "").lower())
        if len(term) >= 4 and term not in {"domain", "field", "study"}
    ]
    ordered_terms: list[str] = []
    for term in interest_terms + domain_terms:
        if term not in ordered_terms:
            ordered_terms.append(term)
    return ordered_terms[:6]


def _interest_signal_terms(request: TopicAgentExploreRequest) -> list[str]:
    generic_domain_terms = {"medical", "imaging", "clinical", "healthcare"}
    return [
        term
        for term in _core_query_terms(request)
        if term not in generic_domain_terms
    ]


def _score_record(
    record: TopicAgentSourceRecord,
    query_terms: set[str],
    core_terms: list[str],
) -> int:
    title_lower = record.title.lower()
    haystack = f"{title_lower} {record.summary.lower()}"
    score = 0
    for term in query_terms:
        if term in title_lower:
            score += 3
        elif term in haystack:
            score += 1
    for term in core_terms:
        if term in title_lower:
            score += 8
        elif term in haystack:
            score += 4
    if "multimodal" in haystack:
        score += 3
    if "medical" in haystack:
        score += 1
    if "reason" in haystack or "reasoning" in haystack:
        score += 4
    matched_core_terms = sum(1 for term in core_terms if term in haystack)
    score += matched_core_terms * 3
    return score


def _matched_core_term_count(record: TopicAgentSourceRecord, core_terms: list[str]) -> int:
    haystack = f"{record.title.lower()} {record.summary.lower()}"
    return sum(1 for term in core_terms if term in haystack)


def _matched_interest_term_count(record: TopicAgentSourceRecord, request: TopicAgentExploreRequest) -> int:
    interest_terms = _interest_signal_terms(request)
    haystack = f"{record.title.lower()} {record.summary.lower()}"
    return sum(1 for term in interest_terms if term in haystack)


def _normalize_record(record: TopicAgentSourceRecord) -> TopicAgentSourceRecord:
    return record.model_copy(
        update={
            "url": record.url.replace("http://arxiv.org", "https://arxiv.org"),
            "identifier": record.identifier.replace("http://arxiv.org", "https://arxiv.org"),
            "title": _clean_xml_text(record.title),
            "summary": _clean_xml_text(record.summary),
        }
    )


def _rank_records(
    records: list[TopicAgentSourceRecord],
    request: TopicAgentExploreRequest,
    max_results: int,
) -> list[TopicAgentSourceRecord]:
    query_terms = _build_query_terms(request)
    core_terms = _core_query_terms(request)
    scored_records = sorted(
        records,
        key=lambda record: (
            _score_record(record, query_terms, core_terms),
            record.year,
        ),
        reverse=True,
    )
    return scored_records[:max_results]


def _filter_ranked_records(
    records: list[TopicAgentSourceRecord],
    request: TopicAgentExploreRequest,
    max_results: int,
) -> list[TopicAgentSourceRecord]:
    core_terms = _core_query_terms(request)
    if not core_terms:
        return records[:max_results]
    filtered = [
        record
        for record in records
        if _matched_core_term_count(record, core_terms) >= 2
        and _matched_interest_term_count(record, request) >= 2
    ]
    if not filtered:
        filtered = [
            record
            for record in records
            if _matched_core_term_count(record, core_terms) >= 1
            and _matched_interest_term_count(record, request) >= 2
        ]
    if not filtered:
        return records[:max_results]
    return filtered[:max_results]


def _load_cached_records(
    cache_path: Path,
    cache_key: str,
    cache_ttl_seconds: int,
) -> list[TopicAgentSourceRecord]:
    cache = _load_cache(cache_path)
    entry = cache.get(cache_key)
    if not isinstance(entry, dict):
        return []
    saved_at = entry.get("saved_at")
    serialized_records = entry.get("records")
    if not isinstance(saved_at, str) or not isinstance(serialized_records, list):
        return []
    try:
        saved_time = datetime.fromisoformat(saved_at)
    except ValueError:
        return []
    age_seconds = (datetime.now(saved_time.tzinfo) - saved_time).total_seconds()
    if age_seconds > cache_ttl_seconds:
        return []
    return [
        TopicAgentSourceRecord.model_validate(record)
        for record in serialized_records
        if isinstance(record, dict)
    ]


def _save_cached_records(
    cache_path: Path,
    cache_key: str,
    records: list[TopicAgentSourceRecord],
) -> None:
    cache = _load_cache(cache_path)
    cache[cache_key] = {
        "saved_at": datetime.now().astimezone().isoformat(),
        "records": [record.model_dump() for record in records],
    }
    atomic_write_json(cache_path, cache)


def _reconstruct_openalex_abstract(abstract_index: dict | None) -> str:
    if not isinstance(abstract_index, dict):
        return ""
    positions: dict[int, str] = {}
    for token, token_positions in abstract_index.items():
        if not isinstance(token, str) or not isinstance(token_positions, list):
            continue
        for position in token_positions:
            if isinstance(position, int):
                positions[position] = token
    return " ".join(token for _, token in sorted(positions.items()))


def _parse_openalex_response(payload: dict) -> list[TopicAgentSourceRecord]:
    if not isinstance(payload, dict):
        return []
    results = payload.get("results")
    if not isinstance(results, list):
        return []

    records: list[TopicAgentSourceRecord] = []
    for index, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        title = _clean_xml_text(str(item.get("display_name") or f"OpenAlex Result {index}"))
        summary = _clean_xml_text(_reconstruct_openalex_abstract(item.get("abstract_inverted_index")))
        primary_location = item.get("primary_location") or {}
        if not isinstance(primary_location, dict):
            primary_location = {}
        source_id = str(item.get("id") or f"https://openalex.org/W{index}")
        url = str(
            primary_location.get("landing_page_url")
            or item.get("doi")
            or source_id
        )
        authorships = item.get("authorships")
        authors: list[str] = []
        if isinstance(authorships, list):
            for authorship in authorships[:4]:
                if not isinstance(authorship, dict):
                    continue
                author = authorship.get("author") or {}
                if isinstance(author, dict):
                    display_name = author.get("display_name")
                    if isinstance(display_name, str) and display_name.strip():
                        authors.append(display_name.strip())
        year = item.get("publication_year")
        try:
            normalized_year = int(year)
        except (TypeError, ValueError):
            normalized_year = datetime.now().year
        lower_title = title.lower()
        lower_summary = summary.lower()
        source_type = "paper"
        source_tier = "B"
        if "survey" in lower_title or "survey" in lower_summary:
            source_type = "survey"
            source_tier = "A"
        elif "benchmark" in lower_title or "benchmark" in lower_summary:
            source_type = "benchmark"
            source_tier = "A"
        records.append(
            TopicAgentSourceRecord(
                source_id=f"openalex_{index}",
                title=title,
                source_type=source_type,
                source_tier=source_tier,
                year=normalized_year,
                authors_or_publisher=", ".join(authors) or "OpenAlex Authors",
                identifier=source_id,
                url=url,
                summary=summary or "No abstract available from OpenAlex.",
                relevance_reason="Retrieved from OpenAlex as a public scholarly metadata source for the current topic query.",
            )
        )
    return records


def _parse_arxiv_response(xml_text: str) -> list[TopicAgentSourceRecord]:
    root = ElementTree.fromstring(xml_text)
    records: list[TopicAgentSourceRecord] = []
    for index, entry in enumerate(root.findall("atom:entry", ATOM_NAMESPACE), start=1):
        title = _clean_xml_text(entry.findtext("atom:title", default="", namespaces=ATOM_NAMESPACE))
        summary = _clean_xml_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NAMESPACE))
        published = entry.findtext("atom:published", default="", namespaces=ATOM_NAMESPACE)
        authors = [
            _clean_xml_text(author.findtext("atom:name", default="", namespaces=ATOM_NAMESPACE))
            for author in entry.findall("atom:author", ATOM_NAMESPACE)
        ]
        primary_id = _clean_xml_text(entry.findtext("atom:id", default="", namespaces=ATOM_NAMESPACE))
        year = _parse_arxiv_year(published)
        source_type = "paper"
        source_tier = "B"
        lower_title = title.lower()
        lower_summary = summary.lower()
        if "survey" in lower_title or "survey" in lower_summary:
            source_type = "survey"
            source_tier = "A"
        elif "benchmark" in lower_title or "benchmark" in lower_summary:
            source_type = "benchmark"
            source_tier = "A"
        records.append(
            TopicAgentSourceRecord(
                source_id=f"arxiv_{index}",
                title=title or f"arXiv Result {index}",
                source_type=source_type,
                source_tier=source_tier,
                year=year,
                authors_or_publisher=", ".join(filter(None, authors[:4])) or "arXiv Authors",
                identifier=primary_id or f"arxiv:{index}",
                url=primary_id or "https://arxiv.org",
                summary=summary or "No abstract available from arXiv.",
                relevance_reason="Retrieved from arXiv as a public academic source for the current topic query.",
            )
        )
    return records


def _clean_xml_text(value: str) -> str:
    return " ".join(value.split()).strip()


def _parse_arxiv_year(value: str) -> int:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).year
    except ValueError:
        return datetime.now().year


def build_topic_agent_provider_registry() -> TopicAgentEvidenceProviderRegistry:
    registry = TopicAgentEvidenceProviderRegistry()
    registry.register("mock", MockTopicAgentEvidenceProvider())
    registry.register("openalex", OpenAlexEvidenceProvider())
    registry.register("arxiv", ArxivEvidenceProvider())
    registry.register(
        "arxiv_or_mock",
        FallbackEvidenceProvider(
            primary=ArxivEvidenceProvider(),
            fallback=MockTopicAgentEvidenceProvider(),
        ),
    )
    registry.register(
        "openalex_or_arxiv_or_mock",
        FallbackEvidenceProvider(
            primary=OpenAlexEvidenceProvider(),
            fallback=FallbackEvidenceProvider(
                primary=ArxivEvidenceProvider(),
                fallback=MockTopicAgentEvidenceProvider(),
            ),
        ),
    )
    return registry
