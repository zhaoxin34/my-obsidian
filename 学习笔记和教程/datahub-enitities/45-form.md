---
title: 表单
entity: form
order: 45
source: https://docs.datahub.com/docs/generated/metamodel/entities/form.md
---

# 表单

表单（Form）实体是 DataHub 元数据模型中的核心实体，用于支持结构化元数据采集与合规工作。表单提供了一种集中化、基于模板的方式，通过协作式的众包工作流为各类数据资产采集关键元数据。

## 标识

表单通过由创建者选定的唯一字符串标识符进行标识。

表单 URN 的结构为：`urn:li:form:<form-id>`

例如：`urn:li:form:metadataInitiative2024`

表单标识符应当有意义且具有描述性，通常代表该表单所属的专项工作或用途（例如 `piiClassification2024`、`dataQualityCompliance`、`retentionPolicyForm`）。

## 重要能力

### 表单元数据与配置

表单通过 `formInfo` aspect 定义，其中包含表单的全部核心信息：

- **名称与描述**：表单用途的展示名称与详细描述
- **类型**：支持两种类型：
  - `COMPLETION`：纯粹用于在实体上采集元数据字段的表单
  - `VERIFICATION`：用于验证实体是否通过特定元数据字段的存在而符合某项策略的表单
- **提示项（Prompt）**：用户需要作答的问题列表。每个提示项代表一项填写特定元数据的要求。目前提示项支持：
  - `STRUCTURED_PROPERTY`：将结构化属性应用到实体的提示项
  - `FIELDS_STRUCTURED_PROPERTY`：将结构化属性应用到数据集模式字段（列）的提示项
- **执行者指派**：定义由谁完成该表单。表单可以指派给：
  - 资产所有者（默认）
  - 指定用户
  - 指定群组

下面是表单元数据的一个示例：

**Python SDK：创建表单**

```python
# Inlined from /metadata-ingestion/examples/library/form_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Imports for metadata model classes
from datahub.metadata.schema_classes import (
    FormActorAssignmentClass,
    FormInfoClass,
    FormPromptClass,
    FormPromptTypeClass,
    FormTypeClass,
    StructuredPropertyParamsClass,
)
from datahub.metadata.urns import FormUrn

# Use the structured property created by structured_property_create_basic.py
retention_property_urn = "urn:li:structuredProperty:io.acryl.privacy.retentionTime"

# define the prompts for our form
prompt_1 = FormPromptClass(
    id="1",  # ensure IDs are globally unique
    title="Data Retention Policy",
    type=FormPromptTypeClass.STRUCTURED_PROPERTY,  # structured property type prompt
    structuredPropertyParams=StructuredPropertyParamsClass(urn=retention_property_urn),
    required=True,
)
prompt_2 = FormPromptClass(
    id="2",  # ensure IDs are globally unique
    title="Field-Level Retention",
    type=FormPromptTypeClass.FIELDS_STRUCTURED_PROPERTY,  # structured property prompt on dataset schema fields
    structuredPropertyParams=StructuredPropertyParamsClass(urn=retention_property_urn),
    required=False,  # dataset schema fields prompts should not be required
)

form_urn = FormUrn("metadata_initiative_1")
form_info_aspect = FormInfoClass(
    name="Metadata Initiative 2024",
    description="Please respond to this form for metadata compliance purposes",
    type=FormTypeClass.VERIFICATION,
    actors=FormActorAssignmentClass(owners=True),
    prompts=[prompt_1, prompt_2],
)

event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=form_info_aspect,
)

# Create rest emitter
rest_emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)
rest_emitter.emit_mcp(event)
print(f"Created form: {form_urn}")

```

### 动态表单指派

表单可以通过两种方式指派给实体：

1. **显式指派**：直接将表单指派给特定的实体 URN
2. **动态指派**：使用 `dynamicFormAssignment` aspect 自动将表单指派给符合特定条件的实体

`dynamicFormAssignment` aspect 通过指定筛选器实现基于规则的表单指派。符合筛选条件的实体将自动应用该表单。筛选器支持：

- 实体类型（例如 数据集、仪表板、图表）
- 平台（例如 snowflake、bigquery、postgres）
- 域归属
- 容器归属

这种动态方式对于大规模合规工作尤为有用：你希望把表单应用到某一类型的所有资产，或某个特定域内的全部资产时尤其如此。

**Python SDK：使用筛选器动态指派表单**

```python
# Inlined from /metadata-ingestion/examples/library/form_create_with_dynamic_assignment.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    CriterionClass,
    DynamicFormAssignmentClass,
    FilterClass,
    FormActorAssignmentClass,
    FormInfoClass,
    FormPromptClass,
    FormPromptTypeClass,
    FormTypeClass,
    StructuredPropertyParamsClass,
)
from datahub.metadata.urns import FormUrn

# Create a form that will be dynamically assigned to all Snowflake datasets
# in the "Finance" domain

# Define the form metadata
form_urn = FormUrn("snowflake_finance_compliance")
form_info = FormInfoClass(
    name="Snowflake Finance Data Compliance",
    description="Compliance form for all Snowflake datasets in the Finance domain",
    type=FormTypeClass.VERIFICATION,
    actors=FormActorAssignmentClass(owners=True),
    prompts=[
        FormPromptClass(
            id="retention_time_prompt",
            title="Data Retention Period",
            description="Specify how long this data should be retained",
            type=FormPromptTypeClass.STRUCTURED_PROPERTY,
            structuredPropertyParams=StructuredPropertyParamsClass(
                urn="urn:li:structuredProperty:io.acryl.dataRetentionTime"
            ),
            required=True,
        ),
        FormPromptClass(
            id="pii_classification_prompt",
            title="PII Classification",
            description="Classify whether this dataset contains PII",
            type=FormPromptTypeClass.STRUCTURED_PROPERTY,
            structuredPropertyParams=StructuredPropertyParamsClass(
                urn="urn:li:structuredProperty:io.acryl.piiClassification"
            ),
            required=True,
        ),
    ],
)

# Define dynamic assignment filter
# This form will be assigned to all entities matching these criteria
dynamic_assignment = DynamicFormAssignmentClass(
    filter=FilterClass(
        criteria=[
            CriterionClass(
                field="platform",
                values=["urn:li:dataPlatform:snowflake"],
                condition="EQUAL",
            ),
            CriterionClass(
                field="domains",
                values=["urn:li:domain:finance"],
                condition="EQUAL",
            ),
            CriterionClass(
                field="_entityType",
                values=["urn:li:entityType:dataset"],
                condition="EQUAL",
            ),
        ]
    )
)

# Create rest emitter
rest_emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

# Emit the form info
form_info_event = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=form_info,
)
rest_emitter.emit(form_info_event)

# Emit the dynamic assignment
dynamic_assignment_event = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=dynamic_assignment,
)
rest_emitter.emit(dynamic_assignment_event)

print(
    f"Created form {form_urn} with dynamic assignment to Snowflake datasets in Finance domain"
)

```

### 实体上的表单指派

当表单被指派给实体时（无论显式还是动态），指派关系都通过目标实体上的 `forms` aspect 进行追踪。该 aspect 维护：

- **未完成的表单**：仍有提示项待完成的表单
- **已完成的表单**：所有必填提示项均已作答的表单
- **验证记录**：对于验证类表单，记录哪些表单已被成功验证
- **提示项状态**：对每个表单分别追踪哪些提示项已完成、哪些尚未完成，并附带时间戳

这使 DataHub 能够围绕表单完成情况提供进度追踪、通知与分析。

### 归属

表单可以通过标准的 `ownership` aspect 归属所有者。表单的所有者通常是负责管理和维护该表单的治理或合规团队成员。

**Python SDK：为表单添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/form_add_owner.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)
from datahub.metadata.urns import CorpUserUrn, FormUrn

# Form URN to add owner to
form_urn = FormUrn("metadata_initiative_2024")

# Create ownership aspect
ownership = OwnershipClass(
    owners=[
        OwnerClass(
            owner=str(CorpUserUrn("governance_team")),
            type=OwnershipTypeClass.TECHNICAL_OWNER,
        )
    ],
    lastModified=AuditStampClass(
        time=0, actor="urn:li:corpuser:datahub", impersonator=None
    ),
)

# Create and emit metadata change proposal
event = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=ownership,
)

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
rest_emitter.emit(event)

print(f"Added owner to form {form_urn}")

```

## 代码示例

### 创建与管理表单

**Python SDK：创建包含多个提示项的验证表单**

```python
# Inlined from /metadata-ingestion/examples/library/form_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Imports for metadata model classes
from datahub.metadata.schema_classes import (
    FormActorAssignmentClass,
    FormInfoClass,
    FormPromptClass,
    FormPromptTypeClass,
    FormTypeClass,
    StructuredPropertyParamsClass,
)
from datahub.metadata.urns import FormUrn

# Use the structured property created by structured_property_create_basic.py
retention_property_urn = "urn:li:structuredProperty:io.acryl.privacy.retentionTime"

# define the prompts for our form
prompt_1 = FormPromptClass(
    id="1",  # ensure IDs are globally unique
    title="Data Retention Policy",
    type=FormPromptTypeClass.STRUCTURED_PROPERTY,  # structured property type prompt
    structuredPropertyParams=StructuredPropertyParamsClass(urn=retention_property_urn),
    required=True,
)
prompt_2 = FormPromptClass(
    id="2",  # ensure IDs are globally unique
    title="Field-Level Retention",
    type=FormPromptTypeClass.FIELDS_STRUCTURED_PROPERTY,  # structured property prompt on dataset schema fields
    structuredPropertyParams=StructuredPropertyParamsClass(urn=retention_property_urn),
    required=False,  # dataset schema fields prompts should not be required
)

form_urn = FormUrn("metadata_initiative_1")
form_info_aspect = FormInfoClass(
    name="Metadata Initiative 2024",
    description="Please respond to this form for metadata compliance purposes",
    type=FormTypeClass.VERIFICATION,
    actors=FormActorAssignmentClass(owners=True),
    prompts=[prompt_1, prompt_2],
)

event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=form_info_aspect,
)

# Create rest emitter
rest_emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)
rest_emitter.emit_mcp(event)
print(f"Created form: {form_urn}")

```

**Python SDK：创建带动态指派的表单**

```python
# Inlined from /metadata-ingestion/examples/library/form_create_with_dynamic_assignment.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    CriterionClass,
    DynamicFormAssignmentClass,
    FilterClass,
    FormActorAssignmentClass,
    FormInfoClass,
    FormPromptClass,
    FormPromptTypeClass,
    FormTypeClass,
    StructuredPropertyParamsClass,
)
from datahub.metadata.urns import FormUrn

# Create a form that will be dynamically assigned to all Snowflake datasets
# in the "Finance" domain

# Define the form metadata
form_urn = FormUrn("snowflake_finance_compliance")
form_info = FormInfoClass(
    name="Snowflake Finance Data Compliance",
    description="Compliance form for all Snowflake datasets in the Finance domain",
    type=FormTypeClass.VERIFICATION,
    actors=FormActorAssignmentClass(owners=True),
    prompts=[
        FormPromptClass(
            id="retention_time_prompt",
            title="Data Retention Period",
            description="Specify how long this data should be retained",
            type=FormPromptTypeClass.STRUCTURED_PROPERTY,
            structuredPropertyParams=StructuredPropertyParamsClass(
                urn="urn:li:structuredProperty:io.acryl.dataRetentionTime"
            ),
            required=True,
        ),
        FormPromptClass(
            id="pii_classification_prompt",
            title="PII Classification",
            description="Classify whether this dataset contains PII",
            type=FormPromptTypeClass.STRUCTURED_PROPERTY,
            structuredPropertyParams=StructuredPropertyParamsClass(
                urn="urn:li:structuredProperty:io.acryl.piiClassification"
            ),
            required=True,
        ),
    ],
)

# Define dynamic assignment filter
# This form will be assigned to all entities matching these criteria
dynamic_assignment = DynamicFormAssignmentClass(
    filter=FilterClass(
        criteria=[
            CriterionClass(
                field="platform",
                values=["urn:li:dataPlatform:snowflake"],
                condition="EQUAL",
            ),
            CriterionClass(
                field="domains",
                values=["urn:li:domain:finance"],
                condition="EQUAL",
            ),
            CriterionClass(
                field="_entityType",
                values=["urn:li:entityType:dataset"],
                condition="EQUAL",
            ),
        ]
    )
)

# Create rest emitter
rest_emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

# Emit the form info
form_info_event = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=form_info,
)
rest_emitter.emit(form_info_event)

# Emit the dynamic assignment
dynamic_assignment_event = MetadataChangeProposalWrapper(
    entityUrn=str(form_urn),
    aspect=dynamic_assignment,
)
rest_emitter.emit(dynamic_assignment_event)

print(
    f"Created form {form_urn} with dynamic assignment to Snowflake datasets in Finance domain"
)

```

**Python SDK：将表单指派给特定实体**

```python
# Inlined from /metadata-ingestion/examples/library/form_assign_to_entities.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import FormAssociationClass, FormsClass
from datahub.metadata.urns import DatasetUrn, FormUrn

# Form to assign
form_urn = FormUrn("metadata_initiative_2024")

# Entities to assign the form to
dataset_urns = [
    DatasetUrn(platform="snowflake", name="prod.analytics.customer_data", env="PROD"),
    DatasetUrn(platform="snowflake", name="prod.analytics.sales_data", env="PROD"),
]

# Create rest emitter
rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Assign the form to each entity by updating the forms aspect
for dataset_urn in dataset_urns:
    # Create a forms aspect with the form marked as incomplete
    forms_aspect = FormsClass(
        incompleteForms=[FormAssociationClass(urn=str(form_urn))],
        completedForms=[],
        verifications=[],
    )

    # Emit the forms aspect for the entity
    event = MetadataChangeProposalWrapper(
        entityUrn=str(dataset_urn),
        aspect=forms_aspect,
    )
    rest_emitter.emit(event)
    print(f"Assigned form {form_urn} to entity {dataset_urn}")

print(f"Successfully assigned form to {len(dataset_urns)} entities")

```

**Python SDK：从实体上移除表单**

```python
# Inlined from /metadata-ingestion/examples/library/form_remove_from_entities.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import FormsClass
from datahub.metadata.urns import DatasetUrn, FormUrn

# Form to remove
form_urn = FormUrn("metadata_initiative_2024")

# Entities to remove the form from
dataset_urns = [
    DatasetUrn(platform="snowflake", name="prod.analytics.customer_data", env="PROD"),
    DatasetUrn(platform="snowflake", name="prod.analytics.sales_data", env="PROD"),
]

# Create rest emitter
rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Remove the form from each entity by setting empty forms aspect
for dataset_urn in dataset_urns:
    # Create an empty forms aspect
    # This will remove all form assignments from the entity
    forms_aspect = FormsClass(
        incompleteForms=[],
        completedForms=[],
        verifications=[],
    )

    # Emit the forms aspect for the entity
    event = MetadataChangeProposalWrapper(
        entityUrn=str(dataset_urn),
        aspect=forms_aspect,
    )
    rest_emitter.emit(event)
    print(f"Removed forms from entity {dataset_urn}")

print(f"Successfully removed forms from {len(dataset_urns)} entities")

```

### 查询表单

可以通过 REST API 查询表单，以获取表单定义并检查其指派状态。

**通过 REST API 查询表单**

```shell
curl 'http://localhost:8080/entities/urn%3Ali%3Aform%3AmetadataInitiative2024'
```

该请求会返回表单实体及其所有 aspect，其中包括 `formInfo`、`dynamicFormAssignment`（若已配置）以及 `ownership`。

**检查实体上的表单指派**

```shell
curl 'http://localhost:8080/entities/urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Asnowflake,mydb.schema.table,PROD)?aspects=forms'
```

该请求返回 `forms` aspect，展示该数据集上所有未完成与已完成的表单。

## 集成点

### 与其他实体的关系

表单在 DataHub 生态中有若干关键集成点：

1. **结构化属性**：表单主要通过提示项与结构化属性交互。每个提示项都可以要求用户在实体或模式字段上填写特定的结构化属性。

2. **资产（数据集、仪表板、图表等）**：表单被指派给数据资产以采集元数据。该关系通过以下方式追踪：

   - 目标实体上的 `forms` aspect
   - 表单上的 `dynamicFormAssignment` 筛选条件

3. **用户与群组**：表单被指派给负责完成它们的特定执行者（用户或群组）。这形成如下工作流：

   - 表单出现在执行者的任务列表中
   - 执行者收到关于待处理表单的通知
   - 按用户分别维护完成情况

4. **域与容器**：表单可依据域或容器归属自动指派，使治理团队能够在域或容器层面施加合规要求。

### 典型使用模式

1. **合规专项工作**：组织创建验证表单，确保关键资产满足合规要求（例如 PII 分类、数据保留策略）

2. **元数据补全**：完成类表单有助于为高价值资产补齐缺失的文档、归属与域指派信息

3. **治理工作流**：表单通过将任务分派给最有能力提供准确信息的领域专家，实现系统化的元数据采集

4. **质量提升**：表单可用于聚焦最重要的资产，逐步提升元数据质量

## 值得注意的例外情况

### 表单提示项类型

目前表单仅支持结构化属性类提示项。每个提示项都要求用户为实体或其模式字段上的结构化属性设置取值。未来的扩展可能涵盖其他元数据类型的提示项（例如文档要求、标签要求）。

### 模式字段提示项

使用 `FIELDS_STRUCTURED_PROPERTY` 提示项类型时，此类提示项不应标记为必填，因为它们适用于数量不确定的模式字段。当用户已恰当地对字段级提示项作出回应时，即视为表单已完成。

### 指派逻辑

表单通过两种相互独立的机制指派给实体：

- **直接指派**：显式指定的实体 URN
- **动态指派**：基于筛选器的自动指派

同一实体可以通过两种机制同时被指派同一个表单。实体上的 `forms` aspect 会将所有指派关系汇总在一起，无论其产生方式。

### 表单生命周期

表单一旦创建并发布，执行者就会在任务队列中看到它。删除表单需要：

1. 硬删除表单实体本身
2. 从已指派该表单的实体上移除对它的所有引用

这一两步流程确保了元数据图中的引用完整性。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](45-form.md)。
