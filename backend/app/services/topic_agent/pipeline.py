from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from app.schemas.topic_agent import (
    TopicAgentClarificationSuggestion,
    TopicAgentCandidateTopic,
    TopicAgentComparisonResult,
    TopicAgentConfidenceSummary,
    TopicAgentConvergenceResult,
    TopicAgentEvidenceDiagnostics,
    TopicAgentEvidencePresentation,
    TopicAgentEvidenceStatement,
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
    evidence_presentation: TopicAgentEvidencePresentation | None = None
    evidence_diagnostics: TopicAgentEvidenceDiagnostics | None = None
    trace: list[TopicAgentTraceEvent] | None = None


@dataclass
class TopicAgentCandidateDraft:
    draft_id: str
    direction_type: str
    working_title: str
    research_question: str
    novelty_note: str
    feasibility_note: str
    risk_note: str
    supporting_source_ids: list[str]
    open_questions: list[str]
    score: int


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
    "making",
    "tools",
    "software",
    "engineering",
    "agent",
    "agents",
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


def _query_intent_flags(request: TopicAgentExploreRequest) -> dict[str, bool]:
    query_text = _query_context_text(request)
    return {
        "hallucination_eval": any(
            term in query_text
            for term in {"hallucination", "grounding evaluation", "faithfulness", "unsupported answers"}
        ),
        "visual_qa": any(
            term in query_text
            for term in {"visual question answering", "med-vqa", "medical vqa", "vqa-rad", "radiology question answering"}
        ),
        "document_qa": any(
            term in query_text
            for term in {"document question answering", "document qa", "medical report", "report-centric"}
        ),
        "broad_medical_reasoning": (
            "medical reasoning" in query_text
            and not any(
                term in query_text
                for term in {
                    "document question answering",
                    "document qa",
                    "medical report",
                    "report-centric",
                    "visual question answering",
                    "vqa",
                    "radiology",
                    "hallucination",
                    "grounding",
                    "multimodal",
                }
            )
        ),
        "bug_fixing": _is_bug_fixing_query(request),
    }


def _is_bug_fixing_query(request: TopicAgentExploreRequest) -> bool:
    query_text = _query_context_text(request)
    return any(
        term in query_text
        for term in {
            "bug fixing",
            "bug-fixing",
            "program repair",
            "code repair",
            "automated bug fixing",
            "automated program repair",
            "software maintenance",
        }
    )


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
        "document_qa": any(term in combined_text for term in {"document question answering", "document qa", "medical report", "meddqa", "report layout"}),
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
    query_flags = _query_intent_flags(request)
    themes: list[str] = []
    if cues["benchmark"]:
        themes.append(f"benchmark design and stress-testing for {topic}")
    if cues["grounding"]:
        themes.append(f"cross-modal grounding and visual dependence in {topic}")
    if query_flags["hallucination_eval"]:
        themes.append(f"hallucination detection and failure analysis in {topic}")
    if query_flags["visual_qa"]:
        themes.append(f"radiology VQA and image-grounded answer reliability in {topic}")
    if (
        (query_flags["document_qa"] or cues["document_qa"])
        and not query_flags["hallucination_eval"]
        and not query_flags["broad_medical_reasoning"]
    ):
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
    query_flags = _query_intent_flags(request)
    methods: list[str] = []
    if cues["benchmark"]:
        methods.append("benchmark-centered experimental design")
    if cues["grounding"]:
        methods.append("grounding-aware evaluation and error analysis")
    if query_flags["hallucination_eval"]:
        methods.append("hallucination auditing and faithfulness checks")
    if cues["agentic"]:
        methods.append("agent-mediated problem decomposition")
    if (
        (query_flags["document_qa"] or cues["document_qa"])
        and not query_flags["hallucination_eval"]
        and not query_flags["broad_medical_reasoning"]
    ):
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
    query_flags = _query_intent_flags(request)
    gaps: list[str] = []
    if cues["benchmark"]:
        if query_flags["broad_medical_reasoning"]:
            gaps.append("benchmark protocols that distinguish genuine reasoning gains from answer-pattern shortcuts")
        elif query_flags["visual_qa"] or cues["grounding"] or cues["radiology"]:
            gaps.append("benchmark protocols that distinguish real image use from shortcut exploitation")
        else:
            gaps.append("benchmark protocols that distinguish genuine task gains from workflow or prompt shortcuts")
    if cues["trust"] or cues["grounding"]:
        gaps.append("trustworthy evaluation signals beyond accuracy-only reporting")
    if query_flags["hallucination_eval"]:
        gaps.append("medical hallucination checks that separate unsupported answers from weak image grounding")
    if cues["radiology"]:
        gaps.append("narrower radiology task slices that remain feasible under student-scale resources")
    if (
        (query_flags["document_qa"] or cues["document_qa"])
        and not query_flags["hallucination_eval"]
        and not query_flags["broad_medical_reasoning"]
    ):
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
    if any(term in phrase for term in {"workflow", "audit", "reproducibility"}):
        return f"workflow and reproducibility support in {topic}"
    if any(term in phrase for term in {"developer", "collaboration", "explainable"}):
        return f"developer collaboration and oversight in {topic}"
    if any(term in phrase for term in {"program improvement", "code intent", "specification"}):
        return f"program improvement and intent-aware workflows in {topic}"
    return f"applied research themes around {phrase} in {topic}"


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


def _dedupe_open_questions(questions: list[str]) -> list[str]:
    deduped: list[str] = []
    normalized_seen: set[str] = set()
    for question in questions:
        normalized = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
        if not normalized or normalized in normalized_seen:
            continue
        normalized_seen.add(normalized)
        deduped.append(question)
    return deduped


def _record_text(record: TopicAgentSourceRecord) -> str:
    return f"{record.title} {record.summary}".lower()


def _record_title_anchor(record: TopicAgentSourceRecord) -> str:
    title_lower = record.title.lower()
    preferred_phrases = [
        "developer workflow support",
        "developer tooling workflows",
        "software engineering",
        "developer-ai collaboration",
        "developer workflow",
        "program improvement",
        "code intent extraction",
        "tool-building agents",
        "empirical software engineering",
        "clinical reasoning",
        "medical reasoning",
        "decision-making",
        "visual question answering",
        "document question answering",
        "radiology vqa",
        "hallucination detection",
        "grounding evaluation",
        "reproducible coding agent evaluation",
        "benchmark",
    ]
    for phrase in preferred_phrases:
        if phrase in title_lower:
            return phrase
    if "making agent tools" in title_lower or "agent tools" in title_lower:
        return "tool-building agents"
    if "software developers" in title_lower or "generalist agents" in title_lower:
        return "developer workflow support"
    if "smart app development" in title_lower or "solidgpt" in title_lower:
        return "developer tooling workflows"
    if "empirical software engineering" in title_lower:
        return "empirical software engineering"

    summary_lower = record.summary.lower()
    for phrase in preferred_phrases:
        if phrase in summary_lower:
            return phrase
    if "developer workflow" in summary_lower or "developer workflows" in summary_lower:
        return "developer workflow support"
    if "reproducib" in summary_lower or "audit" in summary_lower:
        return "reproducible evaluation workflow"

    tokens = _tokenize_text(record.title)
    if len(tokens) >= 2:
        return " ".join(tokens[:2])
    if not tokens:
        summary_tokens = _tokenize_text(record.summary)
        if len(summary_tokens) >= 2:
            return " ".join(summary_tokens[:2])
        if summary_tokens:
            return summary_tokens[0]
        return "target workflow"
    return " ".join(tokens[:3])


def _infer_record_roles_for_drafts(
    record: TopicAgentSourceRecord,
    request: TopicAgentExploreRequest,
) -> set[str]:
    text = _record_text(record)
    query_text = _query_context_text(request)
    roles: set[str] = set()

    if record.source_type == "benchmark" or any(
        term in text for term in {"benchmark", "evaluation", "exam", "leaderboard", "stress test"}
    ):
        roles.add("benchmark_evaluation")
    if any(
        term in text
        for term in {
            "framework",
            "methodology",
            "method",
            "approach",
            "workflow",
            "program improvement",
            "developer-ai collaboration",
            "virtual patient",
        }
    ):
        roles.add("method_framework")
    if any(
        term in text
        for term in {"tooling", "tool", "pipeline", "reproducibility", "audit", "devsecops", "workflow"}
    ):
        roles.add("systems_tooling")
    if any(
        term in text
        for term in {"failure analysis", "hallucination", "calibration", "confidence", "metacognition", "reliability"}
    ):
        roles.add("failure_analysis")
    if record.source_type == "survey" or "systematic review" in text or "survey" in text:
        roles.add("survey_background")

    if (
        ("llm" in query_text or "agent" in query_text or "agents" in query_text)
        and any(term in query_text for term in {"software engineering", "developer tools", "developer workflows", "coding"})
    ):
        if any(
            term in text
            for term in {
                "numpy",
                "pandas",
                "python library",
                "array programming",
                "numerical python",
                "matrix",
                "matrices",
            }
        ) and not any(
            term in text
            for term in {
                "developer",
                "coding",
                "benchmark",
                "evaluation",
                "workflow",
                "agent",
                "program repair",
                "github issues",
            }
        ):
            roles.add("off_target_neighbor")

    if not roles:
        roles.add("domain_background")
    return roles


def _draft_score(
    *,
    direction_type: str,
    record: TopicAgentSourceRecord,
    request: TopicAgentExploreRequest,
    roles: set[str],
) -> int:
    score = 0
    style = _preferred_style(request)
    budget_bucket = _time_budget_bucket(request.constraints.time_budget_months)
    resource_bucket = _resource_bucket(request.constraints.resource_level)
    text = _record_text(record)

    score += 3 if record.source_tier == "A" else 1
    score += min(max(record.year - 2018, 0), 8)

    if direction_type == "evaluation":
        if "benchmark_evaluation" in roles:
            score += 8
        if "failure_analysis" in roles:
            score += 3
        if style == "benchmark-driven":
            score += 3
    elif direction_type == "transfer":
        if "method_framework" in roles:
            score += 8
        if style == "applied":
            score += 4
        if budget_bucket in {"tight", "moderate"}:
            score += 2
        if resource_bucket == "limited":
            score += 2
    elif direction_type == "systems":
        if "systems_tooling" in roles:
            score += 8
        if "failure_analysis" in roles:
            score += 2
        if style == "systems":
            score += 4
        if budget_bucket in {"tight", "moderate"}:
            score += 2

    if "off_target_neighbor" in roles:
        score -= 12
    if "survey_background" in roles and direction_type != "evaluation":
        score -= 2

    if any(term in text for term in {"developer", "coding", "workflow", "benchmark", "evaluation"}):
        score += 2

    return score


def _supports_transfer_draft(text: str) -> bool:
    return any(
        term in text
        for term in {
            "framework",
            "methodology",
            "method",
            "approach",
            "program improvement",
            "autonomous program improvement",
            "developer-ai collaboration",
            "decision-making",
            "differential diagnosis",
            "virtual patient",
            "zero-shot",
            "zero shot",
            "baseline",
            "coding tasks",
        }
    )


def _build_candidate_draft_from_record(
    record: TopicAgentSourceRecord,
    *,
    direction_type: str,
    request: TopicAgentExploreRequest,
    roles: set[str],
) -> TopicAgentCandidateDraft:
    anchor = _record_title_anchor(record)
    if direction_type == "evaluation":
        working_title = "Evidence-Grounded Evaluation Slice"
        research_question = f"How can a narrower evaluation slice around {anchor} reveal actionable limitations in current systems?"
        novelty_note = "Frames novelty through sharper evaluation boundaries rather than broader performance reporting."
        feasibility_note = "Moderate feasibility with public evidence and a bounded evaluation target."
        risk_note = "May become incremental if the evaluation slice is not sharply distinguished."
        open_questions = [f"Which {anchor} slice best isolates the intended failure mode or capability?"]
    elif direction_type == "systems":
        working_title = "Reproducible Workflow And Evaluation Support"
        research_question = f"What tooling or workflow support around {anchor} would make research in this area more reproducible?"
        novelty_note = "Shifts value from model novelty toward reproducibility, workflow support, and evaluation reliability."
        feasibility_note = "High feasibility for a short-cycle engineering-heavy project."
        risk_note = "Applied impact may be clearer than publication novelty unless the workflow pain point is precisely chosen."
        open_questions = [
            "What concrete reproducibility pain point should be prioritized first?",
            f"Which workflow improvement around {anchor} reduces setup or audit cost the most?",
        ]
    else:
        working_title = "Constraint-Aware Method Transfer"
        research_question = f"Can an existing method family associated with {anchor} be adapted effectively under strict practical constraints?"
        novelty_note = "Frames novelty through constrained adaptation of an existing method family."
        feasibility_note = "Strong fit for an applied project that can reuse a visible baseline."
        risk_note = "Novelty may depend heavily on the chosen constraint and evaluation design."
        open_questions = ["Which constraint creates the strongest research signal?"]

    return TopicAgentCandidateDraft(
        draft_id=f"{direction_type}_{record.source_id}",
        direction_type=direction_type,
        working_title=working_title,
        research_question=research_question,
        novelty_note=novelty_note,
        feasibility_note=feasibility_note,
        risk_note=risk_note,
        supporting_source_ids=[record.source_id],
        open_questions=open_questions,
        score=_draft_score(
            direction_type=direction_type,
            record=record,
            request=request,
            roles=roles,
        ),
    )


def _is_generic_anchor(anchor: str) -> bool:
    normalized = anchor.strip().lower()
    return normalized in {
        "",
        "current evidence",
        "software engineering",
        "target workflow",
        "benchmark",
        "empirical software engineering",
    }


def _non_visual_benchmark_question(anchor: str) -> tuple[str, list[str]]:
    if _is_generic_anchor(anchor):
        return (
            "How can a narrower benchmark slice reveal actionable limitations in current systems?",
            ["Which benchmark slice best isolates genuine task gains rather than workflow or prompt shortcuts?"],
        )
    return (
        f"How can a narrower evaluation slice around {anchor} reveal actionable limitations in current systems?",
        [f"Which {anchor} slice best isolates the intended failure mode or capability?"],
    )


def _generate_candidate_drafts(
    evidence_records: list[TopicAgentSourceRecord],
    request: TopicAgentExploreRequest,
) -> list[TopicAgentCandidateDraft]:
    drafts: list[TopicAgentCandidateDraft] = []
    for record in evidence_records:
        roles = _infer_record_roles_for_drafts(record, request)
        text = _record_text(record)
        if "benchmark_evaluation" in roles:
            drafts.append(
                _build_candidate_draft_from_record(
                    record,
                    direction_type="evaluation",
                    request=request,
                    roles=roles,
                )
            )
        if "method_framework" in roles and _supports_transfer_draft(text):
            drafts.append(
                _build_candidate_draft_from_record(
                    record,
                    direction_type="transfer",
                    request=request,
                    roles=roles,
                )
            )
        if "systems_tooling" in roles or "failure_analysis" in roles:
            drafts.append(
                _build_candidate_draft_from_record(
                    record,
                    direction_type="systems",
                    request=request,
                    roles=roles,
                )
            )

    deduped: list[TopicAgentCandidateDraft] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for draft in sorted(drafts, key=lambda item: (item.score, item.direction_type, item.draft_id), reverse=True):
        key = (draft.direction_type, tuple(draft.supporting_source_ids))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(draft)
    return deduped


def _select_candidate_draft(
    drafts: list[TopicAgentCandidateDraft],
    *,
    preferred_type: str,
    used_source_ids: set[str],
) -> TopicAgentCandidateDraft | None:
    best: TopicAgentCandidateDraft | None = None
    best_key: tuple[int, int] | None = None
    for draft in drafts:
        if draft.direction_type != preferred_type:
            continue
        unused_support = sum(1 for source_id in draft.supporting_source_ids if source_id not in used_source_ids)
        rank_key = (unused_support, draft.score)
        if best is None or rank_key > best_key:
            best = draft
            best_key = rank_key
    return best


def _apply_draft_to_candidate(
    candidate: TopicAgentCandidateTopic,
    draft: TopicAgentCandidateDraft | None,
    *,
    override_text: bool,
) -> TopicAgentCandidateTopic:
    if draft is None:
        return candidate
    candidate.supporting_source_ids = _merge_supporting_source_ids(
        draft.supporting_source_ids,
        candidate.supporting_source_ids,
    )
    if override_text:
        candidate.research_question = draft.research_question
        candidate.novelty_note = draft.novelty_note
        candidate.feasibility_note = draft.feasibility_note
        candidate.risk_note = draft.risk_note
        candidate.open_questions = _dedupe_open_questions(draft.open_questions + candidate.open_questions)
    return candidate


def _candidate_binding_terms(
    candidate: TopicAgentCandidateTopic,
    *,
    query_flags: dict[str, bool],
) -> set[str]:
    terms = set(_tokenize_text(" ".join([
        candidate.title,
        candidate.research_question,
        candidate.novelty_note,
        candidate.feasibility_note,
        candidate.risk_note,
        " ".join(candidate.open_questions),
    ])))

    if candidate.candidate_id == "candidate_1":
        terms.update({"benchmark", "evaluation", "verification", "reliability", "stress"})
        if query_flags["visual_qa"]:
            terms.update({"radiology", "vqa", "grounding"})
        if query_flags["hallucination_eval"]:
            terms.update({"hallucination", "grounding", "faithfulness"})
    elif candidate.candidate_id == "candidate_2":
        terms.update({"method", "methods", "framework", "baseline", "adapt", "adapted", "transfer"})
        if "agent" in candidate.novelty_note.lower():
            terms.update({"agent", "collaborative", "zero", "shot"})
        if query_flags["broad_medical_reasoning"]:
            terms.update({"agent", "framework", "collaborators", "zero", "shot"})
    elif candidate.candidate_id == "candidate_3":
        terms.update(
            {
                "workflow",
                "reproducible",
                "tooling",
                "audit",
                "pipeline",
                "annotation",
                "evaluation",
                "reliability",
                "metacognition",
                "verification",
            }
        )
        if query_flags["hallucination_eval"]:
            terms.update({"hallucination", "grounding", "audit"})

    return terms


def _candidate_record_fit(
    candidate: TopicAgentCandidateTopic,
    record: TopicAgentSourceRecord,
    *,
    query_flags: dict[str, bool],
) -> str:
    text = _record_text(record)

    if candidate.candidate_id == "candidate_1":
        if any(
            term in text
            for term in {
                "benchmark",
                "evaluation",
                "defects4j",
                "humanevalfix",
                "swe-bench",
                "empirical evaluation",
            }
        ):
            return "benchmark_support"
        return "general"

    if candidate.candidate_id == "candidate_2":
        if query_flags.get("bug_fixing") and any(
            term in text
            for term in {
                "program repair",
                "bug fixing",
                "repairing",
                "repair bot",
                "repair agent",
                "defects4j",
            }
        ):
            return "method_support"
        if query_flags.get("bug_fixing") and any(
            term in text
            for term in {
                "agent-computer interface",
                "repository navigation",
                "software engineering: a survey",
                "software engineering tasks",
            }
        ):
            return "benchmark_context"
        if any(
            term in text
            for term in {
                "framework",
                "agent",
                "collaborative",
                "zero-shot",
                "zero shot",
                "decision-making",
                "differential diagnosis",
                "virtual patient",
                "clinical reasoning skills",
                "educational tools",
                "autonomous program improvement",
                "developer-ai collaboration",
                "developer workflows",
                "coding tasks",
                "program repair",
                "bug fixing",
                "repairing",
                "lightweight",
                "compact",
                "transformers",
            }
        ):
            return "method_support"
        if any(
            term in text
            for term in {
                "benchmark",
                "examination",
                "usmle",
                "metacognition",
                "free-response",
                "free response",
            }
        ):
            return "benchmark_context"
        if any(
            term in text
            for term in {
                "document question answering",
                "visual question answering",
                "vqa",
                "medical report",
            }
        ):
            return "off_topic_subtask"
        return "general"

    if candidate.candidate_id == "candidate_3":
        if any(
            term in text
            for term in {
                "workflow",
                "reproducible",
                "audit",
                "annotation",
                "tooling",
                "pipeline",
                "agent-computer interface",
                "langgraph",
                "repository",
                "tests",
                "debugging",
                "bug fixing",
                "metacognition",
                "calibration",
                "confidence",
                "clinical decision support",
                "medical challenge problems",
            }
        ):
            return "systems_support"
        if any(
            term in text
            for term in {
                "reliable",
                "reliability",
                "verification",
                "evaluation",
                "failure analysis",
            }
        ):
            return "evaluation_support"
        if query_flags["broad_medical_reasoning"] and any(
            term in text
            for term in {
                "document question answering",
                "document qa",
                "medical report",
                "report images",
                "report layout",
                "benchmark for medical specialization",
                "real-world chinese medical report",
            }
        ):
            return "task_benchmark"
        return "general"

    return "general"


def _rank_supporting_source_ids_for_candidate(
    candidate: TopicAgentCandidateTopic,
    evidence_records: list[TopicAgentSourceRecord],
    *,
    query_flags: dict[str, bool],
    fallback_ids: list[str],
    limit: int = 2,
) -> list[str]:
    if not evidence_records:
        return []

    if candidate.candidate_id == "candidate_1":
        preferred_records = [
            record
            for record in evidence_records
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "benchmark_support"
        ]
        if preferred_records:
            evidence_records = preferred_records + [
                record for record in evidence_records if record not in preferred_records
            ]

    if candidate.candidate_id == "candidate_2":
        preferred_records = [
            record
            for record in evidence_records
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "method_support"
        ]
        if len(preferred_records) < limit:
            preferred_records.extend(
                record
                for record in evidence_records
                if _candidate_record_fit(candidate, record, query_flags=query_flags) == "benchmark_context"
                and record not in preferred_records
            )
        if preferred_records:
            evidence_records = preferred_records + [
                record for record in evidence_records if record not in preferred_records
            ]

    if candidate.candidate_id == "candidate_3":
        preferred_records = [
            record
            for record in evidence_records
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "systems_support"
        ]
        if len(preferred_records) < limit:
            preferred_records.extend(
                record
                for record in evidence_records
                if _candidate_record_fit(candidate, record, query_flags=query_flags) == "evaluation_support"
                and record not in preferred_records
            )
        if preferred_records:
            evidence_records = preferred_records + [
                record for record in evidence_records if record not in preferred_records
            ]

    binding_terms = _candidate_binding_terms(candidate, query_flags=query_flags)
    ranked: list[tuple[int, int, int, str]] = []
    for index, record in enumerate(evidence_records):
        text = _record_text(record)
        overlap = sum(1 for term in binding_terms if term in text)
        if candidate.candidate_id == "candidate_1":
            if "benchmark" in text:
                overlap += 3
            if any(term in text for term in {"verification", "reliable", "reliability", "metacognition"}):
                overlap += 1
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "benchmark_support":
                overlap += 6
        elif candidate.candidate_id == "candidate_2":
            if any(term in text for term in {"agent", "framework", "collaborative", "zero-shot", "zero shot"}):
                overlap += 3
            if any(term in text for term in {"method", "baseline", "adapt"}):
                overlap += 1
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "method_support":
                overlap += 8
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "benchmark_context":
                overlap -= 1
            if _candidate_record_fit(candidate, record, query_flags=query_flags) == "off_topic_subtask":
                overlap -= 4
            if query_flags["broad_medical_reasoning"] and "document question answering" in text:
                overlap -= 1
        elif candidate.candidate_id == "candidate_3":
            if any(term in text for term in {"workflow", "reproducible", "audit", "annotation"}):
                overlap += 3
            if any(term in text for term in {"tool", "tooling", "pipeline"}):
                overlap += 1
            if any(term in text for term in {"reliable", "reliability", "metacognition", "verification", "evaluation"}):
                overlap += 2
            if any(
                term in text
                for term in {
                    "benchmarking expert-level medical reasoning",
                    "metacognition",
                    "confidence",
                    "calibration",
                    "medical challenge problems",
                    "clinical decision support",
                }
            ):
                overlap += 2
            if query_flags["broad_medical_reasoning"]:
                if any(
                    term in text
                    for term in {
                        "document question answering",
                        "document qa",
                        "medical report",
                        "report images",
                        "report layout",
                    }
                ):
                    overlap -= 4
                if any(
                    term in text
                    for term in {
                        "benchmark for medical specialization",
                        "real-world chinese medical report",
                    }
                ):
                    overlap -= 2

        fallback_bonus = 3 if record.source_id in fallback_ids else 0
        tier_bonus = 1 if record.source_tier == "A" else 0
        ranked.append((overlap, fallback_bonus, tier_bonus, record.source_id))

    ranked.sort(reverse=True)
    if not ranked or ranked[0][0] <= 0:
        return fallback_ids[:limit]

    selected: list[str] = []
    for overlap, _fallback_bonus, _tier_bonus, source_id in ranked:
        if source_id not in selected:
            selected.append(source_id)
        if len(selected) == limit:
            break

    if selected:
        return selected
    return fallback_ids[:limit]


def _rebind_candidate_supporting_sources(
    candidates: list[TopicAgentCandidateTopic],
    evidence_records: list[TopicAgentSourceRecord],
    *,
    query_flags: dict[str, bool],
) -> list[TopicAgentCandidateTopic]:
    for candidate in candidates:
        candidate.supporting_source_ids = _rank_supporting_source_ids_for_candidate(
            candidate,
            evidence_records,
            query_flags=query_flags,
            fallback_ids=candidate.supporting_source_ids,
        )
    return candidates


def _apply_query_specific_candidate_polish(
    candidates: list[TopicAgentCandidateTopic],
    *,
    query_flags: dict[str, bool],
) -> list[TopicAgentCandidateTopic]:
    if not candidates:
        return candidates

    candidate_1, candidate_2, candidate_3 = candidates

    if query_flags["visual_qa"]:
        candidate_2.research_question = (
            "Can an existing radiology VQA method family be adapted effectively under strict compute and annotation constraints?"
        )

    if query_flags["hallucination_eval"]:
        candidate_3.open_questions = [
            "What workflow support would make hallucination audits and grounding checks easier to reproduce?",
            "What concrete reproducibility pain point should be prioritized first?",
            "Which workflow improvement reduces compute or setup cost the most?",
        ]

    candidate_1.open_questions = _dedupe_open_questions(candidate_1.open_questions)
    candidate_2.open_questions = _dedupe_open_questions(candidate_2.open_questions)
    candidate_3.open_questions = _dedupe_open_questions(candidate_3.open_questions)
    return [candidate_1, candidate_2, candidate_3]


def _allow_draft_text_override(
    request: TopicAgentExploreRequest,
    *,
    query_flags: dict[str, bool],
) -> bool:
    query_text = _query_context_text(request)
    if any(query_flags.values()):
        return False
    if any(term in query_text for term in {"medical", "clinical", "radiology", "biomedical"}):
        return False
    return True


def _specialize_bug_fixing_candidates(
    candidates: list[TopicAgentCandidateTopic],
    *,
    request: TopicAgentExploreRequest,
) -> list[TopicAgentCandidateTopic]:
    if not _is_bug_fixing_query(request) or len(candidates) < 3:
        return candidates

    candidate_3 = candidates[2]
    normalized_question = candidate_3.research_question.strip().lower()
    if (
        "software engineering" in normalized_question
        or normalized_question
        == "what tooling or evaluation workflow improvements would make research in this area more reproducible?"
    ):
        candidate_3.research_question = (
            "What tooling or workflow support for reproducible bug-fixing agent evaluation would make research in this area more reproducible?"
        )
        candidate_3.open_questions = _dedupe_open_questions(
            [
                "What concrete reproducibility pain point should be prioritized first?",
                "Which workflow improvement for reproducible bug-fixing agent evaluation reduces setup or audit cost the most?",
                "Which workflow improvement reduces compute or setup cost the most?",
            ]
            + candidate_3.open_questions
        )
    return candidates


def generate_candidates(context: TopicAgentPipelineContext) -> list[TopicAgentCandidateTopic]:
    budget_bucket = _time_budget_bucket(context.request.constraints.time_budget_months)
    resource_bucket = _resource_bucket(context.request.constraints.resource_level)
    style = _preferred_style(context.request)
    evidence_records = context.evidence_records or []
    candidate_drafts = _generate_candidate_drafts(evidence_records, context.request)
    evidence_phrases = _filter_evidence_phrases(
        _extract_evidence_phrases(evidence_records),
        topic=context.request.interest,
    )
    evidence_cues = _detect_evidence_cues(evidence_records, context.request)
    query_flags = _query_intent_flags(context.request)
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
        if query_flags["broad_medical_reasoning"]:
            candidate_1.research_question = (
                "How can a narrower benchmark slice expose shortcut behavior and weak reasoning verification in current systems?"
            )
            candidate_1.open_questions = [
                "Which benchmark slice best isolates genuine reasoning quality rather than answer-pattern matching?"
            ]
        else:
            candidate_1.research_question = (
                "How can a narrower benchmark slice expose shortcut behavior and weak evaluation robustness in current systems?"
            )
            candidate_1.open_questions = [
                "Which benchmark slice best isolates genuine task gains rather than workflow or prompt shortcuts?"
            ]
    if grounding_phrase:
        candidate_1.novelty_note = (
            f"Uses {grounding_phrase} as a concrete lens for defining a sharper evaluation target."
        )
        candidate_3.open_questions.insert(
            0,
            f"What workflow support would make {grounding_phrase} evaluation more reproducible?",
        )
    if query_flags["document_qa"] or (
        evidence_cues["document_qa"] and not query_flags["broad_medical_reasoning"]
    ):
        candidate_2.research_question = (
            "Can an existing method family be adapted effectively for document-centric clinical reasoning under strict compute and annotation constraints?"
        )
    elif query_flags["broad_medical_reasoning"]:
        candidate_2.research_question = (
            "Can an existing medical reasoning method family be adapted effectively under strict compute and annotation constraints?"
        )
    elif reasoning_phrase:
        candidate_2.research_question = (
            f"Can an existing method family be adapted effectively for {reasoning_phrase} under strict compute and annotation constraints?"
        )
    if query_flags["hallucination_eval"]:
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
    if query_flags["visual_qa"]:
        candidate_1.research_question = (
            "How can a narrower radiology VQA benchmark slice expose weak image-grounded answering in current systems?"
        )
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

    used_source_ids: set[str] = set()
    draft_for_candidate_1 = _select_candidate_draft(
        candidate_drafts,
        preferred_type="evaluation",
        used_source_ids=used_source_ids,
    )
    if draft_for_candidate_1 is not None:
        used_source_ids.update(draft_for_candidate_1.supporting_source_ids)
    draft_for_candidate_2 = _select_candidate_draft(
        candidate_drafts,
        preferred_type="transfer",
        used_source_ids=used_source_ids,
    )
    if draft_for_candidate_2 is not None:
        used_source_ids.update(draft_for_candidate_2.supporting_source_ids)
    draft_for_candidate_3 = _select_candidate_draft(
        candidate_drafts,
        preferred_type="systems",
        used_source_ids=used_source_ids,
    )

    allow_draft_text_override = _allow_draft_text_override(
        context.request,
        query_flags=query_flags,
    )
    candidate_1 = _apply_draft_to_candidate(
        candidate_1,
        draft_for_candidate_1,
        override_text=allow_draft_text_override,
    )
    candidate_2 = _apply_draft_to_candidate(
        candidate_2,
        draft_for_candidate_2,
        override_text=allow_draft_text_override,
    )
    candidate_3 = _apply_draft_to_candidate(
        candidate_3,
        draft_for_candidate_3,
        override_text=allow_draft_text_override,
    )

    if allow_draft_text_override:
        draft_candidate_1_anchor = ""
        if draft_for_candidate_1 is not None:
            for record in evidence_records:
                if record.source_id == draft_for_candidate_1.supporting_source_ids[0]:
                    draft_candidate_1_anchor = _record_title_anchor(record)
                    break
        if not query_flags["visual_qa"] and not query_flags["hallucination_eval"]:
            candidate_1.research_question, candidate_1.open_questions = _non_visual_benchmark_question(
                draft_candidate_1_anchor
            )
        if "current evidence" in candidate_2.research_question.lower():
            candidate_2.research_question = (
                "Can an existing coding-agent method family be adapted effectively under strict practical constraints?"
            )
        if "associated with software engineering" in candidate_2.research_question.lower():
            candidate_2.research_question = (
                "Can an existing coding-agent method family be adapted effectively under strict practical constraints?"
            )
        if any(
            bad_phrase in candidate_3.research_question.lower()
            for bad_phrase in {"around openhands platform developers", "around empowering smart development"}
        ):
            candidate_3.research_question = (
                "What tooling or workflow support for reproducible coding-agent evaluation would make research in this area more reproducible?"
            )
            candidate_3.open_questions = _dedupe_open_questions(
                [
                    "What concrete reproducibility pain point should be prioritized first?",
                    "Which workflow improvement for reproducible coding-agent evaluation reduces setup or audit cost the most?",
                    "Which workflow improvement reduces compute or setup cost the most?",
                ]
                + candidate_3.open_questions
            )
        if _is_bug_fixing_query(context.request) and (
            "software engineering" in candidate_3.research_question.lower()
            or candidate_3.research_question.lower()
            == "what tooling or evaluation workflow improvements would make research in this area more reproducible?"
        ):
            candidate_3.research_question = (
                "What tooling or workflow support for reproducible bug-fixing agent evaluation would make research in this area more reproducible?"
            )
            candidate_3.open_questions = _dedupe_open_questions(
                [
                    "What concrete reproducibility pain point should be prioritized first?",
                    "Which workflow improvement for reproducible bug-fixing agent evaluation reduces setup or audit cost the most?",
                    "Which workflow improvement reduces compute or setup cost the most?",
                ]
                + candidate_3.open_questions
            )

    result = [
        candidate_1,
        candidate_2,
        candidate_3,
    ]
    result = _apply_query_specific_candidate_polish(
        result,
        query_flags=query_flags,
    )
    result = _specialize_bug_fixing_candidates(
        result,
        request=context.request,
    )
    result = _rebind_candidate_supporting_sources(
        result,
        evidence_records,
        query_flags=query_flags,
    )
    if allow_draft_text_override:
        result[0].supporting_source_ids = _merge_supporting_source_ids(
            draft_for_candidate_1.supporting_source_ids if draft_for_candidate_1 else [],
            result[0].supporting_source_ids,
        )
        result[1].supporting_source_ids = _merge_supporting_source_ids(
            draft_for_candidate_2.supporting_source_ids if draft_for_candidate_2 else [],
            result[1].supporting_source_ids,
        )
        result[2].supporting_source_ids = _merge_supporting_source_ids(
            draft_for_candidate_3.supporting_source_ids if draft_for_candidate_3 else [],
            result[2].supporting_source_ids,
        )
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


def _candidate_by_id(
    candidate_topics: list[TopicAgentCandidateTopic],
    candidate_id: str | None,
) -> TopicAgentCandidateTopic | None:
    if not candidate_id:
        return None
    for candidate in candidate_topics:
        if candidate.candidate_id == candidate_id:
            return candidate
    return None


def _record_keyword_overlap(
    record: TopicAgentSourceRecord,
    statement: str,
) -> int:
    statement_tokens = set(_tokenize_text(statement))
    if not statement_tokens:
        return 0
    record_tokens = set(_tokenize_text(f"{record.title} {record.summary}"))
    return len(statement_tokens.intersection(record_tokens))


def _rank_supporting_source_ids_for_statement(
    statement: str,
    evidence_records: list[TopicAgentSourceRecord],
    *,
    fallback_ids: list[str],
    limit: int = 3,
) -> list[str]:
    ranked: list[tuple[int, int, str]] = []
    for index, record in enumerate(evidence_records):
        overlap = _record_keyword_overlap(record, statement)
        if overlap <= 0:
            continue
        tier_bonus = 1 if record.source_tier == "A" else 0
        ranked.append((overlap, tier_bonus, record.source_id))

    ranked.sort(reverse=True)
    selected = [source_id for _overlap, _tier_bonus, source_id in ranked[:limit]]
    if selected:
        return selected
    return fallback_ids[:limit]


def build_evidence_presentation(context: TopicAgentPipelineContext) -> TopicAgentEvidencePresentation:
    evidence_records = context.evidence_records or []
    candidate_topics = context.candidate_topics or []
    convergence_result = context.convergence_result
    landscape_summary = context.landscape_summary

    source_facts = [
        TopicAgentEvidenceStatement(
            statement=(
                f"Retrieved {record.source_type} evidence '{record.title}' ({record.year}) "
                f"as tier {record.source_tier} support for the current topic."
            ),
            statement_type="source_fact",
            supporting_source_ids=[record.source_id],
            note="Directly grounded in retrieved source metadata and source summary.",
        )
        for record in evidence_records[:3]
    ]

    synthesis_support_ids = [
        record.source_id
        for record in evidence_records[:3]
    ]
    system_synthesis: list[TopicAgentEvidenceStatement] = []
    if landscape_summary and landscape_summary.themes:
        theme_statement = (
            "Current evidence clusters most strongly around "
            + ", ".join(landscape_summary.themes[:2])
            + "."
        )
        system_synthesis.append(
            TopicAgentEvidenceStatement(
                statement=theme_statement,
                statement_type="system_synthesis",
                supporting_source_ids=_rank_supporting_source_ids_for_statement(
                    theme_statement,
                    evidence_records,
                    fallback_ids=synthesis_support_ids,
                ),
                note="Agent synthesis over multiple retrieved sources with theme-level evidence matching.",
            )
        )
    if candidate_topics:
        candidate_support_ids = _merge_supporting_source_ids(
            *[candidate.supporting_source_ids for candidate in candidate_topics]
        )
        system_synthesis.append(
            TopicAgentEvidenceStatement(
                statement=(
                    f"The current output separates into {len(candidate_topics)} candidate directions "
                    "with distinct positioning and comparison scores."
                ),
                statement_type="system_synthesis",
                supporting_source_ids=(candidate_support_ids or synthesis_support_ids)[:4],
                note="Agent synthesis over candidate generation and comparison outputs, anchored to candidate support sets.",
            )
        )

    tentative_inferences: list[TopicAgentEvidenceStatement] = []
    if convergence_result:
        recommended_candidate = _candidate_by_id(
            candidate_topics,
            convergence_result.recommended_candidate_id,
        )
        tentative_inferences.append(
            TopicAgentEvidenceStatement(
                statement=(
                    f"{convergence_result.recommended_candidate_id} is currently the leading direction "
                    "under the present constraints."
                ),
                statement_type="tentative_inference",
                supporting_source_ids=(
                    recommended_candidate.supporting_source_ids
                    if recommended_candidate
                    else synthesis_support_ids
                ),
                note="Recommendation-level inference that still requires human validation.",
                uncertainty_reason=(
                    "This recommendation remains constraint-sensitive and depends on the current evidence bundle, "
                    "not on a settled benchmark choice or direct experimental validation."
                ),
                missing_evidence=convergence_result.manual_checks[:2],
            )
        )
        if convergence_result.manual_checks:
            tentative_inferences.append(
                TopicAgentEvidenceStatement(
                    statement=convergence_result.manual_checks[0],
                    statement_type="tentative_inference",
                    supporting_source_ids=(
                    recommended_candidate.supporting_source_ids
                    if recommended_candidate
                    else synthesis_support_ids
                ),
                note="Open validation requirement rather than a settled fact.",
                uncertainty_reason=(
                    "The recommendation should not be treated as final until this validation step is checked."
                ),
                missing_evidence=[convergence_result.manual_checks[0]],
            )
        )

    result = TopicAgentEvidencePresentation(
        source_facts=source_facts,
        system_synthesis=system_synthesis,
        tentative_inferences=tentative_inferences,
    )
    context.evidence_presentation = result
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


def build_human_confirmations(context: TopicAgentPipelineContext) -> list[str]:
    framing_result = context.framing_result
    convergence_result = context.convergence_result
    confirmations: list[str] = []

    missing_clarification_map = {
        "time_budget": "Confirm the expected project timeline before accepting the recommendation.",
        "resource_level": "Confirm the available resource level so feasibility judgments are grounded.",
        "preferred_style": "Confirm whether the project should prioritize theory, systems work, or applied execution.",
    }

    for missing_field in (framing_result.missing_clarifications if framing_result else []):
        confirmation = missing_clarification_map.get(
            missing_field,
            f"Confirm the missing framing detail for {missing_field} before moving forward.",
        )
        if confirmation not in confirmations:
            confirmations.append(confirmation)

    if framing_result:
        framing_confirmation = (
            f"Confirm that the system correctly interpreted the topic as "
            f"'{framing_result.normalized_topic}'."
        )
        if framing_confirmation not in confirmations:
            confirmations.append(framing_confirmation)

    if convergence_result:
        recommendation_confirmation = (
            f"Confirm that {convergence_result.recommended_candidate_id} should remain the leading direction "
            f"after reviewing the supporting evidence and risks."
        )
        if recommendation_confirmation not in confirmations:
            confirmations.append(recommendation_confirmation)
        for manual_check in convergence_result.manual_checks[:2]:
            normalized = f"Manual check: {manual_check}"
            if normalized not in confirmations:
                confirmations.append(normalized)

    return confirmations


def build_clarification_suggestions(
    context: TopicAgentPipelineContext,
) -> list[TopicAgentClarificationSuggestion]:
    framing_result = context.framing_result
    if not framing_result or not framing_result.missing_clarifications:
        return []

    suggestion_specs = {
        "time_budget": {
            "prompt": "Choose a rough project timeline so the agent can judge scope realistically.",
            "reason": "The current recommendation still lacks an explicit time budget.",
            "suggested_values": ["3", "6", "12"],
            "refine_patch": {
                "constraints": {
                    "time_budget_months": 6,
                }
            },
        },
        "resource_level": {
            "prompt": "Specify the available resource level so feasibility estimates are grounded.",
            "reason": "The current recommendation still lacks a resource assumption.",
            "suggested_values": ["student", "lab", "team"],
            "refine_patch": {
                "constraints": {
                    "resource_level": "student",
                }
            },
        },
        "preferred_style": {
            "prompt": "Choose whether the project should lean applied, systems, or benchmark-driven.",
            "reason": "The current recommendation still lacks a preferred project style.",
            "suggested_values": ["applied", "systems", "benchmark-driven"],
            "refine_patch": {
                "constraints": {
                    "preferred_style": "applied",
                }
            },
        },
    }

    suggestions: list[TopicAgentClarificationSuggestion] = []
    for missing_field in framing_result.missing_clarifications:
        spec = suggestion_specs.get(missing_field)
        if not spec:
            continue
        suggestions.append(
            TopicAgentClarificationSuggestion(
                field_key=missing_field,
                prompt=spec["prompt"],
                reason=spec["reason"],
                suggested_values=spec["suggested_values"],
                refine_patch=spec["refine_patch"],
            )
        )
    return suggestions


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
    build_evidence_presentation(context)
    build_trace(context)
    human_confirmations = build_human_confirmations(context)
    clarification_suggestions = build_clarification_suggestions(context)
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
        evidence_presentation=context.evidence_presentation or TopicAgentEvidencePresentation(),
        human_confirmations=human_confirmations,
        clarification_suggestions=clarification_suggestions,
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
