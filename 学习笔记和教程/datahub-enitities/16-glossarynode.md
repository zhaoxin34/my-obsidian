---
title: 术语表节点
entity: glossarynode
order: 16
source: https://docs.datahub.com/docs/generated/metamodel/entities/glossarynode.md
---

# 术语表节点

术语表节点（GlossaryNode）表示 DataHub 业务术语表中的一种层级分组或分类。GlossaryNodes 充当文件夹或容器，将 GlossaryTerms 组织成逻辑结构，从而让大型业务术语表更易于浏览和管理。

在实践中，GlossaryNodes 让你能够：

- 创建层级化分类以组织业务术语
- 构建多层级分类体系（例如 Finance > Revenue > Recurring Revenue）
- 对特定术语表板块建立归属与治理
- 在同一分类内的相关术语上一致地应用元数据
- 在分类层级上管理权限

例如，你可以创建一个名为 "Finance" 的 GlossaryNode，其中包含 "Revenue"、"Profit" 和 "EBITDA" 等术语，其下再嵌套一个包含 "SOX"、"GDPR" 和 "CCPA" 术语的 "Compliance" GlossaryNode。

## 标识

GlossaryNodes 由单个字段唯一标识：即它的 **name**。该名称在整个生命周期内充当该节点的持久标识符。

### URN 结构

GlossaryNode 的 URN（统一资源名称）遵循如下模式：

```
urn:li:glossaryNode:<node_name>
```

其中：

- `<node_name>`：节点的唯一字符串标识符。可以是可读的（例如 "Finance"），也可以是生成的 ID（例如 "fin-category-001" 或某个 UUID）。

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

1. **使用层级式记法**：为节点加上父分类前缀（例如 `Finance.Revenue`、`Classification.PII`），即使名称本身是扁平的，也能体现结构。
2. **保持一致**：选定一种命名约定（camelCase、点号记法等）并在整个术语表中统一使用。
3. **保持永久性**：节点名称即标识符，不应更改。请使用 `glossaryNodeInfo` 中的 `name` 字段作为显示名称。
4. **考虑深度**：虽然支持嵌套，但为保证可用性，层级深度应保持可控（通常 2-4 层）。

## 重要能力

### 核心节点信息（glossaryNodeInfo）

`glossaryNodeInfo` aspect 包含术语表节点的基本信息：

- **definition**（必填）：对该节点/分类所代表含义的描述。这有助于用户理解该节点内术语的目的与范围。
- **name**：在 UI 中展示的名称。它可以比 URN 标识符更友好（例如 "Financial Metrics" 与 "FinancialMetrics"）。
- **parentNode**：对另一个 GlossaryNode 的引用，作为层级中的父节点。这构成了 UI 中可见的树形结构。
- **id**：可选的标识字段，可存放外部引用或备用 ID。
- **customProperties**：针对你的组织的额外元数据键值对。

示例：

```python
{
  "name": "Financial Metrics",
  "definition": "Category for all financial and accounting-related business terms including revenue, costs, and profitability measures.",
  "parentNode": "urn:li:glossaryNode:Finance"
}
```

### 层级结构

GlossaryNodes 通过 `parentNode` 字段支持任意层级的嵌套，从而形成树形结构：

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
- 一个 GlossaryNode 可以同时包含 GlossaryTerms 和子 GlossaryNodes
- 位于根层级（无父节点）的节点显示在术语表层级的顶部
- 移动某个节点时，其所有后代节点会随之移动

### 归属与治理

GlossaryNodes 通过 `ownership` aspect 支持标准归属元数据。节点层级的归属可以代表：

- 维护该分类及其术语的 stewardship 责任
- 业务领域的主题专业能力
- 对该分类内术语质量与准确性的问责

归属对 GlossaryNodes 尤其有用，因为：

- 可以为所有者授予特殊权限（管理直接子级、管理全部子级）
- 归属可以向下级联到节点内的术语
- 它为术语表各板块建立了清晰的责任归属

### 文档与链接

GlossaryNodes 支持 `institutionalMemory` aspect，允许你：

- 链接到外部文档（Confluence 页面、wiki 等）
- 引用治理策略或标准
- 指向培训材料或风格指南
- 维护与该分类相关的重要链接的历史记录

这对于代表主要领域或专项计划的顶层节点尤其有用。

## 代码示例

### 创建术语表节点


**Python SDK：创建根层级 GlossaryNode**

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


**Python SDK：构建多层级术语表层级结构**

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



### 查询术语表节点


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




**GraphQL：查询根层级的 GlossaryNodes**

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

完整的 YAML 格式规范请参见 [Business Glossary Source](https://docs.datahub.com/docs/generated/ingestion/sources/business-glossary) 文档。



## 集成点

### 与 GlossaryTerm 的关系

GlossaryNodes 为 GlossaryTerms 提供组织结构。该关系通过以下方式建立：

- **GlossaryTerm → GlossaryNode**：术语的 `glossaryTermInfo.parentNode` 字段引用其所属节点
- **导航**：UI 将其渲染为可浏览的层级，用户可以展开节点查看其中包含的术语
- **搜索**：用户可以按术语表节点筛选，找出某个分类下的所有术语

可以这样理解这一关系：

- **GlossaryNode**：文件夹/目录（可以包含术语和其他节点）
- **GlossaryTerm**：文件（实际的业务定义）

### 父子关系

GlossaryNodes 通过自引用的父子关系构成树形结构：

- 子节点通过 `glossaryNodeInfo.parentNode` 引用其父节点
- 一个父节点可以拥有多个子节点（节点和术语均可）
- DataHub UI 在术语表浏览器中将其显示为可展开的树
- GraphQL 解析器提供用于遍历该层级的专用查询

**关键操作：**

- `getRootGlossaryNodes`：获取所有顶层节点（无父节点）
- `parentNodes`：向上导航以查找所有祖先节点
- `children`：向下导航以查找直接子节点
- 移动节点会更新其 `parentNode` 引用，并影响整个子树

### GraphQL API

GraphQL API 为 GlossaryNodes 提供专用操作：

**查询：**

- `glossaryNode(urn)`：获取指定节点及其子节点
- `getRootGlossaryNodes`：获取所有根层级节点
- `search(entity: "glossaryNode")`：按名称/定义搜索节点

**变更：**

- `createGlossaryNode`：创建新节点，可指定父节点
- `updateParentNode`：将节点移动到不同的父节点
- `updateName`：更新显示名称
- `updateDescription`：更新定义

**解析器：**

- `children`：获取直接子节点（节点与术语）
- `childrenCount`：该节点下子节点的数量
- `parentNodes`：从节点到根的祖先路径

关于 UI 操作，请参见[业务术语表文档](https://docs.datahub.com/docs/glossary/business-glossary)。

### 访问控制与权限

GlossaryNodes 通过专用的术语表权限支持细粒度访问控制：

#### 管理直接术语子级

拥有某节点该权限的用户可以：

- 在该节点下直接创建新术语和新节点
- 编辑该节点下直接包含的术语和节点
- 删除该节点下直接包含的术语和节点
- 不能影响孙节点及更深层的后代

**使用场景**：部门负责人管理其直接负责的分类结构

#### 管理全部术语子级

拥有某节点该权限的用户可以：

- 创建、编辑和删除整个子树中的任意术语或节点
- 管理任意深度的嵌套层级
- 完全控制该分类及其所有后代

**使用场景**：数据治理团队管理整个领域（例如所有与 PII 相关的术语）

#### 全局权限：管理术语表

拥有该平台级权限的用户可以：

- 管理整个术语表中的任意节点或术语
- 创建根层级节点
- 拥有完全的管理控制权

这些权限是分层校验的——如果你在父节点上拥有某项权限，则根据权限类型可能同时获得对子节点的权限。

### 与搜索和发现集成

虽然 GlossaryNodes 不会直接应用到数据资产上（那是 GlossaryTerms 的职责），但它们通过以下方式提升可发现性：

1. **分面导航**：用户可以浏览术语表层级以找到相关术语
2. **上下文**：节点结构提供语义分组，帮助用户理解术语之间的关系
3. **筛选**：搜索界面可以按术语所属节点筛选术语
4. **自动补全**：节点结构影响术语的提示与分组方式

## 值得注意的例外情况

### 节点名称与显示名称

与 GlossaryTerms 类似，URN 标识符（`glossaryNodeKey` 中的 `name`）与显示名称（`glossaryNodeInfo` 中的 `name`）是分开的：

- **URN 名称**：使用稳定且不改变的标识符（例如 "finance-001"、"DataGovernance"）
- **显示名称**：使用便于阅读、可随时更新的标签（例如 "Financial Metrics"、"Data Governance"）

这种分离让你可以在 UI 中重命名节点而不会破坏引用。

### 不允许循环引用

层级结构必须是树形结构（有向无环图）：

- 节点不能成为自己的祖先
- 禁止将某个节点移动到其后代节点之下
- DataHub 会校验层级结构以防止出现环

如果尝试创建循环引用，操作将因校验错误而失败。

### 根层级节点

没有父节点（`parentNode` 为 null 或未设置）的节点显示在术语表的根层级：

- 它们代表顶层分类
- 创建根层级节点可能需要更高权限
- 根节点通常代表主要领域或组织分支

### 删除包含子节点的节点

当前行为（可能变更）：

- **DataHub 可能要求节点为空才能删除**
- 你必须先删除或移动所有子节点与术语
- 这样可以避免误删大规模术语表板块

最佳实践：删除节点前始终先移动或重新分配其子节点，或使用能够处理整个子树的操作。

### 显示属性

GlossaryNodes 支持 `displayProperties` aspect（在较新版本中加入），提供额外的 UI 自定义能力：

- 为节点设置自定义图标或颜色
- 显示顺序提示
- UI 特定的渲染偏好

这是一项可选增强功能，适合希望在术语表中获得更多可视化控制的组织。

### 不能直接应用到资产

与 GlossaryTerms 不同，GlossaryNodes **不能**直接应用到数据资产：

- 你无法用 GlossaryNode 给数据集打标签
- 只有 GlossaryTerms 才能应用到数据集、列、仪表盘等
- 节点仅存在于术语表内部，用于组织目的

如果你需要用某个分类给资产打标签，请在该节点下创建一个 GlossaryTerm 并应用该术语。

### 移动节点会影响所有后代

当你将某个节点移动到新的父节点时：

- 所有子节点与术语都会随之移动
- 整个子树被重新定位
- 术语到其父节点的引用会自动维护
- 无需手动更新各个术语

这让重组变得高效，但也需要谨慎操作以避免非预期的移动。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](16-glossarynode.md)。
