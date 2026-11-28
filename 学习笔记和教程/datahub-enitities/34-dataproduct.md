---
title: 数据产品
entity: dataproduct
order: 34
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataproduct.md
---

# 数据产品

数据产品（Data Products）是经过精心整理的数据资产集合，便于发现与消费。它们代表一种创新的组织方式，把 DataHub 中相关的数据资产（如表、仪表板、图表、流水线）打包在一起。数据产品是数据网格（data mesh）架构中的关键概念，在其中它们作为由特定领域团队管理的独立数据单元。

与 DataHub 中通常代表源系统技术资产的其他实体不同，数据产品是 DataHub 自创的概念，提供了一种逻辑分组机制，把资产组织成可供消费的交付物。

## 身份

数据产品由单个字段标识：

- **id**：数据产品的唯一标识符，通常是一个便于阅读的字符串，例如 `pet_of_the_week` 或 `customer_360`。

数据产品标识符的一个示例是 `urn:li:dataProduct:pet_of_the_week`。

标识符的简洁性使数据产品易于创建和引用，因为它们无需绑定到任何特定平台或技术。

## 重要能力

### 数据产品属性

数据产品的核心属性记录在 `dataProductProperties` aspect 中，其中包括：

- **name**：数据产品的显示名称，可搜索并用于自动补全
- **description**：描述数据产品提供什么以及如何使用的文档
- **assets**：属于该数据产品的数据资产列表，每个资产可带有一个可选的 `outputPort` 标记

#### 资产关联

数据产品可以包含 `dataProductProperties` aspect 中定义的各种资产类型：

- 数据集（表、视图、流）
- 数据任务与数据流（流水线）
- 仪表板与图表（可视化）
- 笔记本
- 容器（schema、数据库）
- 机器学习模型、机器学习模型组、机器学习特征表、机器学习特征与机器学习主键

每个资产关联都可以被标记为**输出端口（output port）**，在数据网格术语中，它代表打算与其他团队共享和消费的数据资产。这使数据产品所有者能够区分：

- **内部资产**：在数据产品内部用于处理的数据
- **输出端口**：明确发布用于外部消费的数据

下面的代码片段展示了如何创建包含多个资产的数据产品，并将其中一个标记为输出端口。

**Python：创建带资产的数据产品**

```python
# Inlined from /metadata-ingestion/examples/library/dataproduct_create_sdk.py
from datahub.api.entities.dataproduct.dataproduct import DataProduct
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

data_product = DataProduct(
    id="customer_360",
    display_name="Customer 360",
    domain="urn:li:domain:marketing",
    description="A comprehensive view of customer data including profiles, transactions, and behaviors.",
    assets=[
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,customer_db.public.customer_profile,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,customer_db.public.customer_transactions,PROD)",
        "urn:li:dashboard:(looker,customer_overview)",
    ],
    output_ports=[
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,customer_db.public.customer_profile,PROD)"
    ],
    owners=[
        {"id": "urn:li:corpuser:datahub", "type": "BUSINESS_OWNER"},
        {"id": "urn:li:corpuser:jdoe", "type": "TECHNICAL_OWNER"},
    ],
    terms=["urn:li:glossaryTerm:CustomerData"],
    tags=["urn:li:tag:production"],
    properties={"tier": "gold", "sla": "99.9%"},
    external_url="https://wiki.company.com/customer-360",
)

for mcp in data_product.generate_mcp(upsert=True):
    graph.emit(mcp)

print(f"Created Data Product: urn:li:dataProduct:{data_product.id}")

```

### 资产设置

`assetSettings` aspect 允许数据产品配置自定义设置，例如自定义的资产摘要配置。该 aspect 与领域（Domains）、术语表术语等其他组织实体共用，从而以一致的方式定制资产的展示与摘要方式。

### 标签与术语表术语

数据产品支持标签与术语表术语，便于对数据交付物进行分类和文档化。标签可用于非正式分类（例如 "adoption"、"experimental"），而术语表术语则提供正式的业务词汇关联。

以下是为数据产品添加元数据的示例：

**Python SDK：为数据产品添加标签和术语**

```python
# Inlined from /metadata-ingestion/examples/library/dataproduct_add_metadata.py
from datahub.emitter.mce_builder import (
    make_data_product_urn,
    make_tag_urn,
    make_term_urn,
)
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    GlossaryTermAssociationClass,
    TagAssociationClass,
)
from datahub.specific.dataproduct import DataProductPatchBuilder

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

data_product_urn = make_data_product_urn("customer_360")

for mcp in (
    DataProductPatchBuilder(data_product_urn)
    .add_tag(TagAssociationClass(tag=make_tag_urn("production")))
    .add_tag(TagAssociationClass(tag=make_tag_urn("pii")))
    .add_term(
        GlossaryTermAssociationClass(urn=make_term_urn("CustomerData.PersonalInfo"))
    )
    .build()
):
    rest_emitter.emit(mcp)
    print(f"Added metadata to Data Product {data_product_urn}")

```

### 所有权

数据产品通过 `ownership` aspect 支持所有权。所有者可以是个人或群组，并可拥有不同的所有权类型（BUSINESS_OWNER、TECHNICAL_OWNER、DATA_STEWARD 等）。当通过 UI 创建数据产品时，创建者会自动被添加为所有者。

所有权有助于建立问责机制，明确谁负责维护数据产品并确保数据质量。

### 业务域

数据产品可以选择归属到一个业务域，该业务域代表负责该数据产品的业务领域或团队。

业务域关联记录在 `domains` aspect 中，可在创建数据产品时设置，但不是必需的。

### 文档与机构记忆

数据产品除基本描述字段外，还可以有丰富的文档：

- **institutionalMemory**：指向 Confluence 页面、Google Docs 或其他文档等外部资源的链接
- **forms**：通过 DataHub 的 Forms 功能提供的结构化文档
- **structuredProperties**：由你的组织定义的自定义元数据字段

### 向数据产品添加资产

资产可以通过两种方式关联到数据产品：

1. **从数据产品页面**：使用 “Add Assets” 按钮搜索并一次添加多个资产
2. **从资产页面**：在资产侧边栏使用 “Set Data Product” 选项将其添加到数据产品

**Python SDK：向已有数据产品添加资产**

```python
# Inlined from /metadata-ingestion/examples/library/dataproduct_add_assets.py
from datahub.emitter.mce_builder import make_data_product_urn, make_dataset_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.specific.dataproduct import DataProductPatchBuilder

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

data_product_urn = make_data_product_urn("customer_360")

new_assets = [
    make_dataset_urn(
        platform="snowflake",
        name="customer_db.public.customer_orders",
        env="PROD",
    ),
    make_dataset_urn(
        platform="snowflake",
        name="customer_db.public.customer_support_tickets",
        env="PROD",
    ),
]

for mcp in (
    DataProductPatchBuilder(data_product_urn)
    .add_asset(new_assets[0])
    .add_asset(new_assets[1])
    .build()
):
    rest_emitter.emit(mcp)
    print(f"Added assets to Data Product {data_product_urn}")

```

### 查询数据产品

可以使用 REST API 查询数据产品，以获取其属性和关联资产。

**通过 REST API 查询数据产品**

```python
# Inlined from /metadata-ingestion/examples/library/dataproduct_query_rest.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import (
    DataProductPropertiesClass,
    DomainsClass,
    GlobalTagsClass,
    GlossaryTermsClass,
    OwnershipClass,
)
from datahub.metadata.urns import DataProductUrn

graph = get_default_graph()

data_product_urn = DataProductUrn("pet_of_the_week")

# get_entity_raw() cannot be used to test existence -- entitiesV2 synthesizes the key
# aspect for an entity that was never created, so it always returns a non-empty payload.
if not graph.exists(str(data_product_urn)):
    raise SystemExit(f"Data Product not found: {data_product_urn}")

print(f"Successfully retrieved Data Product: {data_product_urn}")

properties = graph.get_aspect(
    entity_urn=str(data_product_urn), aspect_type=DataProductPropertiesClass
)
if properties is not None:
    print(f"Name: {properties.name}")
    print(f"Description: {properties.description}")

    assets = properties.assets or []
    print(f"Number of assets: {len(assets)}")
    for asset in assets:
        print(f"  - Asset: {asset.destinationUrn} (Output Port: {asset.outputPort})")

domains = graph.get_aspect(entity_urn=str(data_product_urn), aspect_type=DomainsClass)
if domains is not None:
    print(f"Domain: {domains.domains}")

ownership = graph.get_aspect(
    entity_urn=str(data_product_urn), aspect_type=OwnershipClass
)
if ownership is not None:
    print(f"Number of owners: {len(ownership.owners)}")
    for owner in ownership.owners:
        print(f"  - Owner: {owner.owner} (Type: {owner.type})")

tags = graph.get_aspect(entity_urn=str(data_product_urn), aspect_type=GlobalTagsClass)
if tags is not None:
    print(f"Tags: {[t.tag for t in tags.tags]}")

terms = graph.get_aspect(
    entity_urn=str(data_product_urn), aspect_type=GlossaryTermsClass
)
if terms is not None:
    print(f"Glossary Terms: {[t.urn for t in terms.terms]}")

```

## 集成点

数据产品与 DataHub 的若干关键领域集成：

### 与业务域的关系

数据产品可以选择归属到一个业务域，从而形成层级化的组织结构：

```
Domain (e.g., "Marketing")
  └── Data Product (e.g., "Customer 360")
      ├── Dataset: customer_profile
      ├── Dataset: customer_transactions
      ├── Dashboard: customer_overview
      └── DataFlow: customer_pipeline
```

这种层级结构使组织能够实施数据网格原则，即每个领域拥有并管理自己的数据产品。

### 与资产的关系

数据产品与其资产之间建立 `DataProductContains` 关系。该关系是双向的：

- 从数据产品可以看到其包含的所有资产
- 从任意资产可以看到它属于哪个（或哪些）数据产品

#### 每个资产属于单个还是多个数据产品

**默认情况下**，一个资产可以同时属于多个数据产品，从而支持灵活的组织方案。例如，同一个资产可以同时属于 “Customer 360” 产品和 “Marketing Analytics” 产品。这允许同一数据资产在不同领域或用例中服务于多种用途，体现不同的组织视角。

**如果你更倾向于单一数据产品成员关系**（即一个资产在同一时间只能关联到一个数据产品），可以将 `MULTIPLE_DATA_PRODUCTS_PER_ASSET` 环境变量设置为 `false` 来禁用该特性。在此设置下，当把资产分配给新的数据产品时，它会自动从先前关联的数据产品中移除。

要禁用每个资产属于多个数据产品的能力，请在 GMS 配置中设置以下环境变量：

```bash
MULTIPLE_DATA_PRODUCTS_PER_ASSET=false
```

### 授权与访问控制

DataHub 将**产品侧**与**资产侧**的数据产品权限区分开来：

| 操作                                                     | 权限                    | 校验对象                                                                    |
| -------------------------------------------------------- | ----------------------- | --------------------------------------------------------------------------- |
| 创建、更新或删除数据产品                                  | **Manage Data Products** | 与该产品关联的业务域                                                        |
| 在数据产品页面添加/移除资产（`batchSetDataProduct`）     | **Manage Data Products** | 产品上**至少一个**业务域                                                    |
| 从资产详情页设置/取消设置数据产品                         | **Edit Data Product**    | **资产**（`batchAddToDataProducts`、`batchRemoveFromDataProducts`、通过 `batchSetDataProduct` 取消设置） |

**Manage Data Products** 是业务域范围的策略权限。对于产品页的成员关系变更，操作者必须对该产品关联的**至少一个**业务域拥有管理权限。产品与资产的业务域不必一致。当一个产品关联多个业务域时（不常见，但可通过直接写入元数据产生），对其中任意一个产品业务域拥有管理权限即可。没有任何业务域关联的产品无法从产品侧管理（fail-closed）；资产侧的 **Edit Data Product** 授权仍可能通过 MCP 或资产详情页 API 允许成员关系变更。

直接写入元数据（MCP、摄取）时，只要在每一个变更的资产上**产品侧的管理授权或资产侧的编辑授权**任一成功，即允许变更成员关系。

通过 `updateName` 重命名时，也接受针对数据产品 URN 的 **Edit Entity** 作为业务域级管理权限的替代方案。

详见 [数据产品用户指南](https://docs.datahub.com/docs/dataproducts) 与 [元数据策略 —— 派生授权规则](https://docs.datahub.com/docs/authorization/policies#derived-authorization-rules)。

### GraphQL API

DataHub GraphQL API 提供了多个用于操作数据产品的 mutation：

- `createDataProduct`：创建新的数据产品，可选地在某个业务域下
- `updateDataProduct`：更新数据产品属性
- `deleteDataProduct`：删除数据产品
- `batchSetDataProduct`：从数据产品批量添加或移除资产
- `listDataProductAssets`：查询属于某个数据产品的资产

### 搜索与发现

数据产品是 DataHub 中可搜索的实体。`name` 与 `description` 字段会被索引，并且数据产品可按以下维度过滤：

- 业务域
- 所有权
- 标签
- 术语表术语
- 结构化属性

这使得数据消费者能够轻松地在组织范围内发现相关的数据产品。

## 值得注意的例外情况

### 业务域关联

数据产品可以选择归属到一个业务域。分配业务域符合数据网格原则，能让数据产品拥有明确的组织归属者，但数据产品也可以在不带业务域的情况下创建。

### 输出端口

资产关联上的 `outputPort` 标记是一项面向未来的、与数据网格原则对齐的特性。虽然该标记目前已可设置，但围绕输出端口的高级功能（如差异化访问控制或版本化）仍在开发中。当前路线图包括：

- 支持将数据产品中的数据资产标记为私有或可共享
- 支持在数据产品之间手动声明数据血缘
- 支持为数据产品声明逻辑 schema
- 支持数据产品的语义化版本管理

### 基于 YAML 的管理

DataHub 支持通过 YAML 文件以即代码方式管理数据产品。这启用了 GitOps 工作流，数据产品定义可纳入版本控制并通过 CI/CD 流水线部署。`datahub` CLI 提供了以下命令：

- `datahub dataproduct upsert`：从 YAML 创建或更新数据产品
- `datahub dataproduct diff`：比较 YAML 与当前状态
- `datahub dataproduct delete`：删除数据产品

这允许采用混合模式：业务用户通过 UI 管理数据产品，而技术团队采用基础设施即代码的实践。

### 多资产成员关系

**默认行为**：一个资产可以同时属于多个数据产品。这种灵活性支持不同的组织视角——例如，一个数据集可能既属于某个领域专属产品，同时又被纳入跨职能的分析产品。

**遗留单一成员关系模式**：如果你更倾向于一个资产在同一时间只能属于单个数据产品，可以将 `MULTIPLE_DATA_PRODUCTS_PER_ASSET` 环境变量设置为 `false`。在此设置下，当把资产分配给新的数据产品时，它会自动从之前的数据产品关联中移除。

有关配置该行为的更多细节，请参阅上文 “与资产的关系” 一节。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](34-dataproduct.md)。
