import { TopicWorkspaceV2 } from "../../components/TopicWorkspaceV2";
import type { Locale } from "../../types";
import { useTopicAgent } from "./hooks/useTopicAgent";

type TopicAgentDemoPageProps = {
  locale: Locale;
};

export function TopicAgentDemoPage({ locale }: TopicAgentDemoPageProps) {
  const topicAgent = useTopicAgent();

  return (
    <TopicWorkspaceV2
      locale={locale}
      interest={topicAgent.interest}
      problemDomain={topicAgent.problemDomain}
      seedIdea={topicAgent.seedIdea}
      timeBudgetMonths={topicAgent.timeBudgetMonths}
      resourceLevel={topicAgent.resourceLevel}
      preferredStyle={topicAgent.preferredStyle}
      disableCache={topicAgent.disableCache}
      topicResult={topicAgent.topicResult}
      topicComparisonResult={topicAgent.topicComparisonResult}
      topicSessions={topicAgent.topicSessions}
      topicBusy={topicAgent.topicBusy}
      topicError={topicAgent.topicError}
      topicPresets={topicAgent.topicPresets}
      onChangeInterest={topicAgent.setInterest}
      onChangeProblemDomain={topicAgent.setProblemDomain}
      onChangeSeedIdea={topicAgent.setSeedIdea}
      onChangeTimeBudgetMonths={topicAgent.setTimeBudgetMonths}
      onChangeResourceLevel={topicAgent.setResourceLevel}
      onChangePreferredStyle={topicAgent.setPreferredStyle}
      onChangeDisableCache={topicAgent.setDisableCache}
      onSubmit={topicAgent.submitTopicExplore}
      onRefine={() => void topicAgent.refineCurrentTopicSession()}
      onLoadSession={(sessionId) => void topicAgent.loadTopicAgentSession(sessionId)}
      onCompareSession={(sessionId) => void topicAgent.compareTopicAgentSession(sessionId)}
      onApplyPreset={topicAgent.applyTopicPreset}
    />
  );
}
