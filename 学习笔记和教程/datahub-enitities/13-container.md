---
title: 容器
entity: container
order: 13
source: https://docs.datahub.com/docs/generated/metamodel/entities/container.md
---

# 容器

容器（Container）实体是元数据模型中的核心实体，用于表示一组相关数据资产的分组。容器为数据集、图表、仪表盘以及其他容器提供层级化的组织结构，从而在数据平台中实现导航与结构发现。

## 身份（Identity）

容器通过 GUID（全局唯一标识符）唯一标识，该 GUID 通常由容器类型特有的属性组合推导得出。与数据集使用 platform、name 和 environment 不同，容器采用基于其层级属性的、更灵活的标识方案。

容器的 URN 结构为：`urn:li:container:{guid}`

GUID 通常根据容器特有的属性计算得出，例如：

- **数据库容器**：platform + instance + database name
- **Schema 容器**：platform + instance + database + schema name
- **项目容器**：platform + instance + project_id
- **文件夹容器**：platform + instance + folder_abs_path
- **桶容器**：platform + instance + bucket_name

### URN 示例

```
urn:li:container:b5e95fce839e7d78151ed7e0a7420d84
```

GUID 通过 `datahub_guid()` 函数基于一组属性字典生成。例如，一个 Snowflake schema 容器可由以下属性标识：

```python
{
  "platform": "snowflake",
  "instance": "prod_instance",
  "database": "analytics",
  "schema": "reporting"
}
```

## 现实世界概念

容器表示数据平台中的各种层级结构：

- **数据库**：关系型系统中的顶层组织单元（MySQL、PostgreSQL、Snowflake）
- **Schema**：数据库内部的逻辑分组（Snowflake schema、PostgreSQL schema）
- **项目**：云平台中的组织单元（BigQuery project）
- **数据集**：云平台中的逻辑分组（BigQuery dataset）
- **文件夹**：文件系统与数据湖中的目录结构（S3 folder、ADLS directory）
- **桶**：云对象存储中的顶层存储容器（S3 bucket、GCS bucket）
- **工作区**：BI 平台中的组织单元（Power BI workspace、Tableau site）
- **目录**：数据目录中的顶层组织单元（Unity Catalog、Iceberg catalog）
- **元数据存储**：存储元数据仓库（Hive metastore、Unity metastore）

## 重要能力

### 容器属性

`containerProperties` 方面（aspect）包含来自源系统的元数据：

- **name**：容器的显示名称（必填）
- **qualifiedName**：全限定名称（可选，例如 "prod.analytics.reporting"）
- **description**：来自源系统的描述
- **env**：环境标识（PROD、DEV、QA 等）
- **customProperties**：来自源系统的额外键值属性
- **externalUrl**：指向源系统中该容器的链接
- **created**：容器在源系统中创建的时间戳
- **lastModified**：容器在源系统中最后修改的时间戳

### 可编辑的容器属性

`editableContainerProperties` 方面允许用户通过 UI 覆盖或补充信息：

- **description**：用户提供的描述，用于补充或覆盖源系统的描述

这种分离确保了源系统的元数据与用户提供的标注信息不会相互冲突。

### 层级关系

容器通过 `container` 方面支持嵌套层级，该方面将容器链接到其父容器，从而实现多级组织结构：

```
Platform（隐式）
└── Database Container
    └── Schema Container
        └── Dataset
```

例如，在 Snowflake 中：

```
Snowflake Platform
└── ANALYTICS_DB（Database Container）
    └── REPORTING（Schema Container）
        └── SALES_METRICS（Dataset）
        └── REVENUE_TABLE（Dataset）
```

### 子类型

`subTypes` 方面用于指定容器的类型，帮助 UI 渲染相应的图标与行为。常见子类型包括：

- **Database**：关系型数据库容器
- **Schema**：数据库内的 schema 级容器
- **Project**：云项目容器（GCP、Azure）
- **Dataset**：BigQuery 数据集容器
- **Folder**：文件系统文件夹
- **Bucket**：对象存储桶
- **Workspace**：BI 平台工作区
- **Catalog**：数据目录容器
- **Metastore**：元数据存储容器
- **MLflow Experiment**（`MLAssetSubTypes.MLFLOW_EXPERIMENT`）：用于组织训练运行的 ML 实验容器

### 作为容器的 ML 实验

机器学习实验被建模为带有 `MLFLOW_EXPERIMENT` 子类型的容器。这一模式可以将相关的训练运行（即 `dataProcessInstance` 实体）组织成逻辑分组，以便比较与追踪：

```
ML Experiment（Container）
├── Training Run 1（DataProcessInstance）
├── Training Run 2（DataProcessInstance）
└── Training Run 3（DataProcessInstance）
```

训练运行通过 `container` 方面归属于实验。这一结构与常见 ML 平台（如 MLflow）的模式一致，并带来以下能力：

- 比较多次训练尝试的指标
- 追踪模型在迭代过程中的演进
- 按项目或目标组织训练工作

关于 ML 实验与训练运行的更多信息，请参阅：

- [ML 模型实体文档](19-mlmodel.md#training-runs-and-experiments)
- [训练运行的 DataProcessInstance 文档](06-dataprocessinstance.md#tracking-ml-training-run-in-a-container)

### 可包含的实体

以下实体类型可以包含在容器中：

- Datasets
- Charts
- Dashboards
- DataProcessInstances（例如 ML 实验中的训练运行）
- 其他 Containers（用于嵌套层级）

## 代码示例

### 创建数据库容器

**Python SDK：创建数据库容器**

```python
# Inlined from /metadata-ingestion/examples/library/container_create_database.py
# metadata-ingestion/examples/library/container_create_database.py
from datahub.emitter.mcp_builder import DatabaseKey
from datahub.sdk import Container, DataHubClient

client = DataHubClient.from_env()

container = Container(
    container_key=DatabaseKey(
        platform="snowflake",
        instance="production",
        database="analytics_db",
    ),
    display_name="Analytics Database",
    description="Main analytics database containing reporting and metrics data",
    subtype="Database",
    external_url="https://app.snowflake.com/analytics_db",
    parent_container=None,
)

client.entities.upsert(container)

print(f"Created database container with URN: {container.urn}")

```

### 创建带父容器的 Schema 容器

**Python SDK：创建带父数据库的 schema 容器**

```python
# Inlined from /metadata-ingestion/examples/library/container_create_schema.py
# metadata-ingestion/examples/library/container_create_schema.py
from datahub.emitter.mcp_builder import DatabaseKey, SchemaKey
from datahub.sdk import Container, DataHubClient

client = DataHubClient.from_env()

# First, create the database container
database_key = DatabaseKey(
    platform="snowflake",
    instance="production",
    database="analytics_db",
)

database_container = Container(
    container_key=database_key,
    display_name="Analytics Database",
    description="Main analytics database",
    subtype="Database",
)

client.entities.upsert(database_container)
print(f"Created database container: {database_container.urn}")

# Create a schema container within the database
schema_key = SchemaKey(
    platform="snowflake",
    instance="production",
    database="analytics_db",
    schema="reporting",
)

schema_container = Container(
    container_key=schema_key,
    display_name="Reporting Schema",
    description="Schema containing all reporting tables and views",
    subtype="Schema",
)

client.entities.upsert(schema_container)
print(f"Created schema container: {schema_container.urn}")
print("Schema container is nested under database container")

```

### 为容器添加元数据

**Python SDK：为容器添加标签、术语与负责人**

```python
# Inlined from /metadata-ingestion/examples/library/container_add_metadata.py
from datahub.emitter.mcp_builder import DatabaseKey
from datahub.sdk import ContainerUrn, CorpUserUrn, DataHubClient, DomainUrn, TagUrn

client = DataHubClient.from_env()

database_key = DatabaseKey(
    platform="snowflake",
    instance="production",
    database="analytics_db",
)

container = client.entities.get(ContainerUrn.from_string(database_key.as_urn()))

container.set_display_name("Analytics Database")
container.set_description(
    "Main analytics database containing reporting and metrics data"
)
container.set_subtype("Database")
container.set_external_url("https://app.snowflake.com/analytics_db")

container.set_tags([TagUrn("production"), TagUrn("analytics"), TagUrn("pii")])

container.set_terms(["urn:li:glossaryTerm:Finance.ReportingData"])

container.set_owners(
    [
        (CorpUserUrn("john.doe"), "DATAOWNER"),
        (CorpUserUrn("analytics-team"), "TECHNICAL_OWNER"),
    ]
)

container.set_domain(DomainUrn("Analytics"))

container.set_links(
    [
        (
            "https://wiki.company.com/analytics-db",
            "Database Documentation",
        ),
        (
            "https://jira.company.com/ANALYTICS-123",
            "Setup Ticket",
        ),
    ]
)

client.entities.update(container)

print(f"Updated container with comprehensive metadata: {container.urn}")
print(f"  - Tags: {len(container.tags or [])} tags")
print(f"  - Terms: {len(container.terms or [])} terms")
print(f"  - Owners: {len(container.owners or [])} owners")
print(f"  - Links: {len(container.links or [])} links")
print(f"  - Domain: {container.domain}")

```

### 通过 REST API 查询容器

可以使用标准的实体获取 API 检索容器：

**获取包含所有方面的容器实体**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3Acontainer%3Ab5e95fce839e7d78151ed7e0a7420d84'
```

响应将包含与该容器关联的所有方面，包括属性、负责人、标签、术语等。

若要查找某个容器内的所有实体，请使用 relationships API：

**查找容器内包含的所有实体**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3Acontainer%3Ab5e95fce839e7d78151ed7e0a7420d84&types=IsPartOf'
```

这将返回所有以该容器为父容器的实体（数据集、图表、仪表盘、子容器）。

## 集成点

### 与数据集的关系

数据集是容器中最常包含的实体。该关系通过数据集上的 `container` 方面建立，该方面指向容器 URN。

```python
# Dataset links to its parent container (schema)
dataset = Dataset(
    platform="snowflake",
    name="analytics_db.reporting.sales_table",
    env="PROD",
    parent_container=schema_key,  # Links to schema container
)
```

### 层级导航

容器通过父子关系在 DataHub UI 中实现层级导航：

1. **自顶向下浏览**：用户可以从数据库导航到 schema，再导航到表
2. **自底向上面包屑**：数据集在面包屑路径中显示其父容器
3. **浏览路径**：容器用于自动生成浏览路径

### GraphQL 解析器

容器实体拥有专门的 GraphQL 解析器：

- **ContainerEntitiesResolver**：检索容器内的所有实体（数据集、图表、仪表盘、子容器）
- **ParentContainersResolver**：检索任意实体的完整父容器层级

这些解析器支撑了 UI 的层级导航与容器概览页面。

### 常见使用模式

1. **数据库/Schema 层级**：关系型数据库使用 Database 与 Schema 容器
2. **项目/数据集层级**：BigQuery 使用 Project 与 Dataset 容器
3. **工作区/文件夹层级**：BI 工具使用 Workspace 容器进行组织
4. **桶/文件夹层级**：数据湖使用 Bucket 与 Folder 容器
5. **目录/Schema 层级**：现代目录（Unity、Iceberg）使用 Catalog 与 Schema 容器

## 值得注意的例外

### GUID 稳定性

容器 GUID 必须在多次摄取之间保持稳定。由于容器以 GUID 而非 URN 中的显式属性来标识，更改 GUID 计算方式将创建一个新的容器实体，而不是更新现有实体。

创建自定义容器时，请确保用于生成 GUID 的属性满足：

- 随时间保持稳定
- 在平台内唯一
- 派生自不可变的源系统标识符

### 自引用容器

虽然容器可以包含其他容器，但请注意不要创建循环引用。父子关系应构成有向无环图（DAG），而不是环。

### 环境处理

ContainerKey 中的 `env` 字段为向后兼容而做了特殊处理。在某些数据源中，平台实例被错误地设置成了环境值。`backcompat_env_as_instance` 标志用于处理这种情况。

使用 `env` 字段时：

- 将其设置为合法的 FabricType（PROD、DEV、QA 等）
- 不要将其用于平台实例标识
- 多实例部署请使用独立的 `instance` 字段

### 平台实例关联

与在 URN 中嵌入平台实例的数据集不同，容器通过 `dataPlatformInstance` 方面关联平台实例。这使容器可以与数据平台的特定实例相关联，同时保持 GUID 稳定。

### 访问控制

容器支持 `access` 方面，可用于在容器层级建模访问控制策略。这在以下场景中尤其有用：

- 数据库级权限
- Schema 级访问控制
- 项目级授权
- 工作区级安全策略

设置在容器上的访问控制可以被所包含的实体继承，不过该行为取决于具体平台的实现。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](13-container.md)。。
