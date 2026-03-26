# Topic Agent Demo Completion Plan

## Goal

Finish a convincing Topic Agent demo on top of the now-stabilized backend slice.

This plan assumes:

- the backend contract is stable enough for demo use
- backend retrieval and candidate-generation tuning is paused
- the remaining work is mainly frontend composition, walkthrough quality, and demo readiness

## Demo Completion Definition

The demo is complete when a reviewer can:

1. enter a topic request from the UI
2. inspect the recommended direction and backup direction quickly
3. inspect candidate directions with visible supporting evidence
4. inspect trust and diagnostics without needing raw JSON
5. load a recent session and understand what changed

## Current Backend Assumptions

The frontend can now rely on:

- `POST /api/topic-agent/explore`
- `GET /api/topic-agent/sessions`
- `GET /api/topic-agent/sessions/{session_id}`
- `POST /api/topic-agent/sessions/{session_id}/refine`

And on these response surfaces being present:

- framing
- evidence
- landscape
- candidates
- comparison
- convergence
- evidence presentation
- diagnostics
- session history

## Demo Priorities

### P0

- recommendation summary is readable at a glance
- candidate cards are readable and visibly linked to evidence
- evidence browser supports quick source inspection
- trust panel shows facts, synthesis, tentative inference, and diagnostics in clear sections
- session history is easy to browse without overwhelming the page

### P1

- recommendation and trust sections read well in both English and Chinese
- comparison changes between sessions are visible without needing raw JSON
- internal ids and backend-heavy labels are visually softened

### P2

- polish animation and transition details
- deeper interaction patterns for evidence exploration
- richer comparative narrative across multiple sessions

## Suggested Execution Order

1. Verify frontend types against the current backend payload.
2. Verify that the Topic Agent tab uses the feature page as the main entry point.
3. Tighten the top-of-page reading order:
   - input
   - recommendation
   - candidates
   - evidence
   - trust
4. Make session history feel recent-run oriented instead of archival.
5. Add a lightweight demo walkthrough cue in the UI copy where useful.
6. Run one final manual pass on the chosen demo scenarios.

## Recommended Demo Scenarios

Use one topic from each class:

- broad medical reasoning
- narrow radiology VQA
- hallucination / grounding evaluation
- bug-fixing or software-agent topic

Recommended non-medical scenario:

```json
{
  "interest": "llm agents for automated bug fixing",
  "problem_domain": "software engineering",
  "seed_idea": "I want a feasible applied topic on reproducible evaluation for low-cost bug-fixing agents.",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

## Non-Goals For This Demo Pass

Do not expand scope into:

- another backend retrieval-quality pass
- a new candidate-generation architecture
- full source-conflict modeling
- large new backend schema changes

If a backend issue is found, only fix it if it blocks the demo directly.

## Exit Checklist

- frontend Topic Agent view is usable without reading raw JSON
- recommendation, evidence, and trust surfaces appear in the intended order
- recent-session loading works
- one medical and one non-medical demo topic both look acceptable
- docs are aligned with the freeze point and demo story
