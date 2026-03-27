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
  const evidenceTitleById = new Map(
    (topicResult?.evidence_records ?? []).map((record) => [record.source_id, record.title]),
  );
  const copy =
    locale === "zh"
      ? {
          workspace: "选题工作台",
          title: "科研选题副驾",
          banner: "从研究兴趣出发，查看问题定义、证据记录、候选方向与收敛建议。",
          formTitle: "探索输入",
          formCopy: "用一组紧凑的结构化输入启动一次选题探索。",
          interest: "研究兴趣",
          problemDomain: "问题领域",
          seedIdea: "初步想法",
          timeBudget: "时间预算（月）",
          resourceLevel: "资源水平",
          preferredStyle: "偏好风格",
          run: "运行 Topic Agent",
          refine: "基于当前结果收敛",
          running: "正在运行 Topic Agent...",
          framing: "问题定义",
          evidence: "证据记录",
          candidates: "候选方向",
          supportingEvidence: "支撑证据",
          comparison: "比较与收敛",
          candidateScores: "候选比较",
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
        }
      : {
          workspace: "Topic Workspace",
          title: "Research Topic Copilot",
          banner:
            "Start from a research interest and inspect framing, evidence, candidate topics, and convergence support.",
          formTitle: "Exploration Input",
          formCopy: "Use a compact structured form to run a topic exploration pass.",
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
          supportingEvidence: "Supporting Evidence",
          comparison: "Recommendation And Comparison",
          candidateScores: "Candidate Comparison",
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
            <p className="panel-intro">
              {topicSessions.length} {copy.recentSessions.toLowerCase?.() ?? copy.recentSessions}
            </p>
          </div>
        </div>
        {topicSessions.length === 0 ? (
          <div className="empty-state">
            <strong>{copy.noResult}</strong>
            <p>{copy.noResultCopy}</p>
          </div>
        ) : (
          <div className="trace-list">
            {topicSessions.slice(0, 4).map((session) => (
              <article key={session.session_id} className="trace-card">
                <div className="trace-meta-row">
                  <strong>{session.interest}</strong>
                  <button
                    type="button"
                    className="ghost-button"
                    onClick={() => onLoadSession(session.session_id)}
                  >
                    {copy.load}
                  </button>
                </div>
                <p className="trace-detail">
                  {session.problem_domain || session.recommended_candidate_id || session.session_id}
                </p>
              </article>
            ))}
          </div>
        )}
      </article>

      {!topicResult ? (
        <article className="panel panel-span empty-state">
          <strong>{copy.noResult}</strong>
          <p>{copy.noResultCopy}</p>
        </article>
      ) : (
        <>
          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>{copy.framing}</h2>
                <p className="panel-intro">{topicResult.framing_result.normalized_topic}</p>
              </div>
            </div>
            <article className="subsection-card">
              <span className="trace-label">{copy.searchQuestions}</span>
              <div className="list-block">
                {topicResult.framing_result.search_questions.map((question) => (
                  <p key={question}>{question}</p>
                ))}
              </div>
            </article>
          </article>

          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.evidence}</h2>
                <p className="panel-intro">
                  {topicResult.evidence_records.length} {topicResult.evidence_records.length === 1 ? "record" : "records"}
                </p>
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

          <article className="panel panel-span">
            <div className="panel-heading">
              <div>
                <h2>{copy.candidates}</h2>
                <p className="panel-intro">{topicResult.candidate_topics.length}</p>
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
                  <span className="trace-label">{copy.supportingEvidence}</span>
                  <div className="list-block">
                    {candidate.supporting_source_ids.map((sourceId) => (
                      <p key={`${candidate.candidate_id}-${sourceId}`}>
                        {evidenceTitleById.get(sourceId) ?? sourceId}
                      </p>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </article>
        </>
      )}
    </section>
  );
}
