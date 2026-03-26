# Topic Agent 演示场景 / Topic Agent Demo Scenarios

## 中文版

### 目的

本文档定义了一组稳定的 demo 场景，用于手测、验收评审和项目 walkthrough。

目标不是覆盖所有科研选题请求，而是证明当前 Topic Agent 可以：

- 对 topic 请求做 framing
- 检索可检查的 evidence
- 组织 research landscape
- 比较 candidate directions
- 收敛出 recommendation
- 暴露人工确认点

### 使用方式

对于每个场景：

1. 调用 `POST /api/topic-agent/explore`
2. 检查文档中列出的关键字段
3. 对照预期行为判断是否通过
4. 如有需要，再调用 `POST /api/topic-agent/sessions/{session_id}/refine`

推荐使用的接口：

- `POST /api/topic-agent/explore`
- `POST /api/topic-agent/sessions/{session_id}/refine`
- `GET /api/topic-agent/sessions/{session_id}`

### 场景 1：宽泛 medical reasoning

#### 请求体

```json
{
  "interest": "medical reasoning",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### 为什么重要

这是最核心的 broad-query 压力测试。它检查系统能否保持在现代 medical AI reasoning 语境里，而不是漂移到：

- 过老的 reasoning literature
- document-QA overfitting
- 用户没有要求的 multimodal 或 image-grounded wording

#### 需要检查什么

- `evidence_records`
  - 应优先现代 medical AI benchmark、LLM reasoning evaluation 或 reasoning verification 论文
- `landscape_summary.themes`
  - 不应默认变成 `document QA and report-centric reasoning`
- `candidate_topics[0].research_question`
  - 应提到 reasoning verification 或 benchmark validity
  - 不应提到 `image-grounded`
- `candidate_topics[1].research_question`
  - 不应提到 `document-centric clinical reasoning`
- `likely_gaps`
  - 应优先使用如下表述：
    - reasoning gains
    - answer-pattern shortcuts
    - trustworthy evaluation

#### 预期输出形态

- 一条 benchmark-driven 候选路线
- 一条 applied transfer 候选路线
- 一条 tooling / reproducibility 候选路线
- 在 student-scale applied 约束下，`candidate_2` 往往是推荐路线

### 场景 2：Radiology VQA

#### 请求体

```json
{
  "interest": "trustworthy visual question answering in radiology",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow and feasible benchmark-oriented topic.",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### 为什么重要

这个场景用来检查系统能否在一个具体的 multimodal topic 上保持足够窄、足够 benchmark-oriented。

#### 需要检查什么

- `evidence_records`
  - 应优先 `Med-VQA`、`VQA-RAD`、radiology VQA 或 radiology benchmark evidence
- `landscape_summary.themes`
  - 应包含 radiology VQA 或 image-grounded answer reliability
  - 不应被 generic hallucination wording 主导
- `candidate_topics[0].research_question`
  - 应提到 radiology VQA benchmark slicing
- `candidate_topics[1].research_question`
  - 应保持 radiology VQA method transfer wording

#### 预期输出形态

- candidate 1 强调 benchmark slicing 和 image-grounded answering
- candidate 2 强调在 compute 或 annotation 约束下的 practical transfer

### 场景 3：Hallucination And Grounding Evaluation

#### 请求体

```json
{
  "interest": "hallucination detection and grounding evaluation for multimodal medical reasoning",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow evaluation-focused research topic.",
  "constraints": {
    "time_budget_months": 5,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### 为什么重要

这个场景用来检查 evaluation-centric query 是否仍然聚焦在：

- unsupported answers
- grounding faithfulness
- hallucination auditing

而不是漂移到 generic document QA 或宽泛 overview。

#### 需要检查什么

- `evidence_records`
  - 应包含 grounding、hallucination、evaluation 或 benchmark evidence
- `landscape_summary.themes`
  - 应包含 hallucination 或 grounding
- `candidate_topics[1].research_question`
  - 应提到 unsupported 或 weakly grounded answers
- `candidate_topics[2].open_questions`
  - 应聚焦 audit workflow 和 reproducibility

#### 预期输出形态

- candidate 1 收窄 evaluation slice
- candidate 2 提出实用的 evaluation method transfer
- candidate 3 聚焦 audit tooling 或 reproducibility workflow

### 场景 4：Clarification 与 Refine 闭环

#### 请求体

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

#### 为什么重要

这个场景用来检查系统是否能把缺失信息明确暴露出来，让用户知道如何继续做 `refine`。

#### 需要检查什么

- `framing_result.missing_clarifications`
  - 应包含：
    - `time_budget`
    - `resource_level`
    - `preferred_style`
- `human_confirmations`
  - 应明确提示缺失的 scope 和 feasibility 假设
- `clarification_suggestions`
  - 应包含：
    - `field_key`
    - `prompt`
    - `reason`
    - `suggested_values`
    - `refine_patch`

#### Refine 请求

```json
{
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### Refine 后的预期行为

- `missing_clarifications` 变成 `[]`
- `clarification_suggestions` 变成 `[]`
- `human_confirmations` 从补信息提示收缩成最终 recommendation checks

### 快速验收清单

如果评审能确认以下几点成立，说明当前 Topic Agent 行为基本符合预期：

- broad query 保持在 modern medical-AI reasoning 语境
- radiology VQA query 保持窄且 benchmark-oriented
- hallucination / grounding query 保持 evaluation-centric
- 缺失约束会触发 clarification suggestions
- 补完约束后 clarification suggestions 会消失
- candidate directions 有 source linkage，且确实可比较

## English Version

### Purpose

This document defines a small set of stable demo scenarios for manual validation, acceptance review, and project walkthroughs.

The goal is not to prove full coverage of all research-topic requests. The goal is to show that the current Topic Agent slice can:

- frame a topic request
- retrieve inspectable evidence
- organize a research landscape
- compare candidate directions
- converge to a recommendation
- surface human confirmation points

### How To Use This Document

For each scenario:

1. call `POST /api/topic-agent/explore`
2. inspect the response fields listed under `what to check`
3. compare the response against the expected behavior
4. if needed, continue with `POST /api/topic-agent/sessions/{session_id}/refine`

Recommended API surface:

- `POST /api/topic-agent/explore`
- `POST /api/topic-agent/sessions/{session_id}/refine`
- `GET /api/topic-agent/sessions/{session_id}`

### Scenario 1: Broad Medical Reasoning

#### Request

```json
{
  "interest": "medical reasoning",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### Why This Scenario Matters

This is the main broad-query stress case. It checks whether the system can stay in the modern medical-AI reasoning space without drifting into:

- legacy reasoning literature
- document-QA overfitting
- multimodal or image-grounded wording that the user never asked for

#### What To Check

- `evidence_records`
  - should prefer modern medical AI benchmarks, LLM reasoning evaluations, or reasoning verification papers
- `landscape_summary.themes`
  - should not default to `document QA and report-centric reasoning`
- `candidate_topics[0].research_question`
  - should mention reasoning verification or benchmark validity
  - should not mention `image-grounded`
- `candidate_topics[1].research_question`
  - should not mention `document-centric clinical reasoning`
- `likely_gaps`
  - should prefer wording like:
    - reasoning gains
    - answer-pattern shortcuts
    - trustworthy evaluation

#### Expected Outcome Shape

- a benchmark-driven candidate
- an applied transfer candidate
- a tooling / reproducibility candidate
- `candidate_2` is often the recommended path under student-scale applied constraints

### Scenario 2: Radiology VQA

#### Request

```json
{
  "interest": "trustworthy visual question answering in radiology",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow and feasible benchmark-oriented topic.",
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### Why This Scenario Matters

This checks that the system can stay narrow and benchmark-oriented for a specific multimodal topic.

#### What To Check

- `evidence_records`
  - should prefer `Med-VQA`, `VQA-RAD`, radiology VQA, or radiology benchmark evidence
- `landscape_summary.themes`
  - should include radiology VQA or image-grounded answer reliability
  - should not be dominated by generic hallucination wording
- `candidate_topics[0].research_question`
  - should mention radiology VQA benchmark slicing
- `candidate_topics[1].research_question`
  - should stay in radiology VQA method transfer wording

#### Expected Outcome Shape

- candidate 1 emphasizes benchmark slicing and image-grounded answering
- candidate 2 emphasizes practical transfer under compute or annotation constraints

### Scenario 3: Hallucination And Grounding Evaluation

#### Request

```json
{
  "interest": "hallucination detection and grounding evaluation for multimodal medical reasoning",
  "problem_domain": "medical AI",
  "seed_idea": "I want a narrow evaluation-focused research topic.",
  "constraints": {
    "time_budget_months": 5,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### Why This Scenario Matters

This checks whether evaluation-centric queries stay centered on:

- unsupported answers
- grounding faithfulness
- hallucination auditing

instead of drifting into generic document QA or broad overview wording.

#### What To Check

- `evidence_records`
  - should include grounding, hallucination, evaluation, or benchmark evidence
- `landscape_summary.themes`
  - should include hallucination or grounding
- `candidate_topics[1].research_question`
  - should mention unsupported or weakly grounded answers
- `candidate_topics[2].open_questions`
  - should focus on audit workflow and reproducibility

#### Expected Outcome Shape

- candidate 1 narrows the evaluation slice
- candidate 2 adapts an evaluation method under practical constraints
- candidate 3 focuses on audit tooling or reproducibility workflow

### Scenario 4: Clarification And Refine Loop

#### Request

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

#### Why This Scenario Matters

This checks whether the system surfaces missing information clearly enough for a user to continue with `refine`.

#### What To Check

- `framing_result.missing_clarifications`
  - should include:
    - `time_budget`
    - `resource_level`
    - `preferred_style`
- `human_confirmations`
  - should explicitly ask for missing scope and feasibility assumptions
- `clarification_suggestions`
  - should include:
    - `field_key`
    - `prompt`
    - `reason`
    - `suggested_values`
    - `refine_patch`

#### Refine Request

```json
{
  "constraints": {
    "time_budget_months": 6,
    "resource_level": "student",
    "preferred_style": "applied"
  }
}
```

#### Expected Refine Behavior

- `missing_clarifications` becomes `[]`
- `clarification_suggestions` becomes `[]`
- `human_confirmations` shrinks to final recommendation checks instead of missing-input prompts

### Scenario 5: Non-Medical Bug-Fixing Agent Topic

#### Request

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

#### Why This Scenario Matters

This is the main non-medical generalization check for the current demo slice.

It checks whether the system can:

- stay on software-engineering evidence instead of drifting into generic `agent`, `repair`, or `maintenance` neighbors
- produce usable bug-fixing candidates without image- or radiology-specific wording leaks
- keep the systems candidate focused on reproducible bug-fixing evaluation rather than generic software-engineering wording

#### What To Check

- `evidence_records`
  - should prefer bug-fixing, program-repair, or software-agent evidence
  - should not drift into classroom, logistics, spacecraft, or generic maintenance literature
- `candidate_topics[2].research_question`
  - should mention reproducible bug-fixing agent evaluation
  - should not fall back to generic `software engineering`
- `candidate_topics[*].supporting_source_ids`
  - should reflect at least some role separation between evaluation, method, and systems support

#### Expected Outcome Shape

- candidate 1 reads like an evaluation-narrowing direction
- candidate 2 reads like an applied method-transfer direction
- candidate 3 reads like workflow or reproducibility support for bug-fixing agent evaluation

### Quick Acceptance Checklist

The current Topic Agent slice is behaving as intended if the reviewer can verify all of the following:

- broad queries stay in a modern medical-AI reasoning space
- radiology VQA queries stay narrow and benchmark-oriented
- hallucination / grounding queries stay evaluation-centric
- missing constraints trigger clarification suggestions
- completed constraints remove clarification suggestions
- candidate directions remain source-linked and comparable
- at least one non-medical software-agent topic also produces a credible, inspectable result
