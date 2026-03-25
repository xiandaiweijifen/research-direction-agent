import { useState, type FormEvent } from "react";

import type {
  Locale,
  TopicAgentComparisonAssessment,
  TopicAgentSessionResponse,
  TopicAgentSessionSummary,
  TopicAgentSourceRecord,
} from "../types";

type TopicWorkspaceProps = {
  locale: Locale;
  interest: string;
  problemDomain: string;
  seedIdea: string;
  timeBudgetMonths: string;
  resourceLevel: string;
  preferredStyle: string;
  topicResult: TopicAgentSessionResponse | null;
  topicComparisonResult: TopicAgentSessionResponse | null;
  topicSessions: TopicAgentSessionSummary[];
  topicBusy: boolean;
  topicError: string;
  onChangeInterest: (value: string) => void;
  onChangeProblemDomain: (value: string) => void;
  onChangeSeedIdea: (value: string) => void;
  onChangeTimeBudgetMonths: (value: string) => void;
  onChangeResourceLevel: (value: string) => void;
  onChangePreferredStyle: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onRefine: () => void;
  onLoadSession: (sessionId: string) => void;
  onCompareSession: (sessionId: string) => void;
};

export function TopicWorkspaceV2({
  locale,
  interest,
  problemDomain,
  seedIdea,
  timeBudgetMonths,
  resourceLevel,
  preferredStyle,
  topicResult,
  topicComparisonResult,
  topicSessions,
  topicBusy,
  topicError,
  onChangeInterest,
  onChangeProblemDomain,
  onChangeSeedIdea,
  onChangeTimeBudgetMonths,
  onChangeResourceLevel,
  onChangePreferredStyle,
  onSubmit,
  onRefine,
  onLoadSession,
  onCompareSession,
}: TopicWorkspaceProps) {
  const [evidenceTierFilter, setEvidenceTierFilter] = useState("all");
  const [evidenceTypeFilter, setEvidenceTypeFilter] = useState("all");
  const [focusedEvidenceId, setFocusedEvidenceId] = useState<string | null>(null);

  const evidenceTitleById = new Map(
    (topicResult?.evidence_records ?? []).map((record) => [record.source_id, record.title]),
  );
  const candidateTitleById = new Map(
    (topicResult?.candidate_topics ?? []).map((candidate) => [candidate.candidate_id, candidate.title]),
  );
  const evidenceTierOptions = Array.from(
    new Set((topicResult?.evidence_records ?? []).map((record) => record.source_tier)),
  );
  const evidenceTypeOptions = Array.from(
    new Set((topicResult?.evidence_records ?? []).map((record) => record.source_type)),
  );
  const filteredEvidenceRecords = (topicResult?.evidence_records ?? []).filter((record) => {
    const tierMatches = evidenceTierFilter === "all" || record.source_tier === evidenceTierFilter;
    const typeMatches = evidenceTypeFilter === "all" || record.source_type === evidenceTypeFilter;
    return tierMatches && typeMatches;
  });
  const focusedEvidence =
    filteredEvidenceRecords.find((record) => record.source_id === focusedEvidenceId) ??
    topicResult?.evidence_records.find((record) => record.source_id === focusedEvidenceId) ??
    filteredEvidenceRecords[0] ??
    topicResult?.evidence_records[0] ??
    null;

  const copy: Record<string, string> =
    locale === "zh"
      ? {
          workspace: "选题工作台",
          title: "科研选题副驾",
          banner: "从研究兴趣出发，检查问题 framing、证据、候选选题、比较结果与收敛建议。",
          formTitle: "探索输入",
          formCopy: "用一个小而清晰的结构化表单驱动 Topic Agent MVP 工作流。",
          interest: "研究兴趣",
          problemDomain: "问题域",
          seedIdea: "初步想法",
          timeBudget: "时间预算（月）",
          resourceLevel: "资源水平",
          preferredStyle: "偏好风格",
          run: "运行 Topic Agent",
          refine: "基于当前结果收敛",
          running: "正在运行 Topic Agent...",
          framing: "问题 Framing",
          landscape: "方向全景",
          evidence: "证据记录",
          evidenceFocus: "焦点证据",
          evidenceFilters: "证据过滤",
          all: "全部",
          sourceTier: "来源等级",
          sourceType: "来源类型",
          relevance: "相关性",
          openSource: "打开来源",
          candidates: "候选选题",
          supportingEvidence: "支撑证据",
          openQuestions: "待确认问题",
          comparison: "比较与收敛",
          candidateScores: "候选比较",
          rationale: "推荐理由",
          dimensions: "比较维度",
          trace: "执行轨迹",
          confidence: "可信度摘要",
          recentSessions: "最近探索记录",
          load: "加载",
          noResult: "还没有 Topic Agent 结果",
          noResultCopy: "填写研究兴趣并运行后，这里会展示结构化的选题分析结果。",
          recommendation: "推荐方向",
          backup: "备选方向",
          searchQuestions: "检索子问题",
          manualChecks: "人工确认",
          themes: "主题簇",
          methods: "活跃方法",
          gaps: "可能空白",
          saturated: "相对饱和",
          topicCount: "个候选题",
        }
      : {
          workspace: "Topic Workspace",
          title: "Research Topic Copilot",
          banner:
            "Start from a research interest and inspect framing, evidence, candidate topics, and convergence support.",
          formTitle: "Exploration Input",
          formCopy: "Use a small structured form to drive the Topic Agent MVP workflow.",
          interest: "Research Interest",
          problemDomain: "Problem Domain",
          seedIdea: "Seed Idea",
          timeBudget: "Time Budget (Months)",
          resourceLevel: "Resource Level",
          preferredStyle: "Preferred Style",
          run: "Run Topic Agent",
          refine: "Refine Current Session",
          running: "Running Topic Agent...",
          framing: "Problem Framing",
          landscape: "Research Landscape",
          evidence: "Evidence Records",
          evidenceFocus: "Focused Evidence",
          evidenceFilters: "Evidence Filters",
          all: "All",
          sourceTier: "Source Tier",
          sourceType: "Source Type",
          relevance: "Relevance",
          openSource: "Open Source",
          candidates: "Candidate Topics",
          supportingEvidence: "Supporting Evidence",
          openQuestions: "Open Questions",
          comparison: "Comparison And Convergence",
          candidateScores: "Candidate Comparison",
          rationale: "Rationale",
          dimensions: "Dimensions",
          compare: "Compare",
          sessionDiff: "Session Diff",
          currentSession: "Current Session",
          compareSession: "Compared Session",
          candidateDelta: "Candidate Delta",
          evidenceDelta: "Evidence Delta",
          noDiff: "Choose a different history record to compare convergence changes.",
          trace: "Execution Trace",
          confidence: "Confidence Summary",
          recentSessions: "Recent Sessions",
          load: "Load",
          noResult: "No Topic Agent result yet",
          noResultCopy: "Submit a research interest to view structured Topic Agent output here.",
          recommendation: "Recommended",
          backup: "Backup",
          searchQuestions: "Search Questions",
          manualChecks: "Manual Checks",
          themes: "Themes",
          methods: "Active Methods",
          gaps: "Likely Gaps",
          saturated: "Saturated Areas",
          topicCount: "topics",
        };

  const resolveAssessmentTitle = (assessment: TopicAgentComparisonAssessment) =>
    candidateTitleById.get(assessment.candidate_id) ?? assessment.candidate_id;

  const resolveCandidateLabel = (candidateId?: string | null) =>
    (candidateId ? candidateTitleById.get(candidateId) : null) ?? candidateId ?? "-";

  const currentCandidateTitles = new Set((topicResult?.candidate_topics ?? []).map((item) => item.title));
  const comparisonCandidateTitles = new Set(
    (topicComparisonResult?.candidate_topics ?? []).map((item) => item.title),
  );
  const addedCandidateTitles = [...currentCandidateTitles].filter(
    (title) => !comparisonCandidateTitles.has(title),
  );
  const removedCandidateTitles = [...comparisonCandidateTitles].filter(
    (title) => !currentCandidateTitles.has(title),
  );

  const handleFocusEvidence = (record: TopicAgentSourceRecord) => {
    setFocusedEvidenceId(record.source_id);
  };

  return (
    <section className="panel-grid">
      <article className="panel panel-span view-banner">
        <div className="view-banner-content">
          <div>
            <span className="section-label">{copy.workspace}</span>
            <h2 className="view-banner-title">{copy.title}</h2>
            <p className="view-banner-copy">{copy.banner}</p>
          </div>
        </div>
      </article>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <h2>{copy.formTitle}</h2>
            <p className="panel-intro">{copy.formCopy}</p>
          </div>
        </div>
        <form className="stack-form" onSubmit={onSubmit}>
          <label>
            <span>{copy.interest}</span>
            <input value={interest} onChange={(event) => onChangeInterest(event.target.value)} />
          </label>
          <label>
            <span>{copy.problemDomain}</span>
            <input
              value={problemDomain}
              onChange={(event) => onChangeProblemDomain(event.target.value)}
            />
          </label>
          <label>
            <span>{copy.seedIdea}</span>
            <textarea value={seedIdea} onChange={(event) => onChangeSeedIdea(event.target.value)} />
          </label>
          <label>
            <span>{copy.timeBudget}</span>
            <input
              value={timeBudgetMonths}
              inputMode="numeric"
              onChange={(event) => onChangeTimeBudgetMonths(event.target.value)}
            />
          </label>
          <label>
            <span>{copy.resourceLevel}</span>
            <input
              value={resourceLevel}
              onChange={(event) => onChangeResourceLevel(event.target.value)}
            />
          </label>
          <label>
            <span>{copy.preferredStyle}</span>
            <input
              value={preferredStyle}
              onChange={(event) => onChangePreferredStyle(event.target.value)}
            />
          </label>
          <div className="button-row">
            <button type="submit" className="primary-button" disabled={topicBusy}>
              {topicBusy ? copy.running : copy.run}
            </button>
            <button
              type="button"
              className="secondary-button"
              disabled={topicBusy || !topicResult}
              onClick={onRefine}
            >
              {copy.refine}
            </button>
          </div>
        </form>
        {topicError && <p className="error">{topicError}</p>}
      </article>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <h2>{copy.recentSessions}</h2>
            <p className="panel-intro">{topicSessions.length} sessions</p>
          </div>
        </div>
        {topicSessions.length === 0 ? (
          <div className="empty-state">
            <strong>{copy.noResult}</strong>
            <p>{copy.noResultCopy}</p>
          </div>
        ) : (
          <div className="trace-list">
            {topicSessions.map((session) => (
              <article key={session.session_id} className="trace-card">
                <div className="trace-meta-row">
                  <strong>{session.interest}</strong>
                  <span className="status-chip">
                    {session.candidate_count} {copy.topicCount}
                  </span>
                </div>
                <p className="trace-detail">
                  {resolveCandidateLabel(session.recommended_candidate_id)}
                </p>
                <div className="button-row">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => onLoadSession(session.session_id)}
                  >
                    {copy.load}
                  </button>
                  {topicResult && session.session_id !== topicResult.session_id && (
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={() => onCompareSession(session.session_id)}
                    >
                      {copy.compare}
                    </button>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </article>

      <article className="panel preview-panel">
        <div className="panel-heading">
          <div>
            <h2>{copy.framing}</h2>
            <p className="panel-intro">
              {topicResult ? topicResult.framing_result.normalized_topic : copy.noResult}
            </p>
          </div>
        </div>
        {!topicResult ? (
          <div className="empty-state">
            <strong>{copy.noResult}</strong>
            <p>{copy.noResultCopy}</p>
          </div>
        ) : (
          <div className="result-stack">
            <article className="subsection-card">
              <span className="trace-label">{copy.searchQuestions}</span>
              <div className="list-block">
                {topicResult.framing_result.search_questions.map((question) => (
                  <p key={question}>{question}</p>
                ))}
              </div>
            </article>
            <article className="subsection-card">
              <span className="trace-label">{copy.manualChecks}</span>
              <div className="pill-strip">
                {Object.entries(topicResult.framing_result.extracted_constraints).map(
                  ([key, value]) => (
                    <span key={key} className="meta-pill muted-pill">
                      {key}: {value}
                    </span>
                  ),
                )}
              </div>
            </article>
          </div>
        )}
      </article>

      {topicResult && (
        <>
          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.sessionDiff}</h2>
                <p className="panel-intro">
                  {topicComparisonResult ? topicComparisonResult.user_input.interest : copy.noDiff}
                </p>
              </div>
            </div>
            {!topicComparisonResult ? (
              <div className="empty-state">
                <strong>{copy.sessionDiff}</strong>
                <p>{copy.noDiff}</p>
              </div>
            ) : (
              <div className="result-stack">
                <div className="summary-strip">
                  <div className="summary-card summary-card-emphasis">
                    <span>{copy.currentSession}</span>
                    <strong>
                      {resolveCandidateLabel(topicResult.convergence_result.recommended_candidate_id)}
                    </strong>
                  </div>
                  <div className="summary-card">
                    <span>{copy.compareSession}</span>
                    <strong>
                      {topicComparisonResult.candidate_topics.find(
                        (item) =>
                          item.candidate_id ===
                          topicComparisonResult.convergence_result.recommended_candidate_id,
                      )?.title ??
                        topicComparisonResult.convergence_result.recommended_candidate_id}
                    </strong>
                  </div>
                  <div className="summary-card">
                    <span>{copy.evidenceDelta}</span>
                    <strong>
                      {topicResult.evidence_records.length} vs{" "}
                      {topicComparisonResult.evidence_records.length}
                    </strong>
                  </div>
                </div>
                <article className="subsection-card">
                  <span className="trace-label">{copy.candidateDelta}</span>
                  <div className="comparison-diff-grid">
                    <div className="comparison-diff-card">
                      <span className="trace-label">Added In Current</span>
                      <div className="list-block">
                        {(addedCandidateTitles.length > 0 ? addedCandidateTitles : ["No new candidates"]).map(
                          (title) => (
                            <p key={title}>{title}</p>
                          ),
                        )}
                      </div>
                    </div>
                    <div className="comparison-diff-card">
                      <span className="trace-label">Only In Compared</span>
                      <div className="list-block">
                        {(removedCandidateTitles.length > 0 ? removedCandidateTitles : ["No removed candidates"]).map(
                          (title) => (
                            <p key={title}>{title}</p>
                          ),
                        )}
                      </div>
                    </div>
                  </div>
                </article>
                <div className="comparison-diff-grid">
                  <article className="subsection-card">
                    <span className="trace-label">{copy.rationale}</span>
                    <p className="subsection-copy">{topicResult.convergence_result.rationale}</p>
                  </article>
                  <article className="subsection-card">
                    <span className="trace-label">{copy.compareSession}</span>
                    <p className="subsection-copy">
                      {topicComparisonResult.convergence_result.rationale}
                    </p>
                  </article>
                </div>
              </div>
            )}
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.landscape}</h2>
                <p className="panel-intro">
                  {topicResult.landscape_summary.themes.length} {copy.themes.toLowerCase()}
                </p>
              </div>
            </div>
            <div className="result-stack">
              <article className="subsection-card">
                <span className="trace-label">{copy.themes}</span>
                <div className="list-block">
                  {topicResult.landscape_summary.themes.map((item) => (
                    <p key={item}>{item}</p>
                  ))}
                </div>
              </article>
              <article className="subsection-card">
                <span className="trace-label">{copy.methods}</span>
                <div className="pill-strip">
                  {topicResult.landscape_summary.active_methods.map((item) => (
                    <span key={item} className="meta-pill">
                      {item}
                    </span>
                  ))}
                </div>
              </article>
              <article className="subsection-card">
                <span className="trace-label">{copy.gaps}</span>
                <div className="list-block">
                  {topicResult.landscape_summary.likely_gaps.map((item) => (
                    <p key={item}>{item}</p>
                  ))}
                </div>
              </article>
              <article className="subsection-card">
                <span className="trace-label">{copy.saturated}</span>
                <div className="list-block">
                  {topicResult.landscape_summary.saturated_areas.map((item) => (
                    <p key={item}>{item}</p>
                  ))}
                </div>
              </article>
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.evidence}</h2>
                <p className="panel-intro">
                  {filteredEvidenceRecords.length} / {topicResult.evidence_records.length} records
                </p>
              </div>
            </div>
            <div className="result-stack">
              <article className="subsection-card">
                <span className="trace-label">{copy.evidenceFilters}</span>
                <div className="filter-row">
                  <button
                    type="button"
                    className={`filter-chip${evidenceTierFilter === "all" ? " active" : ""}`}
                    onClick={() => setEvidenceTierFilter("all")}
                  >
                    {copy.sourceTier}: {copy.all}
                  </button>
                  {evidenceTierOptions.map((tier) => (
                    <button
                      key={tier}
                      type="button"
                      className={`filter-chip${evidenceTierFilter === tier ? " active" : ""}`}
                      onClick={() => setEvidenceTierFilter(tier)}
                    >
                      {copy.sourceTier}: {tier}
                    </button>
                  ))}
                </div>
                <div className="filter-row">
                  <button
                    type="button"
                    className={`filter-chip${evidenceTypeFilter === "all" ? " active" : ""}`}
                    onClick={() => setEvidenceTypeFilter("all")}
                  >
                    {copy.sourceType}: {copy.all}
                  </button>
                  {evidenceTypeOptions.map((type) => (
                    <button
                      key={type}
                      type="button"
                      className={`filter-chip${evidenceTypeFilter === type ? " active" : ""}`}
                      onClick={() => setEvidenceTypeFilter(type)}
                    >
                      {copy.sourceType}: {type}
                    </button>
                  ))}
                </div>
              </article>
              <div className="trace-list">
                {filteredEvidenceRecords.map((record) => (
                  <article key={record.source_id} className="trace-card">
                    <div className="trace-meta-row">
                      <strong>{record.title}</strong>
                      <span className="status-chip">{record.source_tier}</span>
                    </div>
                    <p className="trace-detail">
                      {record.source_type} | {record.year} | {record.authors_or_publisher}
                    </p>
                    <p className="trace-detail">{record.summary}</p>
                    <p className="trace-detail">
                      {copy.relevance}: {record.relevance_reason}
                    </p>
                    <div className="button-row">
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => handleFocusEvidence(record)}
                      >
                        {copy.evidenceFocus}
                      </button>
                      <a
                        className="inline-link-button"
                        href={record.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {copy.openSource}
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.evidenceFocus}</h2>
                <p className="panel-intro">
                  {focusedEvidence ? focusedEvidence.source_id : copy.noResult}
                </p>
              </div>
            </div>
            {focusedEvidence ? (
              <div className="result-stack">
                <article className="subsection-card">
                  <div className="trace-meta-row">
                    <strong>{focusedEvidence.title}</strong>
                    <span className="status-chip">
                      {focusedEvidence.source_tier} / {focusedEvidence.source_type}
                    </span>
                  </div>
                  <p className="trace-detail">
                    {focusedEvidence.year} | {focusedEvidence.authors_or_publisher}
                  </p>
                  <p className="trace-detail">{focusedEvidence.summary}</p>
                  <p className="trace-detail">
                    {copy.relevance}: {focusedEvidence.relevance_reason}
                  </p>
                  <p className="trace-detail">{focusedEvidence.identifier}</p>
                  <a
                    className="inline-link-button"
                    href={focusedEvidence.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {copy.openSource}
                  </a>
                </article>
              </div>
            ) : (
              <div className="empty-state">
                <strong>{copy.noResult}</strong>
                <p>{copy.noResultCopy}</p>
              </div>
            )}
          </article>

          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.candidates}</h2>
                <p className="panel-intro">{topicResult.candidate_topics.length} candidates</p>
              </div>
            </div>
            <div className="trace-list candidate-grid">
              {topicResult.candidate_topics.map((candidate) => (
                <article key={candidate.candidate_id} className="trace-card">
                  <div className="trace-meta-row">
                    <strong>{candidate.title}</strong>
                    <span className="status-chip">{candidate.positioning}</span>
                  </div>
                  <p className="trace-detail">{candidate.research_question}</p>
                  <div className="pill-strip">
                    <span className="meta-pill">{candidate.novelty_note}</span>
                    <span className="meta-pill muted-pill">{candidate.feasibility_note}</span>
                    <span className="meta-pill muted-pill">{candidate.risk_note}</span>
                  </div>
                  <span className="trace-label">{copy.supportingEvidence}</span>
                  <div className="list-block">
                    {candidate.supporting_source_ids.map((sourceId) => (
                      <p key={`${candidate.candidate_id}-${sourceId}`}>
                        <button
                          type="button"
                          className="inline-link-button"
                          onClick={() => setFocusedEvidenceId(sourceId)}
                        >
                          {sourceId}: {evidenceTitleById.get(sourceId) ?? sourceId}
                        </button>
                      </p>
                    ))}
                  </div>
                  <span className="trace-label">{copy.openQuestions}</span>
                  <div className="list-block">
                    {candidate.open_questions.map((question) => (
                      <p key={question}>{question}</p>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </article>

          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.comparison}</h2>
                <p className="panel-intro">{topicResult.comparison_result.summary}</p>
              </div>
            </div>
            <div className="summary-strip">
              <div className="summary-card summary-card-emphasis">
                <span>{copy.recommendation}</span>
                <strong>
                  {resolveCandidateLabel(topicResult.convergence_result.recommended_candidate_id)}
                </strong>
              </div>
              <div className="summary-card">
                <span>{copy.backup}</span>
                <strong>
                  {resolveCandidateLabel(topicResult.convergence_result.backup_candidate_id)}
                </strong>
              </div>
              <div className="summary-card">
                <span>{copy.confidence}</span>
                <strong>{topicResult.confidence_summary.candidate_separation}</strong>
              </div>
            </div>
            <article className="subsection-card">
              <span className="trace-label">{copy.rationale}</span>
              <p className="subsection-copy">{topicResult.convergence_result.rationale}</p>
            </article>
            <article className="subsection-card">
              <span className="trace-label">{copy.dimensions}</span>
              <div className="pill-strip">
                {topicResult.comparison_result.dimensions.map((dimension) => (
                  <span key={dimension} className="meta-pill">
                    {dimension}
                  </span>
                ))}
              </div>
            </article>
            <article className="subsection-card">
              <span className="trace-label">{copy.manualChecks}</span>
              <div className="list-block">
                {topicResult.convergence_result.manual_checks.map((check) => (
                  <p key={check}>{check}</p>
                ))}
              </div>
            </article>
            <div className="panel-heading">
              <div>
                <h2>{copy.candidateScores}</h2>
                <p className="panel-intro">
                  {topicResult.comparison_result.candidate_assessments.length} assessments
                </p>
              </div>
            </div>
            <div className="trace-list candidate-grid">
              {topicResult.comparison_result.candidate_assessments.map((assessment) => (
                <article key={assessment.candidate_id} className="trace-card comparison-card">
                  <div className="trace-meta-row">
                    <strong>{resolveAssessmentTitle(assessment)}</strong>
                    <span className="status-chip">{assessment.novelty}</span>
                  </div>
                  <div className="comparison-metric-grid">
                    <div className="comparison-metric">
                      <span className="trace-label">Novelty</span>
                      <strong>{assessment.novelty}</strong>
                    </div>
                    <div className="comparison-metric">
                      <span className="trace-label">Feasibility</span>
                      <strong>{assessment.feasibility}</strong>
                    </div>
                    <div className="comparison-metric">
                      <span className="trace-label">Evidence</span>
                      <strong>{assessment.evidence_strength}</strong>
                    </div>
                    <div className="comparison-metric">
                      <span className="trace-label">Data</span>
                      <strong>{assessment.data_availability}</strong>
                    </div>
                    <div className="comparison-metric">
                      <span className="trace-label">Cost</span>
                      <strong>{assessment.implementation_cost}</strong>
                    </div>
                    <div className="comparison-metric">
                      <span className="trace-label">Risk</span>
                      <strong>{assessment.risk}</strong>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.trace}</h2>
                <p className="panel-intro">{topicResult.trace.length} stages</p>
              </div>
            </div>
            <div className="trace-list">
              {topicResult.trace.map((event) => (
                <article key={`${event.stage}-${event.timestamp}`} className="trace-card">
                  <div className="trace-meta-row">
                    <span className="trace-label">{event.stage}</span>
                    <span className="status-chip success">{event.status}</span>
                  </div>
                  <p className="trace-detail">{event.detail}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.confidence}</h2>
                <p className="panel-intro">
                  {topicResult.confidence_summary.evidence_coverage} /{" "}
                  {topicResult.confidence_summary.source_quality}
                </p>
              </div>
            </div>
            <div className="trace-list">
              {topicResult.confidence_summary.rationale.map((reason) => (
                <article key={reason} className="trace-card">
                  <p className="trace-detail">{reason}</p>
                </article>
              ))}
            </div>
          </article>
        </>
      )}
    </section>
  );
}
