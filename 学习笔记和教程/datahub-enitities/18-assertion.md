---
title: 断言
entity: assertion
order: 18
source: https://docs.datahub.com/docs/generated/metamodel/entities/assertion.md
---

# Assertion

assertion 实体代表一条可应用于一个或多个数据集的数据质量规则。断言是 DataHub 数据质量框架的基础，使组织能够定义、监控并执行对其数据的期望。它们涵盖多种检查类型，包括字段级校验、数据量监控、新鲜度追踪、Schema 校验以及基于自定义 SQL 的规则。

断言可以来自多个来源：既可以在 DataHub 内部原生定义，也可以从外部数据质量工具（如 Great Expectations、dbt tests 或 Snowflake Data Quality）摄取，或由基于 ML 的系统推断得出。每条断言都会随时间追踪其评估历史，保留通过、失败和错误的完整审计轨迹。

## 身份标识

一条 **Assertion** 通过 `assertionId` 唯一标识，它是一个全局唯一标识符，在断言的多次运行之间保持不变。URN 格式为：

```
urn:li:assertion:<assertionId>
```

`assertionId` 通常是生成的 GUID，用于唯一标识断言定义。例如：

```
urn:li:assertion:432475190cc846f2894b5b3aa4d55af2
```

### 生成稳定的断言 ID

生成稳定断言 ID 的逻辑因断言来源而异：

- **原生断言**：在 DataHub Cloud 的 UI 或 API 中创建，由平台生成 UUID
- **外部断言**：每个集成工具按各自的约定生成 ID：
  - **Great Expectations**：由平台、期望类型、期望参数、数据集以及列（如果有）派生出的 GUID。期望套件名称不参与 ID 计算。
  - **dbt 测试**：由平台、manifest 中测试的 `unique_id` 以及平台实例派生出的 GUID，另加 env（仅当设置了 `include_env_in_assertion_guid` 且 env 不为 `PROD` 时）以及上游节点（仅当测试依赖多个上游时）
  - **Snowflake Data Quality**：对于 DataHub 编译的 DMF，为嵌入在 DMF 名称中的 ID（`datahub__<id>`）；对于外部 DMF，为由平台、Snowflake 中 DMF-表绑定的 `REFERENCE_ID` 以及平台实例派生出的 GUID
- **推断断言**：基于 ML 的系统根据推断模型与目标生成 ID

关键要求是：同一条断言定义应始终产生相同的 `assertionId`，使 DataHub 即使在断言被反复重新评估的情况下，也能持续追踪其历史。

## 重要能力

### 断言类型

DataHub 支持多种断言类型，每种都用于校验数据质量的不同方面：

#### 1. 字段断言（FIELD）

字段断言用于校验数据集内的单个列或字段，分为两个子类型：

**字段值断言**：校验列中每个值是否满足特定标准。例如：

- 值必须处于特定范围内
- 值必须匹配某个正则表达式
- 值必须属于一组允许值之一
- 值不能为空

**字段指标断言**：校验关于某列的聚合统计量。例如：

- 空值比例必须小于 5%
- 唯一值计数必须等于行数（唯一性检查）
- 均值必须介于 0 与 100 之间
- 标准差必须小于 10


**Python SDK：创建字段唯一性断言**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_create_field_uniqueness.py
# metadata-ingestion/examples/library/assertion_field_uniqueness.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass,
    AssertionStdOperatorClass,
    AssertionTypeClass,
    FieldAssertionInfoClass,
    FieldAssertionTypeClass,
    FieldMetricAssertionClass,
    FieldMetricTypeClass,
    SchemaFieldSpecClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

dataset_urn = builder.make_dataset_urn(platform="snowflake", name="mydb.myschema.users")

field_assertion_info = FieldAssertionInfoClass(
    type=FieldAssertionTypeClass.FIELD_METRIC,
    entity=dataset_urn,
    fieldMetricAssertion=FieldMetricAssertionClass(
        field=SchemaFieldSpecClass(
            path="user_id",
            type="VARCHAR",
            nativeType="VARCHAR",
        ),
        metric=FieldMetricTypeClass.UNIQUE_COUNT,
        operator=AssertionStdOperatorClass.EQUAL_TO,
        parameters=None,
    ),
)

assertion_info = AssertionInfoClass(
    type=AssertionTypeClass.FIELD,
    fieldAssertion=field_assertion_info,
    description="User ID must be unique across all rows",
)

assertion_urn = builder.make_assertion_urn(
    builder.datahub_guid(
        {"entity": dataset_urn, "field": "user_id", "type": "uniqueness"}
    )
)

assertion_info_mcp = MetadataChangeProposalWrapper(
    entityUrn=assertion_urn,
    aspect=assertion_info,
)

emitter.emit_mcp(assertion_info_mcp)
print(f"Created field uniqueness assertion: {assertion_urn}")

```



#### 2. 数据量断言（VOLUME）

数据量断言用于监控数据集中的数据量，支持若干子类型：

- **ROW_COUNT_TOTAL**：总行数必须符合预期
- **ROW_COUNT_CHANGE**：行数随时间的变化必须符合预期
- **INCREMENTING_SEGMENT_ROW_COUNT_TOTAL**：最新分区/片段的行数
- **INCREMENTING_SEGMENT_ROW_COUNT_CHANGE**：相邻分区之间的变化量

数据量断言对于发现数据管道故障、加载不完整或异常的数据增长至关重要。


**Python SDK：创建行数数据量断言**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_create_volume_rows.py
# metadata-ingestion/examples/library/assertion_volume_rows.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass,
    AssertionStdOperatorClass,
    AssertionStdParameterClass,
    AssertionStdParametersClass,
    AssertionStdParameterTypeClass,
    AssertionTypeClass,
    RowCountTotalClass,
    VolumeAssertionInfoClass,
    VolumeAssertionTypeClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

dataset_urn = builder.make_dataset_urn(
    platform="bigquery", name="project.dataset.orders"
)

volume_assertion_info = VolumeAssertionInfoClass(
    type=VolumeAssertionTypeClass.ROW_COUNT_TOTAL,
    entity=dataset_urn,
    rowCountTotal=RowCountTotalClass(
        operator=AssertionStdOperatorClass.BETWEEN,
        parameters=AssertionStdParametersClass(
            minValue=AssertionStdParameterClass(
                type=AssertionStdParameterTypeClass.NUMBER,
                value="1000",
            ),
            maxValue=AssertionStdParameterClass(
                type=AssertionStdParameterTypeClass.NUMBER,
                value="1000000",
            ),
        ),
    ),
)

assertion_info = AssertionInfoClass(
    type=AssertionTypeClass.VOLUME,
    volumeAssertion=volume_assertion_info,
    description="Orders table must contain between 1,000 and 1,000,000 rows",
)

assertion_urn = builder.make_assertion_urn(
    builder.datahub_guid({"entity": dataset_urn, "type": "row-count-range"})
)

assertion_info_mcp = MetadataChangeProposalWrapper(
    entityUrn=assertion_urn,
    aspect=assertion_info,
)

emitter.emit_mcp(assertion_info_mcp)
print(f"Created volume assertion: {assertion_urn}")

```



#### 3. 新鲜度断言（FRESHNESS）

新鲜度断言确保数据在预期的时间窗口内得到更新。支持两种类型：

- **DATASET_CHANGE**：基于从审计日志中捕获的数据集变更操作（insert、update、delete）
- **DATA_JOB_RUN**：基于数据作业的成功执行

新鲜度断言定义一个调度计划，指明应当何时更新（例如每天上午 9 点、每 4 小时一次）以及可接受的容忍度。


**Python SDK：创建数据集变更新鲜度断言**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_create_freshness.py
# metadata-ingestion/examples/library/assertion_freshness.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass,
    AssertionTypeClass,
    FreshnessAssertionInfoClass,
    FreshnessAssertionScheduleClass,
    FreshnessAssertionScheduleTypeClass,
    FreshnessAssertionTypeClass,
    FreshnessCronScheduleClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

dataset_urn = builder.make_dataset_urn(
    platform="redshift", name="prod.analytics.daily_metrics"
)

freshness_assertion_info = FreshnessAssertionInfoClass(
    type=FreshnessAssertionTypeClass.DATASET_CHANGE,
    entity=dataset_urn,
    schedule=FreshnessAssertionScheduleClass(
        type=FreshnessAssertionScheduleTypeClass.CRON,
        cron=FreshnessCronScheduleClass(
            cron="0 9 * * *",
            timezone="America/Los_Angeles",
            windowStartOffsetMs=None,
        ),
    ),
)

assertion_info = AssertionInfoClass(
    type=AssertionTypeClass.FRESHNESS,
    freshnessAssertion=freshness_assertion_info,
    description="Daily metrics table must be updated every day by 9 AM Pacific Time",
)

assertion_urn = builder.make_assertion_urn(
    builder.datahub_guid({"entity": dataset_urn, "type": "freshness-daily-9am"})
)

assertion_info_mcp = MetadataChangeProposalWrapper(
    entityUrn=assertion_urn,
    aspect=assertion_info,
)

emitter.emit_mcp(assertion_info_mcp)
print(f"Created freshness assertion: {assertion_urn}")

```



#### 4. Schema 断言（DATA_SCHEMA）

Schema 断言校验数据集的结构是否符合预期，验证内容包括：

- 特定列的存在或缺失
- 列的数据类型
- 列的顺序（可选）
- Schema 兼容模式：
  - **EXACT_MATCH**：Schema 必须完全匹配
  - **SUPERSET**：实际 Schema 可以包含额外的列
  - **SUBSET**：实际 Schema 可以包含更少的列

Schema 断言对于发现上游数据源中的破坏性变更很有价值。


**Python SDK：创建 Schema 断言**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_create_schema.py
# metadata-ingestion/examples/library/assertion_schema.py
import os
import time

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass,
    AssertionTypeClass,
    AuditStampClass,
    NumberTypeClass,
    SchemaAssertionCompatibilityClass,
    SchemaAssertionInfoClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    SchemalessClass,
    SchemaMetadataClass,
    StringTypeClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

dataset_urn = builder.make_dataset_urn(platform="kafka", name="prod.user_events")

current_timestamp = int(time.time() * 1000)
audit_stamp = AuditStampClass(
    time=current_timestamp,
    actor="urn:li:corpuser:datahub",
)

expected_schema = SchemaMetadataClass(
    schemaName="user_events",
    platform=builder.make_data_platform_urn("kafka"),
    version=0,
    created=audit_stamp,
    lastModified=audit_stamp,
    fields=[
        SchemaFieldClass(
            fieldPath="user_id",
            type=SchemaFieldDataTypeClass(type=StringTypeClass()),
            nativeDataType="string",
            lastModified=audit_stamp,
        ),
        SchemaFieldClass(
            fieldPath="event_type",
            type=SchemaFieldDataTypeClass(type=StringTypeClass()),
            nativeDataType="string",
            lastModified=audit_stamp,
        ),
        SchemaFieldClass(
            fieldPath="timestamp",
            type=SchemaFieldDataTypeClass(type=NumberTypeClass()),
            nativeDataType="long",
            lastModified=audit_stamp,
        ),
        SchemaFieldClass(
            fieldPath="properties",
            type=SchemaFieldDataTypeClass(type=StringTypeClass()),
            nativeDataType="string",
            lastModified=audit_stamp,
        ),
    ],
    hash="",
    platformSchema=SchemalessClass(),
)

schema_assertion_info = SchemaAssertionInfoClass(
    entity=dataset_urn,
    schema=expected_schema,
    compatibility=SchemaAssertionCompatibilityClass.SUPERSET,
)

assertion_info = AssertionInfoClass(
    type=AssertionTypeClass.DATA_SCHEMA,
    schemaAssertion=schema_assertion_info,
    description="User events stream must have required schema fields (can include additional fields)",
)

assertion_urn = builder.make_assertion_urn(
    builder.datahub_guid({"entity": dataset_urn, "type": "schema-check"})
)

assertion_info_mcp = MetadataChangeProposalWrapper(
    entityUrn=assertion_urn,
    aspect=assertion_info,
)

emitter.emit_mcp(assertion_info_mcp)
print(f"Created schema assertion: {assertion_urn}")

```



#### 5. SQL 断言（SQL）

SQL 断言允许使用任意 SQL 查询实现自定义校验逻辑，分为两种类型：

- **METRIC**：执行 SQL 并断言返回的指标符合预期
- **METRIC_CHANGE**：断言某个 SQL 指标随时间的变化

SQL 断言为不适合其他断言类型的复杂校验场景提供了最大的灵活性，例如跨表引用完整性检查或业务规则校验。


**Python SDK：创建 SQL 指标断言**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_create_sql_metric.py
# metadata-ingestion/examples/library/assertion_sql_metric.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AssertionInfoClass,
    AssertionStdOperatorClass,
    AssertionStdParameterClass,
    AssertionStdParametersClass,
    AssertionStdParameterTypeClass,
    AssertionTypeClass,
    SqlAssertionInfoClass,
    SqlAssertionTypeClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

dataset_urn = builder.make_dataset_urn(platform="postgres", name="public.transactions")

sql_assertion_info = SqlAssertionInfoClass(
    type=SqlAssertionTypeClass.METRIC,
    entity=dataset_urn,
    statement="SELECT SUM(amount) FROM public.transactions WHERE status = 'completed' AND date = CURRENT_DATE",
    operator=AssertionStdOperatorClass.GREATER_THAN_OR_EQUAL_TO,
    parameters=AssertionStdParametersClass(
        value=AssertionStdParameterClass(
            type=AssertionStdParameterTypeClass.NUMBER,
            value="0",
        )
    ),
)

assertion_info = AssertionInfoClass(
    type=AssertionTypeClass.SQL,
    sqlAssertion=sql_assertion_info,
    description="Total completed transaction amount today must be non-negative",
)

assertion_urn = builder.make_assertion_urn(
    builder.datahub_guid(
        {"entity": dataset_urn, "type": "sql-completed-transactions-sum"}
    )
)

assertion_info_mcp = MetadataChangeProposalWrapper(
    entityUrn=assertion_urn,
    aspect=assertion_info,
)

emitter.emit_mcp(assertion_info_mcp)
print(f"Created SQL assertion: {assertion_urn}")

```



#### 6. 自定义断言（CUSTOM）

自定义断言为那些未在 DataHub 中直接建模的断言类型提供扩展点，适用于：

- 集成具有独特断言类型的第三方数据质量工具
- 在完全映射到 DataHub 类型体系之前先行启动集成
- 实现组织特有的校验逻辑

### 断言来源

`assertionInfo` aspect 包含一个 `AssertionSource`，用于标识断言的来源：

- **NATIVE**：直接在 DataHub 中定义（DataHub Cloud 功能）
- **EXTERNAL**：从外部工具摄取（Great Expectations、dbt、Snowflake 等）
- **INFERRED**：由基于 ML 的推断系统生成（DataHub Cloud 功能）

外部断言应当配套一个 `dataPlatformInstance` aspect，用于标识其所来自的具体平台实例。

### 断言运行事件

断言的评估通过 `assertionRunEvent` 时序 aspect 追踪。每次评估都会产生一个新事件，包含：

- **timestampMillis**：评估发生的时间
- **runId**：本次评估运行的平台特定标识符
- **asserteeUrn**：被断言的实体（通常是数据集）
- **assertionUrn**：被评估的断言
- **status**：COMPLETE、RUNNING 或 ERROR
- **result**：SUCCESS、FAILURE 或 ERROR 及其详情
- **batchSpec**：关于所评估数据批次的可选信息
- **runtimeContext**：包含运行时参数的可选键值对

运行事件可用于随时间追踪断言健康状况、识别趋势以及排查失败。

### 断言动作

`assertionActions` aspect 定义了对断言结果的自动化响应：

- **onSuccess**：断言通过时触发的动作
- **onFailure**：断言失败时触发的动作

常见动作包括：

- 发送通知（邮件、Slack、PagerDuty）
- 创建事故（incident）
- 触发下游工作流
- 更新元数据

### 标签与元数据

与其他 DataHub 实体一样，断言支持标准的元数据能力：

- **globalTags**：对断言进行分类与组织
- **glossaryTerms**：将断言关联到业务概念
- **status**：将断言标记为启用或废弃


**Python SDK：为断言添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/assertion_add_tag.py
# metadata-ingestion/examples/library/assertion_add_tags.py
import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    TagAssociationClass,
)

graph = DataHubGraph(DatahubClientConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter("http://localhost:8080")

assertion_urn = "urn:li:assertion:432475190cc846f2894b5b3aa4d55af2"

existing_tags = graph.get_aspect(
    entity_urn=assertion_urn,
    aspect_type=GlobalTagsClass,
)

if existing_tags is None:
    existing_tags = GlobalTagsClass(tags=[])

tag_to_add = builder.make_tag_urn("data-quality")

tag_association = TagAssociationClass(tag=tag_to_add)

if tag_association not in existing_tags.tags:
    existing_tags.tags.append(tag_association)

    tags_mcp = MetadataChangeProposalWrapper(
        entityUrn=assertion_urn,
        aspect=existing_tags,
    )

    emitter.emit_mcp(tags_mcp)
    print(f"Added tag '{tag_to_add}' to assertion {assertion_urn}")
else:
    print(f"Tag '{tag_to_add}' already exists on assertion {assertion_urn}")

```



### 标准操作符与参数

断言使用一组标准操作符进行比较：

**数值型**：`BETWEEN`、`LESS_THAN`、`LESS_THAN_OR_EQUAL_TO`、`GREATER_THAN`、`GREATER_THAN_OR_EQUAL_TO`、`EQUAL_TO`、`NOT_EQUAL_TO`

**字符串型**：`CONTAIN`、`START_WITH`、`END_WITH`、`REGEX_MATCH`、`IN`、`NOT_IN`

**布尔型**：`IS_TRUE`、`IS_FALSE`、`NULL`、`NOT_NULL`

**原生型**：`_NATIVE_`，用于平台特定的操作符

参数通过 `AssertionStdParameters` 提供：

- `value`：大多数操作符使用的单个值
- `minValue`、`maxValue`：`BETWEEN` 的区间端点
- 参数类型：`NUMBER`、`STRING`、`SET`

### 标准聚合

字段断言与数据量断言可以在评估前应用聚合函数：

**统计型**：`MEAN`、`MEDIAN`、`STDDEV`、`MIN`、`MAX`、`SUM`

**计数型**：`ROW_COUNT`、`COLUMN_COUNT`、`UNIQUE_COUNT`、`NULL_COUNT`

**比例型**：`UNIQUE_PROPORTION`、`NULL_PROPORTION`

**恒等型**：`IDENTITY`（不做聚合）、`COLUMNS`（所有列）

## 集成点

### 与数据集的关系

断言通过 `Asserts` 关系与数据集建立紧密联系：

- 字段断言针对特定的数据集列
- 数据量断言监控数据集行数
- 新鲜度断言追踪数据集更新时间
- Schema 断言校验数据集结构
- SQL 断言查询数据集内容

数据集维护反向关系，展示所有校验它们的断言。这使用户能够了解应用于任一数据集的所有质量检查。

### 与 Data Job 的关系

原生的 `FreshnessAssertionInfo` 模型允许以数据作业（管道）作为目标：当 `type=DATA_JOB_RUN` 时，`entity` 字段引用的是 dataJob URN 而非数据集。这仅适用于原生新鲜度模型。外部（`CUSTOM`）断言的目标是数据集（`CustomAssertionInfo.entity`），且 `AssertionRunEvent.asserteeUrn` 只接受数据集 URN。

### 与数据平台的关系

外部断言通过 `dataPlatformInstance` aspect 维持与其来源平台的关系，从而实现：

- 按来源工具筛选断言
- 深链接回来源平台
- 了解断言的外部上下文

### GraphQL API

断言可通过 DataHub 的 GraphQL API 完整访问：

- 查询断言及其运行历史
- 创建和更新原生断言
- 删除断言
- 获取特定数据集的断言

主要的 GraphQL 类型：

- `Assertion`：断言主实体
- `AssertionInfo`：断言定义与类型
- `AssertionRunEvent`：评估结果
- `AssertionSource`：来源元数据

### 与 dbt 的集成

DataHub 的 dbt 集成会将 dbt 测试和新鲜度检查输出为 **`AssertionType.CUSTOM`** 断言，并带有结构化的 `CustomAssertionInfo`（scope、operator、aggregation、parameters、fields、nativeType）。

- Schema / 数据测试 → `customAssertion.type = "dbt"`
- 新鲜度检查 → `customAssertion.type = "dbt Freshness"`
- 测试的严重级别、标签和描述都会保留在断言上

### 与 Great Expectations 的集成

Great Expectations action 会将每个 expectation 输出为一条 **`AssertionType.CUSTOM`** 断言，`customAssertion.type = "greatExpectations"`，并根据 expectation 类型与 kwargs 派生出结构化的展示字段。

每个 expectation suite 在 DataHub 中会成为一组 CUSTOM 断言。

### 与 Snowflake Data Quality 的集成

Snowflake DMF（Data Metric Functions）的结果会作为断言结果摄取。断言的类型取决于 DMF 的定义位置：

- **DataHub 编译的 DMF**（`datahub__` 前缀，通过 `datahub assertions compile` 创建）保留其 YAML 定义中的类型，来源为 `NATIVE`：
  - 行数规则 → 数据量断言
  - 唯一性规则 → 字段指标断言
  - 新鲜度规则 → 新鲜度断言
  - 自定义 SQL 规则 → SQL 断言
- **外部 DMF**（直接在 Snowflake 中创建，通过 `include_externally_managed_dmfs` 摄取）会输出为 `CUSTOM` 断言，来源为 `EXTERNAL`。

详见 [Snowflake DMF 断言](/docs/assertions/snowflake/snowflake_dmfs.md#how-external-dmfs-differ-from-datahub-created-dmfs)。

## 注意事项与例外

### 遗留的 Dataset 断言类型

`DATASET` 断言类型是用于外部托管检查的**已废弃**遗留格式（历史上由 dbt 测试和 Great Expectations 使用）。它使用 `DatasetAssertionInfo`，采用通用结构。

**新的外部集成必须使用 `AssertionType.CUSTOM` 配合 `CustomAssertionInfo`**，后者现已支持相同的结构化展示字段（scope、aggregation、operator、parameters、fields、nativeType）。推荐使用 GraphQL 的 `upsertCustomAssertion` / `reportAssertionResult` API，或 [Custom Assertions](/docs/api/tutorials/custom-assertions.md) 中记录的 Python 辅助方法。

原生类型模型（`FIELD`、`VOLUME`、`FRESHNESS`、`DATA_SCHEMA`、`SQL`）用于由 DataHub 原生评估或调度的断言，不应用于外部自行上报的场景。

### 断言结果与断言指标

断言追踪的是通过/失败状态，而 DataHub 还通过 `AssertionResult` 对象支持更细致的指标：

- `actualAggValue`：观测到的实际值（用于数值型断言）
- `externalUrl`：指向源系统中详细结果的链接
- `nativeResults`：平台特定的结果详情

这使得调试以及理解断言为何失败变得更加容易。

### 断言调度

DataHub 通过 `assertionRunEvent` 时序数据追踪断言何时运行，但本身并不直接调度断言评估。调度由以下机制负责：

- **原生断言**：DataHub Cloud 内置的调度器
- **外部断言**：来源平台的调度器（dbt、Airflow 等）
- **按需执行**：手动或通过 API 触发的评估

无论采用何种调度机制，DataHub 都能基于断言运行事件提供监控与告警。

### 断言与测试结果

DataHub 中有两个相关概念：

- **断言**：定义数据质量规则的一等实体
- **测试结果**：可附加到数据集上的更简单的 aspect

测试结果只是轻量的通过/失败指示符，不具备断言的完整表达力。生产环境的数据质量监控请使用断言，简单的摄取期校验请使用测试结果。



> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](18-assertion.md)。
