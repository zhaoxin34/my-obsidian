---
title: 表单
entity: form
source: https://docs.datahub.com/docs/generated/metamodel/entities/form.md
---

# 表单

表单（form）实体是 DataHub 元数据模型中的核心实体，用于支持结构化的元数据收集与合规工作。表单提供了一种集中化、模板化的方式，通过协作式的众包工作流为各类数据资产捕获关键元数据。

## 标识（Identity）

表单由创建者选定的一个唯一字符串标识符来标识。

表单 URN 的结构为：`urn:li:form:<form-id>`

例如：`urn:li:form:metadataInitiative2024`

表单标识符应当有意义且具有描述性，通常体现该表单所服务的事项或用途（例如 `piiClassification2024`、`dataQualityCompliance`、`retentionPolicyForm`）。

## 重要能力

### 表单元数据与配置

表单通过 `formInfo` aspect 定义，其中包含表单的全部核心信息：

- **名称与描述**：表单用途的展示名称与详细描述
- **类型**：支持两种类型：
  - `COMPLETION`：纯粹用于在实体上收集元数据字段的表单
  - `VERIFICATION`：用于通过特定元数据字段的存在性验证实体是否符合某项策略的表单
- **提示项（Prompts）**：用户需要回答的提示（问题）列表。每个提示都代表填写特定元数据的一项要求。当前支持的提示类型有：
  - `STRUCTURED_PROPERTY`：将结构化属性应用到实体的提示
  - `FIELDS_STRUCTURED_PROPERTY`：将结构化属性应用到数据集模式字段（列）的提示
- **执行者分配（Actor Assignment）**：定义应由谁完成该表单。表单可分配给：
  - 资产负责人（默认）
  - 指定用户
  - 指定群组

下面是表单元数据的示例：


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



### 动态表单分配

表单可以通过两种方式分配给实体：

1. **显式分配**：直接将表单分配给特定的实体 URN
2. **动态分配**：使用 `dynamicFormAssignment` aspect 自动把表单分配给符合特定条件的实体

`dynamicFormAssignment` aspect 通过指定过滤器实现基于规则的表单分配。符合过滤条件的实体会自动被应用该表单。过滤器支持：

- 实体类型（例如 datasets、dashboards、charts）
- 平台（例如 snowflake、bigquery、postgres）
- 域成员关系
- 容器成员关系

这种动态方式对大规模合规工作尤其强大，因为你希望把表单应用到某类资产或某个特定域内的全部资产时非常方便。


**Python SDK：使用过滤器动态分配表单**

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



### 实体上的表单分配

当表单被分配给实体时（无论是显式还是动态分配），分配关系通过目标实体上的 `forms` aspect 跟踪。该 aspect 维护：

- **未完成表单**：仍有待完成提示项的表单
- **已完成表单**：所有必填提示项均已回答的表单
- **验证结果**：对于验证类型的表单，跟踪哪些表单已成功通过验证
- **提示状态**：对每个表单跟踪哪些提示已完成、哪些未完成，以及相应的时间戳

这使 DataHub 能够提供跨数据目录的表单完成进度跟踪、通知与分析。

### 归属

表单可通过标准的 `ownership` aspect 指定负责人。表单的负责人通常是负责管理和维护该表单的治理或合规团队成员。


**Python SDK：为表单添加负责人**

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


**Python SDK：创建带多个提示项的验证表单**

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


**Python SDK：创建带动态分配的表单**

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


**Python SDK：将表单分配给特定实体**

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

可以通过 REST API 查询表单，以获取表单定义并检查其分配状态。


**通过 REST API 查询表单**

```shell
curl 'http://localhost:8080/entities/urn%3Ali%3Aform%3AmetadataInitiative2024'
```

该请求返回表单实体及其全部 aspect，包括 `formInfo`、`dynamicFormAssignment`（如已配置）以及 `ownership`。



**检查实体上的表单分配情况**

```shell
curl 'http://localhost:8080/entities/urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Asnowflake,mydb.schema.table,PROD)?aspects=forms'
```

该请求返回 `forms` aspect，显示该数据集的所有未完成与已完成表单。



## 集成点

### 与其他实体的关系

表单在 DataHub 生态中有若干关键集成点：

1. **结构化属性**：表单主要通过提示项与结构化属性交互。每个提示项都可以要求用户在实体或其模式字段上填写特定的结构化属性。

2. **资产（数据集、仪表板、图表等）**：表单被分配给数据资产以收集元数据。该关系通过以下方式跟踪：

   - 目标实体上的 `forms` aspect
   - 表单上的 `dynamicFormAssignment` 过滤条件

3. **用户与群组**：表单被分配给负责完成表单的具体执行者（用户或群组）。这形成如下工作流：

   - 表单出现在执行者的任务列表中
   - 执行者收到待办表单的通知
   - 按用户维护完成情况跟踪

4. **域与容器**：表单可依据域或容器成员关系自动分配，使治理团队能够在域或容器层级施加合规要求。

### 典型使用模式

1. **合规工作**：组织创建验证表单以确保关键资产满足合规要求（例如 PII 分类、数据保留策略）

2. **元数据完善**：完成类表单帮助为高价值资产补齐缺失的文档、归属与域分配

3. **治理工作流**：表单通过将任务路由给最适合提供准确信息的领域专家，实现系统化的元数据收集

4. **质量改进**：表单可用于循序渐进地提升元数据质量，先聚焦最重要的资产

## 显著的例外情况

### 表单提示类型

当前表单仅支持结构化属性类型的提示。每个提示都要求用户在实体或其模式字段上设置结构化属性值。未来的扩展可能包含其他元数据类型的提示（例如文档要求、标签要求）。

### 模式字段提示

使用 `FIELDS_STRUCTURED_PROPERTY` 提示类型时，这些提示不应标记为必填，因为它们适用于数量不确定的模式字段。当用户对字段级提示做出恰当回应后，即认为表单已完成。

### 分配逻辑

表单通过两种相互独立的机制分配给实体：

- **直接分配**：显式指定的实体 URN
- **动态分配**：基于过滤器的自动分配

同一实体可以通过两种机制被分配到同一个表单。实体上的 `forms` aspect 会汇总所有分配结果，无论其产生方式。

### 表单生命周期

表单一旦创建并发布，执行者就会在任务队列中看到它。删除表单需要：

1. 硬删除表单实体本身
2. 从已分配该表单的所有实体上移除对该表单的引用

这个两步流程确保了元数据图中的引用完整性。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](https://docs.datahub.com/docs/generated/metamodel/entities/form.md)。
