# Topic Agent Initial Design

## 1. Product Goal

Design a focused research-topic copilot that helps a researcher move from a vague interest or rough idea to a smaller set of credible candidate topics with explicit evidence and comparison support.

The system should not attempt to automate the full academic workflow. It should help with topic exploration, comparison, and convergence.

## 2. Target Users

Primary users:

- graduate students who have a domain interest but no clear topic
- early-stage researchers who need help narrowing several possible directions

Core jobs to be done:

- clarify what exactly is worth researching
- understand the current landscape quickly
- compare multiple topic paths instead of committing too early
- identify evidence gaps and validation steps before deciding

## 3. Scope Boundaries

In scope:

- problem framing
- literature and evidence retrieval
- landscape synthesis
- candidate topic generation
- candidate comparison
- convergence support
- citation and confidence presentation

Out of scope for the first phase:

- full paper writing
- experiment orchestration
- full reference manager replacement
- long-term academic knowledge graph platform

## 4. Proposed Capability Structure

### 4.1 Problem Framing

Input normalization for:

- research interest
- problem domain
- seed idea
- constraints such as time, data, compute, and preferred style

Output:

- framed research question space
- search sub-questions
- explicit assumptions and missing constraints

### 4.2 Evidence Retrieval

Retrieve from:

- papers
- surveys
- benchmarks
- datasets
- code repositories

Output:

- source records with metadata
- ranked evidence bundles
- source-grade annotations

### 4.3 Landscape Synthesis

Organize evidence into:

- major themes
- representative methods
- common evaluation settings
- active versus saturated topics
- promising open questions

### 4.4 Candidate Topic Generation

Produce several candidate directions, for example:

- gap-driven topic
- method-transfer topic
- domain-application topic
- systems or tooling topic

### 4.5 Comparison And Convergence

Compare candidates across:

- novelty
- feasibility
- evidence support
- data and benchmark availability
- implementation cost
- risk
- match with user constraints

Output:

- comparison matrix
- recommended next-best options
- reasons for deprioritized options

## 5. Workflow Design

Recommended core workflow:

1. `frame_problem`
2. `retrieve_evidence`
3. `synthesize_landscape`
4. `generate_candidates`
5. `compare_candidates`
6. `converge_recommendation`
7. `human_confirm`

This is a better fit than a single-shot response because every stage can preserve evidence, diagnostics, and intermediate decisions.

## 6. Data Sources And Evidence Rules

### 6.1 Source Tiers

Tier A:

- peer-reviewed papers
- authoritative surveys
- official benchmark or dataset documentation

Tier B:

- arXiv preprints
- lab pages
- course notes
- technical blogs from credible organizations

Tier C:

- forum discussion
- personal blogs
- unsupported model inference

### 6.2 Citation Rules

Each important claim should carry:

- title
- source type
- authors or publisher
- year
- identifier or URL
- short supporting rationale
- source tier

### 6.3 Conflict Handling

- prefer Tier A over Tier B and C
- when high-quality sources disagree, surface disagreement explicitly
- do not collapse unsupported inference into fact
- mark stale but influential sources differently from recent evidence

## 7. Human Verification Points

The system should require user confirmation for:

- problem framing correctness
- whether constraints are complete
- whether a candidate is realistically feasible
- whether a reported gap is truly a gap rather than a retrieval miss
- final topic convergence

The system should expose:

- evidence behind each candidate topic
- source-level drill-down
- confidence and conflict notes
- manual rejection and rerun entrypoints

## 8. Evaluation Plan

### 8.1 System Quality

- retrieval precision for high-value sources
- evidence coverage per candidate topic
- citation completeness rate
- evidence-to-claim consistency
- comparison usefulness judged by reviewers

### 8.2 User Outcome

- time to produce 3 credible candidate topics
- perceived decision clarity
- expert rating of candidate-topic quality
- user willingness to continue with a recommended topic

### 8.3 Acceptance Signals

The system is useful if it helps users:

- narrow scope faster
- justify choices with stronger evidence
- identify risks earlier
- reduce low-value reading and topic drift

## 9. Engineering Direction Based On The Current Repository

Suggested reuse of the existing codebase:

- extend retrieval into academic-source retrieval
- evolve tool adapters into paper search, survey lookup, benchmark lookup, and dataset lookup
- reuse workflow persistence for topic exploration sessions
- reuse evaluation infrastructure for topic-selection benchmarks
- reuse trace and diagnostics surfaces for evidence-chain inspection

Suggested new modules:

- `backend/app/services/topic_agent/`
- `backend/app/schemas/topic_agent.py`
- `backend/app/api/routes/topic_agent.py`
- `frontend/src/components/TopicWorkspace.tsx`

## 10. Suggested First Demo

User input:

- interest: "trustworthy multimodal reasoning in medical imaging"
- constraints: student budget, 6 months, benchmark-driven

Demo output:

- a landscape summary
- 3 candidate topics
- a comparison matrix
- a recommended next step
- supporting citations and risks
