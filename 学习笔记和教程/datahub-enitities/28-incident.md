---
title: 事件（故障）
entity: incident
order: 28
source: https://docs.datahub.com/docs/generated/metamodel/entities/incident.md
---

# 事件（故障）

事件（Incident）表示影响 DataHub 中数据资产的数据质量问题、运维故障或任何其他类型的问题。它们提供了一种结构化的方式，用于跨数据集、仪表板、图表、数据流、数据任务和模式字段跟踪、管理并解决问题。事件通过记录问题、分派责任、跟踪解决进度以及维护数据质量事件审计轨迹，帮助团队保持数据可靠性。

## 标识（Identity）

事件由系统生成的 UUID 字符串唯一标识。与大多数从外部系统获取身份的其他 DataHub 实体不同，事件在 DataHub 内部创建，并在创建时被赋予唯一标识符。

事件的 URN 结构为：

```
urn:li:incident:<uuid>
```

示例：

```
urn:li:incident:a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d
```

UUID 在事件被登记时由系统自动生成，确保该 DataHub 实例中所有事件的全局唯一性。

## 重要能力

### 事件类型

事件可以按类型分类，以帮助团队理解问题的性质。DataHub 支持若干预定义的事件类型以及自定义类型：

- **FRESHNESS**：当数据未在预期时间窗口内更新时触发。通常由检测到陈旧数据的新鲜度断言发起。
- **VOLUME**：当数据量超出预期范围（数据过多或过少）时发起。通常由数据量断言生成。
- **FIELD**：表示特定字段值存在问题，例如空值、非法格式或超出可接受范围的取值。与字段级断言相关联。
- **SQL**：由使用自定义查询校验数据的 SQL 断言触发。
- **DATA_SCHEMA**：当检测到 schema 变更时发起，例如新增列、删除列或类型变更。
- **OPERATIONAL**：通用运维事件，例如管道失败、权限问题或系统错误。
- **CUSTOM**：用户自定义的事件类型，用于组织特有的问题。使用 CUSTOM 类型时，必须提供 `customType` 字符串以描述该事件类别。

### 事件状态与生命周期

事件遵循从创建到解决的生命周期，通过状态与阶段字段进行跟踪：

#### 状态（State）

顶层状态表示事件处于活跃还是已解决：

- **ACTIVE**：事件仍在进行中，需要关注或采取行动。
- **RESOLVED**：事件已处理完毕，不再处于活跃状态。

#### 生命周期阶段

事件可以被分派到特定阶段，代表其在解决流程中所处的位置：

- **TRIAGE**：正在评估事件的影响范围与优先级。对于新上报的事件，这通常是第一个阶段。
- **INVESTIGATION**：被指派团队正在调查事件的根因。
- **WORK_IN_PROGRESS**：事件处于整改阶段，正在积极开展修复工作。
- **FIXED**：事件已通过纠正措施解决（整改已完成）。
- **NO_ACTION_REQUIRED**：事件无需采取行动即已解决，例如属于误报、预期行为或自行恢复。

状态中还包含一个 `message` 字段用于提供当前状态的上下文，以及一个 `lastUpdated` 时间戳用于跟踪状态的最后修改时间。

### 优先级

事件可以被赋予优先级，以帮助团队分诊并聚焦最关键的问题：

- **CRITICAL**（优先级 0）：严重问题，需要立即关注，对业务运营或数据质量有显著影响。
- **HIGH**（优先级 1）：重要问题，应尽快处理，但并未立即造成阻塞。
- **MEDIUM**（优先级 2）：中等程度的问题，应在正常工作节奏中处理。
- **LOW**（优先级 3）：轻微问题，可在时间允许时处理。

优先级字段在数据模型中以整数（0-3）存储，便于程序化排序与过滤。

### 被指派人

事件可以指派给一个或多个负责调查与解决问题的用户或群组。每个指派人包含：

- **actor**：被指派到该事件的用户（corpUser）或群组（corpGroup）的 URN。
- **assignedAt**：记录由谁在何时完成指派的审计戳。

多个指派人可以协作解决单个事件，便于引入跨职能团队。

### 受影响实体

事件的一项关键能力是将其链接到一个或多个受影响的数据资产。`entities` 字段包含一个 URN 数组，引用受该事件影响的资产。支持的实体类型包括：

- **dataset**：表、视图、流或其他数据集合
- **chart**：数据可视化
- **dashboard**：包含多个图表的仪表板页面
- **dataFlow**：管道或工作流
- **dataJob**：管道中的单个任务或作业
- **schemaField**：数据集内的特定字段/列

这种关联使用户能够查看影响某个特定资产的所有事件，并了解事件在多个资产间的影响范围。

### 事件来源

`source` 字段跟踪事件是如何创建的：

- **MANUAL**：事件由用户通过 UI 或 API 手动创建。
- **ASSERTION_FAILURE**：事件由失败的断言自动发起。此时 `sourceUrn` 字段包含触发该事件的断言的 URN。

这一区分有助于团队理解哪些事件需要人工排查，哪些来自自动化监控。

### 时间跟踪

事件维护详细的时间信息：

- **startedAt**：事件实际开始的时间（可能早于上报时间）。Search V3 会将其复制到 `sourceCreatedAt`。
- **created**：已废弃。记录由谁在 DataHub 中登记该事件及何时登记的审计戳。请改用 `systemMetadata.aspectCreated`。该字段仍保留且在 Search V2 中保持索引，Search V3 不再索引它。
- **lastUpdated**：状态上的审计戳，跟踪最近一次状态变更。

这些时间数据帮助团队理解事件时间线、计算平均检测时间（MTTD）与平均解决时间（MTTR）。

### 标签

与其他 DataHub 实体一样，事件可以使用 `globalTags` aspect 打标签。标签有助于对事件分类与过滤，便于查找相关问题或按类别分析事件模式。

## 代码示例

### 创建事件

下面的示例演示如何创建一个新事件并将其关联到存在数据质量问题的数据集。


**Python SDK：创建基础事件**

```python
# Inlined from /metadata-ingestion/examples/library/incident_create.py
# metadata-ingestion/examples/library/incident_create.py
import os
import uuid

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.urns import IncidentUrn

# Configuration
gms_endpoint = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_endpoint, token=token)

# Generate a unique incident ID
incident_id = str(uuid.uuid4())
incident_urn = IncidentUrn(incident_id)

# Create the dataset URN that this incident affects
dataset_urn = builder.make_dataset_urn(
    platform="snowflake", name="analytics.sales_fact", env="PROD"
)

# Get the current actor URN for audit stamps
actor_urn = builder.make_user_urn("datahub")
audit_stamp = models.AuditStampClass(
    time=int(builder.get_sys_time() * 1000),
    actor=actor_urn,
)

# Create the incident info aspect
incident_info = models.IncidentInfoClass(
    type=models.IncidentTypeClass.FRESHNESS,
    title="Sales data not updated in 48 hours",
    description="The sales_fact table has not been refreshed since 2023-10-15. Expected daily updates are missing, which may impact downstream reporting and dashboards.",
    entities=[dataset_urn],
    status=models.IncidentStatusClass(
        state=models.IncidentStateClass.ACTIVE,
        stage=models.IncidentStageClass.TRIAGE,
        message="Investigating potential pipeline failure",
        lastUpdated=audit_stamp,
    ),
    priority=0,  # CRITICAL priority (0=CRITICAL, 1=HIGH, 2=MEDIUM, 3=LOW)
    source=models.IncidentSourceClass(type=models.IncidentSourceTypeClass.MANUAL),
    created=audit_stamp,
)

# Create and emit the metadata change proposal
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=str(incident_urn),
    aspect=incident_info,
)

emitter.emit(metadata_change_proposal)
print(f"Created incident {incident_urn} for dataset {dataset_urn}")
print(
    f"Incident details: type={incident_info.type}, priority={incident_info.priority}, status={incident_info.status.state}"
)

```



### 更新事件状态

随着事件在其生命周期中推进，需要更新其状态以反映当前状态与阶段。


**Python SDK：更新事件状态与阶段**

```python
# Inlined from /metadata-ingestion/examples/library/incident_update_status.py
# metadata-ingestion/examples/library/incident_update_status.py

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.urns import IncidentUrn

# Configuration
gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

# Specify the incident to update (use the incident ID from incident_create.py)
incident_id = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
incident_urn = IncidentUrn(incident_id)

# Retrieve the current incident info to preserve other fields
current_incident_info = graph.get_aspect(
    entity_urn=str(incident_urn),
    aspect_type=models.IncidentInfoClass,
)

if not current_incident_info:
    raise ValueError(f"Incident {incident_urn} not found")

# Get the current actor URN for audit stamps
actor_urn = builder.make_user_urn("jdoe")
audit_stamp = models.AuditStampClass(
    time=int(builder.get_sys_time() * 1000),
    actor=actor_urn,
)

# Update the status to reflect progress in resolving the incident
current_incident_info.status = models.IncidentStatusClass(
    state=models.IncidentStateClass.ACTIVE,
    stage=models.IncidentStageClass.WORK_IN_PROGRESS,
    message="Pipeline has been restarted. Monitoring for successful completion.",
    lastUpdated=audit_stamp,
)

# Optionally update priority if severity assessment changed
current_incident_info.priority = (
    1  # HIGH priority (0=CRITICAL, 1=HIGH, 2=MEDIUM, 3=LOW)
)

# Optionally assign team members to work on the incident
assignee1 = models.IncidentAssigneeClass(
    actor=builder.make_user_urn("jdoe"),
    assignedAt=audit_stamp,
)
assignee2 = models.IncidentAssigneeClass(
    actor=builder.make_user_urn("asmith"),
    assignedAt=audit_stamp,
)
current_incident_info.assignees = [assignee1, assignee2]

# Create and emit the metadata change proposal
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=str(incident_urn),
    aspect=current_incident_info,
)

emitter.emit(metadata_change_proposal)
print(f"Updated incident {incident_urn} status to {current_incident_info.status.state}")
print(
    f"Status details: stage={current_incident_info.status.stage}, message={current_incident_info.status.message}"
)
print(f"Priority updated to {current_incident_info.priority}")
print(f"Assigned to {len(current_incident_info.assignees)} team members")

```



### 为事件添加标签

可以为事件添加标签，以按团队、系统、严重程度或任何其他组织维度对其分类。


**Python SDK：为事件添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/incident_add_tag.py
# metadata-ingestion/examples/library/incident_add_tag.py

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.urns import IncidentUrn

# Configuration
gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

# Specify the incident to tag (use the incident ID from incident_create.py)
incident_id = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
incident_urn = IncidentUrn(incident_id)

# Create the tag URN
tag_urn = builder.make_tag_urn("data-quality")

# Get the current actor URN for audit stamps
actor_urn = builder.make_user_urn("datahub")
audit_stamp = models.AuditStampClass(
    time=int(builder.get_sys_time() * 1000),
    actor=actor_urn,
)

# Read current tags to preserve existing ones
current_tags = graph.get_aspect(
    entity_urn=str(incident_urn),
    aspect_type=models.GlobalTagsClass,
)

# Create tag association
tag_association = models.TagAssociationClass(
    tag=tag_urn,
    context="incident_categorization",
)

if current_tags:
    # Check if tag already exists
    tag_exists = any(existing_tag.tag == tag_urn for existing_tag in current_tags.tags)
    if not tag_exists:
        current_tags.tags.append(tag_association)
        updated_tags = current_tags
    else:
        print(f"Tag {tag_urn} already exists on incident {incident_urn}")
        updated_tags = current_tags
else:
    # No existing tags, create new GlobalTags aspect
    updated_tags = models.GlobalTagsClass(tags=[tag_association])

# Create and emit the metadata change proposal
metadata_change_proposal = MetadataChangeProposalWrapper(
    entityUrn=str(incident_urn),
    aspect=updated_tags,
)

emitter.emit(metadata_change_proposal)
print(f"Added tag {tag_urn} to incident {incident_urn}")
print(f"Incident now has {len(updated_tags.tags)} tag(s)")

```



### 通过 Python SDK 查询事件

创建事件后，可以使用 Python SDK 检索它们，以便与外部监控或工单系统集成。


**Python SDK：查询事件**

```python
# Inlined from /metadata-ingestion/examples/library/incident_query_rest_api.py
# metadata-ingestion/examples/library/incident_query_rest_api.py
import os

import datahub.metadata.schema_classes as models
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.urns import IncidentUrn

# Configuration
gms_endpoint = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint, token=token))

# Specify the incident to query (use the incident ID from incident_create.py)
incident_id = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
incident_urn = IncidentUrn(incident_id)

# Query the incident info aspect
incident_info = graph.get_aspect(
    entity_urn=str(incident_urn),
    aspect_type=models.IncidentInfoClass,
)

if incident_info is None:
    raise SystemExit(f"Incident not found: {incident_urn}")

print(f"Incident: {incident_urn}")
print(f"  Type: {incident_info.type}")
print(f"  Title: {incident_info.title}")
print(f"  Description: {incident_info.description}")
print(f"  Priority: {incident_info.priority}")
print(f"  Status State: {incident_info.status.state}")
print(f"  Status Stage: {incident_info.status.stage}")
print(f"  Status Message: {incident_info.status.message}")
print(f"  Affected Entities: {len(incident_info.entities)}")
for entity_urn in incident_info.entities:
    print(f"    - {entity_urn}")

if incident_info.assignees:
    print(f"  Assignees: {len(incident_info.assignees)}")
    for assignee in incident_info.assignees:
        print(f"    - {assignee.actor}")

if incident_info.source:
    print(f"  Source Type: {incident_info.source.type}")
    if incident_info.source.sourceUrn:
        print(f"  Source URN: {incident_info.source.sourceUrn}")

print(f"  Created: {incident_info.created.time} by {incident_info.created.actor}")
print(
    f"  Last Updated: {incident_info.status.lastUpdated.time} by {incident_info.status.lastUpdated.actor}"
)

# Query the tags aspect
tags = graph.get_aspect(
    entity_urn=str(incident_urn),
    aspect_type=models.GlobalTagsClass,
)

if tags:
    print(f"  Tags: {len(tags.tags)}")
    for tag_association in tags.tags:
        print(f"    - {tag_association.tag}")

```



## 集成点

### 与断言的关系

事件与 DataHub 的断言框架紧密集成。当断言（数据质量检查）失败且配置为发起事件时，会自动创建事件实体。这些事件：

- 通过 `sourceUrn` 字段引用触发它们的断言
- 继承断言的类型（FRESHNESS、VOLUME、FIELD、SQL、DATA_SCHEMA）
- 链接到该断言所监控的资产
- 可在断言级别配置失败是否生成事件

该集成为被监控的数据质量检查提供了自动创建事件的能力。

### 资产上的事件摘要

可拥有事件的 DataHub 实体（datasets、dashboards、charts、dataFlows、dataJobs、schemaFields）包含 `incidentsSummary` aspect。该 aspect 提供：

- 影响该实体的活跃事件数量
- 已解决事件的数量
- 活跃事件的优先级分布
- 无需直接查询事件实体即可快速访问事件详情

该摘要在 UI 的资产页面显示，使用户能立即了解数据质量问题。

### GraphQL 操作

DataHub GraphQL API 提供了多个用于处理事件的操作：

- **raiseIncident**：以指定的类型、优先级、状态和受影响实体创建新事件
- **updateIncident**：更新事件属性，包括标题、描述、状态、优先级、被指派人和受影响实体
- **updateIncidentStatus**：专门更新事件的状态与阶段
- **entityIncidents**：查询影响某个特定实体的全部事件

这些操作由 DataHub UI 使用，也可由外部应用直接调用。

### 权限控制

事件操作遵循 DataHub 的权限模型。用户必须对某个实体拥有 `EDIT_ENTITY_INCIDENTS` 特权，才能：

- 创建影响该实体的事件
- 更新与该实体关联的事件
- 变更影响该实体的事件的状态

这确保只有具备相应权限的用户才能管理敏感数据资产的事件。

### 健康状态

事件会影响 DataHub 实体的整体健康状态。存在活跃 CRITICAL 或 HIGH 优先级事件的资产可能在 UI 中被标记为不健康，帮助用户快速识别有问题的数据资产。

## 显著的例外情况

### 单个与多个受影响实体

虽然数据模型支持影响多个实体的事件（通过 `entities` 数组），但部分 GraphQL resolver 在处理多实体事件时目前存在限制。具体而言，`UpdateIncidentStatusResolver` 目前仅针对数组中的第一个实体检查权限。代码中将此标记为未来增强的 TODO。

创建事件时建议：

- 当多个实体受同一根因影响时使用多个实体（例如某上游数据质量问题影响的所有下游数据集）
- 注意用户需要拥有所有受影响实体的相应权限才能更新该事件
- 考虑多实体事件在展示事件详情时对 UI 的影响

### 优先级字段类型

在 PDL 模型中，优先级字段以整数（0-3）而非枚举形式存储。schema 注释中将其标记为未来可能的改进点。GraphQL 层提供了枚举接口（CRITICAL、HIGH、MEDIUM、LOW）映射到这些整数值，但底层存储使用整数。

使用底层 SDK 时，请使用整数值：

- 0 = CRITICAL
- 1 = HIGH
- 2 = MEDIUM
- 3 = LOW

### 自动事件与手动事件

由断言失败自动创建的事件不能将 `source` 字段改为 MANUAL，反之亦然。该字段在创建时即被设定，反映事件的来源。这一区别对报表和分析很重要，它帮助团队了解自动化监控与手动事件上报各自的成效。

### 状态消息长度

虽然 schema 中对状态 `message` 字段没有明确的长度限制，但 UI 组件可能会截断过长的消息。建议保持状态消息简洁（500 字符以内），更长的说明请使用事件的 `description` 字段。

### 事件保留

当受影响实体被移除时，事件不会被自动删除。这会在资产被弃用或删除后仍保留数据质量问题的历史记录。但这可能导致引用已不存在实体的孤儿事件。如果这在你的组织中成为问题，建议为关联已删除资产的事件实现清理流程。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](28-incident.md)。
