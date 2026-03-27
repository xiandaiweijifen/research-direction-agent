from pathlib import Path

from app.core.config import DATA_ROOT
from app.schemas.topic_agent import (
    TopicAgentEvidenceDiagnostics,
    TopicAgentEvidencePresentation,
    TopicAgentExploreRequest,
    TopicAgentRefineRequest,
    TopicAgentSessionListResponse,
    TopicAgentSessionResponse,
    TopicAgentSessionSummary,
)
from app.services.agent.state_store import JsonListRepository
from app.services.topic_agent.pipeline import run_topic_agent_pipeline
from app.services.topic_agent.providers import (
    TopicAgentEvidenceProvider,
    build_topic_agent_provider_registry,
)

TOPIC_AGENT_STORE_PATH = DATA_ROOT / "tool_state" / "topic_agent_sessions.json"
DEFAULT_TOPIC_AGENT_PROVIDER_NAME = "openalex_or_arxiv_or_mock"
TOPIC_AGENT_SESSION_HISTORY_LIMIT = 60


def _load_sessions() -> list[dict]:
    return JsonListRepository(Path(TOPIC_AGENT_STORE_PATH)).load()


def _save_sessions(records: list[dict]) -> None:
    JsonListRepository(Path(TOPIC_AGENT_STORE_PATH)).save(records)


def _trim_session_history(records: list[dict]) -> list[dict]:
    if TOPIC_AGENT_SESSION_HISTORY_LIMIT <= 0:
        return records
    return records[-TOPIC_AGENT_SESSION_HISTORY_LIMIT:]


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_request(request: TopicAgentExploreRequest) -> TopicAgentExploreRequest:
    normalized_interest = request.interest.strip()
    if not normalized_interest:
        raise ValueError("interest_must_not_be_empty")

    return TopicAgentExploreRequest(
        interest=normalized_interest,
        problem_domain=_normalize_optional(request.problem_domain),
        seed_idea=_normalize_optional(request.seed_idea),
        constraints=request.constraints,
        disable_cache=request.disable_cache,
    )


def _pipeline_provider(provider_name: str = DEFAULT_TOPIC_AGENT_PROVIDER_NAME) -> TopicAgentEvidenceProvider:
    registry = build_topic_agent_provider_registry()
    try:
        return registry.get(provider_name)
    except KeyError as exc:
        raise ValueError(f"unknown_topic_agent_provider:{provider_name}") from exc


def _backfill_session_payload(payload: dict) -> dict:
    normalized = dict(payload)
    evidence_records = normalized.get("evidence_records")
    if not isinstance(evidence_records, list):
        evidence_records = []
        normalized["evidence_records"] = evidence_records

    if "evidence_diagnostics" not in normalized or not isinstance(normalized.get("evidence_diagnostics"), dict):
        normalized["evidence_diagnostics"] = TopicAgentEvidenceDiagnostics(
            requested_provider="unknown",
            used_provider="unknown",
            fallback_used=False,
            fallback_reason=None,
            record_count=len(evidence_records),
            cache_hit=False,
        ).model_dump()

    if "human_confirmations" not in normalized or not isinstance(normalized.get("human_confirmations"), list):
        normalized["human_confirmations"] = []

    if "clarification_suggestions" not in normalized or not isinstance(
        normalized.get("clarification_suggestions"),
        list,
    ):
        normalized["clarification_suggestions"] = []

    if "evidence_presentation" not in normalized or not isinstance(
        normalized.get("evidence_presentation"),
        dict,
    ):
        normalized["evidence_presentation"] = TopicAgentEvidencePresentation().model_dump()

    return normalized


def _load_validated_sessions() -> list[TopicAgentSessionResponse]:
    return [
        TopicAgentSessionResponse.model_validate(_backfill_session_payload(item))
        for item in _load_sessions()
    ]


def create_topic_agent_session(request: TopicAgentExploreRequest) -> TopicAgentSessionResponse:
    normalized_request = _normalize_request(request)
    response = run_topic_agent_pipeline(
        normalized_request,
        provider=_pipeline_provider(),
    )
    sessions = _load_sessions()
    sessions.append(response.model_dump())
    _save_sessions(_trim_session_history(sessions))
    return response


def list_topic_agent_sessions(limit: int = 20) -> TopicAgentSessionListResponse:
    if limit <= 0:
        raise ValueError("limit_must_be_positive")

    sessions = list(reversed(_load_validated_sessions()))[:limit]
    return TopicAgentSessionListResponse(
        sessions=[
            TopicAgentSessionSummary(
                session_id=session.session_id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                interest=session.user_input.interest,
                problem_domain=session.user_input.problem_domain,
                candidate_count=len(session.candidate_topics),
                recommended_candidate_id=session.convergence_result.recommended_candidate_id,
            )
            for session in sessions
        ]
    )


def get_topic_agent_session(session_id: str) -> TopicAgentSessionResponse:
    normalized_session_id = session_id.strip()
    if not normalized_session_id:
        raise ValueError("session_id_must_not_be_empty")

    for session in reversed(_load_validated_sessions()):
        if session.session_id == normalized_session_id:
            return session
    raise FileNotFoundError(session_id)


def refine_topic_agent_session(
    session_id: str,
    request: TopicAgentRefineRequest,
) -> TopicAgentSessionResponse:
    existing = get_topic_agent_session(session_id)
    merged_request = TopicAgentExploreRequest(
        interest=_normalize_optional(request.interest) or existing.user_input.interest,
        problem_domain=(
            _normalize_optional(request.problem_domain)
            if request.problem_domain is not None
            else existing.user_input.problem_domain
        ),
        seed_idea=(
            _normalize_optional(request.seed_idea)
            if request.seed_idea is not None
            else existing.user_input.seed_idea
        ),
        constraints=(
            request.constraints
            if request.constraints.model_dump(exclude_none=True)
            else existing.user_input.constraints
        ),
        disable_cache=(
            request.disable_cache
            if request.disable_cache is not None
            else existing.user_input.disable_cache
        ),
    )
    normalized_request = _normalize_request(merged_request)
    updated = run_topic_agent_pipeline(
        normalized_request,
        provider=_pipeline_provider(),
        session_id=existing.session_id,
        created_at=existing.created_at,
    )

    sessions = _load_sessions()
    replaced_sessions: list[dict] = []
    for item in sessions:
        if item.get("session_id") == existing.session_id:
            replaced_sessions.append(updated.model_dump())
        else:
            replaced_sessions.append(item)
    _save_sessions(_trim_session_history(replaced_sessions))
    return updated
