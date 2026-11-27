---
title: 数据产品
entity: dataproduct
order: 34
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataproduct.md
---

# 数据产品

Data Product（数据产品）是精心策划的数据资产集合，旨在便于发现和使用。它们代表一种创新的组织方式，用于在 DataHub 中组织并打包相关的数据资产，例如表、仪表板、图表、流水线及其他实体。数据产品是数据网格架构中的关键概念，在其中它们作为由特定领域团队管理的独立数据单元。

与 DataHub 中通常代表源系统中技术资产的其他实体不同，Data Product 是 DataHub 独创的概念，提供了一种逻辑分组机制，将资产组织成可消费的产品。

## 标识

Data Product 由单一字段标识：

- **id**：Data Product 的唯一标识符，通常是人类可读的字符串，例如 `pet_of_the_week` 或 `customer_360`。

Data Product 标识符的一个示例是 `urn:li:dataProduct:pet_of_the_week`。

标识符的简洁性使 Data Product 易于创建和引用，因为它们无需绑定到任何特定平台或技术。

## 重要能力

### 数据产品属性

Data Product 的核心属性记录在 `dataProductProperties` aspect 中，其中包括：

- **name**：Data Product 的显示名称，可被搜索并用于自动补全
- **description**：描述 Data Product 提供什么以及如何使用它的文档
- **assets**：属于该 Data Product 的数据资产列表，每个资产可带一个可选的 `outputPort` 标志

#### 资产关联

Data Product 可以包含多种资产类型，在 `dataProductProperties` aspect 中定义：

- 数据集（表、视图、流）
- 数据作业和数据流（流水线）
- 仪表板和图表（可视化）
- Notebook
- 容器（模式、数据库）
- ML 模型、ML 模型组、ML 特征表、ML 特性以及 ML 主键

每个资产关联都可以标记为**输出端口（output port）**，在数据网格术语中，它代表打算共享并供其他团队消费的数据资产。这允许 Data Product 的所有者区分：

- **内部资产**：在 Data Product 内部用于处理的数据
- **输出端口**：明确发布供外部消费的数据

以下代码片段展示了如何创建包含多个资产、并把其中一个标记为输出端口的 Data Product。


**Python：创建带资产的 Data Product**

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

`assetSettings` aspect 允许 Data Product 配置自定义设置，例如自定义资产摘要配置。该 aspect 与 Domains、Glossary Terms 等其他组织性实体共享，从而以一致的方式定制资产的展示和摘要方式。

### 标签与术语表术语

Data Product 支持标签和术语表术语，便于你对其数据产品进行分类和记录。标签可用于非正式分类（例如 "adoption"、"experimental"），而术语表术语则提供正式的业务词汇关联。

以下是为 Data Product 添加元数据的示例：


**Python SDK：为 Data Product 添加标签和术语**

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

Data Product 通过 `ownership` aspect 支持所有权。所有者可以是个人或群组，并可具有不同的所有权类型（BUSINESS_OWNER、TECHNICAL_OWNER、DATA_STEWARD 等）。当通过 UI 创建 Data Product 时，创建者会自动被添加为所有者。

所有权有助于建立问责机制，并明确谁负责维护 Data Product 以及确保数据质量。

### 域

一个 Data Product 可以选择归属于一个代表该 Data Product 所属业务领域或团队的 Domain。

Domain 关联记录在 `domains` aspect 中，可在创建 Data Product 时设置，但并非必需。

### 文档与机构记忆

Data Product 除了基本的 description 字段外，还可以有丰富的文档：

- **institutionalMemory**：指向 Confluence 页面、Google Docs 或其他文档等外部资源的链接
- **forms**：通过 DataHub 的 Forms 功能提供的结构化文档
- **structuredProperties**：由你的组织定义的自定义元数据字段

### 向 Data Product 添加资产

资产可以通过两种方式关联到 Data Product：

1. **从 Data Product 页面**：使用 "Add Assets" 按钮搜索并一次性添加多个资产
2. **从资产页面**：使用资产侧边栏中的 "Set Data Product" 选项将其添加到 Data Product


**Python SDK：向已有 Data Product 添加资产**

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



### 查询 Data Product

可以使用 REST API 查询 Data Product，以获取其属性和关联资产。


**通过 REST API 查询 Data Product**

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

Data Product 与 DataHub 的若干关键领域集成：

### 与 Domain 的关系

Data Product 可以选择归属于一个 Domain，从而形成层级化的组织结构：

```
Domain (e.g., "Marketing")
  └── Data Product (e.g., "Customer 360")
      ├── Dataset: customer_profile
      ├── Dataset: customer_transactions
      ├── Dashboard: customer_overview
      └── DataFlow: customer_pipeline
```

这种层级结构使组织能够落实数据网格原则，即每个 Domain 拥有并管理其 Data Product。

### 与资产的关系

Data Product 与其资产建立 `DataProductContains` 关系。该关系是双向的：

- 从 Data Product 可以查看所有包含的资产
- 从任一资产可以查看其所属的 Data Product

#### 每个资产对应单个还是多个 Data Product

**默认情况下**，一个资产可以同时属于多个 Data Product，从而支持灵活的组织方案。例如，一个资产可以同时属于 "Customer 360" 和 "Marketing Analytics" 两个产品。这允许从不同的组织视角出发，让同一数据资产服务于跨领域或跨用例的多种目的。

**如果你偏好单一 Data Product 成员关系**（即一个资产在同一时间只能关联一个 Data Product），可以将 `MULTIPLE_DATA_PRODUCTS_PER_ASSET` 环境变量设置为 `false` 来禁用该功能。在该设置下，当把一个资产分配给新的 Data Product 时，它会自动从之前关联的 Data Product 中移除。

要禁用每个资产对应多个 Data Product，请在 GMS 配置中设置以下环境变量：

```bash
MULTIPLE_DATA_PRODUCTS_PER_ASSET=false
```

### 授权与访问控制

DataHub 将**产品侧**与**资产侧**的 Data Product 权限区分开来：

| 操作                                                               | 权限                    | 评估依据                                                                                             |
| -------------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------- |
| 创建、更新或删除 Data Product                                       | **Manage Data Products** | 与该产品关联的 Domain                                                                                    |
| 从 Data Product 页面添加/移除资产（`batchSetDataProduct`）          | **Manage Data Products** | 产品上**至少一个** Domain                                                                                 |
| 从资产侧栏设置/取消设置 Data Product                                 | **Edit Data Product**    | **资产**（`batchAddToDataProducts`、`batchRemoveFromDataProducts`、通过 `batchSetDataProduct` 取消设置）   |

**Manage Data Products** 是按 Domain 划分的策略权限。对于产品页面的成员关系变更，执行者必须对该产品关联的**至少一个** Domain 具有管理权限。产品 Domain 与资产 Domain 无需匹配。当一个产品关联到多个 Domain 时（不常见，但可通过直接写入元数据实现），对任意一个产品 Domain 具有管理权限即足够。没有关联任何 Domain 的产品无法从产品侧进行管理（fail-closed）；资产侧的 **Edit Data Product** 授权仍可能通过 MCP 或资产档案 API 允许成员关系变更。

直接写入元数据（MCP、摄取）时，只要对每个发生变更的资产而言，**产品侧管理权限或资产侧编辑权限其中之一**验证通过，即允许成员关系变更。

通过 `updateName` 重命名时，也接受对 Data Product URN 的 **Edit Entity** 作为域级管理权限的替代。

详情参见 [Data Products 用户指南](https://docs.datahub.com/docs/dataproducts.md 和 [元数据策略——派生授权规则](https://docs.datahub.com/docs/authorization/policies.md#derived-authorization-rules。

### GraphQL API

DataHub GraphQL API 提供了若干用于操作 Data Product 的变更：

- `createDataProduct`：创建新的 Data Product，可选择放入某个 Domain
- `updateDataProduct`：更新 Data Product 属性
- `deleteDataProduct`：删除 Data Product
- `batchSetDataProduct`：向 Data Product 添加或移除多个资产
- `listDataProductAssets`：查询属于某个 Data Product 的资产

### 搜索与发现

Data Product 在 DataHub 中是可搜索实体。`name` 和 `description` 字段已建立索引，并且可以按以下维度过滤 Data Product：

- Domain
- 所有权
- 标签
- 术语表术语
- 结构化属性

这使数据消费者可以轻松地在整个组织范围内发现相关的 Data Product。

## 值得注意的例外情况

### Domain 关联

一个 Data Product 可以选择归属于一个 Domain。分配 Domain 符合数据网格原则，因为它为 Data Product 提供了明确的组织归属，但 Data Product 也可以在没有 Domain 的情况下创建。

### 输出端口

资产关联上的 `outputPort` 标志是一项面向未来的、与数据网格原则一致的功能。虽然该标志目前可以设置，但围绕输出端口的高级功能（如差异化访问控制或版本管理）仍在开发中。当前路线图包括：

- 支持将 Data Product 中的数据资产标记为私有或可共享
- 支持在 Data Product 之间手动声明数据血缘
- 支持为 Data Product 声明逻辑模式
- 支持 Data Product 的语义化版本管理

### 基于 YAML 的管理

DataHub 支持通过 YAML 文件以即代码方式管理 Data Product。这支持 GitOps 工作流，其中 Data Product 定义受版本控制并通过 CI/CD 流水线部署。`datahub` CLI 提供以下命令：

- `datahub dataproduct upsert`：从 YAML 创建或更新 Data Product
- `datahub dataproduct diff`：将 YAML 与当前状态比较
- `datahub dataproduct delete`：删除 Data Product

这允许采用混合模式：业务用户通过 UI 管理 Data Product，技术团队则使用基础设施即代码实践。

### 多资产成员关系

**默认行为**：一个资产可以同时属于多个 Data Product。这种灵活性支持不同的组织视角——例如，一个数据集既可能属于某个特定领域的产品，同时又被纳入一个跨职能的分析产品。

**旧版单一成员关系模式**：如果你偏好一个资产在同一时间只能属于单个 Data Product 的行为，可以将 `MULTIPLE_DATA_PRODUCTS_PER_ASSET` 环境变量设置为 `false`。在该设置下，当把一个资产分配给新的 Data Product 时，它会自动从其之前的 Data Product 关联中移除。

有关配置此行为的更多细节，请参阅上文“与资产的关系”部分。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](34-dataproduct.md)。
