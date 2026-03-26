# Topic Agent MVP 计划 / Topic Agent MVP Plan

## 中文版

### 目标

为 `Topic Agent` 定义一个明确的第一阶段里程碑，使项目能从高层设计进入实现，而不会膨胀成一个大而全的学术平台。

MVP 要清楚证明一件事：

系统能够把一个模糊的研究兴趣收敛成一小组有证据支撑、可比较、并且显式暴露不确定性的候选选题。

### 1. MVP 产品承诺

MVP 不是完整研究助手。

MVP 至少应帮助用户完成：

- 输入 research interest 或 seed idea
- 获得结构化 problem framing
- 检索并查看 supporting evidence
- 看到 3 个 candidate topic direction
- 用显式维度比较这些方向
- 得到推荐 next-best option 和必要 manual check

如果系统不能稳定完成这 6 件事，就不应继续扩范围。

### 2. MVP 范围

#### 在范围内

- 一条 topic exploration 输入流
- 一条 evidence retrieval workflow
- 一条 landscape synthesis workflow
- 一条 candidate generation workflow
- 一条 comparison and convergence workflow
- source metadata 与 citation display
- source-tier labeling
- 显式 uncertainty 与 conflict note
- manual confirmation checkpoint
- 可持久化的 topic exploration session

#### 不在范围内

- 完整 paper drafting
- experiment planning 或 execution
- 个性化长期 academic memory
- 大范围 multi-agent orchestration
- 大规模 knowledge graph construction
- 复杂 collaboration workflow
- 基于私人 citation library 的 recommendation

### 3. MVP 的目标用户

MVP 主要服务一个核心用户：

- 有 broad interest area 但尚未形成稳定 research topic 的研究生或早期研究者

这类用户最常需要的是：

- problem framing
- 快速理解 landscape
- 获得 candidate option
- 获得 evidence-backed narrowing support

### 4. 核心用户旅程

#### Step 1: Input

用户提交：

- research interest
- 可选的 problem domain
- 可选的 seed idea
- 可选的 constraints

示例：

```json
{
  "interest": "trustworthy multimodal reasoning in medical imaging",
  "problem_domain": "medical AI",
  "seed_idea": "I want to explore whether multimodal LLMs can provide clinically useful explanations",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "benchmark-driven"
  }
}
```

#### Step 2: Problem Framing

系统返回：

- normalized topic statement
- extracted constraints
- missing clarifications
- search sub-questions

#### Step 3: Evidence Retrieval

系统从少量可控 source type 中检索并组织 evidence。

第一阶段 source type：

- papers
- surveys
- benchmark 或 dataset page
- code repository

#### Step 4: Landscape Synthesis

系统把 evidence 组织成：

- major theme
- active method
- likely gap
- saturated area

#### Step 5: Candidate Generation

系统生成 3 个 candidate topic。

每个 candidate 至少包含：

- working title
- core research question
- why it matters
- why it is feasible
- supporting evidence
- major risk 或 uncertainty

#### Step 6: Comparison And Convergence

系统使用以下维度比较 candidate：

- novelty
- feasibility
- evidence strength
- data availability
- implementation cost
- risk

并进一步给出：

- 一个推荐的 next-best option
- 一个 backup option
- final commitment 前的 manual check

### 5. MVP 的窄工作流

MVP 应使用固定、可检查的 workflow：

1. `frame_problem`
2. `retrieve_evidence`
3. `synthesize_landscape`
4. `generate_candidates`
5. `compare_candidates`
6. `converge_recommendation`

它应保持 workflow-based，而不是 single-shot。

同时 workflow 还应支持一个受控回路：

- `refine_scope`

该回路在以下情况下触发：

- evidence 太弱
- scope 太宽
- candidate 过于重复

### 6. MVP 数据模型

#### 6.1 Session Record

建议的持久化 session 结构：

```json
{
  "session_id": "string",
  "created_at": "iso_timestamp",
  "updated_at": "iso_timestamp",
  "user_input": {},
  "framing_result": {},
  "evidence_records": [],
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "human_confirmations": [],
  "trace": [],
  "confidence_summary": {}
}
```

#### 6.2 Evidence Record

每条 evidence record 至少应包含：

```json
{
  "source_id": "string",
  "title": "string",
  "source_type": "paper|survey|benchmark|dataset|code",
  "source_tier": "A|B|C",
  "year": 2025,
  "authors_or_publisher": "string",
  "identifier": "doi|arxiv|url|repo",
  "url": "string",
  "summary": "string",
  "relevance_reason": "string"
}
```

#### 6.3 Candidate Topic

每个 candidate topic 至少应包含：

```json
{
  "candidate_id": "string",
  "title": "string",
  "research_question": "string",
  "positioning": "gap-driven|transfer|application|systems",
  "novelty_note": "string",
  "feasibility_note": "string",
  "risk_note": "string",
  "supporting_source_ids": ["source_1", "source_2"],
  "open_questions": ["string"]
}
```

### 7. MVP API Surface

第一版接口面可以保持很小。

#### POST `/api/topic-agent/explore`

用途：

- 创建新的 topic exploration session
- 跑完整 MVP workflow

请求：

```json
{
  "interest": "string",
  "problem_domain": "string",
  "seed_idea": "string",
  "constraints": {}
}
```

响应：

```json
{
  "session_id": "string",
  "framing_result": {},
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "confidence_summary": {},
  "trace": []
}
```

#### GET `/api/topic-agent/sessions`

用途：

- 列出最近的 exploration session

#### GET `/api/topic-agent/sessions/{session_id}`

用途：

- 查看完整 session，包括 evidence 与 trace

#### POST `/api/topic-agent/sessions/{session_id}/refine`

用途：

- 用更窄或修订后的约束重新运行 workflow

### 8. MVP UI 计划

MVP UI 应保持比当前 generic console 更窄。

建议的首个视图：`Topic Workspace`

#### Section A: Explore

包含：

- input form
- extracted framing
- missing clarifications
- run button

#### Section B: Evidence

包含：

- evidence list
- source tier label
- source type filter
- per-record detail panel
- conflict 与 uncertainty note

#### Section C: Compare

包含：

- 3 张 candidate topic card
- comparison matrix
- recommendation panel
- manual confirmation checklist

### 9. MVP Source 策略

MVP 不应试图一次接入所有 academic source。

推荐的第一阶段实现策略：

- 先做 bounded source adapter layer
- 先允许 mock 或 local evidence mode
- 设计 output model，使未来可以把 mock retrieval 平滑替换成真实 connector

source strategy 只有在以下条件成立时才算可接受：

- evidence record 已标准化
- source tiering 可行
- citation display 一致

### 10. MVP Confidence Model

MVP 不应输出一个不透明的单一 confidence 分数。

更合适的做法是暴露一组小型 confidence summary：

- `evidence_coverage`
- `source_quality`
- `candidate_separation`
- `conflict_level`

示例：

```json
{
  "evidence_coverage": "medium",
  "source_quality": "medium_high",
  "candidate_separation": "high",
  "conflict_level": "low"
}
```

### 11. MVP 验收标准

MVP 可接受，当且仅当它能稳定展示：

- clear problem framing
- candidate topic 背后的可见 evidence
- 3 个真正有差异的 candidate topic
- 一个不重复、不空泛的 comparison
- 一个带显式 limitation 的 recommendation
- 至少一个明确的 human confirmation step

MVP 不可接受，如果：

- candidate 几乎重复
- recommendation 没有 evidence 支撑
- UI 把 source detail 隐藏掉
- evidence 很弱时，系统却表现得很权威

### 12. 建议的实现顺序

1. 定义 schema 与 persisted session model
2. 创建 topic-agent route 与 stub workflow
3. 实现 mock evidence retrieval 与 evidence record
4. 实现 landscape 与 candidate generation stub
5. 实现 comparison 与 convergence output
6. 构建最小 Topic Workspace UI
7. 增加 session inspection 与 refine flow
8. 增加 MVP task 的 evaluation fixture

### 13. 第一个 Demo 场景

输入：

- interest: trustworthy multimodal reasoning in medical imaging
- constraints: 6 months, student resources, benchmark-driven

预期 demo 输出：

- 一条 framed problem summary
- 8 到 15 条 evidence record
- 一份 landscape summary
- 3 个 candidate topic
- 一个 comparison matrix
- 一个带 backup option 的 recommended topic
- 一份 manual verification checklist

### 14. MVP 之后的扩展门槛

在证明以下几点之前，不要继续扩范围：

- narrowing workflow 确实有用
- evidence link 足够可信
- candidate diversity 是真的
- 用户能理解为什么一个 candidate 比另一个更值得推荐

### 15. Demo 与 Acceptance 参考文档

在验证当前 MVP slice 时，建议搭配使用：

- [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- [topic_agent_acceptance_walkthrough.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance_walkthrough.md)

## English Version

### Goal

Define a concrete first milestone for `Topic Agent` so the project can move from high-level design into implementation without expanding into a broad academic platform.

The MVP should prove one thing clearly:

The system can help a user narrow a vague research interest into a small set of evidence-backed candidate topics with explicit comparison and visible uncertainty.

### 1. MVP Product Promise

The MVP is not a full research assistant.

The MVP should help a user:

- enter a research interest or seed idea
- receive a structured problem framing
- retrieve and inspect supporting evidence
- see 3 candidate topic directions
- compare those directions using explicit dimensions
- get a recommended next-best option and required manual checks

If the system cannot do those six things reliably, the MVP should not expand further.

### 2. MVP Scope

#### In Scope

- one topic exploration input flow
- one evidence retrieval workflow
- one landscape synthesis workflow
- one candidate generation workflow
- one comparison and convergence workflow
- source metadata and citation display
- source-tier labeling
- explicit uncertainty and conflict notes
- manual confirmation checkpoints
- persisted topic exploration sessions

#### Out Of Scope

- full paper drafting
- experiment planning or execution
- personalized long-term academic memory
- broad multi-agent orchestration
- large-scale knowledge graph construction
- complex collaboration workflows
- recommendation based on private citation libraries

### 3. Target User For The MVP

The MVP should optimize for one primary user:

- a graduate student or early-stage researcher who has a broad interest area but has not yet formed a stable research topic

This user usually needs:

- problem framing
- quick landscape understanding
- candidate options
- evidence-backed narrowing support

### 4. Core User Journey

#### Step 1: Input

The user submits:

- research interest
- optional problem domain
- optional seed idea
- optional constraints

Example:

```json
{
  "interest": "trustworthy multimodal reasoning in medical imaging",
  "problem_domain": "medical AI",
  "seed_idea": "I want to explore whether multimodal LLMs can provide clinically useful explanations",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "benchmark-driven"
  }
}
```

#### Step 2: Problem Framing

The system returns:

- normalized topic statement
- extracted constraints
- missing clarifications
- search sub-questions

#### Step 3: Evidence Retrieval

The system retrieves and groups evidence from a small number of source types.

First-phase source types:

- papers
- surveys
- benchmark or dataset pages
- code repositories

#### Step 4: Landscape Synthesis

The system organizes the evidence into:

- major themes
- active methods
- likely gaps
- saturated areas

#### Step 5: Candidate Generation

The system produces 3 candidate topics.

Each candidate should include:

- working title
- core research question
- why it may matter
- why it may be feasible
- key supporting evidence
- major risk or uncertainty

#### Step 6: Comparison And Convergence

The system compares candidates using:

- novelty
- feasibility
- evidence strength
- data availability
- implementation cost
- risk

Then it provides:

- one recommended next-best option
- one backup option
- manual checks before final commitment

### 5. Narrow Workflow For The MVP

The MVP should use a fixed, inspectable workflow:

1. `frame_problem`
2. `retrieve_evidence`
3. `synthesize_landscape`
4. `generate_candidates`
5. `compare_candidates`
6. `converge_recommendation`

This should remain workflow-based, not single-shot.

The workflow should also support one controlled loop:

- `refine_scope`

This loop is triggered when:

- evidence is too weak
- the scope is too broad
- candidates are repetitive

### 6. MVP Data Model

#### 6.1 Session Record

Suggested persisted session structure:

```json
{
  "session_id": "string",
  "created_at": "iso_timestamp",
  "updated_at": "iso_timestamp",
  "user_input": {},
  "framing_result": {},
  "evidence_records": [],
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "human_confirmations": [],
  "trace": [],
  "confidence_summary": {}
}
```

#### 6.2 Evidence Record

Each evidence record should include at minimum:

```json
{
  "source_id": "string",
  "title": "string",
  "source_type": "paper|survey|benchmark|dataset|code",
  "source_tier": "A|B|C",
  "year": 2025,
  "authors_or_publisher": "string",
  "identifier": "doi|arxiv|url|repo",
  "url": "string",
  "summary": "string",
  "relevance_reason": "string"
}
```

#### 6.3 Candidate Topic

Each candidate topic should include:

```json
{
  "candidate_id": "string",
  "title": "string",
  "research_question": "string",
  "positioning": "gap-driven|transfer|application|systems",
  "novelty_note": "string",
  "feasibility_note": "string",
  "risk_note": "string",
  "supporting_source_ids": ["source_1", "source_2"],
  "open_questions": ["string"]
}
```

### 7. MVP API Surface

The first version can stay small.

#### POST `/api/topic-agent/explore`

Purpose:

- create a new topic exploration session
- run the full MVP workflow

Request:

```json
{
  "interest": "string",
  "problem_domain": "string",
  "seed_idea": "string",
  "constraints": {}
}
```

Response:

```json
{
  "session_id": "string",
  "framing_result": {},
  "landscape_summary": {},
  "candidate_topics": [],
  "comparison_result": {},
  "convergence_result": {},
  "confidence_summary": {},
  "trace": []
}
```

#### GET `/api/topic-agent/sessions`

Purpose:

- list recent exploration sessions

#### GET `/api/topic-agent/sessions/{session_id}`

Purpose:

- inspect a full session with evidence and trace

#### POST `/api/topic-agent/sessions/{session_id}/refine`

Purpose:

- rerun the workflow with narrower or revised constraints

### 8. MVP UI Plan

The MVP UI should stay narrower than the current generic console.

Suggested first view: `Topic Workspace`

#### Section A: Explore

Contains:

- input form
- extracted framing
- missing clarifications
- run button

#### Section B: Evidence

Contains:

- evidence list
- source tier labels
- source type filters
- per-record detail panel
- conflict and uncertainty notes

#### Section C: Compare

Contains:

- 3 candidate topic cards
- comparison matrix
- recommendation panel
- manual confirmation checklist

### 9. MVP Source Strategy

The MVP should not try to connect to every academic source.

Recommended first implementation strategy:

- start with a bounded source adapter layer
- allow a mock or local evidence mode first
- design the output model so real connectors can replace mock retrieval later

The source strategy should be accepted only if:

- evidence records are normalized
- source tiering is possible
- citation display is consistent

### 10. MVP Confidence Model

The MVP should not output a single opaque confidence score.

Instead it should expose a small confidence summary:

- `evidence_coverage`
- `source_quality`
- `candidate_separation`
- `conflict_level`

Example:

```json
{
  "evidence_coverage": "medium",
  "source_quality": "medium_high",
  "candidate_separation": "high",
  "conflict_level": "low"
}
```

### 11. MVP Acceptance Criteria

The MVP is acceptable if it can consistently show:

- a clear problem framing
- visible evidence behind candidate topics
- 3 meaningfully different candidate topics
- a comparison that is not repetitive or generic
- a recommendation with explicit limitations
- at least one clear human confirmation step

The MVP is not acceptable if:

- candidates are near duplicates
- recommendations are unsupported
- the UI hides source details
- the system appears authoritative while evidence is weak

### 12. Suggested Implementation Order

1. define schemas and persisted session model
2. create topic-agent route and stub workflow
3. implement mock evidence retrieval and evidence records
4. implement landscape and candidate generation stubs
5. implement comparison and convergence output
6. build a minimal Topic Workspace UI
7. add session inspection and refine flow
8. add evaluation fixtures for MVP tasks

### 13. First Demo Scenario

Input:

- interest: trustworthy multimodal reasoning in medical imaging
- constraints: 6 months, student resources, benchmark-driven

Expected demo output:

- one framed problem summary
- 8 to 15 evidence records
- one landscape summary
- 3 candidate topics
- one comparison matrix
- one recommended topic with backup option
- one manual verification checklist

### 14. Expansion Gates After MVP

Do not expand to broader features until the MVP proves:

- the narrowing workflow is useful
- evidence links are trustworthy enough
- candidate diversity is real
- users understand why one candidate is recommended over another

### 15. Demo And Acceptance References

Use these documents when validating the current MVP slice:

- [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
- [topic_agent_acceptance_walkthrough.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance_walkthrough.md)
