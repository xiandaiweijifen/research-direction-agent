# Topic Agent Acceptance Plan

## Goal

Define how to judge whether the planned `Topic Agent` is useful, credible, and sufficiently scoped.

The acceptance focus is not feature count. The acceptance focus is:

- scope control
- evidence quality
- explainability
- decision usefulness

## 1. Acceptance Questions

The design should answer these questions clearly:

1. Does the system help a user narrow a research direction instead of broadening it endlessly?
2. Can the user inspect why a candidate topic was proposed?
3. Are important claims backed by identifiable sources?
4. Does the system surface uncertainty and conflict rather than hiding it?
5. Does the workflow leave room for human confirmation at the right points?

## 2. First-Phase Scope To Accept

The first phase should be considered acceptable if it supports:

- one structured topic-exploration input flow
- one evidence retrieval flow
- one landscape synthesis flow
- 3 to 5 candidate topics
- one comparison view
- one convergence recommendation view
- citation and source-tier inspection

The first phase should not be judged by:

- full academic coverage
- writing quality for long-form outputs
- number of integrated source providers
- multi-agent complexity

## 3. Evidence Acceptance Rules

The output is only acceptable if:

- each candidate topic has supporting evidence
- key claims are linked to sources
- source tier is visible
- conflicting evidence is surfaced explicitly
- unsupported inference is labeled as tentative

The output is not acceptable if:

- the recommendation reads confidently but has weak evidence
- the system hides disagreement across sources
- candidate-topic differences are vague or repetitive

## 4. Human Confirmation Acceptance Rules

The system should force or strongly prompt confirmation for:

- problem framing
- constraint completeness
- final convergence choice

The system should allow a user to:

- reject a candidate topic
- rerun with narrower constraints
- inspect source details before accepting recommendations

## 5. Evaluation Plan

### 5.1 Offline Evaluation

Build a small benchmark set of topic-exploration tasks.

Each task should contain:

- user input
- expected evidence types
- expected candidate-topic diversity
- expected comparison dimensions

Suggested offline metrics:

- high-value source hit rate
- citation completeness rate
- evidence coverage per candidate
- duplicate-candidate rate
- comparison-dimension completeness

### 5.2 Expert Review

Ask domain experts to score outputs on:

- usefulness
- credibility
- evidence quality
- clarity of recommendation
- realism of proposed topics

### 5.3 User Outcome Evaluation

Compare two flows:

- user without Topic Agent
- user with Topic Agent

Measure:

- time to produce 3 candidate topics
- time to reach a final shortlist
- self-reported decision clarity
- expert judgment of final shortlist quality

## 6. Demo Acceptance Criteria

A first demo is acceptable if an observer can see:

- how input is framed
- which evidence was retrieved
- why 3 candidate topics were proposed
- how those candidates differ
- what the system recommends next
- where the user still must decide manually

If the observer mainly sees a polished summary without an evidence chain, the demo is not acceptable.

## 7. Engineering Acceptance Criteria

The implementation direction is acceptable if:

- workflows are explicit rather than hidden in one large prompt
- evidence records are persisted or reconstructable
- retrieval and comparison diagnostics are inspectable
- evaluation can be rerun locally
- the design can start small and grow without re-architecting immediately

## 8. Stop Conditions

Do not expand scope if the first milestone still cannot reliably do these:

- produce distinct candidate topics
- attach evidence to claims
- expose uncertainty clearly
- help users narrow rather than drift
