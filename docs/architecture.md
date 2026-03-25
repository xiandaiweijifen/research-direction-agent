# Architecture

## Goal

Build a focused `Topic Agent` on top of the current local-first agent runtime so that a researcher can move from a vague interest or seed idea to a smaller set of evidence-backed candidate topics.

The goal is not to build a full academic platform. The system should stay narrow:

- frame the research problem
- retrieve evidence
- synthesize the landscape
- compare candidate directions
- support convergence
- preserve evidence chains and human checkpoints

## Product Position

The repository already contains a reusable runtime baseline:

- ingestion and local persistence
- retrieval with diagnostics
- planning and workflow orchestration
- persisted workflow runs
- evaluation and observability surfaces

The new architecture should reuse that baseline rather than replacing it.

## System Shape

The planned system shape is:

1. user submits a research interest, problem domain, or rough idea
2. the system extracts intent, constraints, and missing assumptions
3. retrieval workflows collect evidence from academic and supporting sources
4. synthesis workflows organize the evidence into a research landscape
5. the agent generates multiple candidate topic paths
6. comparison workflows score and explain tradeoffs
7. convergence support recommends next-best options and required manual checks
8. all intermediate reasoning remains attached to evidence, trace records, and confidence signals

## Architecture Layers

### 1. Input And Framing Layer

Responsible for:

- parsing free-form research intent
- extracting constraints such as time, compute, data access, and preferred style
- identifying missing clarifications
- normalizing the input into structured exploration goals

Typical output:

- framed problem statement
- search sub-questions
- explicit assumptions
- clarification-needed fields

### 2. Evidence Retrieval Layer

Responsible for:

- searching external academic and supporting sources
- retrieving source metadata and short evidence payloads
- ranking evidence by relevance and source tier
- exposing retrieval diagnostics and coverage gaps

Likely source categories:

- papers
- surveys
- benchmark pages
- dataset pages
- code repositories

This layer should inherit the existing retrieval discipline from the current project:

- keep diagnostics visible
- keep retrieval traceable
- avoid hidden unsupported claims

### 3. Evidence Store And Citation Layer

Responsible for:

- normalizing source metadata
- attaching source tier and confidence metadata
- keeping claim-to-evidence links
- storing snapshots of explored evidence for later review

Each important output should map back to evidence records with:

- title
- source type
- year
- identifier or URL
- source tier
- supporting rationale

### 4. Landscape Synthesis Layer

Responsible for:

- grouping the evidence into themes
- summarizing major methods and problem formulations
- identifying active areas, saturated areas, and possible gaps
- surfacing uncertainty and disagreement

This layer should not output final topic recommendations directly. Its role is to create a reliable map of the search space first.

### 5. Candidate Generation Layer

Responsible for:

- producing several candidate topic directions
- tying each candidate to evidence bundles
- making explicit what assumptions each candidate depends on

Candidate categories may include:

- gap-driven topics
- transfer or adaptation topics
- application-focused topics
- systems or tooling topics

The system should prefer 3 to 5 candidates rather than one single answer.

### 6. Comparison And Convergence Layer

Responsible for:

- comparing candidate directions across explicit dimensions
- recommending next-best options instead of pretending certainty
- showing reasons for deprioritized paths

Core comparison dimensions:

- novelty
- feasibility
- evidence strength
- data and benchmark availability
- implementation cost
- risk
- alignment with user constraints

### 7. Verification And Human Confirmation Layer

Responsible for:

- exposing evidence chains
- surfacing source conflicts
- marking unsupported inference
- requiring manual confirmation at high-risk decision points

Human confirmation should remain mandatory for:

- problem framing correctness
- whether constraints are complete
- whether a supposed gap is real
- whether a final candidate is feasible for the user
- final topic convergence

## Workflow Model

The recommended shape is workflow-based orchestration rather than a single-shot answer.

Core workflow:

1. `frame_problem`
2. `retrieve_evidence`
3. `synthesize_landscape`
4. `generate_candidates`
5. `compare_candidates`
6. `converge_recommendation`
7. `human_confirm`

Optional recovery loops:

- refine the search query
- narrow the scope
- replace low-quality evidence
- rerun comparison with updated constraints

## Evidence And Trust Rules

### Source Tiers

Tier A:

- peer-reviewed papers
- authoritative surveys
- official benchmark or dataset documentation

Tier B:

- arXiv preprints
- lab pages
- course notes
- credible technical blogs

Tier C:

- forums
- personal blogs
- unsupported model-only inference

### Conflict Rules

- prefer Tier A over Tier B and C when the same claim conflicts
- surface disagreement explicitly when strong sources disagree
- do not merge unsupported inference into factual output
- preserve recent versus classic-source distinctions

### Claim Rules

- every important recommendation should carry evidence
- weakly supported claims should be labeled as tentative
- unsupported synthesis must be visible as inference, not fact

## Reuse Of The Existing Repository

### Existing Parts To Reuse

- `backend/app/services/retrieval/`
  Retrieval logic, diagnostics patterns, and ranking interfaces

- `backend/app/services/agent/`
  Workflow orchestration, run persistence, trace recording, and recovery semantics

- `backend/app/services/llm/`
  Planner and synthesis support with fallback behavior

- `backend/app/services/evaluation/`
  Benchmark and report persistence patterns

- `frontend/src/components/`
  Console-oriented interaction model and inspection surfaces

### New Parts To Add

- `backend/app/api/routes/topic_agent.py`
- `backend/app/schemas/topic_agent.py`
- `backend/app/services/topic_agent/`
- `backend/app/services/topic_agent/source_adapters/`
- `frontend/src/components/TopicWorkspace.tsx`

Suggested service split:

- `framing_service.py`
- `evidence_retrieval_service.py`
- `citation_service.py`
- `landscape_service.py`
- `candidate_service.py`
- `comparison_service.py`
- `convergence_service.py`

## Runtime Session Model

Each topic-exploration session should be persisted similarly to current workflow runs.

Recommended session record fields:

- `session_id`
- `user_input`
- `structured_constraints`
- `evidence_records`
- `landscape_summary`
- `candidate_topics`
- `comparison_result`
- `convergence_result`
- `human_confirmations`
- `trace`
- `confidence_summary`

This keeps the system inspectable and makes evaluation easier.

## Frontend Direction

A narrow first UI is preferable.

Suggested workspace sections:

- `Explore`
  Input, framing result, clarifications, and retrieval status

- `Evidence`
  Retrieved sources, source tiers, citations, and conflicts

- `Compare`
  Candidate topics, tradeoffs, and convergence support

The UI should optimize for:

- evidence drill-down
- explicit uncertainty
- manual confirmation
- rerun after scope adjustment

## Evaluation Direction

The architecture should support evaluation at two levels.

### System-Level Quality

- retrieval quality
- citation completeness
- evidence-to-claim consistency
- comparison usefulness

### User-Level Outcome

- time to produce credible candidate topics
- quality of final topic shortlist
- expert judgment of evidence support
- user confidence in final selection

## Non-Goals For The First Phase

- full paper drafting
- autonomous topic selection without user review
- complete academic knowledge graph infrastructure
- large multi-agent orchestration before the evidence model is stable

## Practical First Milestone

The first milestone should prove that the system can do one thing well:

- accept a research interest
- retrieve evidence from a small number of source types
- produce 3 candidate topics
- compare them with explicit evidence
- recommend a next-best option with visible uncertainty

If that milestone is not convincing, the architecture should not expand yet.

The system is designed to make agent behavior inspectable:

- persisted workflow runs
- planner mode visibility
- planner latency tracking
- step-level trace events
- debug capture for workflow planning
- persisted evaluation reports
- recovery lineage and chain visualization

### Incremental Runtime Maturity

The project is intentionally growing from a capable local runtime toward a more production-like agent system.

Current maturity is strongest in:

- retrieval
- routing
- local tool execution
- planner integration
- workflow traceability
- recovery semantics and lineage
- evaluation dashboards and persisted reports

The next maturity steps are:

- more general rerun policies
- more explicit runtime policies
- real external adapter boundaries
- stronger persistence abstractions
- tighter metric packaging and project documentation
