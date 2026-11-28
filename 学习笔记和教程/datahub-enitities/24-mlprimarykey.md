---
title: ML 主键
entity: mlprimarykey
order: 24
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlprimarykey.md
---

# MLPrimaryKey

MLPrimaryKey 表示机器学习特征存储（feature store）中的主键实体。主键用于唯一标识特征表中的记录，是在在线与离线特征服务中将特征与实体关联起来的关键要素。在 Feast、Tecton 或 AWS SageMaker Feature Store 等特征存储中，主键定义了将特征与其所描述实体关联起来的标识列（例如 `user_id`、`product_id`、`transaction_id`）。

## 标识

MLPrimaryKey 由两部分信息标识：

- **特征命名空间（Feature Namespace）**：主键所在的逻辑分组或命名空间，通常对应一张特征表或一个特征组。它提供了组织层级，并可避免不同特征集之间的命名冲突。
- **主键名称（Primary Key Name）**：主键在命名空间内的具体名称，即在特征存储中引用该键时使用的标识符。

MLPrimaryKey 标识符的一个示例是 `urn:li:mlPrimaryKey:(users_feature_table,user_id)`。

URN 结构遵循如下模式：

```
urn:li:mlPrimaryKey:(<feature_namespace>,<primary_key_name>)
```

其中：

- `<feature_namespace>` 是命名空间，通常与特征表名称一致
- `<primary_key_name>` 是主键的唯一名称

例如：

- `urn:li:mlPrimaryKey:(users_feature_table,user_id)` - 用户特征表中的 User ID
- `urn:li:mlPrimaryKey:(product_features,product_id)` - 产品特征表中的 Product ID
- `urn:li:mlPrimaryKey:(transactions,transaction_id)` - 交易特征表中的 Transaction ID

## 重要能力

### 主键属性

关于 MLPrimaryKey 的核心元数据存储在 `mlPrimaryKeyProperties` aspect 中，包括：

- **描述（Description）**：说明该主键代表什么、标识哪些实体，以及在特征服务中应如何使用。
- **数据类型（Data Type）**：主键的数据类型（如 TEXT、NUMERIC、BOOLEAN、BYTE 等）。它对应 MLFeatureDataType 枚举，有助于在特征服务过程中进行校验与类型检查。
- **版本（Version）**：可用于跟踪主键定义随时间演进的版本标记。当主键 schema 发生变化或需要多个版本共存时，这非常有用。
- **来源（Sources）**：该主键所派生的上游数据集实体的 URN 引用。这会在数据仓库表与 ML 特征存储之间建立血缘连接，确立数据溯源关系。
- **自定义属性（Custom Properties）**：用于存放不适合标准字段的平台特定元数据的额外键值对。

下面的代码片段展示了如何创建带有属性的 MLPrimaryKey：

```python
# Inlined from /metadata-ingestion/examples/library/mlprimarykey_create.py
import os

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Create an emitter to DataHub over REST
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

dataset_urn = builder.make_dataset_urn(
    name="fct_users_created", platform="hive", env="PROD"
)
primary_key_urn = builder.make_ml_primary_key_urn(
    feature_table_name="users_feature_table",
    primary_key_name="user_id",
)

#  Create feature
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=primary_key_urn,
    aspect=models.MLPrimaryKeyPropertiesClass(
        description="Represents the id of the user the other features relate to.",
        # attaching a source to a ml primary key creates lineage between the feature
        # and the upstream dataset. This is how lineage between your data warehouse
        # and machine learning ecosystem is established.
        sources=[dataset_urn],
        dataType="TEXT",
    ),
)

# Emit metadata!
emitter.emit_mcp(metadata_change_proposal)
print(f"Created ML primary key: {primary_key_urn}")

```

### 可编辑属性

与其他 DataHub 实体一样，MLPrimaryKey 将摄取而来的元数据与用户编辑的元数据分离。`editableMlPrimaryKeyProperties` aspect 允许用户在不影响自动化摄取的前提下，通过 DataHub UI 增强元数据：

- **描述**：用户提供的描述，可补充或覆盖来自摄取来源的描述。

这种分离确保：

- 用户编辑在多次摄取运行之间得以保留
- 来源系统的元数据在其对应字段上保持权威
- 数据从业者可以渐进式地改进文档

### 数据血缘

MLPrimaryKey 通过 `sources` 字段支持血缘追踪。通过将主键关联到上游数据集，你可以：

- **追踪数据来源**：了解哪些仓库表或数据源提供了键值
- **影响分析**：识别受源数据变更影响的下游 ML 模型与特征表
- **数据质量监控**：将源自源系统的数据质量问题一路追踪到特征存储
- **合规与审计**：记录从原始数据到 ML 特征的完整数据流

所创建的血缘关系类型为 `DerivedFrom`，并被显式标记为血缘关系（`isLineage: true`），确保它们出现在 DataHub 的血缘可视化中。

### 标签与术语表项

MLPrimaryKey 可以通过 `globalTags` 和 `glossaryTerms` aspect 附加标签（Tags）或术语（Terms）。这可以实现：

- **分类**：为主键打上安全分类标签（如 `pii`、`sensitive`）
- **组织**：用项目或领域标签对相关主键进行分组
- **业务上下文**：将主键关联到业务术语表项，从而提供业务上下文

阅读[这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)以了解标签与术语的区别。以了解标签与术语的区别。

### 所有权

所有权通过 `ownership` aspect 与 MLPrimaryKey 关联。所有者可以是负责维护主键定义的数据科学家、ML 工程师或特征存储管理员。所有权有助于：

- **责任归属**：明确主键定义的维护责任
- **访问控制**：与 DataHub 策略集成以进行权限管理
- **联系方式**：快速找到关于某个主键应咨询的人

### 领域与数据产品

MLPrimaryKey 支持 `domains` aspect，从而可将其归入逻辑业务领域或数据产品。这有助于：

- **组织结构**：按团队、部门或业务单元对 ML 资产分组
- **发现**：在特定领域内筛选和搜索主键
- **治理**：应用领域专属的策略与所有权模型

### 结构化属性

MLPrimaryKey 支持 `structuredProperties` aspect，使组织能够用经过校验且可搜索的自定义字段扩展元数据模型。这可以实现：

- **自定义元数据**：在标准属性之外添加组织专属字段
- **校验**：对自定义元数据强制实施数据质量要求
- **高级搜索**：按自定义属性进行筛选和搜索

## 代码示例

### 创建 MLPrimaryKey

```python
# Inlined from /metadata-ingestion/examples/library/mlprimarykey_create.py
import os

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Create an emitter to DataHub over REST
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

dataset_urn = builder.make_dataset_urn(
    name="fct_users_created", platform="hive", env="PROD"
)
primary_key_urn = builder.make_ml_primary_key_urn(
    feature_table_name="users_feature_table",
    primary_key_name="user_id",
)

#  Create feature
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=primary_key_urn,
    aspect=models.MLPrimaryKeyPropertiesClass(
        description="Represents the id of the user the other features relate to.",
        # attaching a source to a ml primary key creates lineage between the feature
        # and the upstream dataset. This is how lineage between your data warehouse
        # and machine learning ecosystem is established.
        sources=[dataset_urn],
        dataType="TEXT",
    ),
)

# Emit metadata!
emitter.emit_mcp(metadata_change_proposal)
print(f"Created ML primary key: {primary_key_urn}")

```

### 读取 MLPrimaryKey 信息

```python
# Inlined from /metadata-ingestion/examples/library/mlprimarykey_read.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import MLPrimaryKeyPropertiesClass
from datahub.metadata.urns import MlPrimaryKeyUrn

graph = get_default_graph()

# Or get this from the UI (share -> copy urn) and use MlPrimaryKeyUrn.from_string(...)
mlprimarykey_urn = MlPrimaryKeyUrn("users_feature_table", "user_id")

mlprimarykey_properties = graph.get_aspect(
    entity_urn=str(mlprimarykey_urn),
    aspect_type=MLPrimaryKeyPropertiesClass,
)

print("MLPrimaryKey name:", mlprimarykey_urn.name)
print("MLPrimaryKey namespace:", mlprimarykey_urn.feature_namespace)
if mlprimarykey_properties is None:
    raise SystemExit(f"MLPrimaryKey not found: {mlprimarykey_urn}")

print("MLPrimaryKey description:", mlprimarykey_properties.description)
print("MLPrimaryKey data type:", mlprimarykey_properties.dataType)
print("MLPrimaryKey sources:", mlprimarykey_properties.sources)

```

### 将 MLPrimaryKey 添加到特征表

MLPrimaryKey 通常与特征表关联，以定义记录应如何被唯一标识。一张特征表可以有一个或多个主键（复合键）。

```python
# Inlined from /metadata-ingestion/examples/library/mlprimarykey_add_to_mlfeature_table.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import MLFeatureTablePropertiesClass

gms_endpoint = "http://localhost:8080"
# Create an emitter to DataHub over REST
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})

feature_table_urn = builder.make_ml_feature_table_urn(
    feature_table_name="users_feature_table", platform="feast"
)
primary_key_urns = [
    builder.make_ml_primary_key_urn(
        feature_table_name="users_feature_table",
        primary_key_name="user_id",
    ),
]

# This code concatenates the new primary keys with the existing primary keys in the feature table.
# If you want to replace all existing primary keys with only the new ones, you can comment out this line.
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))
feature_table_properties = graph.get_aspect(
    entity_urn=feature_table_urn, aspect_type=MLFeatureTablePropertiesClass
)
if feature_table_properties:
    current_primary_keys = feature_table_properties.mlPrimaryKeys
    print("current_primary_keys:", current_primary_keys)
    if current_primary_keys:
        primary_key_urns += current_primary_keys

feature_table_properties = models.MLFeatureTablePropertiesClass(
    mlPrimaryKeys=primary_key_urns
)
# MCP creation
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=feature_table_urn,
    aspect=feature_table_properties,
)

# Emit metadata! This is a blocking call
emitter.emit(metadata_change_proposal)

```

### 通过 Python SDK 查询 MLPrimaryKey

Python SDK 可用于获取 MLPrimaryKey 的元数据与关系。

```python
# Inlined from /metadata-ingestion/examples/library/mlprimarykey_query_rest.py
from datahub.ingestion.graph.client import RelationshipDirection, get_default_graph
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    GlossaryTermsClass,
    MLPrimaryKeyPropertiesClass,
    OwnershipClass,
)
from datahub.metadata.urns import MlPrimaryKeyUrn

graph = get_default_graph()

primary_key_urn = MlPrimaryKeyUrn("users_feature_table", "user_id")

print("MLPrimaryKey Entity:", primary_key_urn)

properties = graph.get_aspect(
    entity_urn=str(primary_key_urn), aspect_type=MLPrimaryKeyPropertiesClass
)
if properties is None:
    raise SystemExit(f"MLPrimaryKey not found: {primary_key_urn}")

print("\nPrimary Key Properties:")
print(f"  Description: {properties.description}")
print(f"  Data Type: {properties.dataType}")
print(f"  Sources: {properties.sources}")

ownership = graph.get_aspect(
    entity_urn=str(primary_key_urn), aspect_type=OwnershipClass
)
if ownership is not None:
    print("\nOwnership:")
    for owner in ownership.owners:
        print(f"  - {owner.owner} ({owner.type})")

tags = graph.get_aspect(entity_urn=str(primary_key_urn), aspect_type=GlobalTagsClass)
if tags is not None:
    print("\nTags:")
    for tag in tags.tags:
        print(f"  - {tag.tag}")

terms = graph.get_aspect(
    entity_urn=str(primary_key_urn), aspect_type=GlossaryTermsClass
)
if terms is not None:
    print("\nGlossary Terms:")
    for term in terms.terms:
        print(f"  - {term.urn}")

# Feature tables that use this primary key.
print("\n\nFeature Tables using this Primary Key:")
for related in graph.get_related_entities(
    entity_urn=str(primary_key_urn),
    relationship_types=["KeyedBy"],
    direction=RelationshipDirection.INCOMING,
):
    print(f"  - {related.urn}")

# Upstream datasets this primary key is derived from.
print("\nUpstream Datasets (Sources):")
for related in graph.get_related_entities(
    entity_urn=str(primary_key_urn),
    relationship_types=["DerivedFrom"],
    direction=RelationshipDirection.OUTGOING,
):
    print(f"  - {related.urn}")

```

## 集成点

### 与 MLFeatureTable 的关系

MLPrimaryKey 最重要的关系是与 MLFeatureTable 的关系。特征表通过其 `mlPrimaryKeyProperties` aspect 引用主键，从而建立 `KeyedBy` 关系。该关系表示：

- 该特征表使用这些主键来唯一标识记录
- 在服务特征时，这些键用于查询与关联（join）
- 表上的多个主键构成复合键

这种双向关系带来：

- **正向导航**：从特征表查看其所有主键
- **反向导航**：从主键查看使用它的所有特征表
- **可复用性**：同一个主键可以在多个特征表之间共享

### 与 Dataset 的关系

MLPrimaryKey 可以通过 `mlPrimaryKeyProperties` 中的 `sources` 字段关联到 Dataset 实体。这会向上游数据仓库表创建 `DerivedFrom` 血缘关系，从而确立：

- **数据溯源**：追踪主键值的来源
- **影响分析**：了解源表的变更如何影响特征存储
- **跨平台血缘**：将数据仓库资产与 ML 平台资产连接起来

### 与 MLFeature 的关系

虽然并非直接关系，但 MLPrimaryKey 与 MLFeature 同属于同一个特征命名空间（通常是一张特征表）。主键用于标识实体，而特征提供该实体的属性。二者共同构成完整的特征表 schema。

### 搜索与发现

MLPrimaryKey 已完整建立搜索索引，具备以下能力：

- **名称搜索**：主键名称已建立索引，支持自动补全并具有较高的相关性加权
- **命名空间搜索**：特征命名空间支持部分匹配搜索
- **描述搜索**：对描述（若存在）进行全文搜索
- **关系搜索**：通过关联的特征表或来源数据集查找主键

### 平台实例支持

MLPrimaryKey 支持 `dataPlatformInstance` aspect，在以下场景下很有用：

- 存在多个特征存储实例（如 dev、staging、prod）
- 同一个逻辑主键存在于不同环境中
- 组织需要按实例分别跟踪元数据

## 重要例外

### 复合主键

当一张特征表需要多列才能唯一标识一条记录时，就使用复合主键。在 DataHub 中：

- 为复合主键中的每一列分别创建独立的 MLPrimaryKey 实体
- 通过 `MLFeatureTableProperties` 中的 `mlPrimaryKeys` 数组将它们全部关联到该特征表
- 数组中的顺序对某些特征存储可能是有意义的（例如用于索引优化）

示例：

```python
# For a feature table keyed by (user_id, date)
primary_keys = [
    "urn:li:mlPrimaryKey:(daily_user_features,user_id)",
    "urn:li:mlPrimaryKey:(daily_user_features,date)"
]
```

### 主键 vs. 实体键 vs. 连接键

不同特征存储使用不同的术语：

- **Feast**：使用 "entity" 来指代 DataHub 中所称的主键
- **Tecton**：使用 "entity keys" 和 "join keys"
- **SageMaker Feature Store**：使用 "record identifier"
- **Databricks Feature Store**：使用 "primary keys"

DataHub 将这些概念统一归到 `mlPrimaryKey` 实体类型之下。从不同平台摄取时，各连接器会将这些平台专属术语映射到 MLPrimaryKey。

### 主键同时作为特征

在某些特征存储中，主键本身也可以作为特征使用（例如将 `user_id` 同时用作键和训练特征）。在 DataHub 中：

- 为标识符角色创建一个 MLPrimaryKey 实体
- 为特征角色创建一个 MLFeature 实体
- 两者都可以引用同一个源数据集列

这种双重表示准确反映了同一份数据在特征存储中所扮演的不同角色。

### 命名空间一致性

MLPrimaryKey URN 中的特征命名空间通常应与其所在特征表的名称一致。不过，DataHub 并未强制该要求，以便在以下场景中保持灵活性：

- 主键在多个特征表之间共享
- 组织使用不同的命名空间划分方式
- 平台专属的命名约定与逻辑分组不同

### 数据类型演进

主键的数据类型应保持稳定，以避免破坏特征服务。但如果确实需要变更类型：

- 考虑创建一个带版本化名称的新 MLPrimaryKey
- 使用 `version` 字段跟踪 schema 演进
- 在迁移期间同时保留新旧主键
- 迁移完成后更新特征表以引用新的主键

### 主键与隐私

主键常常包含或直接映射到个人身份信息（PII）。组织应当：

- 为 MLPrimaryKey 实体应用适当的标签（如 `pii`、`gdpr_sensitive`）
- 记录对键值所做的任何哈希或加密处理
- 使用 DataHub 策略控制谁可以查看主键元数据
- 关联到可能包含更多隐私元数据的上游数据集实体

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](24-mlprimarykey.md)。。
