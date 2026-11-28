---
title: 指标
entity: metric
order: 37
source: https://docs.datahub.com/docs/generated/metamodel/entities/metric.md
---

# 指标

指标（metric）实体表示在语义层或指标存储中定义的、具名且可复用的业务度量。

## 身份（Identity）

指标由三个字段标识：

- **`platform`** —— 拥有该指标的 DataPlatform URN（例如 `urn:li:dataPlatform:dbt`、`urn:li:dataPlatform:snowflake`）。可作为 URN 字段进行搜索，支持自动补全和 "Platform" 过滤标签。
- **`path`** —— 在其平台内界定该指标作用范围的命名空间路径，避免两个团队在同一平台上定义相同 `id` 的指标时发生名称冲突。
- **`id`** —— 该平台与路径下的指标名称（例如 `total_revenue`、`daily_active_users`）。

URN 示例：`urn:li:metric:(urn:li:dataPlatform:dbt,analytics.orders_model,revenue)`。

## 重要能力（Important Capabilities）

### 指标信息

核心元数据存储在 `metricInfo` aspect 中：

- **`name`** —— 人类可读的显示名称；用于全文搜索与自动补全。
- **`description`** —— 自由文本描述，说明该指标衡量什么。
- **`created`** —— `AuditStamp`（`time` + `actor`），记录指标何时由谁创建。搜索索引为 `createdAt`（DATETIME）。
- **`lastModified`** —— `AuditStamp`，记录最近一次修改。搜索索引为 `lastModifiedAt`（DATETIME）。
- **`expression`** —— 以一种或多种 SQL 方言表达的指标公式。每个 `DialectExpression` 将一个 `Dialect` 枚举值与原始 SQL 字符串配对。
- **`semanticModel`** —— 可选的所属 SemanticModel 的 URN。权威的成员关系指针。搜索索引为 `semanticModel` / `hasSemanticModel`。未关联语义模型而摄入的指标（例如来自 BI 工具的纯目录型指标）该字段保持未设置。

### AI 上下文

可选的 AI/LLM 提示存储在一等 `aiContext` aspect 中（同义词、自然语言指令、少样本示例、自定义指令）。

### 指标关系

层级与派生关系存储在 `metricRelationships` aspect 中：

- **`parentMetric`** —— 父指标的 URN。用于构建指标的层级树。以 `IsPartOf` 图边形式存储。
- **`derivedFrom`** —— 指向源指标的 `DerivedMetricInput` 记录数组。`DerivedMetricInput` 包含 `Edge`，因此其载荷为 Edge 形态（`destinationUrn`、审计戳、`properties` 包）。这些边标记为 `isLineage: true`，因此会出现在 DataHub 血缘图中。
- **`relatedMetrics`** —— 指向语义相关指标的 `Edge` 记录数组（无血缘标记）。

### 治理与血缘

指标实体复用以下标准治理 aspects：`ownership`、`domains`、`globalTags`、`glossaryTerms`、`institutionalMemory`、`structuredProperties`、`status`、`deprecation`、`dataPlatformInstance`、`subTypes`、`documentation`、`browsePathsV2`、`applications`、`aiContext`。

## 与其他实体的关系（Relationships with Other Entities）

| 关系 | 方向 | 目标实体 | Aspect / 边名称 | 血缘？ |
| ---------------------- | --------- | --------------- | ---------------------------------- | -------- |
| ModeledBy              | 出向  | `semanticModel` | `metricInfo.semanticModel`         | 否       |
| IsPartOf               | 出向  | `metric`        | `metricRelationships`              | 否       |
| DerivedFrom            | 出向  | `metric`        | `metricRelationships`              | 是      |
| RelatedTo              | 出向  | `metric`        | `metricRelationships`              | 否       |
| Consumes（数据集）     | 出向  | `dataset`       | `metricUpstreams.datasetUpstreams` | 是      |
| Consumes（schemaField） | 出向  | `schemaField`   | `metricUpstreams.fieldUpstreams`   | 是      |

语义模型成员关系仅存于成员侧：`metricInfo.semanticModel`（`ModeledBy`，非血缘）是唯一事实来源。列出某模型的指标即是对 `semanticModel` 的 ES 过滤（可选地加上 `hasSemanticModel=true`）。

指标到数据集、指标到列的血缘由专门的 `metricUpstreams` aspect 承载。`datasetUpstreams` 与 `fieldUpstreams` 各自独立可选，因此摄入源可按其能提取的粒度填充。指标到指标的派生血缘存放在 `metricRelationships.derivedFrom`，不会并入 `metricUpstreams`。

**基于语义模型的指标的约定**：填充 `metricUpstreams.datasetUpstreams`，写入该指标读取的语义模型数据集 URN。SemanticModel 本身是容器（包围框），而非血缘的一跳 —— 标准链为 `Metric → 逻辑数据集（Semantic Model Dataset）→ 物理数据集`。

## 值得注意的例外（Notable Exceptions）

### 与环境无关的身份

指标在键中编码了 `platform`（一个 DataPlatform URN），但刻意**不**编码 `FabricType`（与数据集不同，数据集的 URN 中包含 PROD/STAGING）。指标被建模为与环境无关的业务定义：PROD 与 STAGING 中的 `total_revenue` 是同一概念，因此两者解析为同一 URN。跨平台指标（例如 dbt 与 Snowflake 中相同的度量）仍是独立实体，因为 `platform` 是 URN 的一部分。

### 通过 structuredProperties 扩展

实体级扩展性使用 `structuredProperties` aspect，该 aspect 已为 `metric` 实体注册。结构化属性支持类型化取值、治理控制、搜索分面与 PATCH 语义 —— 对于尚不值得引入一等 PDL 字段的平台特定元数据（如 `additivity`、`filters`、`metricKind` 和 `measureShape`），它们是推荐的机制。当各平台的使用模式逐渐清晰后，这些字段可以在未来的版本修订中被提升到核心 schema 中。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](37-metric.md)。。
