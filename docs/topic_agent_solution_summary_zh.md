# Topic Agent 方案总结与要求回应

## 1. 文档目的

本文档用于针对原始要求，集中说明当前 `Topic Agent` 的方案设计、实现取舍、验收思路，以及当前版本已经达到的完成度。

对应的原始任务是：

- 设计一个科研选题副驾子系统 `Topic Agent`
- 帮助研究者从研究兴趣、问题域或初步想法出发
- 完成文献检索、方向全景调研、候选路径比较，以及收敛与判断支持
- 最终提供科研选题建议

当前我们给出的不是一个“大而全”的学术助手平台，而是一个**聚焦科研选题收敛的工作流子系统**。

## 2. 当前方案一句话概括

当前 `Topic Agent` 方案可以概括为：

**一个以结构化输入为起点、以证据链为核心、以候选方向比较与收敛推荐为终点的科研选题工作流系统。**

它的重点不是自动替用户决定选题，而是把选题过程拆成：

- 问题 framing
- 学术证据检索
- landscape 梳理
- candidate 生成与比较
- convergence recommendation
- trust / diagnostics / human confirmation

从而让“选题建议”具备更强的可解释性、可追溯性和人工可介入性。

## 3. 对原始要求的整体回应

### 3.1 关于“不预设输出形式、页面结构或系统架构”

当前方案确实没有从一开始就锁死为某一种固定架构，而是先收敛出一个最小闭环：

- 后端以工作流管线为核心
- 前端以 demo 页面组织当前结果
- API 输出采用结构化 JSON，而不是单段自然语言

这意味着：

- 页面结构是后续围绕产品演示逐步形成的
- 系统架构采用的是**单后端工作流 + 学术检索 provider + 前端展示层**的组合
- 并没有为了“看起来高级”而引入不必要的多 Agent 或复杂知识图谱

### 3.2 关于“可以自行决定采用单 Agent、工作流编排、多 Agent、RAG、知识图谱或其他方案”

当前方案采取的是：

- **工作流编排为主**
- **外部 scholarly retrieval provider 为检索源**
- **结构化 evidence bundle 为核心中间层**

而不是：

- 重型多 Agent 架构
- 完整知识图谱系统
- 端到端单 prompt 黑盒生成

这个取舍的原因很明确：

- 当前任务重点是选题收敛与证据链，不是复杂 agent 协作本身
- 工作流结构更容易显式暴露 framing、evidence、candidate、recommendation 这些中间结果
- 更符合验收中强调的“范围收敛”“证据链”“工程化思维”

### 3.3 关于“不需要完整实现，但必须让设计逻辑和验收思路清楚”

当前仓库已经不只是设计稿，而是已经实现了一个可运行的最小闭环：

- 有真实 API
- 有 scholarly retrieval provider
- 有 session 持久化
- 有 candidate comparison 和 convergence
- 有 frontend demo 页面

同时，设计逻辑和验收思路也已经通过文档与实现对应起来：

- 设计逻辑：见 `topic_agent_design.md`
- 验收逻辑：见 `topic_agent_acceptance.md`
- 当前进展：见 `topic_agent_progress.md`
- demo 收口：见 `topic_agent_demo_completion_plan.md`

## 4. 对“至少说明”的八项要求逐条回应

### 4.1 目标用户与核心任务

#### 目标用户

当前系统主要面向：

- 有初步研究兴趣但题目尚未收敛的学生
- 需要在给定资源约束下快速形成研究方向的研究者
- 希望从 broad topic 走向 narrow topic 的用户

#### 核心任务

系统聚焦于四类核心任务：

1. 把模糊兴趣转成结构化研究问题
2. 检索并组织与当前 topic 直接相关的学术证据
3. 生成并比较多个候选研究方向
4. 在现实约束下给出收敛建议，并明确哪些点仍需人工确认

### 4.2 系统边界与能力结构

#### 当前系统边界

系统明确不做：

- 全学术流程自动化
- proposal 全文写作
- 实验自动执行
- 一个覆盖所有科研任务的大平台

系统当前只做：

- 选题探索
- 证据组织
- 候选方向比较
- 收敛与判断支持

#### 当前能力结构

当前 `Topic Agent` 能力结构可以分为六层：

1. `Problem Framing`
2. `Evidence Retrieval`
3. `Landscape Synthesis`
4. `Candidate Generation`
5. `Comparison And Convergence`
6. `Trust / Diagnostics / Human Confirmation`

### 4.3 用户输入与系统输出如何组织

#### 用户输入

当前输入是结构化的，核心包括：

- `interest`
- `problem_domain`
- `seed_idea`
- `constraints`
  - `time_budget_months`
  - `resource_level`
  - `preferred_style`
  - `notes`

这样做的目的，是避免系统把选题问题退化成普通聊天问答。

#### 系统输出

当前输出组织成多个显式层次：

- `framing_result`
- `evidence_records`
- `landscape_summary`
- `candidate_topics`
- `comparison_result`
- `convergence_result`
- `evidence_presentation`
- `human_confirmations`
- `clarification_suggestions`
- `trace`
- `confidence_summary`
- `evidence_diagnostics`

这意味着最终给用户看的不是一个黑盒答案，而是一套可拆解的中间结构。

### 4.4 检索、梳理、比较、收敛的核心 workflow

当前核心 workflow 可以概括为：

1. 用户提交 topic 相关输入
2. 系统先做 `frame_problem`
3. 生成搜索问题并调用 retrieval provider
4. 得到 evidence bundle 后做 landscape synthesis
5. 从 evidence bundle 生成 candidate directions
6. 对 candidate 做结构化 comparison
7. 输出 convergence recommendation
8. 同时补充 human confirmations、clarification suggestions、diagnostics

这条 workflow 的关键点在于：

- retrieval 与 synthesis 是分层的
- candidate 不是凭空生成，而是绑定 evidence
- recommendation 不是最后一步“突然出现”的，而是 comparison 之后的收敛输出

### 4.5 数据源、引用机制、来源分级和冲突处理规则

#### 数据源

当前已接入或使用的主要 scholarly source 包括：

- `OpenAlex`
- `arXiv` fallback

#### 引用机制

每条 evidence record 当前都包含：

- `source_id`
- `title`
- `source_type`
- `source_tier`
- `identifier`
- `url`
- `summary`
- `relevance_reason`

candidate、evidence presentation 和 recommendation 都通过 `supporting_source_ids` 与 evidence records 建立关联。

#### 来源分级

当前系统已显式引入：

- `source_tier`
- `source_type`

并在 provider ranking 里增加了：

- evidence role inference
- topic relevance 判断

也就是说，系统已经不再只看“命中关键词”，而是开始判断：

- 这条 evidence 是否真正支撑当前 topic
- 它是 `topic_relevant`、`domain_neighbor` 还是更弱的词面相关结果

#### 冲突处理规则

当前冲突处理还不是完整的强建模版本，但已经具备基础机制：

- `confidence_summary`
- `tentative_inferences`
- `uncertainty_reason`
- `missing_evidence`

也就是说，当前系统已经能把“不确定”显式暴露出来，但还没有形成完整的“多来源冲突总结器”。

### 4.6 用户如何验证结果，哪些步骤需人工确认

当前验证机制主要体现在三层：

#### 第一层：证据可追溯

用户可以直接检查：

- evidence record 本身
- supporting source ids
- source facts / system synthesis / tentative inferences 的区别

#### 第二层：人工确认点显式暴露

系统会给出：

- `human_confirmations`
- `manual_checks`
- `clarification_suggestions`

这意味着系统不会假装“一切都自动完成”，而是明确指出：

- 哪些条件还缺失
- 哪些判断仍需人工确认

#### 第三层：流程诊断

系统还会暴露：

- `trace`
- `requested_provider`
- `used_provider`
- `fallback_used`
- `record_count`
- `cache_hit`

这样用户不仅能看结果，还能看“结果是怎么来的”。

### 4.7 评估方案，以及如何判断系统真的帮助了科研选题

当前的评估思路不是只看“模型答得像不像”，而是看系统是否在选题任务上形成有效闭环。

可以从以下几个角度判断：

#### 1. 范围是否收敛

判断系统是否把 broad topic 收敛成若干可比较、可执行的 narrow candidate。

#### 2. 证据链是否清楚

判断 candidate 和 recommendation 是否都能回到明确 evidence，而不是空泛生成。

#### 3. 推荐是否可解释

判断 recommendation 是否能明确说明：

- 为什么推荐
- 为什么不是其他候选
- 还缺什么证据
- 哪些地方需要人工确认

#### 4. 输出是否支持真实决策

判断用户能否基于结果继续做下一步，比如：

- 选定一个 candidate 继续深入
- 发现 topic 太宽需要 refine
- 知道哪些 benchmark / dataset 需要确认

当前的 demo 和 acceptance 文档已经把这些作为主要验收信号。

### 4.8 可选：demo、原型、伪代码或接口定义

当前项目已经具备：

- 可运行 backend API
- React frontend demo
- Topic Agent session history
- demo scenarios
- acceptance walkthrough

对应接口已经存在：

- `POST /api/topic-agent/explore`
- `GET /api/topic-agent/sessions`
- `GET /api/topic-agent/sessions/{session_id}`
- `POST /api/topic-agent/sessions/{session_id}/refine`

也就是说，这一项不是停留在“概念草图”，而是已经有了可运行 demo。

## 5. 对重点验收要求的回应

### 5.1 是否做了范围收敛，而不是做成大而全平台

当前方案的核心优点之一就是**范围收敛明确**。

我们没有把系统扩展成：

- 通用科研写作助手
- 全流程学术自动化平台
- 大而全的多 Agent 学术工作台

而是聚焦在：

- 选题探索
- 候选比较
- 收敛支持

这与原始验收要求高度一致。

### 5.2 是否把结果验证、证据链和可信度讲清楚

这是当前方案的第二个核心优点。

当前系统已经显式提供：

- evidence records
- supporting source ids
- source facts / system synthesis / tentative inferences
- confidence summary
- diagnostics
- trace

因此，当前版本虽然还不是完整冲突建模系统，但已经能把“证据链、验证路径、可信度层次”讲清楚。

### 5.3 是否具备工程化和产品化思维

当前方案已经体现了比较明确的工程化和产品化取向：

#### 工程化

- 结构化 API
- provider fallback
- session persistence
- report retention / session retention
- tests
- staged pipeline

#### 产品化

- 前端 demo 页面按用户阅读顺序组织
- recommendation 优先于内部细节
- recent runs 支持回看
- trust panel 区分事实、综合和暂定判断
- 明确当前版本 freeze backend，转向 demo completion

也就是说，当前方案不是“只会写 prompt”，而是已经具备较清晰的系统拆分和交付意识。

## 6. 当前完成度与边界判断

当前最稳妥的判断是：

- 对 design-and-MVP 范围，当前 Topic Agent 方案已经完成约 `85% to 90%`

当前已经比较扎实的部分：

- 结构化输入
- framing
- scholarly retrieval
- evidence bundle
- landscape summary
- candidate comparison
- convergence recommendation
- trust / diagnostics surface
- frontend demo

当前仍然保留的边界与限制：

- comparison / convergence 层仍然带有固定三候选框架痕迹
- source conflict 还没有做强建模
- 一些 broad topic 上 candidate wording 仍可能需要人工润色
- 用户确认流程在产品层面还不是强制式 UX

这些限制不会推翻当前方案成立，但说明当前版本更适合作为：

- 一个清晰可运行的选题工作流原型

而不是：

- 一个已经完全成熟的科研选题产品

## 7. 结论

如果用一句话总结当前方案：

**我们给出的不是一个大而全的学术平台，而是一个围绕科研选题决策构建的、证据链驱动的、可解释的工作流子系统。**

它已经能够回应原始要求中的关键点：

- 有明确目标用户和核心任务
- 有清晰系统边界与能力结构
- 有结构化输入输出
- 有显式 retrieval-to-convergence workflow
- 有 evidence / citation / diagnostics / human confirmation
- 有验收逻辑与 demo 落地

因此，当前方案是一个具有设计逻辑、实现基础、验收思路和产品雏形的 `Topic Agent` 子系统方案。
