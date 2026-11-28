---
title: 版本集
entity: versionset
order: 27
source: https://docs.datahub.com/docs/generated/metamodel/entities/versionset.md
---

# VersionSet

VersionSet 实体是 DataHub 中的核心元数据模型实体，用于将其他实体的相关版本归组在一起。版本集主要用于管理那些具有明确版本并随时间演进的版本化实体，例如 ML 模型、数据集及其他资产。它们提供了一种结构化的方式来组织、追踪同一逻辑资产的不同版本并在其间导航。

## 标识

版本集由两部分信息标识：

- **ID**：版本集的唯一标识符，通常由平台和资产名称通过 GUID 生成。这确保了版本集在 DataHub 中所有版本集之间的唯一性。
- **实体类型**：在此版本集中归组的实体类型（例如 `mlModel`、`dataset`）。单个版本集中的所有实体必须属于同一类型，从而保证类型安全与一致性。

版本集标识符的示例为 `urn:li:versionSet:(abc123def456,mlModel)`。

URN 结构遵循以下模式：`urn:li:versionSet:(<id>,<entityType>)`，其中：

- `<id>` 是唯一的标识符字符串，通常是由平台和资产名称生成的 GUID
- `<entityType>` 是被版本化的实体类型（例如 `mlModel`、`dataset`）

## 重要能力

### 版本集属性

版本集通过 `versionSetProperties` 方面维护有关版本化实体集合的元数据。该方面包含：

#### 最新版本追踪

版本集会自动追踪当前哪个实体是最新版本。这一信息存储在 `latest` 字段中，无需查询所有版本即可快速引用最近的版本。

#### 版本编排方案

版本集支持不同的版本编排方案，以适配各种版本策略：

- **LEXICOGRAPHIC_STRING**：版本按字符串进行字典序排序。这适用于语义化版本（例如 "1.0.0"、"1.1.0"、"2.0.0"）或基于日期的版本。
- **ALPHANUMERIC_GENERATED_BY_DATAHUB**：DataHub 使用 8 字符的字母数字字符串自动生成版本标识符。当源系统未提供自己的版本机制时，这很有用。

版本编排方案一旦设定即保持静态，并决定版本在集合内的排序方式。

#### 自定义属性

与其他 DataHub 实体一样，版本集支持自定义属性，用于存储特定于你的使用场景的额外元数据。


**Python SDK：创建带属性的版本集**

```python
# Inlined from /metadata-ingestion/examples/library/version_set_add_properties.py
# metadata-ingestion/examples/library/version_set_add_properties.py
"""
Create a version set with custom properties and metadata.

This example demonstrates how to create a version set with rich metadata
including custom properties to track additional information.
"""

from datahub.emitter.mce_builder import datahub_guid
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    VersioningSchemeClass,
    VersionSetPropertiesClass,
)

server = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=server)

# Generate a unique ID for the version set
guid_dict = {"platform": "tensorflow", "name": "image-classifier"}
version_set_id = datahub_guid(guid_dict)

# Create the version set URN for an ML model
version_set_urn = f"urn:li:versionSet:({version_set_id},mlModel)"

# Define the latest version (this should be an existing ML model)
latest_model_urn = (
    "urn:li:mlModel:(urn:li:dataPlatform:tensorflow,image-classifier-v3,PROD)"
)

# Create version set properties with custom metadata
version_set_properties = VersionSetPropertiesClass(
    latest=latest_model_urn,
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
    customProperties={
        "model_type": "image_classification",
        "framework": "tensorflow",
        "architecture": "resnet50",
        "dataset": "imagenet",
        "owner_team": "ml-platform",
        "cost_center": "ML-001",
    },
)

# Emit the version set with properties
version_set_mcp = MetadataChangeProposalWrapper(
    entityUrn=version_set_urn,
    aspect=version_set_properties,
)
emitter.emit(version_set_mcp)

print(f"Created version set: {version_set_urn}")
print(f"Latest version: {latest_model_urn}")
print("Custom properties:")
for key, value in version_set_properties.customProperties.items():
    print(f"  {key}: {value}")

```



### 将实体链接到版本集

实体通过版本化实体上的 `versionProperties` 方面链接到版本集。该方面包含：

- **versionSet**：该实体所属版本集的 URN
- **version**：版本标签，应在版本集内保持唯一
- **sortId**：用于按版本编排方案对版本进行排序的标识符
- **aliases**：备选的版本标识符（例如 "latest"、"stable"、"v1"）
- **comment**：关于该版本含义的可选说明
- **isLatest**：指示是否为最新版本的布尔标志（自动维护）
- **timestamps**：来自源系统以及 DataHub 中各自的创建时间戳


**Python SDK：将实体链接到版本集**

```python
# Inlined from /metadata-ingestion/examples/library/version_set_link_entity.py
# metadata-ingestion/examples/library/version_set_link_entity.py
"""
Link an existing entity to an existing version set.

This example shows how to add a new version of an entity to an existing
version set, with proper version tracking and metadata.
"""

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    MetadataAttributionClass,
    VersioningSchemeClass,
    VersionPropertiesClass,
    VersionSetPropertiesClass,
    VersionTagClass,
)

server = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=server)

# Define the version set and the new model version to link
version_set_urn = "urn:li:versionSet:(abc123def456,mlModel)"
new_model_urn = "urn:li:mlModel:(urn:li:dataPlatform:sagemaker,my-model-v2,PROD)"

# Update the version set to mark this as the latest
version_set_properties = VersionSetPropertiesClass(
    latest=new_model_urn,
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
)

version_set_mcp = MetadataChangeProposalWrapper(
    entityUrn=version_set_urn,
    aspect=version_set_properties,
)
emitter.emit(version_set_mcp)

# Create version properties for the new model
version_properties = VersionPropertiesClass(
    versionSet=version_set_urn,
    version=VersionTagClass(
        versionTag="2.0.0",
        metadataAttribution=MetadataAttributionClass(
            time=1675209600000,
            actor="urn:li:corpuser:ml-engineer",
        ),
    ),
    sortId="2.0.0",
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
    comment="Major update with improved accuracy",
    aliases=[
        VersionTagClass(versionTag="v2"),
        VersionTagClass(versionTag="latest"),
    ],
    sourceCreatedTimestamp=AuditStampClass(
        time=1675209600000,
        actor="urn:li:corpuser:ml-engineer",
    ),
    metadataCreatedTimestamp=AuditStampClass(
        time=1675209600000,
        actor="urn:li:corpuser:datahub",
    ),
)

# Emit the version properties for the new model
model_version_mcp = MetadataChangeProposalWrapper(
    entityUrn=new_model_urn,
    aspect=version_properties,
)
emitter.emit(model_version_mcp)

print(f"Linked {new_model_urn} to version set {version_set_urn}")
print("Version: 2.0.0")

```



### 创建新的版本集

创建新的版本集时，通常将第一个版本化实体链接到它。通过将实体链接到新的版本集 URN，即可隐式创建该版本集。


**Python SDK：通过链接第一个实体来创建版本集**

```python
# Inlined from /metadata-ingestion/examples/library/version_set_create.py
# metadata-ingestion/examples/library/version_set_create.py
"""
Create a new version set by linking the first versioned entity.

This example demonstrates creating a version set for an ML model,
establishing the first version in the set.
"""

import os

from datahub.emitter.mce_builder import datahub_guid
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    MetadataAttributionClass,
    VersioningSchemeClass,
    VersionPropertiesClass,
    VersionSetPropertiesClass,
    VersionTagClass,
)

server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=server, token=token)

# Define the ML model URN that we want to version
model_urn = "urn:li:mlModel:(urn:li:dataPlatform:sagemaker,my-model-v1,PROD)"

# Generate a unique ID for the version set based on the model name
guid_dict = {"platform": "sagemaker", "name": "my-model"}
version_set_id = datahub_guid(guid_dict)

# Create the version set URN
version_set_urn = f"urn:li:versionSet:({version_set_id},mlModel)"

# Create version set properties aspect
version_set_properties = VersionSetPropertiesClass(
    latest=model_urn,
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
    customProperties={
        "model_family": "recommendation",
        "framework": "tensorflow",
    },
)

# Emit the version set properties
version_set_mcp = MetadataChangeProposalWrapper(
    entityUrn=version_set_urn,
    aspect=version_set_properties,
)
emitter.emit(version_set_mcp)

# Create version properties for the ML model
version_properties = VersionPropertiesClass(
    versionSet=version_set_urn,
    version=VersionTagClass(
        versionTag="1.0.0",
        metadataAttribution=MetadataAttributionClass(
            time=1672531200000,
            actor="urn:li:corpuser:datahub",
        ),
    ),
    sortId="1.0.0",
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
    comment="Initial production release",
    aliases=[
        VersionTagClass(versionTag="v1"),
        VersionTagClass(versionTag="stable"),
    ],
    metadataCreatedTimestamp=AuditStampClass(
        time=1672531200000,
        actor="urn:li:corpuser:datahub",
    ),
)

# Emit the version properties for the model
model_version_mcp = MetadataChangeProposalWrapper(
    entityUrn=model_urn,
    aspect=version_properties,
)
emitter.emit(model_version_mcp)

print(f"Created version set: {version_set_urn}")
print(f"Linked first version: {model_urn} with version 1.0.0")

```



### 管理多个版本

随着你为某项资产创建新版本，你会将每一个版本以不同的版本标签链接到同一个版本集。版本集会依据版本编排方案自动将 `latest` 指针更新到最近的版本。


**Python SDK：将多个版本链接到一个版本集**

```python
# Inlined from /metadata-ingestion/examples/library/version_set_link_multiple_versions.py
# metadata-ingestion/examples/library/version_set_link_multiple_versions.py
"""
Link multiple versions of an entity to a version set.

This example demonstrates creating a complete version history for an ML model,
showing how to manage multiple versions with semantic versioning.
"""

from typing import TypedDict

from datahub.emitter.mce_builder import datahub_guid
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    MetadataAttributionClass,
    VersioningSchemeClass,
    VersionPropertiesClass,
    VersionSetPropertiesClass,
    VersionTagClass,
)

server = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=server)


class VersionInfo(TypedDict):
    urn: str
    version: str
    sortId: str
    comment: str
    timestamp: int
    aliases: list[str]
    actor: str


# Generate version set URN
guid_dict = {"platform": "pytorch", "name": "sentiment-analyzer"}
version_set_id = datahub_guid(guid_dict)
version_set_urn = f"urn:li:versionSet:({version_set_id},mlModel)"

# Define the model versions we want to link
versions: list[VersionInfo] = [
    {
        "urn": "urn:li:mlModel:(urn:li:dataPlatform:pytorch,sentiment-analyzer-v1,PROD)",
        "version": "1.0.0",
        "sortId": "1.0.0",
        "comment": "Initial release with basic sentiment analysis",
        "timestamp": 1672531200000,
        "aliases": ["v1"],
        "actor": "urn:li:corpuser:data-scientist",
    },
    {
        "urn": "urn:li:mlModel:(urn:li:dataPlatform:pytorch,sentiment-analyzer-v1.1,PROD)",
        "version": "1.1.0",
        "sortId": "1.1.0",
        "comment": "Minor improvements to accuracy",
        "timestamp": 1675209600000,
        "aliases": ["v1.1"],
        "actor": "urn:li:corpuser:data-scientist",
    },
    {
        "urn": "urn:li:mlModel:(urn:li:dataPlatform:pytorch,sentiment-analyzer-v2,PROD)",
        "version": "2.0.0",
        "sortId": "2.0.0",
        "comment": "Major update with multi-language support",
        "timestamp": 1677628800000,
        "aliases": ["v2", "latest", "production"],
        "actor": "urn:li:corpuser:ml-engineer",
    },
]

# Link each version to the version set
for i, version_info in enumerate(versions):
    is_latest = i == len(versions) - 1

    # Create version properties for each model
    version_properties = VersionPropertiesClass(
        versionSet=version_set_urn,
        version=VersionTagClass(
            versionTag=version_info["version"],
            metadataAttribution=MetadataAttributionClass(
                time=version_info["timestamp"],
                actor=version_info["actor"],
            ),
        ),
        sortId=version_info["sortId"],
        versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
        comment=version_info["comment"],
        aliases=[
            VersionTagClass(versionTag=alias) for alias in version_info["aliases"]
        ],
        sourceCreatedTimestamp=AuditStampClass(
            time=version_info["timestamp"],
            actor=version_info["actor"],
        ),
        metadataCreatedTimestamp=AuditStampClass(
            time=version_info["timestamp"],
            actor="urn:li:corpuser:datahub",
        ),
    )

    # Emit version properties
    model_version_mcp = MetadataChangeProposalWrapper(
        entityUrn=version_info["urn"],
        aspect=version_properties,
    )
    emitter.emit(model_version_mcp)

    print(f"Linked version {version_info['version']}: {version_info['urn']}")

# Update version set to point to the latest version
version_set_properties = VersionSetPropertiesClass(
    latest=versions[-1]["urn"],
    versioningScheme=VersioningSchemeClass.LEXICOGRAPHIC_STRING,
    customProperties={
        "model_type": "sentiment_analysis",
        "language_support": "multi-language",
        "framework": "pytorch",
    },
)

version_set_mcp = MetadataChangeProposalWrapper(
    entityUrn=version_set_urn,
    aspect=version_set_properties,
)
emitter.emit(version_set_mcp)

print(f"\nVersion set created: {version_set_urn}")
print(f"Total versions: {len(versions)}")
print(f"Latest version: {versions[-1]['version']}")

```



### 查询版本集与版本化实体

你可以查询版本集以获取所有版本的信息或查找特定版本。


**Python SDK：查询版本集及其版本**

```python
# Inlined from /metadata-ingestion/examples/library/version_set_query.py
# metadata-ingestion/examples/library/version_set_query.py
"""
Query a version set to retrieve information about versions.

This example demonstrates how to fetch version set metadata and query
all versions using both the Python SDK and GraphQL approaches.
"""

from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    VersionPropertiesClass,
    VersionSetPropertiesClass,
)

# Initialize DataHub Graph client
config = DatahubClientConfig(server="http://localhost:8080")
graph = DataHubGraph(config)

# Define the version set URN to query
version_set_urn = "urn:li:versionSet:(abc123def456,mlModel)"

# Method 1: Query using the Python SDK
print("=== Querying Version Set via Python SDK ===\n")

# Get the version set properties
version_set_props = graph.get_aspect(
    entity_urn=version_set_urn,
    aspect_type=VersionSetPropertiesClass,
)

if version_set_props is None:
    raise SystemExit(f"Version set not found: {version_set_urn}")

print(f"Version Set: {version_set_urn}")
print(f"Latest Version: {version_set_props.latest}")
print(f"Versioning Scheme: {version_set_props.versioningScheme}")

if version_set_props.customProperties:
    print("\nCustom Properties:")
    for key, value in version_set_props.customProperties.items():
        print(f"  {key}: {value}")

# Get version properties for the latest version
print("\n=== Latest Version Details ===\n")
latest_version_props = graph.get_aspect(
    entity_urn=version_set_props.latest,
    aspect_type=VersionPropertiesClass,
)

if latest_version_props:
    print(f"Version: {latest_version_props.version.versionTag}")
    print(f"Sort ID: {latest_version_props.sortId}")
    if latest_version_props.comment:
        print(f"Comment: {latest_version_props.comment}")
    if latest_version_props.aliases:
        aliases = [
            alias.versionTag
            for alias in latest_version_props.aliases
            if alias.versionTag is not None
        ]
        print(f"Aliases: {', '.join(aliases)}")

# Method 2: Query all versions using GraphQL
print("\n=== Querying All Versions via GraphQL ===\n")

graphql_query = """
query ($urn: String!) {
  versionSet(urn: $urn) {
    urn
    latestVersion {
      urn
      ... on MLModel {
        properties {
          name
          description
        }
      }
    }
    versionsSearch(input: {
      query: "*"
      start: 0
      count: 100
    }) {
      total
      searchResults {
        entity {
          urn
          ... on MLModel {
            versionProperties {
              version {
                versionTag
              }
              sortId
              comment
              isLatest
              aliases {
                versionTag
              }
            }
          }
        }
      }
    }
  }
}
"""

variables = {"urn": version_set_urn}

response = graph.execute_graphql(graphql_query, variables)

if "versionSet" in response and response["versionSet"]:
    version_set_data = response["versionSet"]
    versions = version_set_data.get("versionsSearch", {}).get("searchResults", [])

    print(f"Found {len(versions)} version(s)\n")

    for result in versions:
        entity = result.get("entity", {})
        version_props = entity.get("versionProperties", {})

        version_tag = version_props.get("version", {}).get("versionTag", "Unknown")
        is_latest = version_props.get("isLatest", False)
        comment = version_props.get("comment", "No comment")
        aliases = [
            alias.get("versionTag")
            for alias in version_props.get("aliases", [])
            if alias.get("versionTag")
        ]

        print(f"Version: {version_tag}")
        print(f"  URN: {entity.get('urn')}")
        print(f"  Latest: {is_latest}")
        print(f"  Comment: {comment}")
        if aliases:
            print(f"  Aliases: {', '.join(aliases)}")
        print()
else:
    print("No version set data found")

```



#### 通过 REST API 查询

标准的 DataHub REST API 可用于获取版本集实体及其属性。


**通过 REST API 获取版本集实体**

```bash
# Fetch a version set by URN
curl 'http://localhost:8080/entities/urn%3Ali%3AversionSet%3A(abc123def456,mlModel)'

# Get all entities in a version set using relationships
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3AversionSet%3A(abc123def456,mlModel)&types=VersionOf'
```



#### 通过 GraphQL 查询

DataHub 的 GraphQL API 为版本集提供了丰富的查询能力：


**GraphQL：查询版本集及其所有版本**

```graphql
query {
  versionSet(urn: "urn:li:versionSet:(abc123def456,mlModel)") {
    urn
    latestVersion {
      urn
      ... on MLModel {
        properties {
          name
          description
        }
      }
    }
    versionsSearch(input: { query: "*", start: 0, count: 10 }) {
      total
      searchResults {
        entity {
          urn
          ... on MLModel {
            versionProperties {
              version {
                versionTag
              }
              comment
              isLatest
              created {
                time
              }
            }
          }
        }
      }
    }
  }
}
```



## 集成点

### 与其他实体的关系

版本集与其他实体之间有一种特定的关系模式：

- **VersionOf**：版本化实体（数据集、ML 模型等）与其版本集之间具有 `VersionOf` 关系
- **最新版本引用**：版本集直接引用最新的版本化实体

### 支持的版本化实体

目前，DataHub 支持对以下实体类型进行版本管理：

- **MLModel**：机器学习模型通常会进行版本管理，以追踪模型的演进
- **Dataset**：数据集可以进行版本管理，以追踪模式变更、数据更新或快照

DataHub 未来的版本可能会将版本集支持扩展到更多实体类型。

### 功能开关

版本集功能由 `entityVersioning` 功能开关控制。必须在你的 DataHub 部署中启用该开关才能使用版本集：

```yaml
# In your DataHub configuration
featureFlags:
  entityVersioning: true
```

### 摄取连接器的使用

多个摄取连接器会自动创建并管理版本集：

- **MLflow**：为 Registered Model 创建版本集，每个 Model Version 都链接到该版本集
- **Vertex AI**：为具有多个版本的模型创建版本集
- **自定义连接器**：你可以在自定义摄取源中以编程方式创建版本集

## 值得注意的例外

### 单一实体类型约束

一个版本集只能包含单一类型的实体。这通过版本集键中的 `entityType` 字段来强制约束。你不能在同一版本集中混放不同类型的实体（例如数据集和 ML 模型）。

### 版本编排方案的不可变性

一旦为版本集设定了版本编排方案，就不应再更改。版本的排序与次序依赖于该方案，更改方案可能会破坏版本次序。

### 最新版本的维护

版本化实体上的 `isLatest` 标志由 DataHub 的版本管理服务自动维护。虽然通过 API 手动设置该字段在技术上可行，但你应依赖通过 `linkAssetVersion` GraphQL 变更或 Python SDK 的版本管理方法所提供的自动维护。

### 权限控制

将实体链接到版本集或从版本集取消链接，需要对版本集和版本化实体同时拥有 UPDATE 权限。请为需要管理版本的用户正确配置权限。

### 版本标签的唯一性

虽然版本标签（`version` 字段）应在版本集内保持唯一，但系统并未严格强制这一点。确保唯一性是客户端代码的责任。存在重复的版本标签可能在查询或浏览版本时造成混淆。

### 删除行为

当一个版本化实体被删除时，它不会自动从其版本集中取消链接。该关系可能会变成失效状态。请考虑在删除前显式取消实体链接，或实现清理逻辑以处理孤立的版本引用。

### 搜索与发现

版本集本身是 DataHub 中可搜索的实体。版本化实体可以按其版本标签、别名和版本集归属进行搜索。请使用 `versionSortId` 字段对搜索结果按版本次序排序。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](27-versionset.md)。
