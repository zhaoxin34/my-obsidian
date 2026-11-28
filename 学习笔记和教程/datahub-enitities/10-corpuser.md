---
title: 企业用户
entity: corpuser
order: 10
source: https://docs.datahub.com/docs/generated/metamodel/entities/corpuser.md
---

# 企业用户

CorpUser 表示企业中的单个用户（或账户）。这些实体构成 DataHub 内部的标识层，代表与数据资产交互、拥有资源、隶属于群组，并在组织内拥有角色与权限的人员。CorpUser 可以代表 LDAP 用户、Active Directory 账户、SSO 身份，或 DataHub 原生用户。

## 标识

CorpUser 由单一信息项唯一标识：

- **Username**：用户在组织内的唯一标识符。它通常来自企业身份提供商（LDAP、Active Directory 等），对于 DataHub 原生用户也可以是电子邮件地址。

CorpUser 的 URN 结构为：

```
urn:li:corpuser:<username>
```

### 示例

```
urn:li:corpuser:jdoe
urn:li:corpuser:john.doe@company.com
urn:li:corpuser:jdoe@company.com
```

用户名存储在 `corpUserKey` aspect 中，它是该实体的身份 aspect。username 字段被标记为可搜索，并在 DataHub UI 中支持自动补全功能。

### 用户名约定

用户名可以根据你的组织身份提供商采用不同约定：

- **LDAP/Active Directory 用户名**：`jdoe`、`john.doe`、`john_doe`
- **电子邮件地址**：`jdoe@company.com`、`john.doe@company.com`
- **SSO 身份**：取决于你的 SSO 提供商的用户名格式
- **DataHub 原生用户**：通常是电子邮件地址

在你的 DataHub 部署中保持用户名格式的一致性非常重要，以确保身份解析和关系追踪正常进行。

## 重要能力

### 档案信息

用户的基本档案信息存储在 `corpUserInfo` aspect 中。它通常由来自 LDAP、Active Directory、Azure AD、Okta 或其他 SSO 系统等身份提供商的摄取连接器自动填充。

**关键字段：**

- **displayName**：用户在 UI 中应显示的名称
- **email**：用于联系用户的电子邮件地址
- **title**：职位（例如 "Senior Data Engineer"）
- **firstName** 和 **lastName**：用户姓名的组成部分
- **fullName**：完整姓名，通常格式为 "firstName lastName"
- **managerUrn**：用户直属经理的 URN 引用（另一个 CorpUser）
- **departmentId** 和 **departmentName**：组织部门信息
- **countryCode**：双字母国家代码（例如 "US"、"UK"）
- **active**：用户账户是否处于活动状态（已弃用，推荐使用 `corpUserStatus`）
- **system**：这是系统/服务账户还是自然人用户

`managerUrn` 字段在用户之间创建关系，从而支持在 DataHub 中可视化组织层级。

### 可编辑的用户信息

`corpUserEditableInfo` aspect 包含用户可通过 DataHub UI 修改的信息，允许用户在身份提供商提供的内容之外补充自己的档案。

**关键字段：**

- **aboutMe**：个人描述或简介
- **displayName**：用户指定的显示名称（覆盖 corpUserInfo 中的名称）
- **title**：用户指定的职位（覆盖 corpUserInfo 中的职位）
- **teams**：用户所属的团队名称列表（例如 ["Data Platform", "Analytics"]）
- **skills**：用户拥有的技能列表（例如 ["Python", "SQL", "Machine Learning"]）
- **pictureLink**：头像图片的 URL
- **slack**：用于沟通的 Slack 用户名
- **phone**：联系电话
- **email**：联系邮箱（可以与系统邮箱不同）
- **platforms**：用户常用的数据平台的 URN
- **persona**：用户的 DataHub persona 的 URN（基于角色的 persona，例如 "Data Analyst"）

### 用户状态

`corpUserStatus` aspect 跟踪用户账户的当前状态，取代了已弃用的 `corpUserInfo` 中的 `active` 字段。

**关键字段：**

- **status**：用户的当前状态（例如 "ACTIVE"、"SUSPENDED"、"PROVISIONED"）
- **lastModified**：审计标记，记录最后修改状态的人以及修改时间

相比简单的布尔值 `active` 字段，该 aspect 提供了对用户账户状态更细粒度的控制。

### 群组成员关系

用户可以通过两个不同的 aspect 成为群组成员：

**groupMembership**：表示在 DataHub 内管理的 CorpGroups 中的成员关系，或从外部系统同步而来的成员关系。这会创建 `IsMemberOfGroup` 关系。

**nativeGroupMembership**：表示在外部身份提供商原生群组（如 Active Directory 组）中的成员关系。这会创建 `IsMemberOfNativeGroup` 关系。

两个 aspect 都存储群组 URN 数组，允许用户同时属于多个群组。

### 角色成员关系

`roleMembership` aspect 将用户与 DataHub 角色关联起来，这些角色定义了他们 在平台内的权限和访问能力。

**关键字段：**

- **roles**：分配给用户的 DataHubRole URN 数组

这会创建 `IsMemberOfRole` 关系，是 DataHub 基于角色的访问控制（RBAC）系统的核心。

### 认证凭据

`corpUserCredentials` aspect 存储 DataHub 原生用户（直接在 DataHub 中创建，而非从外部身份提供商同步的用户）的认证信息。

**关键字段：**

- **salt**：用于密码哈希的盐值
- **hashedPassword**：哈希后的密码
- **passwordResetToken**：用于密码重置操作的可选令牌
- **passwordResetTokenExpirationTimeMillis**：重置令牌的过期时间

该 aspect 仅用于原生认证，对于通过 SSO 或 LDAP 认证的用户不会被填充。

### 用户设置

`corpUserSettings` aspect 存储用户针对 DataHub UI 和功能的个人偏好设置。

**关键字段：**

- **appearance**：控制 DataHub UI 外观与体验的设置
  - `showSimplifiedHomepage`：是否显示仅包含数据集、图表和仪表板的简化首页
  - `showThemeV2`：是否使用 V2 主题
- **views**：Views 功能的设置
  - `defaultView`：用户的默认 DataHub 视图
- **notificationSettings**：通知偏好
- **homePage**：首页体验的设置
  - `pageTemplate`：用户的默认页面模板
  - `dismissedAnnouncementUrns**：用户已忽略的公告列表

### 来源

`origin` aspect 跟踪用户实体的来源，区分 DataHub 原生用户与从外部系统同步而来的用户。

**关键字段：**

- **type**：取值为 "NATIVE" 或 "EXTERNAL"
- **externalType**：外部身份提供商的名称（例如 "AzureAD"、"Okta"、"LDAP"）

该信息有助于了解用户数据的权威来源以及管理同步流程。

### Slack 集成

`slackUserInfo` aspect 包含用户 Slack 身份的详细信息，从而在 DataHub 内支持丰富的 Slack 集成功能。

**关键字段：**

- **slackInstance**：Slack 工作区的 URN
- **id**：唯一的 Slack 成员 ID
- **name**：Slack 用户名
- **realName**：Slack 中的真实姓名
- **displayName**：Slack 中的显示名称
- **email**：与 Slack 账户关联的电子邮件地址
- **teamId**：Slack 团队/工作区 ID
- **isDeleted**、**isAdmin**、**isOwner**、**isPrimaryOwner**、**isBot**：账户状态标志
- **timezone** 和 **timezoneOffset**：用户的时区信息
- **title**：来自 Slack 的职位
- **phone**：来自 Slack 的电话号码
- **profilePictureUrl**：Slack 头像图片的 URL
- **statusText** 和 **statusEmoji**：当前的 Slack 状态

### 标签、结构化属性与表单

与其他 DataHub 实体一样，CorpUser 支持：

- **globalTags**：附加到用户实体用于分类的标签
- **structuredProperties**：由你的组织数据模型定义的自定义属性
- **forms**：可附加到用户以收集结构化信息的表单
- **status**：用于软删除的通用状态 aspect

这些通用 aspect 支持灵活的元数据管理，并与 DataHub 更广泛的元数据框架集成。

## 代码示例

### 创建 CorpUser

创建 CorpUser 最简单的方式是使用高层 Python SDK：


**Python SDK：创建基础用户**

```python
# Inlined from /metadata-ingestion/examples/library/corpuser_create_basic.py
# metadata-ingestion/examples/library/corpuser_create_basic.py
import os

from datahub.api.entities.corpuser.corpuser import CorpUser
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

# Create a basic user with essential information
user = CorpUser(
    id="jdoe",
    display_name="John Doe",
    email="jdoe@company.com",
    title="Senior Data Engineer",
    first_name="John",
    last_name="Doe",
    full_name="John Doe",
    department_name="Data Engineering",
    country_code="US",
)

# Create graph client
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
datahub_graph = DataHubGraph(DataHubGraphConfig(server=gms_server, token=token))

# Emit the user entity
for event in user.generate_mcp():
    datahub_graph.emit(event)

print(f"Created user {user.urn}")

```



### 创建带群组成员关系的 CorpUser

用户通常是群组成员。以下是创建用户并将其分配到群组的方法：


**Python SDK：创建带群组成员关系的用户**

```python
# Inlined from /metadata-ingestion/examples/library/corpuser_create_with_groups.py
# metadata-ingestion/examples/library/corpuser_create_with_groups.py

from datahub.api.entities.corpuser.corpuser import CorpUser
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

# Create a user with group memberships
user = CorpUser(
    id="jsmith",
    display_name="Jane Smith",
    email="jsmith@company.com",
    title="Data Analyst",
    first_name="Jane",
    last_name="Smith",
    full_name="Jane Smith",
    department_name="Analytics",
    country_code="US",
    groups=["data-engineering", "analytics-team"],
)

# Create graph client
datahub_graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Emit the user entity with group memberships
for event in user.generate_mcp():
    datahub_graph.emit(event)

print(f"Created user {user.urn} with group memberships")

```



### 更新用户档案信息

要为已有用户更新可编辑的档案信息：


**Python SDK：更新用户档案**

```python
# Inlined from /metadata-ingestion/examples/library/corpuser_update_profile.py
# metadata-ingestion/examples/library/corpuser_update_profile.py

from datahub.api.entities.corpuser.corpuser import CorpUser, CorpUserGenerationConfig
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

# Update a user's editable profile information
user = CorpUser(
    id="jdoe",
    email="jdoe@company.com",
    description="Passionate about data quality and building reliable data pipelines. "
    "10+ years of experience in data engineering.",
    slack="@jdoe",
    phone="+1-555-0123",
    picture_link="https://company.com/photos/jdoe.jpg",
)

# Create graph client
datahub_graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Emit with override_editable=True to update editable fields
for event in user.generate_mcp(
    generation_config=CorpUserGenerationConfig(override_editable=True)
):
    datahub_graph.emit(event)

print(f"Updated profile for user {user.urn}")

```



### 为用户添加标签

可以为用户打标签以便分类和发现：


**Python SDK：为用户添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/corpuser_add_tag.py
# metadata-ingestion/examples/library/corpuser_add_tag.py

from datahub.emitter.mce_builder import make_tag_urn, make_user_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.metadata.schema_classes import GlobalTagsClass, TagAssociationClass

# User to add tag to
user_urn = make_user_urn("jdoe")

# Tag to add
tag_urn = make_tag_urn("DataEngineering")

# Create graph client
datahub_graph = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Read current tags
current_tags = datahub_graph.get_aspect(
    entity_urn=user_urn, aspect_type=GlobalTagsClass
)

# Initialize tags if they don't exist
if current_tags is None:
    current_tags = GlobalTagsClass(tags=[])

# Check if tag already exists
tag_exists = any(tag.tag == tag_urn for tag in current_tags.tags)

if not tag_exists:
    # Add the new tag
    new_tag = TagAssociationClass(tag=tag_urn)
    current_tags.tags.append(new_tag)

    # Create MCP to update the tags
    mcp = MetadataChangeProposalWrapper(
        entityUrn=user_urn,
        aspect=current_tags,
    )

    # Emit the change
    datahub_graph.emit(mcp)
    print(f"Added tag {tag_urn} to user {user_urn}")
else:
    print(f"Tag {tag_urn} already exists on user {user_urn}")

```



### 通过 REST API 查询用户

可以使用 REST API 获取用户信息：


**REST API：获取用户信息**

```bash
# Get a user by URN
curl -X GET "http://localhost:8080/entities/urn%3Ali%3Acorpuser%3Ajdoe" \
  -H "Authorization: Bearer <your-access-token>"

# Get specific aspects of a user
curl -X GET "http://localhost:8080/aspects/urn%3Ali%3Acorpuser%3Ajdoe?aspect=corpUserInfo&aspect=corpUserEditableInfo&aspect=groupMembership" \
  -H "Authorization: Bearer <your-access-token>"
```



### 搜索用户

可以使用 GraphQL API 或搜索 API 搜索用户：


**GraphQL：搜索用户**

```graphql
query searchUsers {
  search(input: { type: CORP_USER, query: "john", start: 0, count: 10 }) {
    start
    count
    total
    searchResults {
      entity {
        ... on CorpUser {
          urn
          username
          properties {
            displayName
            email
            title
            fullName
          }
          editableProperties {
            aboutMe
            teams
            skills
            slack
          }
        }
      }
    }
  }
}
```



## 集成点

### 与其他实体的关系

CorpUser 与其他 DataHub 实体有若干重要关系：

**所有权关系：**

- CorpUser 可以是数据集、仪表板、图表、数据流以及 DataHub 中几乎任何其他实体的所有者
- 所有权关系包含所有者类型（例如 DATAOWNER、TECHNICAL_OWNER、BUSINESS_OWNER）

**群组关系：**

- 用户通过 `IsMemberOfGroup` 关系隶属于 CorpGroups
- 群组也可以是资产的所有者，提供继承式所有权

**角色关系：**

- 用户通过 `IsMemberOfRole` 关系被分配 DataHub 角色
- 角色定义 DataHub 内的权限和访问级别

**组织层级：**

- `corpUserInfo` 中的 `managerUrn` 字段创建 `ReportsTo` 关系
- 这使组织结构和汇报关系链得以可视化

**平台使用：**

- `corpUserEditableInfo` 中的 `platforms` 字段创建 `IsUserOf` 关系
- 这有助于识别用户常用的平台

**Persona 分配：**

- 用户可以通过 `persona` 字段被分配 DataHub persona
- 这有助于按角色对用户分类并定制其使用体验

### 身份提供商集成

CorpUser 通常从外部身份提供商同步而来：

**LDAP/Active Directory：**

- 大多数组织使用 LDAP 连接器自动同步用户信息
- 用户名通常对应 LDAP 的 `uid` 或 `sAMAccountName`
- 档案信息来自 LDAP 属性

**SSO 提供商（Okta、Azure AD 等）：**

- SSO 集成可在首次登录时自动置备用户
- SSO 提供商的用户属性填充 `corpUserInfo` aspect
- `origin` aspect 跟踪 SSO 提供商作为来源

**DataHub 原生用户：**

- 用户可以直接在 DataHub 中创建，用于测试或小型部署
- 这些用户的凭据存储在 `corpUserCredentials` aspect 中
- 它们被标记为 `origin.type = NATIVE`

### 认证与授权

CorpUser 是 DataHub 安全模型的核心：

**认证：**

- 原生用户使用用户名/密码认证
- SSO 用户通过其身份提供商认证
- API 令牌可以关联到用户以进行编程式访问

**授权（RBAC）：**

- 用户通过 `roleMembership` aspect 被分配角色
- 角色定义用户可以执行的操作
- 策略可以引用用户或群组以授予/限制访问

**元数据访问：**

- 用户只能看到自己有权查看的元数据
- 所有权和群组成员关系会影响用户可以编辑的内容
- 策略可以针对特定用户，也可以基于群组

## 值得注意的例外情况

### 系统用户

CorpUser 既可以表示自然人用户，也可以表示系统/服务账户。`corpUserInfo` 中的 `system` 字段区分这两者：

- **自然人用户**（`system: false`）：与 DataHub 交互的真实人员
- **系统账户**（`system: true`）：服务账户、自动化流程或系统级操作

系统用户应被正确标记，以便在报表、所有权列表和访问审查中区分它们。

### 已弃用的 active 字段

`corpUserInfo` 中的 `active` 字段已弃用。请改用 `corpUserStatus` aspect，它提供：

- 比仅区分活动/非活动更细粒度的状态选项
- 状态变更的审计信息
- 更好的置备工作流支持

在处理用户时，优先检查 `corpUserStatus.status` 而非 `corpUserInfo.active`。

### 用户名不可变性

用户名（位于 `corpUserKey` 中）在用户创建后即不可更改。如果某用户的用户名在源系统中发生变更：

- 必须使用新用户名创建新的 CorpUser 实体
- 所有权及其他关系需要迁移到新实体
- 旧用户可以使用 `status` aspect 进行软删除

请仔细规划用户名策略，以避免频繁的用户名变更。

### 显示名称的优先级

显示名称可能出现在多个 aspect 中，其优先级如下：

1. `corpUserEditableInfo.displayName`（用户指定，优先级最高）
2. `corpUserInfo.displayName`（来自身份提供商）
3. `corpUserInfo.fullName`（未设置显示名称时的回退值）

DataHub UI 按此顺序解析，显示可获得的最具体值。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](10-corpuser.md)。。
