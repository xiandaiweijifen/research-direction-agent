import { FormEvent, useEffect, useState } from "react";

import {
  fetchTopicAgentSession,
  fetchTopicAgentSessions,
  refineTopicAgentSession as refineTopicAgentSessionRequest,
  runTopicAgentExplore as runTopicAgentExploreRequest,
} from "../../../api";
import type {
  TopicAgentSessionResponse,
  TopicAgentSessionSummary,
} from "../../../types";

export type TopicAgentDemoPreset = {
  id: string;
  labelEn: string;
  labelZh: string;
  summaryEn: string;
  summaryZh: string;
  interest: string;
  problemDomain: string;
  seedIdea: string;
  timeBudgetMonths: string;
  resourceLevel: string;
  preferredStyle: string;
};

const TOPIC_AGENT_DEMO_PRESETS: TopicAgentDemoPreset[] = [
  {
    id: "bug_fixing",
    labelEn: "Bug-Fixing Agents",
    labelZh: "Bug 修复 Agent",
    summaryEn: "Modern software-agent demo with reproducible evaluation pressure.",
    summaryZh: "面向现代软件 Agent 的可复现实验演示场景。",
    interest: "llm agents for automated bug fixing",
    problemDomain: "software engineering",
    seedIdea: "I want a feasible applied topic on reproducible evaluation for low-cost bug-fixing agents.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "applied",
  },
  {
    id: "medical_reasoning",
    labelEn: "Broad Medical Reasoning",
    labelZh: "宽泛 Medical Reasoning",
    summaryEn: "Broad-topic stress case for framing and evidence narrowing.",
    summaryZh: "用于 framing 和证据收敛的宽主题压力场景。",
    interest: "medical reasoning",
    problemDomain: "medical AI",
    seedIdea: "I want a feasible applied topic with clear benchmark or evaluation boundaries.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "applied",
  },
  {
    id: "radiology_vqa",
    labelEn: "Radiology VQA",
    labelZh: "放射学 VQA",
    summaryEn: "Narrow benchmark-oriented multimodal topic.",
    summaryZh: "窄范围、基准导向的多模态主题。",
    interest: "trustworthy visual question answering in radiology",
    problemDomain: "medical AI",
    seedIdea: "I want a narrow and feasible benchmark-oriented topic.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "applied",
  },
  {
    id: "repository_bug_fixing",
    labelEn: "Repository Bug-Fixing",
    labelZh: "仓库级 Bug 修复",
    summaryEn: "Repository-level workflow support and evaluation demo.",
    summaryZh: "仓库级工作流与评测支撑演示场景。",
    interest: "repository-level bug-fixing agents",
    problemDomain: "software engineering evaluation",
    seedIdea: "I want a feasible applied topic on reproducible evaluation and workflow support for low-cost repair agents.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "applied",
  },
];

const DEFAULT_INPUT = TOPIC_AGENT_DEMO_PRESETS[0];

export function useTopicAgent() {
  const [interest, setInterest] = useState(DEFAULT_INPUT.interest);
  const [problemDomain, setProblemDomain] = useState(DEFAULT_INPUT.problemDomain);
  const [seedIdea, setSeedIdea] = useState(DEFAULT_INPUT.seedIdea);
  const [timeBudgetMonths, setTimeBudgetMonths] = useState(DEFAULT_INPUT.timeBudgetMonths);
  const [resourceLevel, setResourceLevel] = useState(DEFAULT_INPUT.resourceLevel);
  const [preferredStyle, setPreferredStyle] = useState(DEFAULT_INPUT.preferredStyle);

  const [topicResult, setTopicResult] = useState<TopicAgentSessionResponse | null>(null);
  const [topicComparisonResult, setTopicComparisonResult] =
    useState<TopicAgentSessionResponse | null>(null);
  const [topicSessions, setTopicSessions] = useState<TopicAgentSessionSummary[]>([]);
  const [topicBusy, setTopicBusy] = useState(false);
  const [topicError, setTopicError] = useState("");

  useEffect(() => {
    void loadTopicAgentSessions();
  }, []);

  async function loadTopicAgentSessions() {
    try {
      const payload = await fetchTopicAgentSessions(8);
      setTopicSessions(payload.sessions);
    } catch {
      setTopicSessions([]);
    }
  }

  async function submitTopicExplore(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopicBusy(true);
    setTopicError("");
    setTopicResult(null);
    setTopicComparisonResult(null);

    try {
      const payload = await runTopicAgentExploreRequest(interest, problemDomain, seedIdea, {
        time_budget_months: timeBudgetMonths ? Number(timeBudgetMonths) : undefined,
        resource_level: resourceLevel || undefined,
        preferred_style: preferredStyle || undefined,
      });
      setTopicResult(payload);
      await loadTopicAgentSessions();
    } catch (error) {
      setTopicError(error instanceof Error ? error.message : "Failed to run Topic Agent");
    } finally {
      setTopicBusy(false);
    }
  }

  async function refineCurrentTopicSession() {
    if (!topicResult) {
      return;
    }

    setTopicBusy(true);
    setTopicError("");
    setTopicComparisonResult(null);

    try {
      const payload = await refineTopicAgentSessionRequest(topicResult.session_id, {
        interest: interest || undefined,
        problem_domain: problemDomain || undefined,
        seed_idea: seedIdea || undefined,
        constraints: {
          time_budget_months: timeBudgetMonths ? Number(timeBudgetMonths) : undefined,
          resource_level: resourceLevel || undefined,
          preferred_style: preferredStyle || undefined,
        },
      });
      setTopicResult(payload);
      await loadTopicAgentSessions();
    } catch (error) {
      setTopicError(error instanceof Error ? error.message : "Failed to refine Topic Agent session");
    } finally {
      setTopicBusy(false);
    }
  }

  async function loadTopicAgentSession(sessionId: string) {
    setTopicBusy(true);
    setTopicError("");
    setTopicComparisonResult(null);

    try {
      const payload = await fetchTopicAgentSession(sessionId);
      hydrateInputFromSession(payload);
      setTopicResult(payload);
    } catch (error) {
      setTopicError(error instanceof Error ? error.message : "Failed to load Topic Agent session");
    } finally {
      setTopicBusy(false);
    }
  }

  async function compareTopicAgentSession(sessionId: string) {
    setTopicBusy(true);
    setTopicError("");

    try {
      const payload = await fetchTopicAgentSession(sessionId);
      setTopicComparisonResult(payload);
    } catch (error) {
      setTopicError(error instanceof Error ? error.message : "Failed to compare Topic Agent session");
    } finally {
      setTopicBusy(false);
    }
  }

  function hydrateInputFromSession(payload: TopicAgentSessionResponse) {
    setInterest(payload.user_input.interest);
    setProblemDomain(payload.user_input.problem_domain ?? "");
    setSeedIdea(payload.user_input.seed_idea ?? "");
    setTimeBudgetMonths(
      payload.user_input.constraints.time_budget_months != null
        ? String(payload.user_input.constraints.time_budget_months)
        : "",
    );
    setResourceLevel(payload.user_input.constraints.resource_level ?? "");
    setPreferredStyle(payload.user_input.constraints.preferred_style ?? "");
  }

  function applyTopicPreset(presetId: string) {
    const preset = TOPIC_AGENT_DEMO_PRESETS.find((item) => item.id === presetId);
    if (!preset) {
      return;
    }

    setInterest(preset.interest);
    setProblemDomain(preset.problemDomain);
    setSeedIdea(preset.seedIdea);
    setTimeBudgetMonths(preset.timeBudgetMonths);
    setResourceLevel(preset.resourceLevel);
    setPreferredStyle(preset.preferredStyle);
    setTopicComparisonResult(null);
    setTopicError("");
  }

  return {
    interest,
    problemDomain,
    seedIdea,
    timeBudgetMonths,
    resourceLevel,
    preferredStyle,
    topicResult,
    topicComparisonResult,
    topicSessions,
    topicBusy,
    topicError,
    topicPresets: TOPIC_AGENT_DEMO_PRESETS,
    setInterest,
    setProblemDomain,
    setSeedIdea,
    setTimeBudgetMonths,
    setResourceLevel,
    setPreferredStyle,
    submitTopicExplore,
    refineCurrentTopicSession,
    loadTopicAgentSession,
    compareTopicAgentSession,
    applyTopicPreset,
  };
}
