---
title: 所有权类型
entity: ownershiptype
source: https://docs.datahub.com/docs/generated/metamodel/entities/ownershiptype.md
---

# 所有权类型

所有权类型（OwnershipType）实体表示 DataHub 中自定义的所有权类别。所有权类型定义了用户或用户组可以对数据资产承担的角色与职责。DataHub 提供了内置的所有权类型（技术负责人、业务负责人、数据管家），同时组织也可以创建自定义所有权类型，以匹配其特定的治理模型与组织结构。

## 身份（Identity）

所有权类型实体通过单一字段唯一标识：

- **id**：所有权类型的唯一标识符字符串。对于自定义所有权类型通常是 UUID，对于内置类型则是带系统前缀的标识符。

URN 结构遵循如下模式：`urn:li:ownershipType:<id>`

示例：

- 内置类型：`urn:li:ownershipType:__system__technical_owner`
- 自定义类型：`urn:li:ownershipType:8b3d78d1-a9d9-4f79-a948-10c52e3e8f9e`
- 具名自定义类型：`urn:li:ownershipType:data_quality_lead`

## 重要能力（Important Capabilities）

### 核心信息

`ownershipTypeInfo` aspect 包含所有权类型的核心元数据：

- **name**：所有权类型的显示名称（例如 "Data Quality Lead"、"Compliance Officer"）
- **description**：对该所有权类型职责与范围的详细说明
- **created**：审计戳（audit stamp），记录所有权类型的创建时间与创建者
- **lastModified**：审计戳，跟踪最近一次修改的时间与操作者

### 内置与自定义所有权类型

DataHub 自带四个自动创建的内置所有权类型：

1. **Technical Owner**（`__system__technical_owner`）：参与资产的生产、维护或分发
2. **Business Owner**（`__system__business_owner`）：与资产相关的主要利益相关方或领域专家
3. **Data Steward**（`__system__data_steward`）：参与资产的治理
4. **None**（`__system__none`）：未指定所有权类型

内置类型的 ID 以 `__system__` 开头，不能被彻底删除，只能通过 `status` aspect 进行软删除。自定义所有权类型可以被完整删除，且没有此前缀限制。

### 在所有权分配中的使用

所有权类型通过数据资产 `ownership` aspect 中 `Owner` 记录的 `typeUrn` 字段被引用。这在资产所有者与其具体角色之间建立了关系：

```
Owner {
  owner: urn:li:corpuser:jdoe
  typeUrn: urn:li:ownershipType:data_quality_lead
  type: CUSTOM  // deprecated field, maintained for backwards compatibility
}
```

`ownership` aspect 还维护一个 `ownerTypes` 映射，按所有权类型 URN 对所有者分组，该映射通过 mutation hook 自动填充。

### 状态管理

`status` aspect 控制所有权类型是处于有效状态还是已软删除：

- **removed**：设为 true 时，该所有权类型被视为已删除，但引用会被保留

内置所有权类型只能被软删除（status.removed = true），而自定义类型可以从系统中彻底移除。

## 代码示例（Code Examples）

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

### 在资产上使用自定义所有权类型

**Python SDK：使用自定义所有权类型分配所有者**

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

**Python SDK：查询所有所有权类型**

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

获取指定的所有权类型：

```bash
curl 'http://localhost:8080/entitiesV2/urn%3Ali%3AownershipType%3A__system__technical_owner'
```

响应中包含 `ownershipTypeInfo` 与 `status` aspects：

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

## 集成点（Integration Points）

### 与 Owner Aspect 的关系

所有权类型实体与大多数数据资产（数据集、仪表盘、图表等）上的 `ownership` aspect 存在主要关系。`Owner` 记录包含一个引用所有权类型实体的 `typeUrn` 字段：

```
@Relationship = {
  "name": "ownershipType",
  "entityTypes": [ "ownershipType" ]
}
typeUrn: optional Urn
```

该关系带来以下能力：

- 在搜索与发现中按所有权类型过滤资产
- 在整个组织范围内按角色对所有者分组
- 跟踪每个人对各资产承担的职责

### GraphQL API 集成

GraphQL API 通过若干 resolver 暴露所有权类型：

- **CreateOwnershipTypeResolver**：创建新的自定义所有权类型
- **UpdateOwnershipTypeResolver**：修改已有的所有权类型
- **DeleteOwnershipTypeResolver**：删除所有权类型（系统类型为软删除）
- **ListOwnershipTypesResolver**：返回所有可用的所有权类型

GraphQL 实体类型为 `CUSTOM_OWNERSHIP_TYPE`，映射到 `OwnershipTypeEntity` GraphQL 类型。

### 权限控制

管理所有权类型需要特定权限：

- 创建、更新或删除所有权类型需要 `canManageOwnershipTypes` 权限
- 该权限通常仅限于平台管理员与治理团队

### 常见使用模式

1. **组织特定角色**：定义与组织结构匹配的所有权类型（例如 "Product Manager"、"Data Engineer"、"Analytics Lead"）
2. **合规角色**：为法规合规创建类型（例如 "Privacy Officer"、"Compliance Reviewer"、"Audit Contact"）
3. **生命周期角色**：跟踪数据生命周期中的不同职责（例如 "Data Producer"、"Data Consumer"、"Data Custodian"）
4. **领域特定角色**：为特定领域建立所有权类型（例如 "Marketing Data Owner"、"Finance Data Steward"）

## 值得注意的例外（Notable Exceptions）

### 向后兼容性

`Owner` 记录同时包含已废弃的 `type` 字段（`OwnershipType` 枚举）与较新的 `typeUrn` 字段（指向所有权类型实体的 Urn 引用）。基于枚举的字段为向后兼容而保留，但不应在新的实现中使用。当使用自定义所有权类型时，该枚举字段被设为 `CUSTOM`。

### 系统类型的删除

内置所有权类型（ID 以 `__system__` 开头）无法被彻底删除。`OwnershipTypeService.deleteOwnershipType()` 方法会：

- 通过设置 `status.removed = true` 软删除系统类型
- 通过完全移除实体来硬删除自定义类型

这确保了即便系统类型被停用，对它们的引用仍然有效。

### 从枚举到实体的迁移

历史上，所有权类型是作为固定枚举（`OwnershipType.pdl`）定义的。引入所有权类型实体后，在保持兼容性的同时实现了可扩展性。已废弃的枚举值（DEVELOPER、DATAOWNER、DELEGATE、PRODUCER、CONSUMER、STAKEHOLDER）应迁移到相应的系统所有权类型（TECHNICAL_OWNER、BUSINESS_OWNER、DATA_STEWARD）。

### ID 生成

创建自定义所有权类型时：

- 系统会自动为 `id` 字段生成 UUID
- 组织也可以使用人类可读的 ID（例如 "data_quality_lead"）以便管理
- ID 不得包含保留字符，且必须符合 URL 安全要求
- `__system__` 前缀为内置类型保留

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/ownershiptype.md)。
