import { useState, type FormEvent, type ReactNode } from "react";

import type {
  Locale,
  TopicAgentComparisonAssessment,
  TopicAgentSessionResponse,
  TopicAgentSessionSummary,
} from "../types";
import { TopicAgentCandidatesPanel } from "../features/topic-agent/components/TopicAgentCandidatesPanel";
import { TopicAgentEvidencePanel } from "../features/topic-agent/components/TopicAgentEvidencePanel";
import { TopicAgentFramingPanel } from "../features/topic-agent/components/TopicAgentFramingPanel";
import { TopicAgentInputPanel } from "../features/topic-agent/components/TopicAgentInputPanel";
import { TopicAgentRecommendationSummary } from "../features/topic-agent/components/TopicAgentRecommendationSummary";
import { TopicAgentSessionDiffPanel } from "../features/topic-agent/components/TopicAgentSessionDiffPanel";
import { TopicAgentSessionHistory } from "../features/topic-agent/components/TopicAgentSessionHistory";
import { TopicAgentTrustPanel } from "../features/topic-agent/components/TopicAgentTrustPanel";

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

type TopicSectionShellProps = {
  label: string;
  title: string;
  description: string;
  emphasis?: boolean;
  children: ReactNode;
};

function TopicSectionShell({
  label,
  title,
  description,
  emphasis = false,
  children,
}: TopicSectionShellProps) {
  return (
    <section className={`topic-section-shell panel-span${emphasis ? " topic-section-shell-emphasis" : ""}`}>
      <div className={`topic-section-heading${emphasis ? " topic-section-heading-emphasis" : ""}`}>
        <span className="section-label">{label}</span>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      <div className="topic-section-content">{children}</div>
    </section>
  );
}

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

  const legacyCopy: Record<string, string> =
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

  const copy: Record<string, string> =
    locale === "zh"
      ? {
          workspace: "选题工作台",
          title: "科研选题副驾",
          banner: "从研究兴趣出发，查看问题 framing、证据、候选方向、比较结果与收敛建议。",
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
          landscape: "研究全景",
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
          compare: "比较",
          sessionDiff: "会话对比",
          currentSession: "当前会话",
          compareSession: "对比会话",
          candidateDelta: "候选差异",
          evidenceDelta: "证据差异",
          noDiff: "选择一条不同的历史记录来比较收敛变化。",
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
          themes: "主题",
          methods: "活跃方法",
          gaps: "可能空白",
          saturated: "相对饱和",
          topicCount: "个候选",
          sessions: "条记录",
          candidateUnit: "个候选",
          assessments: "个评估",
          records: "条记录",
          stages: "个阶段",
          addedInCurrent: "当前新增",
          onlyInCompared: "仅在对比会话中",
          noNewCandidates: "没有新增候选",
          noRemovedCandidates: "没有移除候选",
          novelty: "新颖性",
          feasibility: "可行性",
          evidenceStrength: "证据强度",
          dataAvailability: "数据可得性",
          implementationCost: "实现成本",
          risk: "风险",
        }
      : {
          ...legacyCopy,
          sessions: "sessions",
          candidateUnit: "candidates",
          assessments: "assessments",
          records: "records",
          stages: "stages",
          addedInCurrent: "Added In Current",
          onlyInCompared: "Only In Compared",
          noNewCandidates: "No new candidates",
          noRemovedCandidates: "No removed candidates",
          novelty: "Novelty",
          feasibility: "Feasibility",
          evidenceStrength: "Evidence",
          dataAvailability: "Data",
          implementationCost: "Cost",
          risk: "Risk",
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

      <TopicAgentInputPanel
        copy={copy}
        interest={interest}
        problemDomain={problemDomain}
        seedIdea={seedIdea}
        timeBudgetMonths={timeBudgetMonths}
        resourceLevel={resourceLevel}
        preferredStyle={preferredStyle}
        topicBusy={topicBusy}
        topicError={topicError}
        hasTopicResult={Boolean(topicResult)}
        onChangeInterest={onChangeInterest}
        onChangeProblemDomain={onChangeProblemDomain}
        onChangeSeedIdea={onChangeSeedIdea}
        onChangeTimeBudgetMonths={onChangeTimeBudgetMonths}
        onChangeResourceLevel={onChangeResourceLevel}
        onChangePreferredStyle={onChangePreferredStyle}
        onSubmit={onSubmit}
        onRefine={onRefine}
      />

      <TopicAgentSessionHistory
        copy={copy}
        locale={locale}
        topicSessions={topicSessions}
        currentSessionId={topicResult?.session_id}
        resolveCandidateLabel={resolveCandidateLabel}
        onLoadSession={onLoadSession}
        onCompareSession={onCompareSession}
      />

      <div className="topic-section-heading panel-span">
        <span className="section-label">
          {locale === "zh" ? "输入与 framing" : "Input And Framing"}
        </span>
        <h3>{locale === "zh" ? "先定义问题，再进入方向判断" : "Define The Problem Before Judging Directions"}</h3>
        <p>
          {locale === "zh"
            ? "先确认研究兴趣、约束条件和问题 framing 是否合理，这决定后续 evidence 和推荐是否可信。"
            : "Confirm the research interest, constraints, and framing first because they shape the evidence bundle and recommendation quality."}
        </p>
      </div>
      <TopicAgentFramingPanel copy={copy} topicResult={topicResult} />

      {topicResult && (
        <>
          <div className="topic-section-heading panel-span topic-section-heading-emphasis">
            <span className="section-label">
              {locale === "zh" ? "推荐与比较" : "Recommendation And Comparison"}
            </span>
            <h3>{locale === "zh" ? "先看系统建议，再看为何这样建议" : "Read The Recommendation First, Then The Why"}</h3>
            <p>
              {locale === "zh"
                ? "这一部分应该最快回答：系统推荐哪条方向、备选是什么、依据是什么、和上一轮相比变化了什么。"
                : "This section should answer the core demo question fastest: what the system recommends, the backup option, the reasoning, and what changed from a previous run."}
            </p>
          </div>
          <TopicAgentRecommendationSummary
            topicResult={topicResult}
            copy={copy}
            resolveCandidateLabel={resolveCandidateLabel}
            resolveAssessmentTitle={resolveAssessmentTitle}
          />

          <TopicAgentSessionDiffPanel
            copy={copy}
            topicResult={topicResult}
            topicComparisonResult={topicComparisonResult}
            addedCandidateTitles={addedCandidateTitles}
            removedCandidateTitles={removedCandidateTitles}
            resolveCandidateLabel={resolveCandidateLabel}
          />

          <div className="topic-section-heading panel-span">
            <span className="section-label">
              {locale === "zh" ? "候选与证据" : "Candidates And Evidence"}
            </span>
            <h3>{locale === "zh" ? "把候选方向和真实支持来源放在一起读" : "Read Candidate Directions Alongside Their Real Support"}</h3>
            <p>
              {locale === "zh"
                ? "先看候选方向，再展开对应 evidence，判断这些 support 是否真的贴题，而不是只停留在 top benchmark。"
                : "Review candidate directions alongside the evidence list so you can judge whether the support is genuinely topic-specific instead of just coming from the top-ranked benchmark."}
            </p>
          </div>
          <TopicAgentEvidencePanel
            locale={locale}
            copy={copy}
            filteredEvidenceRecords={filteredEvidenceRecords}
            totalEvidenceCount={topicResult.evidence_records.length}
            evidenceTierFilter={evidenceTierFilter}
            evidenceTypeFilter={evidenceTypeFilter}
            evidenceTierOptions={evidenceTierOptions}
            evidenceTypeOptions={evidenceTypeOptions}
            focusedEvidence={focusedEvidence}
            onSetEvidenceTierFilter={setEvidenceTierFilter}
            onSetEvidenceTypeFilter={setEvidenceTypeFilter}
            onFocusEvidence={(record) => setFocusedEvidenceId(record.source_id)}
          />

          <TopicAgentCandidatesPanel
            copy={copy}
            candidates={topicResult.candidate_topics}
            evidenceTitleById={evidenceTitleById}
            onFocusSourceId={setFocusedEvidenceId}
          />

          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.landscape}</h2>
                <p className="panel-intro">
                  {topicResult.landscape_summary.themes.length}{" "}
                  {locale === "zh" ? copy.themes : copy.themes.toLowerCase()}
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

          <div className="topic-section-heading panel-span">
            <span className="section-label">
              {locale === "zh" ? "信任与诊断" : "Trust And Diagnostics"}
            </span>
            <h3>{locale === "zh" ? "最后展示可追溯性、不确定性和人工确认点" : "Close With Traceability, Uncertainty, And Human Checks"}</h3>
            <p>
              {locale === "zh"
                ? "最后一层不是再给更多内容，而是解释哪些结论是事实、哪些是系统综合、哪些仍然需要人工确认。"
                : "The final layer is not about adding more content. It explains which claims are facts, which are system syntheses, and which still require human validation."}
            </p>
          </div>
          <TopicAgentTrustPanel
            topicResult={topicResult}
            copy={copy}
            locale={locale}
            evidenceTitleById={evidenceTitleById}
          />
        </>
      )}
    </section>
  );
}
