---
title: 图表
entity: chart
order: 07
source: https://docs.datahub.com/docs/generated/metamodel/entities/chart.md
---

# 图表

图表（Chart）是数据的可视化表示，通常出现在商业智能（BI）平台和仪表板工具中。在 DataHub 中，图表表示诸如柱状图、饼图、折线图、表格等单个可视化对象。图表通常从 Looker、Tableau、PowerBI、Superset、Mode 等平台摄取而来。

## 标识

图表由两条信息标识：

- **所属平台**：承载该图表的具体 BI 工具或仪表板平台。例如 `looker`、`tableau`、`powerbi`、`superset`、`mode` 等。这对应于图表关键 aspect 中的 `dashboardTool` 字段。
- **该平台内的图表标识符**：每个平台都有自己在系统内唯一标识图表的方式。例如 Looker 使用形如 `look/1234` 的标识符，而 PowerBI 可能使用形如 `tile-abc-123` 的磁贴标识符。

图表标识符的示例为 `urn:li:chart:(looker,look/1234)`。

对于拥有多个实例的平台（例如针对不同环境的独立 Looker 部署），URN 可以包含平台实例标识符：`urn:li:chart:(looker,look/1234,prod-instance)`。

## 重要能力

### 图表信息与元数据

关于图表的核心元数据存储在 `chartInfo` aspect 中，包括：

- **Title**：图表的展示名称（可搜索）
- **Description**：对该图表所展示内容的详细描述
- **Chart Type**：可视化类型（BAR、PIE、SCATTER、TABLE、TEXT、LINE、AREA、HISTOGRAM、BOX_PLOT、WORD_CLOUD、COHORT）
- **Chart URL**：在原生平台中查看图表的链接
- **Access Level**：图表的访问级别（PUBLIC 或 PRIVATE）
- **Last Modified**：追踪图表创建、修改或删除时间的审计戳
- **Last Refreshed**：图表数据最近一次刷新的时间戳

下面的代码片段展示了如何创建一个带基本信息的图表。


**Python SDK：创建图表**

```python
# Inlined from /metadata-ingestion/examples/library/chart_create_simple.py
from datahub.metadata.urns import TagUrn
from datahub.sdk import Chart, DataHubClient

client = DataHubClient.from_env()

chart = Chart(
    name="example_chart",
    platform="looker",
    description="looker chart for production",
    tags=[TagUrn(name="production"), TagUrn(name="data_engineering")],
)

client.entities.upsert(chart)

```


如需创建带更多元数据的复杂图表：


**Python SDK：创建带完整元数据的图表**

```python
# Inlined from /metadata-ingestion/examples/library/chart_create_complex.py
from datahub.metadata.urns import TagUrn
from datahub.sdk import Chart, DataHubClient, Dataset

client = DataHubClient.from_env()

input_datasets = [
    Dataset(
        name="example_dataset",
        platform="snowflake",
        description="looker dataset for production",
        schema=[("id", "string"), ("name", "string")],
    ),
    Dataset(
        name="example_dataset_2",
        platform="snowflake",
        description="looker dataset for production",
        schema=[("id", "string"), ("name", "string")],
    ),
    Dataset(
        name="example_dataset_3",
        platform="snowflake",
        description="looker dataset for production",
        schema=[("id", "string"), ("name", "string")],
    ),
]

# create a chart with two input datasets
chart = Chart(
    name="example_chart",
    platform="looker",
    description="looker chart for production",
    tags=[TagUrn(name="production"), TagUrn(name="data_engineering")],
    input_datasets=[input_datasets[0], input_datasets[1]],
)

for dataset in input_datasets:
    client.entities.upsert(dataset)

# add a new dataset to the chart
chart.add_input_dataset(input_datasets[2])
client.entities.upsert(chart)

```


### 图表查询

图表通常有底层查询（SQL、LookML 等）定义数据的获取与处理方式。`chartQuery` aspect 存储这些信息：

- **Raw Query**：用于生成图表的实际查询文本
- **Query Type**：查询类型（LOOKML 或 SQL）

这些信息对于理解数据血缘和进行审计尤为有用。

### 数据血缘与输入数据集

图表从一个或多个数据集（有时也来自其他图表）消费数据。`chartInfo` aspect 的 `inputEdges` 字段追踪这些关系，在元数据图中创建 `Consumes` 关系。这带来以下能力：

- **影响分析**：了解数据集变更时受影响的图表
- **数据血缘可视化**：展示数据从源数据集流向图表的过程
- **依赖追踪**：识别图表的所有上游依赖


**Python SDK：为图表添加血缘**

```python
# Inlined from /metadata-ingestion/examples/library/chart_add_lineage.py
from datahub.sdk import Chart, DataHubClient, Dataset

client = DataHubClient.from_env()

# Define the source datasets
upstream_dataset1 = Dataset(platform="bigquery", name="project.dataset.sales_table")
upstream_dataset2 = Dataset(platform="bigquery", name="project.dataset.customer_table")

# Create a chart with lineage to upstream datasets
chart = Chart(
    name="sales_by_customer_chart",
    platform="looker",
    display_name="Sales by Customer",
    description="Bar chart showing total sales aggregated by customer",
    input_datasets=[upstream_dataset1, upstream_dataset2],
)

client.entities.upsert(chart)

```


### 字段级血缘

`inputFields` aspect 提供了细粒度追踪，记录图表引用了哪些具体的数据集字段（列）。每个输入字段都会创建一个指向 `schemaField` 实体的 `consumesField` 关系，从而支持：

- **列级影响分析**：了解哪些图表使用了某个特定列
- **数据敏感度追踪**：识别展示敏感字段的图表
- **Schema 变更影响**：预测 schema 变更对可视化造成的影响

### 可编辑属性

DataHub 将来自摄取源的元数据（在 `chartInfo` 中）与用户在 DataHub UI 中编辑的元数据（在 `editableChartProperties` 中）分离开来。这种划分确保：

- 用户编辑在多次摄取运行之间得以保留
- 源系统元数据在其字段上保持权威
- 用户可以丰富元数据而不干扰自动化摄取

`editableChartProperties` aspect 当前支持：

- **Description**：用户提供的描述，用于补充或覆盖摄取而来的描述

### 标签与术语表术语

图表可以附加 Tag 或术语表术语。阅读[这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)以了解 tag 与术语之间的区别。

#### 为图表添加标签

标签通过 `globalTags` aspect 添加到图表。


**Python SDK：为图表添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/chart_add_tag.py
from datahub.sdk import ChartUrn, DataHubClient, TagUrn

client = DataHubClient.from_env()

chart = client.entities.get(ChartUrn("looker", "sales_dashboard"))

chart.add_tag(TagUrn("Important"))

client.entities.update(chart)

print(f"Added tag {TagUrn('Important')} to chart {chart.urn}")

```


#### 为图表添加术语表术语

术语表术语通过 `glossaryTerms` aspect 添加。


**Python SDK：为图表添加术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/chart_add_term.py
from datahub.metadata.urns import GlossaryTermUrn
from datahub.sdk import ChartUrn, DataHubClient

client = DataHubClient.from_env()

chart = client.entities.get(ChartUrn("looker", "sales_dashboard"))

chart.add_term(GlossaryTermUrn("Revenue"))

client.entities.update(chart)

print(f"Added term {GlossaryTermUrn('Revenue')} to chart {chart.urn}")

```


### 归属

图表的归属通过 `ownership` aspect 关联。负责人可以是不同类型，例如 `DATAOWNER`、`TECHNICAL_OWNER`、`BUSINESS_OWNER` 等。归属可以从源系统继承，也可以在 DataHub 中添加。


**Python SDK：为图表添加负责人**

```python
# Inlined from /metadata-ingestion/examples/library/chart_add_owner.py
from datahub.sdk import ChartUrn, CorpUserUrn, DataHubClient

client = DataHubClient.from_env()

chart = client.entities.get(ChartUrn("looker", "sales_dashboard"))

chart.add_owner(CorpUserUrn("jdoe"))

client.entities.update(chart)

print(f"Added owner {CorpUserUrn('jdoe')} to chart {chart.urn}")

```


### 使用统计

图表可以通过 `chartUsageStatistics` aspect 跟踪使用指标（实验性）。该时间序列 aspect 记录：

- **Views Count**：图表被查看的总次数
- **Unique User Count**：查看过该图表的不同用户数
- **Per-User Counts**：按用户细化的使用情况明细

使用统计有助于识别：

- 可能需要性能优化的热门图表
- 可以弃用的未使用图表
- 用户参与模式

### 组织上下文

#### 领域

图表可以使用 `domains` aspect 被组织到领域（业务区域或数据产品）中。这有助于：

- 按业务职能组织图表
- 访问控制与治理
- 领域专家的发现

#### 容器

图表通常隶属于一个仪表板（其父容器）。`container` aspect 追踪该关系，构成层级结构：

```
Dashboard (Container)
├── Chart 1
├── Chart 2
└── Chart 3
```
该层级结构对于以下方面很重要：

- 导航相关联的可视化
- 理解图表上下文
- 从仪表板向图表传播元数据（如归属）

### 嵌入与外部 URL

`embed` aspect 存储允许在外部应用中嵌入图表、或在原生平台中查看图表的 URL。这支持：

- 在 wiki 或文档中嵌入图表
- 深链接到 BI 工具中的图表
- 与外部门户集成

### 图表子类型

来自不同平台的图表可能在 `subTypes` aspect 中定义平台特有的子类型。例如：

- **Looker**：`Look`（已保存的 Looker 可视化）
- **PowerBI**：`PowerBI Tile`（PowerBI 报表页面上的磁贴）
- **Mode**：`Chart`、`Report`（不同的 Mode 可视化类型）

子类型帮助用户理解图表的平台特有属性。

## 与外部系统的集成

### 从 BI 平台摄取

图表通常使用 DataHub 的摄取连接器从 BI 平台自动摄取：

- **Looker**：摄取 Look（已保存的可视化）和仪表板元素
- **Tableau**：从工作簿中摄取 sheet（工作表）
- **PowerBI**：从报表中摄取磁贴
- **Superset**：从仪表板中摄取图表
- **Mode**：摄取图表和可视化
- **Metabase**：摄取问题和可视化

每个连接器都会将平台特有的图表元数据映射到 DataHub 的标准化图表模型。

### 查询图表信息

你可以使用 DataHub 的 REST API 获取图表信息：


**获取图表实体快照**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Achart%3A(looker,look%2F1234)'
```
响应包含该图表的所有 aspect，包括：

- 图表信息（标题、描述、类型）
- 输入数据集（血缘）
- 归属、标签和术语
- 使用统计
- 以及所有其他已配置的 aspect

### 关系 API

你可以查询图表关系，以了解它与其他实体的连接：


**查找图表消费的数据集**

```bash
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Achart%3A(looker,look%2F1234)&types=Consumes'
```
这将返回该图表从中消费数据的所有数据集（以及可能的其他图表）。




**查找消费某个特定数据集的图表**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Abigquery,project.dataset.table,PROD)&types=Consumes'
```
这将返回所有依赖该特定数据集的图表。



## GraphQL API

DataHub 的 GraphQL API 完整支持图表，提供：

- **查询**：搜索、浏览和获取图表
- **变更**：创建、更新和删除图表
- **分面搜索**：按工具、类型、访问级别和查询类型过滤图表
- **血缘查询**：遍历上游和下游关系
- **批量加载**：高效加载多个图表

GraphQL 的 `Chart` 类型包含所有标准元数据字段，以及查询定义和使用统计等图表特有属性。

## 值得注意的例外

### 平台特有的差异

不同 BI 平台有不同映射到图表的概念：

- **Tableau 的 sheet 与 dashboard**：在 Tableau 中，"sheet"（工作表）映射为 DataHub 图表，而 "dashboard" 映射为 DataHub 仪表板实体。一个 Tableau 仪表板可以包含多个 sheet。

- **PowerBI 的磁贴**：PowerBI 有 "tiles"（固定可视化）的概念，在 DataHub 中建模为图表。一个磁贴可以引用多个底层报表或数据集。

- **Looker 的 Look 与仪表板元素**：Looker 有独立的 "Looks"（已保存的可视化）和仪表板元素，两者都在 DataHub 中建模为图表。

### 图表到图表的血缘

虽然大多数图表从数据集消费数据，但某些平台支持派生自其他图表的图表。DataHub 通过图表到图表的 `Consumes` 关系支持这一点，从而实现多层级可视化血缘。

### 已废弃字段

`chartInfo.inputs` 字段已被 `chartInfo.inputEdges` 取代。`inputEdges` 字段提供更丰富的关系元数据，包括关系创建或修改时的时间戳与操作者。

## 相关实体

图表经常与以下其他 DataHub 实体交互：

- **Dashboard**：图表通常包含在仪表板中
- **Dataset**：图表从数据集消费数据
- **SchemaField**：图表通过字段级血缘引用特定字段/列
- **DataPlatform**：图表关联到特定的 BI 平台
- **Domain**：图表可以被组织到业务领域中
- **GlossaryTerm**：图表可以用业务术语标注
- **Tag**：图表可以打标签以便分类和发现
- **CorpUser / CorpGroup**：图表有负责人，并被用户使用

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](07-chart.md)。
