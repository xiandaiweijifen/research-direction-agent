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
  return (
    <article className="panel panel-span">
      <div className="panel-heading">
        <div>
          <h2>{copy.comparison}</h2>
          <p className="panel-intro">{topicResult.comparison_result.summary}</p>
        </div>
      </div>
      <div className="summary-strip">
        <div className="summary-card summary-card-emphasis">
          <span>{copy.recommendation}</span>
          <strong>
            {resolveCandidateLabel(topicResult.convergence_result.recommended_candidate_id)}
          </strong>
        </div>
        <div className="summary-card">
          <span>{copy.backup}</span>
          <strong>{resolveCandidateLabel(topicResult.convergence_result.backup_candidate_id)}</strong>
        </div>
        <div className="summary-card">
          <span>{copy.confidence}</span>
          <strong>{topicResult.confidence_summary.candidate_separation}</strong>
        </div>
      </div>
      <article className="subsection-card">
        <span className="trace-label">{copy.rationale}</span>
        <p className="subsection-copy">{topicResult.convergence_result.rationale}</p>
      </article>
      <article className="subsection-card">
        <span className="trace-label">{copy.dimensions}</span>
        <div className="pill-strip">
          {topicResult.comparison_result.dimensions.map((dimension) => (
            <span key={dimension} className="meta-pill">
              {getTopicAgentDimensionLabel(dimension, locale)}
            </span>
          ))}
        </div>
      </article>
      <article className="subsection-card">
        <span className="trace-label">{copy.manualChecks}</span>
        <div className="list-block">
          {topicResult.convergence_result.manual_checks.map((check) => (
            <p key={check}>{check}</p>
          ))}
        </div>
      </article>
      <div className="panel-heading">
        <div>
          <h2>{copy.candidateScores}</h2>
          <p className="panel-intro">
            {topicResult.comparison_result.candidate_assessments.length} {copy.assessments}
          </p>
        </div>
      </div>
      <div className="trace-list candidate-grid">
        {topicResult.comparison_result.candidate_assessments.map((assessment) => (
          <article key={assessment.candidate_id} className="trace-card comparison-card">
            <div className="trace-meta-row">
              <strong>{resolveAssessmentTitle(assessment)}</strong>
              <span className="status-chip">{assessment.novelty}</span>
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
