---
title: 用户组
entity: corpgroup
source: https://docs.datahub.com/docs/generated/metamodel/entities/corpgroup.md
---

# 用户组（CorpGroup）

corpGroup 实体表示企业内部的组织群组、团队或部门。这些群组可以从 LDAP、Active Directory 或 SAML/SSO 等外部身份提供商同步而来，也可以在 DataHub 内部原生创建。CorpGroup 对于在 DataHub 中管理访问控制、负责人分配以及组织元数据至关重要。

## 身份（Identity）

CorpGroup 由单个字符串字段唯一标识：群组名称。

corpGroup 的 URN 结构为：

```
urn:li:corpGroup:<encoded-group-name>
```

`<encoded-group-name>` 是群组名称的 URL 编码版本，在 DataHub 中作为全局唯一标识符。该编码由 SDK 自动处理。

### 示例

以下是不同群组命名约定下典型的 URN 模式：

```
urn:li:corpGroup:eng-team
urn:li:corpGroup:data-platform
urn:li:corpGroup:cn%3Dadmins%2Cou%3Dgroups%2Cdc%3Dexample%2Cdc%3Dcom  # LDAP DN
urn:li:corpGroup:S-1-5-21-123456789-123456789-123456789-1234          # Active Directory SID
urn:li:corpGroup:marketing-team
```

name 字段可搜索并支持自动补全，便于在 DataHub 中快速找到群组。

## 重要能力

### 群组信息

群组信息存储在两个方面中：

- **corpGroupInfo**：包含通常从外部身份提供商（LDAP、AD、SSO）同步而来的元数据
- **corpGroupEditableInfo**：包含可通过 DataHub UI 编辑的元数据

#### CorpGroupInfo

该方面存储来自外部系统的权威信息：

- **displayName**：群组的人类可读名称
- **email**：群组的联系邮箱
- **description**：群组用途与范围的描述
- **slack**：与群组关联的 Slack 频道
- **created**：群组创建的时间戳

**注意**：corpGroupInfo 中的 `admins`、`members` 和 `groups` 字段已废弃，仅为向后兼容而保留。群组成员关系现在通过 GroupMembership 方面进行管理。

#### CorpGroupEditableInfo

该方面存储可在 DataHub UI 中编辑的信息：

- **description**：可编辑的群组描述
- **pictureLink**：群组头像图片的 URL
- **slack**：群组的 Slack 频道
- **email**：群组的联系邮箱

当两个方面包含同一字段（如 description）时，UI 通常优先展示可编辑版本。

### 群组成员关系

群组成员关系通过 **groupMembership** 方面进行管理，该方面附着在 corpUser 实体上（而非群组自身）。这一设计可以高效地查询某个用户属于哪些群组。

若要将用户加入群组，需要更新用户实体上的 groupMembership 方面，将该群组的 URN 加入其中。

### 来源追踪

**origin** 方面用于追踪群组的来源：

- **NATIVE**：群组直接在 DataHub 中创建
- **EXTERNAL**：群组从外部身份提供商同步而来

对于外部群组，`externalType` 字段可指定来源系统（例如 "LDAP"、"AzureAD"、"Okta"）。

### 负责人

群组可以通过标准的 **ownership** 方面设置负责人。负责人通常是负责该群组的管理员或经理。负责人类型包括 TECHNICAL_OWNER、BUSINESS_OWNER 等。

### 标签与属性

与 DataHub 中的其他实体一样，群组支持：

- **globalTags**：用于组织与发现的群组标签
- **structuredProperties**：由你的组织定义的自定义元数据属性
- **forms**：用于结构化数据采集的元数据表单

## 代码示例

### 创建 CorpGroup

**Python SDK：创建群组并发送到 DataHub**

```python
# Inlined from /metadata-ingestion/examples/library/corpgroup_create.py
# metadata-ingestion/examples/library/corpgroup_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    CorpGroupInfoClass,
    OriginClass,
    OriginTypeClass,
    StatusClass,
)
from datahub.utilities.urns.corp_group_urn import CorpGroupUrn

gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

group_urn = CorpGroupUrn("data-engineering")

group_info = CorpGroupInfoClass(
    displayName="Data Engineering",
    description="The data engineering team builds and maintains data pipelines and infrastructure",
    email="data-eng@example.com",
    slack="data-engineering",
    admins=[],
    members=[],
    groups=[],
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=str(group_urn),
    aspect=group_info,
)
emitter.emit(metadata_event)

status_aspect = StatusClass(removed=False)
metadata_event = MetadataChangeProposalWrapper(
    entityUrn=str(group_urn),
    aspect=status_aspect,
)
emitter.emit(metadata_event)

origin_aspect = OriginClass(type=OriginTypeClass.NATIVE)
metadata_event = MetadataChangeProposalWrapper(
    entityUrn=str(group_urn),
    aspect=origin_aspect,
)
emitter.emit(metadata_event)

print(f"Created group: {group_urn}")

```

### 向群组添加成员

**Python SDK：向已有群组添加成员**

```python
# Inlined from /metadata-ingestion/examples/library/corpgroup_add_members.py
# metadata-ingestion/examples/library/corpgroup_add_members.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import GroupMembershipClass
from datahub.metadata.urns import CorpGroupUrn, CorpUserUrn

graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

group_urn = str(CorpGroupUrn("data-engineering"))

users_to_add = [
    CorpUserUrn("jdoe"),
    CorpUserUrn("asmith"),
    CorpUserUrn("bwilliams"),
]

for user_urn in users_to_add:
    user_urn_str = str(user_urn)

    current_membership = graph.get_aspect(user_urn_str, GroupMembershipClass)

    if current_membership is None:
        current_membership = GroupMembershipClass(groups=[])

    if group_urn not in current_membership.groups:
        current_membership.groups.append(group_urn)

        metadata_event = MetadataChangeProposalWrapper(
            entityUrn=user_urn_str,
            aspect=current_membership,
        )
        emitter.emit(metadata_event)

        print(f"Added {user_urn_str} to group {group_urn}")
    else:
        print(f"{user_urn_str} is already a member of {group_urn}")

```

### 更新群组信息

**Python SDK：更新群组描述与元数据**

```python
# Inlined from /metadata-ingestion/examples/library/corpgroup_update_info.py
# metadata-ingestion/examples/library/corpgroup_update_info.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import (
    CorpGroupEditableInfoClass,
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)
from datahub.metadata.urns import CorpGroupUrn, CorpUserUrn

graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

group_urn = str(CorpGroupUrn("data-engineering"))

editable_info = CorpGroupEditableInfoClass(
    description="Updated description: The data engineering team builds and maintains data pipelines, infrastructure, and ensures data quality across the organization",
    pictureLink="https://example.com/images/data-engineering-logo.png",
    slack="data-engineering",
    email="data-eng@example.com",
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=group_urn,
    aspect=editable_info,
)
emitter.emit(metadata_event)

print(f"Updated editable info for group: {group_urn}")

admin_urn = str(CorpUserUrn("jdoe"))

ownership = OwnershipClass(
    owners=[
        OwnerClass(
            owner=admin_urn,
            type=OwnershipTypeClass.TECHNICAL_OWNER,
        )
    ]
)

metadata_event = MetadataChangeProposalWrapper(
    entityUrn=group_urn,
    aspect=ownership,
)
emitter.emit(metadata_event)

print(f"Added {admin_urn} as owner of group: {group_urn}")

```

### 通过 REST API 查询群组

**获取群组实体及其成员关系**

若要获取包含所有方面的群组实体：

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AcorpGroup%3Aeng-team'
```

若要找出某个特定群组的所有成员用户：

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3AcorpGroup%3Aeng-team&types=IsMemberOfGroup'
```

响应将包含所有在 groupMembership 方面中带有该群组的 corpUser 实体：

```json
{
  "start": 0,
  "count": 3,
  "relationships": [
    {
      "type": "IsMemberOfGroup",
      "entity": "urn:li:corpuser:jdoe"
    },
    {
      "type": "IsMemberOfGroup",
      "entity": "urn:li:corpuser:asmith"
    },
    {
      "type": "IsMemberOfGroup",
      "entity": "urn:li:corpuser:bwilliams"
    }
  ],
  "total": 3
}
```

## 集成点

### 用户管理

CorpGroup 通过 groupMembership 方面与 corpUser 实体紧密集成。当用户被加入某个群组时，其 groupMembership 方面会更新为包含该群组的 URN，从而建立双向关系。

### 负责人关系

群组可以通过 ownership 方面被指定为任意 DataHub 实体（数据集、仪表盘、图表等）的负责人。这支持以团队为单位的所有权归属，此时群组的所有成员都被视为负责人。

负责人分配示例：

```python
# A dataset can have a group as an owner
dataset.add_owner(CorpGroupUrn("data-engineering"))
```

### 访问控制

虽然群组信息并不直接存储在 corpGroup 的方面中，但群组是 DataHub RBAC（基于角色的访问控制）系统的核心组成部分。群组可以：

- 通过 roleMembership 方面被分配角色
- 在 DataHub 策略中被引用，以实现细粒度的访问控制
- 用于管理元数据操作的权限

### 外部身份提供商集成

DataHub 提供从外部系统同步群组的摄取连接器：

#### LDAP 集成

LDAP 数据源连接器可以提取群组及其成员关系：

```yaml
source:
  type: ldap
  config:
    ldap_server: "ldap://ldap.example.com"
    ldap_user: "cn=admin,dc=example,dc=com"
    ldap_password: "${LDAP_PASSWORD}"
    base_dn: "ou=groups,dc=example,dc=com"
    filter: "(objectClass=groupOfNames)"
```

从 LDAP 提取的群组将具有：

- `origin` 方面设为 EXTERNAL，externalType="LDAP"
- 来自 LDAP 属性的显示名称与描述
- 自动同步的群组成员关系

#### Azure AD 集成

Azure AD 数据源连接器从 Microsoft Azure Active Directory 同步群组：

```yaml
source:
  type: azure-ad
  config:
    client_id: "${AZURE_CLIENT_ID}"
    tenant_id: "${AZURE_TENANT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    ingest_users: true
    ingest_groups: true
```

Azure AD 群组将具有：

- `origin` 方面设为 EXTERNAL，externalType="AzureAD"
- Microsoft 365 群组信息（如适用）
- 被扁平化的嵌套群组成员关系

### GraphQL API

corpGroup 实体在 DataHub 的 GraphQL API 中得到完整支持。常见查询包括：

```graphql
query GetGroup {
  corpGroup(urn: "urn:li:corpGroup:eng-team") {
    urn
    name
    properties {
      displayName
      description
      email
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
```

## 值得注意的例外

### 已废弃的成员字段

corpGroupInfo 方面中的 `members`、`admins` 和 `groups` 字段已废弃。这些字段最初用于直接在群组实体上存储成员关系，但这种做法存在可扩展性与一致性问题。

当前的最佳实践是：

1. 使用 corpUser 实体上的 groupMembership 方面追踪用户所属的群组
2. 使用 ownership 方面指定群组管理员
3. 通过 REST API 查询关系以找出群组成员

### 原生群组与外部群组

群组可以通过两种方式创建：

1. **原生群组**：通过 UI 或 API 直接在 DataHub 中创建，origin 类型为 NATIVE
2. **外部群组**：从身份提供商同步而来，origin 类型为 EXTERNAL

外部群组在 DataHub 中通常被视为只读，以防与源系统冲突。更新应在源系统（如 LDAP、Azure AD）中完成，然后重新同步到 DataHub。

### 群组名称编码

群组名称在 URN 中会被 URL 编码，以处理 LDAP DN 与 Active Directory 路径中常见的特殊字符。使用 SDK 时编码会自动完成。然而在手动构造 URN 或发起 API 请求时，请确保进行了正确的 URL 编码：

```python
# Correct - SDK handles encoding
CorpGroupUrn("cn=admins,ou=groups,dc=example,dc=com")
# Result: urn:li:corpGroup:cn%3Dadmins%2Cou%3Dgroups%2Cdc%3Dexample%2Cdc%3Dcom

# Incorrect - manual construction without encoding
"urn:li:corpGroup:cn=admins,ou=groups,dc=example,dc=com"  # Will fail
```

### 群组层级

虽然 corpGroupInfo 方面中包含已废弃的 `groups` 字段用于表示嵌套群组，但 DataHub 目前并不支持一等公民式的群组层级。群组成员关系是扁平的——用户要么是某群组的成员，要么不是。如果需要层级化的群组结构，可以考虑：

1. 在摄取阶段将层级扁平化（例如，若用户属于某个子群组，则将其同时加入所有父群组）
2. 使用命名约定表示层级（例如 "engineering"、"engineering-platform"、"engineering-platform-data"）
3. 使用域（domain）或标签来表示组织结构

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/corpgroup.md)。
