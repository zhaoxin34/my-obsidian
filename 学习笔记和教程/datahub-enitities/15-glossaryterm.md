---
title: 术语表术语
entity: glossaryterm
order: 15
source: https://docs.datahub.com/docs/generated/metamodel/entities/glossaryterm.md
---

# 术语表术语

术语表术语（GlossaryTerm）代表一个标准化的业务定义或词汇术语，可以在整个组织范围内关联到数据资产。GlossaryTerm 是 DataHub 业务术语表（Business Glossary）功能的基本构件，使团队能够建立并维护用于描述数据概念的共享词汇表。

在实际使用中，GlossaryTerm 让你可以：

- 用清晰、权威的定义来定义业务术语
- 在相关业务概念之间创建关系（继承、包含等）
- 用标准化业务术语标记数据资产（数据集、仪表板、图表等）
- 对业务词汇表建立治理与归属机制
- 链接到外部资源与文档

例如，一个 GlossaryTerm 可以为“Customer Lifetime Value (CLV)”给出精确的业务定义，将其与“Revenue”“Customer”等其他术语关联，并应用到存储 CLV 计算结果的具体数据集列上。

## 标识（Identity）

GlossaryTerm 由单个字段唯一标识：其 **name**。该名称在整个生命周期中充当该术语的持久标识符。

### URN 结构

GlossaryTerm 的 URN（统一资源名称）遵循如下模式：

```
urn:li:glossaryTerm:<term_name>
```

其中：

- `<term_name>`：术语的唯一字符串标识符。它可以是人类可读的（例如 "CustomerLifetimeValue"），也可以是生成的 ID（例如 "clv-001" 或 UUID）。

### 示例

```
# Simple term name
urn:li:glossaryTerm:Revenue

# Hierarchical naming convention (common pattern)
urn:li:glossaryTerm:Finance.Revenue
urn:li:glossaryTerm:Classification.PII
urn:li:glossaryTerm:Classification.Confidential

# UUID-based identifier
urn:li:glossaryTerm:41516e31-0acb-fd90-76ff-fc2c98d2d1a3

# Descriptive identifier
urn:li:glossaryTerm:CustomerLifetimeValue
```

### 术语命名的最佳实践

1. **使用层级化命名**：为术语加上所属分类前缀（例如 `Classification.PII`、`Finance.Revenue`），即使名称是扁平的也能表达结构。
2. **保持一致**：选择一种命名约定（camelCase、点号记法等）并统一使用。
3. **保持稳定**：术语名称即标识符，不应更改。显示名称请使用 `glossaryTermInfo` 中的 `name` 字段。
4. **考虑组织结构**：虽然 URN 是扁平的，但你可以使用 glossaryNodes（术语组）在 UI 中创建层级化的组织结构。

## 重要能力

### 核心业务定义（glossaryTermInfo）

`glossaryTermInfo` aspect 包含术语的基本业务信息：

- **definition**（必填）：术语的权威业务定义。应当清晰、简洁，并提供足够的上下文让任何人都能理解该术语的含义。
- **name**：在 UI 中显示的名称。它可以比 URN 标识符更友好（例如 "Customer Lifetime Value" 对比 "CustomerLifetimeValue"）。
- **parentNode**：对 GlossaryNode（术语组）的引用，作为对术语进行层级化组织的文件夹。
- **termSource**：标识该术语是 "INTERNAL"（在组织内部定义）还是 "EXTERNAL"（来自 FIBO 等外部标准）。
- **sourceRef**：外部术语来源的引用标识符（例如 "FIBO" 表示 Financial Industry Business Ontology）。
- **sourceUrl**：指向该术语外部定义的 URL。
- **customProperties**：针对你所在组织的额外元数据键值对。

示例：

```python
{
  "name": "Customer Lifetime Value",
  "definition": "The total revenue a business can expect from a single customer account throughout the business relationship.",
  "termSource": "INTERNAL",
  "parentNode": "urn:li:glossaryNode:Finance"
}
```

### 术语关系（glossaryRelatedTerms）

GlossaryTerm 支持多种关系类型，用于建模业务概念之间的语义联系：

#### 1. IsA 关系（继承）

表示某个术语是另一个术语的特殊化类型。这构成一个"Is-A"层级，更具体的术语继承更宽泛术语的特征。

**使用场景**：`Email` IsA `PersonalInformation`，`SocialSecurityNumber` IsA `PersonalInformation`

#### 2. HasA 关系（包含）

表示某个术语包含或由另一个术语组成。这构成一个"Has-A"关系，即复杂概念由更简单的部分构成。

**使用场景**：`Address` HasA `ZipCode`，`Address` HasA `Street`，`Address` HasA `City`

#### 3. Values 关系

为枚举型术语定义允许的取值。适用于受控词汇表，即某个术语拥有一组固定的有效取值。

**使用场景**：`ColorEnum` HasValues `Red`、`Green`、`Blue`

#### 4. RelatedTo 关系

用于语义相关但不适配其他类别的术语的通用关系。

**使用场景**：`Revenue` RelatedTo `Profit`，`Customer` RelatedTo `Account`

### 层级化组织

GlossaryTerm 可以通过 **GlossaryNodes**（术语组）进行层级化组织。`glossaryTermInfo` 中的 `parentNode` 字段建立起这种关系：

```
GlossaryNode: Classification
  ├── GlossaryTerm: Sensitive
  ├── GlossaryTerm: Confidential
  └── GlossaryTerm: HighlyConfidential

GlossaryNode: PersonalInformation
  ├── GlossaryTerm: Email
  ├── GlossaryTerm: Address
  └── GlossaryTerm: PhoneNumber
```

该层级在 DataHub UI 中可见，有助于用户浏览大型术语表。

### 将术语应用到数据资产

当术语被应用到实际数据资产时才真正发挥作用。术语可以挂载到：

- 数据集（表、视图、文件）
- 数据集字段（列）
- 仪表板
- 图表
- 数据任务
- 容器
- 以及许多其他实体类型

当术语被应用到数据资产时，会创建一个 **TermedWith** 关系，从而实现：

- 发现：查找所有被某个特定业务概念标记的资产
- 治理：跟踪哪些资产包含敏感数据类型
- 文档：为技术资产提供业务上下文
- 合规：识别受监管要求约束的数据集

## 代码示例

### 创建 GlossaryTerm


**Python SDK：创建基础 GlossaryTerm**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_term_create.py
from datahub.sdk import DataHubClient
from datahub.sdk.glossary_term import GlossaryTerm

client = DataHubClient.from_env()

term = GlossaryTerm(
    id="a1b2c3d4",
    display_name="Customer Lifetime Value",
    definition="The total revenue a business can expect from a single customer account throughout the business relationship. This metric helps prioritize customer retention efforts and marketing spend.",
)

client.entities.upsert(term)

```




**Python SDK：创建带完整元数据的 GlossaryTerm**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_term_create_with_metadata.py
from datahub.metadata.urns import CorpGroupUrn, CorpUserUrn
from datahub.sdk import DataHubClient, GlossaryNodeUrn
from datahub.sdk.glossary_term import GlossaryTerm

client = DataHubClient.from_env()

term = GlossaryTerm(
    id="3a4b5c6d",
    display_name="Personally Identifiable Information",
    definition="Information that can be used to identify, contact, or locate a single person, or to identify an individual in context. Examples include name, email address, phone number, and social security number.",
    parent_node=GlossaryNodeUrn("2f3a4b5c"),
    custom_properties={
        "sensitivity_level": "HIGH",
        "data_retention_period": "7_years",
        "regulatory_framework": "GDPR,CCPA",
    },
    owners=[CorpUserUrn("datahub"), CorpGroupUrn("privacy-team")],
    links=[
        (
            "https://wiki.company.com/privacy/pii-guidelines",
            "Internal PII Handling Guidelines",
        ),
        ("https://gdpr.eu/", "GDPR Official Documentation"),
    ],
)

client.entities.upsert(term)

```



### 管理术语关系


**Python SDK：在 GlossaryTerm 之间添加关系**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_term_add_relationships.py
from datahub.metadata.urns import GlossaryTermUrn
from datahub.sdk import DataHubClient
from datahub.sdk.glossary_term import GlossaryTerm

client = DataHubClient.from_env()

# Email — is a type of PII and Sensitive, related to PhoneNumber and Contact
email_term = GlossaryTerm(
    id="1a2b3c4d",
    display_name="Email",
    definition="Email addresses that can identify individuals.",
    is_a=[
        GlossaryTermUrn("a1b2c3d4"),  # Classification.PII
        GlossaryTermUrn("b2c3d4e5"),  # Classification.Sensitive
    ],
    related_terms=[
        GlossaryTermUrn("c3d4e5f6"),  # PersonalInformation.PhoneNumber
        GlossaryTermUrn("d4e5f6a7"),  # PersonalInformation.Contact
    ],
)

# Address — is a type of PII, has components (ZipCode, Street, City, Country)
address_term = GlossaryTerm(
    id="5e6f7a8b",
    display_name="Address",
    definition="Physical addresses that can identify individuals.",
    is_a=[GlossaryTermUrn("a1b2c3d4")],  # Classification.PII
    has_a=[
        GlossaryTermUrn("e5f6a7b8"),  # PersonalInformation.ZipCode
        GlossaryTermUrn("f6a7b8c9"),  # PersonalInformation.Street
        GlossaryTermUrn("a7b8c9d0"),  # PersonalInformation.City
        GlossaryTermUrn("b8c9d0e1"),  # PersonalInformation.Country
    ],
)

# ColorEnum — an enumeration with fixed allowed values
color_enum_term = GlossaryTerm(
    id="9c0d1e2f",
    display_name="Color",
    definition="An enumeration of allowed color values.",
    values=[
        GlossaryTermUrn("c9d0e1f2"),  # Colors.Red
        GlossaryTermUrn("d0e1f2a3"),  # Colors.Green
        GlossaryTermUrn("e1f2a3b4"),  # Colors.Blue
        GlossaryTermUrn("f2a3b4c5"),  # Colors.Yellow
    ],
)

client.entities.upsert(email_term)
client.entities.upsert(address_term)
client.entities.upsert(color_enum_term)

```



### 将术语应用到资产


**Python SDK：为一个数据集添加 GlossaryTerm**

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




**Python SDK：为一个数据集列添加 GlossaryTerm**

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



### 查询 GlossaryTerm


**REST API：按 URN 获取 GlossaryTerm**

```bash
# Fetch a GlossaryTerm entity
curl -X GET 'http://localhost:8080/entities/urn%3Ali%3AglossaryTerm%3ACustomerLifetimeValue' \
  -H 'Authorization: Bearer <token>'

# Response includes all aspects:
# - glossaryTermKey (identity)
# - glossaryTermInfo (definition, name, etc.)
# - glossaryRelatedTerms (relationships)
# - ownership (who owns this term)
# - institutionalMemory (links to documentation)
# - etc.
```




**REST API：搜索被某个术语标记的资产**

```bash
# Find all datasets tagged with a specific term
curl -X POST 'http://localhost:8080/entities?action=search' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{
    "entity": "dataset",
    "input": "*",
    "filter": {
      "or": [
        {
          "and": [
            {
              "field": "glossaryTerms",
              "value": "urn:li:glossaryTerm:Classification.PII",
              "condition": "EQUAL"
            }
          ]
        }
      ]
    },
    "start": 0,
    "count": 10
  }'
```




**Python SDK：查询应用于数据集的术语**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_query_terms.py
from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient.from_env()

dataset = client.entities.get(
    DatasetUrn(platform="hive", name="realestate_db.sales", env="PROD")
)

print(dataset.terms)

```



### 批量操作


**YAML 摄取：从业务术语表文件创建多个术语**

```yaml
# business_glossary.yml
version: "1"
source: MyOrganization
owners:
  users:
    - datahub
nodes:
  - name: Classification
    description: Data classification categories
    terms:
      - name: PII
        description: Personally Identifiable Information
      - name: Confidential
        description: Confidential business data
      - name: Public
        description: Publicly available data

  - name: Finance
    description: Financial domain terms
    terms:
      - name: Revenue
        description: Total income from business operations
      - name: Profit
        description: Financial gain after expenses
        related_terms:
          - Finance.Revenue
# Ingest using the DataHub CLI:
# datahub ingest -c business_glossary.yml
```

完整的 YAML 格式规范请参见 [Business Glossary Source](https://docs.datahub.com/docs/generated/ingestion/sources/business-glossary.md 文档。



## 集成点

### 与 GlossaryNode 的关系

GlossaryNode（术语组）为 GlossaryTerm 提供层级化的组织结构。可以把 GlossaryNode 看作文件夹，把 GlossaryTerm 看作其中的文件。

- 一个 GlossaryTerm 最多只能有一个父 GlossaryNode（通过 `glossaryTermInfo` 中的 `parentNode` 指定）
- GlossaryNode 可以同时包含 GlossaryTerm 和其他 GlossaryNode（形成嵌套层级）
- 根级别的术语（无父节点）显示在术语表顶部

### 应用于数据资产

GlossaryTerm 可通过 `glossaryTerms` aspect 应用于 DataHub 中的大多数实体类型：

**支持的实体：**

- dataset、schemaField（数据集列）
- dashboard、chart
- dataJob、dataFlow
- mlModel、mlFeature、mlFeatureTable、mlPrimaryKey
- notebook
- container
- dataProduct、application
- erModelRelationship、businessAttribute

当你将术语应用到某个实体时，DataHub 会创建：

1. 目标实体上的 `glossaryTerms` aspect，其中包含术语关联
2. 图中的一条 **TermedWith** 关系边
3. 一个可搜索的索引条目，便于你查找所有带有该术语的资产

### GraphQL API

GraphQL API 为 GlossaryTerm 提供丰富的查询与变更能力：

**查询：**

- 获取术语详情及其相关实体
- 以层级方式浏览术语
- 按名称或定义搜索术语
- 获取所有被某个术语标记的实体

**变更：**

- `createGlossaryTerm`：创建新术语
- `addTerms`、`addTerm`：将术语应用到实体
- `removeTerm`、`batchRemoveTerms`：从实体移除术语
- `updateParentNode`：将术语移动到不同的父组

详细示例参见 [GraphQL API 文档](https://docs.datahub.com/docs/api/graphql/overview.md。

### 与搜索和发现集成

GlossaryTerm 从多个方面提升可发现性：

1. **分面搜索（Faceted Search）**：用户可以按术语表术语筛选搜索结果
2. **术语传递（Term Propagation）**：当术语在数据集层级应用时，可以被下游资产继承
3. **相关实体**：术语页面展示所有被该术语标记的资产
4. **自动补全**：用户在搜索或标记资产时输入内容会提示相关术语

### 治理与访问控制

GlossaryTerm 支持通过 DataHub 的策略系统进行细粒度访问控制：

- **Manage Direct Glossary Children**：在特定术语组下直接创建/编辑/删除术语的权限
- **Manage All Glossary Children**：管理某术语组整个子树中任意术语的权限
- 标准实体策略（查看、编辑、删除）适用于单个术语

权限细节参见 [Business Glossary 文档](https://docs.datahub.com/docs/glossary/business-glossary.md。

## 值得注意的例外情况

### 术语名称 vs 显示名称

URN 标识符（`glossaryTermKey` 中的 `name`）与显示名称（`glossaryTermInfo` 中的 `name`）是分开的。最佳实践：

- **URN 名称**：使用稳定不变的标识符（例如 "clv-001"、"Classification.PII"）
- **显示名称**：使用便于阅读且可更新的标签（例如 "Customer Lifetime Value"、"Personally Identifiable Information"）

### 外部术语来源

当使用来自外部标准（FIBO、ISO、行业术语表）的术语时：

- 将 `termSource` 设为 "EXTERNAL"
- 用标准名称填充 `sourceRef`（例如 "FIBO"）
- 包含 `sourceUrl` 指向权威定义
- 考虑使用外部标准的标识符作为你的 URN 名称以保持一致

### 术语关系 vs 层级

不要混淆：

- **父子层级**（通过 `parentNode` → GlossaryNode）：用于浏览的组织结构
- **语义关系**（通过 `glossaryRelatedTerms`）：概念之间的含义联系

一个术语可以既有用于组织的 `parentNode`（例如术语 "Email" 位于节点 "PersonalInformation" 下），也有语义关系（例如 "Email" IsA "PII"，"Email" RelatedTo "Contact"）。

### GlossaryTerm 上的 Schema 元数据

GlossaryTerm 支持 `schemaMetadata` aspect，该 aspect 很少被使用，但有助于为术语本身定义结构化属性。当术语需要携带超出简单自定义属性之外的强类型属性时，可使用这一高级特性。

### 弃用行为

当 GlossaryTerm 被弃用时（通过 `deprecation` aspect）：

- 该术语仍保留在系统中，其关系也会被保留
- 被该术语标记的资产会保留这些关联
- UI 会显示弃用警告
- 该术语可能会从自动补全与建议中隐藏
- 建议创建新术语并迁移资产，而不是复用已弃用的术语名称


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](15-glossaryterm.md)。
