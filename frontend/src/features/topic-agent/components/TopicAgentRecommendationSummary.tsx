import type {
  Locale,
  TopicAgentComparisonAssessment,
  TopicAgentSessionResponse,
} from "../../../types";
import { getTopicAgentDimensionLabel } from "../display";

type TopicAgentRecommendationSummaryProps = {
  locale: Locale;
  topicResult: TopicAgentSessionResponse;
  copy: Record<string, string>;
  resolveCandidateLabel: (candidateId?: string | null) => string;
  resolveAssessmentTitle: (assessment: TopicAgentComparisonAssessment) => string;
};

export function TopicAgentRecommendationSummary({
  locale,
  topicResult,
  copy,
  resolveCandidateLabel,
  resolveAssessmentTitle,
}: TopicAgentRecommendationSummaryProps) {
  const recommendationId = topicResult.convergence_result.recommended_candidate_id;
  const backupId = topicResult.convergence_result.backup_candidate_id;
  const uiCopy =
    locale === "zh"
      ? {
          leadDecision: "当前推荐",
          backupDecision: "备选方向",
          decisionChecklist: "决策检查清单",
          comparisonSnapshot: "比较摘要",
          recommendationReason: "推荐理由",
          recommendationLead:
            "先看这条推荐方向，再决定是否需要回头检查完整评分表。",
          backupLead: "如果主方向太冒险或资源不够，优先回看这条备选。",
          candidateAssessmentLead: "候选评估概览",
          recommendedBadge: "推荐",
          backupBadge: "备选",
        }
      : {
          leadDecision: "Lead Recommendation",
          backupDecision: "Backup Direction",
          decisionChecklist: "Decision Checklist",
          comparisonSnapshot: "Comparison Snapshot",
          recommendationReason: "Recommendation Reason",
          recommendationLead:
            "Start with the lead recommendation before deciding whether you need the full score table.",
          backupLead: "Return to this backup first if the lead option feels too risky or too costly.",
          candidateAssessmentLead: "Candidate Assessment Snapshot",
          recommendedBadge: "Recommended",
          backupBadge: "Backup",
        };

  return (
    <article className="panel panel-span">
      <div className="panel-heading">
        <div>
          <h2>{copy.comparison}</h2>
          <p className="panel-intro">{topicResult.comparison_result.summary}</p>
        </div>
      </div>
      <div className="decision-layout">
        <article className="decision-hero-card">
          <span className="trace-label">{uiCopy.leadDecision}</span>
          <strong>
            {resolveCandidateLabel(recommendationId)}
          </strong>
          <p className="subsection-copy">{uiCopy.recommendationLead}</p>
          <div className="pill-strip">
            <span className="meta-pill">{copy.confidence}: {topicResult.confidence_summary.candidate_separation}</span>
            <span className="meta-pill">{copy.evidenceStrength}: {topicResult.comparison_result.candidate_assessments.find((item) => item.candidate_id === recommendationId)?.evidence_strength ?? "-"}</span>
          </div>
        </article>

        <div className="decision-side-stack">
          <article className="subsection-card decision-side-card">
            <span className="trace-label">{uiCopy.backupDecision}</span>
            <strong>{resolveCandidateLabel(backupId)}</strong>
            <p className="subsection-copy">{uiCopy.backupLead}</p>
          </article>

          <article className="subsection-card decision-side-card">
            <span className="trace-label">{copy.dimensions}</span>
            <div className="pill-strip">
              {topicResult.comparison_result.dimensions.map((dimension) => (
                <span key={dimension} className="meta-pill">
                  {getTopicAgentDimensionLabel(dimension, locale)}
                </span>
              ))}
            </div>
          </article>
        </div>
      </div>

      <div className="comparison-diff-grid">
        <article className="subsection-card">
          <span className="trace-label">{uiCopy.recommendationReason}</span>
          <p className="subsection-copy">{topicResult.convergence_result.rationale}</p>
        </article>

        <article className="subsection-card">
          <span className="trace-label">{uiCopy.decisionChecklist}</span>
          <div className="decision-checklist">
            {topicResult.convergence_result.manual_checks.map((check) => (
              <div key={check} className="decision-check-item">
                <span className="decision-check-bullet" aria-hidden="true">
                  □
                </span>
                <p>{check}</p>
              </div>
            ))}
          </div>
        </article>
      </div>

      <div className="panel-heading comparison-summary-heading">
        <div>
          <h2>{copy.candidateScores}</h2>
          <p className="panel-intro">{uiCopy.candidateAssessmentLead}</p>
        </div>
        <span className="status-chip">
          {topicResult.comparison_result.candidate_assessments.length} {copy.assessments}
        </span>
      </div>
      <div className="trace-list candidate-grid">
        {topicResult.comparison_result.candidate_assessments.map((assessment) => (
          <article key={assessment.candidate_id} className="trace-card comparison-card">
            <div className="trace-meta-row">
              <strong>{resolveAssessmentTitle(assessment)}</strong>
              <div className="pill-strip">
                {assessment.candidate_id === recommendationId && (
                  <span className="status-chip success">{uiCopy.recommendedBadge}</span>
                )}
                {assessment.candidate_id === backupId && (
                  <span className="status-chip">{uiCopy.backupBadge}</span>
                )}
                <span className="status-chip">{assessment.novelty}</span>
              </div>
            </div>
            <div className="comparison-metric-grid">
              <div className="comparison-metric">
                <span className="trace-label">{copy.novelty}</span>
                <strong>{assessment.novelty}</strong>
              </div>
              <div className="comparison-metric">
                <span className="trace-label">{copy.feasibility}</span>
                <strong>{assessment.feasibility}</strong>
              </div>
              <div className="comparison-metric">
                <span className="trace-label">{copy.evidenceStrength}</span>
                <strong>{assessment.evidence_strength}</strong>
              </div>
              <div className="comparison-metric">
                <span className="trace-label">{copy.dataAvailability}</span>
                <strong>{assessment.data_availability}</strong>
              </div>
              <div className="comparison-metric">
                <span className="trace-label">{copy.implementationCost}</span>
                <strong>{assessment.implementation_cost}</strong>
              </div>
              <div className="comparison-metric">
                <span className="trace-label">{copy.risk}</span>
                <strong>{assessment.risk}</strong>
              </div>
            </div>
          </article>
        ))}
      </div>
    </article>
  );
}
