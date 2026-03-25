from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from app.schemas.topic_agent import (
    TopicAgentCandidateTopic,
    TopicAgentComparisonResult,
    TopicAgentConfidenceSummary,
    TopicAgentConvergenceResult,
    TopicAgentEvidenceDiagnostics,
    TopicAgentExploreRequest,
    TopicAgentFramingResult,
    TopicAgentLandscapeSummary,
    TopicAgentSessionResponse,
    TopicAgentSourceRecord,
    TopicAgentTraceEvent,
)
from app.services.ingestion.document_service import build_utc_timestamp
from app.services.topic_agent.providers import (
    TopicAgentEvidenceProvider,
    TopicAgentEvidenceRetrievalResult,
)


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
    evidence_diagnostics: TopicAgentEvidenceDiagnostics | None = None
    trace: list[TopicAgentTraceEvent] | None = None


STOPWORDS = {
    "about",
    "across",
    "analysis",
    "approach",
    "based",
    "benchmark",
    "benchmarks",
    "context",
    "data",
    "evaluation",
    "effective",
    "framework",
    "image",
    "images",
    "imaging",
    "large",
    "learning",
    "medical",
    "method",
    "methods",
    "model",
    "models",
    "paper",
    "recent",
    "results",
    "study",
    "support",
    "system",
    "systems",
    "task",
    "tasks",
    "application",
    "applications",
    "deep",
    "from",
    "liver",
    "open",
    "practical",
    "repository",
    "survey",
    "using",
    "visual",
    "with",
}

EVIDENCE_CUE_TERMS = {
    "agent",
    "benchmark",
    "biomedical",
    "clinical",
    "document",
    "evaluation",
    "grounding",
    "interpretable",
    "multimodal",
    "qa",
    "question answering",
    "radiology",
    "reasoning",
    "safety",
    "trustworthy",
    "vqa",
    "zero shot",
}


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
    retrieval_result: TopicAgentEvidenceRetrievalResult = provider.retrieve(context.request)
    context.evidence_records = retrieval_result.records
    context.evidence_diagnostics = retrieval_result.diagnostics
    return retrieval_result.records


def _tokenize_text(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 4 and token not in STOPWORDS
    ]


def _extract_evidence_phrases(evidence_records: list[TopicAgentSourceRecord]) -> list[str]:
    phrase_scores: dict[str, int] = {}
    for record in evidence_records:
        title_tokens = _tokenize_text(record.title)
        summary_tokens = _tokenize_text(record.summary)
        weight = 2 if record.source_tier == "A" else 1
        for token in title_tokens:
            phrase_scores[token] = phrase_scores.get(token, 0) + (3 * weight)
        for token in summary_tokens[:40]:
            phrase_scores[token] = phrase_scores.get(token, 0) + weight
        title_bigrams = zip(title_tokens, title_tokens[1:])
        for left, right in title_bigrams:
            phrase = f"{left} {right}"
            phrase_scores[phrase] = phrase_scores.get(phrase, 0) + (4 * weight)
    ranked_phrases = sorted(
        phrase_scores.items(),
        key=lambda item: (item[1], len(item[0].split()), item[0]),
        reverse=True,
    )
    selected: list[str] = []
    for phrase, _score in ranked_phrases:
        if phrase in selected:
            continue
        if any(phrase in existing or existing in phrase for existing in selected):
            continue
        selected.append(phrase)
        if len(selected) == 6:
            break
    return selected


def _extract_query_anchor_terms(topic: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", topic.lower())
        if len(token) >= 5 and token not in STOPWORDS
    }


def _filter_evidence_phrases(
    evidence_phrases: list[str],
    *,
    topic: str,
) -> list[str]:
    anchors = _extract_query_anchor_terms(topic)
    filtered: list[str] = []
    for phrase in evidence_phrases:
        parts = phrase.split()
        if len(parts) == 1 and phrase not in anchors:
            if phrase not in EVIDENCE_CUE_TERMS:
                continue
        if any(part in STOPWORDS for part in parts):
            continue
        if anchors and not any(part in anchors or part in EVIDENCE_CUE_TERMS for part in parts):
            continue
        filtered.append(phrase)
    return filtered


def _top_evidence_text(evidence_records: list[TopicAgentSourceRecord], limit: int = 4) -> str:
    return " ".join(
        f"{record.title} {record.summary}"
        for record in evidence_records[:limit]
    ).lower()


def _query_context_text(request: TopicAgentExploreRequest) -> str:
    return " ".join(
        part
        for part in [
            request.interest,
            request.problem_domain or "",
            request.seed_idea or "",
        ]
        if part
    ).lower()


def _detect_evidence_cues(
    evidence_records: list[TopicAgentSourceRecord],
    request: TopicAgentExploreRequest | None = None,
) -> dict[str, bool]:
    text = _top_evidence_text(evidence_records)
    query_text = _query_context_text(request) if request is not None else ""
    combined_text = f"{text} {query_text}".strip()
    return {
        "benchmark": "benchmark" in combined_text or "vqa-rad" in combined_text or "slake" in combined_text,
        "trust": any(term in combined_text for term in {"trustworthy", "ethical", "safety", "hallucination", "reliability"}),
        "grounding": any(term in combined_text for term in {"grounding", "grounded", "image-grounded", "cross-modal"}),
        "radiology": any(term in combined_text for term in {"radiology", "x-ray", "radiation oncology"}),
        "document_qa": any(term in combined_text for term in {"document question answering", "document qa", "medical report", "meddqa", "question answering"}),
        "agentic": any(term in combined_text for term in {"agent collaborative", "learner agent", "ask-answer", "multi-agent", "agent"}),
        "zero_shot": "zero-shot" in combined_text or "zero shot" in combined_text,
        "clinical_reasoning": "clinical reasoning" in combined_text,
        "hallucination_eval": any(term in combined_text for term in {"hallucination", "grounding evaluation", "failure analysis", "faithfulness"}),
        "visual_qa": any(term in combined_text for term in {"visual question answering", "med-vqa", "medical vqa", "vqa-rad", "radiology question answering"}),
    }


def _build_landscape_themes(
    topic: str,
    evidence_records: list[TopicAgentSourceRecord],
    evidence_phrases: list[str],
    request: TopicAgentExploreRequest,
) -> list[str]:
    cues = _detect_evidence_cues(evidence_records, request)
    themes: list[str] = []
    if cues["benchmark"]:
        themes.append(f"benchmark design and stress-testing for {topic}")
    if cues["grounding"]:
        themes.append(f"cross-modal grounding and visual dependence in {topic}")
    if cues["hallucination_eval"]:
        themes.append(f"hallucination detection and failure analysis in {topic}")
    if cues["visual_qa"]:
        themes.append(f"radiology VQA and image-grounded answer reliability in {topic}")
    if cues["document_qa"] and not cues["hallucination_eval"]:
        themes.append(f"document QA and report-centric reasoning in {topic}")
    if cues["trust"]:
        themes.append(f"trustworthy evaluation and failure analysis in {topic}")
    if cues["radiology"]:
        themes.append(f"radiology-oriented multimodal reasoning tasks in {topic}")
    if cues["agentic"]:
        themes.append(f"agent-based decomposition strategies for {topic}")

    for phrase in evidence_phrases:
        theme = _theme_from_phrase(phrase, topic)
        if theme not in themes:
            themes.append(theme)
        if len(themes) == 3:
            break
    return themes[:3]


def _build_active_methods(
    evidence_records: list[TopicAgentSourceRecord],
    evidence_phrases: list[str],
    request: TopicAgentExploreRequest,
) -> list[str]:
    cues = _detect_evidence_cues(evidence_records, request)
    methods: list[str] = []
    if cues["benchmark"]:
        methods.append("benchmark-centered experimental design")
    if cues["grounding"]:
        methods.append("grounding-aware evaluation and error analysis")
    if cues["hallucination_eval"]:
        methods.append("hallucination auditing and faithfulness checks")
    if cues["agentic"]:
        methods.append("agent-mediated problem decomposition")
    if cues["document_qa"] and not cues["hallucination_eval"]:
        methods.append("document QA baseline comparison")
    if cues["radiology"]:
        methods.append("radiology task-specific benchmark slicing")
    for phrase in evidence_phrases:
        if phrase not in methods and len(phrase.split()) >= 2:
            methods.append(phrase)
        if len(methods) == 3:
            break
    return methods[:3]


def _build_likely_gaps(
    evidence_records: list[TopicAgentSourceRecord],
    default_topic: str,
    request: TopicAgentExploreRequest,
) -> list[str]:
    cues = _detect_evidence_cues(evidence_records, request)
    gaps: list[str] = []
    if cues["benchmark"]:
        gaps.append("benchmark protocols that distinguish real image use from shortcut exploitation")
    if cues["trust"] or cues["grounding"]:
        gaps.append("trustworthy evaluation signals beyond accuracy-only reporting")
    if cues["hallucination_eval"]:
        gaps.append("medical hallucination checks that separate unsupported answers from weak image grounding")
    if cues["radiology"]:
        gaps.append("narrower radiology task slices that remain feasible under student-scale resources")
    if cues["document_qa"] and not cues["hallucination_eval"]:
        gaps.append("stronger evidence on reasoning over report layouts and image-text context")
    if not gaps:
        gaps = [
            "clear task scoping for narrow research questions",
            "stronger evidence on feasibility under limited resources",
        ]
    while len(gaps) < 2:
        fallback = "clear task scoping for narrow research questions"
        if fallback not in gaps:
            gaps.append(fallback)
        else:
            gaps.append(f"stronger evidence on feasibility in {default_topic}")
    return gaps[:2]


def _theme_from_phrase(phrase: str, topic: str) -> str:
    if "reasoning" in phrase:
        return f"{phrase} challenges in {topic}"
    if "grounding" in phrase:
        return f"{phrase} and evidence faithfulness in {topic}"
    if "benchmark" in phrase:
        return f"{phrase} design and evaluation in {topic}"
    return f"{phrase} as an emerging theme in {topic}"


def synthesize_landscape(context: TopicAgentPipelineContext) -> TopicAgentLandscapeSummary:
    topic = context.request.interest.strip()
    evidence_records = context.evidence_records or []
    evidence_phrases = _filter_evidence_phrases(
        _extract_evidence_phrases(evidence_records),
        topic=topic,
    )
    derived_themes = _build_landscape_themes(topic, evidence_records, evidence_phrases, context.request)
    active_methods = _build_active_methods(evidence_records, evidence_phrases, context.request)
    if not active_methods:
        active_methods = [
            "survey-guided baseline comparison",
            "benchmark-centered experimental design",
            "cross-method error analysis",
        ]
    likely_gaps = _build_likely_gaps(evidence_records, topic, context.request)
    result = TopicAgentLandscapeSummary(
        themes=derived_themes
        or [
            f"problem framing and task definition in {topic}",
            f"benchmark-driven evaluation for {topic}",
            f"practical deployment concerns in {topic}",
        ],
        active_methods=active_methods,
        likely_gaps=likely_gaps,
        saturated_areas=[
            "broad generic summaries without a sharply defined question",
        ],
    )
    context.landscape_summary = result
    return result


def _supporting_source_ids(
    evidence_records: list[TopicAgentSourceRecord],
    *,
    start: int,
    count: int,
) -> list[str]:
    if not evidence_records:
        return []
    selected = evidence_records[start : start + count]
    if len(selected) < count:
        selected = evidence_records[:count]
    ordered_ids: list[str] = []
    for record in selected:
        if record.source_id not in ordered_ids:
            ordered_ids.append(record.source_id)
    return ordered_ids


def _merge_supporting_source_ids(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for source_id in group:
            if source_id not in merged:
                merged.append(source_id)
    return merged


def generate_candidates(context: TopicAgentPipelineContext) -> list[TopicAgentCandidateTopic]:
    budget_bucket = _time_budget_bucket(context.request.constraints.time_budget_months)
    resource_bucket = _resource_bucket(context.request.constraints.resource_level)
    style = _preferred_style(context.request)
    evidence_records = context.evidence_records or []
    evidence_phrases = _filter_evidence_phrases(
        _extract_evidence_phrases(evidence_records),
        topic=context.request.interest,
    )
    evidence_cues = _detect_evidence_cues(evidence_records, context.request)
    benchmark_phrase = next((phrase for phrase in evidence_phrases if "benchmark" in phrase), None)
    grounding_phrase = next((phrase for phrase in evidence_phrases if "grounding" in phrase), None)
    reasoning_phrase = next((phrase for phrase in evidence_phrases if "reasoning" in phrase), None)

    candidate_1 = TopicAgentCandidateTopic(
        candidate_id="candidate_1",
        title="Benchmark-Guided Narrow Task Definition",
        research_question="How can a narrower benchmark task reveal actionable limitations in current methods?",
        positioning="gap-driven",
        novelty_note="Focuses on under-specified evaluation boundaries rather than generic performance claims.",
        feasibility_note="Moderate feasibility with public resources and modest compute.",
        risk_note="May become incremental if the task boundary is not sharply differentiated.",
        supporting_source_ids=_supporting_source_ids(evidence_records, start=0, count=2),
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
        supporting_source_ids=_merge_supporting_source_ids(
            _supporting_source_ids(evidence_records, start=0, count=1),
            _supporting_source_ids(evidence_records, start=2, count=1),
        ),
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
        supporting_source_ids=_supporting_source_ids(evidence_records, start=1, count=2),
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

    if benchmark_phrase:
        candidate_1.research_question = (
            f"How can a narrower {benchmark_phrase} setting reveal actionable limitations in current methods?"
        )
        candidate_1.open_questions = [
            f"Which {benchmark_phrase} slice best represents the intended problem?"
        ]
    elif evidence_cues["benchmark"]:
        candidate_1.research_question = (
            "How can a narrower benchmark slice expose shortcut behavior and weak multimodal dependence in current systems?"
        )
        candidate_1.open_questions = [
            "Which benchmark slice best isolates genuine image-grounded reasoning?"
        ]
    if grounding_phrase:
        candidate_1.novelty_note = (
            f"Uses {grounding_phrase} as a concrete lens for defining a sharper evaluation target."
        )
        candidate_3.open_questions.insert(
            0,
            f"What workflow support would make {grounding_phrase} evaluation more reproducible?",
        )
    if evidence_cues["clinical_reasoning"] or evidence_cues["document_qa"]:
        candidate_2.research_question = (
            "Can an existing method family be adapted effectively for document-centric clinical reasoning under strict compute and annotation constraints?"
        )
    elif reasoning_phrase:
        candidate_2.research_question = (
            f"Can an existing method family be adapted effectively for {reasoning_phrase} under strict compute and annotation constraints?"
        )
    if evidence_cues["hallucination_eval"]:
        candidate_1.research_question = (
            "How can a narrower evaluation slice expose hallucination risk and weak image grounding in current systems?"
        )
        candidate_2.research_question = (
            "Can an existing evaluation method be adapted to detect unsupported or weakly grounded answers in multimodal medical reasoning under strict compute constraints?"
        )
        candidate_3.open_questions.insert(
            0,
            "What workflow support would make hallucination audits and grounding checks easier to reproduce?",
        )
    if evidence_cues["visual_qa"]:
        candidate_1.open_questions.insert(
            0,
            "Which VQA-RAD or Med-VQA slice best isolates genuine image-grounded answering?",
        )

    if evidence_cues["radiology"]:
        candidate_1.open_questions.append("Would a radiology-focused slice produce a clearer and more feasible evaluation target?")
    if evidence_cues["trust"]:
        candidate_1.novelty_note = (
            "Focuses on trustworthy evaluation boundaries, not just raw task accuracy."
            if not grounding_phrase
            else candidate_1.novelty_note
        )
        candidate_3.open_questions.insert(
            0,
            "What workflow support would make trustworthy evaluation and audit trails easier to reproduce?",
        )
    if evidence_cues["agentic"]:
        candidate_2.novelty_note = (
            "Frames novelty through adapting agent-based reasoning workflows under tighter practical constraints."
        )

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
        candidate_1.novelty_note = (
            candidate_1.novelty_note
            if grounding_phrase
            else "Targets benchmark slicing and evaluation boundary design as the main source of research value."
        )

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
    diagnostics = context.evidence_diagnostics
    provider_detail = "an unknown evidence provider"
    if diagnostics:
        provider_detail = (
            f"{diagnostics.used_provider} provider"
            if not diagnostics.fallback_used
            else (
                f"{diagnostics.used_provider} provider after fallback from "
                f"{diagnostics.requested_provider} ({diagnostics.fallback_reason})"
            )
        )
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
            detail=f"Retrieved {evidence_count} evidence records using the {provider_detail}.",
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
        evidence_diagnostics=context.evidence_diagnostics
        or TopicAgentEvidenceDiagnostics(
            requested_provider="unknown",
            used_provider="unknown",
            fallback_used=False,
            fallback_reason=None,
            record_count=len(context.evidence_records or []),
            cache_hit=False,
        ),
    )
