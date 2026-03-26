import { useState } from "react";

import type { Locale, TopicAgentSourceRecord } from "../../../types";
import { getTopicAgentSourceTypeLabel } from "../display";

type TopicAgentEvidencePanelProps = {
  locale: Locale;
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
  locale,
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
  const [expandedEvidenceIds, setExpandedEvidenceIds] = useState<string[]>([]);

  const uiCopy =
    locale === "zh"
      ? {
          tierFilter: "按来源等级筛选",
          typeFilter: "按来源类型筛选",
          expand: "展开详情",
          collapse: "收起详情",
        }
      : {
          tierFilter: "Filter By Source Tier",
          typeFilter: "Filter By Source Type",
          expand: "Expand Details",
          collapse: "Collapse Details",
        };

  function toggleExpanded(sourceId: string) {
    setExpandedEvidenceIds((current) =>
      current.includes(sourceId)
        ? current.filter((item) => item !== sourceId)
        : [...current, sourceId],
    );
  }

  return (
    <>
      <article className="panel panel-span">
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
            <div className="evidence-filter-stack">
              <div className="evidence-filter-group">
                <span className="trace-label evidence-filter-label">{uiCopy.tierFilter}</span>
                <div className="filter-row evidence-filter-options">
                  <button
                    type="button"
                    className={`filter-chip${evidenceTierFilter === "all" ? " active" : ""}`}
                    onClick={() => onSetEvidenceTierFilter("all")}
                  >
                    {copy.all}
                  </button>
                  {evidenceTierOptions.map((tier) => (
                    <button
                      key={tier}
                      type="button"
                      className={`filter-chip${evidenceTierFilter === tier ? " active" : ""}`}
                      onClick={() => onSetEvidenceTierFilter(tier)}
                    >
                      {tier}
                    </button>
                  ))}
                </div>
              </div>

              <div className="evidence-filter-group">
                <span className="trace-label evidence-filter-label">{uiCopy.typeFilter}</span>
                <div className="filter-row evidence-filter-options">
                  <button
                    type="button"
                    className={`filter-chip${evidenceTypeFilter === "all" ? " active" : ""}`}
                    onClick={() => onSetEvidenceTypeFilter("all")}
                  >
                    {copy.all}
                  </button>
                  {evidenceTypeOptions.map((type) => (
                    <button
                      key={type}
                      type="button"
                      className={`filter-chip${evidenceTypeFilter === type ? " active" : ""}`}
                      onClick={() => onSetEvidenceTypeFilter(type)}
                    >
                      {getTopicAgentSourceTypeLabel(type, locale)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </article>
          <div className="trace-list evidence-record-grid">
            {filteredEvidenceRecords.map((record) => (
              <article key={record.source_id} className="trace-card evidence-record-card">
                <div className="trace-meta-row">
                  <strong>{record.title}</strong>
                  <span className="status-chip">{record.source_tier}</span>
                </div>
                <p className="trace-detail">
                  {getTopicAgentSourceTypeLabel(record.source_type, locale)} | {record.year} |{" "}
                  {record.authors_or_publisher}
                </p>
                <p
                  className={`trace-detail evidence-record-summary${
                    expandedEvidenceIds.includes(record.source_id) ? " expanded" : ""
                  }`}
                >
                  {record.summary}
                </p>
                <p className="trace-detail">
                  {copy.relevance}: {record.relevance_reason}
                </p>
                {expandedEvidenceIds.includes(record.source_id) && (
                  <>
                    <p className="trace-detail evidence-record-identifier">{record.identifier}</p>
                  </>
                )}
                <div className="button-row">
                  <button
                    type="button"
                    className="ghost-button"
                    onClick={() => toggleExpanded(record.source_id)}
                  >
                    {expandedEvidenceIds.includes(record.source_id)
                      ? uiCopy.collapse
                      : uiCopy.expand}
                  </button>
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
                  {focusedEvidence.source_tier} /{" "}
                  {getTopicAgentSourceTypeLabel(focusedEvidence.source_type, locale)}
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
