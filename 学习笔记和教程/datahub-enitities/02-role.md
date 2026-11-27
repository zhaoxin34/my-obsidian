---
title: 角色
entity: role
order: 02
source: https://docs.datahub.com/docs/generated/metamodel/entities/role.md
---

# 角色

角色（role）实体表示来自源系统（例如 Snowflake、BigQuery）的外部访问管理角色，这些角色控制着对数据资产的访问权限。该实体使 DataHub 能够建模并展示哪些角色提供了对数据集的访问，帮助数据消费方了解访问特定数据资源所需的权限。

## 身份（Identity）

角色由单一信息标识：

- 角色的唯一标识符：通常派生自定义该角色的外部 IAM 系统。该标识符应保持稳定，并在你所在组织的各数据平台间唯一。

角色标识符示例：`urn:li:role:snowflake_reader_role`。

## 重要能力（Important Capabilities）

### 角色属性

角色属性存储在 `roleProperties` aspect 中，包含外部访问管理角色的关键信息：

- **名称（Name）**：该角色在外部系统中的显示名称（例如 "Snowflake Reader Role"）
- **描述（Description）**：一段人类可读的说明，解释该角色的用途与范围
- **类型（Type）**：该角色提供的访问级别（例如 "READ"、"WRITE"、"ADMIN"）
- **申请 URL（Request URL）**：指向外部系统的可选链接，用户可在其中申请获得该角色的访问权限

以下代码片段展示了如何创建带属性的角色：

**Python SDK：创建带属性的角色**

```python
# Inlined from /metadata-ingestion/examples/library/role_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import RolePropertiesClass

# Create the role URN
# Role URNs follow the pattern: urn:li:role:{role_id}
role_urn = "urn:li:role:snowflake_reader_role"

# Define the role properties
role_properties = RolePropertiesClass(
    name="Snowflake Reader Role",
    description="Provides read-only access to analytics datasets in Snowflake",
    type="READ",
    requestUrl="https://mycompany.okta.com/access/request/snowflake-reader",
)

# Create a metadata change proposal
mcp = MetadataChangeProposalWrapper(
    entityUrn=role_urn,
    aspect=role_properties,
)

# Emit the metadata change
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
emitter.emit(mcp)
print(f"Created role: {role_urn}")

```

### 角色成员（Actors）

角色可通过 `actors` aspect 分配给用户和用户组。它跟踪哪些用户（corpuser 实体）与用户组（corpGroup 实体）已在外部系统中被授予该角色。

actors aspect 包含：

- **用户（Users）**：已获得该角色的 corp 用户列表
- **用户组（Groups）**：已分配该角色的 corp 用户组列表

以下代码片段展示了如何将用户与用户组分配给角色：

**Python SDK：将用户与用户组分配给角色**

```python
# Inlined from /metadata-ingestion/examples/library/role_assign_actors.py
from datahub.emitter.mce_builder import make_group_urn, make_user_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    ActorsClass,
    RoleGroupClass,
    RoleUserClass,
)

# Create the role URN
# Role URNs follow the pattern: urn:li:role:{role_id}
role_urn = "urn:li:role:snowflake_reader_role"

# Define the users and groups assigned to this role
actors = ActorsClass(
    users=[
        RoleUserClass(user=make_user_urn("john.doe")),
        RoleUserClass(user=make_user_urn("jane.smith")),
    ],
    groups=[
        RoleGroupClass(group=make_group_urn("data-analysts")),
        RoleGroupClass(group=make_group_urn("business-intelligence")),
    ],
)

# Create a metadata change proposal
mcp = MetadataChangeProposalWrapper(
    entityUrn=role_urn,
    aspect=actors,
)

# Emit the metadata change
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
emitter.emit(mcp)
print(f"Assigned users and groups to role: {role_urn}")

```

### 数据集访问集成

角色通过数据集实体上的 `access` aspect 与数据集关联。该 aspect 列出哪些角色为特定数据集提供访问权限，从而清晰呈现访问控制的全貌。

以下代码片段展示了如何将角色与数据集关联：

**Python SDK：将角色与数据集关联**

```python
# Inlined from /metadata-ingestion/examples/library/role_assign_to_dataset.py
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import AccessClass, RoleAssociationClass

# Create the dataset URN
dataset_urn = make_dataset_urn(
    platform="snowflake", name="analytics_db.public.user_events", env="PROD"
)

# Define the roles that provide access to this dataset
# Role URNs follow the pattern: urn:li:role:{role_id}
access_aspect = AccessClass(
    roles=[
        RoleAssociationClass(urn="urn:li:role:snowflake_reader_role"),
        RoleAssociationClass(urn="urn:li:role:snowflake_writer_role"),
        RoleAssociationClass(urn="urn:li:role:snowflake_admin_role"),
    ]
)

# Create a metadata change proposal
mcp = MetadataChangeProposalWrapper(
    entityUrn=dataset_urn,
    aspect=access_aspect,
)

# Emit the metadata change
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
emitter.emit(mcp)
print(f"Associated roles with dataset: {dataset_urn}")

```

### 查询角色信息

可以使用标准 REST API 端点获取角色信息。响应包含该角色实体的全部 aspects。

**通过 REST API 查询角色实体**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Arole%3Asnowflake_reader_role'
```

这将返回完整的角色实体，包括：

- `roleKey`：身份 aspect
- `roleProperties`：名称、描述、类型与申请 URL
- `actors`：分配给该角色的用户与用户组

**Python SDK：查询角色实体**

```python
# Inlined from /metadata-ingestion/examples/library/role_query.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import ActorsClass, RolePropertiesClass
from datahub.metadata.urns import RoleUrn

graph = get_default_graph()

role_urn = RoleUrn("snowflake_reader_role")

props = graph.get_aspect(entity_urn=str(role_urn), aspect_type=RolePropertiesClass)
if props is None:
    raise SystemExit(f"Role not found: {role_urn}")

print(f"Role URN: {role_urn}")
print(f"Name: {props.name}")
print(f"Description: {props.description}")
print(f"Type: {props.type}")
print(f"Request URL: {props.requestUrl}")

actors = graph.get_aspect(entity_urn=str(role_urn), aspect_type=ActorsClass)
if actors is not None:
    if actors.users:
        print(f"Users: {[u.user for u in actors.users]}")
    if actors.groups:
        print(f"Groups: {[g.group for g in actors.groups]}")

```

**通过 REST API 搜索角色**

```bash
curl -X POST 'http://localhost:8080/entities?action=search' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "role",
    "input": "reader",
    "start": 0,
    "count": 10
  }'
```

该查询在角色名称中进行搜索并返回匹配的角色 URN。

## 集成点（Integration Points）

### 与 CorpUser 和 CorpGroup 的关系

角色与用户实体和用户组实体存在直接关系：

- **RoleUser**：通过 "Has" 关系把角色链接到 `corpuser` 实体
- **RoleGroup**：通过 "Has" 关系把角色链接到 `corpGroup` 实体

这些关系带来：

- 查看哪些用户/用户组拥有特定角色
- 发现某个用户或用户组被分配的所有角色
- 审计整个数据生态中的访问模式

### 与 DataHub 角色的区别

区分 `role` 实体与 `dataHubRole` 实体很重要：

- **role**（本实体）：表示来自源系统（例如 Snowflake 角色、BigQuery 角色）的外部访问管理角色，这些角色控制着这些平台中数据资产的访问
- **dataHubRole**：表示 DataHub 内部的角色，用于控制 DataHub 功能的权限（例如管理员角色、编辑者角色）

corpuser 与 corpGroup 实体上的 `roleMembership` aspect 指的是 `dataHubRole` 实体，而非此处记录的外部 `role` 实体。

### 使用模式

role 实体的常见使用模式包括：

1. **访问发现**：数据消费方可查看哪些角色为其所需数据集提供访问权限
2. **自助式访问申请**：用户可识别合适的角色，并通过提供的申请 URL 申请访问
3. **访问审计**：合规团队可跟踪哪些角色为敏感数据集提供访问权限
4. **统一访问视图**：平台团队可创建跨多个数据平台的集中式访问控制视图

### GraphQL API

role 实体通过 DataHub 的 GraphQL API 以 `Role` 类型暴露。主要 resolver 包括：

- `RoleType`：为 role 实体提供搜索与批量加载能力
- `ListRolesResolver`：查询系统中的所有角色
- `BatchAssignRoleResolver`：批量将角色分配给用户/用户组
- `AcceptRoleResolver`：接受角色分配的流程

## 值得注意的例外（Notable Exceptions）

### 实体支持有限

当前 role 实体与访问管理功能仅支持**数据集实体**。虽然从概念上讲角色可应用于其他数据资产（仪表盘、图表等），但 `access` aspect 目前仅为数据集定义。

未来的增强可能会把基于角色的访问管理扩展到更多实体类型。

### 外部系统集成

role 实体旨在表示存在于外部系统中的角色。DataHub 并不直接创建或管理这些角色 —— 它仅为发现与文档目的对其建模。角色成员的实际授予与回收必须在源系统中完成。

### 需要配置

在自托管部署中，访问管理 UI 功能默认关闭。要在 UI 中启用角色可视化，请将 `datahub-gms` 服务的 `SHOW_ACCESS_MANAGEMENT` 环境变量设置为 `true`。

### 活跃开发中

role 实体与访问管理功能正在活跃开发中，可能发生变化。计划中的增强包括：

- 在角色之外建模外部策略
- 从 BigQuery、Snowflake 等来源自动提取角色
- 扩展对数据集以外更多实体类型的支持
- 带审批流程的高级访问申请工作流

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](02-role.md)。
