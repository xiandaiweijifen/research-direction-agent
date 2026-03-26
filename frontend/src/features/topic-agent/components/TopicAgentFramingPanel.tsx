import type { TopicAgentSessionResponse } from "../../../types";

type TopicAgentFramingPanelProps = {
  copy: Record<string, string>;
  topicResult: TopicAgentSessionResponse | null;
};

export function TopicAgentFramingPanel({ copy, topicResult }: TopicAgentFramingPanelProps) {
  return (
    <article className="panel panel-span preview-panel">
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
              {Object.entries(topicResult.framing_result.extracted_constraints).map(([key, value]) => (
                <span key={key} className="meta-pill muted-pill">
                  {key}: {value}
                </span>
              ))}
            </div>
          </article>
        </div>
      )}
    </article>
  );
}
