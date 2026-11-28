---
title: 数据集
entity: dataset
order: 01
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataset.md
---

# 数据集（Dataset）

数据集（dataset）实体是元数据模型中最重要的实体之一。它们代表数据集合，通常在数据库中表现为表或视图（如 BigQuery、Snowflake、Redshift 等），在流处理环境中表现为流（Stream，如 Kafka、Pulsar 等），在数据湖系统中表现为以文件或文件夹形式存在的数据包（如 S3、ADLS 等）。

## 标识（Identity）

数据集由三部分信息唯一标识：

- **所属平台**：承载该数据集的具体数据技术。例如 `hive`、`bigquery`、`redshift` 等。更多细节参见 [dataplatform](56-dataplatform.md)。
- **数据集在特定平台中的名称**：每个平台在系统内部都有唯一的命名方式。名称通常由若干结构化元素拼接而成，并以 `.` 分隔。例如关系型数据集通常命名为 `<db>.<schema>.<table>`，但像 MySQL 这类没有 `schema` 概念的平台除外，因此 MySQL 数据集命名为 `<db>.<table>`。当特定平台可能存在多个实例时（例如有多个不同的 MySQL 数据库实例，各含不同的数据资产），名称还可以包含实例 id，使命名的通用模式变为 `<platform_instance>.<db>.<schema>.<table>`。
- **数据集所属的环境（environment）或 fabric**：这是标识上附带的额外限定符，用于区分位于生产环境与非生产环境（如 Staging、QA 等）中的数据集。支持的完整环境 / fabric 列表见 [FabricType.pdl](https://raw.githubusercontent.com/datahub-project/datahub/master/li-utils/src/main/pegasus/com/linkedin/common/FabricType.pdl)。。

数据集标识符的一个示例是 `urn:li:dataset:(urn:li:dataPlatform:redshift,userdb.public.customer_table,PROD)`。

## 重要能力（Important Capabilities）

### 模式（Schemas）

数据集支持扁平模式和嵌套模式。模式的元数据包含在 `schemaMetadata` aspect 中。模式表示为一个字段数组，每个字段由特定的字段路径（field path）标识。

#### 字段路径详解

属于顶层、或可用基于 `.` 的表示法无歧义表达的字段，可以通过 v1 路径名标识；而属于联合类型（union）的字段则需要使用 `[type=X]` 标记进一步消歧。

以如下描述的简单嵌套模式为例：

```javascript
{
    "type": "record",
    "name": "Customer",
    "fields":[
        {
        "type": "record",
        "name": "address",
        "fields": [
            { "name": "zipcode", "type": string},
            {"name": "street", "type": string}]
        }],
}
```

- v1 字段路径：`address.zipcode`
- v2 字段路径：`[version=2.0].[type=struct].address.[type=string].zipcode"`。更多示例及 v2 fieldPath 的正式规范见[此处](https://docs.datahub.com/docs/docs/advanced/field-path-spec-v2.md)。

理解字段路径很重要，因为字段上的标签、术语、文档都是以它们作为标识来表达的。除字段的类型和名称外，模式还包含附加到单个字段上的描述，以及主键与外键信息。

下面的代码片段展示了如何为一个数据集添加包含 3 个字段的模式（Schema）。

**Python SDK：为一个数据集添加 Schema**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_schema.py
from datahub.sdk import DataHubClient, Dataset

client = DataHubClient.from_env()

dataset = Dataset(
    platform="hive",
    name="realestate_db.sales",
    schema=[
        # tuples of (field name / field path, data type, description)
        (
            "address.zipcode",
            "varchar(50)",
            "This is the zipcode of the address. Specified using extended form and limited to addresses in the United States",
        ),
        ("address.street", "varchar(100)", "Street corresponding to the address"),
        ("last_sold_date", "date", "Date of the last sale date for this property"),
    ],
)

client.entities.upsert(dataset)

```



#### 无键约束数据集的主键

当源端未声明任何键约束时（文件、对象存储、无约束的表），可通过任意写入 API（需 Edit Entity 权限）写入 `editablePrimaryKeys` aspect，其中包含键的字段路径。数据摄取（ingestion）不会写入该 aspect。UI 在存在源端主键时（`schemaMetadata.primaryKeys` 加上带 `isPartOfKey` 的字段）展示源端主键，仅在无源端主键时才展示编辑后的键。

- 字段路径应与 `schemaMetadata.fields[].fieldPath` 匹配。UI 也会用简单形式匹配 v2 路径，因此声明为 `id` 的键会标记字段 `[version=2.0].[type=string].id`。若路径未匹配到任何字段，则不会显示徽标，也不会报错。
- 在合并的同级视图（combined sibling view）中，两个同级实体的编辑后键会被合并，其中任一同级上的源端键优先。

### 标签与术语表术语（Tags and Glossary Terms）

数据集可以附加标签（Tag）或术语（Term）。阅读[这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)以了解标签与术语的区别，从而明白何时该使用哪一个。以了解标签与术语的区别，从而明白何时该使用哪一个。

#### 在数据集顶层添加标签或术语表术语

在顶层，标签通过 `globalTags` aspect 添加，术语通过 `glossaryTerms` aspect 添加。

下面是为数据集添加标签的示例。请注意，这需要先读取数据集当前已设置的标签，再按需新增一个。

**Python SDK：在数据集顶层添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_tag.py
from datahub.sdk import DataHubClient, DatasetUrn, TagUrn

client = DataHubClient.from_env()

dataset = client.entities.get(DatasetUrn(platform="hive", name="realestate_db.sales"))
dataset.add_tag(TagUrn("purchase"))

client.entities.update(dataset)

```



下面是为数据集添加术语的示例。请注意，这需要先读取数据集当前已设置的术语，再按需新增一个。

**Python SDK：在数据集顶层添加术语**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_term.py
from typing import List, Union

from datahub.sdk import DataHubClient, DatasetUrn, GlossaryTermUrn


def add_terms_to_dataset(
    client: DataHubClient,
    dataset_urn: DatasetUrn,
    term_urns: List[Union[GlossaryTermUrn, str]],
) -> None:
    """
    Add glossary terms to a dataset.

    Args:
        client: DataHub client to use
        dataset_urn: URN of the dataset to update
        term_urns: List of term URNs or term names to add
    """
    dataset = client.entities.get(dataset_urn)

    for term in term_urns:
        if isinstance(term, str):
            resolved_term_urn = client.resolve.term(name=term)
            dataset.add_term(resolved_term_urn)
        else:
            dataset.add_term(term)

    client.entities.update(dataset)


def main() -> None:
    """
    Main function to add terms to dataset example.
    """
    client = DataHubClient.from_env()

    dataset_urn = DatasetUrn(platform="hive", name="realestate_db.sales", env="PROD")

    # Add terms using both URN and name resolution
    add_terms_to_dataset(
        client=client,
        dataset_urn=dataset_urn,
        term_urns=[
            GlossaryTermUrn("Classification.HighlyConfidential"),
            "PII",  # Will be resolved by name
        ],
    )


if __name__ == "__main__":
    main()

```



#### 为数据集的列 / 字段添加标签或术语表术语

标签和术语也可以附加到数据集的单个列（字段）上。这些附加操作由摄取连接器 / 转换器通过 `schemaMetadata` aspect 完成，也可由 UI 通过 `editableSchemaMetadata` aspect 完成。
这种分离使得从源系统复制元数据的写入与 UI 中的人工编辑相互隔离。

下面示例展示如何使用底层 Python SDK 为数据集中的字段添加标签。

**Python SDK：为数据集的列（字段）添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_column_tag.py
from datahub.sdk import DataHubClient, DatasetUrn, TagUrn

client = DataHubClient.from_env()

dataset = client.entities.get(
    DatasetUrn(platform="hive", name="fct_users_created", env="PROD")
)

dataset["user_name"].add_tag(TagUrn("deprecated"))

client.entities.update(dataset)

```



类似地，下面的示例展示如何使用底层 Python SDK 为数据集中的字段添加术语。

**Python SDK：为数据集的列（字段）添加术语**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_column_term.py
from datahub.sdk import DataHubClient, DatasetUrn, GlossaryTermUrn

client = DataHubClient.from_env()

dataset = client.entities.get(
    DatasetUrn(platform="hive", name="realestate_db.sales", env="PROD")
)

dataset["address.zipcode"].add_term(GlossaryTermUrn("Classification.Location"))

client.entities.update(dataset)

```



### 归属（Ownership）

归属通过 `ownership` aspect 与数据集关联。所有者可以有若干不同类型，如 `DATAOWNER`、`PRODUCER`、`DEVELOPER`、`CONSUMER` 等。完整的归属类型列表及其含义见 [OwnershipType.pdl](https://raw.githubusercontent.com/datahub-project/datahub/master/metadata-models/src/main/pegasus/com/linkedin/common/OwnershipType.pdl)。归属可以从源系统继承，也可以在 DataHub 中通过 UI 额外添加。源端摄取连接器会在源系统支持时自动设置所有者。。归属可以从源系统继承，也可以在 DataHub 中通过 UI 额外添加。源端摄取连接器会在源系统支持时自动设置所有者。

#### 添加所有者

下面的脚本展示了如何使用底层 Python SDK 为数据集添加所有者。

**Python SDK：为数据集添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_owner.py
from datahub.sdk import CorpUserUrn, DataHubClient, DatasetUrn

client = DataHubClient.from_env()

dataset = client.entities.get(DatasetUrn(platform="hive", name="realestate_db.sales"))

# Add owner with the TECHNICAL_OWNER type
dataset.add_owner(CorpUserUrn("jdoe"))

client.entities.update(dataset)

```



### 细粒度血缘（Fine-grained lineage）

字段级细粒度血缘有两种方式与数据集关联 —— 要么直接挂在数据集的 `upstreamLineage` aspect 上，要么作为 dataJob 的 `dataJobInputOutput` aspect 的一部分被捕获。

**Python SDK：为数据集添加细粒度血缘**

```python
# Inlined from /metadata-ingestion/examples/library/lineage_dataset_add_with_query_node.py
from datahub.metadata.urns import DatasetUrn
from datahub.sdk.main_client import DataHubClient

client = DataHubClient.from_env()

upstream_urn = DatasetUrn(platform="snowflake", name="upstream_table")
downstream_urn = DatasetUrn(platform="snowflake", name="downstream_table")

transformation_text = """
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HighValueFilter").getOrCreate()
df = spark.read.table("customers")
high_value = df.filter("lifetime_value > 10000")
high_value.write.saveAsTable("high_value_customers")
"""

client.lineage.add_lineage(
    upstream=upstream_urn,
    downstream=downstream_urn,
    transformation_text=transformation_text,
    column_lineage={"id": ["id", "customer_id"]},
)

# by passing the transformation_text, the query node will be created with the table level lineage.
# transformation_text can be any transformation logic e.g. a spark job, an airflow DAG, python script, etc.
# if you have a SQL query, we recommend using add_dataset_lineage_from_sql instead.
# note that transformation_text itself will not create a column level lineage.

```




**Python SDK：为 datajob 添加细粒度血缘**

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



#### 查询血缘信息

标准的[获取实体的 GET API](https://docs.datahub.com/docs/metadata-service/#retrieving-entities)可用于读取上面示例创建的数据集 / datajob。可用于读取上面示例创建的数据集 / datajob。
响应中同样会包含细粒度血缘信息。

**获取实体快照，包含细粒度血缘**

```
curl 'http://localhost:8080/entities/urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Apostgres,bar,PROD)'
```

```
curl 'http://localhost:8080/entities/urn%3Ali%3AdataJob%3A(urn%3Ali%3AdataFlow%3A(spark,Flow1,prod),Task1)'
```

以下查询可用于查找某个数据集 / datajob 的上游 / 下游数据集与字段。

**查找数据集的上游数据集与字段**

```
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Apostgres,bar,PROD)&types=DownstreamOf'

{
    "start": 0,
    "count": 9,
    "relationships": [
        {
            "type": "DownstreamOf",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar4,PROD)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD),c1)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c3)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c2)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD),c2)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar4,PROD),c1)"
        },
        {
            "type": "DownstreamOf",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c1)"
        }
    ],
    "total": 9
}
```

**查找 datajob 消费的数据集与字段，即 datajob 的输入**

```
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3AdataJob%3A(urn%3Ali%3AdataFlow%3A(spark,Flow1,prod),Task1)&types=Consumes'

{
    "start": 0,
    "count": 9,
    "relationships": [
        {
            "type": "Consumes",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar4,PROD)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar4,PROD),c1)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD),c2)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar3,PROD),c1)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c3)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c2)"
        },
        {
            "type": "Consumes",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c1)"
        }
    ],
    "total": 9
}
```

**查找 datajob 产出的数据集与字段，即 datajob 的输出**

```
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3AdataJob%3A(urn%3Ali%3AdataFlow%3A(spark,Flow1,prod),Task1)&types=Produces'

{
    "start": 0,
    "count": 11,
    "relationships": [
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD),c9)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c9)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c7)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c6)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c5)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c4)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c3)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c2)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD),c1)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar2,PROD)"
        },
        {
            "type": "Produces",
            "entity": "urn:li:dataset:(urn:li:dataPlatform:postgres,bar,PROD)"
        }
    ],
    "total": 11
}
```

### 文档、链接等

数据集的文档可通过 `datasetProperties` aspect 获得（通常由摄取连接器在源系统中已有信息时填充），也可通过 `editableDatasetProperties` aspect 获得（通常由 UI 填充）。

包含更多数据集知识的链接（例如指向 Confluence 页面的链接）可通过 `institutionalMemory` aspect 添加。

下面是一个简单脚本，展示了如何使用底层 Python SDK 为数据集添加文档及若干页面链接。

**Python SDK：为数据集添加文档与链接**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_documentation.py
from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient.from_env()

dataset = client.entities.get(DatasetUrn(platform="hive", name="realestate_db.sales"))

# Add dataset documentation
documentation = """## The Real Estate Sales Dataset
This is a really important Dataset that contains all the relevant information about sales that have happened organized by address.
"""
dataset.set_description(documentation)

# Add link to institutional memory
dataset.add_link(
    (
        "https://wikipedia.com/real_estate",
        "This is the definition of what real estate means",  # link description
    )
)

client.entities.update(dataset)

```



## 值得注意的例外（Notable Exceptions）

以下对 Dataset 实体的超载用法为图方便而存在，但未来很可能迁移为完全建模的实体类型。

- **OpenAPI 端点**：OpenAPI 端点的 GET API 目前被建模为 Dataset，但在元数据模型中创建 Service/API 实体后，它们应真正被建模为该类实体。
- **DataHub 的逻辑实体（Logical Entities）**（如 Dataset、Chart、Dashboard）：目前被表示为 Dataset，并带有 Entity 子类型。在元数据模型中创建逻辑 ER 模型后，它们应真正被建模为其中的实体。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](01-dataset.md)。。
