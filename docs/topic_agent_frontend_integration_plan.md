# Topic Agent Frontend Integration Plan

## 1. Goal

Integrate the current Topic Agent backend workflow into a frontend demo surface that feels like a focused product flow rather than an internal developer console.

This step does not change backend semantics. It reorganizes the frontend so the existing Topic Agent capability can be demonstrated clearly.

For the current phase, backend quality iteration is intentionally deferred. The goal is to complete a clear and credible Topic Agent presentation layer on top of the stabilized backend slice rather than continue retrieval or synthesis tuning.

Note: a staged retrieval architecture upgrade is now being tracked separately in `docs/topic_agent_retrieval_upgrade_plan.md`. Package 1 keeps the frontend contract stable; later retrieval packages may improve evidence quality without requiring a full frontend redesign.

## 2. Current Frontend Assessment

The current frontend already has Topic Agent API wiring:

- `frontend/src/api.ts`
- `frontend/src/types.ts`
- `frontend/src/components/TopicWorkspaceV2.tsx`
- `frontend/src/App.tsx`

But the current shape is still a console-style implementation:

- `App.tsx` owns too much Topic Agent state directly
- `TopicWorkspaceV2.tsx` is a large all-in-one component
- frontend `types.ts` does not yet reflect the full backend Topic Agent response
- the current Topic Agent screen mixes input, evidence browsing, comparison, and trace inspection in a single large surface

For a demo-first frontend, this should be split into clearer product sections.

## 3. Integration Principles

### 3.1 Keep The Backend Contract Stable

The frontend should consume the existing endpoints as they are:

- `POST /api/topic-agent/explore`
- `GET /api/topic-agent/sessions`
- `GET /api/topic-agent/sessions/{session_id}`
- `POST /api/topic-agent/sessions/{session_id}/refine`

No backend API redesign is required for the first frontend integration pass.

For the current delivery pass, treat the backend response contract as stable unless a frontend-blocking bug is found.

### 3.2 Move Topic-Agent Logic Out Of `App.tsx`

`App.tsx` should remain the shell and view switcher.

Topic Agent state, loading, session handling, and display logic should move into a dedicated feature slice.

### 3.3 Separate Demo Layers

The frontend should distinguish:

- user input and refinement
- recommendation summary
- evidence and citations
- candidate comparison
- trust and diagnostics

This is important because the backend already exposes these layers separately.

## 4. Recommended File Plan

### 4.1 Files To Keep

- `frontend/src/App.tsx`
  - keep as the global shell and tab-level entry point
- `frontend/src/api.ts`
  - keep temporarily as the shared API client entry
- `frontend/src/types.ts`
  - keep temporarily, but extend in the first integration step

### 4.2 Files To De-Emphasize

- `frontend/src/components/TopicWorkspaceV2.tsx`
  - do not continue expanding this as the long-term demo component
  - keep it only as a temporary compatibility wrapper during the transition

### 4.3 New Topic-Agent Feature Structure

Recommended new files:

- `frontend/src/features/topic-agent/TopicAgentDemoPage.tsx`
  - top-level Topic Agent demo page
  - receives only high-level props or owns feature-local composition

- `frontend/src/features/topic-agent/hooks/useTopicAgent.ts`
  - owns frontend state for:
    - current form input
    - current session result
    - comparison session result
    - session history
    - loading and error states
  - moves Topic Agent logic out of `App.tsx`

- `frontend/src/features/topic-agent/components/TopicAgentInputPanel.tsx`
  - input form
  - run explore
  - refine current session

- `frontend/src/features/topic-agent/components/TopicAgentSessionHistory.tsx`
  - recent sessions
  - load session
  - compare session

- `frontend/src/features/topic-agent/components/TopicAgentRecommendationSummary.tsx`
  - recommended candidate
  - backup candidate
  - rationale
  - manual checks
  - confidence summary

- `frontend/src/features/topic-agent/components/TopicAgentLandscapePanel.tsx`
  - themes
  - active methods
  - likely gaps
  - saturated areas

- `frontend/src/features/topic-agent/components/TopicAgentEvidencePanel.tsx`
  - evidence record list
  - evidence filters
  - focused evidence detail

- `frontend/src/features/topic-agent/components/TopicAgentCandidatesPanel.tsx`
  - candidate topic cards
  - supporting sources
  - open questions

- `frontend/src/features/topic-agent/components/TopicAgentComparisonPanel.tsx`
  - candidate assessments
  - convergence comparison
  - comparison session delta

- `frontend/src/features/topic-agent/components/TopicAgentTrustPanel.tsx`
  - `evidence_presentation`
  - `human_confirmations`
  - `clarification_suggestions`
  - `evidence_diagnostics`
  - `trace`

- `frontend/src/features/topic-agent/formatters.ts`
  - helper functions for source lookup
  - candidate label resolution
  - evidence statement formatting
  - confidence / diagnostic badge formatting

## 5. Type Work Required Before UI Work

This is the most important prerequisite.

The backend response already contains fields that are not fully represented in `frontend/src/types.ts`.

The frontend type layer should be extended to include:

- `evidence_presentation`
  - `source_facts`
  - `system_synthesis`
  - `tentative_inferences`

- `clarification_suggestions`

- `evidence_diagnostics`
  - `requested_provider`
  - `used_provider`
  - `fallback_used`
  - `fallback_reason`
  - `record_count`
  - `cache_hit`

- richer Topic Agent evidence statement types:
  - `statement`
  - `statement_type`
  - `supporting_source_ids`
  - `note`
  - `uncertainty_reason`
  - `missing_evidence`

Without this type update, the frontend demo cannot fully expose the trust surface that the backend already supports.

## 6. Planned UI Composition

Recommended demo page composition:

1. Input panel
2. Recommendation summary
3. Candidate cards
4. Evidence browser
5. Comparison and trust sections

This order is better for demo flow because:

- the user sees the answer before the internals
- candidate topics are visible early
- evidence and trust surfaces remain accessible without overwhelming the top of the page

For the current delivery pass, the page should optimize for:

- one-screen comprehension of the recommendation
- quick drilling into candidate evidence
- visible trust and diagnostics without leading with raw internals

## 7. Planned Refactor Sequence

### Step 1. Type Alignment

Modify:

- `frontend/src/types.ts`

Goal:

- make frontend Topic Agent types match the current backend payload

### Step 2. Feature State Extraction

Modify:

- `frontend/src/App.tsx`

Add:

- `frontend/src/features/topic-agent/hooks/useTopicAgent.ts`

Goal:

- remove Topic Agent state and async handling from `App.tsx`

### Step 3. Page Shell Extraction

Add:

- `frontend/src/features/topic-agent/TopicAgentDemoPage.tsx`

Goal:

- create a dedicated Topic Agent feature page

### Step 4. Component Split

Add:

- `TopicAgentInputPanel.tsx`
- `TopicAgentSessionHistory.tsx`
- `TopicAgentRecommendationSummary.tsx`
- `TopicAgentLandscapePanel.tsx`
- `TopicAgentEvidencePanel.tsx`
- `TopicAgentCandidatesPanel.tsx`
- `TopicAgentComparisonPanel.tsx`
- `TopicAgentTrustPanel.tsx`

Goal:

- replace the current monolithic `TopicWorkspaceV2.tsx`

### Step 5. Temporary Compatibility Bridge

Modify:

- `frontend/src/components/TopicWorkspaceV2.tsx`

Goal:

- either wrap the new page temporarily
- or stop using it once `App.tsx` points directly to the new feature page

## 8. Current Delivery Interpretation

At this point, the backend should be considered sufficiently stable for presentation and walkthrough use.

This means the frontend should now assume:

- Topic Agent still returns a three-candidate public shape
- evidence, comparison, convergence, and trust sections are all available
- provider diagnostics and cache diagnostics are part of the demo story
- session history is bounded and suitable for recent-run browsing, not long-term archival inspection

The frontend should not wait for:

- a more open-ended candidate-generation schema
- richer backend conflict modeling
- another backend retrieval pass

Those can remain post-delivery items.

## 9. Suggested Ownership Of Existing Files

### `frontend/src/App.tsx`

Future responsibility:

- app shell
- navigation
- high-level view switching

Should no longer own:

- detailed Topic Agent form state
- Topic Agent async fetch / refine logic
- Topic Agent evidence interaction logic

### `frontend/src/api.ts`

Future responsibility:

- shared request helpers
- Topic Agent request methods can remain here in the next step

Optional later split:

- `frontend/src/features/topic-agent/api.ts`

This split is optional. It is not required for the first pass.

### `frontend/src/types.ts`

Future responsibility:

- canonical API types used by multiple views

Optional later split:

- `frontend/src/features/topic-agent/types.ts`

Again, optional later. For the next step, extending the existing file is enough.

## 10. Demo-Oriented UI Priorities

For the first frontend integration pass, prioritize these surfaces:

- recommended candidate and rationale
- candidate cards with supporting citations
- evidence browser with direct source links
- trust panel showing:
  - source facts
  - system synthesis
  - tentative inferences
  - diagnostics

Lower priority for the first pass:

- highly interactive comparison diff visualizations
- advanced evidence graph interactions
- per-stage animation or complex transitions

## 11. Immediate Next Step

The next implementation step should be presentation-focused rather than architecture-heavy:

1. verify `frontend/src/types.ts` against the now-stable backend payload
2. make sure the Topic Agent tab is routed through a dedicated feature page rather than a monolithic console surface
3. prioritize presentation of recommendation, candidates, evidence, and trust panels in demo order
4. keep session history lightweight and recent-run oriented

Only after that should the Topic Agent page be split into smaller presentation components.

## 12. Frontend Implication Of The Next Backend Upgrade

The current frontend comparison and convergence area is built around a stable three-candidate product shape.

This matches the current backend well enough, but the backend is now planned to move toward:

- evidence-grounded candidate generation

rather than:

- filling fixed benchmark / transfer / systems template slots

This has two frontend implications.

### Near-Term

Do not immediately redesign the whole Topic Agent page.

For the next backend migration step, the frontend should assume:

- the public response still returns 3 candidate cards
- the comparison area still exists
- current panels stay usable

This keeps the demo stable while backend draft-generation logic evolves.

### Medium-Term

Once backend candidate generation is no longer template-first, the frontend should be prepared to show:

- more topic-native candidate titles
- less repetitive candidate positioning labels
- a lighter explanation of how candidates were generated from evidence

Likely future UI additions:

- a short `How These Directions Were Formed` panel
- candidate role summaries derived from evidence-role mix
- a less rigid comparison header than the current fixed recommendation framing

The important product rule is:

- do not let the frontend hard-code the assumption that the same three direction families always exist

The current UI can tolerate that assumption temporarily, but the next backend architecture should be treated as loosening it.
