# Topic Agent 需求简报 / Topic Agent Requirement Brief

## 中文版

### 原始需求

请设计一个科研选题副驾子系统 `Topic Agent`，帮助研究者从研究兴趣、问题域或初步想法出发，完成：

- 文献检索
- 方向全景调研
- 候选路径比较
- 收敛与判断支持

最终目标是给出科研选题建议。

关键约束：

1. 不预设输出形式、页面结构和系统架构
2. 可以采用单 Agent、workflow orchestration、多 Agent、RAG、知识图谱或其他方案
3. 系统不必完整实现，但设计逻辑与验收逻辑必须清楚

方案至少需要说明：

1. 目标用户与核心任务
2. 系统边界与能力结构
3. 用户输入与系统输出如何组织
4. 检索、梳理、比较、收敛的核心 workflow
5. 数据源、引用机制、来源分级与冲突处理规则
6. 用户如何验证结果，哪些步骤需要人工确认
7. 评估方案，以及如何判断系统确实帮助了科研选题
8. 可选的 demo、原型、伪代码或接口定义

重点验收的是：

1. 是否能做范围收敛，而不是做成大而全平台
2. 是否能把证据链、结果验证和可信度讲清楚
3. 是否具备工程化和产品化思维

### 仓库中哪些地方体现了这些要求

#### 设计逻辑

- [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
- [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)

#### 当前实现切片

- [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py)
- [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py)
- [topic_agent_runtime.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/topic_agent_runtime.py)

#### 当前进度跟踪

- [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)

### 当前完成度判断

对于当前 design-and-MVP 范围，原始要求大约已覆盖：`85% to 90%`

#### 已经覆盖较好的部分

- target user 与 core task 已较清楚
- 系统范围被明确收窄为 focused topic-exploration workflow
- 输入与输出已围绕 framing、evidence、landscape、candidate、comparison、convergence 组织
- retrieval 和 synthesis workflow 是显式的，而不是藏在单个 prompt 里
- source metadata、source tier、fallback diagnostics、cache diagnostics、supporting evidence link 已实现
- evaluation 与 acceptance 思路已经进入文档
- 当前实现方向体现了比较清楚的工程拆解与产品拆解

#### 设计里覆盖多于产品里覆盖的部分

- human confirmation checkpoint
- final convergence 前的 explicit user validation loop
- 高质量来源之间 disagreement 的更强显式化

#### 尚未完全覆盖的部分

- 能主动 gate framing 与 final recommendation acceptance 的 end-user confirmation UX
- 更丰富的 conflict modeling 与 contradiction summary
- 覆盖多类 topic 的 benchmark-based acceptance harness
- 更正式的 demo / prototype narrative，把设计文档与用户可见 walkthrough 连接起来

### 如何从工程角度理解这道题

比较实用的理解方式是把要求拆成三类：

- 最小闭环里必须有的
- 做得更强时最好有的
- 当前阶段明确不需要的

#### 最小闭环必须有的部分

- 明确的结构化输入：
  - research interest / problem domain
  - seed idea
  - practical constraints
- 显式 framing 或 clarification step，体现 task modeling awareness
- 至少一个真实或可检查的 scholarly source evidence retrieval
- 能把 evidence 组织成子方向的 landscape synthesis，而不是只总结论文
- 2 到 3 个 candidate research direction，并带显式 comparison 维度
- convergence recommendation，能解释：
  - 哪个方向更优先
  - 为什么
  - 有哪些风险
  - 哪些地方仍需人工判断
- 可见的 source reference 与 evidence link

#### 更强提交最好有的部分

- 显式 human confirmation checkpoint
- source grading 与 conflict-handling 规则能被用户看见
- 一条完整 demo walkthrough
- 更清楚地区分：
  - source-backed facts
  - system synthesis
  - tentative inference

#### 当前阶段明确不要求的部分

- 大规模 multi-agent architecture
- 很重的 frontend 或 polished product shell
- 完整知识图谱
- 大规模 production retrieval platform
- 完整 academic-workflow assistant

### 推荐评审阅读顺序

1. 阅读 [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md) 了解产品与系统逻辑
2. 阅读 [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md) 了解验收标准
3. 阅读 [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md) 了解当前实现进度
4. 查看 [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py) 与 [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py) 了解当前后端切片

### 实际验收视角

如果用原始要求来判断当前 Topic Agent，最稳妥的表述是：

- focused workflow 设计已经比较清楚
- evidence chain 比最初清楚很多
- 系统已经能体现 scope-control 与 engineering decomposition
- backend minimum viable closed loop 已基本到位
- 剩余工作主要在 explicit human confirmation、conflict handling 和 product-layer acceptance polish，而不是基础 retrieval workflow 可行性本身

## English Version

### Original Requirement

Please design a research-topic copilot subsystem, `Topic Agent`, to help researchers start from a research interest, problem domain, or seed idea and complete:

- literature retrieval
- landscape exploration
- candidate direction comparison
- convergence and decision support

The final goal is to provide research-topic recommendations.

Important constraints:

1. The output format, page structure, and system architecture are not pre-specified.
2. The solution may use a single agent, workflow orchestration, multi-agent design, RAG, a knowledge graph, or another approach.
3. The system does not need to be fully implemented, but the design logic and acceptance logic must be clear.

The design should at minimum explain:

1. target users and core tasks
2. system boundary and capability structure
3. how user input and system output are organized
4. the core workflow for retrieval, synthesis, comparison, and convergence
5. data sources, citation mechanism, source grading, and conflict handling rules
6. how users validate results and which steps require human confirmation
7. the evaluation plan and how to judge whether the system truly helps topic selection
8. optional demo, prototype, pseudocode, or interface definition

The acceptance focus is:

1. scope narrowing instead of building a large all-in-one platform
2. clear evidence chain, result verification, and credibility handling
3. engineering and product thinking

### Where This Requirement Is Reflected In The Repository

#### Design Logic

- [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
- [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)

#### Current Implementation Slice

- [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py)
- [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py)
- [topic_agent_runtime.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/topic_agent_runtime.py)

#### Current Progress Tracking

- [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md)

### Current Completion Judgment

For the current design-and-MVP scope, the original requirement is approximately `85% to 90%` covered.

#### Already Covered Well

- target users and core tasks are clearly defined
- system scope is intentionally narrowed to a focused topic-exploration workflow
- input and output are structured around framing, evidence, landscape, candidates, comparison, and convergence
- retrieval and synthesis workflow is explicit rather than hidden in a single prompt
- source metadata, source tiers, fallback diagnostics, cache diagnostics, and supporting evidence links are implemented
- evaluation and acceptance thinking are documented
- the implementation direction shows clear engineering and product decomposition

#### Covered In Design More Than In Product

- human confirmation checkpoints
- explicit user validation loops before final convergence
- stronger source-conflict surfacing when good sources disagree

#### Not Yet Fully Covered

- end-user confirmation UX that actively gates framing and final recommendation acceptance
- richer conflict modeling and contradiction summaries across sources
- a broader benchmark-based acceptance harness for multiple topic classes
- a more formal demo or prototype narrative tying the design docs to a user-facing walkthrough

### Practical Must-Have Reading Of The Requirement

The most useful way to interpret the original requirement is to separate:

- what must exist in the minimal closed loop
- what should exist for a stronger submission
- what is explicitly not required for the current phase

#### Must-Have For The Minimal Closed Loop

- a clear structured input entry for:
  - research interest or problem domain
  - seed idea
  - practical constraints
- an explicit framing or clarification step showing task-modeling awareness
- real evidence retrieval from at least one external or curated scholarly source
- a landscape synthesis step that organizes evidence into sub-directions instead of only summarizing papers
- 2 to 3 candidate research directions with explicit comparison dimensions
- a convergence recommendation that explains:
  - which direction is preferred
  - why
  - what risks remain
  - what still needs human judgment
- visible source references and evidence links

#### Should-Have For A Stronger Submission

- explicit human confirmation checkpoints
- source grading and conflict-handling rules surfaced to the user
- a demo walkthrough with one end-to-end example
- clearer separation between:
  - source-backed facts
  - system synthesis
  - tentative inference

#### Not Required For The Current Phase

- a large multi-agent architecture
- a heavy frontend or polished product shell
- a full knowledge graph
- a large-scale production retrieval platform
- a complete academic-workflow assistant

### Recommended Reading Order For Reviewers

1. Read [topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md) for the product and system logic.
2. Read [topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md) for the acceptance criteria.
3. Read [topic_agent_progress.md](/d:/project/research-topic-copilot/docs/topic_agent_progress.md) for the implementation status.
4. Inspect [pipeline.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/pipeline.py) and [providers.py](/d:/project/research-topic-copilot/backend/app/services/topic_agent/providers.py) for the current backend slice.

### Practical Acceptance View

If the current Topic Agent slice is judged against the original requirement, the most defensible claim is:

- the focused workflow design is clear
- the evidence chain is much clearer than at the start
- the system already demonstrates scope-control and engineering decomposition
- the backend minimum viable closed loop is already largely in place
- the remaining work is mainly around explicit human confirmation, conflict handling, and product-layer acceptance polish rather than basic retrieval workflow viability
