---
title: 术语表节点
entity: glossarynode
order: 16
source: https://docs.datahub.com/docs/generated/metamodel/entities/glossarynode.md
---

# 术语表节点

术语表节点（GlossaryNode）代表 DataHub 业务术语表中的层级分组或分类。GlossaryNode 充当文件夹或容器，将 GlossaryTerm 组织成合乎逻辑的结构，使大型业务术语表更易于浏览和管理。

在实际使用中，GlossaryNode 让你可以：

- 创建层级分类以组织业务术语
- 构建多级分类体系（例如 Finance > Revenue > Recurring Revenue）
- 对特定术语表分区建立归属与治理机制
- 在同一分类内的相关术语上一致地应用元数据
- 在分类层级上管理权限

例如，你可以创建一个名为 "Finance" 的 GlossaryNode，其中包含 "Revenue"、"Profit"、"EBITDA" 等术语，并在其下嵌套一个 "Compliance" GlossaryNode，其中包含 "SOX"、"GDPR"、"CCPA" 术语。

## 标识（Identity）

GlossaryNode 由单个字段唯一标识：其 **name**。该名称在整个生命周期中充当该节点的持久标识符。

### URN 结构

GlossaryNode 的 URN（统一资源名称）遵循如下模式：

```
urn:li:glossaryNode:<node_name>
```

其中：

- `<node_name>`：节点的唯一字符串标识符。它可以是人类可读的（例如 "Finance"），也可以是生成的 ID（例如 "fin-category-001" 或 UUID）。

### 示例

```
# Simple node name
urn:li:glossaryNode:Finance

# Hierarchical naming convention (common pattern)
urn:li:glossaryNode:Finance.Revenue
urn:li:glossaryNode:Classification
urn:li:glossaryNode:Classification.DataSensitivity

# UUID-based identifier
urn:li:glossaryNode:41516e31-0acb-fd90-76ff-fc2c98d2d1a3

# Descriptive identifier
urn:li:glossaryNode:PersonalInformation
```

### 节点命名的最佳实践

1. **使用层级化命名**：为节点加上父分类前缀（例如 `Finance.Revenue`、`Classification.PII`），即使名称是扁平的也能表达结构。
2. **保持一致**：选择一种命名约定（camelCase、点号记法等）并在整个术语表中统一使用。
3. **保持稳定**：节点名称即标识符，不应更改。显示名称请使用 `glossaryNodeInfo` 中的 `name` 字段。
4. **考虑深度**：虽然支持嵌套，但为了可用性，层级应保持适度（通常 2-4 层）。

## 重要能力

### 核心节点信息（glossaryNodeInfo）

`glossaryNodeInfo` aspect 包含术语表节点的基本信息：

- **definition**（必填）：对该节点/分类所代表含义的描述。这有助于用户理解该节点内术语的目的与范围。
- **name**：在 UI 中显示的名称。它可以比 URN 标识符更友好（例如 "Financial Metrics" 对比 "FinancialMetrics"）。
- **parentNode**：对另一个 GlossaryNode 的引用，作为层级中的父节点。这构成 UI 中可见的树形结构。
- **id**：可选的标识符字段，可用于存储外部引用或备用 ID。
- **customProperties**：针对你所在组织的额外元数据键值对。

示例：

```python
{
  "name": "Financial Metrics",
  "definition": "Category for all financial and accounting-related business terms including revenue, costs, and profitability measures.",
  "parentNode": "urn:li:glossaryNode:Finance"
}
```

### 层级结构

GlossaryNode 通过 `parentNode` 字段支持任意层级的嵌套，从而形成树形结构：

```
GlossaryNode: DataGovernance
  ├── GlossaryNode: Classification
  │   ├── GlossaryTerm: Public
  │   ├── GlossaryTerm: Internal
  │   └── GlossaryTerm: Confidential
  │
  ├── GlossaryNode: PersonalInformation
  │   ├── GlossaryNode: DirectIdentifiers
  │   │   ├── GlossaryTerm: Email
  │   │   └── GlossaryTerm: SSN
  │   └── GlossaryNode: IndirectIdentifiers
  │       ├── GlossaryTerm: IPAddress
  │       └── GlossaryTerm: DeviceID
  │
  └── GlossaryNode: Compliance
      ├── GlossaryTerm: GDPR
      └── GlossaryTerm: CCPA
```

关键特征：

- 一个 GlossaryNode 最多只能有一个父节点（单继承）
- 一个 GlossaryNode 可以同时包含 GlossaryTerm 和子 GlossaryNode
- 根级别的节点（无父节点）显示在术语表层级的顶部
- 移动某个节点会自动移动其所有后代

### 归属与治理

GlossaryNode 通过 `ownership` aspect 支持标准归属元数据。节点层级的归属可以体现：

- 维护该分类及其术语的管理责任
- 业务领域的主题专家身份
- 该分类内术语质量与准确性的问责

归属对 GlossaryNode 尤其有用，因为：

- 可以为所有者授予特殊权限（Manage Direct Children、Manage All Children）
- 归属可以向下传递到节点内的术语
- 它为术语表分区建立了清晰的责任归属

### 文档与链接

GlossaryNode 支持 `institutionalMemory` aspect，允许你：

- 链接到外部文档（Confluence 页面、wiki 等）
- 引用治理策略或标准
- 指向培训材料或风格指南
- 维护与该分类相关的重要链接的历史记录

这对于代表主要领域或计划的顶层节点尤其有用。

## 代码示例

### 创建 GlossaryNode


**Python SDK：创建根级别的 GlossaryNode**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_node_create.py
from datahub.sdk import DataHubClient, GlossaryNode

client = DataHubClient.from_env()

# Top-level glossary node
node = GlossaryNode(
    id="7f3d2c1a",
    display_name="Financial Metrics",
    definition="Category for all financial and accounting-related business terms including revenue, costs, and profitability measures.",
)

# Child node nested under Finance
child_node = GlossaryNode(
    id="4b5e6f7a",
    display_name="Revenue Metrics",
    definition="Metrics related to revenue recognition and reporting.",
    parent_node=node,
)

client.entities.upsert(node)
client.entities.upsert(child_node)

```




**Python SDK：创建带父节点的嵌套 GlossaryNode**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_node_create_nested.py
from datahub.sdk import DataHubClient, GlossaryNode

client = DataHubClient.from_env()

parent_node = GlossaryNode(
    id="7f3d2c1a",
    display_name="Finance",
    definition="Top-level category for financial metrics and terms.",
)

child_node = GlossaryNode(
    id="4b5e6f7a",
    display_name="Revenue Metrics",
    definition="Metrics related to revenue recognition and reporting.",
    parent_node=parent_node,
)

client.entities.upsert(parent_node)
client.entities.upsert(child_node)

```



### 管理层级


**Python SDK：构建多级术语表层级**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_term_create_hierarchy.py
from datahub.sdk import DataHubClient, GlossaryNode
from datahub.sdk.glossary_term import GlossaryTerm

client = DataHubClient.from_env()

# Create multi-level hierarchy:
# DataGovernance
#   ├── Classification
#   │   ├── Public (term)
#   │   └── Confidential (term)
#   └── PersonalInformation
#       ├── Email (term)
#       └── SSN (term)

root = GlossaryNode(
    id="8b9c0d1e",
    display_name="Data Governance",
    definition="Top-level governance structure for data classification and management.",
)

classification = GlossaryNode(
    id="2f3a4b5c",
    display_name="Classification",
    definition="Data classification categories.",
    parent_node=root,
)

pii = GlossaryNode(
    id="6d7e8f90",
    display_name="Personal Information",
    definition="Personal and sensitive data categories.",
    parent_node=root,
)

terms = [
    GlossaryTerm(
        id="abcdef12",
        display_name="Public",
        definition="Publicly available data with no restrictions.",
        parent_node=classification,
    ),
    GlossaryTerm(
        id="34567890",
        display_name="Confidential",
        definition="Restricted access data for internal use only.",
        parent_node=classification,
    ),
    GlossaryTerm(
        id="abcd1234",
        display_name="Email Address",
        definition="Email addresses that can identify individuals.",
        parent_node=pii,
    ),
    GlossaryTerm(
        id="5678abcd",
        display_name="Social Security Number",
        definition="Social Security Numbers - highly sensitive personal identifiers.",
        parent_node=pii,
    ),
]

for entity in [root, classification, pii, *terms]:
    client.entities.upsert(entity)

```



### 添加归属


**Python SDK：为 GlossaryNode 添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/glossary_node_add_owner.py
from datahub.metadata.urns import CorpUserUrn
from datahub.sdk import DataHubClient, GlossaryNodeUrn

client = DataHubClient.from_env()

node = client.entities.get(GlossaryNodeUrn("7f3d2c1a"))
node.add_owner(CorpUserUrn("jdoe"))
client.entities.upsert(node)

```



### 查询 GlossaryNode


**REST API：按 URN 获取 GlossaryNode**

```bash
# Fetch a GlossaryNode entity
curl -X GET 'http://localhost:8080/entities/urn%3Ali%3AglossaryNode%3AFinance' \
  -H 'Authorization: Bearer <token>'

# Response includes all aspects:
# - glossaryNodeKey (identity)
# - glossaryNodeInfo (definition, name, parentNode, etc.)
# - ownership (who owns this node)
# - institutionalMemory (links to documentation)
# - etc.
```




**GraphQL：查询根级别的 GlossaryNode**

```graphql
query GetRootGlossaryNodes {
  getRootGlossaryNodes {
    nodes {
      urn
      properties {
        name
        definition
      }
      ownership {
        owners {
          owner {
            ... on CorpUser {
              urn
              username
            }
          }
        }
      }
    }
  }
}
```




**GraphQL：查询 GlossaryNode 的子节点**

```graphql
query GetGlossaryNodeChildren {
  glossaryNode(urn: "urn:li:glossaryNode:Finance") {
    urn
    properties {
      name
      definition
    }
    children {
      count
      relationships {
        entity {
          ... on GlossaryNode {
            urn
            properties {
              name
            }
          }
          ... on GlossaryTerm {
            urn
            properties {
              name
              definition
            }
          }
        }
      }
    }
  }
}
```




### 批量操作


**YAML 摄取：从业务术语表文件创建节点层级**

```yaml
# business_glossary.yml
version: "1"
source: MyOrganization
owners:
  users:
    - datahub
nodes:
  - name: DataGovernance
    description: Top-level governance structure
    nodes:
      - name: Classification
        description: Data classification categories
        terms:
          - name: Public
            description: Publicly available data
          - name: Internal
            description: Internal use only
          - name: Confidential
            description: Restricted access data

      - name: PersonalInformation
        description: Personal and sensitive data categories
        nodes:
          - name: DirectIdentifiers
            description: Direct personal identifiers
            terms:
              - name: Email
                description: Email addresses
              - name: SSN
                description: Social Security Numbers

          - name: IndirectIdentifiers
            description: Indirect identifiers
            terms:
              - name: IPAddress
                description: Internet Protocol addresses
              - name: DeviceID
                description: Device identifiers
# Ingest using the DataHub CLI:
# datahub ingest -c business_glossary.yml
```

完整的 YAML 格式规范请参见 [Business Glossary Source](https://docs.datahub.com/docs/generated/ingestion/sources/business-glossary.md 文档。



## 集成点

### 与 GlossaryTerm 的关系

GlossaryNode 为 GlossaryTerm 提供组织结构。该关系通过以下方式建立：

- **GlossaryTerm → GlossaryNode**：术语的 `glossaryTermInfo.parentNode` 字段引用其所属节点
- **导航**：UI 将其呈现为可浏览的层级，用户可以展开节点查看包含的术语
- **搜索**：用户可以按术语表节点筛选，找到某个分类下的所有术语

可以将该关系理解为：

- **GlossaryNode**：文件夹/目录（可以包含术语和其他节点）
- **GlossaryTerm**：文件（实际的业务定义）

### 父子关系

GlossaryNode 通过自引用的父子关系构成树形结构：

- 子节点通过 `glossaryNodeInfo.parentNode` 引用其父节点
- 父节点可以拥有许多子节点（既有节点也有术语）
- DataHub UI 在术语表浏览器中将其显示为可展开的树
- GraphQL resolver 提供用于遍历层级的专用查询

**关键操作：**

- `getRootGlossaryNodes`：获取所有顶层节点（无父节点）
- `parentNodes`：向上导航，找到所有祖先
- `children`：向下导航，找到直接子节点
- 移动节点会更新其 `parentNode` 引用并影响整个子树

### GraphQL API

GraphQL API 为 GlossaryNode 提供专用操作：

**查询：**

- `glossaryNode(urn)`：获取特定节点及其子节点
- `getRootGlossaryNodes`：获取所有根级别节点
- `search(entity: "glossaryNode")`：按名称/定义搜索节点

**变更：**

- `createGlossaryNode`：创建新节点，可指定父节点
- `updateParentNode`：将节点移动到不同的父节点
- `updateName`：更新显示名称
- `updateDescription`：更新定义

**Resolver：**

- `children`：获取直接子节点（节点与术语）
- `childrenCount`：该节点下的子节点数量
- `parentNodes`：从节点到根的祖先路径

UI 操作参见 [Business Glossary 文档](https://docs.datahub.com/docs/glossary/business-glossary.md。

### 访问控制与权限

GlossaryNode 支持通过专门的术语表权限进行细粒度访问控制：

#### Manage Direct Glossary Children

拥有某节点该权限的用户可以：

- 在该节点下直接创建新的术语与节点
- 编辑该节点下直接的术语与节点
- 删除该节点下直接的术语与节点
- 不能影响孙节点或更深的后代

**使用场景**：部门负责人管理其直接负责的分类结构

#### Manage All Glossary Children

拥有某节点该权限的用户可以：

- 创建、编辑、删除整个子树中的任意术语或节点
- 管理任意深度的嵌套层级
- 对该分类及其所有后代拥有完全控制权

**使用场景**：数据治理团队管理整个领域（例如所有与 PII 相关的术语）

#### 全局权限：Manage Glossaries

拥有该平台级权限的用户可以：

- 管理整个术语表中的任意节点或术语
- 创建根级别的节点
- 拥有完全的管理控制权

这些权限是按层级检查的——如果你在父节点上拥有权限，根据权限类型不同，它可能同时授予你对子节点的权限。

### 与搜索和发现集成

虽然 GlossaryNode 不会直接应用到数据资产上（那是 GlossaryTerm 的职责），但它们通过以下方式提升可发现性：

1. **分面导航**：用户可以浏览术语表层级找到相关术语
2. **上下文**：节点结构提供了语义分组，帮助用户理解术语之间的关系
3. **筛选**：搜索界面可以按术语所属节点筛选术语
4. **自动补全**：节点结构会影响术语建议与分组方式

## 值得注意的例外情况

### 节点名称 vs 显示名称

与 GlossaryTerm 类似，URN 标识符（`glossaryNodeKey` 中的 `name`）与显示名称（`glossaryNodeInfo` 中的 `name`）是分开的：

- **URN 名称**：使用稳定不变的标识符（例如 "finance-001"、"DataGovernance"）
- **显示名称**：使用便于阅读且可更新的标签（例如 "Financial Metrics"、"Data Governance"）

这种分离让你可以在 UI 中重命名节点而不破坏引用。

### 不允许循环引用

层级必须是树形结构（有向无环图）：

- 节点不能是它自己的祖先
- 将节点移动到其后代之下会被阻止
- DataHub 会校验层级以防止出现环

如果你尝试创建循环引用，操作将因校验错误而失败。

### 根级别节点

没有父节点（`parentNode` 为 null 或未设置）的节点显示在术语表的根级别：

- 它们代表顶层分类
- 创建根级别节点可能需要更高的权限
- 根节点通常代表主要领域或组织分支

### 删除包含子节点的节点

当前行为（可能发生变化）：

- **DataHub 可能要求节点为空才能删除**
- 你必须先删除或移动所有子节点与术语
- 这是为了防止大规模术语表分区被意外丢失

最佳实践：删除节点前始终先移动或重新分配其子节点，或使用能处理整个子树的批量操作。

### 显示属性

GlossaryNode 支持 `displayProperties` aspect（在较新版本中添加），可提供额外的 UI 定制能力：

- 为节点设置自定义图标或颜色
- 显示顺序提示
- UI 特定的渲染偏好

这是可选增强功能，适合希望对术语表有更多视觉控制的组织。

### 不能直接应用到资产

与 GlossaryTerm 不同，GlossaryNode **不能**直接应用到数据资产：

- 你无法用 GlossaryNode 标记数据集
- 只有 GlossaryTerm 才能应用到数据集、列、仪表板等
- 节点仅用于术语表内部的组织目的

如果你需要用某个分类标记资产，请在该节点下创建一个 GlossaryTerm 并应用该术语。

### 移动节点会影响所有后代

当你将节点移动到新的父节点下时：

- 所有子节点与术语都会随之移动
- 整个子树被重新定位
- 术语到其父节点的引用会自动维护
- 无需手动更新单个术语

这让重组变得高效，但需要谨慎以避免非预期的移动。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](16-glossarynode.md)。
