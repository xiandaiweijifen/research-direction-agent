# Topic Agent MVP Plan

## Goal

Define a concrete first milestone for `Topic Agent` so the project can move from high-level design into implementation without expanding into a broad academic platform.

The MVP should prove one thing clearly:

The system can help a user narrow a vague research interest into a small set of evidence-backed candidate topics with explicit comparison and visible uncertainty.

## 1. MVP Product Promise

The MVP is not a full research assistant.

The MVP should help a user:

- enter a research interest or seed idea
- receive a structured problem framing
- retrieve and inspect supporting evidence
- see 3 candidate topic directions
- compare those directions using explicit dimensions
- get a recommended next-best option and required manual checks

If the system cannot do those six things reliably, the MVP should not expand further.

## 2. MVP Scope

### In Scope

- one topic exploration input flow
- one evidence retrieval workflow
- one landscape synthesis workflow
- one candidate generation workflow
- one comparison and convergence workflow
- source metadata and citation display
- source-tier labeling
- explicit uncertainty and conflict notes
- manual confirmation checkpoints
- persisted topic exploration sessions

### Out Of Scope

- full paper drafting
- experiment planning or execution
- personalized long-term academic memory
- broad multi-agent orchestration
- large-scale knowledge graph construction
- complex collaboration workflows
- recommendation based on private citation libraries

## 3. Target User For The MVP

The MVP should optimize for one primary user:

- a graduate student or early-stage researcher who has a broad interest area but has not yet formed a stable research topic

This user usually needs:

- problem framing
- quick landscape understanding
- candidate options
- evidence-backed narrowing support

## 4. Core User Journey

### Step 1: Input

The user submits:

- research interest
- optional problem domain
- optional seed idea
- optional constraints

Example:

```json
{
  "interest": "trustworthy multimodal reasoning in medical imaging",
  "problem_domain": "medical AI",
  "seed_idea": "I want to explore whether multimodal LLMs can provide clinically useful explanations",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "benchmark-driven"
  }
}
```

### Step 2: Problem Framing

The system returns:

- normalized topic statement
- extracted constraints
- missing clarifications
- search sub-questions

### Step 3: Evidence Retrieval

The system retrieves and groups evidence from a small number of source types.

First-phase source types:

- papers
- surveys
- benchmark or dataset pages
- code repositories

### Step 4: Landscape Synthesis

The system organizes the evidence into:

- major themes
- active methods
- likely gaps
- saturated areas

### Step 5: Candidate Generation

The system produces 3 candidate topics.

Each candidate should include:

- working title
- core research question
- why it may matter
- why it may be feasible
- key supporting evidence
- major risk or uncertainty

### Step 6: Comparison And Convergence

The system compares candidates using:

- novelty
- feasibility
- evidence strength
- data availability
- implementation cost
- risk

Then it provides:

- one recommended next-best option
- one backup option
- manual checks before final commitment

## 5. Narrow Workflow For The MVP

The MVP should use a fixed, inspectable workflow:

1. `frame_problem`
2. `retrieve_evidence`
3. `synthesize_landscape`
4. `generate_candidates`
5. `compare_candidates`
6. `converge_recommendation`

This should remain workflow-based, not single-shot.

The workflow should also support one controlled loop:

- `refine_scope`

This loop is triggered when:

- evidence is too weak
- the scope is too broad
- candidates are repetitive

## 6. MVP Data Model

### 6.1 Session Record

Suggested persisted session structure:

```json
{
  "session_id": "string",
  "created_at": "iso_timestamp",
  "updated_at": "iso_timestamp",
  "user_input": {},
  "framing_result": {},
  "evidence_records": [],
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "human_confirmations": [],
  "trace": [],
  "confidence_summary": {}
}
```

### 6.2 Evidence Record

Each evidence record should include at minimum:

```json
{
  "source_id": "string",
  "title": "string",
  "source_type": "paper|survey|benchmark|dataset|code",
  "source_tier": "A|B|C",
  "year": 2025,
  "authors_or_publisher": "string",
  "identifier": "doi|arxiv|url|repo",
  "url": "string",
  "summary": "string",
  "relevance_reason": "string"
}
```

### 6.3 Candidate Topic

Each candidate topic should include:

```json
{
  "candidate_id": "string",
  "title": "string",
  "research_question": "string",
  "positioning": "gap-driven|transfer|application|systems",
  "novelty_note": "string",
  "feasibility_note": "string",
  "risk_note": "string",
  "supporting_source_ids": ["source_1", "source_2"],
  "open_questions": ["string"]
}
```

## 7. MVP API Surface

The first version can stay small.

### POST `/api/topic-agent/explore`

Purpose:

- create a new topic exploration session
- run the full MVP workflow

Request:

```json
{
  "interest": "string",
  "problem_domain": "string",
  "seed_idea": "string",
  "constraints": {}
}
```

Response:

```json
{
  "session_id": "string",
  "framing_result": {},
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "confidence_summary": {},
  "trace": []
}
```

### GET `/api/topic-agent/sessions`

Purpose:

- list recent exploration sessions

### GET `/api/topic-agent/sessions/{session_id}`

Purpose:

- inspect a full session with evidence and trace

### POST `/api/topic-agent/sessions/{session_id}/refine`

Purpose:

- rerun the workflow with narrower or revised constraints

## 8. MVP UI Plan

The MVP UI should stay narrower than the current generic console.

Suggested first view: `Topic Workspace`

### Section A: Explore

Contains:

- input form
- extracted framing
- missing clarifications
- run button

### Section B: Evidence

Contains:

- evidence list
- source tier labels
- source type filters
- per-record detail panel
- conflict and uncertainty notes

### Section C: Compare

Contains:

- 3 candidate topic cards
- comparison matrix
- recommendation panel
- manual confirmation checklist

## 9. MVP Source Strategy

The MVP should not try to connect to every academic source.

Recommended first implementation strategy:

- start with a bounded source adapter layer
- allow a mock or local evidence mode first
- design the output model so real connectors can replace mock retrieval later

The source strategy should be accepted only if:

- evidence records are normalized
- source tiering is possible
- citation display is consistent

## 10. MVP Confidence Model

The MVP should not output a single opaque confidence score.

Instead it should expose a small confidence summary:

- `evidence_coverage`
- `source_quality`
- `candidate_separation`
- `conflict_level`

Example:

```json
{
  "evidence_coverage": "medium",
  "source_quality": "medium_high",
  "candidate_separation": "high",
  "conflict_level": "low"
}
```

## 11. MVP Acceptance Criteria

The MVP is acceptable if it can consistently show:

- a clear problem framing
- visible evidence behind candidate topics
- 3 meaningfully different candidate topics
- a comparison that is not repetitive or generic
- a recommendation with explicit limitations
- at least one clear human confirmation step

The MVP is not acceptable if:

- candidates are near duplicates
- recommendations are unsupported
- the UI hides source details
- the system appears authoritative while evidence is weak

## 12. Suggested Implementation Order

1. define schemas and persisted session model
2. create topic-agent route and stub workflow
3. implement mock evidence retrieval and evidence records
4. implement landscape and candidate generation stubs
5. implement comparison and convergence output
6. build a minimal Topic Workspace UI
7. add session inspection and refine flow
8. add evaluation fixtures for MVP tasks

## 13. First Demo Scenario

Input:

- interest: trustworthy multimodal reasoning in medical imaging
- constraints: 6 months, student resources, benchmark-driven

Expected demo output:

- one framed problem summary
- 8 to 15 evidence records
- one landscape summary
- 3 candidate topics
- one comparison matrix
- one recommended topic with backup option
- one manual verification checklist

## 14. Expansion Gates After MVP

Do not expand to broader features until the MVP proves:

- the narrowing workflow is useful
- evidence links are trustworthy enough
- candidate diversity is real
- users understand why one candidate is recommended over another

## 15. Demo And Acceptance References

Use these documents when validating the current MVP slice:

- [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- [topic_agent_acceptance_walkthrough.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance_walkthrough.md)
