---
title: 数据任务
entity: datajob
order: 03
source: https://docs.datahub.com/docs/generated/metamodel/entities/datajob.md
---

# 数据任务

数据任务表示数据管道或工作流中一个个独立的数据处理工作单元。它们是更大数据流中负责转换、移动或处理数据的任务、步骤或操作。示例包括 Airflow 任务、dbt 模型、Spark 作业、Databricks notebook，以及编排系统中类似的处理单元。

## 标识

数据任务由两部分信息唯一确定：

- 其所属的数据流（管道/工作流）：表示为一个指向父级 `dataFlow` 实体的 URN。该数据流定义了编排器（例如 `airflow`、`spark`、`dbt`）、流 ID（例如 DAG 名称或管道名称），以及运行所在的集群。
- 该流内唯一的任务标识符：这是一个字符串，用于在其父流中唯一标识该任务（例如任务名、步骤名、模型名）。

数据任务的 URN 结构为：`urn:li:dataJob:(urn:li:dataFlow:(<orchestrator>,<flow_id>,<cluster>),<job_id>)`

### 示例

**Airflow 任务：**

```
urn:li:dataJob:(urn:li:dataFlow:(airflow,daily_etl_dag,prod),transform_customer_data)
```

**dbt 模型：**

```
urn:li:dataJob:(urn:li:dataFlow:(dbt,analytics_project,prod),staging.stg_customers)
```

**Spark 作业：**

```
urn:li:dataJob:(urn:li:dataFlow:(spark,data_processing_pipeline,PROD),aggregate_sales_task)
```

**Databricks notebook：**

```
urn:li:dataJob:(urn:li:dataFlow:(databricks,etl_workflow,production),process_events_notebook)
```

## 重要能力

### 任务信息（dataJobInfo）

`dataJobInfo` aspect 记录数据任务的核心属性：

- **名称**：任务的易读名称（支持自动补全搜索）
- **描述**：任务用途的详细说明
- **类型**：任务类型（例如 SQL、Python、Spark 等）
- **流 URN**：指向父级数据流的引用
- **创建/修改时间戳**：任务在源系统中创建或最后修改的时间
- **环境**：任务运行所处的环境（PROD、DEV、QA 等）
- **自定义属性**：特定于源系统的额外键值属性
- **外部引用**：指向外部文档或定义的链接（例如 GitHub 链接）

### 输入/输出血缘（dataJobInputOutput）

`dataJobInputOutput` aspect 定义该任务的数据血缘关系：

- **输入数据集**：任务在处理过程中消费的数据集（通过 `inputDatasetEdges`）
- **输出数据集**：任务产生的数据集（通过 `outputDatasetEdges`）
- **输入数据任务**：该任务所依赖的其他数据任务（通过 `inputDatajobEdges`）
- **输入数据集字段**：从输入数据集消费的具体 schema 字段
- **输出数据集字段**：在输出数据集中产生的具体 schema 字段
- **细粒度血缘**：列级血缘映射，展示哪些上游字段贡献给下游字段

该 aspect 建立了关键关系，使 DataHub 能够在整个数据生态中构建并可视化数据血缘图谱。

### 可编辑属性（editableDataJobProperties）

`editableDataJobProperties` aspect 存储通过 DataHub UI 所做的文档编辑：

- **描述**：用户编辑的文档，用于补充或覆盖采集到的描述
- **变更审计戳**：记录谁在何时做了编辑

这种分离确保 UI 中的人工编辑得到保留，不会被采集管道覆盖。

### 归属

与其他实体一样，数据任务通过 `ownership` aspect 支持归属。所有者可以是用户或群组，具有多种归属类型（DATAOWNER、PRODUCER、DEVELOPER 等）。这有助于确定谁负责维护和排查该任务。

### 标签与术语表术语

数据任务可以打标签并关联术语表术语：

- **标签**（`globalTags` aspect）：用于分类、分级或运维目的（例如 PII、关键、已废弃）
- **术语表术语**（`glossaryTerms` aspect）：将任务与术语表中的业务术语和概念关联起来

### 域与应用

数据任务可以被组织为：

- **域**（`domains` aspect）：用于组织结构的业务域或数据域
- **应用**（`applications` aspect）：关联到特定的应用或系统

### 结构化属性与表单

数据任务支持：

- **结构化属性**：由你的组织定义的自定义类型化属性
- **表单**：用于保持一致性的结构化文档表单

## 代码示例

### 创建数据任务

创建数据任务最简单的方式是使用 Python SDK v2：


**Python SDK：创建基本数据任务**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_create_basic.py
# metadata-ingestion/examples/library/datajob_create_basic.py
from datahub.metadata.urns import DataFlowUrn, DatasetUrn
from datahub.sdk import DataHubClient, DataJob

client = DataHubClient.from_env()

datajob = DataJob(
    name="transform_customer_data",
    flow_urn=DataFlowUrn(
        orchestrator="airflow",
        flow_id="daily_etl_pipeline",
        cluster="prod",
    ),
    description="Transforms raw customer data into analytics-ready format",
    inlets=[
        DatasetUrn(platform="postgres", name="raw.customers", env="PROD"),
        DatasetUrn(platform="postgres", name="raw.addresses", env="PROD"),
    ],
    outlets=[
        DatasetUrn(platform="snowflake", name="analytics.dim_customers", env="PROD"),
    ],
)

client.entities.upsert(datajob)
print(f"Created data job: {datajob.urn}")

```



### 添加标签、术语与归属

可以向数据任务添加常用元数据，以提升可发现性与治理水平：


**Python SDK：为数据任务添加标签、术语与归属**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_add_tags_terms_ownership.py
# metadata-ingestion/examples/library/datajob_add_tags_terms_ownership.py
from datahub.metadata.urns import (
    CorpUserUrn,
    DataFlowUrn,
    DataJobUrn,
    GlossaryTermUrn,
    TagUrn,
)
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

datajob_urn = DataJobUrn(
    job_id="transform_customer_data",
    flow=DataFlowUrn(
        orchestrator="airflow", flow_id="daily_etl_pipeline", cluster="prod"
    ),
)

datajob = client.entities.get(datajob_urn)

datajob.add_tag(TagUrn("Critical"))
datajob.add_tag(TagUrn("ETL"))

datajob.add_term(GlossaryTermUrn("CustomerData"))
datajob.add_term(GlossaryTermUrn("DataTransformation"))

datajob.add_owner(CorpUserUrn("data_engineering_team"))
datajob.add_owner(CorpUserUrn("john.doe"))

client.entities.update(datajob)

print(f"Added tags, terms, and ownership to {datajob_urn}")

```



### 更新任务属性

你可以使用底层 API 更新任务属性（例如描述）：


**Python SDK：更新数据任务描述**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_update_description.py
# metadata-ingestion/examples/library/datajob_update_description.py
from datahub.sdk import DataFlowUrn, DataHubClient, DataJobUrn

client = DataHubClient.from_env()

dataflow_urn = DataFlowUrn(
    orchestrator="airflow", flow_id="daily_etl_pipeline", cluster="prod"
)
datajob_urn = DataJobUrn(flow=dataflow_urn, job_id="transform_customer_data")

datajob = client.entities.get(datajob_urn)
datajob.set_description(
    "This job performs critical customer data transformation. "
    "It joins raw customer records with address information and applies "
    "data quality rules before loading into the analytics warehouse."
)

client.entities.update(datajob)

print(f"Updated description for {datajob_urn}")

```



### 查询数据任务信息

通过 Python SDK 获取数据任务信息：


**Python SDK：查询数据任务**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_query_rest.py
# metadata-ingestion/examples/library/datajob_query_rest.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import (
    DataJobInfoClass,
    DataJobInputOutputClass,
    EditableDataJobPropertiesClass,
    GlobalTagsClass,
    OwnershipClass,
)
from datahub.metadata.urns import DataFlowUrn, DataJobUrn

graph = get_default_graph()

datajob_urn = DataJobUrn(
    flow=DataFlowUrn(
        orchestrator="airflow", flow_id="daily_etl_pipeline", cluster="prod"
    ),
    job_id="transform_customer_data",
)

job_info = graph.get_aspect(entity_urn=str(datajob_urn), aspect_type=DataJobInfoClass)
if job_info is None:
    raise SystemExit(f"DataJob not found: {datajob_urn}")

# Description lives in two places: dataJobInfo is what ingestion writes, and the
# editable overlay is what UI and SDK edits write. Show both rather than reimplement
# the precedence -- DataJob.description already resolves it (see datajob_read.py).
editable = graph.get_aspect(
    entity_urn=str(datajob_urn), aspect_type=EditableDataJobPropertiesClass
)

print(f"Job Name: {job_info.name}")
print(f"Description (dataJobInfo): {job_info.description}")
if editable is not None:
    print(f"Description (editable overlay): {editable.description}")

lineage = graph.get_aspect(
    entity_urn=str(datajob_urn), aspect_type=DataJobInputOutputClass
)
if lineage is not None:
    # Lineage comes back either as plain urn lists or as edges carrying audit stamps,
    # depending on which writer produced it -- the SDK writes the former. Read both.
    # The two forms can coexist on one entity, so dedupe the union rather than
    # concatenating it. dict.fromkeys keeps first-seen order.
    inputs = list(
        dict.fromkeys(
            [*(lineage.inputDatasets or [])]
            + [edge.destinationUrn for edge in (lineage.inputDatasetEdges or [])]
        )
    )
    outputs = list(
        dict.fromkeys(
            [*(lineage.outputDatasets or [])]
            + [edge.destinationUrn for edge in (lineage.outputDatasetEdges or [])]
        )
    )

    print(f"\nInput Datasets: {len(inputs)}")
    for dataset_urn in inputs:
        print(f"  - {dataset_urn}")
    print(f"Output Datasets: {len(outputs)}")
    for dataset_urn in outputs:
        print(f"  - {dataset_urn}")

ownership = graph.get_aspect(entity_urn=str(datajob_urn), aspect_type=OwnershipClass)
if ownership is not None:
    print(f"\nOwners: {len(ownership.owners)}")
    for owner in ownership.owners:
        print(f"  - {owner.owner} ({owner.type})")

tags = graph.get_aspect(entity_urn=str(datajob_urn), aspect_type=GlobalTagsClass)
if tags is not None:
    print("\nTags:")
    for tag in tags.tags:
        print(f"  - {tag.tag}")

```



### 为数据任务添加血缘

数据任务常用于定义血缘关系。参见现有的血缘示例：


**Python SDK：使用 DataJobPatchBuilder 添加血缘**

```python
# Inlined from /metadata-ingestion/examples/library/datajob_add_lineage_patch.py
from datahub.emitter.mce_builder import (
    make_data_job_urn,
    make_dataset_urn,
    make_schema_field_urn,
)
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import (
    FineGrainedLineageClass as FineGrainedLineage,
    FineGrainedLineageDownstreamTypeClass as FineGrainedLineageDownstreamType,
    FineGrainedLineageUpstreamTypeClass as FineGrainedLineageUpstreamType,
)
from datahub.specific.datajob import DataJobPatchBuilder

# Create DataHub Client
datahub_client = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Create DataJob URN
datajob_urn = make_data_job_urn(
    orchestrator="airflow", flow_id="dag_abc", job_id="task_456"
)

# Create DataJob Patch to Add Lineage
patch_builder = DataJobPatchBuilder(datajob_urn)
patch_builder.add_input_dataset(
    make_dataset_urn(platform="kafka", name="SampleKafkaDataset", env="PROD")
)
patch_builder.add_output_dataset(
    make_dataset_urn(platform="hive", name="SampleHiveDataset", env="PROD")
)
patch_builder.add_input_datajob(
    make_data_job_urn(orchestrator="airflow", flow_id="dag_abc", job_id="task_123")
)
patch_builder.add_input_dataset_field(
    make_schema_field_urn(
        parent_urn=make_dataset_urn(
            platform="hive", name="fct_users_deleted", env="PROD"
        ),
        field_path="user_id",
    )
)
patch_builder.add_output_dataset_field(
    make_schema_field_urn(
        parent_urn=make_dataset_urn(
            platform="hive", name="fct_users_created", env="PROD"
        ),
        field_path="user_id",
    )
)

# Update column-level lineage through the Data Job
lineage1 = FineGrainedLineage(
    upstreamType=FineGrainedLineageUpstreamType.FIELD_SET,
    upstreams=[
        make_schema_field_urn(make_dataset_urn("postgres", "raw_data.users"), "user_id")
    ],
    downstreamType=FineGrainedLineageDownstreamType.FIELD,
    downstreams=[
        make_schema_field_urn(
            make_dataset_urn("postgres", "analytics.user_metrics"),
            "user_id",
        )
    ],
    transformOperation="IDENTITY",
    confidenceScore=1.0,
)
patch_builder.add_fine_grained_lineage(lineage1)
patch_builder.remove_fine_grained_lineage(lineage1)
# Replaces all existing fine-grained lineages
patch_builder.set_fine_grained_lineages([lineage1])

patch_mcps = patch_builder.build()

# Emit DataJob Patch
for patch_mcp in patch_mcps:
    datahub_client.emit(patch_mcp)

```




**Python SDK：通过数据任务定义细粒度血缘**

```python
# Inlined from /metadata-ingestion/examples/library/lineage_emitter_datajob_finegrained.py
import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.com.linkedin.pegasus2avro.dataset import (
    FineGrainedLineage,
    FineGrainedLineageDownstreamType,
    FineGrainedLineageUpstreamType,
)
from datahub.metadata.schema_classes import DataJobInputOutputClass


def datasetUrn(tbl):
    return builder.make_dataset_urn("postgres", tbl)


def fldUrn(tbl, fld):
    return builder.make_schema_field_urn(datasetUrn(tbl), fld)


# Lineage of fields output by a job
# bar.c1          <-- unknownFunc(bar2.c1, bar4.c1)
# bar.c2          <-- myfunc(bar3.c2)
# {bar.c3,bar.c4} <-- unknownFunc(bar2.c2, bar2.c3, bar3.c1)
# bar.c5          <-- unknownFunc(bar3)
# {bar.c6,bar.c7} <-- unknownFunc(bar4)
# bar2.c9 has no upstream i.e. its values are somehow created independently within this job.

# Note that the semantic of the "transformOperation" value is contextual.
# In above example, it is regarded as some kind of UDF; but it could also be an expression etc.

fineGrainedLineages = [
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.FIELD_SET,
        upstreams=[fldUrn("bar2", "c1"), fldUrn("bar4", "c1")],
        downstreamType=FineGrainedLineageDownstreamType.FIELD,
        downstreams=[fldUrn("bar", "c1")],
    ),
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.FIELD_SET,
        upstreams=[fldUrn("bar3", "c2")],
        downstreamType=FineGrainedLineageDownstreamType.FIELD,
        downstreams=[fldUrn("bar", "c2")],
        confidenceScore=0.8,
        transformOperation="myfunc",
    ),
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.FIELD_SET,
        upstreams=[fldUrn("bar2", "c2"), fldUrn("bar2", "c3"), fldUrn("bar3", "c1")],
        downstreamType=FineGrainedLineageDownstreamType.FIELD_SET,
        downstreams=[fldUrn("bar", "c3"), fldUrn("bar", "c4")],
        confidenceScore=0.7,
    ),
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.DATASET,
        upstreams=[datasetUrn("bar3")],
        downstreamType=FineGrainedLineageDownstreamType.FIELD,
        downstreams=[fldUrn("bar", "c5")],
    ),
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.DATASET,
        upstreams=[datasetUrn("bar4")],
        downstreamType=FineGrainedLineageDownstreamType.FIELD_SET,
        downstreams=[fldUrn("bar", "c6"), fldUrn("bar", "c7")],
    ),
    FineGrainedLineage(
        upstreamType=FineGrainedLineageUpstreamType.NONE,
        upstreams=[],
        downstreamType=FineGrainedLineageDownstreamType.FIELD,
        downstreams=[fldUrn("bar2", "c9")],
    ),
]

# The lineage of output col bar.c9 is unknown. So there is no lineage for it above.
# Note that bar2 is an input as well as an output dataset, but some fields are inputs while other fields are outputs.

dataJobInputOutput = DataJobInputOutputClass(
    inputDatasets=[datasetUrn("bar2"), datasetUrn("bar3"), datasetUrn("bar4")],
    outputDatasets=[datasetUrn("bar"), datasetUrn("bar2")],
    inputDatajobs=None,
    inputDatasetFields=[
        fldUrn("bar2", "c1"),
        fldUrn("bar2", "c2"),
        fldUrn("bar2", "c3"),
        fldUrn("bar3", "c1"),
        fldUrn("bar3", "c2"),
        fldUrn("bar4", "c1"),
    ],
    outputDatasetFields=[
        fldUrn("bar", "c1"),
        fldUrn("bar", "c2"),
        fldUrn("bar", "c3"),
        fldUrn("bar", "c4"),
        fldUrn("bar", "c5"),
        fldUrn("bar", "c6"),
        fldUrn("bar", "c7"),
        fldUrn("bar", "c9"),
        fldUrn("bar2", "c9"),
    ],
    fineGrainedLineages=fineGrainedLineages,
)

dataJobLineageMcp = MetadataChangeProposalWrapper(
    entityUrn=builder.make_data_job_urn("spark", "Flow1", "Task1"),
    aspect=dataJobInputOutput,
)

# Create an emitter to the GMS REST API.
emitter = DatahubRestEmitter("http://localhost:8080")

# Emit metadata!
emitter.emit_mcp(dataJobLineageMcp)

```



## 集成点

### 与 DataFlow 的关系

每个数据任务恰好归属于一个 `dataFlow` 实体，后者代表父级的管道或工作流。数据流记录：

- 编排器/平台（Airflow、Spark、dbt 等）
- 流/管道/DAG 标识符
- 其执行所在的集群或环境

这种层级关系使 DataHub 能够在工作流中组织任务，并理解其执行上下文。

### 与数据集的关系

数据任务通过定义以下关系来建立血缘：

- 与输入数据集的**消费（Consumes）**关系
- 与输出数据集的**产出（Produces）**关系

这些关系是 DataHub 血缘图谱的基础。当任务处理数据时，它在上游来源与下游输出之间创建连接，从而支持影响分析和数据发现。

### 与 DataProcessInstance 的关系

`dataJob` 表示处理任务的定义，而 `dataProcessInstance` 表示该任务的某次具体执行或运行。流程实例记录：

- 运行时信息（开始时间、结束时间、耗时）
- 状态（成功、失败、运行中）
- 该次运行对应的输入/输出数据集
- 错误信息与日志

这种分离使你既能跟踪任务的静态定义，也能跟踪其动态运行时行为。

### GraphQL 解析器

DataHub GraphQL API 为数据任务提供丰富的查询能力：

- **DataJobType**：用于查询数据任务信息的主类型
- **DataJobRunsResolver**：解析执行历史与运行信息
- **DataFlowDataJobsRelationshipsMapper**：映射流与任务之间的关系
- **UpdateLineageResolver**：处理任务的血缘更新

### 采集来源

数据任务通常采集自：

- **Airflow**：任务与 DAG，并提取血缘
- **dbt**：以模型作为数据任务，并基于 SQL 提取血缘
- **Spark**：作业定义及其数据集依赖
- **Databricks**：notebook 与工作流
- **Dagster**：op 与 asset 作为处理单元
- **Prefect**：任务与流
- **AWS Glue**：ETL 作业
- **Azure Data Factory**：管道活动
- **Looker**：LookML 模型与派生表

这些连接器会自动从源系统提取作业定义、血缘与元数据。

## 值得注意的例外

### DataHub 采集任务

DataHub 自身的采集管道以带有特殊 aspect 的数据任务表示：

- **datahubIngestionRunSummary**：跟踪采集运行的统计信息、已处理实体数、警告与错误
- **datahubIngestionCheckpoint**：维护增量采集的状态

这些 aspect 专用于 DataHub 内部采集框架，不用于通用的数据任务。

### 任务状态弃用

`dataJobInfo` 中的 `status` 字段已被 `dataProcessInstance` 模型取代。不再把任务状态存储在任务定义本身，而是为每次执行创建独立的流程实例实体，并在其中保存各自的状态信息。这使任务定义与运行时执行历史之间的分离更加清晰。

### SubType 使用

`subTypes` aspect 允许你把任务归类为：

- SQL 任务
- Python 任务
- Notebook 任务
- 容器任务
- 自定义任务类型

这有助于在 UI 与 API 查询中对任务进行过滤和整理。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](03-datajob.md)。
