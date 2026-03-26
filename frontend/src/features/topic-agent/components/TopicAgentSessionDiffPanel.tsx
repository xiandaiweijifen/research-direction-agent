import type { TopicAgentSessionResponse } from "../../../types";

type TopicAgentSessionDiffPanelProps = {
  copy: Record<string, string>;
  topicResult: TopicAgentSessionResponse;
  topicComparisonResult: TopicAgentSessionResponse | null;
  addedCandidateTitles: string[];
  removedCandidateTitles: string[];
  resolveCandidateLabel: (candidateId?: string | null) => string;
};

export function TopicAgentSessionDiffPanel({
  copy,
  topicResult,
  topicComparisonResult,
  addedCandidateTitles,
  removedCandidateTitles,
  resolveCandidateLabel,
}: TopicAgentSessionDiffPanelProps) {
  return (
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
                    item.candidate_id === topicComparisonResult.convergence_result.recommended_candidate_id,
                )?.title ?? topicComparisonResult.convergence_result.recommended_candidate_id}
              </strong>
            </div>
            <div className="summary-card">
              <span>{copy.evidenceDelta}</span>
              <strong>
                {topicResult.evidence_records.length} vs {topicComparisonResult.evidence_records.length}
              </strong>
            </div>
          </div>
          <article className="subsection-card">
            <span className="trace-label">{copy.candidateDelta}</span>
            <div className="comparison-diff-grid">
              <div className="comparison-diff-card">
                <span className="trace-label">{copy.addedInCurrent}</span>
                <div className="list-block">
                  {(addedCandidateTitles.length > 0 ? addedCandidateTitles : [copy.noNewCandidates]).map(
                    (title) => (
                      <p key={title}>{title}</p>
                    ),
                  )}
                </div>
              </div>
              <div className="comparison-diff-card">
                <span className="trace-label">{copy.onlyInCompared}</span>
                <div className="list-block">
                  {(removedCandidateTitles.length > 0 ? removedCandidateTitles : [copy.noRemovedCandidates]).map(
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
              <p className="subsection-copy">{topicComparisonResult.convergence_result.rationale}</p>
            </article>
          </div>
        </div>
      )}
    </article>
  );
}
