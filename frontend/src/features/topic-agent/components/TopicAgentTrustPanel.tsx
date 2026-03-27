import type { TopicAgentSessionResponse } from "../../../types";

type TopicAgentTrustPanelProps = {
  topicResult: TopicAgentSessionResponse;
  copy: Record<string, string>;
  locale: "en" | "zh";
  evidenceTitleById: Map<string, string>;
};

function renderEvidenceLinks(sourceIds: string[], evidenceTitleById: Map<string, string>) {
  if (sourceIds.length === 0) {
    return null;
  }

  return (
    <div className="pill-strip">
      {sourceIds.map((sourceId) => (
        <span key={sourceId} className="meta-pill muted-pill">
          {evidenceTitleById.get(sourceId) ?? sourceId}
        </span>
      ))}
    </div>
  );
}

export function TopicAgentTrustPanel({
  topicResult,
  copy,
  locale,
  evidenceTitleById,
}: TopicAgentTrustPanelProps) {
  const trustCopy =
    locale === "zh"
      ? {
          trust: "可信度与诊断",
          trustIntro: "展示当前结论如何被证据支撑，以及哪些地方仍需人工确认。",
          sourceFacts: "来源事实",
          systemSynthesis: "系统综合",
          tentativeInferences: "暂定推断",
          supportingSources: "支撑来源",
          note: "说明",
          uncertainty: "不确定性",
          missingEvidence: "缺失证据",
          confirmations: "人工确认项",
          clarifications: "澄清建议",
          diagnostics: "证据诊断",
          requestedProvider: "请求 Provider",
          usedProvider: "实际 Provider",
          fallbackUsed: "是否 fallback",
          recordCount: "记录数",
          cacheHit: "缓存命中",
          trace: copy.trace,
          confidence: copy.confidence,
          stages: copy.stages,
          yes: "是",
          no: "否",
        }
      : {
          trust: "Trust And Diagnostics",
          trustIntro:
            "Show how the current recommendation is supported, and which parts still require human review.",
          sourceFacts: "Source Facts",
          systemSynthesis: "System Synthesis",
          tentativeInferences: "Tentative Inferences",
          supportingSources: "Supporting Sources",
          note: "Note",
          uncertainty: "Uncertainty",
          missingEvidence: "Missing Evidence",
          confirmations: "Human Confirmations",
          clarifications: "Clarification Suggestions",
          diagnostics: "Evidence Diagnostics",
          requestedProvider: "Requested Provider",
          usedProvider: "Used Provider",
          fallbackUsed: "Fallback Used",
          recordCount: "Record Count",
          cacheHit: "Cache Hit",
          trace: copy.trace,
          confidence: copy.confidence,
          stages: copy.stages,
          yes: "yes",
          no: "no",
        };

  const evidenceSections = [
    {
      title: trustCopy.sourceFacts,
      statements: topicResult.evidence_presentation.source_facts,
    },
    {
      title: trustCopy.systemSynthesis,
      statements: topicResult.evidence_presentation.system_synthesis,
    },
    {
      title: trustCopy.tentativeInferences,
      statements: topicResult.evidence_presentation.tentative_inferences,
    },
  ];

  return (
    <article className="panel panel-span">
      <div className="panel-heading">
        <div>
          <h2>{trustCopy.trust}</h2>
          <p className="panel-intro">{trustCopy.trustIntro}</p>
        </div>
      </div>

      <div className="comparison-diff-grid">
        {evidenceSections.map((section) => (
          <article key={section.title} className="subsection-card">
            <span className="trace-label">{section.title}</span>
            {section.statements.length === 0 ? (
              <p className="subsection-copy">-</p>
            ) : (
              <div className="trace-list">
                {section.statements.map((item, index) => (
                  <article
                    key={`${section.title}-${index}-${item.statement}`}
                    className="trace-card"
                  >
                    <p className="trace-detail">{item.statement}</p>
                    {renderEvidenceLinks(item.supporting_source_ids, evidenceTitleById)}
                    {item.note && (
                      <p className="trace-detail">
                        {trustCopy.note}: {item.note}
                      </p>
                    )}
                    {item.uncertainty_reason && (
                      <p className="trace-detail">
                        {trustCopy.uncertainty}: {item.uncertainty_reason}
                      </p>
                    )}
                    {item.missing_evidence.length > 0 && (
                      <div className="list-block">
                        {item.missing_evidence.map((missing) => (
                          <p key={missing}>
                            {trustCopy.missingEvidence}: {missing}
                          </p>
                        ))}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>

      <div className="comparison-diff-grid">
        <article className="subsection-card">
          <span className="trace-label">{trustCopy.confirmations}</span>
          <div className="list-block">
            {topicResult.human_confirmations.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
        </article>

        <article className="subsection-card">
          <span className="trace-label">{trustCopy.clarifications}</span>
          {topicResult.clarification_suggestions.length === 0 ? (
            <p className="subsection-copy">-</p>
          ) : (
            <div className="trace-list">
              {topicResult.clarification_suggestions.map((item) => (
                <article key={item.field_key} className="trace-card">
                  <div className="trace-meta-row">
                    <strong>{item.field_key}</strong>
                  </div>
                  <p className="trace-detail">{item.prompt}</p>
                  <p className="trace-detail">
                    {trustCopy.note}: {item.reason}
                  </p>
                  {item.suggested_values.length > 0 && (
                    <div className="pill-strip">
                      {item.suggested_values.map((value) => (
                        <span key={value} className="meta-pill">
                          {value}
                        </span>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </article>
      </div>

      <div className="comparison-diff-grid">
        <article className="subsection-card">
          <span className="trace-label">{trustCopy.diagnostics}</span>
          <div className="trace-grid">
            <div>
              <span className="trace-label">{trustCopy.requestedProvider}</span>
              <strong>{topicResult.evidence_diagnostics.requested_provider}</strong>
            </div>
            <div>
              <span className="trace-label">{trustCopy.usedProvider}</span>
              <strong>{topicResult.evidence_diagnostics.used_provider}</strong>
            </div>
            <div>
              <span className="trace-label">{trustCopy.fallbackUsed}</span>
              <strong>
                {topicResult.evidence_diagnostics.fallback_used ? trustCopy.yes : trustCopy.no}
              </strong>
            </div>
            <div>
              <span className="trace-label">{trustCopy.recordCount}</span>
              <strong>{topicResult.evidence_diagnostics.record_count}</strong>
            </div>
            <div>
              <span className="trace-label">{trustCopy.cacheHit}</span>
              <strong>
                {topicResult.evidence_diagnostics.cache_hit ? trustCopy.yes : trustCopy.no}
              </strong>
            </div>
          </div>
          {topicResult.evidence_diagnostics.fallback_reason && (
            <p className="trace-detail">
              {trustCopy.note}: {topicResult.evidence_diagnostics.fallback_reason}
            </p>
          )}
        </article>

        <article className="subsection-card">
          <span className="trace-label">{trustCopy.confidence}</span>
          <div className="trace-list">
            {topicResult.confidence_summary.rationale.map((reason) => (
              <article key={reason} className="trace-card">
                <p className="trace-detail">{reason}</p>
              </article>
            ))}
          </div>
        </article>
      </div>

      <article className="subsection-card">
        <span className="trace-label">
          {trustCopy.trace} · {topicResult.trace.length} {trustCopy.stages}
        </span>
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
    </article>
  );
}
