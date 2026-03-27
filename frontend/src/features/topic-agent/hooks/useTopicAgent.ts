import { FormEvent, useEffect, useState } from "react";

import {
  fetchTopicAgentSession,
  fetchTopicAgentSessions,
  refineTopicAgentSession as refineTopicAgentSessionRequest,
  runTopicAgentExplore as runTopicAgentExploreRequest,
} from "../../../api";
import type { TopicAgentSessionResponse, TopicAgentSessionSummary } from "../../../types";

export type TopicAgentDemoPreset = {
  id: string;
  group: "recommended" | "boundary";
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
    group: "recommended",
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
    id: "repository_bug_fixing",
    group: "recommended",
    labelEn: "Repository Bug-Fixing",
    labelZh: "仓库级 Bug 修复",
    summaryEn: "Repository-level workflow support and reproducible evaluation demo.",
    summaryZh: "仓库级工作流与可复现评测支持演示场景。",
    interest: "repository-level bug-fixing agents",
    problemDomain: "software engineering evaluation",
    seedIdea: "I want a feasible applied topic on reproducible evaluation and workflow support for low-cost repair agents.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "applied",
  },
  {
    id: "repository_issue_resolution",
    group: "recommended",
    labelEn: "Repository Issue Resolution",
    labelZh: "仓库级 Issue 解决",
    summaryEn: "Repository issue-resolution agents with workflow and benchmark pressure.",
    summaryZh: "带有工作流与 benchmark 压力的仓库级 issue 解决 Agent 演示场景。",
    interest: "repository github issue triage and resolution agents",
    problemDomain: "software engineering workflow evaluation",
    seedIdea: "I want a feasible systems-oriented topic on reproducible workflow evaluation and infrastructure support for low-cost repository-level GitHub issue resolution agents.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "systems",
  },
  {
    id: "boundary_programming_education",
    group: "boundary",
    labelEn: "Boundary Check: Programming Education",
    labelZh: "边界检查：编程教育",
    summaryEn: "Cross-domain education case for showing current system boundaries.",
    summaryZh: "用于展示当前系统边界的跨域教育场景。",
    interest: "ai-supported feedback workflows for programming education",
    problemDomain: "computing education research",
    seedIdea: "I want a feasible benchmark-driven topic on evaluation design for AI-supported feedback workflows in programming education.",
    timeBudgetMonths: "6",
    resourceLevel: "student",
    preferredStyle: "benchmark-driven",
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
  const [disableCache, setDisableCache] = useState(false);

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
      }, {
        disable_cache: disableCache,
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
        disable_cache: disableCache,
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
    setDisableCache(payload.user_input.disable_cache ?? false);
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
    setDisableCache(false);
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
    disableCache,
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
    setDisableCache,
    submitTopicExplore,
    refineCurrentTopicSession,
    loadTopicAgentSession,
    compareTopicAgentSession,
    applyTopicPreset,
  };
}
