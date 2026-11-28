---
title: 数据契约
entity: datacontract
order: 41
source: https://docs.datahub.com/docs/generated/metamodel/entities/datacontract.md
---

# 数据契约

数据契约（Data Contract）是数据资产的生产方与消费方之间的约定，用于定义关于数据质量、结构与运维特征的期望和保证。数据契约是一种正式承诺，通过明确数据消费方可以从数据生产方获得什么，从而帮助在数据管道中建立信任与可靠性。

DataHub 中的数据契约构建在[断言（assertion）](18-assertion.md)之上，代表一组经过整理的、针对物理数据资产的可验证保证。它们以生产方为中心（producer-oriented），即每个物理数据资产只有一个由其生产方拥有的契约，其中声明消费方可以依赖的标准与 SLA。

## 标识

数据契约由单个唯一字符串标识符来标识：

- 唯一契约 id：用于唯一标识该契约的字符串标识符。可以是任意字符串值，通常会根据被契约的实体自动生成。

数据契约的 URN 结构为：`urn:li:dataContract:<contract-id>`

URN 示例：

- `urn:li:dataContract:my-critical-dataset-contract`
- `urn:li:dataContract:a1b2c3d4-e5f6-7890-abcd-ef1234567890`

以编程方式创建数据契约时，可以显式指定契约 ID，也可以根据被契约的实体自动生成。自动生成会使用由实体 URN 派生的 GUID 创建稳定、确定性的 ID，从而确保契约在多次运行之间可复现。

## 重要能力

数据契约通过断言提供三类主要保证：

### 契约属性

`dataContractProperties` aspect 定义了契约的核心特征，包括：

- **实体关联**：该契约所适用的实体（通常是数据集）的 URN。目前 DataHub 支持数据集契约，未来计划支持数据产品及其他实体类型。
- **Schema 契约**：定义对数据资产逻辑结构期望的断言。Schema 契约确保你的数据结构保持一致并符合消费方的预期。
- **新鲜度契约**：定义数据新鲜度运维 SLA 的断言。这些契约规定数据应有多新，帮助消费方理解可以依赖的新鲜度保证。
- **数据质量契约**：定义表级或列级质量期望的断言。其中包括对数据完整性、准确性、有效性以及自定义质量检查的约束。
- **原始契约**：契约定义的可选 YAML 格式字符串表示，便于存储原始的契约规格说明。

每种契约类型（schema、freshness、data quality）都包含对断言实体的引用，而这些断言实体定义了实际的校验逻辑与评估标准。

下面的代码片段展示了如何创建一个包含 schema、freshness 与 data quality 断言的基础数据契约。


**Python SDK：创建数据契约**

```python
# Inlined from /metadata-ingestion/examples/library/datacontract_create_basic.py
# metadata-ingestion/examples/library/datacontract_create_basic.py
import os

from datahub.emitter.mce_builder import make_assertion_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DataContractPropertiesClass,
    DataContractStateClass,
    DataContractStatusClass,
    DataQualityContractClass,
    FreshnessContractClass,
    SchemaContractClass,
    StatusClass,
)

dataset_urn = make_dataset_urn(platform="snowflake", name="purchases", env="PROD")

schema_assertion_urn = make_assertion_urn("schema-assertion-for-purchases")
freshness_assertion_urn = make_assertion_urn("freshness-assertion-for-purchases")
quality_assertion_urn_1 = make_assertion_urn("quality-assertion-for-purchases-1")
quality_assertion_urn_2 = make_assertion_urn("quality-assertion-for-purchases-2")

contract_urn = "urn:li:dataContract:purchases-contract"

properties_aspect = DataContractPropertiesClass(
    entity=dataset_urn,
    schema=[SchemaContractClass(assertion=schema_assertion_urn)],
    freshness=[FreshnessContractClass(assertion=freshness_assertion_urn)],
    dataQuality=[
        DataQualityContractClass(assertion=quality_assertion_urn_1),
        DataQualityContractClass(assertion=quality_assertion_urn_2),
    ],
)

status_aspect = StatusClass(removed=False)

contract_status_aspect = DataContractStatusClass(state=DataContractStateClass.ACTIVE)

rest_emitter = DatahubRestEmitter(
    gms_server=os.getenv("DATAHUB_GMS_URL", "http://localhost:8080"),
    token=os.getenv("DATAHUB_GMS_TOKEN"),
)

for event in MetadataChangeProposalWrapper.construct_many(
    entityUrn=contract_urn,
    aspects=[
        properties_aspect,
        status_aspect,
        contract_status_aspect,
    ],
):
    rest_emitter.emit(event)

print(f"Created data contract {contract_urn}")

```



### Schema 契约

Schema 契约确保数据资产的结构符合预期。它们在以下方面尤为重要：

- 防止数据管道中的破坏性变更
- 确保对下游消费方的向后兼容
- 记录数据资产的预期结构
- 校验 schema 变更是有意为之且受控的

一个 schema 契约引用一个 schema 断言实体，该实体包含实际的 schema 规格说明与校验逻辑。断言既可以使用 DataHub 内置的断言框架创建，也可以通过集成 dbt、Great Expectations 等外部工具创建。


**Python SDK：为已有数据契约添加 schema 契约**

```python
# Inlined from /metadata-ingestion/examples/library/datacontract_add_schema_contract.py
# metadata-ingestion/examples/library/datacontract_add_schema_contract.py

from datahub.emitter.mce_builder import make_assertion_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    DataContractPropertiesClass,
    SchemaContractClass,
)

contract_urn = "urn:li:dataContract:purchases-contract"

graph = DataHubGraph(config=DatahubClientConfig(server="http://localhost:8080"))

contract_properties = graph.get_aspect(
    entity_urn=contract_urn,
    aspect_type=DataContractPropertiesClass,
)

if not contract_properties:
    raise SystemExit(f"Contract {contract_urn} not found")

new_schema_assertion_urn = make_assertion_urn("new-schema-assertion")

existing_schema = contract_properties.schema or []
existing_schema.append(SchemaContractClass(assertion=new_schema_assertion_urn))

contract_properties.schema = existing_schema

event = MetadataChangeProposalWrapper(
    entityUrn=contract_urn,
    aspect=contract_properties,
)

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
rest_emitter.emit(event)

print(f"Added schema contract to {contract_urn}")

```



### 新鲜度契约

新鲜度契约定义数据应当有多新的 SLA。它们有助于回答如下问题：

- 该数据集应当多久更新一次？
- 可接受的最大数据陈旧程度是多少？
- 消费方可以在什么时候期待新数据到达？

新鲜度契约对于时效性敏感的应用至关重要，因为陈旧数据可能导致错误决策或错失机会。它们通常规定诸如“数据最多不应超过 2 小时未更新”或“数据每天至少更新一次”之类的阈值。


**Python SDK：为已有数据契约添加新鲜度契约**

```python
# Inlined from /metadata-ingestion/examples/library/datacontract_add_freshness_contract.py
# metadata-ingestion/examples/library/datacontract_add_freshness_contract.py

from datahub.emitter.mce_builder import make_assertion_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    DataContractPropertiesClass,
    FreshnessContractClass,
)

contract_urn = "urn:li:dataContract:purchases-contract"

graph = DataHubGraph(config=DatahubClientConfig(server="http://localhost:8080"))

contract_properties = graph.get_aspect(
    entity_urn=contract_urn,
    aspect_type=DataContractPropertiesClass,
)

if not contract_properties:
    raise SystemExit(f"Contract {contract_urn} not found")

new_freshness_assertion_urn = make_assertion_urn("new-freshness-assertion")

existing_freshness = contract_properties.freshness or []
existing_freshness.append(FreshnessContractClass(assertion=new_freshness_assertion_urn))

contract_properties.freshness = existing_freshness

event = MetadataChangeProposalWrapper(
    entityUrn=contract_urn,
    aspect=contract_properties,
)

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
rest_emitter.emit(event)

print(f"Added freshness contract to {contract_urn}")

```



### 数据质量契约

数据质量契约定义关于数据质量特征的期望。其中可以包括：

- **完整性**：关键列中不含空值，或空值比例低于某个阈值
- **有效性**：取值符合预期的格式、范围或模式
- **准确性**：取值满足业务规则与约束
- **一致性**：列之间的关系得以保持
- **自定义检查**：面向业务场景的特定校验逻辑

与 schema 契约和新鲜度契约（通常每个数据集只有一个）不同，一个数据契约可以包含多个数据质量断言，每个断言针对数据质量的不同方面。


**Python SDK：为已有数据契约添加数据质量契约**

```python
# Inlined from /metadata-ingestion/examples/library/datacontract_add_quality_contract.py
# metadata-ingestion/examples/library/datacontract_add_quality_contract.py

from datahub.emitter.mce_builder import make_assertion_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    DataContractPropertiesClass,
    DataQualityContractClass,
)

contract_urn = "urn:li:dataContract:purchases-contract"

graph = DataHubGraph(config=DatahubClientConfig(server="http://localhost:8080"))

contract_properties = graph.get_aspect(
    entity_urn=contract_urn,
    aspect_type=DataContractPropertiesClass,
)

if not contract_properties:
    raise SystemExit(f"Contract {contract_urn} not found")

new_quality_assertion_urn_1 = make_assertion_urn("completeness-check-user-id")
new_quality_assertion_urn_2 = make_assertion_urn("validity-check-email-format")

existing_quality = contract_properties.dataQuality or []
existing_quality.extend(
    [
        DataQualityContractClass(assertion=new_quality_assertion_urn_1),
        DataQualityContractClass(assertion=new_quality_assertion_urn_2),
    ]
)

contract_properties.dataQuality = existing_quality

event = MetadataChangeProposalWrapper(
    entityUrn=contract_urn,
    aspect=contract_properties,
)

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
rest_emitter.emit(event)

print(f"Added data quality contracts to {contract_urn}")

```



### 契约状态

`dataContractStatus` aspect 跟踪契约的当前状态。契约可以处于以下两种状态之一：

- **ACTIVE**：契约已生效并被执行。违约应当触发告警或阻断数据管道。
- **PENDING**：契约待实施。可以用于可见性或规划目的，但尚未被执行。

契约状态还可以包含自定义属性，用于记录契约状态的额外元数据。

**Python SDK：更新数据契约的状态**

```python
# Inlined from /metadata-ingestion/examples/library/datacontract_update_status.py
# metadata-ingestion/examples/library/datacontract_update_status.py

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DataContractStateClass,
    DataContractStatusClass,
)

contract_urn = "urn:li:dataContract:purchases-contract"

contract_status_aspect = DataContractStatusClass(state=DataContractStateClass.ACTIVE)

event = MetadataChangeProposalWrapper(
    entityUrn=contract_urn,
    aspect=contract_status_aspect,
)

rest_emitter = DatahubRestEmitter(gms_server="http://localhost:8080")
rest_emitter.emit(event)

print(f"Updated status of data contract {contract_urn} to ACTIVE")

```



### 标签与术语表术语

与其他 DataHub 实体一样，数据契约也可以附加标签与术语表术语。这些有助于：

- 按业务领域、关键程度或其他维度对契约分类
- 将契约关联到业务术语表术语，以便更好地理解
- 在 DataHub UI 中筛选和搜索契约

数据契约上的标签与术语遵循与其他实体相同的模式，使用 `globalTags` 与 `glossaryTerms` aspects。

### 结构化属性

数据契约支持结构化属性，允许你为契约附加自定义的强类型元数据。这在以下场景下很有用：

- 添加契约专属元数据，例如 SLA 等级、执行级别或评审状态
- 与外部契约管理系统集成
- 记录业务上下文与归属信息

结构化属性在平台级别定义，可应用到任意数据契约实体。

## 集成点

### 与断言的关系

数据契约构建在[断言](18-assertion.md)实体之上。每个契约都包含对断言 URN 的引用，这些断言定义了实际的校验逻辑。这种拆分方式带来以下好处：

- 在多个契约之间复用断言
- 将断言逻辑与契约定义独立管理
- 在契约上下文之外评估断言
- 跟踪断言结果与历史记录

契约与断言之间的关系通过 `ContractFor` 关系（契约指向实体）以及 `IncludesSchemaAssertion`、`IncludesFreshnessAssertion`、`IncludesDataQualityAssertion` 关系（契约指向断言）来建立。

### 与数据集的关系

目前，数据契约主要与[数据集](01-dataset.md)实体关联。`dataContractProperties` aspect 包含一个引用数据集 URN 的 `entity` 字段。该关系通过 `ContractFor` 关系类型记录。

一个数据集同一时间可以有一个生效的数据契约，但该契约可以被更新或替换。消费方可以查询数据集以获取其关联的契约，并了解可以依赖的保证。

### 与数据质量工具的集成

数据契约可与外部的数据质量和测试工具集成：

- **dbt 测试**：dbt 测试结果可以作为断言摄取到 DataHub，随后在数据契约中引用。这让你既能使用 dbt 的测试框架，又能在 DataHub 中管理契约。
- **Great Expectations**：Great Expectations 检查点可以通过 DataHubValidationAction 将断言结果发布到 DataHub，使期望套件成为数据契约的一部分。
- **自定义工具**：任何外部系统都可以通过 API 将断言结果发布到 DataHub，从而在现有数据质量基础设施之上构建数据契约。

### GraphQL API

数据契约可通过 DataHub 的 GraphQL API 访问，该 API 提供：

- **Upsert 操作**：使用 `upsertDataContract` mutation 创建或更新契约
- **查询操作**：获取契约详情，包括所有关联的断言
- **契约评估**：通过评估所有关联断言来检查契约状态
- **实体解析**：从数据集导航到其契约，反之亦然

GraphQL API 特别适合将数据契约集成到 CI/CD 管道、自定义 UI 或工作流编排系统中。

### REST API

数据契约可以使用 DataHub 的 REST API 创建、读取、更新和删除。标准的实体 CRUD 操作均适用：

- `POST /entities` - 创建或更新数据契约实体
- `GET /entities/urn:li:dataContract:<id>` - 按 URN 获取数据契约
- `DELETE /entities/urn:li:dataContract:<id>` - 删除数据契约

也可以使用针对特定 aspect 的端点单独更新 aspect，从而对契约属性和状态进行细粒度控制。

## 值得注意的例外情况

### 生产方与消费方导向

DataHub 的数据契约以生产方为中心，即每个物理数据资产都有一个由生产方拥有的契约。这一设计选择使契约易于管理，并确保归属清晰。

然而，这未必适用于所有用例。有些组织更偏好以消费方为导向的契约，即每个消费方为共享数据资产定义自己的期望。虽然 DataHub 并不直接支持消费方导向的契约，但可以通过以下方式实现类似功能：

- 在同一数据集上创建多个由不同所有者持有的断言
- 使用标签或结构化属性标明哪些消费方关注哪些断言
- 构建自定义工作流，为不同消费方评估断言的子集

### 契约执行

DataHub 中的数据契约定义期望，但不会自动执行它们。执行依赖于：

- 配置断言评估（使用 DataHub 内置能力或外部工具）
- 配置在契约被违反时的告警与通知
- 将契约检查集成到数据管道和 CI/CD 工作流中

DataHub 提供了定义与跟踪契约的框架，但实际的执行需要结合你的数据基础设施做额外的集成工作。

### 断言生命周期

删除数据契约时，关联的断言不会被自动删除。这是有意为之——断言可以独立存在，也可能被其他契约使用或被单独监控。

如果希望同时移除契约及其断言，必须分别删除两者。这样可以确保即使契约发生变化，断言定义及其历史结果仍被保留。

### 基于 YAML 的契约定义

DataHub 支持使用 `DataContract` Python 模型在 YAML 文件中定义数据契约。这提供了一种更简单、声明式的契约定义方式，可进行版本控制并像代码一样评审。

YAML 格式在以下方面尤其有用：

- 将契约定义纳入基础设施即代码（IaC）工作流
- 将契约定义与 dbt 模型或其他数据管道代码存放在一起
- 通过标准代码评审流程评审契约变更

不过，基于 YAML 的契约在摄取时会被转换为底层的 MCP（Metadata Change Proposal）格式，因此所有操作最终使用的都是相同的底层实体与 aspect 结构。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](41-datacontract.md)。
