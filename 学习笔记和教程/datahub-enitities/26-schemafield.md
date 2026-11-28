---
title: 模式字段
entity: schemafield
order: 26
source: https://docs.datahub.com/docs/generated/metamodel/entities/schemafield.md
---

# 模式字段

schemaField 实体表示数据集模式中的单个列或字段。虽然模式信息通常作为数据集 `schemaMetadata` aspect 的一部分被摄取，但 schemaField 实体作为一等实体存在，以便在字段级别直接挂载标签、术语表术语、文档和结构化属性等元数据。

默认情况下，并不会为每一列都实体化 schemaField 实体。只有当元数据被直接写入其 URN 时才会创建 —— 例如为某列分配业务属性，或通过 SDK 为字段设置标签、术语表术语、文档或结构化属性。列搜索并不依赖于该实体存在：字段路径、描述、标签和术语是从数据集的 `schemaMetadata` aspect 投影到父数据集的搜索文档中并建立索引的。

希望为每一列都拥有 schemaField 实体的运维人员可以选择启用。`MCP_SIDE_EFFECTS_SCHEMA_FIELD_ENABLED` 会在数据集摄取过程中实体化字段的 key / 别名 / 状态，而非阻塞的系统更新步骤 `GenerateSchemaFieldsFromSchemaMetadata`（`SYSTEM_UPDATE_SCHEMA_FIELDS_FROM_SCHEMA_METADATA_ENABLED`）则回填已有数据集。两者默认关闭 —— 启用它们会使实体数量、索引大小和写入扇出随每个数据集的列数成比例增长。

无论采用哪种方式，schemaField 都充当数据集级元数据与列级元数据之间的纽带，从而支持字段级别的细粒度数据治理与血缘追踪。

## 标识

SchemaField 实体由两部分唯一标识：

- **父级 URN**：包含该字段的数据集的 URN
- **字段路径**：在模式中标识该字段的路径（例如 `user_id`，嵌套字段为 `address.zipcode`）

schemaField 的 URN 结构遵循如下模式：

```
urn:li:schemaField:(<parent_dataset_urn>,<encoded_field_path>)
```

### 示例

**简单字段：**

```
urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:postgres,public.users,PROD),user_id)
```

**嵌套字段：**

```
urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:bigquery,project.dataset.table,PROD),address.zipcode)
```

**含特殊字符的字段（URL 编码）：**

```
urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD),first%20name)
```

注意，如果字段路径包含特殊字符，则其组成部分可能经过 URL 编码。v1 字段路径使用 `.` 记法表示嵌套结构，而 v2 字段路径包含类型信息（例如 `[version=2.0].[type=struct].address.[type=string].zipcode`）。

## 重要能力

### 字段信息（schemafieldInfo）

`schemafieldInfo` aspect 包含关于该模式字段的基本标识信息：

- **name**：字段的显示名称
- **schemaFieldAliases**：该字段的替代 URN，用于存储字段路径的变体

该 aspect 主要由 DataHub 内部使用，以支持字段路径变体和搜索功能。

### 文档

`documentation` aspect 存储来自多个来源的字段级文档。与数据集层级的描述模式（使用两个独立 aspect：`datasetProperties` 和 `editableDatasetProperties`）不同，字段级文档使用单一的统一 aspect，可以包含来自不同来源的多条文档条目。

每条文档条目包括：

- 文档文本 / 描述
- 来源系统或归属信息

**Python SDK：为模式字段添加或更新文档**

```python
# Inlined from /metadata-ingestion/examples/library/schemafield_add_documentation.py
import time

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

dataset_urn = builder.make_dataset_urn(
    platform="bigquery", name="project.dataset.transactions", env="PROD"
)

field_urn = builder.make_schema_field_urn(
    parent_urn=dataset_urn, field_path="transaction_amount"
)

current_docs = graph.get_aspect(
    entity_urn=field_urn, aspect_type=models.DocumentationClass
)

documentation_text = (
    "The monetary value of the transaction in USD. "
    "This field is calculated from the base currency amount "
    "using the exchange rate at transaction time."
)

attribution = models.MetadataAttributionClass(
    time=int(time.time() * 1000),
    actor=builder.make_user_urn("data_steward"),
    source=builder.make_data_platform_urn("manual"),
)

new_doc = models.DocumentationAssociationClass(
    documentation=documentation_text,
    attribution=attribution,
)

if current_docs and current_docs.documentations:
    source_exists = False
    for i, doc in enumerate(current_docs.documentations):
        if doc.attribution and doc.attribution.source == attribution.source:
            current_docs.documentations[i] = new_doc
            source_exists = True
            break
    if not source_exists:
        current_docs.documentations.append(new_doc)
else:
    current_docs = models.DocumentationClass(documentations=[new_doc])

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=field_urn,
        aspect=current_docs,
    )
)

```

### 标签

标签可以通过 `globalTags` aspect 直接添加到模式字段。这与数据集层级的标签相互独立，从而支持对单个列进行细粒度分类。

字段上的标签常用于：

- 标记敏感数据（PII、PHI、机密）
- 指示数据质量问题
- 标记已废弃字段
- 按安全级别或合规要求对数据进行分类

**Python SDK：为模式字段添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/schemafield_add_tag.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

dataset_urn = builder.make_dataset_urn(
    platform="postgres", name="public.users", env="PROD"
)

field_urn = builder.make_schema_field_urn(
    parent_urn=dataset_urn, field_path="email_address"
)

current_tags = graph.get_aspect(
    entity_urn=field_urn, aspect_type=models.GlobalTagsClass
)

tag_to_add = builder.make_tag_urn("PII")
tag_association = models.TagAssociationClass(tag=tag_to_add)

if current_tags and current_tags.tags:
    if tag_to_add not in [tag.tag for tag in current_tags.tags]:
        current_tags.tags.append(tag_association)
else:
    current_tags = models.GlobalTagsClass(tags=[tag_association])

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=field_urn,
        aspect=current_tags,
    )
)

```

### 术语表术语

术语表术语可以通过 `glossaryTerms` aspect 挂载到模式字段，从而实现列级的语义标注。这有助于用户理解单个字段的业务含义。

**Python SDK：为模式字段添加术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/schemafield_add_term.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

dataset_urn = builder.make_dataset_urn(
    platform="snowflake", name="analytics.public.orders", env="PROD"
)

field_urn = builder.make_schema_field_urn(
    parent_urn=dataset_urn, field_path="customer_id"
)

current_terms = graph.get_aspect(
    entity_urn=field_urn, aspect_type=models.GlossaryTermsClass
)

term_to_add = builder.make_term_urn("CustomerIdentifier")
term_association = models.GlossaryTermAssociationClass(urn=term_to_add)

if current_terms and current_terms.terms:
    if term_to_add not in [term.urn for term in current_terms.terms]:
        current_terms.terms.append(term_association)
else:
    current_terms = models.GlossaryTermsClass(
        terms=[term_association],
        auditStamp=models.AuditStampClass(time=0, actor="urn:li:corpuser:datahub"),
    )

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=field_urn,
        aspect=current_terms,
    )
)

```

### 业务属性

`businessAttributes` aspect 允许将业务属性定义与模式字段关联。业务属性提供了一种方式，将企业特有的元数据维度（如数据分类、保留策略或业务规则）直接挂载到字段上。

对于需要在字段级别跟踪标准 aspect 未涵盖的自定义治理元数据的组织来说，这尤其有用。

### 结构化属性

模式字段通过 `structuredProperties` aspect 支持结构化属性，使组织可以用自定义的类型化属性扩展元数据模型。这适用于跟踪如下字段级元数据：

- 数据质量分数
- 业务关键度评级
- 自定义分类体系
- 监管合规标记

**Python SDK：为模式字段添加结构化属性**

```python
# Inlined from /metadata-ingestion/examples/library/schemafield_add_structured_properties.py
import time

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

dataset_urn = builder.make_dataset_urn(
    platform="hive", name="logging.events.clickstream", env="PROD"
)

field_urn = builder.make_schema_field_urn(parent_urn=dataset_urn, field_path="user_id")

current_properties = graph.get_aspect(
    entity_urn=field_urn, aspect_type=models.StructuredPropertiesClass
)

property_urn = "urn:li:structuredProperty:io.acryl.dataQuality.score"
property_value = "0.95"

new_assignment = models.StructuredPropertyValueAssignmentClass(
    propertyUrn=property_urn,
    values=[property_value],
    created=models.AuditStampClass(
        time=int(time.time() * 1000), actor=builder.make_user_urn("datahub")
    ),
)

if current_properties and current_properties.properties:
    property_exists = False
    for i, prop in enumerate(current_properties.properties):
        if prop.propertyUrn == property_urn:
            current_properties.properties[i] = new_assignment
            property_exists = True
            break
    if not property_exists:
        current_properties.properties.append(new_assignment)
else:
    current_properties = models.StructuredPropertiesClass(properties=[new_assignment])

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=field_urn,
        aspect=current_properties,
    )
)

```

### 字段别名（schemaFieldAliases）

`schemaFieldAliases` aspect 存储模式字段的替代 URN。这在以下场景中很有用：

- 因模式演进导致字段路径变化
- 使用多种字段路径格式（v1 与 v2）
- 需要维护跨平台的字段引用

### 废弃

字段可以通过 `deprecation` aspect 标记为已废弃，表示不应在新应用或新分析中使用。该废弃 aspect 包含：

- 废弃时间戳
- 说明废弃原因的可选备注
- 执行废弃操作的可选操作者

### 逻辑父级

`logicalParent` aspect 可以将模式字段与逻辑父实体（如容器或业务域）关联，从而支持与物理数据集结构不同的组织层级。

### 表单

表单可以通过 `forms` aspect 挂载到模式字段，从而在字段级别实现结构化数据采集与校验。这适用于记录字段级认证、审批或额外的元数据。

### 状态

`status` aspect 指示模式字段是处于活跃状态还是已被软删除。

### 测试结果

`testResults` aspect 可存储针对特定字段运行的数据质量测试结果，将测试结论直接关联到其所校验的列。

### 事件（Incidents）

模式字段参与共享的事件子系统，该子系统让数据质量问题可以针对其所影响的具体列进行跟踪，而不是整个数据集。事件通过 `raiseIncident` GraphQL 变更（或 Python SDK）在字段上发起，并通过 `SchemaFieldEntity` GraphQL 类型的 `incidents` 字段读回。该字段携带一个汇总的 `incidentsSummary` aspect，会随着事件的发起与解决自动维护。由于单个事件可以引用多个实体，因此一个事件可以在同一生命周期中关联受影响的列、其父数据集以及下游模型。

在字段上读取事件遵循与通过 GraphQL 读取任何其他字段元数据相同的规则，因此取决于[功能开关依赖](#功能开关依赖)中描述的 `schemaFieldEntityFetchEnabled` 功能开关。发起和解决事件不受该开关影响。

### 子类型

`subTypes` aspect 允许在数据类型之外对模式字段进行分类，从而支持自定义分类体系。

## 代码示例

### 通过 REST API 查询模式字段

标准的 GET API 可用于获取模式字段实体及其 aspect：

**获取 schemaField 实体**

```python
# Inlined from /metadata-ingestion/examples/library/schemafield_query_entity.py
import datahub.emitter.mce_builder as builder
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import (
    DocumentationClass,
    StructuredPropertiesClass,
)

graph = get_default_graph()

dataset_urn = builder.make_dataset_urn(
    platform="postgres", name="public.customers", env="PROD"
)

field_urn = builder.make_schema_field_urn(
    parent_urn=dataset_urn, field_path="email_address"
)

# get_entity_semityped() cannot be used to test existence -- it always returns a
# non-empty aspect bag, even for an entity that does not exist. graph.exists() is
# the real probe.
if not graph.exists(field_urn):
    raise SystemExit(f"Schema field not found: {field_urn}")

print(f"Schema Field URN: {field_urn}")

documentation = graph.get_aspect(entity_urn=field_urn, aspect_type=DocumentationClass)
if documentation is not None:
    for doc in documentation.documentations:
        print(f"Documentation: {doc.documentation[:100]}...")

structured_properties = graph.get_aspect(
    entity_urn=field_urn, aspect_type=StructuredPropertiesClass
)
if structured_properties is not None:
    for prop in structured_properties.properties:
        print(f"Property {prop.propertyUrn}: {prop.values}")

```

API 调用示例：

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AschemaField%3A(urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Apostgres%2Cpublic.users%2CPROD)%2Cuser_id)'
```

该调用返回与模式字段关联的所有 aspect，包括标签、术语、文档和结构化属性。

### 处理细粒度血缘

模式字段是细粒度（列级）血缘的核心。在定义数据集之间的血缘时，可以指定哪些字段从上游流向下游：

**展示字段级关系的血缘查询示例**

```bash
# Find upstream fields of a specific schema field
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3AschemaField%3A(urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Apostgres%2Cpublic.orders%2CPROD)%2Cuser_id)&types=DownstreamOf'
```

该查询展示了哪些上游字段对该字段的值作出贡献，从而支持列级的影响分析。

## 集成点

### 与数据集的关系

模式字段与数据集之间是父子关系。数据集的 `schemaMetadata` aspect 定义字段的结构和元数据，而单个 schemaField 实体则允许在字段级别直接挂载元数据。

关键集成点：

- 字段在数据集的 `schemaMetadata` 和 `editableSchemaMetadata` aspect 中被引用
- 字段级标签和术语既可通过数据集 aspect（`schemaMetadata`）设置，也可直接设置在 schemaField 实体上
- UI 通常修改数据集上的 `editableSchemaMetadata`，而摄取连接器设置 `schemaMetadata`

### 细粒度血缘

模式字段对于列级血缘至关重要：

- **DataJob 实体**：`dataJobInputOutput` aspect 可以指定 `inputDatasetFields` 和 `outputDatasetFields`
- **数据集血缘**：数据集上的 `upstreamLineage` aspect 可以包含映射具体字段的 `fineGrainedLineages`
- **血缘查询**：字段级血缘表现为 schemaField 实体之间的关系

### GraphQL API

GraphQL API 以 `SchemaFieldEntity` 类型将模式字段实体作为一等实体暴露。关键解析器包括：

- 获取字段元数据（标签、术语、文档）
- 查询字段血缘关系
- 跨数据集搜索字段

注意：通过 GraphQL 获取字段受 `schemaFieldEntityFetchEnabled` 功能开关控制，该开关默认启用。禁用后，模式字段元数据只能通过父数据集的 schema aspect 访问。

### 搜索与发现

模式字段会针对搜索建立索引，使用户能够：

- 按列名查找数据集
- 搜索带有特定标签或术语的字段
- 通过描述内容发现字段
- 按字段级分类筛选

这些能力由两个不同的索引提供。按列名、描述、标签或术语查找**数据集**，使用的是从 `schemaMetadata` 投影到数据集自身搜索文档中的字段（`fieldPaths`、`fieldDescriptions`、`fieldLabels`、`fieldTags`、`fieldGlossaryTerms`），无论 schemaField 实体是否存在都能工作。而搜索**schemaField 实体本身**则使用独立的 `schemaField` 搜索组，只返回已实体化的字段。

## 值得注意的例外

### 双重访问模式

模式字段元数据可以通过两种方式访问和修改：

1. **通过父数据集**：使用数据集上的 `schemaMetadata` 或 `editableSchemaMetadata` aspect
2. **直接在 schemaField 实体上**：在 schemaField URN 上使用 `globalTags`、`glossaryTerms`、`documentation` 等 aspect

最佳实践：

- 摄取连接器应使用数据集级 aspect（`schemaMetadata`）
- UI 编辑通常使用数据集级 aspect（`editableSchemaMetadata`）
- 直接更新 schemaField 实体适用于程序化批量操作，或在处理字段级血缘时使用

### 业务域与归属（可选的 MCP 镜像）

`schemaField` 支持 `domains` 和 `ownership` aspect。运维人员可以选择通过 MCP 副作用把这些 aspect 从父数据集复制到每个字段上：

- `MCP_SIDE_EFFECTS_SCHEMA_FIELD_ENABLED`（主开关 —— 同时会实体化字段的 key / 别名 / 状态）
- `MCP_SIDE_EFFECTS_SCHEMA_FIELD_DOMAIN_ENABLED`
- `MCP_SIDE_EFFECTS_SCHEMA_FIELD_OWNERSHIP_ENABLED`

在某个子开关开启期间，数据集业务域 / 归属的写入与删除会镜像到对应的字段 aspect。

**历史数据盘点**：修改这些开关后，运行（或等待）非阻塞的系统更新步骤 `GenerateSchemaFieldsFromSchemaMetadata`，并设置 `SYSTEM_UPDATE_SCHEMA_FIELDS_FROM_SCHEMA_METADATA_ENABLED=true`。该步骤的升级 id 由生效的业务域 / 归属开关组合指纹确定，因此某种组合的**首次**启用或禁用都会获得一次全新执行：启用时会从已存储的数据集 aspect 回填；禁用时会删除对应已关闭开关的字段 `domains` / `ownership`。**禁用时的清理不区分来源** —— 它会移除每个被扫描数据集下所有字段的该 aspect，包括直接写在 schemaField 上的 aspect（而不仅是镜像副本）。**循环切换**（回到某个已 SUCCEEDED 的指纹组合）**不会**重新执行 —— 请使用**手动重新处理**（`SYSTEM_UPDATE_SCHEMA_FIELDS_FROM_SCHEMA_METADATA_REPROCESS=true`），或清除 / 修改该指纹对应的 `dataHubUpgrade` URN 上的 `dataHubUpgradeResult`（两者均可）。参见[破坏性变更](https://docs.datahub.com/docs/how/breaking-changes)和[环境变量](https://docs.datahub.com/docs/deploy/environment-vars#schema-fields-configuration)。

### 功能开关依赖

在 GraphQL 中填充 schemaField 实体受 `schemaFieldEntityFetchEnabled` 功能开关（`SCHEMA_FIELD_ENTITY_FETCH_ENABLED`）控制，该开关**默认启用**。禁用后，`SchemaFieldType.batchLoad` 会跳过实体获取，并返回每个字段的空 aspect 映射，因此：

- 存储在 schemaField URN 上的元数据（标签、术语、文档、结构化属性）不会被返回
- 字段级元数据必须从父数据集的 `schemaMetadata` / `editableSchemaMetadata` 读取
- 该字段本身仍可解析，数据集级 schema aspect 不受影响

该开关管控的是**读取**这些实体的成本 —— 每批渲染的字段一次批量获取 —— 而不决定它们是否存在。实体化是另一个独立的问题，默认同样关闭；参见[业务域与归属](#业务域与归属（可选的 MCP 镜像）)。

### 字段路径编码

如果 schemaField URN 中的字段路径包含特殊字符（空格、特殊符号等），则必须进行 URL 编码。请始终使用 `datahub.emitter.mce_builder` 中的 `make_schema_field_urn` 工具函数来正确构造 URN：

```python
from datahub.emitter.mce_builder import make_schema_field_urn

# Automatically handles encoding
field_urn = make_schema_field_urn(
    parent_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)",
    field_path="first name"  # Will be encoded as "first%20name"
)
```

### V1 与 V2 字段路径

DataHub 支持两种字段路径格式：

- **V1**：简单的点号记法（例如 `address.zipcode`）
- **V2**：类型感知的记法（例如 `[version=2.0].[type=struct].address.[type=string].zipcode`）

以下情况需要使用 v2 字段路径：

- 字段名本身有歧义的联合类型
- 带类型信息的复杂嵌套结构
- 需要精确消歧的字段路径

大多数简单模式可以使用 v1 字段路径。在处理复杂类型或当摄取连接器生成 v2 路径时请使用 v2。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](26-schemafield.md)。
