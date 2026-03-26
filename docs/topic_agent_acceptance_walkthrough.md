# Topic Agent 验收演示说明 / Topic Agent Acceptance Walkthrough

## 中文版

### 目的

本文档用于给评审、老师或项目审查者提供一份更适合演示的 Topic Agent 讲解顺序。

适用场景：

- demo 演示
- 里程碑评审
- 验收讨论
- 最终提交汇报

目标不是展示一个通用学术助手，而是展示一个聚焦、可解释、可验证的科研选题副驾。

### 评审需要看懂什么

完成 walkthrough 后，评审应该能回答：

1. 系统输入是什么
2. 系统如何做范围收敛，而不是无限发散
3. 证据从哪里来
4. 系统如何把证据变成候选方向
5. 推荐结论为什么成立
6. 哪些地方仍然需要人工确认

### 推荐演示顺序

1. 展示一次 `explore` 请求
2. 查看 framing 和缺失澄清项
3. 查看 evidence 和 diagnostics
4. 查看 landscape synthesis
5. 查看 candidate topics 和 comparison result
6. 查看 convergence result
7. 查看 human confirmations 和 clarification suggestions
8. 如有需要，再展示一次 `refine`

### 演示 A：宽泛 medical reasoning

#### 输入

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

#### 演示重点

- 系统不会把它当作一次模糊闲聊直接回答
- 系统会先规范化 topic 并抽取约束
- evidence retrieval 应优先现代 medical AI reasoning benchmark
- 宽泛 query 的表述应集中在：
  - reasoning verification
  - benchmark validity
  - answer-pattern shortcuts
- 不应漂移到：
  - 老旧 reasoning 文献
  - document-centric wording
  - 用户没有提到的 image-grounded wording

#### 验收信号

如果评审能看到系统把一个宽泛主题收敛成：

- benchmark slice 路线
- applied transfer 路线
- tooling / evaluation 路线

并且每条路线都有清楚的 supporting evidence，这个演示就是成功的。

### 演示 B：窄化的 radiology VQA

#### 输入

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

#### 演示重点

- evidence 应优先 `Med-VQA`、`VQA-RAD`、radiology VQA 相关论文
- landscape themes 应保持窄、保持 benchmark 导向
- candidate wording 应强调：
  - benchmark slicing
  - image-grounded reliability
  - constrained practical transfer

#### 验收信号

如果评审能看到系统保持 topic-specific，而不是塌缩成 generic medical AI overview，这个演示就是成功的。

### 演示 C：以评估为核心的 hallucination query

#### 输入

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

#### 演示重点

- evidence 应偏 grounding、hallucination、faithfulness、evaluation
- candidate directions 应保持 evaluation-centric
- 系统不应漂移到 generic document QA 或宽泛 overview

#### 验收信号

如果评审能看到：

- candidate 1 在收窄 evaluation slice
- candidate 2 在提出 practical evaluation transfer
- candidate 3 在提出 audit workflow 或 reproducibility support

那么这个演示就是成功的。

### 演示 D：Clarification 与 Refine 闭环

#### 初始输入

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

#### 首次返回要看什么

- `missing_clarifications`
- `human_confirmations`
- `clarification_suggestions`

重点在于：系统不会假装缺失约束无所谓，而是明确提示用户补信息。

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

#### Refine 后要看什么

- `missing_clarifications` 变空
- `clarification_suggestions` 变空
- `human_confirmations` 从补信息提示收缩为最终决策确认

#### 验收信号

如果评审能看到真实的 clarification loop，而不是 one-shot answer generator，这个演示就是成功的。

### 需要明确告诉评审的内容

#### 已经比较强的部分

- scope 收得住
- workflow 可检查
- candidate 有 evidence linkage
- 几类关键 query 的行为已经比较稳定
- diagnostics 和 confidence surface 已经存在

#### 仍是部分完成的部分

- 明确的 source conflict summary
- 更完整的 end-user confirmation UX
- 更完整的 acceptance benchmark harness

#### 明确不在当前范围内的部分

- 全学术流程自动化
- proposal writing
- experiment execution
- 大规模 multi-agent orchestration
- 很重的产品外壳或知识图谱基础设施

### 推荐搭配阅读的文档

1. [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
2. [topic_agent_mvp.md](/d:/project/research-topic-copilot/docs/topic_agent_mvp.md)
3. [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)
4. [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
5. [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)

## English Version

### Purpose

This document provides a reviewer-friendly walkthrough for the current Topic Agent slice.

It is designed for:

- demo sessions
- milestone reviews
- acceptance discussions
- final submission walkthroughs

The goal is to show the current system as a focused, evidence-driven topic-selection copilot rather than a generic academic assistant.

### What The Reviewer Should Understand

By the end of the walkthrough, a reviewer should be able to answer:

1. what the system takes as input
2. how it narrows the topic instead of expanding it endlessly
3. where the evidence comes from
4. how the system turns evidence into candidate directions
5. how the recommendation is justified
6. where human confirmation still matters

### Recommended Walkthrough Order

1. show one `explore` request
2. inspect framing and missing clarifications
3. inspect retrieved evidence and diagnostics
4. inspect landscape synthesis
5. inspect candidate topics and comparison result
6. inspect convergence result
7. inspect human confirmations and clarification suggestions
8. optionally show one `refine` cycle

### Walkthrough A: Broad Medical Reasoning

#### Input

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

#### What To Highlight

- the system does not treat this as a vague free-form chat request
- it normalizes the topic and extracts constraints
- evidence retrieval should prioritize modern medical AI reasoning benchmarks
- broad-query wording should stay in:
  - reasoning verification
  - benchmark validity
  - answer-pattern shortcuts
- it should not drift into:
  - legacy reasoning literature
  - document-centric wording
  - image-grounded wording that the user never asked for

#### Acceptance Signal

This walkthrough is successful if the reviewer can see that a broad topic still converges to:

- a benchmark-slice path
- an applied transfer path
- a tooling / evaluation path

with visible supporting evidence for each candidate.

### Walkthrough B: Narrow Radiology VQA

#### Input

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

#### What To Highlight

- evidence should favor `Med-VQA`, `VQA-RAD`, or radiology VQA papers
- landscape themes should stay narrow and benchmark-oriented
- candidate wording should emphasize:
  - benchmark slicing
  - image-grounded reliability
  - practical transfer under constrained resources

#### Acceptance Signal

This walkthrough is successful if the reviewer can see that the system can stay narrow and topic-specific without collapsing into a generic medical AI overview.

### Walkthrough C: Evaluation-Centric Hallucination Query

#### Input

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

#### What To Highlight

- evidence should favor grounding, hallucination, faithfulness, or evaluation records
- candidate directions should stay evaluation-centric
- the system should not drift into broad document QA or generic multimodal overviews

#### Acceptance Signal

This walkthrough is successful if the reviewer can see that:

- candidate 1 narrows the evaluation slice
- candidate 2 proposes a practical evaluation transfer path
- candidate 3 focuses on audit workflow or reproducibility support

### Walkthrough D: Clarification And Refine Loop

#### Initial Input

```json
{
  "interest": "medical reasoning",
  "constraints": {}
}
```

#### What To Highlight On First Response

- `missing_clarifications`
- `human_confirmations`
- `clarification_suggestions`

The important point is that the system does not silently continue as if missing constraints do not matter.

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

#### What To Highlight On Refine Response

- `missing_clarifications` becomes empty
- `clarification_suggestions` becomes empty
- `human_confirmations` shrinks to final decision checks

#### Acceptance Signal

This walkthrough is successful if the reviewer can see a real clarification loop rather than a one-shot answer generator.

### What Reviewers Should Be Told Explicitly

#### What Is Already Strong

- focused scope
- inspectable workflow
- evidence-linked candidates
- stable query-specific behavior on key demo classes
- explicit confidence and diagnostics surfaces

#### What Is Still Partial

- explicit source-conflict summaries
- end-user confirmation UX in a richer frontend flow
- broader acceptance benchmark harness

#### What Is Intentionally Out Of Scope

- full academic workflow automation
- proposal writing
- experiment execution
- large multi-agent orchestration
- heavy product shell or complex knowledge graph infrastructure

### Recommended Supporting Documents

Use these documents alongside the walkthrough:

1. [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
2. [topic_agent_mvp.md](/d:/project/research-topic-copilot/docs/topic_agent_mvp.md)
3. [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)
4. [topic_agent_demo_scenarios.md](/d:/project/research-topic-copilot/docs/topic_agent_demo_scenarios.md)
5. [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)
