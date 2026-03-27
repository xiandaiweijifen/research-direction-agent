# Topic Agent 开发进度 / Topic Agent Progress

## 中文版

### 范围

本文档跟踪 Topic Agent 后端检索与综合工作流的最新开发进度。

### 已完成里程碑

#### 检索与 Provider 稳定性

- 增加了 `arxiv` provider 及 fallback wiring
- 增加了 `openalex` provider，并将其设为主要学术来源
- 在 API 响应中增加 provider diagnostics：
  - `requested_provider`
  - `used_provider`
  - `fallback_used`
  - `fallback_reason`
  - `record_count`
  - `cache_hit`
- 将 `arxiv` 访问改为 `https`
- 增加 provider retry 与更宽松的外部请求 timeout

#### OpenAlex 质量改进

- 增加多 query 的 OpenAlex retrieval
- 增加带版本的 OpenAlex cache key
- 在 cache read 阶段增加 reranking 与 refiltering，避免旧缓存顺序固化
- 将旧缓存中的 `source_id` 规范为稳定的 OpenAlex work id，例如 `openalex_w4414530509`
- 用 title normalization 和 preference rules 折叠 DOI / arXiv / alternate version 的近重复记录
- 下调 generic overview paper 的权重，并限制其只作为 backfill
- 增加 query alias expansion：
  - `med-vqa`
  - `medical vqa`
  - `vqa-rad`
  - `radiology question answering`
  - `medical hallucination grounding evaluation`

#### Synthesis 改进

- 将 landscape synthesis 改成 evidence-driven，而不是 broad template
- 增加 query-aware cue detection：
  - `visual_qa`
  - `hallucination_eval`
  - `document_qa`
- 调整 synthesis wording：
  - radiology VQA query 保持 benchmark slicing 和 image-grounded answering
  - hallucination / grounding query 保持 unsupported answers、faithfulness 和 audit workflow
- 增加 candidate wording polish 与 open-question deduplication

#### Confirmation 与 Clarification 改进

- 在 Topic Agent 响应中增加 `human_confirmations`，把缺失约束和最终 recommendation check 显式化
- 增加结构化 `clarification_suggestions`，包含：
  - `field_key`
  - `prompt`
  - `reason`
  - `suggested_values`
  - `refine_patch`
- 当前已经支持轻量 clarification loop：
  - `explore`
  - 查看 missing clarifications 和 suggestion patches
  - `refine`
  - 确认 clarification prompt 在补全约束后消失

#### Session 兼容性改进

- 在读取旧 session 时自动补齐缺失字段：
  - `evidence_diagnostics`
  - `human_confirmations`
  - `clarification_suggestions`
- 这解决了历史 session schema-read failure 的问题

#### Broad Query Retrieval 改进

- 为宽泛 `medical reasoning` query 增加偏现代 medical AI 的 query expansion：
  - `medical reasoning benchmark`
  - `medical reasoning large language models`
  - `clinical reasoning benchmark medical ai`
  - `medical question answering reasoning benchmark`
- 对宽泛且 modern-AI-oriented 的 medical reasoning query，下调 legacy reasoning records
- 对 benchmark / verification / question answering / LLM 相关 evidence 增加排序加权

#### Broad Query Synthesis 改进

- 降低宽泛 `medical reasoning` query 对 `document QA` 的过拟合
- 宽泛 medical reasoning topic 不再因为一篇 `MedDQA` 类 evidence 就默认掉到：
  - `document QA and report-centric reasoning`
  - `document-centric clinical reasoning`
- document-centric synthesis 只保留给：
  - 明确的 document/report query
  - broad-query 之外、document-specific signal 足够强的情形
- 进一步归一化宽泛 query wording，使 `medical reasoning` 不再默认落到：
  - `weak multimodal dependence`
  - `image-grounded reasoning`
  - `real image use`
- 现在更偏：
  - reasoning verification
  - reasoning quality
  - answer-pattern shortcuts
  - benchmark validity

### 当前状态

#### 阶段判断

当前最准确的阶段描述是：

- 基础底座已就位
- topic-agent 语义和 workflow 已建立
- 后端最小可用闭环基本完成
- 产品层的 validation 与 confirmation loop 仍未完全完成

更直白地说：

- 项目已经不是纯设计阶段
- 后端 Topic Agent 已经可以完成端到端 exploratory run
- 剩余工作主要是产品化、显式 confirmation flow 和更强的 trust surface

#### 对照原始计划的完成度

当前 design-and-MVP slice 的估计完成度为：`85% to 90%`

粗略拆分如下：

- target user 和 core task definition：`done`
- system boundary 和 capability structure：`done`
- input / output organization：`done`
- retrieval / synthesis / comparison / convergence workflow：`done`
- source diagnostics / citation metadata / source grading：`mostly done`
- human confirmation 和 verification flow：`partially done`
- acceptance logic 和 evaluation plan：`done in docs, partial in product flow`
- disagreeing sources 的完整 conflict modeling：`not done`
- polished end-user validation UX 和显式 human-confirm checkpoint：`not done`

#### Demo 就绪度

- 稳定手测场景文档位于：
  - [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- 面向评审的演示叙述文档位于：
  - [topic_agent_acceptance_walkthrough.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance_walkthrough.md)
- 当前 demo 已覆盖：
  - broad `medical reasoning`
  - radiology VQA
  - hallucination / grounding evaluation
  - clarification 与 refine loop

#### 当前比较稳定的部分

- 近几轮手测中，OpenAlex 已是默认成功路径
- cache response 可以保持当前 ranking 行为
- 稳定 OpenAlex source id 已可工作
- duplicate evidence version 不再长期占多个 top slot
- generic overview evidence 已不再主导 evidence list 顶部

#### 当前表现较好的 query 类型

- `trustworthy multimodal reasoning in medical imaging`
- `document-centric clinical reasoning with multimodal medical reports`
- `hallucination detection and grounding evaluation for multimodal medical reasoning`
- `trustworthy visual question answering in radiology`

### 剩余限制

- 某些 landscape summary 仍可能在 survey 与 task-specific benchmark 混合时带出偏宽的 secondary theme
- candidate wording 已比之前好很多，但面向特定 venue 时仍建议人工润色
- 当前没有显式建模 source disagreement / controversy，只靠 basic confidence summary
- human confirmation 已进入 schema 与 response，但产品流里还没有强制型 confirmation UX
- 当前实现仍是 focused workflow slice，而不是完整 standalone Topic Agent platform
- 宽泛 topic query 虽然已经改进，但仍需要偶尔人工复核，因为 generic medical term 依然可能召回策略价值较低的文献
- 宽泛 topic synthesis 虽已改进，但极泛 query 的 wording 仍建议人工 review，因为顶层 evidence 可能混合 benchmark、clinical reasoning 和 QA 场景

### 手测关注点

手测 `/api/topic-agent/explore` 时，建议优先检查：

- `evidence_diagnostics.used_provider` 一般应为 `openalex`
- `fallback_used` 一般应为 `false`
- `evidence_records` 顶部应优先 benchmark / VQA / grounding / document QA / radiology task-specific paper，而不是 generic overview
- `candidate_topics[*].supporting_source_ids` 应指向 evidence bundle 顶部附近的 task-specific evidence

### 测试状态

最近一次后端回归命令：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests\test_topic_agent_api.py backend\tests\test_topic_agent_pipeline.py backend\tests\test_topic_agent_providers.py backend\tests\test_health_api.py
```

最近结果：

- `45 passed`

## English Version

### Scope

This file tracks the recent development progress for the backend Topic Agent retrieval and synthesis workflow.

### Completed Milestones

#### Retrieval And Provider Stability

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

#### OpenAlex Quality Improvements

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
  - `clinical reasoning benchmark`
  - `clinical decision support reasoning evaluation`
  - `medical reasoning metacognition benchmark`
  - `free-response clinical reasoning evaluation`
- Bumped the OpenAlex cache schema version to invalidate stale retrieval caches after ranking changes.

#### Synthesis Improvements

- Made landscape synthesis evidence-driven instead of relying on broad templates.
- Added query-aware cue detection for:
  - `visual_qa`
  - `hallucination_eval`
  - `document_qa`
- Balanced synthesis wording so:
  - radiology VQA queries stay centered on benchmark slicing and image-grounded answering
  - hallucination / grounding queries stay centered on unsupported answers, faithfulness, and audit workflows
- Added candidate wording polish and open-question deduplication.

#### Confirmation And Clarification Improvements

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

#### Session Compatibility Improvements

- Backfilled legacy session payloads on load when older records are missing:
  - `evidence_diagnostics`
  - `human_confirmations`
  - `clarification_suggestions`
- This removed schema-read failures on historical session data.

#### Broad Query Retrieval Improvements

- Added generic `medical reasoning` query expansion aimed at modern medical AI evidence:
  - `medical reasoning benchmark`
  - `medical reasoning large language models`
  - `clinical reasoning benchmark medical ai`
  - `medical question answering reasoning benchmark`
- Added ranking penalties for legacy, non-modern medical reasoning records when the query is broad and modern-AI-oriented.
- Added ranking boosts for benchmark / verification / question answering / LLM style evidence under broad `medical reasoning` queries.

#### Clinical Reasoning Retrieval Improvements

- Added a dedicated retrieval case for broad `clinical medical reasoning` queries under the OpenAlex path.
- Reduced VQA / document-QA / report-image bias for `clinical medical reasoning` when the user did not ask for multimodal, radiology, or document-centric work.
- Increased ranking preference for:
  - clinical reasoning benchmarks
  - metacognition and calibration
  - decision-support evaluation
  - free-response clinical reasoning examinations

#### Broad Query Synthesis Improvements

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

#### Evidence Presentation Refinements

- Added structured `evidence_presentation` layers to separate:
  - `source_facts`
  - `system_synthesis`
  - `tentative_inferences`
- Added `supporting_source_ids` to each evidence-presentation statement so users can trace claims back to retrieved evidence records.
- Added `uncertainty_reason` and `missing_evidence` for tentative inferences so recommendation-level statements explicitly show why they remain provisional.
- Tightened `system_synthesis` source binding by matching synthesis statements against source titles and summaries instead of always reusing the top retrieved records.
- Tightened `candidate_topics[*].supporting_source_ids` so method-transfer recommendations are more likely to bind to method / framework evidence rather than defaulting to the top benchmark record.

### Current Status

#### Stage Assessment

The current best-fit stage description is:

- foundation in place
- topic-agent semantics and workflow established
- backend minimum viable closed loop largely completed
- product-layer validation and confirmation loop still incomplete

In short:

- the project is no longer only in the design phase
- the backend Topic Agent slice is already capable of end-to-end exploratory runs
- the remaining work is mainly productization, explicit confirmation flow, and richer trust surfaces
- backend quality iteration is currently deferred so the next phase can focus on consolidating the user-facing Topic Agent experience rather than continuing retrieval tuning

#### Completion Against The Original Topic Agent Plan

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

#### Demonstration Readiness

- Stable manual validation scenarios are now documented in:
  - [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- Acceptance-oriented walkthrough guidance is now documented in:
  - [topic_agent_acceptance_walkthrough.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance_walkthrough.md)
- Delivery-stage execution guidance is now documented in:
  - [topic_agent_demo_completion_plan.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_completion_plan.md)
- The current validation coverage includes:
  - broad `medical reasoning`
  - radiology VQA
  - hallucination / grounding evaluation
  - clarification and refine loop behavior
  - non-medical software-agent and bug-fixing topic exploration

#### Stable

- OpenAlex is the normal successful path in recent manual tests.
- Cached responses preserve current ranking behavior.
- Stable OpenAlex source ids are working.
- Duplicate evidence versions are no longer taking multiple top slots.
- Generic overview evidence is no longer dominating the top of the evidence list.
- Topic Agent session history is now capped and trimmed on save.
- Evaluation report history is now capped and pruned automatically.

#### Strong Query Classes

- `trustworthy multimodal reasoning in medical imaging`
- `document-centric clinical reasoning with multimodal medical reports`
- `hallucination detection and grounding evaluation for multimodal medical reasoning`
- `trustworthy visual question answering in radiology`

### Remaining Limitations

- Some landscape summaries can still surface a secondary theme that is broader than ideal when evidence mixes surveys with task-specific benchmarks.
- Candidate wording is much better, but final research-question phrasing still benefits from manual review for venue-specific positioning.
- The current slice does not model explicit source disagreement or controversy beyond basic confidence summaries.
- Human confirmation is represented in the design and response schema, but the current product slice still does not enforce an explicit confirmation workflow in the UI.
- The current implementation is a focused workflow slice, not a full standalone Topic Agent platform.
- Broad topic queries are better than before, but still need occasional manual review because generic medical terms can retrieve historically relevant but strategically weak literature.
- Broad topic synthesis is improved, but wording on very general topics still benefits from manual review because top evidence can legitimately mix benchmarks, clinical reasoning, and QA settings.
- Candidate generation is still mostly organized around a fixed three-direction frame, so broad topic exploration can feel repetitive even when retrieval improves.
- The current convergence layer still behaves more like template filling than open candidate generation, especially on non-medical modern topics such as coding agents.
- Some non-medical repository / bug-fixing queries still retrieve partially relevant repository-mining or broad software-engineering records, so evidence bundles remain serviceable for presentation and inspection, but not yet publication-grade.

### Generic Quality-Control Slice

The first backend generalization slice is now implemented at the provider-ranking layer.

Completed in this slice:

- introduced reusable evidence-role inference in `providers.py`, including:
  - `benchmark_evaluation`
  - `method_framework`
  - `systems_tooling`
  - `survey_background`
  - `code_resource`
  - `dataset_resource`
  - `failure_analysis`
  - `domain_background`
  - `off_target_neighbor`
- added `topic_fit_score` as a separate scoring component so directly on-topic evidence can outrank merely adjacent literature
- added a modern-topic guard in ranked filtering so legacy neighboring records are backfilled after more on-topic evidence for modern AI / agent queries
- kept this slice provider-local so ranking can improve without rewriting the whole pipeline
- added `topic_relevant`, `domain_neighbor`, and `lexical_match` style internal evidence relevance labeling for bundle selection
- added stronger code-repair query disambiguation so generic autonomous-maintenance neighbors are penalized
- added candidate-role-aware evidence rebinding so evaluation, method, and systems candidates bind more consistently on bug-fixing topics

This is intended to improve:

- `medical reasoning`
- `clinical medical reasoning`
- `llm agents for software engineering`
- and other broad modern topics

without requiring one-off ranking patches for each topic family.

Recent manual checks show this slice is working materially better on:

- `llm agents for automated bug fixing`
- `program repair with llm agents`
- `repository-level bug-fixing agents`

Next planned backend quality steps:

- add explicit `era_fit` instead of only a lightweight modern-topic penalty
- add candidate-aware evidence selection so different candidate types bind to different evidence roles more consistently
- add evidence-bundle balancing so the final top evidence set is not overly repetitive or skewed toward one weakly aligned sub-area

### Next Architecture Upgrade

The next major backend direction should no longer focus only on retrieval and ranking patches.

The system should evolve from:

- fixed candidate templates with evidence binding

to:

- evidence-grounded candidate generation

Planned upgrade path:

- generate 5 to 8 provisional candidate drafts from the current evidence bundle
- score drafts for:
  - evidence support
  - distinctiveness
  - feasibility under user constraints
  - risk
- merge near-duplicate drafts
- select the strongest 3 to 4 final candidates for comparison and convergence

Why this shift is needed:

- retrieval quality alone cannot solve the repetitive-candidate problem
- broad modern topics such as `llm agents for software engineering` still reveal that the current candidate layer is too template-driven
- the product needs the model to play a stronger evidence-judgment role, not only a ranking-consumer role

The public API should remain stable during the first migration step.

Near-term implementation strategy:

- keep the current response schema
- add an internal draft-candidate phase behind the existing pipeline
- let current final candidates be populated from the strongest generated drafts
- delay frontend structural changes until draft quality stabilizes

### Internal Draft-Candidate Step

The first migration step toward evidence-grounded candidate generation is now implemented in the pipeline.

Completed in this slice:

- added an internal draft-candidate structure inside `pipeline.py`
- draft generation now happens from retrieved evidence before final candidate mapping
- final public candidates still remain `candidate_1 / candidate_2 / candidate_3` for compatibility
- query-specific medical and radiology behaviors are preserved by limiting when draft text is allowed to override existing candidate wording
- modern non-medical topics can now use draft-selected primary evidence and draft-shaped candidate wording more directly

Current limitation of this step:

- the public candidate shape is still fixed to three final slots
- draft generation is not yet exposed in the API or frontend
- convergence is still performed over the three final slots rather than over a larger draft pool

This means the architecture has started to move away from pure template filling, but it has not yet completed the full evidence-grounded candidate-generation transition.

### Frontend Productization Slice

The frontend Topic Agent page is now structurally functional and suitable for guided presentation, but further productization is still useful.

Recently completed frontend improvements include:

- extraction into feature-level Topic Agent components
- clearer demo reading order
- evidence-card collapsing and focused evidence drill-down
- recent-session collapsing
- more human-readable labels for source types, candidate positioning, and comparison dimensions

The next likely frontend polish areas are:

- more consistent Chinese/English localization
- softer presentation of internal identifiers and debugging-style fields
- lighter-weight trust-panel summaries before detailed drill-down

### Current Delivery Focus

The backend should now be treated as functionally stable for the current delivery pass.

That means:

- no more retrieval-quality tuning unless a demo-blocking regression appears
- no more candidate-generation architecture changes before the demo is complete
- remaining implementation focus should move to frontend composition, demo flow, and walkthrough quality

### Manual Validation Notes

When manually checking `/api/topic-agent/explore`, prioritize:

- `evidence_diagnostics.used_provider` should normally be `openalex`
- `fallback_used` should normally be `false`
- `evidence_records` top positions should prefer benchmark / VQA / grounding / document QA / radiology task-specific papers over generic overview papers
- `candidate_topics[*].supporting_source_ids` should point to the task-specific evidence near the top of the retrieved bundle

### Test Status

Latest backend regression command:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests\test_topic_agent_api.py backend\tests\test_topic_agent_pipeline.py backend\tests\test_topic_agent_providers.py backend\tests\test_report_store_service.py backend\tests\test_health_api.py
```

Latest result:

- `70 passed`

### Retrieval Upgrade Track

- Added [topic_agent_retrieval_upgrade_plan.md](/d:/project/research-topic-copilot/docs/topic_agent_retrieval_upgrade_plan.md) to track the staged retrieval architecture upgrade.
- Completed retrieval upgrade package 1:
  - split provider retrieval into explicit phases for planning, cache lookup, candidate collection, normalization/ranking, and diagnostics construction
  - kept the backend response contract stable
  - prepared the provider implementation for later hybrid retrieval and reranking packages
- Package 1 verification:
  - `backend/tests/test_topic_agent_providers.py`: `40 passed`
  - `backend/tests/test_topic_agent_api.py`: `8 passed`
  - the API pytest process completed successfully even when the shell wrapper timed out immediately after completion
- Retrieval upgrade package 2 has started:
  - OpenAlex query construction is now grouped into explicit retrieval routes:
    - `base`
    - `core_focus`
    - `alias`
    - `role_expansion`
  - per-query diagnostics now include route labels, so later fusion and reranking work can be measured route-by-route
  - added a lightweight route-aware fusion bonus so records retrieved by multiple routes are ranked more favorably than one-route-only matches
  - added a lightweight reciprocal-rank-style route signal for software-agent and code-repair topics, so route-local top candidates matter more than weak expansion-only neighbors
  - added a query-family-aware candidate hygiene layer so software-agent and code-repair queries require same-task qualification before candidates enter the final evidence pool
  - current behavior is still heuristic route-aware fusion rather than full candidate fusion such as RRF
- Package 2 verification for the current sub-step:
  - `backend/tests/test_topic_agent_providers.py`: `45 passed`
  - `backend/tests/test_topic_agent_api.py`: `8 passed`

### Comparison And Convergence Upgrade

- Comparison scoring is no longer assigned only by fixed candidate slot.
- Candidate assessments now derive more of their dimension labels from:
  - support count
  - candidate positioning
  - origin signals
  - style and budget constraints
- Convergence recommendation is no longer selected only from a style-to-slot mapping.
- Recommendation and backup selection now consume the comparison assessments as the primary decision surface, while still respecting style and budget as soft preferences rather than hard slot rules.
- Current verification:
  - `backend/tests/test_topic_agent_pipeline.py`: `21 passed`
  - `backend/tests/test_topic_agent_api.py`: `8 passed`

### Query Rewrite Stabilization

- Added a query-family-aware anchor-preserving rewrite layer in OpenAlex query planning.
- The new logic targets retrieval drift at the query-construction layer rather than adding more negative-result blacklists.
- Two query families now receive stronger task-preserving `core_focus` and `alias` rewrites before generic role expansions:
  - repository issue-resolution agent workflows
  - benchmark-slicing style repository repair / validation queries
- This keeps retrieval queries closer to task anchors such as:
  - `github issue resolution`
  - `repository-level agent`
  - `repository repair benchmark`
  - `program repair benchmark`
- The software-agent interactive fan-out cap remains intact after narrowing the family trigger.
- Current verification:
  - `backend/tests/test_topic_agent_providers.py`: `47 passed`
  - `backend/tests/test_topic_agent_pipeline.py`: `21 passed`
  - `backend/tests/test_topic_agent_api.py`: `8 passed`

### Issue-Resolution Hygiene Tightening

- Added a narrower same-task qualification path for the `repository issue-resolution` query family.
- For this family, final candidates now need stronger joint evidence of:
  - issue-resolution intent such as `github issues` or `issue resolution`
  - repository-level setting
  - agent / benchmark / software-engineering task framing
- This is meant to stop collaborative-engineering and generic workflow neighbors from leaking into downstream support sets after the improved query rewrites have already pulled the right issue-resolution papers into the pool.
- Current verification:
  - `backend/tests/test_topic_agent_providers.py`: `48 passed`
  - `backend/tests/test_topic_agent_pipeline.py`: `21 passed`
  - `backend/tests/test_topic_agent_api.py`: `8 passed`

### Cache Control And Clean Backfill

- Added a request-level `disable_cache` flag for topic-agent explore requests.
- This is intended for manual validation and debugging so retrieval changes can be tested without having to keep mutating the request body just to miss cache.
- Normal cached behavior remains the default.
- Added a limited clean-backfill step after same-task filtering:
  - retrieval still prefers same-task evidence first
  - if the final pool becomes too tight, the system can backfill from clean anchor-aligned candidates
  - off-target and generic collaborative-engineering neighbors are still excluded from this backfill path
- Current verification:
  - `backend/tests/test_topic_agent_providers.py`: `50 passed`
  - `backend/tests/test_topic_agent_pipeline.py`: `21 passed`
  - `backend/tests/test_topic_agent_api.py`: `9 passed`

### Retrieval Closure Note

- The retrieval track is now in a reasonable closure state for the current delivery pass.
- The main outcomes are:
  - staged provider retrieval instead of one large monolithic retrieval flow
  - explicit query routes with per-route diagnostics
  - lightweight route-aware fusion
  - query-family-aware candidate hygiene
  - anchor-preserving query rewrites for drifting software-agent query families
  - stricter issue-resolution qualification
  - request-level cache bypass for manual validation
  - limited clean backfill so high-purity retrieval does not collapse too aggressively
- Recent manual checks indicate that:
  - repository repair benchmark queries no longer drift into generic software-security or vibe-coding neighbors
  - repository issue-resolution queries no longer leak collaborative-engineering neighbors into downstream support sets
  - the issue-resolution family can now keep a cleaner final pool while still backfilling one additional clean record when appropriate
- Recommended operating guidance:
  - keep default cached behavior for normal product use
  - use `disable_cache=true` only for retrieval validation and debugging
  - do not broaden retrieval heuristics again unless a new real query family shows a concrete regression
- The next high-value work should now move away from retrieval tuning unless a demo-blocking failure appears.

### Generalization Spot Check

- A small post-closure spot check was run to test whether the current backend should be described as broadly generalized.
- The answer is no: the current backend has a stronger generalization framework, but not universal validated performance across all topic families.

Observed outcome by family:

- stable and already validated:
  - repository repair / benchmark
  - repository issue-resolution / software-agent
- partially transferable but not yet stable:
  - adjacent software-engineering assistant topics such as repository-scale code review assistants
  - ML reproducibility / dataset-centric LLM evaluation topics
- clearly outside the currently stabilized retrieval families:
  - computing-education and education-oriented AI workflow topics

The main implication is:

- current retrieval should be presented as family-aware and regression-driven, not as a fully domain-agnostic topic discovery engine
- architecture-level generalization exists, but effect-level generalization has only been validated for a subset of families
- this boundary is now explicit and should be reflected in demos and review discussion
