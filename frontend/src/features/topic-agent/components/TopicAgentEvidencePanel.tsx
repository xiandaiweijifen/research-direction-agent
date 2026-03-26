import type { TopicAgentSourceRecord } from "../../../types";

type TopicAgentEvidencePanelProps = {
  copy: Record<string, string>;
  filteredEvidenceRecords: TopicAgentSourceRecord[];
  totalEvidenceCount: number;
  evidenceTierFilter: string;
  evidenceTypeFilter: string;
  evidenceTierOptions: string[];
  evidenceTypeOptions: string[];
  focusedEvidence: TopicAgentSourceRecord | null;
  onSetEvidenceTierFilter: (value: string) => void;
  onSetEvidenceTypeFilter: (value: string) => void;
  onFocusEvidence: (record: TopicAgentSourceRecord) => void;
};

export function TopicAgentEvidencePanel({
  copy,
  filteredEvidenceRecords,
  totalEvidenceCount,
  evidenceTierFilter,
  evidenceTypeFilter,
  evidenceTierOptions,
  evidenceTypeOptions,
  focusedEvidence,
  onSetEvidenceTierFilter,
  onSetEvidenceTypeFilter,
  onFocusEvidence,
}: TopicAgentEvidencePanelProps) {
  return (
    <>
      <article className="panel">
        <div className="panel-heading">
          <div>
            <h2>{copy.evidence}</h2>
            <p className="panel-intro">
              {filteredEvidenceRecords.length} / {totalEvidenceCount} {copy.records}
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
                onClick={() => onSetEvidenceTierFilter("all")}
              >
                {copy.sourceTier}: {copy.all}
              </button>
              {evidenceTierOptions.map((tier) => (
                <button
                  key={tier}
                  type="button"
                  className={`filter-chip${evidenceTierFilter === tier ? " active" : ""}`}
                  onClick={() => onSetEvidenceTierFilter(tier)}
                >
                  {copy.sourceTier}: {tier}
                </button>
              ))}
            </div>
            <div className="filter-row">
              <button
                type="button"
                className={`filter-chip${evidenceTypeFilter === "all" ? " active" : ""}`}
                onClick={() => onSetEvidenceTypeFilter("all")}
              >
                {copy.sourceType}: {copy.all}
              </button>
              {evidenceTypeOptions.map((type) => (
                <button
                  key={type}
                  type="button"
                  className={`filter-chip${evidenceTypeFilter === type ? " active" : ""}`}
                  onClick={() => onSetEvidenceTypeFilter(type)}
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
                    onClick={() => onFocusEvidence(record)}
                  >
                    {copy.evidenceFocus}
                  </button>
                  <a className="inline-link-button" href={record.url} target="_blank" rel="noreferrer">
                    {copy.openSource}
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>
      </article>

      <article className="panel panel-span">
        <div className="panel-heading">
          <div>
            <h2>{copy.evidenceFocus}</h2>
            <p className="panel-intro">{focusedEvidence ? focusedEvidence.source_id : copy.noResult}</p>
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
              <a className="inline-link-button" href={focusedEvidence.url} target="_blank" rel="noreferrer">
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
    </>
  );
}
