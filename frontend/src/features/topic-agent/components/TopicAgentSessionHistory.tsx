import { useMemo, useState } from "react";

import type { TopicAgentSessionSummary } from "../../../types";

type TopicAgentSessionHistoryProps = {
  copy: Record<string, string>;
  locale?: "en" | "zh";
  topicSessions: TopicAgentSessionSummary[];
  currentSessionId?: string | null;
  resolveCandidateLabel: (candidateId?: string | null) => string;
  onLoadSession: (sessionId: string) => void;
  onCompareSession: (sessionId: string) => void;
};

export function TopicAgentSessionHistory({
  copy,
  locale = "en",
  topicSessions,
  currentSessionId,
  resolveCandidateLabel,
  onLoadSession,
  onCompareSession,
}: TopicAgentSessionHistoryProps) {
  const [expanded, setExpanded] = useState(false);
  const visibleSessions = useMemo(
    () => (expanded ? topicSessions : topicSessions.slice(0, 4)),
    [expanded, topicSessions],
  );
  const hiddenCount = Math.max(topicSessions.length - visibleSessions.length, 0);
  const uiCurrent = locale === "zh" ? "当前" : "Current";
  const uiUpdated = locale === "zh" ? "更新于" : "Updated";

  function formatUpdatedAt(value: string) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : "en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }

  const uiCopy =
    locale === "zh"
      ? {
          showMore: `灞曞紑鍓?${hiddenCount} 鏉¤褰?`,
          showLess: "鏀惰捣鍘嗗彶璁板綍",
        }
      : {
          showMore: `Show ${hiddenCount} more`,
          showLess: "Show less",
        };

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
          {visibleSessions.map((session) => (
            <article key={session.session_id} className="trace-card">
              <div className="trace-meta-row">
                <strong>{session.interest}</strong>
                <div className="pill-strip">
                  {currentSessionId === session.session_id && (
                    <span className="status-chip success">{uiCurrent}</span>
                  )}
                  <span className="status-chip">
                    {session.candidate_count} {copy.topicCount}
                  </span>
                </div>
              </div>
              <p className="trace-detail">
                {uiUpdated}: {formatUpdatedAt(session.updated_at)}
              </p>
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
          {topicSessions.length > 4 && (
            <div className="session-history-actions">
              <button
                type="button"
                className="ghost-button"
                onClick={() => setExpanded((current) => !current)}
              >
                {expanded ? uiCopy.showLess : uiCopy.showMore}
              </button>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
