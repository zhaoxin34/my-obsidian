---
title: 仪表板
entity: dashboard
order: 08
source: https://docs.datahub.com/docs/generated/metamodel/entities/dashboard.md
---

# 仪表板（Dashboard）

仪表板（dashboard）是可视化与图表的集合，用于提供对数据的洞察。在 DataHub 中，仪表板代表一组图表（可视化），通常存在于商业智能（BI）平台与数据可视化工具中。仪表板通常从 Looker、Tableau、PowerBI、Superset、Mode、Grafana 等平台摄取而来。

## 标识（Identity）

仪表板由两部分信息唯一标识：

- **所属平台**：承载该仪表板的具体 BI 工具或仪表板平台。例如 `looker`、`tableau`、`powerbi`、`superset`、`mode` 等。这对应于仪表板 key aspect 中的 `dashboardTool` 字段。
- **仪表板在特定平台中的标识符**：每个平台都有自己唯一标识仪表板的方式。例如 Looker 使用形如 `dashboards.999999` 的标识符，PowerBI 可能使用 GUID，而 Tableau 使用站点相对路径。

仪表板标识符的一个示例是 `urn:li:dashboard:(looker,dashboards.999999)`。

对于存在多个实例的平台（例如针对不同环境分别部署的 Looker），URN 可以包含平台实例标识符：`urn:li:dashboard:(looker,dashboards.999999,prod-instance)`。

## 重要能力（Important Capabilities）

### 仪表板信息与元数据

仪表板的核心元数据存储在 `dashboardInfo` aspect 中，其中包括：

- **标题（Title）**：仪表板的显示名称（可搜索，启用自动补全）
- **描述（Description）**：仪表板所展示内容的详细描述
- **仪表板 URL**：在原生平台中查看该仪表板的链接
- **访问级别（Access Level）**：仪表板的访问级别（PUBLIC 或 PRIVATE）
- **最后修改（Last Modified）**：跟踪仪表板创建、修改或删除的审计戳
- **最后刷新（Last Refreshed）**：仪表板数据最后刷新的时间戳，含刷新者信息
- **自定义属性（Custom Properties）**：平台特定的键值对形式的元数据

下面的代码片段展示了如何创建一个包含基本信息的仪表板。

**Python SDK：创建仪表板**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_create_simple.py
from datahub.metadata.urns import TagUrn
from datahub.sdk import Dashboard, DataHubClient

client = DataHubClient.from_env()

dashboard = Dashboard(
    name="example_dashboard",
    platform="looker",
    description="looker dashboard for production",
    tags=[TagUrn(name="production"), TagUrn(name="data_engineering")],
)

client.entities.upsert(dashboard)

```



对于包含图表与数据集的更复杂仪表板创建：

**Python SDK：创建带图表和数据集的仪表板**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_create_complex.py
from datahub.metadata.urns import TagUrn
from datahub.sdk import Chart, Dashboard, DataHubClient, Dataset

client = DataHubClient.from_env()
dashboard1 = Dashboard(
    name="example_dashboard_2",
    platform="looker",
    description="looker dashboard for production",
)
chart = Chart(
    name="example_chart",
    platform="looker",
    description="looker chart for production",
)

input_dataset = Dataset(
    name="example_dataset5",
    platform="snowflake",
    description="snowflake dataset for production",
)


dashboard2 = Dashboard(
    name="example_dashboard",
    platform="looker",
    description="looker dashboard for production",
    tags=[TagUrn(name="production"), TagUrn(name="data_engineering")],
    input_datasets=[input_dataset.urn],
    charts=[chart.urn],
    dashboards=[dashboard1.urn],
)


client.entities.upsert(dashboard1)
client.entities.upsert(chart)
client.entities.upsert(input_dataset)

client.entities.upsert(dashboard2)

```



### 容器关系 —— 仪表板中的图表

仪表板充当图表的容器。`dashboardInfo` aspect 的 `chartEdges` 字段跟踪哪些图表属于该仪表板，从而建立层级关系：

```
Dashboard (Container)
├── Chart 1 (Bar Chart)
├── Chart 2 (Pie Chart)
└── Chart 3 (Line Chart)
```

每个 chart edge 包含：

- **目标 URN（Destination URN）**：图表的 URN
- **创建时间（Created）**：图表被添加时的审计戳
- **最后修改（Last Modified）**：该关系被修改时的审计戳
- **属性（Properties）**：该关系的可选自定义属性

该关系支持：

- **导航**：用户可以从仪表板浏览到其组成图表
- **依赖跟踪**：了解哪些图表属于哪些仪表板
- **元数据传播**：归属与标签可以从仪表板继承到图表
- **影响分析**：当某个仪表板被废弃时，识别所有受影响的图表

**Python SDK：为仪表板添加图表**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_add_charts.py
from datahub.sdk import Chart, Dashboard, DataHubClient

client = DataHubClient.from_env()

# Create charts that belong to the dashboard
chart1 = Chart(platform="looker", name="sales_by_region_chart")
chart2 = Chart(platform="looker", name="revenue_trend_chart")
chart3 = Chart(platform="looker", name="customer_count_chart")

# Create dashboard with charts
dashboard = Dashboard(
    platform="looker",
    name="sales_dashboard",
    display_name="Sales Overview Dashboard",
    description="Comprehensive sales analytics dashboard",
)

# Add charts to the dashboard
dashboard.add_chart(chart1)
dashboard.add_chart(chart2)
dashboard.add_chart(chart3)

# Upsert the dashboard (this will also create the chart relationships)
client.entities.upsert(dashboard)

```



### 数据血缘 —— 数据集依赖

仪表板通常消费一个或多个数据集的数据。`dashboardInfo` aspect 的 `datasetEdges` 字段跟踪这些关系，在元数据图中创建 `Consumes` 关系。这支持：

- **影响分析**：了解某个数据集变更时受影响哪些仪表板
- **数据血缘可视化**：展示数据从源数据集流向仪表板的路径
- **依赖跟踪**：识别仪表板的所有上游依赖
- **合规性**：跟踪哪些仪表板使用了敏感或受监管的数据

**Python SDK：为仪表板添加数据集血缘**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_add_lineage.py
from datahub.sdk import Dashboard, DataHubClient, Dataset

client = DataHubClient.from_env()

# Define the source datasets
sales_dataset = Dataset(platform="bigquery", name="project.dataset.sales")
customer_dataset = Dataset(platform="bigquery", name="project.dataset.customers")
products_dataset = Dataset(platform="bigquery", name="project.dataset.products")

# Create dashboard with lineage to upstream datasets
dashboard = Dashboard(
    platform="looker",
    name="sales_dashboard",
    display_name="Sales Overview Dashboard",
    description="Dashboard showing sales metrics across regions and products",
)

# Add dataset dependencies
dashboard.add_input_dataset(sales_dataset)
dashboard.add_input_dataset(customer_dataset)
dashboard.add_input_dataset(products_dataset)

# Upsert the dashboard (this will create the Consumes relationships)
client.entities.upsert(dashboard)

```



### 嵌套仪表板

一些平台支持包含其他仪表板的仪表板（例如包含多个仪表板的 PowerBI App）。`dashboardInfo` aspect 的 `dashboards` 字段跟踪这些嵌套关系，从而支持层级化的仪表板组织：

```
PowerBI App (Dashboard)
├── Sales Dashboard (Dashboard)
│   ├── Chart 1
│   └── Chart 2
└── Marketing Dashboard (Dashboard)
    ├── Chart 3
    └── Chart 4
```

对于 PowerBI 这类 App 作为多个仪表板顶层容器的平台而言，这尤其有用。

### 字段级血缘

`inputFields` aspect（可选）提供细粒度跟踪，记录仪表板引用了哪些具体的数据集字段（列）。每个输入字段都会创建一个指向 `schemaField` 实体的 `consumesField` 关系，从而支持：

- **列级影响分析**：了解哪些仪表板使用了某个特定列
- **数据敏感性跟踪**：识别展示了敏感字段的仪表板
- **模式变更影响**：预测模式变更对仪表板的影响

### 可编辑属性（Editable Properties）

DataHub 将来自摄取源的元数据（位于 `dashboardInfo`）与用户在 DataHub UI 中编辑的元数据（位于 `editableDashboardProperties`）分离开来。这种分离确保：

- 用户编辑在多次摄取运行之间得以保留
- 源系统元数据在其字段上仍保持权威
- 用户可以增强元数据而不干扰自动化摄取

`editableDashboardProperties` aspect 目前支持：

- **描述（Description）**：用户提供的描述，用于补充或覆盖摄取的描述

**Python SDK：更新仪表板可编辑属性**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_update_editable.py
import datahub.metadata.schema_classes as models
from datahub.sdk import DashboardUrn, DataHubClient

client = DataHubClient.from_env()

dashboard_urn = DashboardUrn("looker", "dashboards.999999")

dashboard = client.entities.get(dashboard_urn)

current_editable = dashboard._get_aspect(models.EditableDashboardPropertiesClass)

if current_editable:
    current_editable.description = "Updated description added via DataHub UI"
else:
    current_editable = models.EditableDashboardPropertiesClass(
        description="Updated description added via DataHub UI"
    )
    dashboard._set_aspect(current_editable)

client.entities.update(dashboard)
print(f"Updated editable properties for dashboard {dashboard_urn}")

```



### 标签与术语表术语（Tags and Glossary Terms）

仪表板可以附加标签（Tag）或术语（Term）。阅读[这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)以了解标签与术语的区别。

#### 为仪表板添加标签

标签通过 `globalTags` aspect 添加到仪表板。

**Python SDK：为仪表板添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_add_tag.py
from datahub.sdk import DashboardUrn, DataHubClient, TagUrn

client = DataHubClient.from_env()

dashboard = client.entities.get(DashboardUrn("looker", "dashboards.999999"))

dashboard.add_tag(TagUrn("Production"))

client.entities.update(dashboard)

print(f"Added tag {TagUrn('Production')} to dashboard {dashboard.urn}")

```



#### 为仪表板添加术语表术语

术语通过 `glossaryTerms` aspect 添加。

**Python SDK：为仪表板添加术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_add_term.py
from datahub.metadata.urns import GlossaryTermUrn
from datahub.sdk import DashboardUrn, DataHubClient

client = DataHubClient.from_env()

dashboard = client.entities.get(DashboardUrn("looker", "dashboards.999999"))

dashboard.add_term(GlossaryTermUrn("SalesMetrics"))

client.entities.update(dashboard)

print(f"Added term {GlossaryTermUrn('SalesMetrics')} to dashboard {dashboard.urn}")

```



### 归属（Ownership）

归属通过 `ownership` aspect 与仪表板关联。所有者可以有不同类型，如 `DATAOWNER`、`TECHNICAL_OWNER`、`BUSINESS_OWNER` 等。归属可以从源系统继承，也可以在 DataHub 中添加。

**Python SDK：为仪表板添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_add_owner.py
from datahub.sdk import CorpUserUrn, DashboardUrn, DataHubClient

client = DataHubClient.from_env()

dashboard = client.entities.get(DashboardUrn("looker", "dashboards.999999"))

dashboard.add_owner(CorpUserUrn("jdoe"))

client.entities.update(dashboard)

print(f"Added owner {CorpUserUrn('jdoe')} to dashboard {dashboard.urn}")

```



### 使用统计（Usage Statistics）

仪表板可通过 `dashboardUsageStatistics` aspect 跟踪使用指标（实验性）。该时间序列 aspect 记录：

- **浏览次数（Views Count）**：仪表板被查看的总次数
- **执行次数（Executions Count）**：仪表板被刷新或同步的次数
- **独立用户数（Unique User Count）**：查看过该仪表板的不同用户数量
- **按用户的计数（Per-User Counts）**：按单个用户细分的使用明细
- **收藏数（Favorites Count）**：收藏该仪表板的用户数量
- **最后查看时间（Last Viewed At）**：最近一次查看的时间戳
- **事件粒度（Event Granularity）**：统计的时间分桶（按天、按小时）

使用统计有助于识别：

- 可能需要性能优化的热门仪表板
- 可以废弃的未使用仪表板
- 用户参与模式
- 仪表板采用率指标

**Python SDK：为仪表板添加使用统计**

```python
# Inlined from /metadata-ingestion/examples/library/dashboard_usage.py
from datetime import datetime
from typing import List

import datahub.metadata.schema_classes as models
from datahub.metadata.urns import CorpUserUrn
from datahub.sdk import DataHubClient
from datahub.sdk.dashboard import Dashboard

client = DataHubClient.from_env()

# Day 1: User activity and absolute usage statistics
usage_day_1_user_counts: List[models.DashboardUserUsageCountsClass] = [
    models.DashboardUserUsageCountsClass(
        user=str(CorpUserUrn("user1")),
        executionsCount=3,
        usageCount=3,
    ),
    models.DashboardUserUsageCountsClass(
        user=str(CorpUserUrn("user2")),
        executionsCount=2,
        usageCount=2,
    ),
]

usage_day_1_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-09", "%Y-%m-%d").timestamp() * 1000
    ),
    eventGranularity=models.TimeWindowSizeClass(unit=models.CalendarIntervalClass.DAY),
    uniqueUserCount=2,
    executionsCount=5,
    userCounts=usage_day_1_user_counts,
)

absolute_usage_day_1_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-09", "%Y-%m-%d").timestamp() * 1000
    ),
    favoritesCount=100,
    viewsCount=25,
    lastViewedAt=round(
        datetime.strptime("2022-02-09 04:45:30", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
    ),
)

dashboard = Dashboard(
    platform="looker",
    name="dashboards.999999",
    extra_aspects=[usage_day_1_stats, absolute_usage_day_1_stats],
)

client.entities.update(dashboard)

# Day 2: Updated user activity and absolute usage statistics
usage_day_2_user_counts: List[models.DashboardUserUsageCountsClass] = [
    models.DashboardUserUsageCountsClass(
        user=str(CorpUserUrn("user1")),
        executionsCount=4,
        usageCount=4,
    ),
    models.DashboardUserUsageCountsClass(
        user=str(CorpUserUrn("user2")),
        executionsCount=6,
        usageCount=6,
    ),
]

usage_day_2_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-10", "%Y-%m-%d").timestamp() * 1000
    ),
    eventGranularity=models.TimeWindowSizeClass(unit=models.CalendarIntervalClass.DAY),
    uniqueUserCount=2,
    executionsCount=10,
    userCounts=usage_day_2_user_counts,
)

absolute_usage_day_2_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-10", "%Y-%m-%d").timestamp() * 1000
    ),
    favoritesCount=100,
    viewsCount=27,
    lastViewedAt=round(
        datetime.strptime("2022-02-10 10:45:30", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
    ),
)

dashboard = Dashboard(
    platform="looker",
    name="dashboards.999999",
    extra_aspects=[usage_day_2_stats, absolute_usage_day_2_stats],
)

client.entities.update(dashboard)

# Day 3: Single user activity and absolute usage statistics
usage_day_3_user_counts: List[models.DashboardUserUsageCountsClass] = [
    models.DashboardUserUsageCountsClass(
        user=str(CorpUserUrn("user1")),
        executionsCount=2,
        usageCount=2,
    ),
]

usage_day_3_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-11", "%Y-%m-%d").timestamp() * 1000
    ),
    eventGranularity=models.TimeWindowSizeClass(unit=models.CalendarIntervalClass.DAY),
    uniqueUserCount=1,
    executionsCount=2,
    userCounts=usage_day_3_user_counts,
)

absolute_usage_day_3_stats = models.DashboardUsageStatisticsClass(
    timestampMillis=round(
        datetime.strptime("2022-02-11", "%Y-%m-%d").timestamp() * 1000
    ),
    favoritesCount=102,
    viewsCount=30,
    lastViewedAt=round(
        datetime.strptime("2022-02-11 02:45:30", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
    ),
)

dashboard = Dashboard(
    platform="looker",
    name="dashboards.999999",
    extra_aspects=[usage_day_3_stats, absolute_usage_day_3_stats],
)

client.entities.update(dashboard)

```



### 组织上下文（Organizational Context）

#### 域（Domains）

仪表板可通过 `domains` aspect 被归入某个域（业务领域或数据产品）。这有助于：

- 按业务职能组织仪表板
- 访问控制与治理
- 域专家进行检索发现

#### 容器层级（Container Hierarchy）

仪表板可以归属于更高层级的容器（例如 Tableau project 或 PowerBI workspace）。`container` aspect 跟踪该关系，创建层级结构：

```
Tableau Project (Container)
├── Sales Dashboard
├── Marketing Dashboard
└── Finance Dashboard
```

该层级对以下方面很重要：

- 在相关仪表板之间导航
- 理解组织结构
- 从容器向仪表板传播元数据（如归属）

### 嵌入与外部 URL

`embed` aspect 存储允许在外部应用中嵌入仪表板、或在原生平台中查看仪表板的 URL。`dashboardInfo` 中的 `dashboardUrl` 字段提供指向仪表板的直接链接。这支持：

- 在 wiki 或文档中嵌入仪表板
- 深链接到 BI 工具中的仪表板
- 与外部门户集成

### 仪表板子类型（Subtypes）

来自不同平台的仪表板可能在 `subTypes` aspect 中定义平台特定的子类型。例如：

- **PowerBI**：`PowerBI App`（容纳多个 PowerBI 仪表板的容器）
- **Looker**：不同的 Looker 仪表板类型
- **Tableau**：工作簿（workbook）类型

子类型帮助用户理解仪表板的平台特有属性。

## 与外部系统的集成

### 从 BI 平台摄取

仪表板通常通过 DataHub 的摄取连接器从 BI 平台自动摄取：

- **Looker**：摄取仪表板及其元素（图表 / looks）
- **Tableau**：摄取仪表板（工作簿）及其工作表
- **PowerBI**：摄取报表和应用（应用可包含多个仪表板）
- **Superset**：摄取仪表板及其图表
- **Mode**：摄取报表（仪表板）与查询
- **Grafana**：摄取仪表板及其面板

每个连接器都会将平台特定的仪表板元数据映射到 DataHub 的标准化仪表板模型，其中包括：

- 仪表板标题、描述与 URL
- 容器关系（仪表板内的图表）
- 数据集依赖（血缘）
- 归属信息
- 平台特有的自定义属性

### 查询仪表板信息

可以使用 DataHub 的 REST API 获取仪表板信息：

**获取仪表板实体快照**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Adashboard%3A(looker,dashboards.999999)'
```

响应包含仪表板的所有 aspect，包括：

- 仪表板信息（标题、描述、URL）
- 仪表板中包含的图表
- 仪表板消费的数据集
- 归属、标签与术语
- 使用统计
- 以及所有其他已配置的 aspect

### 关系 API（Relationships API）

可以查询仪表板关系，以了解它与其他实体的连接：

**查找仪表板中包含的图表**

```bash
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Adashboard%3A(looker,dashboards.999999)&types=Contains'
```

该请求返回所有属于此仪表板的图表。

**查找仪表板消费的数据集**

```bash
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Adashboard%3A(looker,dashboards.999999)&types=Consumes'
```

该请求返回此仪表板所依赖的所有数据集。

**查找包含某个特定图表的仪表板**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3Achart%3A(looker,look%2F1234)&types=Contains'
```

该请求返回所有包含指定图表的仪表板。

## GraphQL API

DataHub 的 GraphQL API 完整支持仪表板，提供：

- **查询（Queries）**：搜索、浏览与获取仪表板
- **变更（Mutations）**：创建、更新与删除仪表板
- **分面搜索（Faceted Search）**：按工具、访问级别及其他属性过滤仪表板
- **血缘查询（Lineage Queries）**：遍历上游（数据集）与下游关系
- **批量加载（Batch Loading）**：高效加载多个仪表板
- **使用统计（Usage Statistics）**：查询仪表板使用指标

GraphQL 的 `Dashboard` 类型包含所有标准元数据字段，以及图表、数据集和使用统计等仪表板特有属性。

## 值得注意的例外（Notable Exceptions）

### 平台特定的差异

不同 BI 平台对应仪表板的概念各不相同：

- **Tableau**：Tableau 的 "workbook" 对应 DataHub 的 dashboard 实体。一个工作簿包含多个 "sheet"（图表）。Tableau 中还存在工作簿内的 "dashboard"，它是 sheet 的集合 —— 这些同样在 DataHub 中被建模为 dashboard 实体。

- **PowerBI**：PowerBI 有 "report"（对应仪表板）和 "app"（容纳多个报表的容器）。App 也被建模为仪表板，但带有用于区分的子类型。

- **Looker**：Looker 仪表板包含 "element"，可以是图表、look 或文本元素。每个可视元素在 DataHub 中都会成为一个图表。

- **Superset**：Superset 仪表板包含 "slice"（图表）。关系是直接的 dashboard 到 chart。

### 已废弃字段

`dashboardInfo.charts` 与 `dashboardInfo.datasets` 字段已被 `dashboardInfo.chartEdges` 和 `dashboardInfo.datasetEdges` 取代。`Edges` 版本提供更丰富的关系元数据，包括关系创建或修改的时间戳与操作者。

### 容器 vs 父级

仪表板扮演双重角色：

- 它们是图表的**容器**（通过 `chartEdges`）
- 它们自身也可以有**父容器**（例如 Tableau project 或 PowerBI workspace）

这种两级层级对于理解组织结构很重要。

## 相关实体

仪表板经常与以下其他 DataHub 实体交互：

- **Chart**：仪表板包含图表（可视元素）
- **Dataset**：仪表板从数据集消费数据
- **SchemaField**：仪表板可通过字段级血缘引用特定字段 / 列
- **DataPlatform**：仪表板与特定的 BI 平台关联
- **Container**：仪表板可以归属于更高层级的容器（项目、工作区）
- **Domain**：仪表板可以归入业务域
- **GlossaryTerm**：仪表板可以用业务术语标注
- **Tag**：仪表板可以打标签以便于分类与发现
- **CorpUser / CorpGroup**：仪表板拥有所有者并被用户使用

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](08-dashboard.md)。
