# Topic Agent Progress

## Scope

This file tracks the recent development progress for the backend Topic Agent retrieval and synthesis workflow.

## Completed Milestones

### Retrieval And Provider Stability

- Added `arxiv` provider with fallback wiring.
- Added `openalex` provider and made it the primary scholarly source in the fallback chain.
- Added provider diagnostics to the API response:
  - `requested_provider`
  - `used_provider`
  - `fallback_used`
  - `fallback_reason`
  - `record_count`
  - `cache_hit`
- Switched `arxiv` access to `https`.
- Added provider retries and relaxed external request timeouts.

### OpenAlex Quality Improvements

- Added multi-query OpenAlex retrieval.
- Added versioned OpenAlex cache keys.
- Added reranking and refiltering on cache read, so old cached ordering does not persist after ranking changes.
- Normalized legacy cached `source_id` values to stable OpenAlex work ids such as `openalex_w4414530509`.
- Collapsed near-duplicate OpenAlex records across DOI / arXiv / alternate versions using title normalization and record preference rules.
- Downranked generic overview papers and restricted them to backfill behavior when task-specific evidence is sufficient.
- Added query alias expansion for:
  - `med-vqa`
  - `medical vqa`
  - `vqa-rad`
  - `radiology question answering`
  - `medical hallucination grounding evaluation`

### Synthesis Improvements

- Made landscape synthesis evidence-driven instead of relying on broad templates.
- Added query-aware cue detection for:
  - `visual_qa`
  - `hallucination_eval`
  - `document_qa`
- Balanced synthesis wording so:
  - radiology VQA queries stay centered on benchmark slicing and image-grounded answering
  - hallucination / grounding queries stay centered on unsupported answers, faithfulness, and audit workflows
- Added candidate wording polish and open-question deduplication.

### Confirmation And Clarification Improvements

- Added `human_confirmations` to Topic Agent responses so missing constraints and final recommendation checks are explicit in the API output.
- Added structured `clarification_suggestions` with:
  - `field_key`
  - `prompt`
  - `reason`
  - `suggested_values`
  - `refine_patch`
- This now supports a lightweight backend clarification loop:
  - `explore`
  - inspect missing clarifications and suggestion patches
  - `refine`
  - confirm that clarification prompts disappear once constraints are filled

### Session Compatibility Improvements

- Backfilled legacy session payloads on load when older records are missing:
  - `evidence_diagnostics`
  - `human_confirmations`
  - `clarification_suggestions`
- This removed schema-read failures on historical session data.

### Broad Query Retrieval Improvements

- Added generic `medical reasoning` query expansion aimed at modern medical AI evidence:
  - `medical reasoning benchmark`
  - `medical reasoning large language models`
  - `clinical reasoning benchmark medical ai`
  - `medical question answering reasoning benchmark`
- Added ranking penalties for legacy, non-modern medical reasoning records when the query is broad and modern-AI-oriented.
- Added ranking boosts for benchmark / verification / question answering / LLM style evidence under broad `medical reasoning` queries.

### Broad Query Synthesis Improvements

- Reduced `document QA` overfitting for broad `medical reasoning` queries.
- Broad medical reasoning topics no longer default to:
  - `document QA and report-centric reasoning`
  - `document-centric clinical reasoning`
  just because one top benchmark contains `MedDQA` or related document-QA evidence.
- Document-centric synthesis is now reserved for:
  - explicit document/report queries
  - stronger document-specific evidence signals outside the broad-query case
- Normalized broad-query wording so general medical reasoning outputs no longer default to:
  - `weak multimodal dependence`
  - `image-grounded reasoning`
  - `real image use`
  when the user never asked for a multimodal or image-centric topic.
- Broad medical reasoning wording now prefers:
  - reasoning verification
  - reasoning quality
  - answer-pattern shortcuts
  - benchmark validity

## Current Status

### Stage Assessment

The current best-fit stage description is:

- foundation in place
- topic-agent semantics and workflow established
- backend minimum viable closed loop largely completed
- product-layer validation and confirmation loop still incomplete

In short:

- the project is no longer only in the design phase
- the backend Topic Agent slice is already capable of end-to-end exploratory runs
- the remaining work is mainly productization, explicit confirmation flow, and richer trust surfaces

### Completion Against The Original Topic Agent Plan

Estimated completion for the current design-and-MVP slice: `85% to 90%`.

Rough breakdown:

- target user and core task definition: `done`
- system boundary and capability structure: `done`
- input and output organization: `done`
- retrieval / synthesis / comparison / convergence workflow: `done`
- source diagnostics, citation metadata, source grading: `mostly done`
- human confirmation and verification flow: `partially done`
- acceptance logic and evaluation plan: `done in docs, partial in product flow`
- full conflict modeling across disagreeing sources: `not done`
- polished end-user validation UX and explicit human-confirm checkpoints: `not done`

### Demo Readiness

- Stable manual demo scenarios are now documented in:
  - [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- The current demo coverage includes:
  - broad `medical reasoning`
  - radiology VQA
  - hallucination / grounding evaluation
  - clarification and refine loop behavior

### Stable

- OpenAlex is the normal successful path in recent manual tests.
- Cached responses preserve current ranking behavior.
- Stable OpenAlex source ids are working.
- Duplicate evidence versions are no longer taking multiple top slots.
- Generic overview evidence is no longer dominating the top of the evidence list.

### Good Query Classes

- `trustworthy multimodal reasoning in medical imaging`
- `document-centric clinical reasoning with multimodal medical reports`
- `hallucination detection and grounding evaluation for multimodal medical reasoning`
- `trustworthy visual question answering in radiology`

## Remaining Limitations

- Some landscape summaries can still surface a secondary theme that is broader than ideal when evidence mixes surveys with task-specific benchmarks.
- Candidate wording is much better, but final research-question phrasing still benefits from manual review for venue-specific positioning.
- The current slice does not model explicit source disagreement or controversy beyond basic confidence summaries.
- Human confirmation is represented in the design and response schema, but the current product slice still does not enforce an explicit confirmation workflow in the UI.
- The current implementation is a focused workflow slice, not a full standalone Topic Agent platform.
- Broad topic queries are better than before, but still need occasional manual review because generic medical terms can retrieve historically relevant but strategically weak literature.
- Broad topic synthesis is improved, but wording on very general topics still benefits from manual review because top evidence can legitimately mix benchmarks, clinical reasoning, and QA settings.

## Manual Validation Notes

When manually checking `/api/topic-agent/explore`, prioritize:

- `evidence_diagnostics.used_provider` should normally be `openalex`
- `fallback_used` should normally be `false`
- `evidence_records` top positions should prefer benchmark / VQA / grounding / document QA / radiology task-specific papers over generic overview papers
- `candidate_topics[*].supporting_source_ids` should point to the task-specific evidence near the top of the retrieved bundle

## Test Status

Latest backend regression command:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests\test_topic_agent_api.py backend\tests\test_topic_agent_pipeline.py backend\tests\test_topic_agent_providers.py backend\tests\test_health_api.py
```

Latest result:

- `45 passed`
