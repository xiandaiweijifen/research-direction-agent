import type { FormEvent } from "react";
import type { Locale } from "../../../types";
import type { TopicAgentDemoPreset } from "../hooks/useTopicAgent";

type TopicAgentInputPanelProps = {
  locale: Locale;
  copy: Record<string, string>;
  topicPresets: TopicAgentDemoPreset[];
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
  onApplyPreset: (presetId: string) => void;
};

export function TopicAgentInputPanel({
  locale,
  copy,
  topicPresets,
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
  onApplyPreset,
}: TopicAgentInputPanelProps) {
  const uiCopy =
    locale === "zh"
      ? {
          presets: "Demo 场景",
          presetsIntro: "先用稳定场景演示，再切回自由输入。",
          recentRunsHint: "会话历史已经按 recent runs 收敛，不再作为长档案展示。",
          boundaryTitle: "当前更适合演示的方向",
          boundaryCopy:
            "当前后端在软件工程导向 family 上更稳定，尤其是 repository repair、repository issue-resolution 及其相邻方向。跨域方向仍应视为边界检查，而不是默认稳定能力。",
          readingPathTitle: "默认阅读顺序",
          readingPathCopy: "建议按 framing → top evidence → comparison → recommendation 的顺序查看结果。",
        }
      : {
          presets: "Demo Presets",
          presetsIntro: "Start with a stable scenario, then switch back to free-form input.",
          recentRunsHint: "Session history is now trimmed to recent runs instead of acting like a long archive.",
          boundaryTitle: "Best-Fit Demo Families",
          boundaryCopy:
            "The current backend is most stable on software-engineering-oriented families, especially repository repair, repository issue-resolution, and nearby directions. Cross-domain topics should still be treated as boundary checks rather than default strengths.",
          readingPathTitle: "Default Reading Path",
          readingPathCopy:
            "For demos, read the result in this order: framing → top evidence → comparison → recommendation.",
        };

  return (
    <article className="panel">
      <div className="panel-heading">
        <div>
          <h2>{copy.formTitle}</h2>
          <p className="panel-intro">{copy.formCopy}</p>
        </div>
      </div>
      <article className="subsection-card">
        <span className="trace-label">{uiCopy.presets}</span>
        <p className="subsection-copy">{uiCopy.presetsIntro}</p>
        <div className="trace-list">
          {topicPresets.map((preset) => {
            const label = locale === "zh" ? preset.labelZh : preset.labelEn;
            const summary = locale === "zh" ? preset.summaryZh : preset.summaryEn;
            return (
              <article key={preset.id} className="trace-card">
                <div className="trace-meta-row">
                  <strong>{label}</strong>
                  <button
                    type="button"
                    className="ghost-button"
                    onClick={() => onApplyPreset(preset.id)}
                    disabled={topicBusy}
                  >
                    {copy.load}
                  </button>
                </div>
                <p className="trace-detail">{summary}</p>
              </article>
            );
          })}
        </div>
      </article>
      <article className="subsection-card">
        <span className="trace-label">{uiCopy.boundaryTitle}</span>
        <p className="subsection-copy">{uiCopy.boundaryCopy}</p>
        <span className="trace-label">{uiCopy.readingPathTitle}</span>
        <p className="subsection-copy">{uiCopy.readingPathCopy}</p>
      </article>
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
      <p className="panel-intro">{uiCopy.recentRunsHint}</p>
      {topicError && <p className="error">{topicError}</p>}
    </article>
  );
}
