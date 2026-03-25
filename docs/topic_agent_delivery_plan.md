# Topic Agent Delivery Plan

## Purpose

This document turns the Topic Agent requirement into a phased development checklist.

The goal is to keep the project focused on a convincing, testable topic-selection copilot instead of drifting into a large academic platform.

## Phase 1: Must-Have Closed Loop

These items define the minimum implementation that should exist for the Topic Agent to feel like a real topic-selection copilot.

### 1. Structured Input Entry

The user should be able to provide at least:

- research interest or problem domain
- seed idea
- constraints:
  - time
  - resource level
  - preferred style such as theoretical or applied

Current status:

- implemented in backend request schema and current API workflow

### 2. Clarification And Framing

The system should not answer from a vague sentence without showing a framing step.

Minimum acceptable behavior:

- normalize the topic
- extract constraints
- expose missing clarifications
- produce search sub-questions

Current status:

- partially implemented through framing and missing-clarification fields
- not yet implemented as an explicit user confirmation step

### 3. Evidence Retrieval

The system must retrieve from real or at least inspectable sources rather than relying only on model memory.

Minimum acceptable behavior:

- retrieve evidence records
- preserve citation metadata
- expose source tier and provider diagnostics

Current status:

- implemented with `openalex` primary retrieval and `arxiv` fallback

### 4. Landscape Organization

The system must turn retrieved evidence into a direction map, not just a paper summary.

Minimum acceptable behavior:

- major themes
- representative methods
- likely gaps
- saturated areas

Current status:

- implemented through `landscape_summary`

### 5. Candidate Path Comparison

The system should output 2 to 3 candidate directions and compare them on fixed dimensions.

Minimum acceptable behavior:

- candidate topics
- supporting evidence ids
- comparison dimensions such as:
  - novelty
  - feasibility
  - evidence strength
  - data availability
  - implementation cost
  - risk

Current status:

- implemented

### 6. Convergence Recommendation

The system should recommend a next-best direction rather than only listing evidence.

Minimum acceptable behavior:

- recommend a preferred candidate
- explain why it was preferred
- note manual checks or unresolved risks

Current status:

- implemented

### 7. Source Visibility

The output should expose references and evidence links clearly enough for a user to verify them.

Minimum acceptable behavior:

- evidence list
- source ids
- identifiers or URLs
- source tier
- candidate-to-evidence linkage

Current status:

- implemented

## Phase 2: Should-Have Product And Trustworthiness Additions

These items are not required to prove the core design, but they materially improve acceptance quality.

### 1. Explicit Human Confirmation Points

- confirm framing and constraints
- confirm which comparison dimensions matter most
- confirm or reject final convergence

Current status:

- documented in design
- not yet enforced in the product flow

### 2. Source Conflict Handling

- surface disagreement across strong sources
- avoid flattening conflicting claims into a single confident answer
- distinguish source fact from system inference

Current status:

- partially covered through source-tier design and confidence summaries
- not yet implemented as explicit conflict summaries

### 3. Demo Walkthrough

- one end-to-end scenario
- inspectable evidence chain
- candidate comparison
- recommended direction
- manual confirmation points

Current status:

- partially available through manual API runs
- not yet packaged as a formal walkthrough

## Phase 3: Not-Now Items

These are explicitly lower priority and should not drive the current implementation.

- multi-agent orchestration for its own sake
- complex frontend flows
- full knowledge graph infrastructure
- large-scale production search and indexing
- full proposal writing or experiment planning automation

## Current Best-Fit Completion View

If measured against this phased plan:

- Phase 1 is mostly complete
- Phase 2 is partially complete
- Phase 3 is intentionally deferred

The current implementation is best described as:

- a focused backend Topic Agent slice with a credible evidence-driven workflow
- a backend minimum viable closed loop that already supports end-to-end exploratory runs
- strong enough for design review and manual acceptance discussion
- still needing explicit confirmation UX and stronger conflict handling before it can be called fully product-complete
