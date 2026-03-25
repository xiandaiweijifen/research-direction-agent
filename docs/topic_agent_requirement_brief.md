# Topic Agent Requirement Brief

## Original Requirement

Please design a research-topic copilot subsystem, `Topic Agent`, to help researchers start from a research interest, problem domain, or seed idea and complete:

- literature retrieval
- landscape exploration
- candidate direction comparison
- convergence and decision support

The final goal is to provide research-topic recommendations.

Important constraints:

1. The output format, page structure, and system architecture are not pre-specified.
2. The solution may use a single agent, workflow orchestration, multi-agent design, RAG, a knowledge graph, or another approach.
3. The system does not need to be fully implemented, but the design logic and acceptance logic must be clear.

The design should at minimum explain:

1. target users and core tasks
2. system boundary and capability structure
3. how user input and system output are organized
4. the core workflow for retrieval, synthesis, comparison, and convergence
5. data sources, citation mechanism, source grading, and conflict handling rules
6. how users validate results and which steps require human confirmation
7. the evaluation plan and how to judge whether the system truly helps topic selection
8. optional demo, prototype, pseudocode, or interface definition

The acceptance focus is:

1. scope narrowing instead of building a large all-in-one platform
2. clear evidence chain, result verification, and credibility handling
3. engineering and product thinking

## Where This Requirement Is Reflected In The Repository

### Design Logic

- [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
- [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)

### Current Implementation Slice

- [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py)
- [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py)
- [topic_agent_runtime.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/topic_agent_runtime.py)

### Current Progress Tracking

- [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)

## Current Completion Judgment

For the current design-and-MVP scope, the original requirement is approximately `80% to 85%` covered.

### Already Covered Well

- target users and core tasks are clearly defined
- system scope is intentionally narrowed to a focused topic-exploration workflow
- input and output are structured around framing, evidence, landscape, candidates, comparison, and convergence
- retrieval and synthesis workflow is explicit rather than hidden in a single prompt
- source metadata, source tiers, fallback diagnostics, cache diagnostics, and supporting evidence links are implemented
- evaluation and acceptance thinking are documented
- the implementation direction shows clear engineering and product decomposition

### Covered In Design More Than In Product

- human confirmation checkpoints
- explicit user validation loops before final convergence
- stronger source-conflict surfacing when good sources disagree

### Not Yet Fully Covered

- end-user confirmation UX that actively gates framing and final recommendation acceptance
- richer conflict modeling and contradiction summaries across sources
- a broader benchmark-based acceptance harness for multiple topic classes
- a more formal demo or prototype narrative tying the design docs to a user-facing walkthrough

## Practical Must-Have Reading Of The Requirement

The most useful way to interpret the original requirement is to separate:

- what must exist in the minimal closed loop
- what should exist for a stronger submission
- what is explicitly not required for the current phase

### Must-Have For The Minimal Closed Loop

- a clear structured input entry for:
  - research interest or problem domain
  - seed idea
  - practical constraints
- an explicit framing or clarification step showing task-modeling awareness
- real evidence retrieval from at least one external or curated scholarly source
- a landscape synthesis step that organizes evidence into sub-directions instead of only summarizing papers
- 2 to 3 candidate research directions with explicit comparison dimensions
- a convergence recommendation that explains:
  - which direction is preferred
  - why
  - what risks remain
  - what still needs human judgment
- visible source references and evidence links

### Should-Have For A Stronger Submission

- explicit human confirmation checkpoints
- source grading and conflict-handling rules surfaced to the user
- a demo walkthrough with one end-to-end example
- clearer separation between:
  - source-backed facts
  - system synthesis
  - tentative inference

### Not Required For The Current Phase

- a large multi-agent architecture
- a heavy frontend or polished product shell
- a full knowledge graph
- a large-scale production retrieval platform
- a complete academic-workflow assistant

## Recommended Reading Order For Reviewers

1. Read [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md) for the product and system logic.
2. Read [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md) for the acceptance criteria.
3. Read [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md) for the implementation status.
4. Inspect [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py) and [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py) for the current backend slice.

## Practical Acceptance View

If the current Topic Agent slice is judged against the original requirement, the most defensible claim is:

- the focused workflow design is clear
- the evidence chain is much clearer than at the start
- the system already demonstrates scope-control and engineering decomposition
- the remaining work is mainly around explicit human confirmation, conflict handling, and product-layer acceptance polish rather than basic retrieval workflow viability
