---
title: 代码仓库
entity: repository
order: 54
source: https://docs.datahub.com/docs/generated/metamodel/entities/repository.md
---

# Repository

Repository（代码仓库）是源代码仓库（GitHub、GitLab、内部 SCM 等）的一等表示。它是**软件到数据生命周期的起源节点**——`repo → service → api → app → dataset`——并产出编目在其他地方的 [Service](51-service.md、[API](53-api.md 和 [Application](35-application.md。Repository 不是表格类资产：它没有列、查询、统计、质量或预览。

## 身份标识

Repository 由单个字段标识：

- **id**：仓库的唯一标识符。按约定为 `<platform>.<org>/<name>`（例如 `github.acme/payments`、`gitlab.acme/data-platform`）；原生仓库或平台未知的仓库可以省略平台前缀。

示例 URN 为 `urn:li:repository:github.acme/payments`。该键本身与平台无关——平台信息记录在 `dataPlatformInstance` aspect 上，而不是键中。

## 重要能力

### Repository Properties

`repositoryProperties` aspect 承载描述性元数据：

- **name**：显示名称，可通过自动补全搜索。
- **description**：该仓库包含什么。
- **defaultBranch**：默认分支（例如 `main`、`master`）。
- **languages**：所使用的编程语言，约定按普遍程度从高到低排序（仓库常为多语言，因此这是一个列表）。
- **license**：仓库的许可证（例如 `Apache-2.0`、`MIT`）。
- **homepageUrl**：指向仓库主页或文档的链接。
- **archived**：该仓库是否已归档（只读 / 不再维护）。
- **created** / **lastModified**：审计时间戳。

### 来源绑定

`repositorySource` aspect 记录仓库存放位置以及其在源系统中的标识方式：`externalUrl`（网页或克隆 URL）与 `externalId`（例如 GitHub 的数字仓库 ID 或 `org/name` slug）。

### 血缘

`repositoryLineage` aspect 记录仓库之间的来源关系——目前为 `forkOf`，即该仓库是其 git fork 的来源仓库（`RepositoryForkOf`）。

除 fork 血缘之外，Repository 是软件到数据链路的上游锚点：它产出的 Service 和 API 通过各自的 `SourcedFrom` 边指回它，[Agent Skill](55-agentskill.md 也可能将其列为事实来源。因此 Repository 概况页会以入向 `SourcedFrom` 关系的形式展现“它产出了什么”。

### 治理

Repository 支持标准治理 aspects——所有权、标签、术语表术语、域、结构化属性和机构记忆——此外还支持浏览路径（`browsePathsV2`）以及标准的 `subTypes` aspect（例如 `GIT_REPOSITORY`）。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](54-repository.md)。
