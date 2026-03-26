# Topic Agent Acceptance Walkthrough

## Purpose

This document provides a reviewer-friendly walkthrough for the current Topic Agent slice.

It is designed for:

- demo sessions
- milestone reviews
- acceptance discussions
- final submission walkthroughs

The goal is to show the current system as a focused, evidence-driven topic-selection copilot rather than a generic academic assistant.

## What The Reviewer Should Understand

By the end of the walkthrough, a reviewer should be able to answer:

1. what the system takes as input
2. how it narrows the topic instead of expanding it endlessly
3. where the evidence comes from
4. how the system turns evidence into candidate directions
5. how the recommendation is justified
6. where human confirmation still matters

## Recommended Walkthrough Order

1. show one `explore` request
2. inspect framing and missing clarifications
3. inspect retrieved evidence and diagnostics
4. inspect landscape synthesis
5. inspect candidate topics and comparison result
6. inspect convergence result
7. inspect human confirmations and clarification suggestions
8. optionally show one `refine` cycle

## Walkthrough A: Broad Medical Reasoning

### Input

```json
{
  "interest": "medical reasoning",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

### What To Highlight

- the system does not treat this as a vague free-form chat request
- it normalizes the topic and extracts constraints
- evidence retrieval should prioritize modern medical AI reasoning benchmarks
- broad-query wording should stay in:
  - reasoning verification
  - benchmark validity
  - answer-pattern shortcuts
- it should not drift into:
  - legacy reasoning literature
  - document-centric wording
  - image-grounded wording that the user never asked for

### Acceptance Signal

This walkthrough is successful if the reviewer can see that a broad topic still converges to:

- a benchmark-slice path
- an applied transfer path
- a tooling / evaluation path

with visible supporting evidence for each candidate.

## Walkthrough B: Narrow Radiology VQA

### Input

```json
{
  "interest": "trustworthy visual question answering in radiology",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow and feasible benchmark-oriented topic.",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

### What To Highlight

- evidence should favor `Med-VQA`, `VQA-RAD`, or radiology VQA papers
- landscape themes should stay narrow and benchmark-oriented
- candidate wording should emphasize:
  - benchmark slicing
  - image-grounded reliability
  - practical transfer under constrained resources

### Acceptance Signal

This walkthrough is successful if the reviewer can see that the system can stay narrow and topic-specific without collapsing into a generic medical AI overview.

## Walkthrough C: Evaluation-Centric Hallucination Query

### Input

```json
{
  "interest": "hallucination detection and grounding evaluation for multimodal medical reasoning",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow evaluation-focused research topic.",
  "constraints": {
    "time_budget_months": 5,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

### What To Highlight

- evidence should favor grounding, hallucination, faithfulness, or evaluation records
- candidate directions should stay evaluation-centric
- the system should not drift into broad document QA or generic multimodal overviews

### Acceptance Signal

This walkthrough is successful if the reviewer can see that:

- candidate 1 narrows the evaluation slice
- candidate 2 proposes a practical evaluation transfer path
- candidate 3 focuses on audit workflow or reproducibility support

## Walkthrough D: Clarification And Refine Loop

### Initial Input

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

### What To Highlight On First Response

- `missing_clarifications`
- `human_confirmations`
- `clarification_suggestions`

The important point is that the system does not silently continue as if missing constraints do not matter.

### Refine Request

```json
{
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

### What To Highlight On Refine Response

- `missing_clarifications` becomes empty
- `clarification_suggestions` becomes empty
- `human_confirmations` shrinks to final decision checks

### Acceptance Signal

This walkthrough is successful if the reviewer can see a real clarification loop rather than a one-shot answer generator.

## What Reviewers Should Be Told Explicitly

### What Is Already Strong

- focused scope
- inspectable workflow
- evidence-linked candidates
- stable query-specific behavior on key demo classes
- explicit confidence and diagnostics surfaces

### What Is Still Partial

- explicit source-conflict summaries
- end-user confirmation UX in a richer frontend flow
- broader acceptance benchmark harness

### What Is Intentionally Out Of Scope

- full academic workflow automation
- proposal writing
- experiment execution
- large multi-agent orchestration
- heavy product shell or complex knowledge graph infrastructure

## Recommended Supporting Documents

Use these documents alongside the walkthrough:

1. [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
2. [topic_agent_mvp.md](/d:/project/research-topic-copilot/docs/topic_agent_mvp.md)
3. [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)
4. [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
5. [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)
