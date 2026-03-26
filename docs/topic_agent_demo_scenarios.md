# Topic Agent Demo Scenarios

## Purpose

This document defines a small set of stable demo scenarios for manual validation, acceptance review, and project walkthroughs.

The goal is not to prove full coverage of all research-topic requests. The goal is to show that the current Topic Agent slice can:

- frame a topic request
- retrieve inspectable evidence
- organize a research landscape
- compare candidate directions
- converge to a recommendation
- surface human confirmation points

## How To Use This Document

For each scenario:

1. call `POST /api/topic-agent/explore`
2. inspect the response fields listed under `what to check`
3. compare the response against the expected behavior
4. if needed, continue with `POST /api/topic-agent/sessions/{session_id}/refine`

Recommended API surface:

- `POST /api/topic-agent/explore`
- `POST /api/topic-agent/sessions/{session_id}/refine`
- `GET /api/topic-agent/sessions/{session_id}`

## Scenario 1: Broad Medical Reasoning

### Request

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

### Why This Scenario Matters

This is the main broad-query stress case. It checks whether the system can stay in the modern medical-AI reasoning space without drifting into:

- legacy reasoning literature
- document-QA overfitting
- multimodal or image-grounded wording that the user never asked for

### What To Check

- `evidence_records`
  - should prefer modern medical AI benchmarks, LLM reasoning evaluations, or reasoning verification papers
- `landscape_summary.themes`
  - should not default to `document QA and report-centric reasoning`
- `candidate_topics[0].research_question`
  - should mention reasoning verification or benchmark validity
  - should not mention `image-grounded`
- `candidate_topics[1].research_question`
  - should not mention `document-centric clinical reasoning`
- `likely_gaps`
  - should prefer wording like:
    - reasoning gains
    - answer-pattern shortcuts
    - trustworthy evaluation

### Expected Outcome Shape

- a benchmark-driven candidate
- an applied transfer candidate
- a tooling / reproducibility candidate
- `candidate_2` is often the recommended path under student-scale applied constraints

## Scenario 2: Radiology VQA

### Request

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

### Why This Scenario Matters

This checks that the system can stay narrow and benchmark-oriented for a specific multimodal topic.

### What To Check

- `evidence_records`
  - should prefer `Med-VQA`, `VQA-RAD`, radiology VQA, or radiology benchmark evidence
- `landscape_summary.themes`
  - should include radiology VQA or image-grounded answer reliability
  - should not be dominated by generic hallucination wording
- `candidate_topics[0].research_question`
  - should mention radiology VQA benchmark slicing
- `candidate_topics[1].research_question`
  - should stay in radiology VQA method transfer wording

### Expected Outcome Shape

- candidate 1 emphasizes benchmark slicing and image-grounded answering
- candidate 2 emphasizes practical transfer under compute or annotation constraints

## Scenario 3: Hallucination And Grounding Evaluation

### Request

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

### Why This Scenario Matters

This checks whether evaluation-centric queries stay centered on:

- unsupported answers
- grounding faithfulness
- hallucination auditing

instead of drifting into generic document QA or broad overview wording.

### What To Check

- `evidence_records`
  - should include grounding, hallucination, evaluation, or benchmark evidence
- `landscape_summary.themes`
  - should include hallucination or grounding
- `candidate_topics[1].research_question`
  - should mention unsupported or weakly grounded answers
- `candidate_topics[2].open_questions`
  - should focus on audit workflow and reproducibility

### Expected Outcome Shape

- candidate 1 narrows the evaluation slice
- candidate 2 adapts an evaluation method under practical constraints
- candidate 3 focuses on audit tooling or reproducibility workflow

## Scenario 4: Clarification And Refine Loop

### Request

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

### Why This Scenario Matters

This checks whether the system surfaces missing information clearly enough for a user to continue with `refine`.

### What To Check

- `framing_result.missing_clarifications`
  - should include:
    - `time_budget`
    - `resource_level`
    - `preferred_style`
- `human_confirmations`
  - should explicitly ask for missing scope and feasibility assumptions
- `clarification_suggestions`
  - should include:
    - `field_key`
    - `prompt`
    - `reason`
    - `suggested_values`
    - `refine_patch`

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

### Expected Refine Behavior

- `missing_clarifications` becomes `[]`
- `clarification_suggestions` becomes `[]`
- `human_confirmations` shrinks to final recommendation checks instead of missing-input prompts

## Quick Acceptance Checklist

The current Topic Agent slice is behaving as intended if the reviewer can verify all of the following:

- broad queries stay in a modern medical-AI reasoning space
- radiology VQA queries stay narrow and benchmark-oriented
- hallucination / grounding queries stay evaluation-centric
- missing constraints trigger clarification suggestions
- completed constraints remove clarification suggestions
- candidate directions remain source-linked and comparable
