---
title: 查询
entity: query
order: 33
source: https://docs.datahub.com/docs/generated/metamodel/entities/query.md
---

# 查询

查询（Query）实体表示已针对一个或多个数据资产（如数据集、表或视图）执行过的 SQL 查询（或其他语言的查询）。查询实体既记录手动创建的查询，也记录通过自动抓取 BigQuery、Snowflake、Redshift 等数据平台的查询日志而发现的查询。

查询是理解数据血缘、使用模式以及数据集之间关系的有力构件。当 DataHub 从数据仓库摄取查询日志时，会自动创建查询实体，记录 SQL 语句、它们引用的数据集、执行统计以及随时间变化的使用模式。

## 标识

查询实体由单条信息标识：

- 唯一标识符（`id`），作为查询实体的键。该标识符通常由规范化后的查询文本哈希生成，从而确保相同查询被去重并视为同一实体。

查询标识符的示例为 `urn:li:query:3b8d7b8c7e4e8b4e3c2e1a5c6d7e8f9a`。该标识符是一个唯一字符串，可以通过多种方式生成：

- 规范化 SQL 查询文本的哈希（系统发现的查询常用此方式）
- 用户提供的标识符（手动创建的查询）
- 平台特有的查询标识符

## 重要能力

### 查询属性

`queryProperties` aspect 包含查询的核心信息：

- **Statement**：实际的查询文本及其语言（SQL 或 UNKNOWN）
- **Source**：查询的发现方式（用户通过 UI 输入的查询为 `MANUAL`，抓取器发现的查询为 `SYSTEM`）
- **Name**：可选的展示名称，用于以人类可读的方式标识查询
- **Description**：可选描述，说明该查询的作用
- **Created/Modified**：追踪谁创建以及谁最后修改了该查询的审计戳与时间戳
- **Origin**：该查询来源的实体（例如 View、存储过程、dbt 模型等）
- **Custom Properties**：用于平台特有元数据的额外键值对

下面的代码片段展示了如何创建一个带属性的查询实体。


**Python SDK：创建带属性的查询**

```python
# Inlined from /metadata-ingestion/examples/library/query_create.py
# metadata-ingestion/examples/library/query_create.py
import os
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    QueryLanguageClass,
    QueryPropertiesClass,
    QuerySourceClass,
    QueryStatementClass,
    QuerySubjectClass,
    QuerySubjectsClass,
)
from datahub.metadata.urns import CorpUserUrn, DatasetUrn, QueryUrn

query_id = "my-unique-query-id"
query_urn = QueryUrn(query_id)

current_timestamp = int(time.time() * 1000)
actor_urn = CorpUserUrn("datahub")

query_properties = QueryPropertiesClass(
    statement=QueryStatementClass(
        value="SELECT customer_id, order_total FROM orders WHERE order_date >= '2024-01-01'",
        language=QueryLanguageClass.SQL,
    ),
    source=QuerySourceClass.MANUAL,
    name="Customer Orders Q1 2024",
    description="Query to retrieve all customer orders from Q1 2024 for reporting",
    created=AuditStampClass(time=current_timestamp, actor=actor_urn.urn()),
    lastModified=AuditStampClass(time=current_timestamp, actor=actor_urn.urn()),
)

dataset_urn = DatasetUrn.from_string(
    "urn:li:dataset:(urn:li:dataPlatform:postgres,public.orders,PROD)"
)
query_subjects = QuerySubjectsClass(
    subjects=[
        QuerySubjectClass(entity=dataset_urn.urn()),
    ]
)

gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
rest_emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

mcpw_properties = MetadataChangeProposalWrapper(
    entityUrn=query_urn.urn(),
    aspect=query_properties,
)
rest_emitter.emit(mcpw_properties)

mcpw_subjects = MetadataChangeProposalWrapper(
    entityUrn=query_urn.urn(),
    aspect=query_subjects,
)
rest_emitter.emit(mcpw_subjects)

print(f"Created query {query_urn}")

```


你也可以更新已有查询的特定属性：


**Python SDK：更新查询属性**

```python
# Inlined from /metadata-ingestion/examples/library/query_update_properties.py
# metadata-ingestion/examples/library/query_update_properties.py
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import (
    AuditStampClass,
    QueryPropertiesClass,
)
from datahub.metadata.urns import CorpUserUrn, QueryUrn

query_urn = QueryUrn("my-unique-query-id")

graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

existing_properties = graph.get_aspect(
    entity_urn=query_urn.urn(),
    aspect_type=QueryPropertiesClass,
)

if not existing_properties:
    raise SystemExit(f"Query {query_urn} does not exist or has no properties")

current_timestamp = int(time.time() * 1000)
actor_urn = CorpUserUrn("datahub")

existing_properties.name = "Updated Query Name"
existing_properties.description = "This query has been updated with new documentation"
existing_properties.lastModified = AuditStampClass(
    time=current_timestamp, actor=actor_urn.urn()
)

event = MetadataChangeProposalWrapper(
    entityUrn=query_urn.urn(),
    aspect=existing_properties,
)

emitter.emit(event)
print(f"Updated properties for query {query_urn}")

```


### 查询主体

`querySubjects` aspect 记录查询所引用的数据资产，即查询从中读取或写入的数据集、表、视图或其他实体。

在单资产查询中（例如 `SELECT * FROM table`），主体将包含单个表引用。在多资产查询中（例如跨多表的 join），主体可能包含多个表引用。


**Python SDK：为查询添加主体**

```python
# Inlined from /metadata-ingestion/examples/library/query_add_subjects.py
# metadata-ingestion/examples/library/query_add_subjects.py

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import QuerySubjectClass, QuerySubjectsClass
from datahub.metadata.urns import DatasetUrn, QueryUrn

query_urn = QueryUrn("my-unique-query-id")

graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

existing_subjects = graph.get_aspect(
    entity_urn=query_urn.urn(),
    aspect_type=QuerySubjectsClass,
)

subjects = existing_subjects.subjects if existing_subjects else []

new_dataset_urn = DatasetUrn.from_string(
    "urn:li:dataset:(urn:li:dataPlatform:postgres,public.customers,PROD)"
)
new_subject = QuerySubjectClass(entity=new_dataset_urn.urn())

if new_subject not in subjects:
    subjects.append(new_subject)

query_subjects_aspect = QuerySubjectsClass(subjects=subjects)

event = MetadataChangeProposalWrapper(
    entityUrn=query_urn.urn(),
    aspect=query_subjects_aspect,
)

emitter.emit(event)
print(f"Added subject to query {query_urn}")

```


### 查询使用统计

`queryUsageStatistics` aspect 是一个时间序列 aspect，随时间跟踪查询的执行统计与使用模式，包括：

- **Query Count**：某个时间桶内该查询被执行的总次数
- **Query Cost**：执行该查询所消耗的计算成本（平台特有）
- **Last Executed At**：最近一次执行的时间戳
- **Unique User Count**：执行该查询的不同用户数
- **User Counts**：按用户细化的执行次数明细

该 aspect 通常由处理数据平台查询日志的摄取连接器自动填充。其时间序列特性便于跟踪查询使用的趋势与模式。

### 平台实例

`dataPlatformInstance` aspect 允许你指定该查询关联到数据平台的哪一个具体实例。当同一平台有多个实例时（例如多个 Snowflake 账号或 BigQuery 项目），这一点非常有用。

## 集成点

### 与数据集的关系

查询通过 `querySubjects` aspect 与数据集实体建立根本性关系。查询中的每个主体都引用一个数据集 URN，形成双向关系，使你可以：

- 从查询导航到它引用的数据集
- 从数据集导航到引用它的所有查询

**授权：** 查询的写操作（创建、更新、删除）要求对 `querySubjects` 中的每个主体数据集拥有 **Edit Dataset Queries**（或 **Edit Entity**）权限。GraphQL 变更通过解析器前置检查强制执行这一点；目前 Query 的写入没有单独的 aspect 校验器。

**读取授权**是派生得出的，而非存储在 Query URN 上：

- 当启用查看授权（`VIEW_AUTHORIZATION_ENABLED`）时，若操作者对**每个**主体数据集都拥有 **View Entity Page** 或 **Edit Dataset Queries**（或 **Edit Entity**）权限，则 Query 元数据可见。
- **没有主体**的 Query 会被隐藏（默认拒绝）。
- Schema 字段主体在检查访问权限之前会解析为其父数据集。
- 如果操作者能通过部分但非全部主体读取，则整个 Query 都会被隐藏。

读取检查在 GraphQL、Rest.li 和搜索中保持一致。参见[元数据策略 — 派生授权规则](https://docs.datahub.com/docs/authorization/policies#derived-authorization-rules)。

该关系对于理解数据集使用情况和基于查询的血缘至关重要。

### 血缘集成

查询在 DataHub 的血缘能力中扮演核心角色：

- **基于查询的血缘**：当 DataHub 处理 SQL 查询时（无论来自查询日志还是手动提供），它会执行 SQL 解析以提取列级血缘信息。该血缘随后附加到数据集上，展示数据如何经由 SQL 转换从源列流向目标列。

- **细粒度血缘**：数据集上的细粒度血缘边可以引用查询，为特定列的派生过程提供 SQL 上下文。查询 URN 存储在细粒度血缘信息的 `query` 字段中。

- **来源追踪**：查询可以带有一个 `origin` 字段，指向其来源实体（例如 View 或存储过程），从而建立起从查询执行回溯到其源定义的可追踪链条。

### 摄取来源

多个 DataHub 摄取连接器会自动发现并创建查询实体：

- **BigQuery**：从审计日志和信息模式中提取查询
- **Snowflake**：处理账户使用视图中的查询历史
- **Redshift**：从 `STL_QUERY`、`SVL_QUERY` 等系统表读取
- **SQL Queries Source**：一个可处理任意 SQL 数据库查询日志的通用连接器
- **Mode**：从 Mode 报表和分析中提取查询
- **Hex**：从 Hex notebook 单元格中发现查询

这些连接器通常：

1. 获取包含 SQL 语句与元数据的查询日志
2. 解析 SQL 以识别被引用的表
3. 创建带有适当属性与主体的查询实体
4. 以时间序列数据形式生成使用统计
5. 基于 SQL 解析产出列级血缘

### GraphQL API

可以通过 DataHub GraphQL API 创建、更新和删除查询：

- **createQuery**：创建带有指定属性与主体的新查询
- **updateQuery**：更新已有查询的名称、描述或语句
- **deleteQuery**：硬删除一个查询实体

这些变更通过 GraphQL 端点提供，供 DataHub UI 用于手动管理查询。

### 使用分析

查询实体为数据集使用分析提供数据。当查询使用统计被摄取时，它们会：

- 增加数据集的使用计数
- 追踪哪些用户在查询哪些数据集
- 提供关于查询模式与频率的洞察
- 帮助基于查询活动识别高价值数据集

## 值得注意的例外

### 查询去重

查询会根据其规范化后的查询文本自动去重。这意味着：

- 空白差异会被忽略
- 注释通常在规范化过程中被移除
- 不同用户或不同时期的相同查询会合并为单个查询实体
- 使用统计会在同一规范化查询的所有执行之上聚合

这种去重对于管理大规模部署中的查询数量至关重要。

### 临时表

在处理涉及临时表的查询时，SQL 解析聚合器会维护会话上下文以：

- 追踪会话内临时表的创建与使用
- 穿透临时表解析到其底层的永久表
- 避免创建引用短生命周期临时表的查询主体

这确保查询血缘反映真实的数据依赖关系，而非中间临时结构。

### 查询大小限制

非常大的查询语句（例如生成了数千行的查询）可能会被截断或拒绝，以维持系统性能。具体限制取决于后端配置与存储层。

### 语言支持

目前查询实体主要支持 SQL 作为查询语言。虽然存在 `UNKNOWN` 语言选项，但 DataHub 的 SQL 解析与血缘提取能力是专门为 SQL 方言设计的。其他查询语言（例如 Cypher、SPARQL 或专有查询语言）可以被存储，但不会从自动血缘提取中获益。

### 手动查询与系统查询

查询有两种来源：

- `MANUAL`：用户通过 DataHub UI 或 API 创建的查询
- `SYSTEM`：由摄取连接器自动发现的查询

这一区分有助于分辨用户精心整理的查询（可能配有文档与命名）与从查询日志中自动发现的可能数量庞大的查询。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](33-query.md)。
