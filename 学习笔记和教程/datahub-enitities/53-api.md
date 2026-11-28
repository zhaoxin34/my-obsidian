---
title: API
entity: api
order: 53
source: https://docs.datahub.com/docs/generated/metamodel/entities/api.md
---

# API

API 是一个具名的可调用单元，具有带类型的输入与输出 schema——可以是一个 MCP 工具、一个 REST 端点、
一个 gRPC 方法、一个 GraphQL 操作、一个函数，等等。将 API 作为一等实体编目，
让人类和智能体都能在构建新的可调用单元之前先发现已有的调用能力，
并使调用方 → API 的依赖关系（组合出该 API 的服务、调用它的智能体）在图谱中可见。

API 的种类通过标准的 `subTypes` 方面来刻画。标准子类型为
`MCP_TOOL`、`REST_ENDPOINT`、`GRPC_METHOD`、`GRAPHQL_OPERATION` 与 `FUNCTION`——
它们各自基于一种具体的可调用单元种类，而非基于该 API 恰好被如何使用
（"作为智能体的工具"是一种关系，而非内在种类——MCP 工具同样只是 API）。

## 标识

API 由单个字段标识：

- **id**：API 的唯一标识符，例如 `order-lookup-mcp` 或生成的 UUID。

URN 示例为 `urn:li:api:order-lookup-mcp`。对于 REST 端点，id 由所属服务、
HTTP 方法与路径生成（例如 `order-entry-api/GET/orders/{orderId}`），
因此同一个操作无论是手工注册还是从 OpenAPI 规范抓取，都解析到同一个 URN。
由于一个 `(方法, 路径)` 组合标识一个 REST 操作，
在多个方法下提供的端点（同一路径上的 GET 与 POST）会按方法建模为不同的 API 实体。

## 重要能力

### API 属性

`apiProperties` 方面承载编目标识信息：

- **name**：显示名称，可搜索并支持自动补全。
- **description**：该 API 的作用以及何时使用它。
- **externalUrl**：指向该 API 的注册条目、文档或源码的可选链接。
- **sourceRepository**：产出该 API 的[代码仓库](54-repository.md)（`SourcedFrom`），
  从而点亮 `repo → service → api → app → dataset` 链路。
- **created** / **lastModified**：审计戳。

### 签名

输入/输出契约存放在独立的 `apiSignature` 方面中，与 `apiProperties` 分开，
因为签名是从端点抓取而来的（OpenAPI/JSON-Schema 文档、MCP 工具清单、函数定义），
并以自己的节奏演进——当契约变化时，只需重新摄取该方面，编目标识保持不变。它包含：

- **schemaDefinition**：完整的输入/输出 schema，作为不透明字符串（通常是 JSON Schema）——
  这是唯一的事实来源表示，即使结构化字段无法捕获某些构造也能完整往返。
- **inputFields** / **outputFields**：复用 DataHub schema-field 模型的结构化、类型化视图，
  使嵌套/结构体/数组类型、可空性以及字段描述能够使用标准 schema 组件渲染。
  每个字段的 `fieldPath` 即参数名；`nullable=false` 表示必填参数。
- **inputDatasetEdges** / **outputDatasetEdges**：_按引用_ 表示的输入与输出 schema——
  指向已经对载荷建模的[数据集](01-dataset.md)实体的边
  （一个 protobuf message、一条 Avro record、一个共享 DTO）。当同一种 message 类型在许多 API 中复用，
  或同时还流经 topic 与表时，使用这些边以便 schema 只定义一次。这些是血缘边
  （`Consumes` 与 `Produces`），因此图谱呈现为 请求数据集 → API → 响应数据集。每条边都是一个
  `Edge`，因而可以携带审计戳与 properties 映射；目前尚无功能读取边属性，
  所以诸如流式模式等协议细节属于未来工作。

某一侧（输入或输出）应当要么内联表示，要么按引用表示。若两者同时存在，
则以被引用数据集的 schema 为准，内联字段视为缓存或部分视图。

#### 示例：基于 protobuf message 的 gRPC 方法

将每个 protobuf `message` 作为数据集摄取（`datahub-protobuf` 模块即如此实现，
并带有完整的嵌套 schema）。然后将每个 `rpc` 注册为子类型为 `GRPC_METHOD` 的 API，
其签名指向这些数据集：

```yaml
id: orders.OrderService/GetOrder
name: GetOrder
subtypes: [GRPC_METHOD]
input_datasets:
  - urn:li:dataset:(urn:li:dataPlatform:kafka,orders.GetOrderRequest,PROD)
output_datasets:
  - urn:li:dataset:(urn:li:dataPlatform:kafka,orders.Order,PROD)
```

### REST 属性

对于子类型为 `REST_ENDPOINT` 的 API，`restApiProperties` 方面记录 `method`（HTTP 动词）
与 `path`（相对于所属服务基础 URL 的路由模板，例如 `/orders/{orderId}`）。
这些信息保存在子类型专属的方面中，以便调用方按方法筛选，并将共享同一路径的端点归组。

### 关系

API 通过入向边与软件到数据的图谱其余部分相连：

- [服务](51-service.md)组合出它（`ServiceComposesApi`）。
- [AI 智能体](52-aiagent.md)将其作为工具调用（`AgentUsesTool`）。
- [智能体技能](55-agentskill.md)依赖它（`SkillRequiresTool`）。

### 治理与版本管理

API 支持标准治理方面——所有权、标签、术语表术语、Domains、结构化属性与机构记忆——
并支持原生版本管理（`versionProperties`）。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](53-api.md)。
