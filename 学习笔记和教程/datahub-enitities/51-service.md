---
title: 服务
entity: service
order: 51
source: https://docs.datahub.com/docs/generated/metamodel/entities/service.md
---

# Service

Service（服务）是目录中针对外部服务的一个条目，该服务对外暴露可调用的 API——例如 MCP server、REST API、GraphQL API、gRPC 服务等。Service 对其暴露的 [API](53-api.md) 进行分组，承载完整的接口定义，并处于产出它的 [Repository](54-repository.md 与消费它的 [Applications](35-application.md/智能体之间，位于 `repo → service → api → app → dataset` 链路中。 进行分组，承载完整的接口定义，并处于产出它的 [Repository](54-repository.md) 与消费它的 [Applications](35-application.md/智能体之间，位于 `repo → service → api → app → dataset` 链路中。 与消费它的 [Applications](35-application.md/智能体之间，位于) `repo → service → api → app → dataset` 链路中。 `repo → service → api → app → dataset` 链路中。

服务的具体种类通过标准的 `subTypes` aspect 记录（例如 `MCP`、`REST_API`、`OPEN_API`、`GRPC`）。注意 Service 只承载目录信息（身份、描述、接口）；诸如 DataHub 的 Ask DataHub 集成所需认证等运维配置，单独存放在 `GlobalSettings.aiPlugins` 中，而不在实体上。

## 身份标识

Service 由单个字段标识：

- **id**：服务的唯一标识符，例如 `glean-search`、`internal-tools` 或 `weather-api`。

示例 URN 为 `urn:li:service:glean-search`。

## 重要能力

### Service Properties

`serviceProperties` aspect 承载目录身份信息以及服务在图中的位置：

- **displayName**：在 UI 和搜索结果中显示的名称，可通过自动补全搜索。
- **description**：该服务提供什么。
- **lifecycle**：生命周期阶段——`EXPERIMENTAL`、`PRODUCTION` 或 `DEPRECATED`——以徽章形式呈现，便于使用方一眼看出该服务是否可安全依赖。
- **apis**：该服务组合/暴露的 [API](53-api.md（`ServiceComposesApi`）。这是一条血缘边，API) 位于服务的下游，因此端点会正确地嵌套在其服务之下。 位于服务的下游，因此端点会正确地嵌套在其服务之下。
- **sourceRepository**：产出该服务的 [Repository](54-repository.md（`SourcedFrom`）)。

### Service Definition

`serviceDefinition` aspect 承载完整的接口文档——即操作级 API 实体被解析出来的事实来源。它记录：

- **format**：如何解析 `rawSpec`——`OPENAPI`、`GRAPHQL_SDL`、`GRPC_PROTO`、`ASYNCAPI`、`JSON_SCHEMA` 或 `OTHER`。
- **rawSpec**：完整的 spec 文档，逐字保留。以 `LargeString`（可选压缩）存储，使大型 spec 能容纳在 aspect 大小限制之内；读取方收到解压后的文本。在服务概况页的 Definition 标签页中以只读方式渲染。
- **version** / **externalUrl**：可选的 spec 版本，以及指向规范托管源的链接。

之所以将其独立为一个 aspect（而非 `serviceProperties` 上的字段），是因为 spec 数据块较大且仅在概况页需要，而 `serviceProperties` 在每张搜索卡片和页头都会被获取。

### MCP Server 属性

对于子类型为 `MCP` 的服务，`mcpServerProperties` aspect 承载连接信息：服务器 `url`、`transport`（`HTTP`、`SSE` 或 `WEBSOCKET`）、可选的连接 `timeout`，以及任意非认证用的 `customHeaders`（例如 `X-Tenant-ID`）。认证请求头在 `GlobalSettings.aiPlugins` 中配置，而不在此处。

### 健康状况与治理

Service 通过共享的事件子系统（`incidentsSummary`）展现运维健康状况，并支持标准的所有权、标签和状态 aspects。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](51-service.md)。。
