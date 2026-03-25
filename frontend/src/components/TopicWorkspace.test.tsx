import type { FormEvent } from "react";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TopicWorkspace } from "./TopicWorkspace";

describe("TopicWorkspace", () => {
  it("renders topic-agent results and submits the exploration form", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn((event: FormEvent<HTMLFormElement>) => event.preventDefault());
    const onRefine = vi.fn();

    render(
      <TopicWorkspace
        locale="en"
        interest="trustworthy multimodal reasoning in medical imaging"
        problemDomain="medical AI"
        seedIdea="narrow benchmark-driven topic"
        timeBudgetMonths="6"
        resourceLevel="student"
        preferredStyle="benchmark-driven"
        topicSessions={[
          {
            session_id: "session_1",
            created_at: "2026-03-25T00:00:00+00:00",
            updated_at: "2026-03-25T00:00:00+00:00",
            interest: "trustworthy multimodal reasoning in medical imaging",
            problem_domain: "medical AI",
            candidate_count: 1,
            recommended_candidate_id: "candidate_1",
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
          ],
          comparison_result: {
            dimensions: ["novelty"],
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
            ],
          },
          convergence_result: {
            recommended_candidate_id: "candidate_1",
            backup_candidate_id: "candidate_2",
            rationale: "Best balance.",
            manual_checks: ["Check benchmark availability."],
          },
          human_confirmations: [],
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
      />,
    );

    expect(screen.getByText("Research Topic Copilot")).toBeInTheDocument();
    expect(screen.getByText("Recent Survey")).toBeInTheDocument();
    expect(screen.getByText("Benchmark-Guided Narrow Task Definition")).toBeInTheDocument();
    expect(screen.getAllByText("candidate_1")).toHaveLength(2);
    expect(screen.getByText("Evidence coverage is medium.")).toBeInTheDocument();
    expect(screen.getByText("Recent Sessions")).toBeInTheDocument();
    expect(screen.getByText("1 topics")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Run Topic Agent" }));
    expect(onSubmit).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole("button", { name: "Refine Current Session" }));
    expect(onRefine).toHaveBeenCalledTimes(1);
  });
});
