from pathlib import Path

from app.core.config import DATA_ROOT
from app.schemas.topic_agent import (
    TopicAgentExploreRequest,
    TopicAgentRefineRequest,
    TopicAgentSessionListResponse,
    TopicAgentSessionResponse,
    TopicAgentSessionSummary,
)
from app.services.agent.state_store import JsonListRepository
from app.services.topic_agent.pipeline import run_topic_agent_pipeline
from app.services.topic_agent.providers import MockTopicAgentEvidenceProvider

TOPIC_AGENT_STORE_PATH = DATA_ROOT / "tool_state" / "topic_agent_sessions.json"


def _load_sessions() -> list[dict]:
    return JsonListRepository(Path(TOPIC_AGENT_STORE_PATH)).load()


def _save_sessions(records: list[dict]) -> None:
    JsonListRepository(Path(TOPIC_AGENT_STORE_PATH)).save(records)


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
    )


def _pipeline_provider() -> MockTopicAgentEvidenceProvider:
    return MockTopicAgentEvidenceProvider()


def create_topic_agent_session(request: TopicAgentExploreRequest) -> TopicAgentSessionResponse:
    normalized_request = _normalize_request(request)
    response = run_topic_agent_pipeline(
        normalized_request,
        provider=_pipeline_provider(),
    )
    sessions = _load_sessions()
    sessions.append(response.model_dump())
    _save_sessions(sessions)
    return response


def list_topic_agent_sessions(limit: int = 20) -> TopicAgentSessionListResponse:
    if limit <= 0:
        raise ValueError("limit_must_be_positive")

    sessions = [TopicAgentSessionResponse.model_validate(item) for item in reversed(_load_sessions())][
        :limit
    ]
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

    for item in reversed(_load_sessions()):
        if item.get("session_id") == normalized_session_id:
            return TopicAgentSessionResponse.model_validate(item)
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
    _save_sessions(replaced_sessions)
    return updated
