---
title: API
entity: api
source: https://docs.datahub.com/docs/generated/metamodel/entities/api.md
---

# API

API 是一个具名的可调用单元，具有带类型的输入与输出 schema —— 可以是 MCP 工具、REST 端点、gRPC 方法、GraphQL 操作、函数等等。将 API 作为一等实体编目，可以让人类和智能体在构建新的可调用单元之前先发现已有的可调用单元，并使调用方 → API 的依赖关系（组合出该 API 的服务、调用它的智能体）在图谱中可见。

API 的种类通过标准的 `subTypes` aspect 捕获。标准子类型为 `MCP_TOOL`、`REST_ENDPOINT`、`GRPC_METHOD`、`GRAPHQL_OPERATION` 和 `FUNCTION` —— 每一种都基于具体的可调用单元种类，而非基于 API 的使用方式（"成为某个智能体的工具"是一种关系，而不是内在种类 —— 一个 MCP 工具就是一个 API）。

## 身份（Identity）

API 由单一字段标识：

- **id**：API 的唯一标识符，例如 `order-lookup-mcp` 或生成的 UUID。

URN 示例为 `urn:li:api:order-lookup-mcp`。对于 REST 端点，id 由所属服务、HTTP 方法与路径生成（例如 `order-entry-api/GET/orders/{orderId}`），从而使同一操作无论是手工注册还是从 OpenAPI 规范抓取，都解析为同一 URN。由于一个 `(method, path)` 组合标识一个 REST 操作，在同一路径下以多种方法提供的端点（同一路径上的 GET 与 POST）会被建模为按方法区分的独立 API 实体。

## 重要能力（Important Capabilities）

### API 属性

`apiProperties` aspect 保存编目身份信息：

- **name**：显示名称，可搜索并支持自动补全。
- **description**：该 API 的作用以及何时使用。
- **externalUrl**：指向该 API 的注册条目、文档或源码的可选链接。
- **sourceRepository**：该 API 产出所在的 [Repository](./repository.md)（`SourcedFrom`），点亮 `repo → service → api → app → dataset` 链路。
- **created** / **lastModified**：审计戳。

### 签名（Signature）

输入/输出契约存放在独立的 `apiSignature` aspect 中，与 `apiProperties` 分开，因为签名是从端点抓取的（OpenAPI/JSON-Schema 文档、MCP 工具清单、函数定义），且按其自身节奏演进 —— 当契约变化时，只有该 aspect 被重新摄入，编目身份保持不变。它携带：

- **schemaDefinition**：完整的输入/输出 schema，以不透明字符串表示（通常是 JSON Schema）—— 这是真相来源表示，即使结构化字段无法捕获某些构造也能无损回写。
- **inputFields** / **outputFields**：结构化、类型化的视图，复用 DataHub 的 schema 字段模型，从而让嵌套/结构体/数组类型、可空性与字段描述都能用标准的 schema 组件渲染。每个字段的 `fieldPath` 即参数名；`nullable=false` 表示该参数为必填。
- **inputDatasetEdges** / **outputDatasetEdges**：**按引用**表示的输入与输出 schema —— 指向已建模载荷的 [Dataset](./dataset.md) 实体的边（一个 protobuf message、一个 Avro record、一个共享 DTO）。当同一种 message 类型在许多 API 之间复用，或同时也流经 topic 与 table 时使用这些边，从而只定义一次 schema。这些是血缘边（`Consumes` 与 `Produces`），因此图谱呈现为 请求数据集 → API → 响应数据集。每个边都是一个 `Edge`，因此可以携带审计戳与 properties 包；目前尚无读取边属性的地方，所以诸如流式模式等协议细节属于未来工作。

某一侧（输入或输出）应当要么内联表达，要么按引用表达。如果两者同时存在，以被引用数据集的 schema 为准，内联字段被视为缓存或部分视图。

#### 示例：基于 protobuf message 的 gRPC 方法

将每个 protobuf `message` 作为 Dataset 摄入（`datahub-protobuf` 模块可以做到这一点，包含完整的嵌套 schema）。然后将每个 `rpc` 注册为子类型为 `GRPC_METHOD` 的 API，其签名指向这些数据集：

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

对于子类型为 `REST_ENDPOINT` 的 API，`restApiProperties` aspect 记录 `method`（HTTP 动词）与 `path`（相对于所属服务 base URL 的路由模板，例如 `/orders/{orderId}`）。这些信息保留在子类型专用的 aspect 上，以便调用方按方法过滤并对共享同一路径的端点进行分组。

### 关系

API 通过入向边与"软件到数据"图谱的其余部分相连：

- [Service](./service.md) 组合它（`ServiceComposesApi`）。
- [AI Agents](./aiAgent.md) 将其作为工具调用（`AgentUsesTool`）。
- [Agent Skills](./agentSkill.md) 需要它（`SkillRequiresTool`）。

### 治理与版本管理

API 支持标准治理 aspects —— 所有权、标签、术语表术语、领域、结构化属性与机构记忆 —— 并且原生支持版本管理（`versionProperties`）。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/api.md)。
