---
title: 数据平台实例
entity: dataplatforminstance
order: 62
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataplatforminstance.md
---

# Data Platform Instance

Data Platform Instance（数据平台实例）表示某个数据平台的一次具体部署或实例。[dataPlatform](56-dataplatform.md) 表示一种技术类型（如 MySQL、Snowflake、BigQuery），而 dataPlatformInstance 则表示该平台的某个特定运行实例（如 "production-mysql-cluster"、"dev-snowflake-account"、"analytics-bigquery-project"）。 表示一种技术类型（如 MySQL、Snowflake、BigQuery），而 dataPlatformInstance 则表示该平台的某个特定运行实例（如 "production-mysql-cluster"、"dev-snowflake-account"、"analytics-bigquery-project"）。

对于在不同环境、区域或组织单元中运行同一平台技术多个实例的组织，该实体至关重要。它使 DataHub 能够区分来自不同平台实例的资产，并提供了一种组织和管理平台级元数据与凭据的方式。

## 标识

Data Platform Instance 由两个组成部分标识：

- **Platform**：数据平台技术的 URN（如 `urn:li:dataPlatform:snowflake`）
- **Instance**：该特定实例的唯一字符串标识符（如 "prod-us-west-2"、"dev-cluster-01"）

完整 URN 遵循如下模式：

```
urn:li:dataPlatformInstance:(urn:li:dataPlatform:<platform>,<instance_id>)
```

### 示例

- `urn:li:dataPlatformInstance:(urn:li:dataPlatform:mysql,production-mysql-01)`
  - 一个生产环境的 MySQL 数据库集群
- `urn:li:dataPlatformInstance:(urn:li:dataPlatform:snowflake,acme-prod-account)`
  - 一个生产环境的 Snowflake 账户
- `urn:li:dataPlatformInstance:(urn:li:dataPlatform:bigquery,analytics-project)`
  - 一个用于分析分析的 BigQuery 项目
- `urn:li:dataPlatformInstance:(urn:li:dataPlatform:iceberg,data-lake-warehouse)`
  - 一个 Iceberg warehouse 实例

## 重要能力

### 平台实例属性

`dataPlatformInstanceProperties` aspect 包含关于该平台实例的描述性元数据：

- **name**：便于展示的实例名称（可搜索，支持自动补全）
- **description**：说明该实例的用途、使用方式或特征的文档
- **customProperties**：用于存放额外自定义元数据的键值对
- **externalUrl**：指向该实例外部文档或管理控制台的链接

该 aspect 有助于用户理解每个平台实例代表什么以及应如何使用。

```python
# Inlined from /metadata-ingestion/examples/library/platform_instance_create.py
# metadata-ingestion/examples/library/platform_instance_create.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataPlatformInstancePropertiesClass

# Create the platform instance URN
platform_instance_urn = builder.make_dataplatform_instance_urn(
    platform="mysql", instance="production-mysql-cluster"
)

# Define properties for the platform instance
platform_properties = DataPlatformInstancePropertiesClass(
    name="Production MySQL Cluster",
    description="Primary MySQL database cluster serving production workloads in US West region",
    customProperties={
        "region": "us-west-2",
        "environment": "production",
        "cluster_size": "3-node",
        "version": "8.0.35",
    },
    externalUrl="https://cloud.mysql.com/console/clusters/prod-cluster",
)

# Create metadata change proposal
platform_instance_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=platform_properties,
)

# Emit metadata to DataHub
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
emitter.emit_mcp(platform_instance_mcp)

print(f"Created platform instance: {platform_instance_urn}")

```

### Iceberg Warehouse 配置

DataHub 可以充当 Iceberg catalog，通过平台实例管理 Iceberg 表。`icebergWarehouseInfo` aspect 存储管理 Iceberg warehouse 所需的配置：

- **dataRoot**：表存储根位置的 S3 路径
- **clientId**：AWS access key ID secret 的 URN 引用
- **clientSecret**：AWS secret access key secret 的 URN 引用
- **region**：warehouse 所在的 AWS 区域
- **role**：用于凭据发放（credential vending）的 IAM role ARN
- **tempCredentialExpirationSeconds**：临时凭据的过期时间
- **env**：环境/fabric 类型（PROD、DEV、QA 等）

这使 DataHub 能够以 REST catalog 的方式管理 Iceberg 表，负责数据访问的元数据操作与凭据发放。

`datahub iceberg` CLI 提供了创建、更新、列出和删除 Iceberg warehouse 的命令。详情请参阅 [Iceberg 集成文档](https://datahubproject.io/docs/generated/ingestion/sources/iceberg)。。

### 所有权与标签

与其他 DataHub 实体一样，平台实例支持：

- **ownership**：跟踪谁拥有或管理该平台实例
- **globalTags**：应用标签进行分类（如 "production"、"pci-compliant"、"deprecated"）
- **institutionalMemory**：添加指向运行手册、文档或相关资源的链接

这些 aspect 使平台实例具备治理能力与可发现性。

```python
# Inlined from /metadata-ingestion/examples/library/platform_instance_add_metadata.py
# metadata-ingestion/examples/library/platform_instance_add_metadata.py
import time

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    GlobalTagsClass,
    InstitutionalMemoryClass,
    InstitutionalMemoryMetadataClass,
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
    TagAssociationClass,
)

# Create the platform instance URN
platform_instance_urn = builder.make_dataplatform_instance_urn(
    platform="snowflake", instance="acme-prod-account"
)

# Add ownership
owners = [
    OwnerClass(
        owner=builder.make_user_urn("data-platform-team"),
        type=OwnershipTypeClass.TECHNICAL_OWNER,
    ),
    OwnerClass(
        owner=builder.make_user_urn("john.doe"),
        type=OwnershipTypeClass.DATAOWNER,
    ),
]

ownership_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=OwnershipClass(owners=owners),
)

# Add tags
tags = GlobalTagsClass(
    tags=[
        TagAssociationClass(tag=builder.make_tag_urn("production")),
        TagAssociationClass(tag=builder.make_tag_urn("pci-compliant")),
        TagAssociationClass(tag=builder.make_tag_urn("tier-1")),
    ]
)

tags_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=tags,
)

# Add institutional memory (links)
links = InstitutionalMemoryClass(
    elements=[
        InstitutionalMemoryMetadataClass(
            url="https://wiki.company.com/snowflake-prod-runbook",
            description="Production Snowflake Runbook",
            createStamp=AuditStampClass(
                time=int(time.time() * 1000), actor=builder.make_user_urn("datahub")
            ),
        ),
        InstitutionalMemoryMetadataClass(
            url="https://wiki.company.com/snowflake-access-guide",
            description="How to request access to production Snowflake",
            createStamp=AuditStampClass(
                time=int(time.time() * 1000), actor=builder.make_user_urn("datahub")
            ),
        ),
    ]
)

links_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=links,
)

# Emit all metadata changes
emitter = DatahubRestEmitter("http://localhost:8080")
emitter.emit_mcp(ownership_mcp)
emitter.emit_mcp(tags_mcp)
emitter.emit_mcp(links_mcp)

print(f"Added ownership, tags, and links to: {platform_instance_urn}")

```

### 状态与废弃

平台实例可以标记状态信息：

- **status**：指示该实例是活跃的还是已被移除
- **deprecation**：在实例被逐步下线时将其标记为已废弃，可附带可选的退役日期与迁移说明

这有助于向用户传达平台实例的生命周期信息。

## 代码示例

### 创建平台实例

创建平台实例最常见的方式是通过摄取框架：当源配置中指定了 `platform_instance` 配置时，它会自动创建平台实例。不过你也可以通过编程方式创建：

```python
# Inlined from /metadata-ingestion/examples/library/platform_instance_create.py
# metadata-ingestion/examples/library/platform_instance_create.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataPlatformInstancePropertiesClass

# Create the platform instance URN
platform_instance_urn = builder.make_dataplatform_instance_urn(
    platform="mysql", instance="production-mysql-cluster"
)

# Define properties for the platform instance
platform_properties = DataPlatformInstancePropertiesClass(
    name="Production MySQL Cluster",
    description="Primary MySQL database cluster serving production workloads in US West region",
    customProperties={
        "region": "us-west-2",
        "environment": "production",
        "cluster_size": "3-node",
        "version": "8.0.35",
    },
    externalUrl="https://cloud.mysql.com/console/clusters/prod-cluster",
)

# Create metadata change proposal
platform_instance_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=platform_properties,
)

# Emit metadata to DataHub
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
emitter.emit_mcp(platform_instance_mcp)

print(f"Created platform instance: {platform_instance_urn}")

```

### 将平台实例附加到数据集

在摄取元数据时，`dataPlatformInstance` aspect 会将数据集链接到其平台实例。这通常由摄取连接器完成，也可以手动完成：

```python
# Inlined from /metadata-ingestion/examples/library/dataset_attach_platform_instance.py
from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient.from_env()

dataset = client.entities.get(
    DatasetUrn(
        platform="mysql",
        name="production-mysql-cluster.ecommerce.customers",
        env="PROD",
    )
)

dataset._set_platform_instance(platform="mysql", instance="production-mysql-cluster")

client.entities.update(dataset)

print("Attached platform instance 'production-mysql-cluster'")
print(f"to dataset {dataset.urn}")

```

### 查询平台实例

你可以使用 REST API 或 GraphQL 获取平台实例信息：

```python
# Inlined from /metadata-ingestion/examples/library/platform_instance_query.py
# metadata-ingestion/examples/library/platform_instance_query.py
import json
import os

import datahub.emitter.mce_builder as builder
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

# Create a DataHub graph client
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
config = DatahubClientConfig(server=gms_server, token=token)
graph = DataHubGraph(config)

# Create the platform instance URN
platform_instance_urn = builder.make_dataplatform_instance_urn(
    platform="mysql", instance="production-mysql-cluster"
)

# Check if the platform instance exists
if graph.exists(platform_instance_urn):
    print(f"Platform instance exists: {platform_instance_urn}\n")

    # Get the full entity with all aspects
    entity = graph.get_entity_semityped(platform_instance_urn)

    # Access the key aspect to get platform and instance ID
    if "dataPlatformInstanceKey" in entity:
        key_aspect = entity["dataPlatformInstanceKey"]
        print(f"Platform: {key_aspect.platform}")
        print(f"Instance ID: {key_aspect.instance}\n")

    # Access properties
    if "dataPlatformInstanceProperties" in entity:
        props = entity["dataPlatformInstanceProperties"]
        print(f"Name: {props.name}")
        print(f"Description: {props.description}")
        if props.customProperties:
            print("Custom Properties:")
            for key, value in props.customProperties.items():
                print(f"  {key}: {value}")
        if props.externalUrl:
            print(f"External URL: {props.externalUrl}")
        print()

    # Access ownership
    if "ownership" in entity:
        ownership = entity["ownership"]
        print("Owners:")
        for owner in ownership.owners:
            print(f"  - {owner.owner} ({owner.type})")
        print()

    # Access tags
    if "globalTags" in entity:
        global_tags = entity["globalTags"]
        print("Tags:")
        for tag_association in global_tags.tags:
            print(f"  - {tag_association.tag}")
        print()

    # Access institutional memory (links)
    if "institutionalMemory" in entity:
        institutional_memory = entity["institutionalMemory"]
        print("Links:")
        for element in institutional_memory.elements:
            print(f"  - {element.description}: {element.url}")
        print()

    # Get raw aspects using REST API for complete data
    raw_entity = graph.get_entity_raw(
        entity_urn=platform_instance_urn,
        aspects=[
            "dataPlatformInstanceKey",
            "dataPlatformInstanceProperties",
            "ownership",
            "globalTags",
            "institutionalMemory",
            "deprecation",
            "status",
        ],
    )

    print("Raw entity data:")
    print(json.dumps(raw_entity, indent=2))

else:
    print(f"Platform instance does not exist: {platform_instance_urn}")

```

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AdataPlatformInstance%3A(urn%3Ali%3AdataPlatform%3Amysql%2Cproduction-cluster)'
```

```graphql
query {
  search(
    input: {
      type: DATA_PLATFORM_INSTANCE
      query: "dataPlatform:iceberg"
      start: 0
      count: 10
    }
  ) {
    searchResults {
      entity {
        ... on DataPlatformInstance {
          urn
          platform {
            name
          }
          instanceId
          properties {
            name
            description
          }
        }
      }
    }
  }
}
```

## 集成点

### 与其他实体的关系

许多实体通过 `dataPlatformInstance` aspect 引用平台实例：

- **Datasets**：将数据集与所属平台实例关联，从而支持按实例筛选与组织
- **Charts**：BI 工具的图表可以关联到其所查询的特定实例
- **Dashboards**：仪表板与平台实例关联
- **Data Jobs**：ETL/管道作业引用其运行所在的平台实例
- **Data Flows**：管道定义可以与平台实例关联
- **ML Models**：模型可以跟踪其训练所用的平台实例
- **Containers**：数据库 schema、文件夹及其他容器引用其实例
- **Assertions**：数据质量断言可以限定到特定实例

这在所有数据资产之上创建了一个强大的组织维度。

### 摄取框架集成

大多数 DataHub 摄取源都支持 `platform_instance` 配置参数。指定后，连接器会自动将该平台实例附加到所有被摄取的实体上：

```yaml
source:
  type: mysql
  config:
    host_port: "mysql.prod.company.com:3306"
    platform_instance: "production-mysql-cluster"
    # ... other config
```

随后该平台实例被用于：

- 区分同一平台不同实例上的资产
- 在 UI 中支持实例级别的筛选
- 支持多租户或多区域部署
- 按部署环境组织元数据

### 在数据集命名中的使用

对于支持多实例的平台，平台实例通常会被纳入数据集名称以确保唯一性。例如：

- 不含实例：`urn:li:dataset:(urn:li:dataPlatform:mysql,db.schema.table,PROD)`
- 含有实例：`urn:li:dataset:(urn:li:dataPlatform:mysql,prod-cluster.db.schema.table,PROD)`

这确保了不同实例上同名表具有各自不同的 URN。

### Iceberg Catalog 集成

当 DataHub 作为 Iceberg REST catalog 提供服务时，平台实例即代表 Iceberg warehouse。每个 warehouse 配置包含：

- 用于 S3 访问的存储凭据
- 用于凭据发放的 IAM role 配置
- 对象存储中的 warehouse 根位置
- 环境标识

DataHub 管理这些 warehouse 内 Iceberg 表的生命周期，负责：

- 表的创建与元数据存储
- 为读写访问生成临时凭据
- 表的发现与血缘追踪
- Schema 演进

有关将 Iceberg warehouse 作为平台实例进行管理的命令，请参阅 `datahub iceberg` CLI。

## 重要例外

### 内部使用 vs. 外部使用

在 DataHub 的实体注册表中，Data Platform Instance 被归类为 "internal" 实体，意味着它们主要用于组织与元数据管理，而非作为主要的发现目标。用户通常与数据集、仪表板等资产交互，而不是直接浏览平台实例。

不过，平台实例是可搜索的，在排查资产组织方式或平台级配置时，可以在 DataHub UI 中查看。

### 平台实例 vs. 环境

平台实例不同于实体 URN 中使用的环境/fabric 概念（PROD、DEV、QA 等）。环境是许多实体标识符的必需组成部分，而平台实例是可选的，提供了更细粒度的组织维度。

单个平台实例通常对应一个环境，但同一环境内可以有多个实例（例如 "prod-us-west"、"prod-us-east"、"prod-eu-central" 同属 PROD 环境）。

### 自动创建实例

平台实例通常在摄取过程中被隐式创建，而非事先显式定义。当某个摄取源引用了一个并不存在的平台实例时，DataHub 会自动创建一个基础的平台实例实体。随后你可以为其补充属性、所有权和标签等额外元数据。

### 有限的 GraphQL 搜索

与数据集、仪表板等主要实体不同，平台实例在 GraphQL 中的搜索功能有限。支持使用 `type: DATA_PLATFORM_INSTANCE` 的 `search` 查询，但某些高级搜索功能可能尚未完全实现。REST API 访问可提供完整功能。

### 不可变的键组成部分

平台实例一旦创建，其键组成部分（platform URN 与 instance ID）便不可更改。如果需要重命名某个实例，必须创建新的平台实例实体并从旧实体迁移引用。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](62-dataplatforminstance.md)。。
