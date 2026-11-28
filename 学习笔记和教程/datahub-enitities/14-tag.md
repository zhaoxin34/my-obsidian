---
title: 标签
entity: tag
order: 14
source: https://docs.datahub.com/docs/generated/metamodel/entities/tag.md
---

# 标签

标签是 DataHub 的核心元数据实体之一，为数据资产的分类、归类与组织提供了灵活机制。它们代表可应用到数据集、仪表板、图表等实体上的标记，使用户能够快速识别、筛选和归组整个数据生态中的相关资产。

## 标识

标签由单条信息标识：

- **标签名称**：唯一的字符串标识符，既作为技术主键，也作为人类可读的引用。名称应当简单、具备描述性，且通常遵循小写命名约定（例如 `pii`、`deprecated`、`quarterly`）。

标签标识符示例：`urn:li:tag:pii`。

URN 结构很直接：

```
urn:li:tag:<tag_name>
```

其中 `<tag_name>` 是标签的唯一标识符。与许多其他 DataHub 实体不同，标签不需要平台限定符或环境规格，因此可普遍应用于所有数据资产。

## 重要能力

### 标签属性

标签支持若干属性，用于增强其在 DataHub 中的可用性与外观：

- **显示名称**：可以不同于技术标识符的友好名称。例如，名称为 `pii` 的标签，其显示名称可以是 "Personally Identifiable Information"。
- **描述**：详细文档，说明该标签代表什么、何时应使用，以及与之相关的组织策略。
- **颜色**：十六进制颜色代码（例如 `#FF0000`），便于在 UI 中做视觉区分，让带标签的资产一眼可辨。

这些属性存储在 `tagProperties` 方面中，可在创建标签时设置，也可后续更新。

### 将标签应用到实体

标签通过 `globalTags` 方面应用到其他实体。几乎所有 DataHub 核心实体都支持打标签，包括：

- **数据集**：表、视图、流及其他数据集合
- **仪表板**：BI 仪表板与报表界面
- **图表**：单个可视化与报告
- **数据任务**：ETL 任务、转换管道
- **数据流**：完整的数据管道与工作流
- **ML 模型**：机器学习模型与部署
- **容器**：数据库、schema 及其他组织结构
- **术语表术语**：业务术语与概念

标签可在多个层级应用：

1. **实体级**：应用于整个资产（例如将整个数据集标记为 `sensitive`）
2. **字段级**：应用于数据集中特定的列或字段（例如仅将 `email` 列标记为 `pii`）

### 标签与术语表术语

虽然标签和术语表术语都提供分类能力，但二者用途不同：

- **标签**是轻量、非正式的标签，用于快速归类。适合数据质量状态（`needs_review`）、
  安全分级（`confidential`）或项目关联（`q4_initiative`）等运营性关注点。
- **术语表术语**是带丰富元数据、关系与治理的正式业务词汇。适合 "Customer"、"Revenue"、
  "Product SKU" 等业务概念。

详细比较请阅读 [这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)。

### 所有权

与其他核心实体一样，标签支持 `ownership` 方面。这允许组织指定谁负责维护标签定义并确保使用的一致性。标签负责人可以是拥有各种所有权类型（例如 `DATAOWNER`、`STEWARD`）的用户或用户组。

### 弃用与状态

标签可以通过 `deprecation` 方面标记为已弃用，表示不应再使用。`status` 方面允许在保留历史引用的同时对标签进行软删除。

## 代码示例

### 创建标签


**Python SDK：创建基础标签**

```python
# Inlined from /metadata-ingestion/examples/library/tag_create_basic.py
# metadata-ingestion/examples/library/tag_create_basic.py
from datahub.sdk import DataHubClient, Tag

client = DataHubClient.from_env()

# Create a basic tag with properties
tag = Tag(
    name="pii",
    display_name="Personally Identifiable Information",
    description="This tag indicates that the asset contains PII data and should be handled according to data privacy regulations.",
    color="#FF0000",
)

# Upsert the tag
client.entities.upsert(tag)

print(f"Created tag: {tag.urn}")

```



### 为标签添加所有权


**Python SDK：为标签添加负责人**

```python
# Inlined from /metadata-ingestion/examples/library/tag_add_ownership.py
# metadata-ingestion/examples/library/tag_add_ownership.py
from datahub.metadata.urns import CorpUserUrn
from datahub.sdk import DataHubClient, Tag

client = DataHubClient.from_env()

# Create a tag with ownership
tag = Tag(
    name="data_quality",
    owners=[
        CorpUserUrn("data_steward"),
    ],
)

# Upsert the tag
client.entities.upsert(tag)

print(f"Created tag with ownership: {tag.urn}")

```



### 将标签应用到数据集


**Python SDK：将标签应用到数据集**

```python
# Inlined from /metadata-ingestion/examples/library/tag_apply_to_dataset.py
# metadata-ingestion/examples/library/tag_apply_to_dataset.py
from datahub.sdk import DataHubClient, Dataset, Tag

client = DataHubClient.from_env()

# Create Dataset entity
dataset = Dataset(platform="snowflake", name="db.schema.customers", env="PROD")

# Create Tag entity
tag = Tag(name="pii")

# Apply tag to dataset
dataset.add_tag(tag.urn)

# Update the dataset with the new tag
client.entities.upsert(dataset)

print(f"Applied tag {tag.urn} to dataset {dataset.urn}")

```



### 查询标签信息

可以使用 Python SDK 获取标签元数据，并查看哪些实体被打上了该标签。


**Python SDK：获取标签实体信息**

```python
# Inlined from /metadata-ingestion/examples/library/tag_query_rest.py
# metadata-ingestion/examples/library/tag_query_rest.py

from datahub.ingestion.graph.client import RelationshipDirection, get_default_graph
from datahub.metadata.schema_classes import OwnershipClass, TagPropertiesClass
from datahub.metadata.urns import TagUrn

graph = get_default_graph()

tag_urn = TagUrn("pii")

properties = graph.get_aspect(entity_urn=str(tag_urn), aspect_type=TagPropertiesClass)
if properties is None:
    raise SystemExit(f"Tag not found: {tag_urn}")

print(f"Tag name: {properties.name}")
print(f"Description: {properties.description}")
print(f"Color: {properties.colorHex}")

ownership = graph.get_aspect(entity_urn=str(tag_urn), aspect_type=OwnershipClass)
if ownership is not None:
    print(f"Number of owners: {len(ownership.owners)}")
    for owner in ownership.owners:
        print(f"  - Owner: {owner.owner}, Type: {owner.type}")

# Find all entities tagged with this tag by walking the TaggedWith relationship.
tagged = list(
    graph.get_related_entities(
        entity_urn=str(tag_urn),
        relationship_types=["TaggedWith"],
        direction=RelationshipDirection.INCOMING,
    )
)
print(f"Found {len(tagged)} entities tagged with this tag")
for related in tagged:
    print(f"  - {related.urn} (type: {related.relationship_type})")

```



### 搜索带标签的资产

标签已完全集成到 DataHub 的搜索能力中，可让你找到所有带特定标签的资产。


**Python SDK：按标签搜索资产**

```python
from datahub.sdk import DataHubClient
from datahub.sdk.search_filters import FilterDsl as F

client = DataHubClient.from_env()

# Find all assets tagged with "pii"
results = client.search.get_urns(filter=F.tag("urn:li:tag:pii"))

print(f"Found {len(results)} assets tagged with 'pii'")
for urn in results:
    print(f"  - {urn}")
```



## 集成点

### 与其他实体的关系

标签在被标记的实体与标签实体之间创建 `TaggedWith` 关系。这一双向关系支持：

- **正向导航**：从一个数据集查看其全部标签
- **反向导航**：从一个标签查看使用它的全部实体
- **影响分析**：在弃用某个标签之前了解其影响范围

### GraphQL API 支持

标签在 DataHub 的 GraphQL API 中得到完整支持，提供专门的解析器：

- **创建标签**：`CreateTagResolver` 支持以编程方式创建标签，并带有权限校验
- **更新标签**：`SetTagColorResolver` 以及用于标签属性的更新操作
- **删除标签**：`DeleteTagResolver` 用于移除废弃标签
- **向实体添加标签**：`AddTagResolver`、`AddTagsResolver` 及批量操作
- **从实体移除标签**：`RemoveTagResolver` 及批量移除操作

这些解析器会强制执行授权策略，确保只有具备适当权限（`CREATE_TAG`、`MANAGE_TAGS` 或 `EDIT_ENTITY`）的用户才能修改标签及标签分配。

### 搜索与发现

标签已针对搜索建立索引，具备以下能力：

- **全文搜索**：可搜索标签名称与描述
- **自动补全**：标签名称支持自动补全，便于选择
- **筛选**：在所有搜索界面中都可按标签筛选资产
- **分面**：标签会作为筛选选项出现在搜索结果中

## 值得注意的例外

### 标签命名约定

虽然 DataHub 并未强制严格的命名约定，但仍建议遵循以下最佳实践：

- **使用小写**：实践中可使标签不区分大小写（`pii` 与 `PII`）
- **使用下划线或连字符**：适用于多词标签（`data_quality` 或 `data-quality`）
- **保持简洁**：短名称更易读易用
- **避免特殊字符**：仅使用字母数字字符、下划线和连字符

### 标签泛滥

组织应围绕标签创建建立治理机制，以避免"标签 sprawl"：

- **定义核心集合**：从 10-20 个必要标签起步
- **记录使用方式**：为每个标签维护清晰的适用说明
- **定期审计**：周期性检查并合并相近或未使用的标签
- **所有权模型**：指定标签负责人以审批新标签或变更

### 系统标签与用户标签

虽然 DataHub 并未正式区分系统标签与用户标签，组织通常会建立如下约定：

- **系统标签**：由自动化流程创建（例如 `ingestion_error`、`schema_drift`）
- **用户标签**：由数据从业者手动创建（例如 `important`、`sandbox`）

如有需要，可考虑使用前缀或命名空间来区分这两类标签。

### 标签与访问控制

标签本身既不授予也不限制对数据的访问。但它们可以与 DataHub 策略配合使用，用于：

- 控制谁可以查看某些带标签的资产
- 限制谁可以应用敏感标签
- 基于标签存在与否触发工作流（例如为标记了 `requires_docs` 的资产生成文档）

标签是关于你的数据的元数据，而不是安全机制。访问控制请使用 DataHub 的授权功能。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](14-tag.md)。
