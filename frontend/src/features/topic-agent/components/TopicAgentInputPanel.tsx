import type { FormEvent } from "react";

type TopicAgentInputPanelProps = {
  copy: Record<string, string>;
  interest: string;
  problemDomain: string;
  seedIdea: string;
  timeBudgetMonths: string;
  resourceLevel: string;
  preferredStyle: string;
  topicBusy: boolean;
  topicError: string;
  hasTopicResult: boolean;
  onChangeInterest: (value: string) => void;
  onChangeProblemDomain: (value: string) => void;
  onChangeSeedIdea: (value: string) => void;
  onChangeTimeBudgetMonths: (value: string) => void;
  onChangeResourceLevel: (value: string) => void;
  onChangePreferredStyle: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onRefine: () => void;
};

export function TopicAgentInputPanel({
  copy,
  interest,
  problemDomain,
  seedIdea,
  timeBudgetMonths,
  resourceLevel,
  preferredStyle,
  topicBusy,
  topicError,
  hasTopicResult,
  onChangeInterest,
  onChangeProblemDomain,
  onChangeSeedIdea,
  onChangeTimeBudgetMonths,
  onChangeResourceLevel,
  onChangePreferredStyle,
  onSubmit,
  onRefine,
}: TopicAgentInputPanelProps) {
  return (
    <article className="panel">
      <div className="panel-heading">
        <div>
          <h2>{copy.formTitle}</h2>
          <p className="panel-intro">{copy.formCopy}</p>
        </div>
      </div>
      <form className="stack-form" onSubmit={onSubmit}>
        <label>
          <span>{copy.interest}</span>
          <input value={interest} onChange={(event) => onChangeInterest(event.target.value)} />
        </label>
        <label>
          <span>{copy.problemDomain}</span>
          <input value={problemDomain} onChange={(event) => onChangeProblemDomain(event.target.value)} />
        </label>
        <label>
          <span>{copy.seedIdea}</span>
          <textarea value={seedIdea} onChange={(event) => onChangeSeedIdea(event.target.value)} />
        </label>
        <label>
          <span>{copy.timeBudget}</span>
          <input
            value={timeBudgetMonths}
            inputMode="numeric"
            onChange={(event) => onChangeTimeBudgetMonths(event.target.value)}
          />
        </label>
        <label>
          <span>{copy.resourceLevel}</span>
          <input value={resourceLevel} onChange={(event) => onChangeResourceLevel(event.target.value)} />
        </label>
        <label>
          <span>{copy.preferredStyle}</span>
          <input
            value={preferredStyle}
            onChange={(event) => onChangePreferredStyle(event.target.value)}
          />
        </label>
        <div className="button-row">
          <button type="submit" className="primary-button" disabled={topicBusy}>
            {topicBusy ? copy.running : copy.run}
          </button>
          <button
            type="button"
            className="secondary-button"
            disabled={topicBusy || !hasTopicResult}
            onClick={onRefine}
          >
            {copy.refine}
          </button>
        </div>
      </form>
      {topicError && <p className="error">{topicError}</p>}
    </article>
  );
}
