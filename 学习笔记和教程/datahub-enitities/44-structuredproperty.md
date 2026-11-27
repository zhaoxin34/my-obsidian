---
title: 结构化属性
entity: structuredproperty
order: 44
source: https://docs.datahub.com/docs/generated/metamodel/entities/structuredproperty.md
---

# 结构化属性

结构化属性（Structured Properties）是可附加到 DataHub 中任意实体类型的自定义、带类型的元数据字段。它们使组织能够以领域特定的属性扩展核心元数据模型，从而支持治理、合规与数据发现等各项工作。

## 标识（Identity）

结构化属性由唯一的一段信息标识：

- 属性的 **id** 或 **qualified name**：这是一个遵循命名空间约定的唯一字符串标识符，通常使用点号分隔（例如 `io.acryl.privacy.retentionTime` 或 `companyName.department.propertyName`）。限定名会成为 URN 的一部分，且在你所在 DataHub 实例的所有结构化属性中必须全局唯一。

结构化属性标识符的示例为 `urn:li:structuredProperty:io.acryl.privacy.retentionTime`。

与其他可能需要多段信息（平台、名称、环境）的实体不同，结构化属性具有简单扁平的标识模型，仅基于其限定名。

## 重要能力

### 属性定义

结构化属性的核心元数据记录在 `propertyDefinition` aspect 中，该 aspect 定义了：

#### 类型系统

结构化属性通过 `valueType` 字段支持强类型值，该字段必须引用一个有效的 `dataType` 实体。支持的类型包括：

- **string**：文本值（纯文本）
- **rich_text**：带格式的富文本
- **number**：数值（整数或小数）
- **date**：日期值
- **urn**：对其他 DataHub 实体的引用

类型以 URN 形式指定：`urn:li:dataType:datahub.string`、`urn:li:dataType:datahub.number` 等。

#### 类型限定符

对于 URN 类型的属性，可以使用 `typeQualifier` 字段限制允许引用的实体类型，从而创建只引用特定实体类型的属性：

```json
{
  "valueType": "urn:li:dataType:datahub.urn",
  "typeQualifier": {
    "allowedTypes": [
      "urn:li:entityType:datahub.corpuser",
      "urn:li:entityType:datahub.corpGroup"
    ]
  }
}
```

#### 基数

结构化属性可通过 `cardinality` 字段接受单值或多值：

- **SINGLE**：只能赋一个值（默认）
- **MULTIPLE**：可以以数组形式赋多个值

#### 实体类型限制

`entityTypes` 数组指定该属性可应用的实体类型。例如，某属性可能仅适用于：

- 数据集：`urn:li:entityType:datahub.dataset`
- 模式字段（列）：`urn:li:entityType:datahub.schemaField`
- 仪表板：`urn:li:entityType:datahub.dashboard`
- 任意实体类型的组合

#### 通过允许值进行校验

为保证数据质量与一致性，可以使用 `allowedValues` 数组定义可接受值的白名单。每个允许值可包含：

- **value**：实际取值（字符串或数字）
- **description**：对该取值含义的说明

一旦定义了允许值，系统会校验任何属性赋值是否匹配其中之一。

#### 不可变性

`immutable` 字段（默认 `false`）决定属性值在设置后能否被修改。当为 `true` 时，属性值即为永久值，不可修改或删除，从而保证关键元数据的完整性。

#### 版本控制

`version` 字段支持破坏性 schema 变更，允许以向后不兼容的方式更新属性定义。版本必须遵循 `yyyyMMddhhmmss` 格式（例如 `20240614080000`）。应用新版本时：

- 旧 schema 下的旧值将不可访问
- 新值必须符合更新后的 schema
- 旧值将被异步删除

### 显示设置

`structuredPropertySettings` aspect 控制属性在 DataHub UI 中的呈现方式：

- **isHidden**：为 `true` 时属性在 UI 中不可见（适用于内部元数据）
- **showInSearchFilters**：为 `true` 时用户可按该属性的值过滤搜索结果
- **showInAssetSummary**：为 `true` 时在资产侧边栏显示该属性
- **hideInAssetSummaryWhenEmpty**：为 `true` 且启用了 `showInAssetSummary` 时，属性无值时从侧边栏隐藏
- **showAsAssetBadge**：为 `true` 时在资产卡片上以徽章形式显示属性值（仅适用于带允许值的 string/number 类型）
- **showInColumnsTable**：为 `true` 时在数据集 schema 表格中以列的形式显示该属性（适用于列级属性）

### 通用 Aspect

结构化属性同样支持标准的 DataHub aspect：

- **status**：通过设置 `removed: true` 支持软删除，隐藏属性但不删除底层数据
- **institutionalMemory**：允许附加说明属性用途与使用方式的文档链接
- **deprecation**：可将属性标记为已废弃，同时保留历史数据

## 代码示例

### 创建结构化属性

下面的示例创建一个用于跟踪数据保留时间的结构化属性，值为数值并带校验：


**Python SDK：创建带允许值的结构化属性**

```python
# Inlined from /metadata-ingestion/examples/library/structured_property_create_basic.py
import os

from datahub.api.entities.structuredproperties.structuredproperties import (
    AllowedValue,
    StructuredProperties,
)
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig

# Create a DataHub client
client = DataHubGraph(
    DataHubGraphConfig(
        server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
        token=os.getenv("DATAHUB_GMS_TOKEN"),
    )
)

# Define a structured property for data retention time
retention_property = StructuredProperties(
    id="io.acryl.privacy.retentionTime",
    qualified_name="io.acryl.privacy.retentionTime",
    display_name="Retention Time",
    type="number",
    description="Number of days to retain data based on privacy and compliance requirements",
    entity_types=["dataset", "dataFlow"],
    cardinality="SINGLE",
    allowed_values=[
        AllowedValue(
            value=30.0,
            description="30 days - for ephemeral data containing PII",
        ),
        AllowedValue(
            value=90.0,
            description="90 days - for monthly reporting data with PII",
        ),
        AllowedValue(
            value=365.0,
            description="365 days - for non-sensitive data",
        ),
    ],
)

# Emit the structured property to DataHub
for mcp in retention_property.generate_mcps():
    client.emit(mcp)

print(f"Created structured property: {retention_property.urn}")

```



### 创建带实体类型限制的结构化属性

下面的示例创建一个接受 URN 值但只允许引用用户和群组的属性：


**Python SDK：创建带类型限定符的结构化属性**

```python
# Inlined from /metadata-ingestion/examples/library/structured_property_create_with_type_qualifier.py
from datahub.api.entities.structuredproperties.structuredproperties import (
    StructuredProperties,
    TypeQualifierAllowedTypes,
)
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

# Create a DataHub client
client = DataHubGraph(DatahubClientConfig(server="http://localhost:8080"))

# Define a structured property that references DataHub entities
# This property can only reference CorpUser or CorpGroup entities
data_steward_property = StructuredProperties(
    id="io.acryl.governance.dataSteward",
    qualified_name="io.acryl.governance.dataSteward",
    display_name="Data Steward",
    type="urn",
    description="The designated data steward responsible for this asset's governance and quality",
    entity_types=["dataset", "dashboard", "chart", "dataJob"],
    cardinality="SINGLE",
    type_qualifier=TypeQualifierAllowedTypes(
        allowed_types=[
            "urn:li:entityType:datahub.corpuser",
            "urn:li:entityType:datahub.corpGroup",
        ]
    ),
)

# Emit the structured property to DataHub
for mcp in data_steward_property.generate_mcps():
    client.emit_mcp(mcp)

print(f"Created structured property: {data_steward_property.urn}")

# Example: Create a multi-value property for related datasets
related_datasets_property = StructuredProperties(
    id="io.acryl.lineage.relatedDatasets",
    qualified_name="io.acryl.lineage.relatedDatasets",
    display_name="Related Datasets",
    type="urn",
    description="Other datasets that are semantically or functionally related to this asset",
    entity_types=["dataset"],
    cardinality="MULTIPLE",
    type_qualifier=TypeQualifierAllowedTypes(
        allowed_types=["urn:li:entityType:datahub.dataset"]
    ),
)

# Emit the second structured property
for mcp in related_datasets_property.generate_mcps():
    client.emit_mcp(mcp)

print(f"Created structured property: {related_datasets_property.urn}")

```



### 将结构化属性应用到实体

结构化属性定义完成后，即可将其赋给实体：


**Python SDK：把结构化属性应用到数据集**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_update_structured_properties.py
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.rest_emitter import DataHubRestEmitter
from datahub.specific.dataset import DatasetPatchBuilder

# Create rest emitter
rest_emitter = DataHubRestEmitter(gms_server="http://localhost:8080")

dataset_urn = make_dataset_urn(platform="hive", name="fct_users_created", env="PROD")

for patch_mcp in (
    DatasetPatchBuilder(dataset_urn)
    .set_structured_property("io.acryl.dataManagement.replicationSLA", 120)
    .build()
):
    rest_emitter.emit(patch_mcp)

print(f"Added cluster_name, retention_time properties to dataset {dataset_urn}")

```



### 对结构化属性执行 Patch 操作

若需更细粒度的控制，可使用 patch 操作添加或移除单个属性：


**Python SDK：使用 patch 添加与移除结构化属性**

```python
# Inlined from /metadata-ingestion/examples/library/dataset_add_structured_properties_patch.py
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.specific.dataset import DatasetPatchBuilder

# Create DataHub Client
datahub_client = DataHubGraph(DataHubGraphConfig(server="http://localhost:8080"))

# Create Dataset URN
dataset_urn = make_dataset_urn(platform="hive", name="fct_users_created", env="PROD")

# Create Dataset Patch to Add and Remove Structured Properties
patch_builder = DatasetPatchBuilder(dataset_urn)
patch_builder.add_structured_property(
    "urn:li:structuredProperty:retentionTimeInDays", 12
)
patch_builder.remove_structured_property(
    "urn:li:structuredProperty:customClassification"
)
patch_mcps = patch_builder.build()

# Emit Dataset Patch
for patch_mcp in patch_mcps:
    datahub_client.emit(patch_mcp)

```



### 查询结构化属性定义

检索结构化属性定义以了解其配置：


**Python SDK：查询结构化属性**

```python
# Inlined from /metadata-ingestion/examples/library/structured_property_query.py
from datahub.api.entities.structuredproperties.structuredproperties import (
    StructuredProperties,
)
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

# Create a DataHub client
client = DataHubGraph(DatahubClientConfig(server="http://localhost:8080"))

# List all structured properties in the system
print("Listing all structured properties:")
print("-" * 80)

for structured_property in StructuredProperties.list(client):
    print(f"\nURN: {structured_property.urn}")
    print(f"Display Name: {structured_property.display_name}")
    print(f"Type: {structured_property.type}")
    print(f"Cardinality: {structured_property.cardinality}")
    print(f"Entity Types: {', '.join(structured_property.entity_types or [])}")

    if structured_property.allowed_values:
        print("Allowed Values:")
        for av in structured_property.allowed_values:
            print(f"  - {av.value}: {av.description}")

# Retrieve a specific structured property by URN
print("\n" + "=" * 80)
print("Retrieving specific structured property:")
print("-" * 80)

property_urn = "urn:li:structuredProperty:io.acryl.privacy.retentionTime"

try:
    specific_property = StructuredProperties.from_datahub(client, property_urn)

    print(f"\nURN: {specific_property.urn}")
    print(f"Qualified Name: {specific_property.qualified_name}")
    print(f"Display Name: {specific_property.display_name}")
    print(f"Description: {specific_property.description}")
    print(f"Type: {specific_property.type}")
    print(f"Cardinality: {specific_property.cardinality}")
    print(f"Immutable: {specific_property.immutable}")
    print(f"Entity Types: {', '.join(specific_property.entity_types or [])}")

    if specific_property.allowed_values:
        print("\nAllowed Values:")
        for av in specific_property.allowed_values:
            print(f"  - {av.value}: {av.description}")

    if specific_property.type_qualifier:
        print("\nType Qualifier - Allowed Entity Types:")
        for entity_type in specific_property.type_qualifier.allowed_types:
            print(f"  - {entity_type}")

except Exception as e:
    print(f"Error retrieving structured property: {e}")

# Example: List just the URNs (for scripting)
print("\n" + "=" * 80)
print("All structured property URNs:")
print("-" * 80)

for urn in StructuredProperties.list_urns(client):
    print(urn)

```



### 通过 REST API 查询

也可以使用 REST API 检索结构化属性定义：


**REST API：获取结构化属性定义**

```bash
curl -X 'GET' \
  'http://localhost:8080/openapi/v3/entity/structuredProperty/urn%3Ali%3AstructuredProperty%3Aio.acryl.privacy.retentionTime/propertyDefinition' \
  -H 'accept: application/json'
```

响应示例：

```json
{
  "urn": "urn:li:structuredProperty:io.acryl.privacy.retentionTime",
  "propertyDefinition": {
    "value": {
      "qualifiedName": "io.acryl.privacy.retentionTime",
      "displayName": "Retention Time",
      "valueType": "urn:li:dataType:datahub.number",
      "description": "Number of days to retain data",
      "entityTypes": ["urn:li:entityType:datahub.dataset"],
      "cardinality": "SINGLE",
      "allowedValues": [
        {
          "value": { "double": 30 },
          "description": "30 days for ephemeral data"
        },
        {
          "value": { "double": 90 },
          "description": "90 days for regular data"
        }
      ]
    }
  }
}
```



## 集成点

### 结构化属性与其他实体的关系

结构化属性在整个 DataHub 生态中支持灵活的元数据扩展：

#### 应用于核心数据资产

结构化属性可附加到任意核心数据资产：

- **数据集**：跟踪数据质量指标、保留策略或合规分类
- **模式字段**：在列级别添加业务术语、敏感度标签或校验规则
- **图表与仪表板**：记录认证状态、评审日期或使用指南
- **数据任务与管道**：记录 SLA 要求、关键程度或维护计划

#### 应用于组织类实体

属性同样可扩展到组织与治理类实体：

- **域**：跟踪归属模式、成熟度级别或战略重要性
- **术语表术语**：添加审批状态、版本号或相关法规
- **数据产品**：记录产品生命周期阶段、目标受众或支持等级
- **用户与群组**：存储员工 ID、成本中心或访问复核日期

#### 与表单的关系

结构化属性与 DataHub 表单配合使用可以实现：

- **合规工作流**：表单可收集结构化属性值以确保政策合规
- **批量更新**：表单支持同时更新多个资产上的结构化属性
- **校验**：表单在数据收集过程中强制属性约束

#### 搜索与发现

结构化属性增强搜索能力：

- 标记为 `showInSearchFilters: true` 的属性可作为分面（faceted）搜索过滤器
- 用户可按属性值过滤结果，以找到满足特定条件的资产
- 聚合查询可汇总整个数据资产范围内的属性值分布

#### GraphQL Resolver

GraphQL 层通过多个 resolver 暴露结构化属性：

- `CreateStructuredPropertyResolver`：创建新的结构化属性定义
- `UpdateStructuredPropertyResolver`：修改已有属性定义（在允许的约束内）
- `DeleteStructuredPropertyResolver`：删除结构化属性定义
- `UpsertStructuredPropertiesResolver`：为实体赋值属性值（构建 MCP；孤儿赋值在 GMS 中处理）
- `RemoveStructuredPropertiesResolver`：从实体上移除属性值

这些 resolver 位于 `/datahub-graphql-core/src/main/java/com/linkedin/datahub/graphql/resolvers/structuredproperties/`。

#### GMS 赋值 mutator

`StructuredPropertiesAssignmentMutator`（`metadata-io/.../structuredproperties/hooks/`）是针对所有实体的 `structuredProperties` aspect 注册的 `MutationHook`：

- **读取**：过滤掉定义已被软删除的赋值（`StructuredPropertyUtils.filterSoftDelete`）。
- **写入**：当 `structuredProperties.dropMissingPropertyValuesWithWarning` 为 `true`（默认）时，`StructuredPropertiesValidator` 跳过对缺失定义的校验，且 `StructuredPropertiesAssignmentMutator` 在提交前丢弃这些赋值（`StructuredPropertyUtils.filterMissingPropertyDefinitions`），为每个被丢弃的 URN 记录一条警告；若没有剩余有效赋值则拒绝写入。

在 `application.yaml` 中通过 `structuredProperties.dropMissingPropertyValuesWithWarning` 配置，对应环境变量 `STRUCTURED_PROPERTIES_DROP_MISSING_PROPERTY_VALUES_WITH_WARNING`。

当 `structuredProperties.dropOversizedKeywordValuesFromIndex` 为 `true`（默认 `false`）时，超过 `keywordMaxLength` 的字符串值仍存储在实体上，但不会写入搜索文档（`SearchDocumentTransformer`）。写入不会被拒绝。GraphQL/OpenAPI 读取仍会返回存储的值。

#### 硬删除的副作用

硬删除 `structuredProperty` 实体时，`EntityServiceImpl` 会在 `deleteUrn` 之前捕获 `propertyDefinition` aspect，并额外发出一个 `propertyDefinition` DELETE 元数据变更日志，使 `PropertyDefinitionDeleteSideEffect` 即使在存储移除后仅可见主 aspect DELETE 的情况下，也能清理其他实体上的赋值。

## 显著的例外情况

### 属性定义约束

结构化属性一旦创建并投入使用，某些字段不可修改，以避免数据不一致：

**不可变字段：**

- **valueType**：不可更改数据类型（例如从 string 改为 number）
- **allowedValues**：不可移除或修改已有允许值（只能新增）
- **cardinality**：在未提升版本的情况下不可在 SINGLE 与 MULTIPLE 之间切换

**可修改字段：**

- **displayName**：可更新以提升可读性
- **description**：可补充或澄清
- **entityTypes**：可新增实体类型（但不可移除已有的）
- **allowedValues**：可追加额外的允许值
- **显示设置**：所有 `structuredPropertySettings` 均可自由修改

### 通过版本控制进行破坏性变更

若要进行向后不兼容的变更（如修改 cardinality 或移除允许值），必须：

1. 设置新的 `version` 值，格式为 `yyyyMMddhhmmss`
2. 应用更新后的定义
3. 接受旧值将变得不可访问
4. 使用新 schema 重新赋予属性值

这是一个破坏性操作，应谨慎规划。

### 软删除与硬删除

结构化属性支持两种删除模式：

**软删除**（通过 `status` aspect 设置 `removed: true`）：

- 属性定义仍保留在系统中
- 属性值在读取时被 `StructuredPropertiesAssignmentMutator` 隐藏，但不会从存储中删除
- 阻止新的赋值
- 使用该属性的搜索过滤器被禁用
- 通过设置 `removed: false` 完全可逆

**硬删除**（通过删除实体）：

- 彻底移除结构化属性定义实体
- 在实体移除之前发出额外的 `propertyDefinition` DELETE 事件，以确保赋值清理可靠执行
- 通过 `PropertyDefinitionDeleteSideEffect` 触发对其他实体上属性值的异步 PATCH REMOVE
- 启用 `dropMissingPropertyValuesWithWarning`（默认）后，后续写入时实体上残留的孤儿赋值可被清除
- 不可逆
- Elasticsearch 映射将持续存在直至重新索引

### 列级属性

为模式字段（列）创建属性时请注意：

- 设置 `showInColumnsTable: true` 会在所有数据集 schema 视图中显示该属性
- 列级属性会自动出现在列侧边栏中
- 过多可见属性会使界面显得杂乱，因此应审慎使用显示设置

### 搜索索引

结构化属性值使用特殊命名约定在 Elasticsearch 中建立索引：

- **未版本化**：`structuredProperties.io_acryl_privacy_retentionTime`
- **已版本化**：`structuredProperties._versioned.io_acryl_privacy_retentionTime02.20240614080000.string`

理解该约定对以下场景很重要：

- 使用 OpenAPI 的高级搜索查询
- 调试搜索问题
- 创建自定义聚合

更多信息请参考：

- [结构化属性功能指南](/docs/features/feature-guides/properties/overview.md)
- [结构化属性 API 教程](/docs/api/tutorials/structured-properties.md)


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](44-structuredproperty.md)。
