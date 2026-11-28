---
title: 语义模型
entity: semanticmodel
order: 36
source: https://docs.datahub.com/docs/generated/metamodel/entities/semanticmodel.md
---

# 语义模型

语义模型实体表示一个逻辑数据模型，它将数据集组织在一起，并定义指标所使用的维度上下文（字段、维度、关系）。它充当原始数据集与基于其计算的业务指标之间的桥梁。

## 标识

语义模型由三个字段标识：

- **`platform`** —— 拥有该语义模型的 DataPlatform URN
  （例如 `urn:li:dataPlatform:dbt`、`urn:li:dataPlatform:snowflake`）。可作为 URN 字段搜索，
  支持自动补全和 "Platform" 筛选标签。
- **`path`** —— 在其平台内限定该语义模型作用域的命名空间路径，避免两个团队在同一平台上
  定义具有相同 `id` 的模型时发生名称冲突。
- **`id`** —— 该模型在此平台与路径下的名称
  （例如 `orders_model`、`customer_360`）。

URN 示例：`urn:li:semanticModel:(urn:li:dataPlatform:dbt,analytics,orders_model)`。

## 重要能力

### 语义模型信息

核心元数据存储在 `semanticModelInfo` 方面中：

- **`name`** —— 人类可读的显示名称；用于全文搜索与自动补全。
- **`description`** —— 对该模型所代表内容的自由文本描述。
- **`created`** —— `AuditStamp`（`time` + `actor`），记录语义模型何时创建以及由谁创建。
  在搜索中索引为 `createdAt`（DATETIME）。
- **`lastModified`** —— `AuditStamp`，记录最近一次修改。
  在搜索中索引为 `lastModifiedAt`（DATETIME）。
- **`nativeDefinition`** —— 可选的逐字源定义（例如 Snowflake
  的 `CREATE SEMANTIC VIEW` DDL、dbt 的 `semantic_model` YAML，或 Databricks
  的 `CREATE METRIC VIEW` DDL）。原样保留以便往返与调试；DataHub 不会对其进行解析。
- **`datasets`** —— **已弃用。** 保留是为了让已摄取的数据仍可读取；
  `@Relationship` / `@Searchable` 注解已被移除，因此该字段不再写入图或搜索边。
  新写入不得填充该字段。成员关系以每个逻辑数据集的 `semanticModelProperties.semanticModel`
  （`IsPartOf`）为准。重新摄取以填充 `metricUpstreams.datasetUpstreams`，具体按指标路由由连接器决定。
- **`relationships`** —— 可选的 `SemanticModelRelationship` 记录数组，描述该模型中逻辑数据集之间的连接路径
  （from 别名、to 别名、连接列、可选名称、可选基数（复用 `ERModelRelationshipCardinality`），
  以及可选的每条关系的 AI 上下文）。from/to 别名指向各逻辑数据集的 `semanticModelProperties.alias`。

### AI 上下文

针对语义模型本身的可选 AI/LLM 提示存放在一等公民 `aiContext` 方面中
（同义词、自然语言指令、少样本示例与自定义指令）。`SemanticModelRelationship` 上每条关系的
AI 上下文仍以内联形式保留。

### 作为数据集实体的逻辑数据集

语义模型暴露的每个逻辑数据集都是独立的 `dataset` 实体——拥有自己的 URN、
自己的 `schemaMetadata` 以及自己的治理界面。正是这种独立标识，使得无需重新实现即可
实现独立的搜索、治理与血缘。

- **URN 模式**：使用**源平台**（已注册——例如 `dbt`、`snowflake`、
  `databricks`、`cube`、`atscale`），并在数据集名称中编码
  `<sm_path>.<sm_id>.<view_name>`，使逻辑数据集在各语义模型之间保持唯一。示例：
  `urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.orders_model.orders_ds,PROD)`。
- **`subTypes`** —— 携带 `Semantic Model Dataset`（在 Python 摄取 SDK 中为 `DatasetSubTypes.SEMANTIC_MODEL_DATASET`），
  这是一个独立于 `Semantic View`（`DatasetSubTypes.SEMANTIC_VIEW`）的专用子类型。
  后者仍保留给平台原生的语义视图对象（例如 Snowflake 的 `CREATE SEMANTIC VIEW`），
  作为独立的顶层数据集摄取。
- **`semanticModelProperties` 方面** —— 标准数据集方面之上的语义模型专属维度：
  - **`alias`** —— 在其所属语义模型的 `SemanticModelRelationship` 连接路径中用于引用该数据集的逻辑别名。
  - **`semanticModel`** —— 所属 SemanticModel 的权威 URN（`IsPartOf`，非血缘）。
    在搜索中索引为 `semanticModel` / `hasSemanticModel`。列出某模型的数据集即对该字段做 ES 筛选。
- **`viewProperties` 方面**（标准，已在 `dataset` 上注册）—— 当逻辑数据集由视图或内联查询支撑时，
  在其中保存原生 SQL（`viewLogic`），与任何其他由视图支撑的数据集完全一致。
- **`schemaMetadata` 方面**（标准）—— 字段投影：该逻辑数据集暴露哪些列，以及它们的结构类型。
  字段级语义元数据（表达式、聚合、维度/度量/过滤分类）通过 `semanticFieldAnnotation` 叠加在其上
  —— 参见下文[字段与维度](#字段与维度)。
- **`upstreamLineage` 方面**（标准）—— 回到该逻辑数据集所派生自的表或查询的物理血缘；
  参见下文[血缘](#血缘)。

### 字段与维度

列标识、结构类型与治理信息（标签、术语表术语、描述）都存放在标准的 `schemaField` 实体上——
与每个其他数据集的列所使用的实体相同，该实体已具备列级血缘、搜索索引与审计轨迹。
语义专属元数据通过 `semanticFieldAnnotation` 方面叠加在其上，该方面挂在对应列的 `schemaField` 实体上：

- **`type`** —— 必填的 `SemanticFieldType` 枚举，用于标识字段种类：`DIMENSION`
  （分组/过滤属性）、`MEASURE`（可聚合的数值）、`FILTER`（具名布尔谓词），
  或 `OTHER`（为无法干净映射到上述三类的源构造保留的前向兼容出口）。
- **`expression`** —— 在一种或多种 SQL 方言下的底层 SQL 表达式。
- **`aggregationFunction`** —— 可选的聚合函数名（例如 `SUM`、`COUNT_DISTINCT`、
  `AVG`），在 `type == MEASURE` 时应用。
- **`dimension`** —— 可选的 `Dimension` 记录；仅当 `type == DIMENSION` 时填充。目前
  暴露 `isTime: boolean`，用于标记用于日期范围过滤的时间维度。

字段级 AI/LLM 提示存放在 `schemaField` 实体的一等公民 `aiContext` 方面中。

### 内联查询来源

某些语义层平台允许逻辑数据集以内联 SQL 查询而非持久化表作为来源
（例如带 `source: <SELECT ...>` 的 Databricks 指标视图）。由于逻辑数据集是标准的 `dataset` 实体，
这与其他任何 SQL 无法解析到单一表的视图支撑数据集使用相同的机制：原始 SQL 存放于
`viewProperties.viewLogic`，而 `upstreamLineage.upstreams` 为 SQL 引用的每张物理表携带一个 `Upstream` 条目
（通过 SQL 解析提取），每个条目可选择通过 `Upstream.query` 标注因果关系的 `query` 实体。
这种情况无需任何语义模型专属建模。

### 血缘

SemanticModel 是其逻辑数据集与指标的容器（类似 Domains），而不是血缘的一跳。
在血缘浏览器中，它呈现为围绕其成员的边界框。基于语义模型的指标的标准血缘链为：

`Metric → Logical Dataset (Semantic Model Dataset) → Physical Dataset`

**Metric → 逻辑数据集** —— 用指标读取的语义模型数据集 URN 填充 `metricUpstreams.datasetUpstreams`
（`Consumes`，`isLineage: true`）。可选地用对应的 `schemaField` URN 填充
`metricUpstreams.fieldUpstreams` 以提供列级血缘。

**Metric ↔ 语义模型** —— 成员关系仅存储在 `metricInfo.semanticModel`
（`ModeledBy`，非血缘）上。该字段驱动搜索/筛选/分面以及血缘浏览器中的边界框成员关系。

**语义模型 ↔ 逻辑数据集** —— 成员关系仅存储在
`semanticModelProperties.semanticModel`（`IsPartOf`，非血缘）上。每个逻辑数据集还保留
`semanticModelProperties.alias` 以支撑连接边。

**逻辑数据集 → 物理来源** —— 逻辑数据集上的标准 `upstreamLineage` 方面
（与每个数据集已在使用的方面相同），为每个物理来源表或查询填充一个 `Upstream` 条目。

**列级血缘** —— 逻辑数据集上的标准 `upstreamLineage.fineGrainedLineages`，
两侧均使用 `schemaField` URN —— 无需语义模型专属的列级血缘基础设施。

### 治理

语义模型实体复用以下标准治理方面：`ownership`、`domains`、
`globalTags`、`glossaryTerms`、`institutionalMemory`、`structuredProperties`、`status`、
`deprecation`、`dataPlatformInstance`、`subTypes`、`documentation`、`browsePathsV2`、
`applications`、`aiContext`。

其逻辑数据集实体（及其 `schemaField`）会自动继承完整的标准 Dataset/SchemaField
治理界面——标签、术语表术语、所有权、描述、结构化属性——无需任何语义模型专属的重新实现。

## 与其他实体的关系

| 关系 | 方向 | 目标实体 | 方面 / 边名称                      | 是否血缘 |
| ------------ | --------- | ------------- | --------------------------------------- | -------- |
| IsPartOf     | 入向   | `dataset`     | `semanticModelProperties.semanticModel` | 否       |
| ModeledBy    | 入向   | `metric`      | `metricInfo.semanticModel`              | 否       |

Metric → SMD 血缘位于 `metricUpstreams.datasetUpstreams`（而非语义模型上）——
参见上文[血缘](#血缘)。之后的遍历继续经由每个逻辑数据集的
`upstreamLineage`（SemanticModelDataset → Physical Dataset）。

## 值得注意的例外

### 已弃用的 `semanticModelInfo.datasets`

早期的指标目录摄取将逻辑数据集成员关系存储在容器上的 `semanticModelInfo.datasets`
（带有带血缘标记的 `Contains` 边）。该字段已弃用：它为存量数据兼容性保留在 PDL 中，
但注解已被移除，生产者也不再写入它。成员关系已存在于
`semanticModelProperties.semanticModel` 上；重新摄取以填充
`metricUpstreams.datasetUpstreams`，具体按指标路由由连接器决定。GraphQL 的
`SemanticModelInfo.datasets` 同样已弃用并返回空值——请通过在
`semanticModelProperties.semanticModel` 上做 Elasticsearch 筛选来发现成员数据集
（指标则使用 `metrics(...)` / `metricInfo.semanticModel`）。

### SemanticModelRelationship 与通用 Relationship

该连接路径记录命名为 `SemanticModelRelationship`（而非 `Relationship`），以避免与
DataHub 的 `com.linkedin.common.Relationship` 模型产生名称冲突。

### 通过 structuredProperties 实现可扩展性

实体级可扩展性使用 `structuredProperties` 方面，它已为 `semanticModel` 实体
（以及支撑其逻辑数据集与字段的 `dataset`/`schemaField` 实体）注册。结构化属性支持类型化取值、
治理控制、搜索分面与 PATCH 语义——对于任何不值得设置为一等 PDL 字段的平台专属元数据，
它们都是推荐机制。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](36-semanticmodel.md)。
