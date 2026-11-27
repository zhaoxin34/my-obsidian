---
title: 应用
entity: application
order: 35
source: https://docs.datahub.com/docs/generated/metamodel/entities/application.md
---

# 应用

应用实体表示在你的数据生态中生产或消费数据资产的软件应用、服务或系统。应用提供了一种组织和归组相关数据资产的方式，按创建、转换或使用这些资产的软件进行归类，从而更好地理解数据溯源与使用模式。

## 标识

应用由一部分信息标识：

- 应用的唯一标识符（`id`）：这是一个在你的 DataHub 实例内唯一标识该应用的字符串。它可以是任何有意义的标识符，例如应用名、服务名或系统标识符。常见模式包括使用 kebab-case 名称（例如 `customer-analytics-service`）、全限定服务名（例如 `com.company.analytics.customer-service`），或简单的描述性名称（例如 `tableau-reports`）。

应用标识符的示例为 `urn:li:application:customer-analytics-service`。

与需要平台和环境限定符的数据集不同，应用采用更简单的 URN 结构，仅包含应用标识符，因而能灵活表示组织内各类软件应用。

## 重要能力

### 应用属性

应用的核心元数据存储在 `applicationProperties` aspect 中。该 aspect 包含：

- **名称**：应用的可读展示名称（例如 "Customer Analytics Service"、"Data Pipeline Orchestrator"）
- **描述**：说明应用做什么、其用途以及如何使用的文档
- **自定义属性**：用于存储应用特有附加元数据的键值对
- **外部引用**：指向外部文档、源代码仓库、仪表板或其他相关资源的链接

下面的代码片段展示了如何创建带有基本属性的应用。


**Python SDK：创建应用**

```python
# Inlined from /metadata-ingestion/examples/library/application_create.py
# metadata-ingestion/examples/library/application_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import ApplicationPropertiesClass


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

application_urn = make_application_urn("customer-analytics-service")

application_properties = ApplicationPropertiesClass(
    name="Customer Analytics Service",
    description="A microservice that processes customer events and generates analytics insights for the marketing team",
    customProperties={
        "team": "data-platform",
        "language": "python",
        "repository": "https://github.com/company/customer-analytics",
    },
    externalUrl="https://wiki.company.com/customer-analytics",
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=application_properties,
)
emitter.emit(metadata_event)

print(f"Created application: {application_urn}")

```

### 更新应用属性

你可以通过发出新的 `applicationProperties` aspect 来更新已有应用的属性。SDK 会将新属性与已有属性合并。


**Python SDK：更新应用属性**

```python
# Inlined from /metadata-ingestion/examples/library/application_update_properties.py
# metadata-ingestion/examples/library/application_update_properties.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import ApplicationPropertiesClass


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

updated_properties = ApplicationPropertiesClass(
    name="Customer Analytics Service v2",
    description="Updated: A microservice that processes customer events and generates real-time analytics insights. Now includes ML-based predictions.",
    customProperties={
        "team": "data-platform",
        "language": "python",
        "repository": "https://github.com/company/customer-analytics",
        "version": "2.0.0",
        "deployment": "kubernetes",
    },
    externalUrl="https://wiki.company.com/customer-analytics-v2",
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=updated_properties,
)
emitter.emit(metadata_event)

print(f"Updated properties for application: {application_urn}")

```

### 标签与术语表术语

与其他实体一样，应用可以附加标签或术语。请阅读[这篇博客](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)，以了解标签与术语之间的区别，从而明确何时该使用哪一个。

#### 为应用添加标签

标签通过 `globalTags` aspect 添加到应用。标签适用于按技术栈、团队归属、关键程度或其他组织维度对应用进行分类。


**Python SDK：为应用添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/application_add_tag.py
# metadata-ingestion/examples/library/application_add_tag.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import GlobalTagsClass, TagAssociationClass


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


def make_tag_urn(tag_name: str) -> str:
    """Create a DataHub tag URN."""
    return f"urn:li:tag:{tag_name}"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

tag_to_add = make_tag_urn("production")

tags = GlobalTagsClass(
    tags=[
        TagAssociationClass(tag=tag_to_add),
    ]
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=tags,
)
emitter.emit(metadata_event)

print(f"Added tag {tag_to_add} to application {application_urn}")

```

#### 为应用添加术语表术语

术语通过 `glossaryTerms` aspect 添加。术语适用于将应用与业务概念、数据域或标准化术语关联起来。


**Python SDK：为应用添加术语**

```python
# Inlined from /metadata-ingestion/examples/library/application_add_term.py
# metadata-ingestion/examples/library/application_add_term.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    GlossaryTermAssociationClass,
    GlossaryTermsClass,
)


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


def make_term_urn(term_name: str) -> str:
    """Create a DataHub glossary term URN."""
    return f"urn:li:glossaryTerm:{term_name}"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

term_to_add = make_term_urn("CustomerData")

terms = GlossaryTermsClass(
    terms=[
        GlossaryTermAssociationClass(urn=term_to_add),
    ],
    auditStamp=AuditStampClass(time=0, actor="urn:li:corpuser:datahub"),
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=terms,
)
emitter.emit(metadata_event)

print(f"Added term {term_to_add} to application {application_urn}")

```

### 所有权

所有权通过 `ownership` aspect 关联到应用。所有者可以有若干不同类型，如 `TECHNICAL_OWNER`、`BUSINESS_OWNER`、`DATA_STEWARD` 等。完整的所有权类型列表及其含义请参见 [OwnershipType.pdl](https://raw.githubusercontent.com/datahub-project/datahub/master/metadata-models/src/main/pegasus/com/linkedin/common/OwnershipType.pdl)。

下面的脚本展示了如何使用底层 Python SDK 为应用添加所有者。


**Python SDK：为应用添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/application_add_owner.py
# metadata-ingestion/examples/library/application_add_owner.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


def make_user_urn(username: str) -> str:
    """Create a DataHub user URN."""
    return f"urn:li:corpuser:{username}"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

owner_to_add = make_user_urn("jdoe")

ownership = OwnershipClass(
    owners=[
        OwnerClass(
            owner=owner_to_add,
            type=OwnershipTypeClass.TECHNICAL_OWNER,
        )
    ]
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=ownership,
)
emitter.emit(metadata_event)

print(f"Added owner {owner_to_add} to application {application_urn}")

```

### 域

应用可以与域关联，以按业务领域、部门或数据域进行组织。域通过 `domains` aspect 设置。


**Python SDK：为应用添加域**

```python
# Inlined from /metadata-ingestion/examples/library/application_add_domain.py
# metadata-ingestion/examples/library/application_add_domain.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DomainsClass


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


def make_domain_urn(domain_id: str) -> str:
    """Create a DataHub domain URN."""
    return f"urn:li:domain:{domain_id}"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

domain_to_add = make_domain_urn("marketing")

domains = DomainsClass(domains=[domain_to_add])

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=application_urn,
    aspect=domains,
)
emitter.emit(metadata_event)

print(f"Added domain {domain_to_add} to application {application_urn}")

```

### 应用资产（成员关系）

应用最强大的能力之一是能够与数据资产关联，从而在应用与该应用生产或消费的数据集、仪表板、图表或其他实体之间建立关系。

`applications` aspect 附加在数据资产上（而非应用实体本身），用以标明哪些应用与这些资产相关联。这种双向关系带来以下能力：

- 查找与特定应用关联的所有数据资产
- 发现哪些应用生产或消费某个数据集
- 跨应用边界追踪数据血缘
- 理解应用数据足迹的完整范围


**Python SDK：将资产与应用关联**

```python
# Inlined from /metadata-ingestion/examples/library/application_add_assets.py
# metadata-ingestion/examples/library/application_add_assets.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import ApplicationsClass


def make_application_urn(application_id: str) -> str:
    """Create a DataHub application URN."""
    return f"urn:li:application:{application_id}"


def make_dataset_urn(platform: str, name: str, env: str) -> str:
    """Create a DataHub dataset URN."""
    return f"urn:li:dataset:(urn:li:dataPlatform:{platform},{name},{env})"


emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

application_urn = make_application_urn("customer-analytics-service")

dataset_urns = [
    make_dataset_urn("snowflake", "prod.marketing.customer_events", "PROD"),
    make_dataset_urn("snowflake", "prod.marketing.customer_profiles", "PROD"),
    make_dataset_urn("kafka", "customer-events-stream", "PROD"),
]

for dataset_urn in dataset_urns:
    applications_aspect = ApplicationsClass(applications=[application_urn])

    metadata_event = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=applications_aspect,
    )
    emitter.emit(metadata_event)

    print(f"Associated {dataset_urn} with application {application_urn}")

print(f"\nSuccessfully associated {len(dataset_urns)} assets with application")

```

### 查询应用

可以使用 Python SDK 查询应用，以获取全部 aspect 与元数据。


**Python SDK：获取应用实体**

```python
# Inlined from /metadata-ingestion/examples/library/application_query_rest_api.py
# metadata-ingestion/examples/library/application_query_rest_api.py
import json

from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import ApplicationPropertiesClass
from datahub.metadata.urns import ApplicationUrn

graph = get_default_graph()

application_urn = ApplicationUrn("customer-analytics-service")

props = graph.get_aspect(
    entity_urn=str(application_urn), aspect_type=ApplicationPropertiesClass
)
if props is None:
    raise SystemExit(f"Application not found: {application_urn}")

print(f"Application: {application_urn}")
print(f"Application Name: {props.name}")
print(f"Description: {props.description}")
if props.customProperties:
    print(f"Custom Properties: {json.dumps(props.customProperties, indent=2)}")

```

或者使用 curl：

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Aapplication%3Acustomer-analytics-service'
```

你还可以使用搜索 API 查询与应用关联的所有资产：


**查找与应用关联的所有资产**

```bash
# Using the search API to find entities with a specific application
curl -X POST 'http://localhost:8080/entities?action=search' \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "*",
    "entity": "dataset",
    "start": 0,
    "count": 10,
    "filter": {
      "or": [
        {
          "and": [
            {
              "field": "applications",
              "value": "urn:li:application:customer-analytics-service",
              "condition": "EQUAL"
            }
          ]
        }
      ]
    }
  }'
```

## 集成点

### 与其他实体的关系

应用可以与 DataHub 中多种类型的实体关联：

1. **数据集**：最常见的用法是把应用与其生产或消费的数据集关联。这有助于追踪数据溯源，并理解哪些应用位于特定数据集的上游或下游。
2. **仪表板与图表**：生成报表或可视化的应用可以关联到仪表板和图表实体，明确哪个应用产生了哪些分析产物。
3. **数据作业与数据流**：ETL 管道和数据处理应用可以关联到它们所编排或执行的 `dataJob` 与 `dataFlow` 实体。
4. **ML 模型与 ML 特征**：机器学习应用可以关联到其训练或用于推理的模型与特征。
5. **域**：应用可以归属于业务域，有助于按组织结构或业务职能进行组织。
6. **所有权**：应用拥有所有者（技术所有者、业务所有者），由其负责维护和运营。

### 常见使用模式

#### 模式 1：服务到数据集的映射

最常见的模式是把微服务或应用映射到它们所生产的数据集：

```
Customer Service Application → produces → customer_events dataset
                             → produces → customer_profiles dataset
                             → consumes → user_authentication dataset
```

该模式通常在摄取期间这样实现：

- 为每个数据集添加 `applications` aspect
- 在该 aspect 中引用应用 URN

#### 模式 2：报表应用的组织

商业智能与报表工具可以按应用来组织其仪表板和图表：

```
Tableau Application → contains → Sales Dashboard
                    → contains → Marketing Dashboard
Power BI Application → contains → Finance Dashboard
```

#### 模式 3：数据管道分组

数据管道编排系统可以把相关作业归到某个应用之下：

```
Airflow Application → orchestrates → daily_etl_pipeline
                    → orchestrates → hourly_refresh_pipeline
                    → orchestrates → weekly_aggregation_pipeline
```

### GraphQL API

应用与 DataHub 的 GraphQL API 完整集成，支持：

- 通过 `createApplication` mutation 创建应用
- 更新应用属性
- 通过 `deleteApplication` mutation 删除应用
- 通过 `batchSetApplication` mutation 批量设置应用资产
- 查询应用及其关系

应用的 GraphQL 解析器位于 `datahub-graphql-core/src/main/java/com/linkedin/datahub/graphql/resolvers/application/`。

## 值得注意的例外

### 应用与数据产品

应用与数据产品相关但属于不同概念：

- **应用**表示生产或消费数据的软件系统。它们是代表代码与基础设施的技术实体。
- **数据产品**表示为消费而打包的、经过治理的数据资产。它们是代表数据作为产品的业务实体。

一个应用可能生产多个数据产品，而一个数据产品也可能由多个应用协同产出。

### 应用与平台

不要将应用与数据平台混淆：

- **数据平台**（例如 Snowflake、BigQuery、Kafka）表示承载数据资产的技术或系统。
- **应用**表示创建或使用这些数据资产的具体软件应用。

例如：

- 平台：`snowflake`
- 数据集：`urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)`
- 应用：`urn:li:application:customer-analytics-service`（写入该 Snowflake 表）

### 基于 UUID 的标识符

应用 ID 可以是任意字符串，支持但不要求使用 UUID。如果你在通过 ApplicationService 创建应用时未提供 ID，则会自动生成一个 UUID。不过，为便于发现与维护，通常更倾向于使用有意义的、可读的标识符。

### 未来增强方向

应用实体相对较新，未来可能会扩展包含：

- 服务网格集成以实现自动发现
- API 规范与端点文档
- 部署与版本追踪
- 资源消耗指标
- 依赖关系图可视化

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](35-application.md)。
