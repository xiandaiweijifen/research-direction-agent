import type { FormEvent } from "react";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TopicWorkspaceV2 } from "./TopicWorkspaceV2";

describe("TopicWorkspaceV2", () => {
  it("renders topic-agent results, filters evidence, and submits actions", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn((event: FormEvent<HTMLFormElement>) => event.preventDefault());
    const onRefine = vi.fn();
    const onCompareSession = vi.fn();

    render(
      <TopicWorkspaceV2
        locale="en"
        interest="trustworthy multimodal reasoning in medical imaging"
        problemDomain="medical AI"
        seedIdea="narrow benchmark-driven topic"
        timeBudgetMonths="6"
        resourceLevel="student"
        preferredStyle="benchmark-driven"
        topicComparisonResult={{
          session_id: "session_2",
          created_at: "2026-03-24T00:00:00+00:00",
          updated_at: "2026-03-24T00:00:00+00:00",
          user_input: {
            interest: "trustworthy multimodal reasoning in medical imaging",
            problem_domain: "medical AI",
            seed_idea: "previous pass",
            constraints: {
              time_budget_months: 6,
              resource_level: "student",
              preferred_style: "benchmark-driven",
              notes: null,
            },
          },
          framing_result: {
            normalized_topic: "trustworthy multimodal reasoning in medical imaging",
            extracted_constraints: {
              time_budget_months: "6",
            },
            missing_clarifications: [],
            search_questions: ["What methods are common?"],
          },
          evidence_records: [
            {
              source_id: "source_1",
              title: "Recent Survey",
              source_type: "survey",
              source_tier: "A",
              year: 2025,
              authors_or_publisher: "Survey Authors",
              identifier: "survey:1",
              url: "https://example.org",
              summary: "Survey summary",
              relevance_reason: "High-level map",
            },
          ],
          landscape_summary: {
            themes: ["theme"],
            active_methods: ["method"],
            likely_gaps: ["gap"],
            saturated_areas: ["saturated"],
          },
          candidate_topics: [
            {
              candidate_id: "candidate_2",
              title: "Method Transfer Under Practical Constraints",
              research_question: "Can existing methods adapt under resource limits?",
              positioning: "transfer",
              novelty_note: "medium novelty",
              feasibility_note: "high feasibility",
              risk_note: "medium risk",
              supporting_source_ids: ["source_1"],
              open_questions: ["Which constraint matters most?"],
            },
          ],
          comparison_result: {
            dimensions: ["novelty", "feasibility"],
            summary: "Previous pass summary.",
            candidate_assessments: [
              {
                candidate_id: "candidate_2",
                novelty: "medium",
                feasibility: "high",
                evidence_strength: "medium",
                data_availability: "medium",
                implementation_cost: "medium_low",
                risk: "medium",
              },
            ],
          },
          convergence_result: {
            recommended_candidate_id: "candidate_2",
            backup_candidate_id: null,
            rationale: "Previous rationale.",
            manual_checks: ["Previous check."],
          },
          evidence_presentation: {
            source_facts: [],
            system_synthesis: [],
            tentative_inferences: [],
          },
          human_confirmations: [],
          clarification_suggestions: [],
          trace: [
            {
              stage: "frame_problem",
              status: "completed",
              timestamp: "2026-03-24T00:00:00+00:00",
              detail: "Previous trace.",
            },
          ],
          confidence_summary: {
            evidence_coverage: "medium",
            source_quality: "high",
            candidate_separation: "medium",
            conflict_level: "low",
            rationale: ["Previous confidence."],
          },
          evidence_diagnostics: {
            requested_provider: "openalex",
            used_provider: "openalex",
            fallback_used: false,
            fallback_reason: null,
            record_count: 1,
            cache_hit: false,
          },
        }}
        topicSessions={[
          {
            session_id: "session_1",
            created_at: "2026-03-25T00:00:00+00:00",
            updated_at: "2026-03-25T00:00:00+00:00",
            interest: "trustworthy multimodal reasoning in medical imaging",
            problem_domain: "medical AI",
            candidate_count: 2,
            recommended_candidate_id: "candidate_1",
          },
          {
            session_id: "session_2",
            created_at: "2026-03-24T00:00:00+00:00",
            updated_at: "2026-03-24T00:00:00+00:00",
            interest: "trustworthy multimodal reasoning in medical imaging",
            problem_domain: "medical AI",
            candidate_count: 1,
            recommended_candidate_id: "candidate_2",
          },
        ]}
        topicBusy={false}
        topicError=""
        topicResult={{
          session_id: "session_1",
          created_at: "2026-03-25T00:00:00+00:00",
          updated_at: "2026-03-25T00:00:00+00:00",
          user_input: {
            interest: "trustworthy multimodal reasoning in medical imaging",
            problem_domain: "medical AI",
            seed_idea: "narrow benchmark-driven topic",
            constraints: {
              time_budget_months: 6,
              resource_level: "student",
              preferred_style: "benchmark-driven",
              notes: null,
            },
          },
          framing_result: {
            normalized_topic: "trustworthy multimodal reasoning in medical imaging",
            extracted_constraints: {
              time_budget_months: "6",
            },
            missing_clarifications: [],
            search_questions: ["What are the main research themes?"],
          },
          evidence_records: [
            {
              source_id: "source_1",
              title: "Recent Survey",
              source_type: "survey",
              source_tier: "A",
              year: 2025,
              authors_or_publisher: "Survey Authors",
              identifier: "survey:1",
              url: "https://example.org",
              summary: "Survey summary",
              relevance_reason: "High-level map",
            },
            {
              source_id: "source_2",
              title: "Open Repo",
              source_type: "code",
              source_tier: "B",
              year: 2024,
              authors_or_publisher: "Maintainers",
              identifier: "repo:2",
              url: "https://example.org/repo",
              summary: "Reusable baselines",
              relevance_reason: "Feasibility support",
            },
          ],
          landscape_summary: {
            themes: ["theme"],
            active_methods: ["method"],
            likely_gaps: ["gap"],
            saturated_areas: ["saturated"],
          },
          candidate_topics: [
            {
              candidate_id: "candidate_1",
              title: "Benchmark-Guided Narrow Task Definition",
              research_question: "How can a narrower benchmark task reveal limitations?",
              positioning: "gap-driven",
              novelty_note: "high",
              feasibility_note: "medium",
              risk_note: "medium",
              supporting_source_ids: ["source_1"],
              open_questions: ["Which benchmark subset?"],
            },
            {
              candidate_id: "candidate_2",
              title: "Method Transfer Under Practical Constraints",
              research_question: "Can existing methods adapt under resource limits?",
              positioning: "transfer",
              novelty_note: "medium novelty",
              feasibility_note: "high feasibility",
              risk_note: "medium risk",
              supporting_source_ids: ["source_2"],
              open_questions: ["Which constraint matters most?"],
            },
          ],
          comparison_result: {
            dimensions: ["novelty", "feasibility"],
            summary: "Candidate 1 is strongest on research focus.",
            candidate_assessments: [
              {
                candidate_id: "candidate_1",
                novelty: "high",
                feasibility: "medium",
                evidence_strength: "medium_high",
                data_availability: "medium",
                implementation_cost: "medium",
                risk: "medium",
              },
              {
                candidate_id: "candidate_2",
                novelty: "medium",
                feasibility: "high",
                evidence_strength: "medium",
                data_availability: "medium_high",
                implementation_cost: "medium_low",
                risk: "medium",
              },
            ],
          },
          convergence_result: {
            recommended_candidate_id: "candidate_1",
            backup_candidate_id: "candidate_2",
            rationale: "Best balance.",
            manual_checks: ["Check benchmark availability."],
          },
          evidence_presentation: {
            source_facts: [],
            system_synthesis: [],
            tentative_inferences: [],
          },
          human_confirmations: [],
          clarification_suggestions: [],
          trace: [
            {
              stage: "frame_problem",
              status: "completed",
              timestamp: "2026-03-25T00:00:00+00:00",
              detail: "Structured the user input.",
            },
          ],
          confidence_summary: {
            evidence_coverage: "medium",
            source_quality: "medium_high",
            candidate_separation: "high",
            conflict_level: "low",
            rationale: ["Evidence coverage is medium."],
          },
          evidence_diagnostics: {
            requested_provider: "openalex",
            used_provider: "openalex",
            fallback_used: false,
            fallback_reason: null,
            record_count: 2,
            cache_hit: false,
          },
        }}
        onChangeInterest={vi.fn()}
        onChangeProblemDomain={vi.fn()}
        onChangeSeedIdea={vi.fn()}
        onChangeTimeBudgetMonths={vi.fn()}
        onChangeResourceLevel={vi.fn()}
        onChangePreferredStyle={vi.fn()}
        onSubmit={onSubmit}
        onRefine={onRefine}
        onLoadSession={vi.fn()}
        onCompareSession={onCompareSession}
      />,
    );

    expect(screen.getByText("Research Topic Copilot")).toBeInTheDocument();
    expect(screen.getByText("Research Landscape")).toBeInTheDocument();
    expect(screen.getByText("Evidence Filters")).toBeInTheDocument();
    expect(screen.getAllByText("Focused Evidence").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Recent Survey").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Open Repo").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Benchmark-Guided Narrow Task Definition").length).toBeGreaterThan(
      0,
    );
    expect(screen.getByText("Evidence coverage is medium.")).toBeInTheDocument();
    expect(screen.getByText("Recent Sessions")).toBeInTheDocument();
    expect(screen.getByText("2 topics")).toBeInTheDocument();
    expect(screen.getByText("Session Diff")).toBeInTheDocument();
    expect(screen.getByText("Previous rationale.")).toBeInTheDocument();
    expect(screen.getAllByText("Benchmark-Guided Narrow Task Definition").length).toBeGreaterThan(
      0,
    );
    expect(screen.getByText("Candidate Comparison")).toBeInTheDocument();
    expect(screen.getAllByText("Best balance.").length).toBeGreaterThan(0);
    expect(screen.getByText("Check benchmark availability.")).toBeInTheDocument();
    expect(screen.getAllByText("medium_high").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Supporting Evidence").length).toBeGreaterThan(0);
    expect(screen.getByText("source_1: Recent Survey")).toBeInTheDocument();
    expect(screen.getByText("source_2: Open Repo")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "A" }));
    expect(screen.getAllByText("Recent Survey").length).toBeGreaterThan(0);
    expect(screen.queryByText("Open Repo")).not.toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "All" })[0]);
    expect(screen.getAllByText("Open Repo").length).toBeGreaterThan(0);

    await user.click(screen.getByRole("button", { name: "source_2: Open Repo" }));
    expect(screen.getByText("repo:2")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Compare" }));
    expect(onCompareSession).toHaveBeenCalledWith("session_2");

    await user.click(screen.getByRole("button", { name: "Run Topic Agent" }));
    expect(onSubmit).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole("button", { name: "Refine Current Session" }));
    expect(onRefine).toHaveBeenCalledTimes(1);
  });
});
