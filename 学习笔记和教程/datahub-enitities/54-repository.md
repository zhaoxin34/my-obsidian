---
title: 代码仓库
entity: repository
order: 54
source: https://docs.datahub.com/docs/generated/metamodel/entities/repository.md
---

# 代码仓库

代码仓库（Repository）是源代码仓库的一等公民表示（GitHub、GitLab、内部 SCM 等）。它是**软件到数据生命周期的起始节点**——
`repo → service → api → app → dataset`——并产出在别处编目的 [Services](51-service.md)、[APIs](53-api.md) 和
[Applications](35-application.md)。代码仓库不是表格类资产：它没有列、查询、统计、质量或预览。

## 标识

代码仓库由单个字段标识：

- **id**：代码仓库的唯一标识符。按惯例为 `<platform>.<org>/<name>`
  （例如 `github.acme/payments`、`gitlab.acme/data-platform`）；原生或平台未知的仓库可以省略平台前缀。

一个示例 URN 是 `urn:li:repository:github.acme/payments`。键本身与平台无关——平台承载在
`dataPlatformInstance` aspect 上，而非键中。

## 重要能力

### 仓库属性

`repositoryProperties` aspect 承载描述性元数据：

- **name**：显示名称，支持自动补全搜索。
- **description**：该仓库包含什么。
- **defaultBranch**：默认分支（例如 `main`、`master`）。
- **languages**：所使用的编程语言，按惯例以最主流的排在最前
  （仓库常常是多语言的，因此这是一个列表）。
- **license**：仓库的许可证（例如 `Apache-2.0`、`MIT`）。
- **homepageUrl**：指向仓库主页或文档的链接。
- **archived**：仓库是否已归档（只读／不再维护）。
- **created** / **lastModified**：审计时间戳。

### 源绑定

`repositorySource` aspect 记录仓库存放位置以及其在源系统中的标识方式：`externalUrl`（网页或克隆 URL）
和 `externalId`（例如 GitHub 的数字仓库 ID 或 `org/name` 形式的 slug）。

### 血缘

`repositoryLineage` aspect 记录仓库之间的来源关系——目前是 `forkOf`，即该仓库是其 git fork 源
的仓库（`RepositoryForkOf`）。

除 fork 血缘之外，代码仓库还是软件到数据链路的上游锚点：它产出的服务和 API 通过各自的 `SourcedFrom` 边指回它，
而 [Agent Skills](55-agentskill.md) 也可能将其列为自身的真实来源。因此代码仓库 profile 会以入向的
`SourcedFrom` 关系呈现“它产出了什么”。

### 治理

代码仓库支持标准治理 aspects——所有权、标签、术语表术语、域、结构化属性和机构记忆——
此外还有浏览路径（`browsePathsV2`）和标准 `subTypes` aspect（例如 `GIT_REPOSITORY`）。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](54-repository.md)。
