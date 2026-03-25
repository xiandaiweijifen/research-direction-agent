from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.schemas.topic_agent import (
    TopicAgentCandidateTopic,
    TopicAgentComparisonResult,
    TopicAgentConfidenceSummary,
    TopicAgentConvergenceResult,
    TopicAgentExploreRequest,
    TopicAgentFramingResult,
    TopicAgentLandscapeSummary,
    TopicAgentSessionResponse,
    TopicAgentSourceRecord,
    TopicAgentTraceEvent,
)
from app.services.ingestion.document_service import build_utc_timestamp
from app.services.topic_agent.providers import TopicAgentEvidenceProvider


@dataclass
class TopicAgentPipelineContext:
    request: TopicAgentExploreRequest
    framing_result: TopicAgentFramingResult | None = None
    evidence_records: list[TopicAgentSourceRecord] | None = None
    landscape_summary: TopicAgentLandscapeSummary | None = None
    candidate_topics: list[TopicAgentCandidateTopic] | None = None
    comparison_result: TopicAgentComparisonResult | None = None
    convergence_result: TopicAgentConvergenceResult | None = None
    confidence_summary: TopicAgentConfidenceSummary | None = None
    trace: list[TopicAgentTraceEvent] | None = None


def _time_budget_bucket(months: int | None) -> str:
    if months is None:
        return "unknown"
    if months <= 4:
        return "tight"
    if months <= 8:
        return "moderate"
    return "extended"


def _resource_bucket(resource_level: str | None) -> str:
    normalized = (resource_level or "").strip().lower()
    if normalized in {"student", "limited", "solo"}:
        return "limited"
    if normalized in {"lab", "team", "moderate"}:
        return "moderate"
    if normalized:
        return "strong"
    return "unknown"


def _preferred_style(request: TopicAgentExploreRequest) -> str:
    return (request.constraints.preferred_style or "").strip().lower()


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


def frame_problem(context: TopicAgentPipelineContext) -> TopicAgentFramingResult:
    request = context.request
    result = TopicAgentFramingResult(
        normalized_topic=request.interest.strip(),
        extracted_constraints=_build_extracted_constraints(request),
        missing_clarifications=_build_missing_clarifications(request),
        search_questions=_build_search_questions(request),
    )
    context.framing_result = result
    return result


def retrieve_evidence(
    context: TopicAgentPipelineContext,
    provider: TopicAgentEvidenceProvider,
) -> list[TopicAgentSourceRecord]:
    records = provider.retrieve(context.request)
    context.evidence_records = records
    return records


def synthesize_landscape(context: TopicAgentPipelineContext) -> TopicAgentLandscapeSummary:
    topic = context.request.interest.strip()
    result = TopicAgentLandscapeSummary(
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
    context.landscape_summary = result
    return result


def generate_candidates(context: TopicAgentPipelineContext) -> list[TopicAgentCandidateTopic]:
    budget_bucket = _time_budget_bucket(context.request.constraints.time_budget_months)
    resource_bucket = _resource_bucket(context.request.constraints.resource_level)
    style = _preferred_style(context.request)

    candidate_1 = TopicAgentCandidateTopic(
        candidate_id="candidate_1",
        title="Benchmark-Guided Narrow Task Definition",
        research_question="How can a narrower benchmark task reveal actionable limitations in current methods?",
        positioning="gap-driven",
        novelty_note="Focuses on under-specified evaluation boundaries rather than generic performance claims.",
        feasibility_note="Moderate feasibility with public resources and modest compute.",
        risk_note="May become incremental if the task boundary is not sharply differentiated.",
        supporting_source_ids=["source_1", "source_2"],
        open_questions=["Which benchmark subset best represents the intended problem?"],
    )
    candidate_2 = TopicAgentCandidateTopic(
        candidate_id="candidate_2",
        title="Method Transfer Under Practical Constraints",
        research_question="Can an existing method family be adapted effectively under stricter resource constraints?",
        positioning="transfer",
        novelty_note="Combines known methods with a narrower operating constraint.",
        feasibility_note="Higher feasibility because it can start from existing baselines.",
        risk_note="Novelty may depend heavily on the chosen constraint and evaluation design.",
        supporting_source_ids=["source_1", "source_3"],
        open_questions=["Which constraint creates the strongest research signal?"],
    )
    candidate_3 = TopicAgentCandidateTopic(
        candidate_id="candidate_3",
        title="Tooling And Evaluation Workflow Support",
        research_question="What tooling or evaluation workflow improvements would make research in this area more reproducible?",
        positioning="systems",
        novelty_note="Shifts from model novelty to workflow and evaluation reliability.",
        feasibility_note="Strong feasibility for a short-cycle project with engineering emphasis.",
        risk_note="May fit a systems or tooling venue better than a method-centric venue.",
        supporting_source_ids=["source_2", "source_3"],
        open_questions=["What concrete reproducibility pain point should be prioritized first?"],
    )

    if budget_bucket == "tight":
        candidate_1.feasibility_note = "Lower feasibility under a tight timeline unless the benchmark scope is aggressively constrained."
        candidate_2.feasibility_note = "High feasibility for a short project because it can reuse known baselines and smaller evaluation slices."
        candidate_3.feasibility_note = "High feasibility for a short-cycle project with engineering emphasis and bounded implementation scope."
        candidate_1.open_questions.append("Can the task be scoped to a 4-month or shorter execution window?")

    if resource_bucket == "limited":
        candidate_2.research_question = "Can an existing method family be adapted effectively under strict compute and annotation constraints?"
        candidate_2.novelty_note = "Frames novelty through constraint-aware adaptation rather than larger-model gains."
        candidate_3.open_questions.append("Which workflow improvement reduces compute or setup cost the most?")

    if style == "applied":
        candidate_2.title = "Applied Method Transfer Under Practical Constraints"
        candidate_2.positioning = "applied-transfer"
        candidate_2.feasibility_note = "Strong fit for an applied project that needs a visible baseline-to-improvement story."
        candidate_3.risk_note = "Applied impact may be clearer than publication novelty unless evaluation endpoints are sharply chosen."
    elif style == "systems":
        candidate_3.title = "Systems Workflow Support For Reproducible Evaluation"
        candidate_3.positioning = "systems-priority"
        candidate_3.novelty_note = "Emphasizes reproducibility infrastructure and evaluation reliability over new model design."
    elif style == "benchmark-driven":
        candidate_1.title = "Benchmark-Guided Narrow Task Definition"
        candidate_1.positioning = "benchmark-gap"
        candidate_1.novelty_note = "Targets benchmark slicing and evaluation boundary design as the main source of research value."

    result = [
        candidate_1,
        candidate_2,
        candidate_3,
    ]
    context.candidate_topics = result
    return result


def compare_candidates(context: TopicAgentPipelineContext) -> TopicAgentComparisonResult:
    budget_bucket = _time_budget_bucket(context.request.constraints.time_budget_months)
    style = _preferred_style(context.request)
    assessments_by_id = {
        "candidate_1": {
            "candidate_id": "candidate_1",
            "novelty": "high",
            "feasibility": "medium",
            "evidence_strength": "medium_high",
            "data_availability": "medium",
            "implementation_cost": "medium",
            "risk": "medium",
        },
        "candidate_2": {
            "candidate_id": "candidate_2",
            "novelty": "medium",
            "feasibility": "high",
            "evidence_strength": "medium",
            "data_availability": "medium_high",
            "implementation_cost": "medium_low",
            "risk": "medium",
        },
        "candidate_3": {
            "candidate_id": "candidate_3",
            "novelty": "medium",
            "feasibility": "high",
            "evidence_strength": "medium",
            "data_availability": "high",
            "implementation_cost": "low",
            "risk": "medium_high",
        },
    }

    if budget_bucket == "tight":
        assessments_by_id["candidate_1"]["feasibility"] = "low_medium"
        assessments_by_id["candidate_1"]["implementation_cost"] = "medium_high"
        assessments_by_id["candidate_2"]["feasibility"] = "high"
        assessments_by_id["candidate_3"]["feasibility"] = "high"

    if style == "applied":
        assessments_by_id["candidate_2"]["novelty"] = "medium_high"
        assessments_by_id["candidate_2"]["evidence_strength"] = "medium_high"
        assessments_by_id["candidate_2"]["risk"] = "medium_low"
        summary = (
            "Candidate 2 is strongest for applied feasibility under the current constraints, "
            "candidate 1 remains strongest on research framing, and candidate 3 remains the fastest engineering path."
        )
    elif style == "systems":
        assessments_by_id["candidate_3"]["novelty"] = "medium_high"
        assessments_by_id["candidate_3"]["evidence_strength"] = "medium_high"
        assessments_by_id["candidate_3"]["risk"] = "medium"
        summary = (
            "Candidate 3 is strongest for a systems-oriented project, candidate 1 still offers the clearest research framing, "
            "and candidate 2 remains the most direct transfer path."
        )
    else:
        summary = (
            "Candidate 1 is strongest on research focus, candidate 2 is strongest on practical feasibility, "
            "and candidate 3 is strongest on execution speed for an engineering-oriented project."
        )

    result = TopicAgentComparisonResult(
        dimensions=[
            "novelty",
            "feasibility",
            "evidence_strength",
            "data_availability",
            "implementation_cost",
            "risk",
        ],
        summary=summary,
        candidate_assessments=list(assessments_by_id.values()),
    )
    context.comparison_result = result
    return result


def converge_recommendation(context: TopicAgentPipelineContext) -> TopicAgentConvergenceResult:
    budget_bucket = _time_budget_bucket(context.request.constraints.time_budget_months)
    style = _preferred_style(context.request)

    recommended_candidate_id = "candidate_1"
    backup_candidate_id = "candidate_2"
    rationale = (
        "Candidate 1 currently offers the best balance between research value, evidence support, "
        "and scope control for a first serious topic exploration."
    )

    if style == "applied" or budget_bucket == "tight":
        recommended_candidate_id = "candidate_2"
        backup_candidate_id = "candidate_1"
        rationale = (
            "Candidate 2 is the best fit for the current constraints because it starts from reusable baselines, "
            "matches an applied project style, and is easier to execute within a tighter timeline."
        )
    elif style == "systems":
        recommended_candidate_id = "candidate_3"
        backup_candidate_id = "candidate_2"
        rationale = (
            "Candidate 3 is the best fit for a systems-oriented topic because it emphasizes workflow reliability, "
            "bounded engineering scope, and clearer reproducibility outcomes."
        )

    manual_checks = [
        "Confirm that the selected sub-problem is narrow enough for the available timeline.",
        "Verify that at least one benchmark or dataset is realistically accessible.",
        "Check whether the proposed gap is genuinely underexplored rather than a retrieval miss.",
    ]
    if budget_bucket == "tight":
        manual_checks[0] = "Confirm that the selected sub-problem can be completed within a 4-month or shorter timeline."
    if style == "applied":
        manual_checks.append("Verify that the topic still has enough novelty signal for the intended venue.")

    result = TopicAgentConvergenceResult(
        recommended_candidate_id=recommended_candidate_id,
        backup_candidate_id=backup_candidate_id,
        rationale=rationale,
        manual_checks=manual_checks,
    )
    context.convergence_result = result
    return result


def _derive_evidence_coverage(evidence_records: list[TopicAgentSourceRecord]) -> str:
    if len(evidence_records) >= 6:
        return "high"
    if len(evidence_records) >= 3:
        return "medium"
    return "low"


def _derive_source_quality(evidence_records: list[TopicAgentSourceRecord]) -> str:
    tier_a_count = sum(1 for record in evidence_records if record.source_tier == "A")
    if tier_a_count >= 3:
        return "high"
    if tier_a_count >= 1:
        return "medium_high"
    return "medium"


def _derive_candidate_separation(candidate_topics: list[TopicAgentCandidateTopic]) -> str:
    positionings = {candidate.positioning for candidate in candidate_topics}
    if len(positionings) >= 3:
        return "high"
    if len(positionings) == 2:
        return "medium"
    return "low"


def build_confidence_summary(context: TopicAgentPipelineContext) -> TopicAgentConfidenceSummary:
    evidence_records = context.evidence_records or []
    candidate_topics = context.candidate_topics or []
    evidence_coverage = _derive_evidence_coverage(evidence_records)
    source_quality = _derive_source_quality(evidence_records)
    candidate_separation = _derive_candidate_separation(candidate_topics)
    conflict_level = "low"
    result = TopicAgentConfidenceSummary(
        evidence_coverage=evidence_coverage,
        source_quality=source_quality,
        candidate_separation=candidate_separation,
        conflict_level=conflict_level,
        rationale=[
            f"Evidence coverage is {evidence_coverage} based on the current number of retrieved records.",
            f"Source quality is {source_quality} based on the current source-tier mix.",
            f"Candidate separation is {candidate_separation} based on the diversity of candidate positioning.",
            f"Conflict level is {conflict_level} because this development slice does not yet model explicit source disagreement.",
        ],
    )
    context.confidence_summary = result
    return result


def build_trace(context: TopicAgentPipelineContext) -> list[TopicAgentTraceEvent]:
    evidence_count = len(context.evidence_records or [])
    candidate_count = len(context.candidate_topics or [])
    result = [
        TopicAgentTraceEvent(
            stage="frame_problem",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail="Structured the user input into a topic-exploration request.",
        ),
        TopicAgentTraceEvent(
            stage="retrieve_evidence",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail=f"Built a mock evidence bundle with {evidence_count} records for the current development slice.",
        ),
        TopicAgentTraceEvent(
            stage="synthesize_landscape",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail="Organized the current evidence bundle into a lightweight research landscape summary.",
        ),
        TopicAgentTraceEvent(
            stage="generate_candidates",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail=f"Generated {candidate_count} candidate topic directions from the current evidence bundle.",
        ),
        TopicAgentTraceEvent(
            stage="compare_candidates",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail="Produced a structured candidate comparison across fixed MVP dimensions.",
        ),
        TopicAgentTraceEvent(
            stage="converge_recommendation",
            status="completed",
            timestamp=build_utc_timestamp(),
            detail="Produced a recommended next-best option with manual verification checks.",
        ),
    ]
    context.trace = result
    return result


def run_topic_agent_pipeline(
    request: TopicAgentExploreRequest,
    *,
    provider: TopicAgentEvidenceProvider,
    session_id: str | None = None,
    created_at: str | None = None,
) -> TopicAgentSessionResponse:
    timestamp = build_utc_timestamp()
    context = TopicAgentPipelineContext(request=request)
    frame_problem(context)
    retrieve_evidence(context, provider)
    synthesize_landscape(context)
    generate_candidates(context)
    compare_candidates(context)
    converge_recommendation(context)
    build_confidence_summary(context)
    build_trace(context)
    return TopicAgentSessionResponse(
        session_id=session_id or uuid.uuid4().hex,
        created_at=created_at or timestamp,
        updated_at=timestamp,
        user_input=request,
        framing_result=context.framing_result,
        evidence_records=context.evidence_records or [],
        landscape_summary=context.landscape_summary,
        candidate_topics=context.candidate_topics or [],
        comparison_result=context.comparison_result,
        convergence_result=context.convergence_result,
        human_confirmations=[],
        trace=context.trace or [],
        confidence_summary=context.confidence_summary,
    )
