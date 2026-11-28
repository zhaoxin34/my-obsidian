---
title: 指标
entity: metric
order: 37
source: https://docs.datahub.com/docs/generated/metamodel/entities/metric.md
---

# 指标

metric 实体表示定义在语义层或指标存储中的、具名且可复用的业务度量。

## 标识

指标由三个字段标识：

- **`platform`** —— 拥有该指标的 DataPlatform URN
  （例如 `urn:li:dataPlatform:dbt`、`urn:li:dataPlatform:snowflake`）。可作为 URN 字段搜索，
  支持自动补全和 "Platform" 筛选标签。
- **`path`** —— 在其平台内限定该指标作用域的命名空间路径，避免两个团队在同一平台上
  定义具有相同 `id` 的指标时发生名称冲突。
- **`id`** —— 该指标在此平台与路径下的名称
  （例如 `total_revenue`、`daily_active_users`）。

URN 示例：`urn:li:metric:(urn:li:dataPlatform:dbt,analytics.orders_model,revenue)`。

## 重要能力

### 指标信息

核心元数据存储在 `metricInfo` 方面中：

- **`name`** —— 人类可读的显示名称；用于全文搜索与自动补全。
- **`description`** —— 对该指标所度量内容的自由文本描述。
- **`created`** —— `AuditStamp`（`time` + `actor`），记录指标何时创建以及由谁创建。
  在搜索中索引为 `createdAt`（DATETIME）。
- **`lastModified`** —— `AuditStamp`，记录最近一次修改。
  在搜索中索引为 `lastModifiedAt`（DATETIME）。
- **`expression`** —— 以一种或多种 SQL 方言表达的指标公式。每个 `DialectExpression` 将
  一个 `Dialect` 枚举值与原始 SQL 字符串配对。

- **`semanticModel`** —— 所属 SemanticModel 的可选 URN。权威的成员关系
  指针。在搜索中索引为 `semanticModel` / `hasSemanticModel`。未随语义模型一起摄取的指标
  （例如来自 BI 工具的纯目录型指标）该字段保持未设置。

### AI 上下文

可选的 AI/LLM 提示存放在一等公民 `aiContext` 方面中
（同义词、自然语言指令、少样本示例与自定义指令）。

### 指标关系

层级关系与派生关系存储在 `metricRelationships` 方面中：

- **`parentMetric`** —— 父指标的 URN。用于构建指标的层级树。
  以 `IsPartOf` 图边存储。
- **`derivedFrom`** —— 指向源指标的 `DerivedMetricInput` 记录数组。
  `DerivedMetricInput` 包含 `Edge`，因此载荷形态为 Edge
  （`destinationUrn`、审计戳、`properties` 包）。这些边会标记
  `isLineage: true`，从而出现在 DataHub 血缘图中。
- **`relatedMetrics`** —— 指向语义相关指标的 `Edge` 记录数组（无
  血缘标记）。

### 治理与血缘

metric 实体复用以下标准治理方面：`ownership`、`domains`、
`globalTags`、`glossaryTerms`、`institutionalMemory`、`structuredProperties`、`status`、
`deprecation`、`dataPlatformInstance`、`subTypes`、`documentation`、`browsePathsV2`、
`applications`、`aiContext`。

## 与其他实体的关系

| 关系           | 方向 | 目标实体   | 方面 / 边名称                 | 是否血缘 |
| ---------------------- | --------- | --------------- | ---------------------------------- | -------- |
| ModeledBy              | 出向  | `semanticModel` | `metricInfo.semanticModel`         | 否       |
| IsPartOf               | 出向  | `metric`        | `metricRelationships`              | 否       |
| DerivedFrom            | 出向  | `metric`        | `metricRelationships`              | 是      |
| RelatedTo              | 出向  | `metric`        | `metricRelationships`              | 否       |
| Consumes (dataset)     | 出向  | `dataset`       | `metricUpstreams.datasetUpstreams` | 是      |
| Consumes (schemaField) | 出向  | `schemaField`   | `metricUpstreams.fieldUpstreams`   | 是      |

语义模型成员关系仅记录在成员一侧：`metricInfo.semanticModel`（`ModeledBy`，
非血缘）是唯一的事实来源。列出某模型的指标即对
`semanticModel` 做 ES 筛选（可选择加上 `hasSemanticModel=true`）。

指标到数据集、指标到列的血缘由专门的 `metricUpstreams` 方面承载。
`datasetUpstreams` 与 `fieldUpstreams` 各自独立可选，
以便摄取源能填充其所能提取的粒度。指标到指标的派生血缘位于
`metricRelationships.derivedFrom`，不会并入 `metricUpstreams`。

**基于语义模型的指标的约定：** 用指标读取的语义模型数据集 URN 填充
`metricUpstreams.datasetUpstreams`。SemanticModel 本身是一个容器（边界框），
而不是血缘的一跳——标准链为
`Metric → Logical Dataset (Semantic Model Dataset) → Physical Dataset`。

## 值得注意的例外

### 与环境无关的标识

指标在键中编码 `platform`（一个 DataPlatform URN），但刻意不编码
`FabricType`（不同于数据集——数据集的 URN 中包含 PROD/STAGING）。指标被建模为
与环境无关的业务定义：PROD 与 STAGING 中的 `total_revenue` 是同一概念，
因此二者解析到同一个 URN。跨平台的指标（例如 dbt 与 Snowflake 中的同一度量）
仍是独立实体，因为 `platform` 是 URN 的一部分。

### 通过 structuredProperties 实现可扩展性

实体级可扩展性使用 `structuredProperties` 方面，它已为 `metric` 实体注册。
结构化属性支持类型化取值、治理控制、搜索分面与 PATCH 语义——
对于尚不值得设置为一等 PDL 字段的平台专属元数据，如 `additivity`、`filters`、
`metricKind` 与 `measureShape`，它们是推荐机制。当各平台的使用模式逐渐清晰后，
这些字段可在未来的修订中提升为核心 schema 的一部分。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](37-metric.md)。
