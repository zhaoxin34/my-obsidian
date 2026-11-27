---
title: 语义模型
entity: semanticmodel
source: https://docs.datahub.com/docs/generated/metamodel/entities/semanticmodel.md
---

# 语义模型

语义模型（Semantic Model）实体表示一种逻辑数据模型，它将数据集分组，并定义指标所使用的维度上下文（字段、维度、关系）。它在原始数据集与基于其计算的业务指标之间充当桥梁。

## 身份（Identity）

语义模型由三个字段标识：

- **`platform`** —— 拥有该语义模型的 DataPlatform URN（例如 `urn:li:dataPlatform:dbt`、`urn:li:dataPlatform:snowflake`）。可作为 URN 字段进行搜索，支持自动补全和 "Platform" 过滤标签。
- **`path`** —— 在其平台内界定该语义模型作用范围的命名空间路径，避免两个团队在同一平台上定义相同 `id` 的模型时发生名称冲突。
- **`id`** —— 该平台与路径下的模型名称（例如 `orders_model`、`customer_360`）。

URN 示例：`urn:li:semanticModel:(urn:li:dataPlatform:dbt,analytics,orders_model)`。

## 重要能力（Important Capabilities）

### 语义模型信息

核心元数据存储在 `semanticModelInfo` aspect 中：

- **`name`** —— 人类可读的显示名称；用于全文搜索与自动补全。
- **`description`** —— 自由文本描述，说明该模型代表什么。
- **`created`** —— `AuditStamp`（`time` + `actor`），记录语义模型何时由谁创建。搜索索引为 `createdAt`（DATETIME）。
- **`lastModified`** —— `AuditStamp`，记录最近一次修改。搜索索引为 `lastModifiedAt`（DATETIME）。
- **`nativeDefinition`** —— 可选的逐字来源定义（例如 Snowflake 的 `CREATE SEMANTIC VIEW` DDL、dbt 的 `semantic_model` YAML，或 Databricks 的 `CREATE METRIC VIEW` DDL）。原样保留以便回写与调试；DataHub 不会解析它。
- **`datasets`** —— **已废弃。** 保留以便已摄入的 aspect 仍可读取；`@Relationship` / `@Searchable` 注解已被移除，因此该字段不再写入图或搜索边。新的写入不得填充该字段。成员关系以每个逻辑数据集的 `semanticModelProperties.semanticModel`（`IsPartOf`）为准。重新摄入以由连接器按指标路由填充 `metricUpstreams.datasetUpstreams`。
- **`relationships`** —— 可选的 `SemanticModelRelationship` 记录数组，描述该模型内逻辑数据集之间的连接路径（from 别名、to 别名、连接列、可选名称、可选基数（复用 `ERModelRelationshipCardinality`），以及可选的按关系的 AI 上下文）。from/to 别名指向各逻辑数据集的 `semanticModelProperties.alias`。

### AI 上下文

针对语义模型本身的可选 AI/LLM 提示存储在一等 `aiContext` aspect 中（同义词、自然语言指令、少样本示例、自定义指令）。`SemanticModelRelationship` 上按关系的 AI 上下文仍以内联形式保留。

### 作为数据集实体的逻辑数据集

语义模型暴露的每个逻辑数据集都是独立的 `dataset` 实体 —— 有自己的 URN、自己的 `schemaMetadata`，以及自己的治理界面。独立的身份标识使得无需重新实现即可实现独立的搜索、治理与血缘。

- **URN 模式**：使用**源平台**（已注册，例如 `dbt`、`snowflake`、`databricks`、`cube`、`atscale`），并在数据集名称中编码 `<sm_path>.<sm_id>.<view_name>`，使逻辑数据集在多个语义模型之间保持唯一。示例：`urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.orders_model.orders_ds,PROD)`。
- **`subTypes`** —— 携带 `Semantic Model Dataset`（Python 摄入 SDK 中为 `DatasetSubTypes.SEMANTIC_MODEL_DATASET`），这是一个独立于 `Semantic View`（`DatasetSubTypes.SEMANTIC_VIEW`）的专用子类型。后者仍保留给平台原生的语义视图对象（例如 Snowflake 的 `CREATE SEMANTIC VIEW`），其本身作为顶层数据集摄入。
- **`semanticModelProperties`** aspect —— 标准 Dataset aspect 之上的语义模型专用 facet：
  - **`alias`** —— 在其所属语义模型的 `SemanticModelRelationship` 连接路径中引用该数据集所用的逻辑别名。
  - **`semanticModel`** —— 所属 SemanticModel 的权威 URN（`IsPartOf`，非血缘）。搜索索引为 `semanticModel` / `hasSemanticModel`。列出某模型的即是对该字段的 ES 过滤。
- **`viewProperties`** aspect（标准，已在 `dataset` 上注册）—— 当逻辑数据集由视图或内联查询支撑时，保存其原生 SQL（`viewLogic`），与任何其他由视图支撑的数据集完全一致。
- **`schemaMetadata`** aspect（标准）—— 字段投影：该逻辑数据集暴露哪些列及其结构类型。字段级语义元数据（表达式、聚合、维度/度量/过滤分类）通过 `semanticFieldAnnotation` 叠加在其上 —— 参见下文 [字段与维度](#字段与维度)。
- **`upstreamLineage`** aspect（标准）—— 回到该逻辑数据集所派生的物理表或查询的物理血缘 —— 参见下文 [血缘](#血缘)。

### 字段与维度

列的身份标识、结构类型与治理（标签、术语表术语、描述）都存放在标准 `schemaField` 实体上 —— 与其他所有 Dataset 的列所使用的实体相同，它已具备列级血缘、搜索索引与审计轨迹。语义专用元数据通过 `semanticFieldAnnotation` aspect 叠加其上，附着在该列对应的 `schemaField` 实体上：

- **`type`** —— 必填的 `SemanticFieldType` 枚举，标识字段种类：`DIMENSION`（分组/过滤属性）、`MEASURE`（可聚合的数值）、`FILTER`（具名布尔谓词），或 `OTHER`（为无法良好映射到上述三类的来源构造保留的前向兼容出口）。
- **`expression`** —— 一个或多个方言下的底层 SQL 表达式。
- **`aggregationFunction`** —— 可选的聚合函数名（例如 `SUM`、`COUNT_DISTINCT`、`AVG`），在 `type == MEASURE` 时应用。
- **`dimension`** —— 可选的 `Dimension` 记录；仅在 `type == DIMENSION` 时填充。目前暴露 `isTime: boolean`，用于标记用于日期范围过滤的时间维度。

字段级 AI/LLM 提示存放在 `schemaField` 实体的一等 `aiContext` aspect 上。

### 内联查询来源

某些语义层平台允许逻辑数据集的数据来源于内联 SQL 查询而非持久化表（例如带 `source: <SELECT ...>` 的 Databricks metric view）。由于逻辑数据集是标准 `dataset` 实体，这沿用了任何其他由视图支撑且 SQL 无法解析到单一表的数据集所用的机制：原始 SQL 位于 `viewProperties.viewLogic`，`upstreamLineage.upstreams` 为 SQL 引用的每个物理表携带一条 `Upstream` 记录（通过 SQL 解析提取），每条记录可选地通过 `Upstream.query` 标注因果 `query` 实体。此场景无需任何语义模型专用的建模。

### 血缘

SemanticModel 是其逻辑数据集与指标的容器（类似 Domain），而非血缘中的一跳。在血缘浏览器中它渲染为其成员周围的包围框。基于语义模型的指标的标准血缘链为：

`Metric → 逻辑数据集（Semantic Model Dataset）→ 物理数据集`

**Metric → 逻辑数据集** —— 填充 `metricUpstreams.datasetUpstreams`，写入该指标读取的语义模型数据集 URN（`Consumes`，`isLineage: true`）。可选填充 `metricUpstreams.fieldUpstreams`，写入对应的 `schemaField` URN 以实现列级血缘。

**Metric ↔ 语义模型** —— 成员关系仅存储在 `metricInfo.semanticModel`（`ModeledBy`，非血缘）。该字段驱动搜索/过滤/分面，以及血缘浏览器中的包围框成员展示。

**语义模型 ↔ 逻辑数据集** —— 成员关系仅存储在 `semanticModelProperties.semanticModel`（`IsPartOf`，非血缘）。每个逻辑数据集还保留 `semanticModelProperties.alias` 以支持连接边。

**逻辑数据集 → 物理来源** —— 逻辑数据集上的标准 `upstreamLineage` aspect（与所有数据集通用的同一 aspect），每个物理来源表或查询填充一条 `Upstream` 记录。

**列级血缘** —— 逻辑数据集上的标准 `upstreamLineage.fineGrainedLineages`，两侧均使用 `schemaField` URN —— 无需语义模型专用的列血缘基础设施。

### 治理

语义模型实体复用以下标准治理 aspects：`ownership`、`domains`、`globalTags`、`glossaryTerms`、`institutionalMemory`、`structuredProperties`、`status`、`deprecation`、`dataPlatformInstance`、`subTypes`、`documentation`、`browsePathsV2`、`applications`、`aiContext`。

其逻辑数据集实体（以及它们的 `schemaField`）自动继承完整的标准 Dataset/SchemaField 治理界面 —— 标签、术语表术语、所有权、描述、结构化属性 —— 无需任何语义模型专用的重新实现。

## 与其他实体的关系（Relationships with Other Entities）

| 关系 | 方向 | 目标实体 | Aspect / 边名称 | 血缘？ |
| ------------ | --------- | ------------- | --------------------------------------- | -------- |
| IsPartOf     | 入向   | `dataset`     | `semanticModelProperties.semanticModel` | 否       |
| ModeledBy    | 入向   | `metric`      | `metricInfo.semanticModel`              | 否       |

Metric → SMD 血缘存放在 `metricUpstreams.datasetUpstreams`（而不在语义模型上）—— 参见上文 [血缘](#血缘)。遍历随后通过各逻辑数据集的 `upstreamLineage` 继续（SemanticModelDataset → Physical Dataset）。

## 值得注意的例外（Notable Exceptions）

### 已废弃的 `semanticModelInfo.datasets`

早期指标目录摄入会把逻辑数据集成员关系存储在容器的 `semanticModelInfo.datasets` 中（带血缘标记的 `Contains` 边）。该字段已废弃：它为兼容已存储数据仍保留在 PDL 中，但注解已被移除，生产者也不再写入。成员关系已位于 `semanticModelProperties.semanticModel`；重新摄入以由连接器按指标路由填充 `metricUpstreams.datasetUpstreams`。GraphQL 的 `SemanticModelInfo.datasets` 同样已废弃并返回空 —— 请通过对 `semanticModelProperties.semanticModel` 的 Elasticsearch 过滤来发现成员数据集（指标则使用 `metrics(...)` / `metricInfo.semanticModel`）。

### SemanticModelRelationship 与通用 Relationship 的区别

该连接路径记录命名为 `SemanticModelRelationship`（而非 `Relationship`），以避免与 DataHub 的 `com.linkedin.common.Relationship` 模型发生名称冲突。

### 通过 structuredProperties 扩展

实体级扩展性使用 `structuredProperties` aspect，该 aspect 已为 `semanticModel` 实体（以及支撑其逻辑数据集与字段的 `dataset`/`schemaField` 实体）注册。结构化属性支持类型化取值、治理控制、搜索分面与 PATCH 语义 —— 对于尚不值得引入一等 PDL 字段的平台特定元数据，它们是推荐的机制。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/semanticmodel.md)。
