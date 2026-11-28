---
title: ML 特征表
entity: mlfeaturetable
order: 22
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlfeaturetable.md
---

# ML 特征表

ML 特征表实体表示在特征库（feature store）中组织在一起的一组相关机器学习特征。特征表是 ML 特征管理体系中的基础构件，把具有共同特征（例如相同的主键、更新频率或数据源）的特征归为一组。它们在数据仓库中的原始数据与 ML 模型在训练和推理期间所消费的特征之间架起了桥梁。

## 标识

ML 特征表由两部分信息唯一确定：

- 承载该特征表的平台：即具体的特征库或 ML 平台技术。示例包括 `feast`、`tecton`、`sagemaker` 等。更多细节参见 [dataplatform](56-dataplatform.md)。
- 特征表的名称：在该特定平台内唯一标识这组特征的唯一标识符。

ML 特征表标识符的一个示例是 `urn:li:mlFeatureTable:(urn:li:dataPlatform:feast,users_feature_table)`。

标识由 `mlFeatureTableKey` aspect 定义，其中包含：

- `platform`：指向承载该特征表的数据平台的 URN 引用
- `name`：该特征表在该平台内的唯一名称

## 重要能力

### 特征表属性

ML 特征表通过 `mlFeatureTableProperties` aspect 支持全面的元数据。该 aspect 记录特征表的基本特征：

#### 描述与文档

特征表可以带有详细描述，说明其用途、包含的特征类型以及何时应当使用。这类文档帮助数据科学家和 ML 工程师发现并理解所在组织中的特征表。


**Python SDK：创建带属性的 ML 特征表**

```python
# Inlined from /metadata-ingestion/examples/library/mlfeature_table_create_with_properties.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})

feature_table_urn = builder.make_ml_feature_table_urn(
    feature_table_name="customer_features", platform="feast"
)

feature_table_properties = models.MLFeatureTablePropertiesClass(
    description="Customer demographic and behavioral features for churn prediction models. "
    "Updated daily from the customer data warehouse.",
    customProperties={
        "update_frequency": "daily",
        "feature_count": "25",
        "team": "customer-analytics",
        "sla_hours": "24",
    },
)

metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=feature_table_urn,
    aspect=feature_table_properties,
)

emitter.emit(metadata_change_proposal)

```



#### 特征

特征表最重要的属性是它所包含的特征集合。特征表通过 `mlFeatures` 属性与其中的各个特征保持显式关系。这在特征表与每个具体特征之间建立了 “Contains” 关系，从而支持：

- 发现表中所有特征
- 从特征表导航到单个特征
- 理解特征的组织与分组方式


**Python SDK：向特征表添加特征**

```python
# Inlined from /metadata-ingestion/examples/library/mlfeature_table_add_features.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})

feature_table_urn = builder.make_ml_feature_table_urn(
    feature_table_name="customer_features", platform="feast"
)

new_feature_urns = [
    builder.make_ml_feature_urn(
        feature_name="customer_lifetime_value",
        feature_table_name="customer_features",
    ),
    builder.make_ml_feature_urn(
        feature_name="days_since_last_purchase",
        feature_table_name="customer_features",
    ),
    builder.make_ml_feature_urn(
        feature_name="total_purchase_count",
        feature_table_name="customer_features",
    ),
]

# Read existing features to avoid overwriting them
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))
feature_table_properties = graph.get_aspect(
    entity_urn=feature_table_urn,
    aspect_type=models.MLFeatureTablePropertiesClass,
)

if feature_table_properties and feature_table_properties.mlFeatures:
    existing_features = feature_table_properties.mlFeatures
    all_feature_urns = list(set(existing_features + new_feature_urns))
else:
    all_feature_urns = new_feature_urns

updated_properties = models.MLFeatureTablePropertiesClass(
    mlFeatures=all_feature_urns,
    description="Customer features with newly added purchase metrics",
)

metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=feature_table_urn,
    aspect=updated_properties,
)

emitter.emit(metadata_change_proposal)

```



#### 主键

特征表定义一个或多个主键，用于唯一标识表中的每一行。这些主键至关重要，用于：

- 将特征与训练数据集关联（join）
- 在模型推理期间查找特征值
- 理解特征的实体粒度（例如用户级、交易级）

当指定多个主键时，它们将作为复合键生效。`mlPrimaryKeys` 属性会与每个主键实体建立 “KeyedBy” 关系。


**Python SDK：向特征表添加主键**

```python
# Inlined from /metadata-ingestion/examples/library/mlfeature_table_add_primary_keys.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})

feature_table_urn = builder.make_ml_feature_table_urn(
    feature_table_name="customer_features", platform="feast"
)

primary_key_urns = [
    builder.make_ml_primary_key_urn(
        feature_table_name="customer_features",
        primary_key_name="customer_id",
    )
]

# Read existing properties to preserve other fields
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))
feature_table_properties = graph.get_aspect(
    entity_urn=feature_table_urn,
    aspect_type=models.MLFeatureTablePropertiesClass,
)

if feature_table_properties:
    feature_table_properties.mlPrimaryKeys = primary_key_urns
    updated_properties = feature_table_properties
else:
    updated_properties = models.MLFeatureTablePropertiesClass(
        mlPrimaryKeys=primary_key_urns,
    )

metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=feature_table_urn,
    aspect=updated_properties,
)

emitter.emit(metadata_change_proposal)

# Also create the primary key entity with its properties
dataset_urn = builder.make_dataset_urn(
    name="customers", platform="snowflake", env="PROD"
)
primary_key_urn = primary_key_urns[0]

primary_key_properties = models.MLPrimaryKeyPropertiesClass(
    description="Unique identifier for customers in the system",
    dataType="TEXT",
    sources=[dataset_urn],
)

pk_metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=primary_key_urn,
    aspect=primary_key_properties,
)

emitter.emit(pk_metadata_change_proposal)

```



#### 自定义属性

特征表通过 `customProperties` 字段支持自定义属性，让你记录不适合标准 schema 的平台专属或组织专属元数据。可能包括：

- 更新频率或新鲜度 SLA
- 特征库配置项
- 成本或资源使用情况
- 团队或项目归属信息

### 主键属性

虽然主键是从特征表中被引用的，但它们是独立实体，拥有由 `mlPrimaryKeyProperties` aspect 定义的自身属性。理解主键元数据对于正确使用特征表至关重要：

#### 数据类型

主键具有数据类型（使用 `MLFeatureDataType` 定义），用于指定取值的类型：

- `ORDINAL`：整数值
- `NOMINAL`：类别值
- `BINARY`：布尔值
- `COUNT`：计数值
- `TIME`：时间戳值
- `TEXT`：字符串值
- 其他数值类型，如 `CONTINUOUS`、`INTERVAL`

#### 来源血缘

主键可以通过 `sources` 属性声明其来源数据集。这会建立血缘关系，展示主键取值派生自哪些上游数据集。这对于理解数据来源与影响分析至关重要。

#### 版本管理

主键通过 `version` 属性支持版本管理，使团队能够跟踪键定义随时间的变化，并并行维护多个版本。

### 标签与术语表术语

与其他 DataHub 实体一样，ML 特征表支持标签和术语表术语，用于分类和发现：

- 标签（通过 `globalTags` aspect）提供轻量级的分类
- 术语表术语（通过 `glossaryTerms` aspect）关联到业务定义与概念

阅读 [这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)，了解何时该使用标签、何时该使用术语。

### 归属

归属通过 `ownership` aspect 与特征表关联。所有者可以是负责维护该特征表的个人或团队。清晰的归属至关重要，用于：

- 知道遇到特征问题时该联系谁
- 理解特征质量与更新的责任归属
- 治理与访问控制决策

### 域与组织

特征表可以被归入域（通过 `domains` aspect），以表示组织结构或职能领域。这有助于团队通过把相关特征表归组在一起，来管理大型特征目录。

## 代码示例

### 创建完整的 ML 特征表

下面是一个综合性示例，创建带有全部核心 aspect 的特征表：


**Python SDK：创建完整的 ML 特征表**

```python
# Inlined from /metadata-ingestion/examples/library/mlfeature_table_create_complete.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})

# Step 1: Create the source dataset for lineage
dataset_urn = builder.make_dataset_urn(
    name="customer_transactions", platform="snowflake", env="PROD"
)

# Step 2: Create the primary key entity
primary_key_urn = builder.make_ml_primary_key_urn(
    feature_table_name="transaction_features",
    primary_key_name="transaction_id",
)

primary_key_properties = models.MLPrimaryKeyPropertiesClass(
    description="Unique identifier for each transaction",
    dataType="TEXT",
    sources=[dataset_urn],
)

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=primary_key_urn,
        aspect=primary_key_properties,
    )
)

# Step 3: Create the feature entities
feature_1_urn = builder.make_ml_feature_urn(
    feature_name="transaction_amount",
    feature_table_name="transaction_features",
)

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=feature_1_urn,
        aspect=models.MLFeaturePropertiesClass(
            description="Total amount of the transaction in USD",
            dataType="CONTINUOUS",
            sources=[dataset_urn],
        ),
    )
)

feature_2_urn = builder.make_ml_feature_urn(
    feature_name="is_fraud",
    feature_table_name="transaction_features",
)

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=feature_2_urn,
        aspect=models.MLFeaturePropertiesClass(
            description="Binary indicator of fraudulent transaction",
            dataType="BINARY",
            sources=[dataset_urn],
        ),
    )
)

# Step 4: Create the feature table with all properties
feature_table_urn = builder.make_ml_feature_table_urn(
    feature_table_name="transaction_features", platform="feast"
)

feature_table_properties = models.MLFeatureTablePropertiesClass(
    description="Real-time transaction features for fraud detection models",
    mlFeatures=[feature_1_urn, feature_2_urn],
    mlPrimaryKeys=[primary_key_urn],
    customProperties={
        "update_frequency": "real-time",
        "team": "fraud-detection",
        "critical": "true",
    },
)

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=feature_table_urn,
        aspect=feature_table_properties,
    )
)

# Step 5: Add tags for categorization
emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=feature_table_urn,
        aspect=models.GlobalTagsClass(
            tags=[
                models.TagAssociationClass(tag=builder.make_tag_urn("Fraud Detection")),
                models.TagAssociationClass(
                    tag=builder.make_tag_urn("Real-time Features")
                ),
            ]
        ),
    )
)

# Step 6: Add ownership
emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=feature_table_urn,
        aspect=models.OwnershipClass(
            owners=[
                models.OwnerClass(
                    owner=builder.make_user_urn("data_science_team"),
                    type=models.OwnershipTypeClass.DATAOWNER,
                )
            ]
        ),
    )
)

print(f"Successfully created feature table: {feature_table_urn}")

```



### 查询 ML 特征表

你可以使用 Python SDK 和 REST API 获取 ML 特征表元数据：


**Python SDK：读取 ML 特征表**

```python
# Inlined from /metadata-ingestion/examples/library/mlfeature_table_read.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import MLFeatureTablePropertiesClass
from datahub.metadata.urns import DataPlatformUrn, MlFeatureTableUrn

graph = get_default_graph()

# Or get this from the UI (share -> copy urn) and use MlFeatureTableUrn.from_string(...)
mlfeature_table_urn = MlFeatureTableUrn("feast", "users_feature_table")

mlfeature_table_properties = graph.get_aspect(
    entity_urn=str(mlfeature_table_urn),
    aspect_type=MLFeatureTablePropertiesClass,
)

print("MLFeature Table name:", mlfeature_table_urn.name)
print(
    "MLFeature Table platform:",
    DataPlatformUrn.from_string(mlfeature_table_urn.platform).platform_name,
)
if mlfeature_table_properties is None:
    raise SystemExit(f"MLFeature Table not found: {mlfeature_table_urn}")

print("MLFeature Table description:", mlfeature_table_properties.description)
print("MLFeature Table features:", mlfeature_table_properties.mlFeatures)

```




**REST API：获取 ML 特征表元数据**

```bash
# Get the complete entity with all aspects
curl 'http://localhost:8080/entities/urn%3Ali%3AmlFeatureTable%3A(urn%3Ali%3AdataPlatform%3Afeast,users_feature_table)'

# Get relationships to see features and primary keys
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3AmlFeatureTable%3A(urn%3Ali%3AdataPlatform%3Afeast,users_feature_table)&types=Contains,KeyedBy'
```



## 集成点

ML 特征表在 DataHub 元数据模型中与多个其他实体集成：

### 与 ML 特征的关系

特征表通过 “Contains” 关系包含 ML 特征。`mlFeatures` 数组中的每个特征代表一个具体特征，它可以是：

- 被 ML 模型独立使用
- 拥有自己的元数据、血缘和文档
- 在某些特征库实现中被多个特征表共享

导航是双向的——既可以从特征表导航到特征，也可以从特征返回其父表。

### 与 ML 主键的关系

特征表通过 “KeyedBy” 关系引用 ML 主键。主键：

- 定义特征表的实体粒度
- 支持在训练数据集中将特征与实体标识符关联
- 在表示同一实体类型时，可被多个特征表共享
- 通过 `sources` 属性拥有指向上游数据集的自身血缘

### 与 ML 模型的关系

虽然特征表元数据中不直接引用模型，但 ML 模型通过 `MLModelProperties` 中的 `mlFeatures` 属性消费特征。这建立了 “Consumes” 血缘关系，展示哪些模型使用了某个特征表中的特征。该血缘可用于：

- 理解特征表变更带来的下游影响
- 发现哪些模型依赖特定特征表
- 追踪特征在各模型中的使用与采用情况

### 与数据集的关系

特征表通过两条路径与数据集间接关联：

1. **通过 ML 特征**：各个特征可以通过其 `sources` 属性声明来源数据集，形成 “DerivedFrom” 血缘
2. **通过 ML 主键**：主键可以声明来源数据集，展示实体标识符的来源

这种血缘把特征库与上游数据仓库连接起来，实现从原始数据到模型预测的端到端数据血缘。

### 平台集成

特征表通过 key aspect 中的 `platform` 属性与特定数据平台（例如 Feast、Tecton）关联。这会建立 “SourcePlatform” 关系，用于：

- 标识承载该特征表的特征库系统
- 支持按平台进行过滤和整理
- 支持多平台特征库环境

### 事件（Incidents）

ML 特征表参与共享的 incidents 子系统。可以通过 `raiseIncident` GraphQL mutation（或 Python SDK）在特征表上发起事件，通过 `MLFeatureTable` GraphQL 类型的 `incidents` 字段列回事件列表，并且特征表会携带一个自动维护的汇总 `incidentsSummary` aspect，随事件的发起与解决而更新。

## 值得注意的例外

### 特征库平台差异

不同特征库平台的能力和概念各不相同：

- **Feast**：直接使用 “feature table” 这一术语。Feast 中的特征表与该实体一一对应。
- **Tecton**：使用 “feature views” 和 “feature services” 作为类似概念，可将其建模为特征表。
- **SageMaker Feature Store**：使用 “feature groups”，对应特征表。
- **Databricks Feature Store**：使用 “feature tables”，但采用 database.schema.table 命名模式。

从这些平台采集时，请确保命名约定与平台的术语保持一致。

### 自定义属性使用

与同时拥有 `datasetProperties` 和 `editableDatasetProperties` 的数据集不同，特征表只有：

- `mlFeatureTableProperties`：主属性 aspect（通常来自采集）
- `editableMlFeatureTableProperties`：仅可在 UI 中编辑的描述

对于自定义元数据，请使用 `mlFeatureTableProperties` 中的 `customProperties` 映射，而不是创建自定义 aspect。

### 实体引用与实体创建

使用 SDK 创建特征表时：

- 你**必须先创建被引用的实体**：先创建各个 ML 特征和 ML 主键，再在特征表中引用它们
- 特征表只存储 URN 引用——它不会创建特征或主键实体
- 如果引用了不存在的实体，它们会在 UI 中显示为失效引用

这与其他一些 DataHub 实体不同——在那些实体中子实体可以内联创建。

### 血缘注意事项

特征表血缘通常通过其所包含的特征和主键建立：

- 特征表自身没有直接的 `upstreamLineage` aspect
- 血缘是通过所含特征的 `sources` 属性流动的
- 查询血缘时，你需要穿过 “Contains” 关系才能找到上游数据集

这一设计反映出：在 ML 系统中特征才是血缘的原子单位，而特征表只是组织性构件。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](22-mlfeaturetable.md)。
