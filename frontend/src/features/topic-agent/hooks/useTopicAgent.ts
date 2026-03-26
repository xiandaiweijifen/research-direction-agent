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

const DEFAULT_INPUT = {
  interest: "trustworthy multimodal reasoning in medical imaging",
  problemDomain: "medical AI",
  seedIdea: "I want a narrow and feasible research topic.",
  timeBudgetMonths: "6",
  resourceLevel: "student",
  preferredStyle: "benchmark-driven",
};

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
  };
}
