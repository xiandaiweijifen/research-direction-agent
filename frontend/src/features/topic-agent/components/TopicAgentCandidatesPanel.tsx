import type { Locale, TopicAgentCandidateTopic } from "../../../types";
import { getTopicAgentPositioningLabel } from "../display";

type TopicAgentCandidatesPanelProps = {
  locale: Locale;
  copy: Record<string, string>;
  candidates: TopicAgentCandidateTopic[];
  evidenceTitleById: Map<string, string>;
  onFocusSourceId: (sourceId: string) => void;
};

export function TopicAgentCandidatesPanel({
  locale,
  copy,
  candidates,
  evidenceTitleById,
  onFocusSourceId,
}: TopicAgentCandidatesPanelProps) {
  return (
    <article className="panel panel-span">
      <div className="panel-heading">
        <div>
          <h2>{copy.candidates}</h2>
          <p className="panel-intro">
            {candidates.length} {copy.candidateUnit}
          </p>
        </div>
      </div>
      <div className="trace-list candidate-grid">
        {candidates.map((candidate) => (
          <article key={candidate.candidate_id} className="trace-card">
            <div className="trace-meta-row">
              <strong>{candidate.title}</strong>
              <span className="status-chip">
                {getTopicAgentPositioningLabel(candidate.positioning, locale)}
              </span>
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
                    onClick={() => onFocusSourceId(sourceId)}
                  >
                    {evidenceTitleById.get(sourceId) ?? sourceId}
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
  );
}
