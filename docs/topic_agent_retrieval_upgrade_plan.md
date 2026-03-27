# Topic Agent Retrieval Upgrade Plan

## Goal

Upgrade Topic Agent retrieval from a primarily heuristic query-engineering pipeline into a staged retrieval architecture that can support:

- broader topic generalization
- better retrieval relevance under abstract or benchmark-heavy queries
- controlled latency for interactive use
- explicit diagnostics at each retrieval stage

The target architecture is not a one-shot rewrite. It is an incremental upgrade path from the current OpenAlex-centric implementation toward:

- multi-route candidate retrieval
- candidate fusion
- reranking
- evidence-driven downstream comparison and convergence

## Why This Upgrade Is Needed

The current retrieval slice is usable, but recent manual tests exposed two structural limits:

1. Query fan-out can dominate latency.
2. Pure query expansion plus heuristic filtering can drift toward weakly related benchmark or systems papers on abstract topics.

The system is therefore in a good position for a retrieval architecture upgrade:

- the current diagnostics are already strong enough to expose provider latency and query fan-out
- the current heuristic filters provide a useful safety baseline
- the downstream Topic Agent workflow is stable enough to absorb better evidence bundles

## Package Plan

### Package 1: Retrieval Structure Split

Objective:

- split retrieval into explicit stages without changing the public backend contract

Scope:

- factor provider retrieval into:
  - retrieval planning
  - cache lookup
  - candidate collection
  - normalization and final ranking
  - diagnostic result construction
- keep current behavior and current evidence diagnostics shape stable

Acceptance:

- existing retrieval behavior remains materially unchanged
- provider and API tests pass
- later hybrid and reranking work can be inserted without expanding a single monolithic `retrieve()` body

Status:

- completed

### Package 2: Multi-Route Candidate Retrieval

Objective:

- move from a single query-expansion route to a small set of explicit retrieval routes

Scope:

- keep the current OpenAlex route
- introduce route-level candidate grouping
- prepare route fusion instead of direct concatenation
- continue using current heuristic filters as a safety layer

Acceptance:

- route-level diagnostics show where candidates came from
- query fan-out remains bounded
- evidence quality does not regress on current stable query families

Status:

- in progress
- current sub-step completed:
  - OpenAlex query construction is now grouped into explicit retrieval routes:
    - `base`
    - `core_focus`
    - `alias`
    - `role_expansion`
  - per-query diagnostics now carry route information
  - cache keys still depend on the flattened query bundle, so the external contract stays stable
  - route-aware candidate fusion has been added in lightweight form:
    - records that are retrieved through multiple routes receive a controlled route-coverage bonus
    - higher-priority routes such as `base` and `core_focus` contribute more than `role_expansion`
    - a lightweight reciprocal-rank-style signal is now included for software-agent and code-repair query families, so route-local high-ranked candidates contribute more than low-ranked expansion-only neighbors
- still pending:
  - more explicit route-level fusion such as RRF or route-balanced candidate merging
  - explicit route-aware candidate balancing

### Package 3: Candidate Fusion And Reranking

Objective:

- improve generalization by separating recall from final ordering

Scope:

- add candidate fusion, likely via a simple and robust method such as reciprocal rank fusion
- add a reranking stage over a bounded candidate set
- shift topic-specific heuristics from primary ranking logic toward guardrails and fallback rules

Acceptance:

- weakly related benchmark/system papers are less likely to occupy top evidence slots
- repository repair and medical reasoning topic families do not regress
- more abstract queries become less brittle

### Package 4: Downstream Evidence-Driven Comparison

Objective:

- ensure comparison and convergence consume reranked evidence rather than mostly fixed candidate scaffolds

Scope:

- connect candidate generation more directly to reranked evidence clusters
- tighten evidence support accounting in comparison
- make convergence recommendations more explicitly evidence-driven

Acceptance:

- candidate support sets are cleaner
- recommendation rationale reflects reranked evidence rather than mostly template structure
- different query families produce more visibly differentiated comparison outputs

## Design Constraints

- Demo stability remains important.
- Backend response contracts should stay stable unless a real product need forces a change.
- Each package must remain independently testable and reversible.
- Latency may increase moderately if relevance improves materially. A 30s to 40s uncached retrieval budget is acceptable for deep retrieval, provided the output quality and generalization improve.

## Current Notes

Package 1 intentionally does not attempt to improve retrieval quality by itself. Its job is to create a staged implementation boundary so that hybrid retrieval and reranking can be introduced cleanly in later packages.
