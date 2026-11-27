---
title: 领域
entity: domain
source: https://docs.datahub.com/docs/generated/metamodel/entities/domain.md
---

# 领域

领域（Domain）是组织内部用于组织数据资产的、经策划的顶层类别。它们代表逻辑分组，通常与业务单元、部门或职能领域相对应。与非正式标签式的 tag 不同，领域提供了一种结构化的方式来组织资产，并支持集中式或分布式管理。一个数据资产在同一时间只能属于一个领域。

## 标识

领域由单个信息项标识：

- 唯一的领域 id：这是一个在 DataHub 内唯一标识该领域的字符串标识符。该 id 可以由 DataHub 自动生成，也可以在创建领域时手动指定。通过 UI 或 API 创建领域而未指定 id 时，DataHub 会自动生成一个基于 UUID 的标识符。若需要编程访问或希望使用便于人类阅读的标识符，可以指定自定义 id，例如 "marketing"、"engineering" 或 "finance"。

领域标识符的示例为 `urn:li:domain:marketing`。

对于自动生成的领域，URN 可能形如 `urn:li:domain:6289fccc-4af2-4cbb-96ed-051e7d1de93c`。

## 重要能力

### 领域属性

领域属性存储在 `domainProperties` aspect 中，包含关于该领域的核心元数据：

- **名称**：领域的展示名称（例如 "Marketing"、"Platform Engineering"）
- **描述**：可选的详细描述，说明该领域代表什么
- **父领域**：领域可以是层级化的，子领域嵌套在父领域之下。这支持诸如 "Engineering" > "Data Engineering" > "Data Platform" 的组织结构
- **创建时间戳**：关于领域创建时间的审计信息

下面是创建带属性领域的示例：

**Python SDK：创建领域**

```python
# Inlined from /metadata-ingestion/examples/library/domain_create.py
import os

from datahub.emitter.mce_builder import make_domain_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DomainPropertiesClass

# Get DataHub connection details from environment
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")

domain_urn = make_domain_urn("marketing")
domain_properties_aspect = DomainPropertiesClass(
    name="Marketing", description="Entities related to the marketing department"
)

event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
    entityUrn=domain_urn,
    aspect=domain_properties_aspect,
)

rest_emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
rest_emitter.emit(event)
print(f"Created domain {domain_urn}")

```

### 嵌套的领域层级

领域通过父子关系支持层级化组织，从而可以表示多层的组织结构。例如，你可以有一个顶层 "Engineering" 领域，其下包含 "Data Engineering"、"ML Engineering" 和 "Infrastructure Engineering" 等子领域。

**Python SDK：创建嵌套领域**

```python
# Inlined from /metadata-ingestion/examples/library/domain_create_nested.py
import os

from datahub.emitter.mce_builder import make_domain_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DomainPropertiesClass

domain_urn = make_domain_urn("verticals")
domain_properties_aspect = DomainPropertiesClass(
    name="Verticals",
    description="Entities related to the verticals sub-domain",
    parentDomain="urn:li:domain:marketing",
)

event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
    entityUrn=domain_urn,
    aspect=domain_properties_aspect,
)

# Get DataHub connection details from environment
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")

rest_emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
rest_emitter.emit(event)
print(f"Created domain {domain_urn}")

```

### 所有权

与 DataHub 中其他实体一样，领域可以通过 `ownership` aspect 分配所有者。领域所有者通常负责：

- 管理哪些资产属于该领域
- 维护领域元数据与文档
- 治理领域内的数据质量标准
- 作为领域相关问题的对接人

领域的所有权类型与其他实体遵循相同的模式，包括 `TECHNICAL_OWNER`、`BUSINESS_OWNER`、`DATA_STEWARD` 等。

**Python SDK：为领域添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/domain_add_owner.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)
from datahub.metadata.urns import CorpUserUrn, DomainUrn

graph = DataHubGraph(DatahubClientConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

domain_urn = DomainUrn(id="marketing")

# Get existing ownership
existing_ownership = graph.get_aspect(str(domain_urn), OwnershipClass)
owner_list = (
    list(existing_ownership.owners)
    if existing_ownership and existing_ownership.owners
    else []
)

# Add new owner with the TECHNICAL_OWNER type
owner_list.append(
    OwnerClass(owner=str(CorpUserUrn("jdoe")), type=OwnershipTypeClass.TECHNICAL_OWNER)
)

# Emit ownership
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=str(domain_urn), aspect=OwnershipClass(owners=owner_list)
    )
)

```

### 文档与链接

领域通过 `institutionalMemory` aspect 支持文档，可链接到外部资源，例如：

- 描述该领域目的与范围的 Confluence 页面
- 关于数据治理策略的文档
- 团队 wiki 或手册
- 该领域的新人入门指南

**Python SDK：为领域添加文档链接**

```python
# Inlined from /metadata-ingestion/examples/library/domain_add_documentation.py
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    AuditStampClass,
    DomainPropertiesClass,
    InstitutionalMemoryClass,
    InstitutionalMemoryMetadataClass,
)
from datahub.metadata.urns import CorpUserUrn, DomainUrn

graph = DataHubGraph(DatahubClientConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

domain_urn = DomainUrn(id="marketing")

# Get existing properties
existing_properties = graph.get_aspect(str(domain_urn), DomainPropertiesClass)

# Update description
if existing_properties:
    existing_properties.description = (
        "The Marketing domain contains all data assets related to marketing operations, "
        "campaigns, customer analytics, and brand management."
    )
    properties = existing_properties
else:
    properties = DomainPropertiesClass(
        name="Marketing",
        description=(
            "The Marketing domain contains all data assets related to marketing operations, "
            "campaigns, customer analytics, and brand management."
        ),
    )

# Emit properties
emitter.emit_mcp(
    MetadataChangeProposalWrapper(entityUrn=str(domain_urn), aspect=properties)
)

# Get existing institutional memory
existing_memory = graph.get_aspect(str(domain_urn), InstitutionalMemoryClass)
links_list = (
    list(existing_memory.elements)
    if existing_memory and existing_memory.elements
    else []
)

# Add new links
audit_stamp = AuditStampClass(
    time=int(time.time() * 1000), actor=str(CorpUserUrn("datahub"))
)

links_list.append(
    InstitutionalMemoryMetadataClass(
        url="https://wiki.company.com/domains/marketing",
        description="Marketing Domain Wiki - Overview and Guidelines",
        createStamp=audit_stamp,
    )
)

links_list.append(
    InstitutionalMemoryMetadataClass(
        url="https://confluence.company.com/marketing-data-governance",
        description="Marketing Data Governance Policies",
        createStamp=audit_stamp,
    )
)

# Emit institutional memory
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=str(domain_urn), aspect=InstitutionalMemoryClass(elements=links_list)
    )
)

```

### 将资产分配到领域

领域的首要用途是组织数据资产。资产通过资产实体上的 `domains` aspect 分配到领域（而非在领域实体上设置），从而在资产与领域之间建立关系。

**Python SDK：将数据集分配到领域**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_domain.py
from datahub.metadata.urns import DatasetUrn, DomainUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

dataset = client.entities.get(DatasetUrn(platform="snowflake", name="example_dataset"))

# If you don't know the domain urn, you can look it up:
# domain_urn = client.resolve.domain(name="marketing")

# NOTE: This will overwrite the existing domain
dataset.set_domain(DomainUrn(id="marketing"))

client.entities.update(dataset)

```

将资产分配到领域后，它将：

- 出现在 UI 中该领域的实体列表里
- 可以在搜索结果中按领域筛选
- 在资产的详情页上显示领域徽标

### 查询领域

你可以使用 REST API 和 GraphQL API 查询领域及其关联实体。

#### 通过 REST API 获取领域信息

**REST API：按 URN 获取领域**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Adomain%3Amarketing' \
  -H 'Authorization: Bearer <token>'
```

这将返回领域实体及其所有 aspect，包括：

- `domainKey`：唯一标识符
- `domainProperties`：名称、描述、父领域
- `ownership`：领域的所有者
- `institutionalMemory`：链接与文档

#### 列出领域中的资产

领域维护着与所有被分配资产的关系。你可以查询这些关系来查找某个领域内的全部实体。

**REST API：查找某领域内的所有资产**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3Adomain%3Amarketing&types=AssociatedWith' \
  -H 'Authorization: Bearer <token>'
```

这将返回所有已与指定领域关联的实体。

**Python SDK：从数据集查询领域**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_query_domain.py
from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient.from_env()

dataset = client.entities.get(
    DatasetUrn(platform="hive", name="fct_users_created", env="PROD")
)

# Print the dataset domain
print(dataset.domain)

```

### 按领域搜索与筛选

资产被分配到领域后，你可以：

- 使用领域过滤器筛选搜索结果
- 在特定领域内搜索以查找资产
- 将领域作为复杂搜索查询的一部分

资产上的 `domains` 字段已建立索引并可搜索，因此按领域成员关系筛选大量数据集非常高效。

**Python SDK：搜索某领域内的实体**

```python
# Inlined from /metadata-ingestion/examples/library/search_filter_by_domain.py
from datahub.sdk import DataHubClient
from datahub.sdk.search_filters import FilterDsl as F

# search for all assets in the marketing domain
client = DataHubClient.from_env()
results = client.search.get_urns(filter=F.domain("urn:li:domain:marketing"))

```

## 集成点

领域与若干关键的 DataHub 功能集成：

### 与其他实体的关系

领域与以下对象存在关系：

- **数据资产**：数据集、仪表板、图表、ML 模型及其他数据资产可通过 `domains` aspect 分配到领域
- **父领域**：领域可具有父子关系，从而形成层级化的组织结构
- **用户与用户组**：领域拥有所有者（通过 `ownership` aspect），负责管理该领域

### GraphQL 解析器

领域实体在 `datahub-graphql-core` 模块中由若干 GraphQL 解析器支持：

- `CreateDomainResolver`：创建新领域
- `SetDomainResolver`：将资产分配到领域
- `UnsetDomainResolver`：从领域移除资产
- `ListDomainsResolver`：列出所有可用领域
- `DeleteDomainResolver`：删除领域
- `DomainEntitiesResolver`：获取某领域内的全部实体
- `ParentDomainsResolver`：解析领域的父级层级
- `BatchSetDomainResolver`：一次性将多个资产分配到领域
- `MoveDomainResolver`：将领域移动到不同的父领域

### 使用模式

常见使用模式包括：

1. **数据网格组织**：使用领域表示不同的数据产品团队或业务域
2. **部门结构**：按公司部门（财务、市场、工程）组织资产
3. **产品线**：按产品或业务线对资产分组
4. **合规边界**：按合规要求或数据驻留规则区分资产
5. **嵌套结构**：创建诸如 区域 > 国家 > 业务单元 的层级化组织

### 与摄取的集成

在元数据摄取过程中，可以通过摄取配方中的 `domain` 配置自动分配领域，从而实现：

- 基于命名模式批量分配领域
- 在发现过程中自动分配领域
- 在相似资产之间保持一致的领域标记

详细的摄取配置示例请参见 [Domains 功能指南](/docs/domains)。

## 值得注意的例外

### 单领域归属

与支持多重归属的 tag 和术语表术语不同，一个资产在同一时间只能属于一个领域。若将资产分配到新领域，它会自动从原领域移除。

### 摄取过程中的领域解析

在摄取配方中使用裸领域名称（如 "Marketing"）时，DataHub 会尝试将其解析为已置备的领域。解析过程依次检查：

1. 是否存在 URN 为 `urn:li:domain:Marketing` 的领域
2. 是否存在名称为 "Marketing" 的领域

若解析失败，摄取将失败以确保数据完整性。为避免解析问题，可在摄取配置中使用完全限定的领域 URN。

### 层级方面的注意事项

按层级组织领域时：

- 资产被分配到最具体的（叶子）领域，而非父领域
- 父领域不会自动继承子领域的资产
- 领域层级主要用于 UI 中的组织清晰度
- 删除父领域不会自动删除或重新分配子领域

### 权限

管理领域需要 "Manage Domains" 平台权限，其中包括：

- 创建新领域
- 修改领域属性
- 将资产分配到领域
- 删除领域

单项资产分配也可通过特定实体类型上的 "Edit Domain" 元数据策略进行控制。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/domain.md)。
