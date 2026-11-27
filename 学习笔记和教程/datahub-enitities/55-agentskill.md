---
title: 智能体技能
entity: agentskill
order: 55
source: https://docs.datahub.com/docs/generated/metamodel/entities/agentskill.md
---

# Agent Skill

Agent Skill（智能体技能）是 AI 智能体所采用的、高层次的可复用能力包——专门化的提示/指令，加上应用它们所需的工具。技能比工具高一个层级：工具是单个可调用单元，而技能把领域专业知识（“怎么做”和“何时做”）与其依赖的底层工具打包在一起。同一个技能可被许多智能体采用，因此将其建模为独立实体，可以避免在每个智能体上重复这些专业知识。

技能遵循“以 git 作为事实来源”的模式（例如 agentskills.io 标准）：技能定义在仓库中，并在 DataHub 中编目以便发现、治理和复用。

## 身份标识

Agent Skill 由单个字段标识：

- **id**：技能的唯一标识符，通常是便于阅读的 slug，如 `customer-service-skill` 或生成的 UUID。

示例 URN 为 `urn:li:agentSkill:customer-service-skill`。

## 重要能力

### Skill Info

`agentSkillInfo` aspect 承载技能的定义：

- **name**：显示名称，可通过自动补全搜索。
- **description**：技能做什么，以及何时使用它。
- **instructions**：技能 `SKILL.md` 文件的 markdown 正文（不含 YAML frontmatter）——即技能被激活时加载的执行指引。
- **sourceRepository**：技能定义所在的位置（见下文）。
- **requiredTools**：该技能运行所需的 [API](53-api.md 实体（`SkillRequiresTool`）。
- **created** / **lastModified**：审计时间戳。

### 来源仓库

`sourceRepository` 字段（一个 `SkillSourceRepository`）指向拥有该技能定义的 git 位置。它携带 `repositoryUrn`（首选，当 [Repository](54-repository.md 已在 DataHub 中编目时）或外部 `url`，以及指向仓库内定义文件的 `path`（例如 `customer-service/SKILL.md`）。

### 与智能体的关系

智能体通过其 `aiAgentDependencies` aspect 上声明的 `AgentHasSkill` 关系采用技能——因此 Agent Skill 概况页会展现使用它的智能体，而技能本身又暴露其所需工具。这使得 agent → skill → tool 链路可以从任一端遍历。

### 治理与版本控制

Agent Skill 支持标准治理 aspects——所有权、标签、术语表术语、域、结构化属性和机构记忆——并支持原生版本控制（`versionProperties`）。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](55-agentskill.md)。
