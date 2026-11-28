---
title: ER 模型关系
entity: ermodelrelationship
order: 32
source: https://docs.datahub.com/docs/generated/metamodel/entities/ermodelrelationship.md
---

# ER 模型关系（ER Model Relationship）

实体-关系（Entity-Relationship，ER）模型关系表示实体-关系图中的实体之间的连接，具体建模数据集字段如何通过外键约束、join 以及其他引用关系相互关联。在 DataHub 中，这些关系捕获表之间的语义连接，使用户能够理解数据结构、强制引用完整性，并在字段级别追踪数据血缘。

ER 模型关系对于记录数据库 schema、数据仓库模型，以及任何表关系理解对数据治理、影响分析与查询优化至关重要的结构化数据系统，尤其有价值。

## 标识

ER 模型关系由单一标识符唯一确定：

- **id**：关系的唯一字符串标识符。以编程方式创建时，通常基于关系名称与涉及的两个数据集生成 MD5 哈希（按字母序排序以确保一致性）。

URN 结构遵循如下模式：

```
urn:li:erModelRelationship:<id>
```

### URN 示例

```
urn:li:erModelRelationship:employee_to_company
urn:li:erModelRelationship:a1b2c3d4e5f6g7h8i9j0
```

### ID 生成

通过 UI 或 API 创建关系时，ID 通常使用哈希函数确定性地生成，以确保一致性：

1. 构造一个键按字母序排列的 JSON 字符串：`Destination`、`ERModelRelationName`、`Source`
2. 将字典序较小的数据集 URN 作为 "Destination"，较大的作为 "Source"
3. 对该 JSON 字符串生成 MD5 哈希

这确保了两个数据集之间的同一关系无论创建顺序如何，总是获得相同的 ID。

## 重要能力

### 关系属性

ER 模型关系通过 `erModelRelationshipProperties` 方面捕获数据集如何相互连接的关键元数据。该核心方面包含：

#### 核心属性

- **name**：关系的可读名称（例如 "Employee to Company Relationship"）
- **source**：源数据集的 URN（关系中的第一个实体）
- **destination**：目标数据集的 URN（关系中的第二个实体）
- **cardinality**：定义数据集之间的关系类型

#### 基数类型

DataHub 支持四种基数类型，用于描述一个数据集中的记录与另一个数据集中的记录之间的关联方式：

- **ONE_ONE**：一对一关系。源数据集中的每条记录恰好对应目标数据集中的一条记录。

  - 示例：Employee → EmployeeDetails（一个员工对应一条详情记录）

- **ONE_N**：一对多关系。源数据集中的每条记录可以对应目标数据集中的多条记录。

  - 示例：Department → Employee（一个部门拥有多名员工）

- **N_ONE**：多对一关系。源数据集中的多条记录可以对应目标数据集中的一条记录。

  - 示例：Employee → Company（多名员工隶属于一家公司）

- **N_N**：多对多关系。两个数据集中的记录都可能在另一数据集中有多条对应记录。
  - 示例：Student → Course（学生选修多门课程，课程有多个学生选读）

#### 字段映射

`relationshipFieldMappings` 数组定义了两个数据集之间由哪些具体字段相连。每个映射包含：

- **sourceField**：源数据集中的字段路径（例如 "company_id"）
- **destinationField**：目标数据集中的字段路径（例如 "id"）

对于依赖多个字段的复合键，可以指定多个字段映射。

#### 自定义属性

与其他 DataHub 实体一样，ER 模型关系支持自定义属性，用于存储额外元数据，例如：

- 约束类型（例如 "Foreign Key"、"Referential Integrity"）
- 索引信息
- 数据库特定元数据
- 业务规则或校验逻辑

#### 时间戳

关系包含可选的时间戳信息，用于跟踪其在源系统中何时创建与最后修改：

- **created**：包含创建时间与操作者的 AuditStamp
- **lastModified**：包含最后修改时间与操作者的 AuditStamp

### 创建 ER 模型关系

下面是一个完整的示例，展示了如何创建两个数据集并在它们之间建立多对一关系：


**Python SDK：创建 ER 模型关系**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_create_basic.py
# metadata-ingestion/examples/library/ermodelrelationship_create_basic.py
import os
import time

from datahub.emitter.mce_builder import make_data_platform_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    ERModelRelationshipCardinalityClass,
    ERModelRelationshipKeyClass,
    ERModelRelationshipPropertiesClass,
    NumberTypeClass,
    OtherSchemaClass,
    RelationshipFieldMappingClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    SchemaMetadataClass,
    StringTypeClass,
)

GMS_ENDPOINT = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
GMS_TOKEN = os.getenv("DATAHUB_GMS_TOKEN")
PLATFORM = "mysql"
ENV = "PROD"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, token=GMS_TOKEN)


def create_dataset_with_schema(
    dataset_name: str, fields: list[SchemaFieldClass]
) -> str:
    """Helper function to create a dataset with schema."""
    dataset_urn = make_dataset_urn(PLATFORM, dataset_name, ENV)

    schema_metadata = SchemaMetadataClass(
        schemaName=dataset_name,
        platform=make_data_platform_urn(PLATFORM),
        fields=fields,
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema=""),
    )

    emitter.emit_mcp(
        MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=schema_metadata,
        )
    )

    return dataset_urn


def create_schema_field(
    field_path: str, native_type: str, data_type: SchemaFieldDataTypeClass
) -> SchemaFieldClass:
    """Helper function to create a schema field."""
    return SchemaFieldClass(
        fieldPath=field_path,
        type=data_type,
        nativeDataType=native_type,
        description=f"Field: {field_path}",
        lastModified=AuditStampClass(
            time=int(time.time() * 1000),
            actor="urn:li:corpuser:datahub",
        ),
    )


# Create Employee table
employee_fields = [
    create_schema_field("id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())),
    create_schema_field(
        "name", "varchar(100)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "email", "varchar(255)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "company_id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())
    ),
]
employee_urn = create_dataset_with_schema("Employee", employee_fields)
print(f"Created Employee dataset: {employee_urn}")

# Create Company table
company_fields = [
    create_schema_field("id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())),
    create_schema_field(
        "name", "varchar(200)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "industry", "varchar(100)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
]
company_urn = create_dataset_with_schema("Company", company_fields)
print(f"Created Company dataset: {company_urn}")

# Create ER Model Relationship
relationship_id = "employee_to_company"
relationship_urn = f"urn:li:erModelRelationship:{relationship_id}"

# Emit the key aspect
relationship_key = ERModelRelationshipKeyClass(id=relationship_id)
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=relationship_urn,
        aspect=relationship_key,
    )
)

# Emit the properties aspect
relationship_properties = ERModelRelationshipPropertiesClass(
    name="Employee to Company Relationship",
    source=employee_urn,
    destination=company_urn,
    relationshipFieldMappings=[
        RelationshipFieldMappingClass(
            sourceField="company_id",
            destinationField="id",
        )
    ],
    cardinality=ERModelRelationshipCardinalityClass.N_ONE,
    customProperties={
        "constraint_type": "FOREIGN_KEY",
        "on_delete": "CASCADE",
        "on_update": "CASCADE",
    },
    created=AuditStampClass(
        time=int(time.time() * 1000),
        actor="urn:li:corpuser:datahub",
    ),
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=relationship_urn,
        aspect=relationship_properties,
    )
)

print(f"Created ER Model Relationship: {relationship_urn}")
print(
    "This N:1 relationship connects Employee.company_id to Company.id, "
    "representing that many employees belong to one company."
)

```

### 可编辑属性

`editableERModelRelationshipProperties` 方面允许用户通过 DataHub UI 添加或修改关系元数据，而不覆盖从源系统摄取的信息。这种分离方式与 DataHub 各实体中采用的模式一致。

可编辑属性包括：

- **description**：说明关系用途、约束或业务逻辑的文档
- **name**：覆盖源系统名称的替代显示名称

#### 更新可编辑属性


**Python SDK：更新关系的可编辑属性**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_update_properties.py
# metadata-ingestion/examples/library/ermodelrelationship_update_properties.py
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    EditableERModelRelationshipPropertiesClass,
)

GMS_ENDPOINT = "http://localhost:8080"
relationship_urn = "urn:li:erModelRelationship:employee_to_company"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, extra_headers={})

# Create or update editable properties
audit_stamp = AuditStampClass(
    time=int(time.time() * 1000), actor="urn:li:corpuser:datahub"
)

editable_properties = EditableERModelRelationshipPropertiesClass(
    name="Employee-Company Foreign Key",
    description=(
        "This relationship establishes referential integrity between the Employee "
        "and Company tables. Each employee record must reference a valid company. "
        "The relationship enforces CASCADE on both UPDATE and DELETE operations, "
        "meaning changes to company IDs will propagate to employee records, and "
        "deleting a company will delete all associated employees."
    ),
    created=audit_stamp,
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=relationship_urn,
        aspect=editable_properties,
    )
)

print(f"Updated editable properties for ER Model Relationship {relationship_urn}")
print(f"Name: {editable_properties.name}")
print(f"Description: {editable_properties.description}")

```

### 标签与术语表术语

ER 模型关系与其他 DataHub 实体一样，支持添加标签与术语表术语。这让你可以对关系进行分类、用数据分类标签标注它们，或将其关联到业务概念。

#### 添加标签

标签可用于按类型、重要性或数据域对关系进行分类：


**Python SDK：为 ER 模型关系添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_add_tag.py
# metadata-ingestion/examples/library/ermodelrelationship_add_tag.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    TagAssociationClass,
)

GMS_ENDPOINT = "http://localhost:8080"
relationship_urn = "urn:li:erModelRelationship:employee_to_company"
tag_urn = "urn:li:tag:ForeignKey"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, extra_headers={})

# Read current tags
# FIXME: emitter.get not available
# gms_response = emitter.get(relationship_urn, aspects=["globalTags"])
current_tags: dict[
    str, object
] = {}  # gms_response.get("globalTags", {}) if gms_response else {}

# Build new tags list
existing_tags = []
if isinstance(current_tags, dict) and "tags" in current_tags:
    tags_list = current_tags["tags"]
    if isinstance(tags_list, list):
        existing_tags = [tag["tag"] for tag in tags_list]

# Add new tag if not already present
if tag_urn not in existing_tags:
    tag_associations = [
        TagAssociationClass(tag=existing_tag) for existing_tag in existing_tags
    ]
    tag_associations.append(TagAssociationClass(tag=tag_urn))

    global_tags = GlobalTagsClass(tags=tag_associations)

    emitter.emit_mcp(
        MetadataChangeProposalWrapper(
            entityUrn=relationship_urn,
            aspect=global_tags,
        )
    )

    print(f"Added tag {tag_urn} to ER Model Relationship {relationship_urn}")
else:
    print(f"Tag {tag_urn} already exists on {relationship_urn}")

```

#### 添加术语表术语

术语表术语将关系与业务概念和术语联系起来：


**Python SDK：为 ER 模型关系添加术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_add_term.py
# metadata-ingestion/examples/library/ermodelrelationship_add_term.py
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    GlossaryTermAssociationClass,
    GlossaryTermsClass,
)

GMS_ENDPOINT = "http://localhost:8080"
relationship_urn = "urn:li:erModelRelationship:employee_to_company"
term_urn = "urn:li:glossaryTerm:ReferentialIntegrity"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, extra_headers={})

# Read current glossary terms
# FIXME: emitter.get not available
# gms_response = emitter.get(relationship_urn, aspects=["glossaryTerms"])
current_terms: dict[
    str, object
] = {}  # gms_response.get("glossaryTerms", {}) if gms_response else {}

# Build new terms list
existing_terms = []
if isinstance(current_terms, dict) and "terms" in current_terms:
    terms_list = current_terms["terms"]
    if isinstance(terms_list, list):
        existing_terms = [term["urn"] for term in terms_list]

# Add new term if not already present
if term_urn not in existing_terms:
    term_associations = [
        GlossaryTermAssociationClass(urn=existing_term)
        for existing_term in existing_terms
    ]
    term_associations.append(GlossaryTermAssociationClass(urn=term_urn))

    glossary_terms = GlossaryTermsClass(
        terms=term_associations,
        auditStamp=AuditStampClass(time=0, actor="urn:li:corpuser:datahub"),
    )

    emitter.emit_mcp(
        MetadataChangeProposalWrapper(
            entityUrn=relationship_urn,
            aspect=glossary_terms,
        )
    )

    print(f"Added glossary term {term_urn} to ER Model Relationship {relationship_urn}")
else:
    print(f"Glossary term {term_urn} already exists on {relationship_urn}")

```

### 归属

可以为 ER 模型关系指定归属，以表明谁负责维护该关系定义，或在所连接的数据集发生变化时应当咨询谁。


**Python SDK：为 ER 模型关系添加归属人**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_add_owner.py
# metadata-ingestion/examples/library/ermodelrelationship_add_owner.py
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)

GMS_ENDPOINT = "http://localhost:8080"
relationship_urn = "urn:li:erModelRelationship:employee_to_company"
owner_urn = "urn:li:corpuser:jdoe"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, extra_headers={})

# Read current ownership
# FIXME: emitter.get not available
# gms_response = emitter.get(relationship_urn, aspects=["ownership"])
current_ownership: dict[
    str, object
] = {}  # gms_response.get("ownership", {}) if gms_response else {}

# Build new owners list
existing_owners = []
if isinstance(current_ownership, dict) and "owners" in current_ownership:
    owners_list = current_ownership["owners"]
    if isinstance(owners_list, list):
        existing_owners = [owner["owner"] for owner in owners_list]

# Add new owner if not already present
if owner_urn not in existing_owners:
    owner_list = [
        OwnerClass(owner=existing_owner, type=OwnershipTypeClass.DATAOWNER)
        for existing_owner in existing_owners
    ]
    owner_list.append(
        OwnerClass(
            owner=owner_urn,
            type=OwnershipTypeClass.DATAOWNER,
        )
    )

    ownership = OwnershipClass(
        owners=owner_list,
        lastModified=AuditStampClass(
            time=int(time.time() * 1000),
            actor="urn:li:corpuser:datahub",
        ),
    )

    emitter.emit_mcp(
        MetadataChangeProposalWrapper(
            entityUrn=relationship_urn,
            aspect=ownership,
        )
    )

    print(f"Added owner {owner_urn} to ER Model Relationship {relationship_urn}")
else:
    print(f"Owner {owner_urn} already exists on {relationship_urn}")

```

### 复杂关系

ER 模型关系可以建模复杂的数据结构，包括复合键以及通过中间表（junction table）实现的多对多关系：


**Python SDK：创建带复合键的多对多关系**

```python
# Inlined from /metadata-ingestion/examples/library/ermodelrelationship_complex_many_to_many.py
# metadata-ingestion/examples/library/ermodelrelationship_complex_many_to_many.py
import time

from datahub.emitter.mce_builder import make_data_platform_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    ERModelRelationshipCardinalityClass,
    ERModelRelationshipKeyClass,
    ERModelRelationshipPropertiesClass,
    NumberTypeClass,
    OtherSchemaClass,
    RelationshipFieldMappingClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    SchemaMetadataClass,
    StringTypeClass,
)

GMS_ENDPOINT = "http://localhost:8080"
PLATFORM = "postgres"
ENV = "PROD"

emitter = DatahubRestEmitter(gms_server=GMS_ENDPOINT, extra_headers={})


def create_dataset_with_schema(
    dataset_name: str, fields: list[SchemaFieldClass]
) -> str:
    """Helper function to create a dataset with schema."""
    dataset_urn = make_dataset_urn(PLATFORM, dataset_name, ENV)

    schema_metadata = SchemaMetadataClass(
        schemaName=dataset_name,
        platform=make_data_platform_urn(PLATFORM),
        fields=fields,
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema=""),
    )

    emitter.emit_mcp(
        MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=schema_metadata,
        )
    )

    return dataset_urn


def create_schema_field(
    field_path: str, native_type: str, data_type: SchemaFieldDataTypeClass
) -> SchemaFieldClass:
    """Helper function to create a schema field."""
    return SchemaFieldClass(
        fieldPath=field_path,
        type=data_type,
        nativeDataType=native_type,
        description=f"Field: {field_path}",
        lastModified=AuditStampClass(
            time=int(time.time() * 1000),
            actor="urn:li:corpuser:datahub",
        ),
    )


# Create Student table
student_fields = [
    create_schema_field("id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())),
    create_schema_field(
        "name", "varchar(100)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "email", "varchar(255)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
]
student_urn = create_dataset_with_schema("Student", student_fields)
print(f"Created Student dataset: {student_urn}")

# Create Course table
course_fields = [
    create_schema_field("id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())),
    create_schema_field(
        "code", "varchar(20)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "title", "varchar(200)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
]
course_urn = create_dataset_with_schema("Course", course_fields)
print(f"Created Course dataset: {course_urn}")

# Create StudentCourse junction table with composite key
student_course_fields = [
    create_schema_field(
        "student_id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())
    ),
    create_schema_field(
        "course_id", "int", SchemaFieldDataTypeClass(type=NumberTypeClass())
    ),
    create_schema_field(
        "enrollment_date", "date", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
    create_schema_field(
        "grade", "varchar(2)", SchemaFieldDataTypeClass(type=StringTypeClass())
    ),
]
student_course_urn = create_dataset_with_schema("StudentCourse", student_course_fields)
print(f"Created StudentCourse junction table: {student_course_urn}")

# Create relationship: StudentCourse -> Student (many-to-one)
student_relationship_id = "student_course_to_student"
student_relationship_urn = f"urn:li:erModelRelationship:{student_relationship_id}"

student_relationship_key = ERModelRelationshipKeyClass(id=student_relationship_id)
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=student_relationship_urn,
        aspect=student_relationship_key,
    )
)

student_relationship_properties = ERModelRelationshipPropertiesClass(
    name="StudentCourse to Student Relationship",
    source=student_course_urn,
    destination=student_urn,
    relationshipFieldMappings=[
        RelationshipFieldMappingClass(
            sourceField="student_id",
            destinationField="id",
        )
    ],
    cardinality=ERModelRelationshipCardinalityClass.N_ONE,
    customProperties={
        "constraint_type": "FOREIGN_KEY",
        "part_of_composite_key": "true",
    },
    created=AuditStampClass(
        time=int(time.time() * 1000),
        actor="urn:li:corpuser:datahub",
    ),
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=student_relationship_urn,
        aspect=student_relationship_properties,
    )
)

print(f"Created relationship: {student_relationship_urn}")

# Create relationship: StudentCourse -> Course (many-to-one)
course_relationship_id = "student_course_to_course"
course_relationship_urn = f"urn:li:erModelRelationship:{course_relationship_id}"

course_relationship_key = ERModelRelationshipKeyClass(id=course_relationship_id)
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=course_relationship_urn,
        aspect=course_relationship_key,
    )
)

course_relationship_properties = ERModelRelationshipPropertiesClass(
    name="StudentCourse to Course Relationship",
    source=student_course_urn,
    destination=course_urn,
    relationshipFieldMappings=[
        RelationshipFieldMappingClass(
            sourceField="course_id",
            destinationField="id",
        )
    ],
    cardinality=ERModelRelationshipCardinalityClass.N_ONE,
    customProperties={
        "constraint_type": "FOREIGN_KEY",
        "part_of_composite_key": "true",
    },
    created=AuditStampClass(
        time=int(time.time() * 1000),
        actor="urn:li:corpuser:datahub",
    ),
)

emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn=course_relationship_urn,
        aspect=course_relationship_properties,
    )
)

print(f"Created relationship: {course_relationship_urn}")

print("\nMany-to-many relationship established through junction table:")
print("- Student N:N Course (via StudentCourse junction table)")
print("- StudentCourse has composite primary key (student_id, course_id)")
print("- Each component of the composite key is a foreign key to its respective table")

```

### 查询关系

可以使用标准的 DataHub REST API 查询 ER 模型关系：


**获取一个 ER 模型关系**

```bash
curl 'http://localhost:8080/entitiesV2/urn%3Ali%3AerModelRelationship%3Aemployee_to_company'
```

响应中包含该关系的所有方面：

```json
{
  "urn": "urn:li:erModelRelationship:employee_to_company",
  "aspects": {
    "erModelRelationshipKey": {
      "id": "employee_to_company"
    },
    "erModelRelationshipProperties": {
      "name": "Employee to Company Relationship",
      "source": "urn:li:dataset:(urn:li:dataPlatform:mysql,Employee,PROD)",
      "destination": "urn:li:dataset:(urn:li:dataPlatform:mysql,Company,PROD)",
      "relationshipFieldMappings": [
        {
          "sourceField": "company_id",
          "destinationField": "id"
        }
      ],
      "cardinality": "N_ONE",
      "customProperties": {
        "constraint": "Foreign Key"
      }
    }
  }
}
```

**查找某个数据集的所有关系**

通过查询关系 API 可以发现与特定数据集相连的关系：

```bash
# Find relationships where the dataset is the source
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Amysql,Employee,PROD)&types=ermodelrelationA'

# Find relationships where the dataset is the destination
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Amysql,Company,PROD)&types=ermodelrelationB'
```

## 集成点

ER 模型关系与 DataHub 的其他多个实体与功能集成：

### 数据集集成

ER 模型关系与 [Dataset](01-dataset.md) 实体本质相连。每个关系必须恰好引用两个数据集： 实体本质相连。每个关系必须恰好引用两个数据集：

- 在 UI 中，可从数据集页面发现相关关系
- GraphQL API 会自动解析源数据集与目标数据集的详情
- 关系信息丰富了数据集的 schema 视图

### Schema 字段集成

尽管该实体将字段路径存储为字符串，但它们对应于被引用数据集中的 [SchemaField](26-schemafield.md) 实体。这实现了： 实体。这实现了：

- 在 UI 中可视化展示外键关系
- 字段级血缘分析
- schema 变更时的影响分析

### 数据血缘

ER 模型关系与 DataHub 的血缘功能互为补充但又彼此不同：

- **ER 模型关系**：建模数据集之间的静态结构与引用约束
- **上游/下游血缘**：刻画数据如何经由转换与流水线流动

两者结合，可完整呈现数据结构与数据流的全貌。

### GraphQL API

DataHub GraphQL API 为 ER 模型关系提供丰富的查询能力：

- `erModelRelationship(urn: String!)`：获取特定关系
- 通过 mutation 创建与更新关系
- 从数据集遍历到其关系
- 用于构建 ER 图的批量查询能力

### 权限控制

创建与修改 ER 模型关系需要在 DataHub 权限策略框架中拥有相应权限。用户必须同时拥有源数据集与目标数据集的编辑权限，才能在二者之间创建关系。

## 值得注意的例外

### 非方向性关系

虽然 ER 模型关系包含 "source" 与 "destination" 字段，但这并不必然意味着传统外键意义上的方向性：

- source/destination 的排序主要出于内部一致性考虑
- 生成 ID 时，数据集按字母序排列，以确保同一关系总是产生相同的 ID
- 基数类型（ONE_N 与 N_ONE）明确刻画了关系的实际方向

### 关系生命周期

目前 ER 模型关系与其连接的数据集是相互独立的：

- 删除数据集不会自动删除其关系
- 数据集被删除后，可能存在孤儿关系（指向已不存在的数据集）
- 应用应当处理关系端点可能不存在的情况

### Schema 演进

ER 模型关系以字符串而非带版本的 schema 引用来引用字段路径：

- 如果数据集 schema 中的字段名发生变化，关系可能仍引用过时的字段名
- 没有任何自动校验确保被引用的字段存在于当前 schema 中
- 应用应当在创建关系时实现字段校验

### 平台支持

并非所有数据平台都一等公民地支持 ER 模型关系：

- 关系型数据库（MySQL、PostgreSQL、Oracle）天然映射到该模型
- NoSQL 数据库与数据湖可能没有显式的关系元数据
- 部分摄取连接器会自动抽取外键关系，另一些则不会

### 未来演进方向

ER Model Relationship 实体未来可能会演进为包含：

- 除基数之外的更多关系类型（继承、组合）
- 用于追踪关系随时间变化的版本管理
- 面向复杂转换逻辑的双向字段映射
- 与数据质量规则及约束校验的集成


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](32-ermodelrelationship.md)。。
