import uuid
from pathlib import Path

from app.core.config import DATA_ROOT
from app.schemas.topic_agent import (
    TopicAgentCandidateTopic,
    TopicAgentComparisonResult,
    TopicAgentConfidenceSummary,
    TopicAgentConvergenceResult,
    TopicAgentExploreRequest,
    TopicAgentFramingResult,
    TopicAgentLandscapeSummary,
    TopicAgentRefineRequest,
    TopicAgentSessionListResponse,
    TopicAgentSessionResponse,
    TopicAgentSessionSummary,
    TopicAgentSourceRecord,
    TopicAgentTraceEvent,
)
from app.services.agent.state_store import JsonListRepository
from app.services.ingestion.document_service import build_utc_timestamp

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


def _build_extracted_constraints(request: TopicAgentExploreRequest) -> dict[str, str]:
    constraints: dict[str, str] = {}
    if request.constraints.time_budget_months is not None:
        constraints["time_budget_months"] = str(request.constraints.time_budget_months)
    if request.constraints.resource_level:
        constraints["resource_level"] = request.constraints.resource_level
    if request.constraints.preferred_style:
        constraints["preferred_style"] = request.constraints.preferred_style
    if request.constraints.notes:
        constraints["notes"] = request.constraints.notes
    return constraints


def _build_missing_clarifications(request: TopicAgentExploreRequest) -> list[str]:
    missing: list[str] = []
    if request.constraints.time_budget_months is None:
        missing.append("time_budget")
    if not request.constraints.resource_level:
        missing.append("resource_level")
    if not request.constraints.preferred_style:
        missing.append("preferred_style")
    return missing


def _build_search_questions(request: TopicAgentExploreRequest) -> list[str]:
    topic = request.interest.strip()
    return [
        f"What are the main research themes in {topic}?",
        f"What methods and benchmarks are commonly used in {topic}?",
        f"What open problems or underexplored gaps exist in {topic}?",
    ]


def _build_mock_evidence_records(request: TopicAgentExploreRequest) -> list[TopicAgentSourceRecord]:
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


def _build_mock_landscape_summary(request: TopicAgentExploreRequest) -> TopicAgentLandscapeSummary:
    topic = request.interest.strip()
    return TopicAgentLandscapeSummary(
        themes=[
            f"problem framing and task definition in {topic}",
            f"benchmark-driven evaluation for {topic}",
            f"practical deployment concerns in {topic}",
        ],
        active_methods=[
            "survey-guided baseline comparison",
            "benchmark-centered experimental design",
            "cross-method error analysis",
        ],
        likely_gaps=[
            "clear task scoping for narrow research questions",
            "stronger evidence on feasibility under limited resources",
        ],
        saturated_areas=[
            "broad generic summaries without a sharply defined question",
        ],
    )


def _build_mock_candidate_topics() -> list[TopicAgentCandidateTopic]:
    return [
        TopicAgentCandidateTopic(
            candidate_id="candidate_1",
            title="Benchmark-Guided Narrow Task Definition",
            research_question="How can a narrower benchmark task reveal actionable limitations in current methods?",
            positioning="gap-driven",
            novelty_note="Focuses on under-specified evaluation boundaries rather than generic performance claims.",
            feasibility_note="Moderate feasibility with public resources and modest compute.",
            risk_note="May become incremental if the task boundary is not sharply differentiated.",
            supporting_source_ids=["source_1", "source_2"],
            open_questions=["Which benchmark subset best represents the intended problem?"],
        ),
        TopicAgentCandidateTopic(
            candidate_id="candidate_2",
            title="Method Transfer Under Practical Constraints",
            research_question="Can an existing method family be adapted effectively under stricter resource constraints?",
            positioning="transfer",
            novelty_note="Combines known methods with a narrower operating constraint.",
            feasibility_note="Higher feasibility because it can start from existing baselines.",
            risk_note="Novelty may depend heavily on the chosen constraint and evaluation design.",
            supporting_source_ids=["source_1", "source_3"],
            open_questions=["Which constraint creates the strongest research signal?"],
        ),
        TopicAgentCandidateTopic(
            candidate_id="candidate_3",
            title="Tooling And Evaluation Workflow Support",
            research_question="What tooling or evaluation workflow improvements would make research in this area more reproducible?",
            positioning="systems",
            novelty_note="Shifts from model novelty to workflow and evaluation reliability.",
            feasibility_note="Strong feasibility for a short-cycle project with engineering emphasis.",
            risk_note="May fit a systems or tooling venue better than a method-centric venue.",
            supporting_source_ids=["source_2", "source_3"],
            open_questions=["What concrete reproducibility pain point should be prioritized first?"],
        ),
    ]


def _build_mock_comparison_result() -> TopicAgentComparisonResult:
    return TopicAgentComparisonResult(
        dimensions=[
            "novelty",
            "feasibility",
            "evidence_strength",
            "data_availability",
            "implementation_cost",
            "risk",
        ],
        summary=(
            "Candidate 1 is strongest on research focus, candidate 2 is strongest on practical feasibility, "
            "and candidate 3 is strongest on execution speed for an engineering-oriented project."
        ),
    )


def _build_mock_convergence_result() -> TopicAgentConvergenceResult:
    return TopicAgentConvergenceResult(
        recommended_candidate_id="candidate_1",
        backup_candidate_id="candidate_2",
        rationale=(
            "Candidate 1 currently offers the best balance between research value, evidence support, "
            "and scope control for a first serious topic exploration."
        ),
        manual_checks=[
            "Confirm that the selected sub-problem is narrow enough for the available timeline.",
            "Verify that at least one benchmark or dataset is realistically accessible.",
            "Check whether the proposed gap is genuinely underexplored rather than a retrieval miss.",
        ],
    )


def _build_trace() -> list[TopicAgentTraceEvent]:
    now = build_utc_timestamp()
    return [
        TopicAgentTraceEvent(
            stage="frame_problem",
            status="completed",
            timestamp=now,
            detail="Structured the user input into a topic-exploration request.",
        ),
        TopicAgentTraceEvent(
            stage="retrieve_evidence",
            status="completed",
            timestamp=now,
            detail="Built a mock evidence bundle for the first development slice.",
        ),
        TopicAgentTraceEvent(
            stage="generate_candidates",
            status="completed",
            timestamp=now,
            detail="Generated three candidate topic directions from the current evidence bundle.",
        ),
        TopicAgentTraceEvent(
            stage="converge_recommendation",
            status="completed",
            timestamp=now,
            detail="Produced a recommended next-best option with manual verification checks.",
        ),
    ]


def _build_session_payload(
    request: TopicAgentExploreRequest,
    *,
    session_id: str | None = None,
    created_at: str | None = None,
) -> TopicAgentSessionResponse:
    timestamp = build_utc_timestamp()
    framing_result = TopicAgentFramingResult(
        normalized_topic=request.interest.strip(),
        extracted_constraints=_build_extracted_constraints(request),
        missing_clarifications=_build_missing_clarifications(request),
        search_questions=_build_search_questions(request),
    )
    return TopicAgentSessionResponse(
        session_id=session_id or uuid.uuid4().hex,
        created_at=created_at or timestamp,
        updated_at=timestamp,
        user_input=request,
        framing_result=framing_result,
        evidence_records=_build_mock_evidence_records(request),
        landscape_summary=_build_mock_landscape_summary(request),
        candidate_topics=_build_mock_candidate_topics(),
        comparison_result=_build_mock_comparison_result(),
        convergence_result=_build_mock_convergence_result(),
        human_confirmations=[],
        trace=_build_trace(),
        confidence_summary=TopicAgentConfidenceSummary(
            evidence_coverage="medium",
            source_quality="medium_high",
            candidate_separation="high",
            conflict_level="low",
        ),
    )


def create_topic_agent_session(request: TopicAgentExploreRequest) -> TopicAgentSessionResponse:
    normalized_interest = request.interest.strip()
    if not normalized_interest:
        raise ValueError("interest_must_not_be_empty")

    normalized_request = TopicAgentExploreRequest(
        interest=normalized_interest,
        problem_domain=_normalize_optional(request.problem_domain),
        seed_idea=_normalize_optional(request.seed_idea),
        constraints=request.constraints,
    )
    response = _build_session_payload(normalized_request)
    sessions = _load_sessions()
    sessions.append(response.model_dump())
    _save_sessions(sessions)
    return response


def list_topic_agent_sessions(limit: int = 20) -> TopicAgentSessionListResponse:
    if limit <= 0:
        raise ValueError("limit_must_be_positive")

    sessions = [
        TopicAgentSessionResponse.model_validate(item)
        for item in reversed(_load_sessions())
    ][:limit]
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
        constraints=request.constraints if request.constraints.model_dump(exclude_none=True) else existing.user_input.constraints,
    )
    updated = _build_session_payload(
        merged_request,
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
