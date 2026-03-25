import type { FormEvent } from "react";

import type { Locale, TopicAgentSessionResponse, TopicAgentSessionSummary } from "../types";

type TopicWorkspaceProps = {
  locale: Locale;
  interest: string;
  problemDomain: string;
  seedIdea: string;
  timeBudgetMonths: string;
  resourceLevel: string;
  preferredStyle: string;
  topicResult: TopicAgentSessionResponse | null;
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
};

export function TopicWorkspace({
  locale,
  interest,
  problemDomain,
  seedIdea,
  timeBudgetMonths,
  resourceLevel,
  preferredStyle,
  topicResult,
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
}: TopicWorkspaceProps) {
  const copy =
    locale === "zh"
      ? {
          workspace: "选题工作台",
          title: "科研选题副驾",
          banner: "从研究兴趣出发，查看问题 framing、证据记录、候选选题和收敛建议。",
          formTitle: "探索输入",
          formCopy: "先用一个很小的结构化表单驱动 Topic Agent MVP 工作流。",
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
          evidence: "证据记录",
          candidates: "候选选题",
          comparison: "比较与收敛",
          trace: "执行轨迹",
          confidence: "可信度摘要",
          recentSessions: "最近探索记录",
          load: "加载",
          noResult: "还没有 Topic Agent 结果",
          noResultCopy: "填写研究兴趣并运行后，这里会展示结构化结果。",
          recommendation: "推荐方向",
          backup: "备选方向",
          searchQuestions: "检索子问题",
          manualChecks: "人工确认",
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
          evidence: "Evidence Records",
          candidates: "Candidate Topics",
          comparison: "Comparison And Convergence",
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
                  <span className="status-chip">{session.candidate_count} topics</span>
                </div>
                <p className="trace-detail">{session.recommended_candidate_id ?? "-"}</p>
                <div className="button-row">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => onLoadSession(session.session_id)}
                  >
                    {copy.load}
                  </button>
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
          <div className="trace-list">
            {topicResult.framing_result.search_questions.map((question) => (
              <article key={question} className="trace-card">
                <span className="trace-label">{copy.searchQuestions}</span>
                <p className="trace-detail">{question}</p>
              </article>
            ))}
          </div>
        )}
      </article>

      {topicResult && (
        <>
          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.evidence}</h2>
                <p className="panel-intro">{topicResult.evidence_records.length} records</p>
              </div>
            </div>
            <div className="trace-list">
              {topicResult.evidence_records.map((record) => (
                <article key={record.source_id} className="trace-card">
                  <div className="trace-meta-row">
                    <strong>{record.title}</strong>
                    <span className="status-chip">{record.source_tier}</span>
                  </div>
                  <p className="trace-detail">{record.summary}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.candidates}</h2>
                <p className="panel-intro">{topicResult.candidate_topics.length} candidates</p>
              </div>
            </div>
            <div className="trace-list">
              {topicResult.candidate_topics.map((candidate) => (
                <article key={candidate.candidate_id} className="trace-card">
                  <div className="trace-meta-row">
                    <strong>{candidate.title}</strong>
                    <span className="status-chip">{candidate.positioning}</span>
                  </div>
                  <p className="trace-detail">{candidate.research_question}</p>
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
              <div className="summary-card">
                <span>{copy.recommendation}</span>
                <strong>{topicResult.convergence_result.recommended_candidate_id}</strong>
              </div>
              <div className="summary-card">
                <span>{copy.backup}</span>
                <strong>{topicResult.convergence_result.backup_candidate_id ?? "-"}</strong>
              </div>
              <div className="summary-card">
                <span>{copy.confidence}</span>
                <strong>{topicResult.confidence_summary.candidate_separation}</strong>
              </div>
            </div>
            <div className="trace-list">
              {topicResult.convergence_result.manual_checks.map((check) => (
                <article key={check} className="trace-card">
                  <span className="trace-label">{copy.manualChecks}</span>
                  <p className="trace-detail">{check}</p>
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
