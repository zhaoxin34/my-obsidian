---
title: AI 智能体
entity: aiagent
order: 52
source: https://docs.datahub.com/docs/generated/metamodel/entities/aiagent.md
---

# AI 智能体

AI 智能体（AI Agent）是一等公民目录实体，代表一个 AI 智能体——即构建在一个或多个 LLM 之上、使用工具和技能来完成任务
的系统（LangChain agents、Google ADK agents、Snowflake Cortex agents、DataHub 自有的 "Ask DataHub" 助手等）。
将智能体编目，可以让团队发现有哪些智能体存在、弄清它们能做什么以及依赖什么、对它们进行治理，并追踪它们到所触及数据的血缘。

智能体分为三种类型，区别在于 `aiAgentInfo` aspect 的 `source.type`：

- **System**（`SYSTEM`）：在部署时引导创建（例如通过 YAML），终端用户不可编辑。
- **Native**（`NATIVE`）：由终端用户通过 UI 或 API 在 DataHub 上创建和管理。
- **External**（`EXTERNAL`）：在 DataHub 之外管理，但在此编目以便发现和治理。

这是来源／治理维度，而非功能维度——单智能体、多智能体或 copilot 之类的区分（如有需要）通过标准的 `subTypes` aspect 叠加表达。

## 标识

AI 智能体由单个字段标识：

- **id**：智能体的唯一标识符，通常是可读的 slug，例如 `ask-datahub`，或生成的 UUID。

一个示例 URN 是 `urn:li:aiAgent:ask-datahub`。该标识符与平台无关；平台（如有）承载在 `dataPlatformInstance` aspect 上，而非键中。

## 重要能力

### 智能体信息

核心属性位于 `aiAgentInfo` aspect 上：

- **name**：显示名称，支持自动补全搜索。
- **tagline**：约 120 字符的单行简短摘要，显示在智能体卡片、标题栏副标题和选择器下拉列表中。缺失时，界面会退化为截断描述。
- **description**：智能体做什么，**以及何时应路由到它**。推荐风格是
  "X does Y. Use when Z."——对于路由型智能体（如 Ask DataHub），在决定是否委派时会逐字读取该文本，因此
  "Use when…" 这一部分至关重要，而非装饰性内容。
- **instructions**：注入到智能体系统提示中、超出标准模板之外的定制基础指令。
- **source**：智能体定义的来源（见下文）。
- **created** / **lastModified**：审计时间戳。

### 来源与智能体家族

`source` 字段（一个 `AIAgentSource`）记录智能体的来源 `type`（`SYSTEM` / `NATIVE` /
`EXTERNAL`），并可选地记录一个指向该智能体克隆来源的 `clonedFrom` 引用
（即 `ClonedFromAgent` 关系）。克隆体逐字继承其基座的配置——一个前端模块、一套工具面板、一组指令——
差异仅在于它们所管理的产物。以这种方式将基座智能体与其克隆体归为一组，即构成一个**智能体家族**。

### 依赖关系

`aiAgentDependencies` aspect 以指向其他一等公民实体的类型化关系捕获智能体所依赖的内容：

- **skills** → 智能体采用的 [Agent Skill](55-agentskill.md) 实体（`AgentHasSkill`）。
- **tools** → 智能体调用的 [API](53-api.md) 实体（`AgentUsesTool`）。这是一条血缘边：工具位于智能体的上游，
  构成 `repo → service → api → agent` 链路。
- **models** → 智能体运行所依赖的 `mlModel` 实体（即 LLM）（`AgentUsesModel`）。

### 版本控制、治理与健康状态

AI 智能体支持标准治理 aspects——所有权、标签、术语表术语、域、结构化属性和机构记忆——
以及原生版本控制（`versionProperties`，使智能体的连续修订归入一个版本集合），并通过共享的 incidents
子系统（`incidentsSummary`）提供健康状态。智能体也可以通过 `upstreamLineage` 参与血缘。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](52-aiagent.md)。
