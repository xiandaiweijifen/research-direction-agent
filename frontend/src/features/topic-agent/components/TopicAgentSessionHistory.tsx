import type { TopicAgentSessionSummary } from "../../../types";

type TopicAgentSessionHistoryProps = {
  copy: Record<string, string>;
  topicSessions: TopicAgentSessionSummary[];
  currentSessionId?: string | null;
  resolveCandidateLabel: (candidateId?: string | null) => string;
  onLoadSession: (sessionId: string) => void;
  onCompareSession: (sessionId: string) => void;
};

export function TopicAgentSessionHistory({
  copy,
  topicSessions,
  currentSessionId,
  resolveCandidateLabel,
  onLoadSession,
  onCompareSession,
}: TopicAgentSessionHistoryProps) {
  return (
    <article className="panel">
      <div className="panel-heading">
        <div>
          <h2>{copy.recentSessions}</h2>
          <p className="panel-intro">
            {topicSessions.length} {copy.sessions}
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
          {topicSessions.map((session) => (
            <article key={session.session_id} className="trace-card">
              <div className="trace-meta-row">
                <strong>{session.interest}</strong>
                <span className="status-chip">
                  {session.candidate_count} {copy.topicCount}
                </span>
              </div>
              <p className="trace-detail">{resolveCandidateLabel(session.recommended_candidate_id)}</p>
              <div className="button-row">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => onLoadSession(session.session_id)}
                >
                  {copy.load}
                </button>
                {currentSessionId && session.session_id !== currentSessionId && (
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
  );
}
