# Research Topic Copilot

## Demo Video

Topic Agent demo video location:

- Local demo folder: [docs/demo](d:/project/research-topic-copilot/docs/demo)
- Recommended video file: [docs/demo/topic-agent-demo.mp4](d:/project/research-topic-copilot/docs/demo/topic-agent-demo.mp4)

If the video is hosted externally later, replace the local file reference above with the final public link.

Research Topic Copilot is a local-first agent system for research topic exploration, evidence gathering, candidate direction comparison, and topic convergence support.

This repository currently contains a reusable agent runtime baseline:

- document ingestion and local artifact persistence
- retrieval with diagnostics and lightweight reranking
- agent routing, tool planning, and workflow orchestration
- persisted workflow runs, recovery semantics, and trace inspection
- evaluation datasets, reports, and a frontend console

The next product direction is a focused sub-system: `Topic Agent`.
It is intended to help a researcher start from a broad interest, problem domain, or rough idea, then move through:

1. literature retrieval
2. landscape synthesis
3. candidate topic generation
4. candidate comparison
5. convergence and decision support

This project is not intended to become a general-purpose academic platform. The scope is intentionally narrower: a decision-support copilot for research topic selection with explicit evidence chains and human checkpoints.

## Current Repository Status

The current codebase is a strong runtime baseline, not yet a finished research-topic product.

Implemented today:

- FastAPI backend and React frontend
- local document upload, preview, chunking, and embeddings
- retrieval-backed question answering
- tool-style execution through local adapters
- workflow planning with fallback paths
- persisted workflow runs and recovery lineage
- benchmark datasets and evaluation dashboards

Still to be added for the new direction:

- academic-source connectors and retrieval adapters
- evidence model for citation-grade outputs
- research-landscape synthesis workflows
- candidate topic comparison and convergence logic
- user-facing verification and confidence surfaces
- topic-selection evaluation methodology

## Initial Design Direction

The planned `Topic Agent` should focus on a small number of user tasks:

- turn a vague interest into a researchable problem framing
- collect and organize supporting evidence from high-value sources
- compare several candidate research directions with explicit tradeoffs
- help the user converge while keeping the final decision human-owned

Planned system modules:

- `Problem Framing`: normalize user intent, constraints, and research goals
- `Evidence Retrieval`: search papers, surveys, datasets, benchmarks, and code artifacts
- `Landscape Synthesis`: identify main themes, active methods, open gaps, and saturated areas
- `Candidate Generation`: produce several candidate topic paths rather than one answer
- `Comparison And Convergence`: compare novelty, feasibility, evidence support, and risk
- `Verification Layer`: expose citations, source grades, conflicts, and manual confirmation steps

## Documentation

- Architecture baseline: [docs/architecture.md](/d:/project/research-topic-copilot/docs/architecture.md)
- Roadmap: [docs/roadmap.md](/d:/project/research-topic-copilot/docs/roadmap.md)
- Topic Agent initial design: [docs/topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
- Topic Agent acceptance plan: [docs/topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)
- Topic Agent MVP plan: [docs/topic_agent_mvp.md](/d:/project/research-topic-copilot/docs/topic_agent_mvp.md)

## Local Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH='.'
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

- Console: `http://127.0.0.1:5173`

## Environment

Create a repo-root `.env` file based on `.env.example`.

Minimal fallback setup:

```env
APP_ENV=development
EMBEDDING_PROVIDER=mock
CHAT_PROVIDER=fallback
TOOL_PLANNER_PROVIDER=fallback
CLARIFICATION_PLANNER_PROVIDER=fallback
WORKFLOW_PLANNER_PROVIDER=fallback
```

## Project Structure

- `backend/`: FastAPI backend and agent runtime
- `frontend/`: React console
- `data/`: local raw documents, chunks, embeddings, eval datasets, and persisted runtime state
- `docs/`: architecture, roadmap, and design notes
- `scripts/`: local development and evaluation helpers

## 中文说明

# Research Topic Copilot

Research Topic Copilot 是一个本地优先的科研选题副驾系统，目标是支持研究兴趣探索、证据收集、候选方向比较，以及选题收敛判断。

当前仓库已经具备一套可复用的 agent runtime 基线：

- 文档摄取与本地产物持久化
- 带诊断能力的检索与轻量 rerank
- agent 路由、工具规划与工作流编排
- 工作流运行记录、恢复语义与轨迹追踪
- 评测数据集、报告和前端控制台

接下来的产品方向会收敛到一个明确子系统：`Topic Agent`。
它希望帮助研究者从“研究兴趣 / 问题域 / 初步想法”出发，逐步完成：

1. 文献检索
2. 方向全景梳理
3. 候选选题生成
4. 候选路径比较
5. 收敛与判断支持

这个项目不会被设计成“大而全”的科研平台。范围会刻意收敛为：一个强调证据链、引用、人工确认和可信度表达的科研选题决策副驾。

## 当前仓库状态

现有代码库更像一个扎实的 runtime 基座，还不是完整的科研选题产品。

已经具备：

- FastAPI 后端与 React 前端
- 本地文档上传、预览、切块与 embedding
- 基于检索的问答链路
- 本地 adapter 风格的工具执行
- 带 fallback 的工作流规划
- 持久化 workflow run 与恢复链路
- benchmark 数据集与评测看板

面向新方向仍需新增：

- 学术数据源连接器与检索适配器
- 面向引用输出的 evidence 数据模型
- 方向全景梳理 workflow
- 候选选题比较与收敛逻辑
- 用户验证入口与可信度展示
- “是否真的帮助科研选题”的评测方法

## 初步设计方向

规划中的 `Topic Agent` 只聚焦少数几个核心任务：

- 把模糊兴趣转化为可研究的问题 framing
- 从高价值来源中收集并组织证据
- 生成多个候选选题路径，而不是只给一个答案
- 用显式 tradeoff 帮助用户收敛，但最终判断仍由人完成

建议的系统模块：

- `Problem Framing`：整理用户意图、约束和研究目标
- `Evidence Retrieval`：检索论文、综述、数据集、benchmark 和代码资源
- `Landscape Synthesis`：梳理主题、主流方法、空白点和已饱和方向
- `Candidate Generation`：生成多个候选选题路径
- `Comparison And Convergence`：比较新颖性、可行性、证据强度和风险
- `Verification Layer`：展示引用、来源分级、冲突信息与人工确认点

## 文档入口

- 架构基线：[docs/architecture.md](/d:/project/research-topic-copilot/docs/architecture.md)
- 规划路线：[docs/roadmap.md](/d:/project/research-topic-copilot/docs/roadmap.md)
- Topic Agent 初步设计：[docs/topic_agent_design.md](/d:/project/research-topic-copilot/docs/topic_agent_design.md)
- Topic Agent 验收规划：[docs/topic_agent_acceptance.md](/d:/project/research-topic-copilot/docs/topic_agent_acceptance.md)
- Topic Agent MVP 规划：[docs/topic_agent_mvp.md](/d:/project/research-topic-copilot/docs/topic_agent_mvp.md)

## 本地启动

### 后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH='.'
uvicorn app.main:app --reload
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

## 环境配置

在仓库根目录基于 `.env.example` 创建 `.env`。

最小 fallback 配置：

```env
APP_ENV=development
EMBEDDING_PROVIDER=mock
CHAT_PROVIDER=fallback
TOOL_PLANNER_PROVIDER=fallback
CLARIFICATION_PLANNER_PROVIDER=fallback
WORKFLOW_PLANNER_PROVIDER=fallback
```

## 目录结构

- `backend/`：FastAPI 后端与 agent runtime
- `frontend/`：React 控制台
- `data/`：本地文档、chunks、embeddings、评测数据和运行状态
- `docs/`：架构、路线图与设计文档
- `scripts/`：本地开发与评测辅助脚本
