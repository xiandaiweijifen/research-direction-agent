from pydantic import BaseModel, Field


class TopicAgentConstraintSet(BaseModel):
    time_budget_months: int | None = None
    resource_level: str | None = None
    preferred_style: str | None = None
    notes: str | None = None


class TopicAgentExploreRequest(BaseModel):
    interest: str
    problem_domain: str | None = None
    seed_idea: str | None = None
    constraints: TopicAgentConstraintSet = Field(default_factory=TopicAgentConstraintSet)


class TopicAgentRefineRequest(BaseModel):
    interest: str | None = None
    problem_domain: str | None = None
    seed_idea: str | None = None
    constraints: TopicAgentConstraintSet = Field(default_factory=TopicAgentConstraintSet)


class TopicAgentSourceRecord(BaseModel):
    source_id: str
    title: str
    source_type: str
    source_tier: str
    year: int
    authors_or_publisher: str
    identifier: str
    url: str
    summary: str
    relevance_reason: str


class TopicAgentFramingResult(BaseModel):
    normalized_topic: str
    extracted_constraints: dict[str, str] = Field(default_factory=dict)
    missing_clarifications: list[str] = Field(default_factory=list)
    search_questions: list[str] = Field(default_factory=list)


class TopicAgentLandscapeSummary(BaseModel):
    themes: list[str] = Field(default_factory=list)
    active_methods: list[str] = Field(default_factory=list)
    likely_gaps: list[str] = Field(default_factory=list)
    saturated_areas: list[str] = Field(default_factory=list)


class TopicAgentCandidateTopic(BaseModel):
    candidate_id: str
    title: str
    research_question: str
    positioning: str
    novelty_note: str
    feasibility_note: str
    risk_note: str
    supporting_source_ids: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class TopicAgentComparisonResult(BaseModel):
    dimensions: list[str] = Field(default_factory=list)
    summary: str
    candidate_assessments: list[dict[str, str]] = Field(default_factory=list)


class TopicAgentConvergenceResult(BaseModel):
    recommended_candidate_id: str
    backup_candidate_id: str | None = None
    rationale: str
    manual_checks: list[str] = Field(default_factory=list)


class TopicAgentConfidenceSummary(BaseModel):
    evidence_coverage: str
    source_quality: str
    candidate_separation: str
    conflict_level: str
    rationale: list[str] = Field(default_factory=list)


class TopicAgentEvidenceDiagnostics(BaseModel):
    requested_provider: str
    used_provider: str
    fallback_used: bool = False
    fallback_reason: str | None = None
    record_count: int = 0
    cache_hit: bool = False


class TopicAgentTraceEvent(BaseModel):
    stage: str
    status: str
    timestamp: str
    detail: str


class TopicAgentSessionResponse(BaseModel):
    session_id: str
    created_at: str
    updated_at: str
    user_input: TopicAgentExploreRequest
    framing_result: TopicAgentFramingResult
    evidence_records: list[TopicAgentSourceRecord] = Field(default_factory=list)
    landscape_summary: TopicAgentLandscapeSummary
    candidate_topics: list[TopicAgentCandidateTopic] = Field(default_factory=list)
    comparison_result: TopicAgentComparisonResult
    convergence_result: TopicAgentConvergenceResult
    human_confirmations: list[str] = Field(default_factory=list)
    trace: list[TopicAgentTraceEvent] = Field(default_factory=list)
    confidence_summary: TopicAgentConfidenceSummary
    evidence_diagnostics: TopicAgentEvidenceDiagnostics


class TopicAgentSessionSummary(BaseModel):
    session_id: str
    created_at: str
    updated_at: str
    interest: str
    problem_domain: str | None = None
    candidate_count: int = 0
    recommended_candidate_id: str | None = None


class TopicAgentSessionListResponse(BaseModel):
    sessions: list[TopicAgentSessionSummary] = Field(default_factory=list)
