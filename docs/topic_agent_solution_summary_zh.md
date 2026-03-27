# Topic Agent 方案总结与要求回应

## 1. 文档目的

本文用于集中说明当前 `Topic Agent` 的设计思路、实现取舍、系统边界与验收逻辑，并逐条回应原始作业要求。

需要先说明的是：当前项目并不是完全从零开始搭建，而是基于我此前的工程基础项目 `agent-knowledge-system` 继续开发和收敛而来。

基础项目仓库：
- https://github.com/xiandaiweijifen/agent-knowledge-system

本次工作的重点，不是重复建设底层运行时，而是在既有工程基础上，围绕“科研选题副驾子系统 `Topic Agent`”完成以下工作：

- 收敛任务边界，明确系统只服务于科研选题探索与判断支持
- 接入 scholarly retrieval 与 evidence workflow
- 形成 candidate comparison 与 convergence 支持链路
- 补充 trust、diagnostics 与前端展示层

因此，下面的说明应理解为：**在既有 agent system 基座之上，新增加并完成交付收口的 Topic Agent 子系统方案。**

## 2. 当前方案概括

当前 `Topic Agent` 可以概括为：

**一个以结构化输入为起点、以证据链为中间层、以候选方向比较与收敛建议为核心输出的科研选题决策支持子系统。**

它的重点不是替研究者自动决定选题，而是把“选题”这件事拆成一条可以检查、可以追溯、可以人工介入的工作流，包括：

- 问题 framing
- 学术证据检索
- landscape 梳理
- candidate 生成与比较
- convergence recommendation
- trust / diagnostics / human confirmation

## 3. 对原始要求的整体回应

### 3.1 关于“不预设输出形式、页面结构或系统架构”

当前方案并不是先固定某一种技术形态，再强行把问题塞进去，而是先收敛出一个最小可运行闭环：

- 后端以工作流管线为核心
- 前端以结构化结果展示为核心
- API 输出采用分层 JSON，而不是单段自然语言

这意味着：

- 页面结构是围绕任务目标逐步收敛出来的
- 系统架构采用的是“工作流后端 + scholarly retrieval provider + 前端展示层”的组合
- 没有为了形式复杂度而引入不必要的重型多 Agent 或知识图谱系统

### 3.2 关于“可以自行决定采用单 Agent、工作流编排、多 Agent、RAG、知识图谱或其他方案”

当前方案的核心选择是：

- **以工作流编排为主**
- **以 scholarly retrieval provider 作为证据来源入口**
- **以结构化 evidence bundle 作为核心中间层**

而不是：

- 重型多 Agent 协作架构
- 完整知识图谱平台
- 单 prompt 端到端黑盒生成

这样取舍的原因很明确：

- 当前任务重点是选题收敛与判断支持，而不是 agent 协作本身
- 工作流结构更容易显式暴露 framing、evidence、candidate、recommendation 等关键中间结果
- 更符合题目强调的范围收敛、证据链表达和工程化思维

### 3.3 关于“不需要完整实现，但必须让设计逻辑和验收思路清楚”

当前仓库已经不只是概念方案，而是实现了一个可运行的最小闭环：

- 有真实 API
- 有 scholarly retrieval provider
- 有 session 持久化
- 有 candidate comparison 与 convergence
- 有 frontend demo 页面

同时，设计逻辑和验收思路也通过文档明确表达：

- 设计逻辑：`topic_agent_design.md`
- 验收逻辑：`topic_agent_acceptance.md`
- 当前进展：`topic_agent_progress.md`
- 交付收口：`topic_agent_demo_completion_plan.md`

## 4. 对八项要求的逐条回应

### 4.1 目标用户与核心任务

#### 目标用户

当前系统主要面向：

- 有初步研究兴趣，但题目尚未收敛的学生或研究者
- 需要在时间、资源、风格等现实约束下快速形成可执行方向的用户
- 希望从 broad topic 走向 narrow topic 的科研探索者

#### 核心任务

系统聚焦四类核心任务：

1. 把模糊兴趣转成结构化研究问题
2. 检索并组织与当前 topic 相关的学术证据
3. 生成并比较多个候选研究方向
4. 在现实约束下给出收敛建议，并明确哪些点仍需人工确认

### 4.2 系统边界与能力结构

#### 系统边界

当前系统明确不做：

- 全学术流程自动化
- proposal 全文写作
- 实验自动执行
- 覆盖所有科研任务的大平台

当前系统只做：

- 选题探索
- 证据组织
- 候选方向比较
- 收敛与判断支持

#### 能力结构

当前 `Topic Agent` 的能力结构可以分为六层：

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

这样设计是为了避免系统把选题问题退化成普通聊天问答。

#### 系统输出

当前输出按显式层次组织，包括：

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

因此最终给用户的不是一个黑盒答案，而是一套可拆解、可检查的中间结构。

### 4.4 检索、梳理、比较、收敛的核心 workflow

当前核心 workflow 可以概括为：

1. 用户提交 topic 相关输入
2. 系统执行 `frame_problem`
3. 生成搜索问题并调用 retrieval provider
4. 获得 evidence bundle 后执行 landscape synthesis
5. 基于 evidence 生成 candidate directions
6. 对 candidate 做结构化 comparison
7. 输出 convergence recommendation
8. 同时补充 human confirmations、clarification suggestions 与 diagnostics

这条 workflow 的关键点在于：

- retrieval 与 synthesis 是分层的
- candidate 不是凭空生成，而是绑定 evidence
- recommendation 不是最后突然出现，而是 comparison 之后的收敛输出

### 4.5 数据源、引用机制、来源分级和冲突处理规则

#### 数据源

当前已接入或使用的 scholarly source 包括：

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

并在 provider ranking 中加入：

- evidence role inference
- topic relevance 判断

也就是说，系统不再只看“是否命中关键词”，而是开始判断：

- 这条 evidence 是否真正支撑当前 topic
- 它属于 `topic_relevant`、`domain_neighbor` 还是更弱的词面相关结果

#### 冲突处理

当前冲突处理还不是完整的强建模版本，但已经具备基础机制：

- `confidence_summary`
- `tentative_inferences`
- `uncertainty_reason`
- `missing_evidence`

也就是说，当前系统已经能够显式暴露“不确定”，但还没有形成完整的多来源冲突汇总器。

### 4.6 用户如何验证结果，哪些步骤需人工确认

当前验证机制主要体现在三层。

#### 第一层：证据可追溯

用户可以直接检查：

- evidence record 本身
- supporting source ids
- source facts / system synthesis / tentative inferences 的区分

#### 第二层：人工确认点显式暴露

系统会给出：

- `human_confirmations`
- `manual_checks`
- `clarification_suggestions`

这意味着系统不会假装“一切都自动完成”，而是明确指出：

- 哪些条件仍缺失
- 哪些判断仍需人工确认

#### 第三层：流程诊断

系统还会暴露：

- `trace`
- `evidence_diagnostics`
- `cache_hit`
- `used_provider`
- `record_count`

这让用户能够区分：

- 当前结果是 fresh retrieval 还是缓存命中
- 当前用了哪个 provider
- 系统实际经过了哪些阶段

### 4.7 评估方案，以及如何判断系统真的帮助了科研选题

当前的评估思路不是只看“回答是否通顺”，而是看系统是否真的提升了选题收敛质量。

可以从四类指标判断：

#### 1. 结构完整性

系统是否稳定输出：

- framing
- evidence
- landscape
- candidate comparison
- convergence recommendation

#### 2. 证据质量

关注：

- evidence 是否贴题
- supporting source 是否可追溯
- 是否存在明显领域漂移
- 是否能区分 source fact 与 inference

#### 3. 决策支持价值

关注：

- candidate 之间是否真的可比较
- recommendation 是否有清楚理由
- manual checks 是否能帮助用户判断下一步

#### 4. 产品可用性

关注：

- 输入是否足够明确
- 页面是否便于检查证据与推荐
- recent runs、diagnostics、trust panels 是否帮助用户理解结果

如果一个系统只能“说得像答案”，但不能帮助用户更快形成更稳的选题判断，那它就没有真正完成这个任务。

### 4.8 可选项：demo、原型、接口定义

当前仓库已经提供：

- demo 页面
- 前后端原型
- 结构化 API 输出
- 会话持久化与 recent runs
- 中文总结文档与 README 入口

因此这一项不是停留在概念层，而是已经有可演示的交付形态。

## 5. 对重点验收点的回应

### 5.1 是否做到了范围收敛，而不是大而全平台

当前方案明确做到了范围收敛。

系统只聚焦：

- 研究兴趣到问题 framing
- scholarly evidence gathering
- landscape summary
- candidate comparison
- convergence support

没有扩展到：

- 全流程科研自动化
- 大规模知识管理平台
- 自动实验代理系统

### 5.2 是否把结果验证、证据链和可信度讲清楚

当前方案把这三点作为核心设计要求，而不是附属功能。

对应机制包括：

- evidence records
- supporting source ids
- source facts / system synthesis / tentative inferences 分层
- trust / diagnostics 面板
- human confirmations 与 manual checks

也就是说，系统不是只输出“结论”，而是同时输出结论的支撑结构与不确定性边界。

### 5.3 是否具备工程化和产品化思维

当前方案在工程与产品两个层面都做了明确收敛。

工程上：

- 有后端 API
- 有 provider fallback
- 有 session persistence
- 有 diagnostics
- 有测试与回归

产品上：

- 输入是结构化的，而不是泛聊天入口
- 输出按任务阶段分层展示
- recent runs、trust、evidence inspection 等界面都围绕“可检查、可比较、可收敛”设计

因此，这不是一个只停留在概念描述中的方案，而是一个已经具备工程原型和交付表达能力的子系统。

## 6. 当前完成度与边界说明

当前版本已经完成了一个可以演示、可以检查、可以说明设计逻辑的交付切片，但它仍然不是最终成熟产品。

当前已经完成的部分包括：

- 结构化输入与问题 framing
- scholarly retrieval provider 接入
- evidence bundle 组织
- candidate generation / comparison / convergence
- trust / diagnostics / human confirmation
- frontend demo 展示

仍然保留边界的部分包括：

- 更强的冲突建模
- 更丰富的数据源接入
- 更长期的选题跟踪与协作能力
- 更正式的研究评估数据闭环

因此，更准确的定位是：

**当前项目已经完成了一个聚焦、可运行、可验收的 Topic Agent 子系统原型，并且能够较完整地展示设计逻辑、证据链结构与工程实现路径。**

## 7. 当前 Retrieval 状态补充

在后续实现中，retrieval 这条线已经继续推进到一个比较适合收口的状态。

当前 retrieval 不是简单的“发一个 query 拿几条结果”，而是具备了以下能力：

- staged provider retrieval
- query routes 与 route-level diagnostics
- lightweight route-aware fusion
- query-family-aware candidate hygiene
- anchor-preserving query rewrites
- issue-resolution family 的更严格 same-task qualification
- request-level `disable_cache` 调试开关
- limited clean backfill

这些增强的实际意义是：

- 对 software-agent / repository-repair 这类 query，系统不再那么容易被泛 workflow、泛 collaborative engineering、泛 software-security 邻居带偏
- retrieval 结果对 downstream candidate comparison 和 convergence 的污染明显减少
- 手测时不必反复修改请求体来绕过缓存，可以直接用 `disable_cache=true`
- final evidence pool 在高纯度前提下不至于收得过紧，必要时可以补回少量干净候选

因此，当前版本的更准确描述是：

- retrieval 已经从“容易漂移的演示级实现”提升到了“可解释、可调试、可阶段性收口的工程化实现”
- 后续如果没有新的真实 query family 暴露回归，项目重点应优先转向 demo 表达、文档质量与交付收尾，而不是继续无边界地调 retrieval
