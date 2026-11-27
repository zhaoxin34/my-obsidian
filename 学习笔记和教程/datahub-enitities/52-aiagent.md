---
title: AI Agent
entity: aiagent
order: 52
source: https://docs.datahub.com/docs/generated/metamodel/entities/aiagent.md
---

# AI Agent

AI Agent（AI 智能体）是目录中的一等实体，代表一个 AI 智能体——基于一个或多个 LLM 构建、使用工具与技能来完成任务的系统（LangChain agents、Google ADK agents、Snowflake Cortex agents、DataHub 自有的 “Ask DataHub” 助手等）。将智能体编目，可以让团队发现存在哪些智能体、理解它们能做什么以及依赖什么、对它们进行治理，并追踪它们到所触及数据的血缘。

智能体分为三种类型，通过 `aiAgentInfo` aspect 的 `source.type` 区分：

- **System**（`SYSTEM`）：在部署时引导创建（例如通过 YAML），终端用户不可编辑。
- **Native**（`NATIVE`）：由终端用户通过 UI 或 API 在 DataHub 上创建和管理。
- **External**（`EXTERNAL`）：在 DataHub 之外管理，但在此编目以便发现和治理。

这是来源/治理维度，而非功能维度——单智能体、多智能体或 copilot 之类的区分（如有需要）通过标准的 `subTypes` aspect 叠加表达。

## 身份标识

AI Agent 由单个字段标识：

- **id**：智能体的唯一标识符，通常是便于阅读的 slug，如 `ask-datahub` 或生成的 UUID。

示例 URN 为 `urn:li:aiAgent:ask-datahub`。该标识符与平台无关；平台信息（如有）记录在 `dataPlatformInstance` aspect 上，而不是键中。

## 重要能力

### Agent Info

核心属性位于 `aiAgentInfo` aspect 上：

- **name**：显示名称，可通过自动补全搜索。
- **tagline**：约 120 字符的单行简短摘要，显示在智能体卡片、页面主视觉副标题和选择器下拉列表中。若缺失，这些界面会回退为截断描述。
- **description**：智能体做什么，**以及何时应路由到它**。推荐风格为 “X does Y. Use when Z.”——对于路由型智能体（如 Ask DataHub），在决定是否委派时会逐字读取该文本，因此 “Use when…” 这部分至关重要，而非装饰性内容。
- **instructions**：除标准模板文字之外，注入到智能体系统提示中的自定义基础指令。
- **source**：智能体定义的来源（见下文）。
- **created** / **lastModified**：审计时间戳。

### 来源与智能体家族

`source` 字段（一个 `AIAgentSource`）记录智能体的来源 `type`（`SYSTEM` / `NATIVE` / `EXTERNAL`），并可选地记录指向该智能体克隆来源智能体的 `clonedFrom` 引用（`ClonedFromAgent` 关系）。克隆体逐字继承其基座的配置——一套前端模块、一套工具面板、一组指令——仅在所管理的产物上有所不同。将基座智能体及其克隆体以此方式分组，就形成了**智能体家族（Agent Family）**。

### 依赖关系

`aiAgentDependencies` aspect 记录智能体所依赖的内容，形式为到其他一等实体的带类型关系：

- **skills** → 智能体采用的 [Agent Skill](55-agentskill.md 实体（`AgentHasSkill`）。
- **tools** → 智能体调用的 [API](53-api.md 实体（`AgentUsesTool`）。这是一条血缘边：工具位于智能体的上游，构成 `repo → service → api → agent` 链路的一部分。
- **models** → 智能体运行所基于的 `mlModel` 实体（LLM）（`AgentUsesModel`）。

### 版本控制、治理与健康状况

AI Agent 支持标准治理 aspects——所有权、标签、术语表术语、域、结构化属性和机构记忆——同时还支持原生版本控制（`versionProperties`，从而使智能体的连续修订归入一个版本集合）以及通过共享事件子系统的健康状况（`incidentsSummary`）。智能体也可以通过 `upstreamLineage` 参与血缘追踪。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](52-aiagent.md)。
