---
title: 数据流
entity: dataflow
order: 04
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataflow.md
---

# 数据流

DataFlow 表示由 Apache Airflow、Azkaban、Prefect、Dagster 或类似工作流管理平台编排的高层数据处理流水线或工作流。DataFlow 作为相关 DataJob 的容器，呈现数据处理任务的整体执行上下文与组织方式。

## 标识

DataFlow 由三个组成部分唯一确定：

- **Orchestrator**：执行该流的工作流管理平台（例如 `airflow`、`azkaban`、`prefect`、`dagster`）
- **Flow ID**：工作流在编排器内的唯一标识符（通常是 DAG 名称、流水线名称或工作流标识符）
- **Cluster**：流运行所在的执行环境或集群（例如 `prod`、`staging`、`dev`）

URN 结构遵循以下模式：

```
urn:li:dataFlow:(<orchestrator>,<flowId>,<cluster>)
```

### URN 示例

**生产环境中的 Apache Airflow DAG：**

```
urn:li:dataFlow:(airflow,daily_sales_pipeline,prod)
```

**预发布环境中的 Prefect flow：**

```
urn:li:dataFlow:(prefect,customer_analytics,staging)
```

**开发环境中的 Azkaban workflow：**

```
urn:li:dataFlow:(azkaban,data_quality_checks,dev)
```

## 重要能力

### DataFlow 核心信息

DataFlow 通过 `dataFlowInfo` 方面维护关于该流水线的关键元数据：

- **Name**：该流的显示名称（可能与 flow_id 不同）
- **Description**：对该流作用及其目的的详细说明
- **Project**：该流所属的可选命名空间或项目
- **创建/修改时间戳**：该流在源系统中创建与最后修改的时间
- **External URL**：指向编排平台 UI 中该流的链接
- **Custom Properties**：用于附加平台特定元数据的键值对
- **Environment**：fabric 类型（PROD、DEV、STAGING 等）

### 可编辑属性

`editableDataFlowProperties` 方面允许用户通过 DataHub UI 修改某些属性，而不会干扰来自源系统的采集：

- **Description**：用户编辑的文档说明，其优先级高于采集而来的描述

这种分离确保在 DataHub 中所做的编辑会被保留，不会被后续的采集运行覆盖。

### 版本信息

`versionInfo` 方面用于追踪该流的版本信息：

- **Version**：形如 git commit hash 或 md5 hash 的标识符
- **Version Type**：所使用的版本标识符类型（例如 "git"、"md5"）

这对于追踪流水线代码变更、将流水线版本与其执行历史对应起来尤为有用。

### 与 DataJob 的关系

DataFlow 是 DataJob 的父实体。每个 DataJob 的标识都通过 DataJobKey 中的 `flow` 字段引用其父 DataFlow，从而形成层级关系：

```
DataFlow (Pipeline)
  └─ DataJob (Task 1)
  └─ DataJob (Task 2)
  └─ DataJob (Task 3)
```

该结构与工作流编排器在 DAG 或流水线中组织任务的方式一致。

### 事件追踪

`incidentsSummary` 方面提供了对数据质量或运维问题的可见性：

- **活动事件**：当前尚未解决、正在影响该流的事件
- **已解决事件**：已被处理的事件的历史记录
- **事件详情**：每个事件的类型、优先级、创建时间与解决时间

这使 DataHub 能够作为数据流水线的集中式事件管理系统。

## 代码示例

### 创建 DataFlow


**Python SDK：创建一个基础 DataFlow**

```python
# Inlined from /metadata-ingestion/examples/library/dataflow_create.py
from datahub.metadata.urns import TagUrn
from datahub.sdk import DataFlow, DataHubClient

client = DataHubClient.from_env()

dataflow = DataFlow(
    name="example_dataflow",
    platform="airflow",
    description="airflow pipeline for production",
    tags=[TagUrn(name="production"), TagUrn(name="data_engineering")],
)

client.entities.upsert(dataflow)

```



### 创建带完整元数据的 DataFlow


**Python SDK：创建带所有者、标签与自定义属性的 DataFlow**

```python
# Inlined from /metadata-ingestion/examples/library/dataflow_comprehensive.py
# metadata-ingestion/examples/library/dataflow_comprehensive.py
from datetime import datetime, timezone

from datahub.metadata.urns import CorpGroupUrn, CorpUserUrn, GlossaryTermUrn, TagUrn
from datahub.sdk import DataFlow, DataHubClient

client = DataHubClient.from_env()

# Create a DataFlow with comprehensive metadata
dataflow = DataFlow(
    platform="airflow",
    name="daily_sales_aggregation",
    display_name="Daily Sales Aggregation Pipeline",
    platform_instance="PROD-US-EAST",
    env="PROD",
    description="Aggregates daily sales data from multiple sources and updates reporting tables",
    external_url="https://airflow.company.com/dags/daily_sales_aggregation",
    custom_properties={
        "team": "analytics",
        "schedule": "0 2 * * *",
        "sla_hours": "4",
        "priority": "high",
    },
    created=datetime(2024, 1, 15, tzinfo=timezone.utc),
    last_modified=datetime.now(timezone.utc),
    subtype="ETL",
    owners=[
        CorpUserUrn("jdoe"),
        CorpGroupUrn("data-engineering"),
    ],
    tags=[
        TagUrn(name="production"),
        TagUrn(name="sales"),
        TagUrn(name="critical"),
    ],
    terms=[
        GlossaryTermUrn("Classification.Confidential"),
    ],
    domain="urn:li:domain:sales",
)

# Upsert the DataFlow
client.entities.upsert(dataflow)

print(f"Created DataFlow: {dataflow.urn}")
print(f"Display Name: {dataflow.display_name}")
print(f"Description: {dataflow.description}")
print(f"External URL: {dataflow.external_url}")
print(f"Custom Properties: {dataflow.custom_properties}")

```



### 读取 DataFlow 元数据


**Python SDK：读取 DataFlow 并访问其属性**

```python
# Inlined from /metadata-ingestion/examples/library/dataflow_read.py
from datahub.sdk import DataFlowUrn, DataHubClient

client = DataHubClient.from_env()

# Or get this from the UI (share -> copy urn) and use DataFlowUrn.from_string(...)
dataflow_urn = DataFlowUrn(
    orchestrator="airflow", flow_id="example_dataflow", cluster="PROD"
)

dataflow_entity = client.entities.get(dataflow_urn)
print("DataFlow name:", dataflow_entity.name)
print("DataFlow platform:", dataflow_entity.platform)
print("DataFlow description:", dataflow_entity.description)

```



### 为 DataFlow 添加标签与术语


**Python SDK：为 DataFlow 添加标签和术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/dataflow_add_tags_terms.py
# metadata-ingestion/examples/library/dataflow_add_tags_terms.py
from datahub.metadata.urns import DataFlowUrn, GlossaryTermUrn, TagUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

# Get the existing DataFlow
dataflow_urn = DataFlowUrn("airflow", "daily_sales_pipeline", "prod")
dataflow = client.entities.get(dataflow_urn)

# Add tags
dataflow.add_tag(TagUrn(name="pii"))
dataflow.add_tag(TagUrn(name="quarterly-review"))

# Add glossary terms
dataflow.add_term(GlossaryTermUrn("DataQuality.Validated"))
dataflow.add_term(GlossaryTermUrn("BusinessCritical.Revenue"))

# Save changes
client.entities.upsert(dataflow)

print(f"Updated DataFlow: {dataflow.urn}")
print(f"Tags: {[str(tag) for tag in dataflow.tags] if dataflow.tags else []}")
print(f"Terms: {[str(term) for term in dataflow.terms] if dataflow.terms else []}")

```



### 为 DataFlow 添加所有权


**Python SDK：为 DataFlow 设置所有者**

```python
# Inlined from /metadata-ingestion/examples/library/dataflow_add_ownership.py
# metadata-ingestion/examples/library/dataflow_add_ownership.py
from datahub.metadata.urns import CorpGroupUrn, CorpUserUrn, DataFlowUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

# Get the existing DataFlow
dataflow_urn = DataFlowUrn("airflow", "daily_sales_pipeline", "prod")
dataflow = client.entities.get(dataflow_urn)

# Add individual owners
dataflow.add_owner((CorpUserUrn("alice"), "DATAOWNER"))
dataflow.add_owner((CorpUserUrn("bob"), "DEVELOPER"))

# Add group owner
dataflow.add_owner((CorpGroupUrn("analytics-team"), "DATAOWNER"))

# Save changes
client.entities.upsert(dataflow)

print(f"Updated DataFlow: {dataflow.urn}")
print(f"Owners: {dataflow.owners}")

```



### 通过 REST API 查询 DataFlow

DataFlow 可通过标准的 DataHub REST API 查询：


**REST API：获取 DataFlow 实体**

```bash
# Get a complete DataFlow snapshot
curl 'http://localhost:8080/entitiesV2/urn%3Ali%3AdataFlow%3A(airflow,daily_sales_pipeline,prod)'
```

响应包含全部方面：

```json
{
  "urn": "urn:li:dataFlow:(airflow,daily_sales_pipeline,prod)",
  "aspects": {
    "dataFlowKey": {
      "orchestrator": "airflow",
      "flowId": "daily_sales_pipeline",
      "cluster": "prod"
    },
    "dataFlowInfo": {
      "name": "Daily Sales Pipeline",
      "description": "Processes daily sales data and updates aggregates",
      "project": "analytics",
      "externalUrl": "https://airflow.company.com/dags/daily_sales_pipeline"
    },
    "ownership": { ... },
    "globalTags": { ... }
  }
}
```



### 创建包含 DataJob 的 DataFlow


**Python SDK：创建带关联 DataJob 的 DataFlow**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_create_full.py
from datahub.metadata.urns import DatasetUrn, TagUrn
from datahub.sdk import DataFlow, DataHubClient, DataJob

client = DataHubClient.from_env()

# datajob will inherit the platform and platform instance from the flow

dataflow = DataFlow(
    platform="airflow",
    name="example_dag",
    platform_instance="PROD",
    description="example dataflow",
    tags=[TagUrn(name="tag1"), TagUrn(name="tag2")],
)

datajob = DataJob(
    name="example_datajob",
    flow=dataflow,
    inlets=[
        DatasetUrn(platform="hdfs", name="dataset1", env="PROD"),
    ],
    outlets=[
        DatasetUrn(platform="hdfs", name="dataset2", env="PROD"),
    ],
)

client.entities.upsert(dataflow)
client.entities.upsert(datajob)

```



## 集成点

### 与 DataJob 的关系

DataFlow 与 DataJob 之间通过 `IsPartOf` 关系构成父子关系。这是主要的集成点：

```python
from datahub.sdk import DataFlow, DataJob, DataHubClient

# DataJob automatically links to its parent DataFlow
flow = DataFlow(platform="airflow", name="my_dag")
job = DataJob(name="extract_data", flow=flow)
```

### 与数据集的关系

虽然 DataFlow 本身不直接引用数据集，但其子 DataJob 会通过以下方式与数据集建立血缘关系：

- **Inlets**：作业消费的输入数据集
- **Outlets**：作业产出的输出数据集

这通过 DataFlow 的组成作业形成了到数据集的间接血缘。

### 编排器平台集成

常见会产生 DataFlow 实体的编排器：

- **Apache Airflow**：每个 DAG 成为一个 DataFlow，任务成为 DataJob
- **Prefect**：Flow 是 DataFlow，task 是 DataJob
- **Dagster**：Job/Pipeline 是 DataFlow，op/solid 是 DataJob
- **Azkaban**：Flow 是 DataFlow，job 是 DataJob
- **Fivetran**：连接器表示为 DataFlow，同步操作表示为 DataJob

### DataProcessInstance 追踪

DataFlow 的执行可通过 DataProcessInstance 实体进行追踪，其中记录：

- 流运行的开始与结束时间
- 成功/失败状态
- 特定运行的输入与输出数据集

这使得流水线运行历史可被追踪，并有助于排查失败原因。

### GraphQL 集成

DataFlow 实体通过 DataHub 的 GraphQL API 暴露，完整支持：

- 查询流元数据
- 按编排器和集群浏览流
- 按名称、描述和项目搜索流
- 更新流属性（所有权、标签、术语等）

关键 GraphQL 解析器：

- `dataFlow`：按 URN 获取单个 DataFlow
- `searchAcrossEntities`：带过滤条件搜索 DataFlow
- `updateDataFlow`：修改 DataFlow 属性

## 值得注意的例外

### Cluster 与 Environment

DataFlow 在 URN 中使用 `cluster` 字段进行标识，同时在 `dataFlowInfo` 方面中还有 `env` 字段。二者用途不同：

- **Cluster**：身份的一部分，通常与环境一致，但也可以表示特定的部署实例
- **环境（env）**：fabric 类型（PROD、DEV、STAGING）的语义标识，可搜索、可过滤

在大多数情况下两者应当一致（例如 cluster="prod" 与 env="PROD"），但在存在多个生产集群或需要表达复杂部署拓扑时，它们可能不一致。

### Platform 与 Orchestrator

在整个代码库中，你会同时看到这两个术语：

- 在 URN 结构和 key 方面中，该字段名为 `orchestrator`
- 在 Python SDK 和部分 API 中，它被称为 `platform`

二者是同义的，都指执行该流的工作流管理系统。

### 旧版 API 与 SDK

创建 DataFlow 存在两套 API：

1. **旧版 API**（`datahub.api.entities.datajob.DataFlow`）：使用较早的 emitter 模式
2. **现代 SDK**（`datahub.sdk.DataFlow`）：推荐方式，接口更简洁

新代码应使用现代 SDK（从 `datahub.sdk` 导入），尽管两者都仍在维护以保持向后兼容。

### DataFlow 与 DataPipeline

在某些上下文中，你可能在文档或 UI 里看到 "data pipelines" 的说法。这些是非正式称谓，指向的就是 DataFlow。元数据模型中正式的实体类型是 `dataFlow`，而不是 `dataPipeline`。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](04-dataflow.md)。
