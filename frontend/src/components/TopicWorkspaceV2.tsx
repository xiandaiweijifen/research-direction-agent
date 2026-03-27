import { useState, type FormEvent, type ReactNode } from "react";

import type {
  Locale,
  TopicAgentComparisonAssessment,
  TopicAgentSessionResponse,
  TopicAgentSessionSummary,
} from "../types";
import type { TopicAgentDemoPreset } from "../features/topic-agent/hooks/useTopicAgent";
import { TopicAgentCandidatesPanel } from "../features/topic-agent/components/TopicAgentCandidatesPanel";
import { TopicAgentEvidencePanel } from "../features/topic-agent/components/TopicAgentEvidencePanel";
import { TopicAgentFramingPanel } from "../features/topic-agent/components/TopicAgentFramingPanel";
import { TopicAgentInputPanel } from "../features/topic-agent/components/TopicAgentInputPanel";
import { TopicAgentRecommendationSummary } from "../features/topic-agent/components/TopicAgentRecommendationSummary";
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
  topicPresets: TopicAgentDemoPreset[];
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
  onApplyPreset: (presetId: string) => void;
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
    <section
      className={`topic-section-shell panel-span${emphasis ? " topic-section-shell-emphasis" : ""}`}
    >
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
  topicPresets,
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
  onApplyPreset,
}: TopicWorkspaceProps) {
  const [evidenceTierFilter, setEvidenceTierFilter] = useState("all");
  const [evidenceTypeFilter, setEvidenceTypeFilter] = useState("all");
  const [focusedEvidenceId, setFocusedEvidenceId] = useState<string | null>(null);

  void topicComparisonResult;
  void onCompareSession;

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
          banner: "从研究兴趣出发，查看问题 framing、证据、候选方向、比较结果与收敛建议。",
          formTitle: "探索输入",
          formCopy: "用一组结构化输入驱动 Topic Agent 的选题探索流程。",
          interest: "研究兴趣",
          problemDomain: "问题领域",
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
          evidenceFocus: "聚焦证据",
          evidenceFilters: "证据过滤",
          all: "全部",
          sourceTier: "来源等级",
          sourceType: "来源类型",
          relevance: "相关性",
          openSource: "打开来源",
          candidates: "候选方向",
          supportingEvidence: "支撑证据",
          openQuestions: "待确认问题",
          comparison: "比较与收敛",
          candidateScores: "候选比较",
          rationale: "推荐理由",
          dimensions: "比较维度",
          compare: "比较",
          trace: "执行轨迹",
          confidence: "可信度摘要",
          recentSessions: "最近运行记录",
          load: "加载",
          noResult: "还没有 Topic Agent 结果",
          noResultCopy: "提交研究兴趣后，这里会展示结构化的选题分析结果。",
          recommendation: "推荐方向",
          backup: "备选方向",
          searchQuestions: "搜索问题",
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
          workspace: "Topic Workspace",
          title: "Research Topic Copilot",
          banner:
            "Start from a research interest and inspect framing, evidence, candidate topics, and convergence support.",
          formTitle: "Exploration Input",
          formCopy: "Use a small structured form to drive the Topic Agent workflow.",
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
          trace: "Execution Trace",
          confidence: "Confidence Summary",
          recentSessions: "Recent Runs",
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
        locale={locale}
        copy={copy}
        topicPresets={topicPresets}
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
        onApplyPreset={onApplyPreset}
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

      <TopicSectionShell
        label={locale === "zh" ? "输入与 framing" : "Input And Framing"}
        title={locale === "zh" ? "先定义问题，再判断方向" : "Define The Problem Before Judging Directions"}
        description={
          locale === "zh"
            ? "先确认研究兴趣、约束条件和问题 framing 是否合理，因为这会直接影响后续证据与推荐质量。"
            : "Confirm the research interest, constraints, and framing first because they shape the evidence bundle and recommendation quality."
        }
      >
        <TopicAgentFramingPanel locale={locale} copy={copy} topicResult={topicResult} />
      </TopicSectionShell>

      {topicResult && (
        <>
          <TopicSectionShell
            label={locale === "zh" ? "推荐与比较" : "Recommendation And Comparison"}
            title={
              locale === "zh"
                ? "先看系统建议，再看它为什么这样建议"
                : "Read The Recommendation First, Then The Why"
            }
            description={
              locale === "zh"
                ? "这一部分要最快回答三个问题：推荐哪条方向、备选是什么、推荐依据是什么。"
                : "This section should answer the core demo question fastest: what the system recommends, the backup option, and why."
            }
            emphasis
          >
            <TopicAgentRecommendationSummary
              locale={locale}
              topicResult={topicResult}
              copy={copy}
              resolveCandidateLabel={resolveCandidateLabel}
              resolveAssessmentTitle={resolveAssessmentTitle}
            />
          </TopicSectionShell>

          <TopicSectionShell
            label={locale === "zh" ? "候选与证据" : "Candidates And Evidence"}
            title={
              locale === "zh"
                ? "把候选方向和真实支撑来源放在一起看"
                : "Read Candidate Directions Alongside Their Real Support"
            }
            description={
              locale === "zh"
                ? "先看候选方向，再展开对应 evidence，判断这些支撑是否真正贴题，而不是只来自高频文献。"
                : "Review candidate directions alongside the evidence list so you can judge whether the support is genuinely topic-specific."
            }
          >
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
              locale={locale}
              copy={copy}
              candidates={topicResult.candidate_topics}
              evidenceTitleById={evidenceTitleById}
              onFocusSourceId={setFocusedEvidenceId}
            />
          </TopicSectionShell>

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

          <TopicSectionShell
            label={locale === "zh" ? "可信度与诊断" : "Trust And Diagnostics"}
            title={
              locale === "zh"
                ? "最后展示可追溯性、不确定性和人工确认点"
                : "Close With Traceability, Uncertainty, And Human Checks"
            }
            description={
              locale === "zh"
                ? "这一层不是再给更多内容，而是解释哪些结论是事实、哪些是系统综合、哪些仍需人工确认。"
                : "The final layer explains which claims are facts, which are system syntheses, and which still require human validation."
            }
          >
            <TopicAgentTrustPanel
              topicResult={topicResult}
              copy={copy}
              locale={locale}
              evidenceTitleById={evidenceTitleById}
            />
          </TopicSectionShell>
        </>
      )}
    </section>
  );
}
