---
title: 所有权类型
entity: ownershiptype
order: 38
source: https://docs.datahub.com/docs/generated/metamodel/entities/ownershiptype.md
---

# 所有权类型

ownershipType 实体表示 DataHub 中的自定义所有权分类。所有权类型定义了用户或用户组对数据资产可以承担的角色与职责。DataHub 内置了若干所有权类型（技术负责人、业务负责人、数据管理员），但组织也可以创建自定义所有权类型，以匹配其特定的治理模型与组织结构。

## 标识

OwnershipType 实体由单个字段唯一标识：

- **id**：所有权类型的唯一标识符字符串。对于自定义所有权类型通常是一个 UUID，对于内置类型则是带系统前缀的标识符。

URN 结构遵循模式：`urn:li:ownershipType:<id>`

示例：

- 内置类型：`urn:li:ownershipType:__system__technical_owner`
- 自定义类型：`urn:li:ownershipType:8b3d78d1-a9d9-4f79-a948-10c52e3e8f9e`
- 具名自定义类型：`urn:li:ownershipType:data_quality_lead`

## 重要能力

### 核心信息

`ownershipTypeInfo` 方面（aspect）包含所有权类型的关键元数据：

- **name**：所有权类型的显示名称（例如 "Data Quality Lead"、"Compliance Officer"）
- **description**：对该所有权类型的职责与范围的详细说明
- **created**：记录所有权类型何时创建、由谁创建的审计戳（audit stamp）
- **lastModified**：跟踪最后修改时间与操作者的审计戳

### 内置类型与自定义类型

DataHub 随附四个自动创建的内置所有权类型：

1. **Technical Owner**（`__system__technical_owner`）：参与资产的生产、维护或分发
2. **Business Owner**（`__system__business_owner`）：与资产相关的主要利益相关方或领域专家
3. **Data Steward**（`__system__data_steward`）：参与资产的治理
4. **None**（`__system__none`）：未指定所有权类型

内置类型的 ID 以 `__system__` 为前缀，无法被硬删除，只能通过 `status` 方面进行软删除。自定义所有权类型可以被彻底删除，且不受此前缀限制。

### 在所有权分配中的使用

在数据资产的 `ownership` 方面中，所有权类型通过 `Owner` 记录的 `typeUrn` 字段被引用。这在资产负责人与其具体角色之间建立了关系：

```
Owner {
  owner: urn:li:corpuser:jdoe
  typeUrn: urn:li:ownershipType:data_quality_lead
  type: CUSTOM  // deprecated field, maintained for backwards compatibility
}
```

ownership 方面还维护一个 `ownerTypes` 映射，按所有权类型 URN 对负责人分组，该映射通过变更钩子（mutation hooks）自动填充。

### 状态管理

`status` 方面控制所有权类型是处于生效状态还是已被软删除：

- **removed**：设为 true 时，该所有权类型被视为已删除，但相关引用会被保留

内置所有权类型只能被软删除（status.removed = true），而自定义类型可以从系统中彻底移除。

## 代码示例

### 创建自定义所有权类型


**Python SDK：创建自定义所有权类型**

```python
# Inlined from /metadata-ingestion/examples/library/ownership_type_create_custom.py
import os
import time

from datahub.emitter.mce_builder import make_user_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    OwnershipTypeInfoClass,
    OwnershipTypeKeyClass,
)

emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

ownership_type_id = "data_quality_lead"
ownership_type_urn = f"urn:li:ownershipType:{ownership_type_id}"

current_timestamp = int(time.time() * 1000)
actor_urn = make_user_urn("datahub")

# Emit the key aspect
ownership_type_key = OwnershipTypeKeyClass(id=ownership_type_id)
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=ownership_type_urn,
        aspect=ownership_type_key,
    )
)

# Emit the info aspect
ownership_type_info = OwnershipTypeInfoClass(
    name="Data Quality Lead",
    description="Responsible for ensuring data quality standards and monitoring data quality metrics",
    created=AuditStampClass(time=current_timestamp, actor=actor_urn),
    lastModified=AuditStampClass(time=current_timestamp, actor=actor_urn),
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=ownership_type_urn,
        aspect=ownership_type_info,
    )
)

print(f"Created custom ownership type: {ownership_type_urn}")

```



### 将自定义所有权类型用于资产


**Python SDK：使用自定义所有权类型分配负责人**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_owner_custom_type.py
from datahub.emitter.mce_builder import (
    make_dataset_urn,
    make_ownership_type_urn,
    make_user_urn,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import (
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)

# Create DataHub client
graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter("http://localhost:8080")

# Create dataset URN
dataset_urn = make_dataset_urn(platform="snowflake", name="analytics.users", env="PROD")

# Create custom ownership type URN
# This should reference a previously created custom ownership type
custom_ownership_type_urn = make_ownership_type_urn("data_quality_lead")

# Create an owner with the custom ownership type
owner = OwnerClass(
    owner=make_user_urn("jdoe"),
    type=OwnershipTypeClass.CUSTOM,  # Use CUSTOM enum for custom types
    typeUrn=custom_ownership_type_urn,  # Reference the custom ownership type entity
)

# Get existing ownership or create new
try:
    existing_ownership = graph.get_aspect(dataset_urn, OwnershipClass)
    if existing_ownership:
        # Add to existing owners
        existing_ownership.owners.append(owner)
        ownership = existing_ownership
    else:
        # Create new ownership aspect
        ownership = OwnershipClass(owners=[owner])
except Exception:
    # Create new ownership aspect if retrieval fails
    ownership = OwnershipClass(owners=[owner])

# Emit the ownership aspect
mcp = MetadataChangeProposalWrapper(
    entityUrn=str(dataset_urn),
    aspect=ownership,
)

emitter.emit_mcp(mcp)

print(
    f"Added owner {owner.owner} with custom ownership type {custom_ownership_type_urn}"
)
print(f"to dataset {dataset_urn}")

```



### 列出所有权类型


**Python SDK：查询全部所有权类型**

```python
# Inlined from /metadata-ingestion/examples/library/ownership_type_list.py
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

# Create DataHub client
graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Search for all ownership type entities
# Note: The GraphQL API provides a listOwnershipTypes query, but we can also
# use the search API to find all ownership types
search_query = """
query listOwnershipTypes($input: ListOwnershipTypesInput!) {
  listOwnershipTypes(input: $input) {
    start
    count
    total
    ownershipTypes {
      urn
      type
      info {
        name
        description
      }
    }
  }
}
"""

variables = {
    "input": {
        "start": 0,
        "count": 100,  # Adjust as needed
    }
}

# Execute the GraphQL query
result = graph.execute_graphql(query=search_query, variables=variables)

# Process and display the results
if result and "listOwnershipTypes" in result:
    ownership_types = result["listOwnershipTypes"]["ownershipTypes"]
    total = result["listOwnershipTypes"]["total"]

    print(f"Found {total} ownership types:")
    print("-" * 80)

    for ownership_type in ownership_types:
        urn = ownership_type["urn"]
        name = ownership_type["info"]["name"]
        description = ownership_type["info"].get("description", "No description")

        print(f"URN: {urn}")
        print(f"Name: {name}")
        print(f"Description: {description}")
        print("-" * 80)
else:
    print("No ownership types found or query failed")

```



### 通过 REST API 查询


**通过 REST API 获取所有权类型**

获取特定的所有权类型：

```bash
curl 'http://localhost:8080/entitiesV2/urn%3Ali%3AownershipType%3A__system__technical_owner'
```

响应中包含 `ownershipTypeInfo` 与 `status` 方面：

```json
{
  "urn": "urn:li:ownershipType:__system__technical_owner",
  "aspects": {
    "ownershipTypeInfo": {
      "value": {
        "name": "Technical Owner",
        "description": "Involved in the production, maintenance, or distribution of the asset(s).",
        "created": {
          "time": 1234567890000,
          "actor": "urn:li:corpuser:datahub"
        },
        "lastModified": {
          "time": 1234567890000,
          "actor": "urn:li:corpuser:datahub"
        }
      }
    }
  }
}
```



## 集成点

…


### 与 Owner 方面的关系

ownershipType 实体与大多数数据资产（数据集、仪表板、图表等）上的 `ownership` 方面存在主要关系。`Owner` 记录包含一个 `typeUrn` 字段，用于引用 ownershipType 实体：

```
@Relationship = {
  "name": "ownershipType",
  "entityTypes": [ "ownershipType" ]
}
typeUrn: optional Urn
```

该关系支持：

- 在搜索与发现中按所有权类型筛选资产
- 按角色在整个组织范围内对负责人分组
- 跟踪每项资产各项职责的承担者

### GraphQL API 集成

GraphQL API 通过若干解析器暴露所有权类型：

- **CreateOwnershipTypeResolver**：创建新的自定义所有权类型
- **UpdateOwnershipTypeResolver**：修改已有的所有权类型
- **DeleteOwnershipTypeResolver**：删除所有权类型（系统类型为软删除）
- **ListOwnershipTypesResolver**：返回所有可用的所有权类型

GraphQL 实体类型为 `CUSTOM_OWNERSHIP_TYPE`，映射到 `OwnershipTypeEntity` GraphQL 类型。

### 授权

管理所有权类型需要特定授权：

- 创建、更新或删除所有权类型需要 `canManageOwnershipTypes` 权限
- 该权限通常仅限于平台管理员与治理团队

### 常见使用模式

1. **组织专属角色**：定义与组织结构匹配的所有权类型（例如 "Product Manager"、"Data Engineer"、"Analytics Lead"）

2. **合规角色**：为法规合规创建类型（例如 "Privacy Officer"、"Compliance Reviewer"、"Audit Contact"）

3. **生命周期角色**：跟踪数据生命周期中的不同职责（例如 "Data Producer"、"Data Consumer"、"Data Custodian"）

4. **领域专属角色**：为特定领域确立所有权类型（例如 "Marketing Data Owner"、"Finance Data Steward"）

## 值得注意的例外

### 向后兼容

`Owner` 记录同时包含已弃用的 `type` 字段（OwnershipType 枚举）和较新的 `typeUrn` 字段（指向 ownershipType 实体的 Urn 引用）。基于枚举的字段为向后兼容而保留，但不应在新实现中使用。当使用自定义所有权类型时，枚举字段会被设为 `CUSTOM`。

### 系统类型的删除

内置所有权类型（ID 以 `__system__` 开头）无法被彻底删除。`OwnershipTypeService.deleteOwnershipType()` 方法将：

- 通过设置 `status.removed = true` 软删除系统类型
- 通过彻底移除实体来硬删除自定义类型

这确保了即使系统类型被停用，对它们的引用仍然有效。

### 从枚举迁移到实体

历史上，所有权类型定义为一个固定枚举（`OwnershipType.pdl`）。ownershipType 实体的引入在保持兼容性的同时实现了可扩展性。已弃用的枚举值（DEVELOPER、DATAOWNER、DELEGATE、PRODUCER、CONSUMER、STAKEHOLDER）应迁移到相应的系统所有权类型（TECHNICAL_OWNER、BUSINESS_OWNER、DATA_STEWARD）。

### ID 生成

创建自定义所有权类型时：

- 系统会自动为 `id` 字段生成一个 UUID
- 组织也可以使用人类可读的 ID（例如 "data_quality_lead"）以便管理
- ID 不得包含保留字符，且必须是 URL 安全的
- `__system__` 前缀为内置类型保留


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](38-ownershiptype.md)。
