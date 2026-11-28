---
title: 数据处理
entity: dataprocess
order: 05
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataprocess.md
---

# 数据处理

> **已弃用**：该实体已弃用，不应用于新的实现。
>
> **请改用 [dataFlow](04-dataflow.md) 和 [dataJob](03-datajob.md。** 和 [dataJob](03-datajob.md。**)
>
> `dataProcess` 实体是早期对数据处理任务建模的尝试，现已被更健壮、更灵活的 `dataFlow` 和 `dataJob` 实体取代，后者能更好地体现现代数据流水线的层级结构。

## 弃用说明

弃用 `dataProcess` 实体是为了更清晰地划分：

- **DataFlow**：表示整体的流水线/工作流（例如一个 Airflow DAG、dbt 项目、Spark 应用）
- **DataJob**：表示流水线中的单个任务（例如一个 Airflow task、dbt model、Spark job）

这种两级层次结构更符合现代编排系统组织数据处理工作的方式，并为血缘跟踪、所有权分配和运维监控提供了更大的灵活性。

### 为什么被弃用？

最初的 `dataProcess` 实体存在若干局限：

1. **没有层次结构**：无法表示流水线与其组成任务之间的关系
2. **编排器支持有限**：扁平结构无法很好地映射到基于 DAG 的编排平台，如 Airflow、Prefect 或 Dagster
3. **语义不清晰**：无法确定 dataProcess 代表的是整条流水线还是单个任务
4. **血缘建模薄弱**：缺少任务级粒度，血缘关系不够精确

新的 `dataFlow` 和 `dataJob` 模型通过提供清晰的父子关系解决了这些局限，映射真实的数据处理架构。

## 标识（历史参考）

DataProcess 实体由三个组成部分标识：

- **Name**：流程名称（通常是 ETL 作业名称）
- **Orchestrator**：工作流管理平台（例如 `airflow`、`azkaban`）
- **Origin (Fabric)**：流程运行的环境（PROD、DEV 等）

URN 结构为：

```
urn:li:dataProcess:(<name>,<orchestrator>,<origin>)
```

### URN 示例

```
urn:li:dataProcess:(customer_etl_job,airflow,PROD)
urn:li:dataProcess:(sales_aggregation,azkaban,DEV)
```

## 重要能力（历史参考）

### DataProcessInfo Aspect

`dataProcessInfo` aspect 捕获流程的输入与输出：

- **Inputs**：流程消费的数据集 URN 数组
- **Outputs**：流程产出的数据集 URN 数组

这通过与数据集之间的 "Consumes" 关系建立了基本的血缘关系。

### 通用 Aspects

与其他实体一样，dataProcess 支持：

- **所有权**：为流程分配所有者
- **状态**：将流程标记为已移除
- **全局标签**：分类与归类
- **机构记忆**：指向文档的链接

## 迁移指南

### 何时使用 DataFlow，何时使用 DataJob

**在表示以下内容时使用 DataFlow：**

- Airflow DAG
- dbt 项目
- Prefect flow
- Dagster pipeline
- Azkaban workflow
- 任何相关数据处理任务的容器

**在表示以下内容时使用 DataJob：**

- DAG 中的 Airflow task
- 项目中的 dbt model
- flow 中的 Prefect task
- pipeline 中的 Dagster op/asset
- 单个处理步骤

**两者结合使用：**

- 为流水线创建一个 DataFlow
- 为流水线中的每个任务创建 DataJob
- 将 DataJob 链接到其父 DataFlow

### 概念映射

| DataProcess 概念 | 新模型对应物             | 说明                             |
| ------------------- | -------------------------- | -------------------------------- |
| 含任务的流程        | DataFlow + DataJobs       | 拆分为两个实体                  |
| 流程名称            | DataFlow flowId           | 成为父级标识符                  |
| 单步骤流程          | DataFlow + 1 个 DataJob   | 仍需同时创建两个实体             |
| 编排器              | DataFlow orchestrator     | 概念相同，建模更佳               |
| 来源/Fabric         | DataFlow cluster          | 通常与对应环境一致               |
| 输入/输出           | DataJob dataJobInputOutput| 移至作业层级以提升精确性         |

### 迁移步骤

从 `dataProcess` 迁移到 `dataFlow`/`dataJob`：

1. **确定流程结构**：判断你的 dataProcess 代表的是流水线（包含多个步骤）还是单个任务

2. **创建 DataFlow**：表示整体的流水线/工作流

   - 使用相同的 orchestrator 值
   - 使用流程名称作为 flow ID
   - 使用 cluster 标识符（通常与 origin/fabric 一致）

3. **创建 DataJob**：在 flow 内创建一个或多个作业

   - 对于单步骤流程：创建一个以流程命名的作业
   - 对于多步骤流程：为每个步骤创建一个作业
   - 将每个作业链接到其父 DataFlow

4. **迁移血缘**：将输入/输出数据集关系从流程层级移至作业层级

5. **迁移元数据**：将所有权、标签和文档转移到相应实体（通常流水线级元数据归 DataFlow，任务级元数据归具体 DataJob）

### 迁移示例

**示例 1：简单单任务流程**

旧 dataProcess：

```
urn:li:dataProcess:(daily_report,airflow,PROD)
```

新结构：

```
DataFlow: urn:li:dataFlow:(airflow,daily_report,prod)
DataJob:  urn:li:dataJob:(urn:li:dataFlow:(airflow,daily_report,prod),daily_report_task)
```

**示例 2：多步骤 ETL 流水线**

旧 dataProcess：

```
urn:li:dataProcess:(customer_pipeline,airflow,PROD)
```

新结构：

```
DataFlow: urn:li:dataFlow:(airflow,customer_pipeline,prod)
DataJob:  urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),extract_customers)
DataJob:  urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),transform_customers)
DataJob:  urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),load_customers)
```

## 代码示例

### 查询已存在的 DataProcess 实体

如果为迁移目的需要查询已存在的 dataProcess 实体：


**Python SDK：查询 dataProcess 实体**

```python
# Inlined from /metadata-ingestion/examples/library/dataprocess_query_deprecated.py
"""
Example: Query an existing (deprecated) dataProcess entity for migration purposes.

This example shows how to read a deprecated dataProcess entity from DataHub
to understand its structure before migrating it to dataFlow and dataJob entities.

Note: This is only for reading existing data. Do NOT create new dataProcess entities.
Use dataFlow and dataJob instead for all new implementations.
"""

from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import (
    DataProcessInfoClass,
    OwnershipClass,
    StatusClass,
)
from datahub.metadata.urns import DataProcessUrn

graph = get_default_graph()

dataprocess_urn = DataProcessUrn(
    name="customer_etl_job", orchestrator="airflow", env="PROD"
)

if not graph.exists(str(dataprocess_urn)):
    raise SystemExit(
        f"dataProcess not found: {dataprocess_urn}\n"
        "DataProcess is deprecated - use dataFlow and dataJob instead."
    )

print(f"Found dataProcess: {dataprocess_urn}")
print("\n=== Entity Aspects ===")

# The identity fields come from the urn itself -- no need to fetch the key aspect.
print("\nIdentity:")
print(f"  Name: {dataprocess_urn.name}")
print(f"  Orchestrator: {dataprocess_urn.orchestrator}")
print(f"  Origin (Fabric): {dataprocess_urn.env}")

info = graph.get_aspect(
    entity_urn=str(dataprocess_urn), aspect_type=DataProcessInfoClass
)
if info is not None:
    print("\nProcess Info:")
    if info.inputs is not None:
        print(f"  Input Datasets: {len(info.inputs)}")
        for inp in info.inputs:
            print(f"    - {inp}")
    if info.outputs is not None:
        print(f"  Output Datasets: {len(info.outputs)}")
        for out in info.outputs:
            print(f"    - {out}")

ownership = graph.get_aspect(
    entity_urn=str(dataprocess_urn), aspect_type=OwnershipClass
)
if ownership is not None:
    print("\nOwnership:")
    for owner in ownership.owners:
        print(f"  - {owner.owner} (type: {owner.type})")

status = graph.get_aspect(entity_urn=str(dataprocess_urn), aspect_type=StatusClass)
if status is not None:
    print(f"\nStatus: {status.removed}")

flow_urn = (
    f"urn:li:dataFlow:({dataprocess_urn.orchestrator},"
    f"{dataprocess_urn.name},{dataprocess_urn.env.lower()})"
)
print("\n=== Migration Recommendation ===")
print("Replace this dataProcess with:")
print(f"  DataFlow URN: {flow_urn}")
print(f"  DataJob URN: urn:li:dataJob:({flow_urn},main_task)")
print("\nSee dataprocess_migrate_to_flow_job.py for migration code examples.")

```



### 创建等价的 DataFlow 和 DataJob（推荐）

不要使用 dataProcess，而应创建现代的等价实体：


**Python SDK：创建 DataFlow 和 DataJob 以替换 dataProcess**

```python
# Inlined from /metadata-ingestion/examples/library/dataprocess_migrate_to_flow_job.py
"""
Example: Migrate from deprecated dataProcess to modern dataFlow and dataJob entities.

This example shows how to create the modern dataFlow and dataJob entities
that replace the deprecated dataProcess entity.

The dataProcess entity used a flat structure:
  dataProcess -> inputs/outputs

The new model uses a hierarchical structure:
  dataFlow (pipeline) -> dataJob (task) -> inputs/outputs

This provides better organization and more precise lineage tracking.
"""

from datahub.metadata.urns import DatasetUrn
from datahub.sdk import DataFlow, DataHubClient, DataJob

client = DataHubClient.from_env()

# Old dataProcess would have been:
# urn:li:dataProcess:(customer_etl_job,airflow,PROD)
# with inputs and outputs at the process level

# New approach: Create a DataFlow for the pipeline
dataflow = DataFlow(
    platform="airflow",  # Same as the old 'orchestrator' field
    name="customer_etl_job",  # Same as the old 'name' field
    platform_instance="prod",  # Based on old 'origin' field
    description="ETL pipeline for customer data processing",
)

# Create DataJob(s) within the flow
# For a simple single-task process, create one job
# For complex multi-step processes, create multiple jobs
datajob = DataJob(
    name="customer_etl_task",  # Task name within the flow
    flow=dataflow,  # Link to parent flow
    description="Main ETL task for customer data",
    # Inputs and outputs now live at the job level for precise lineage
    inlets=[
        DatasetUrn(platform="mysql", name="raw_db.customers", env="PROD"),
        DatasetUrn(platform="mysql", name="raw_db.orders", env="PROD"),
    ],
    outlets=[
        DatasetUrn(platform="postgres", name="analytics.customer_summary", env="PROD"),
    ],
)

# Upsert both entities
client.entities.upsert(dataflow)
client.entities.upsert(datajob)

print("Successfully migrated from dataProcess to dataFlow + dataJob!")
print(f"DataFlow URN: {dataflow.urn}")
print(f"DataJob URN: {datajob.urn}")
print("\nKey improvements over dataProcess:")
print("- Clear separation between pipeline (DataFlow) and task (DataJob)")
print("- Support for multi-step pipelines with multiple DataJobs")
print("- More precise lineage at the task level")
print("- Better integration with modern orchestration platforms")

```



### 完整迁移示例


**Python SDK：从 dataProcess 到 dataFlow/dataJob 的完整迁移**

```python
# Inlined from /metadata-ingestion/examples/library/dataprocess_full_migration.py
"""
Example: Complete migration from dataProcess to dataFlow/dataJob with metadata preservation.

This example demonstrates a full migration path that:
1. Reads an existing deprecated dataProcess entity
2. Extracts all its metadata (inputs, outputs, ownership)
3. Creates equivalent dataFlow and dataJob entities
4. Preserves all metadata relationships

Use this as a template for migrating multiple dataProcess entities in bulk.
"""

from typing import List, Union

from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import DataProcessInfoClass, OwnershipClass
from datahub.metadata.urns import DataProcessUrn, DatasetUrn
from datahub.sdk import DataFlow, DataHubClient, DataJob

graph = get_default_graph()
client = DataHubClient(graph=graph)

# Step 1: Define the dataProcess to migrate
old_dataprocess_urn = DataProcessUrn(
    name="sales_pipeline", orchestrator="airflow", env="PROD"
)

print(f"Migrating: {old_dataprocess_urn}")

# Bail out before writing anything if the source entity isn't there. Emitting from
# defaults would create a dataFlow full of placeholder metadata.
if not graph.exists(str(old_dataprocess_urn)):
    raise SystemExit(
        f"dataProcess not found: {old_dataprocess_urn}\n"
        "Nothing to migrate (already migrated, or never created)."
    )

# Step 2: Read the metadata off the existing dataProcess. Identity comes from the
# urn itself; dataProcess has no globalTags aspect, so there are no tags to migrate.
info = graph.get_aspect(
    entity_urn=str(old_dataprocess_urn), aspect_type=DataProcessInfoClass
)
ownership = graph.get_aspect(
    entity_urn=str(old_dataprocess_urn), aspect_type=OwnershipClass
)

input_datasets: List[Union[str, DatasetUrn]] = (
    [DatasetUrn.from_string(urn) for urn in (info.inputs or [])] if info else []
)
output_datasets: List[Union[str, DatasetUrn]] = (
    [DatasetUrn.from_string(urn) for urn in (info.outputs or [])] if info else []
)
owners = ownership.owners if ownership else []

print("\n=== Extracted Metadata ===")
print(f"Name: {old_dataprocess_urn.name}")
print(f"Orchestrator: {old_dataprocess_urn.orchestrator}")
print(f"Environment: {old_dataprocess_urn.env}")
print(f"Inputs: {len(input_datasets)} datasets")
print(f"Outputs: {len(output_datasets)} datasets")
print(f"Owners: {len(owners)}")

# Step 3: Create the new DataFlow, carrying ownership straight over.
dataflow = DataFlow(
    platform=old_dataprocess_urn.orchestrator,
    name=old_dataprocess_urn.name,
    platform_instance=old_dataprocess_urn.env.lower(),
    description=f"Migrated from dataProcess {old_dataprocess_urn.name}",
    owners=owners,
)

# Step 4: Create the DataJob(s)
# For simplicity, creating one job. In practice, you might split into multiple jobs.
datajob = DataJob(
    name=f"{old_dataprocess_urn.name}_main",
    flow=dataflow,
    description=f"Main task for {old_dataprocess_urn.name}",
    inlets=input_datasets,
    outlets=output_datasets,
)

# Step 5: Upsert the entities
client.entities.upsert(dataflow)
client.entities.upsert(datajob)

print("\n=== Created New Entities ===")
print(f"DataFlow: {dataflow.urn}")
print(f"DataJob: {datajob.urn}")
print(f"Migrated {len(owners)} owner(s) to DataFlow")

print("\n=== Migration Complete ===")
print("Next steps:")
print("1. Verify the new entities in DataHub UI")
print("2. Update any downstream systems to reference the new URNs")
print("3. Consider soft-deleting the old dataProcess entity")

```



## 集成点

### 历史用途

dataProcess 实体此前被以下场景使用：

1. **早期摄取连接器**：早期的 Airflow、Azkaban 连接器在迁移到 dataFlow/dataJob 之前
2. **自定义集成**：用户自行构建且尚未更新的集成
3. **遗留元数据**：现有 DataHub 实例中的历史数据

### 现代替代方案

所有现代 DataHub 连接器都使用 dataFlow 和 dataJob：

- **Airflow**：DAG → DataFlow，Task → DataJob
- **dbt**：项目 → DataFlow，模型 → DataJob
- **Prefect**：Flow → DataFlow，Task → DataJob
- **Dagster**：Pipeline → DataFlow，Op/Asset → DataJob
- **Fivetran**：连接器 → DataFlow，同步操作 → DataJob
- **AWS Glue**：Job → DataFlow，Step → DataJob
- **Azure Data Factory**：Pipeline → DataFlow，Activity → DataJob

### DataProcessInstance

请注意，`dataProcessInstance` **并未弃用**。它表示以下两者的某一次具体执行/运行：

- dataJob（推荐）
- 遗留的 dataProcess（为向后兼容）

DataProcessInstance 继续用于跟踪流水线运行历史、状态和运行时信息。

## 值得注意的例外情况

### 移除时间线

- **弃用时间**：2021 年初（随 dataFlow/dataJob 一起引入）
- **状态**：仍保留在实体注册表中以实现向后兼容
- **当前状态**：没有活跃的摄取源会创建 dataProcess 实体
- **移除**：没有具体时间表，为现有数据而维护

### 读取已有数据

出于向后兼容，dataProcess 实体仍可通过所有 DataHub API 读取。你的实例中已有的 dataProcess 实体将继续正常工作并在 UI 中展示。

### 不建议新增写入

虽然技术上可以创建新的 dataProcess 实体，但**强烈不推荐**。所有新的集成都应使用 dataFlow 和 dataJob。

### 升级路径

没有自动迁移工具。拥有大量 dataProcess 数据的组织应：

1. 使用 Python SDK 查询已存在的 dataProcess 实体
2. 创建等价的 dataFlow 和 dataJob 实体
3. 保留 URN 映射以维持血缘连续性
4. 迁移验证完成后，考虑软删除旧的 dataProcess 实体

### GraphQL API

dataProcess 实体在 GraphQL API 中仅以最小程度暴露。现代的 GraphQL 查询和变更操作聚焦于 dataFlow 和 dataJob 实体。

## 附加资源

- [DataFlow 实体文档](04-dataflow.md)
- [DataJob 实体文档](03-datajob.md)
- [血缘文档](https://docs.datahub.com/docs/features/feature-guides/lineage.md)
- [Airflow 集成指南](https://docs.datahub.com/docs/lineage/airflow.md)


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](05-dataprocess.md)。。
