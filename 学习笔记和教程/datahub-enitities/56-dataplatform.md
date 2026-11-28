---
title: 数据平台
entity: dataplatform
order: 56
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataplatform.md
---

# 数据平台

数据平台（Data Platform）是一个元数据实体，代表承载并管理数据资产的源系统、技术或工具。数据平台是 DataHub 元数据模型的基础构件，为所有数据集、仪表板、图表、作业和其他数据资产提供命名空间与分类体系。

数据平台的示例包括数据库（MySQL、PostgreSQL、Oracle）、数据仓库（Snowflake、BigQuery、Redshift）、BI 工具（Looker、Tableau、Power BI）、数据湖（S3、HDFS）、消息代理（Kafka），以及数据存放或流经的众多其他系统。

## 标识

数据平台由单个组成部分唯一标识：

- **platformName**：技术的标准化名称（例如 "mysql"、"snowflake"、"looker"、"kafka"）

数据平台的 URN 结构为：

```
urn:li:dataPlatform:<platformName>
```

### 示例

```
urn:li:dataPlatform:mysql
urn:li:dataPlatform:snowflake
urn:li:dataPlatform:bigquery
urn:li:dataPlatform:looker
urn:li:dataPlatform:kafka
urn:li:dataPlatform:s3
urn:li:dataPlatform:dbt
```

### 平台命名约定

平台名称遵循以下约定：

- **全小写**：所有平台名称均为小写（例如 "bigquery" 而非 "BigQuery"）
- **不含空格**：多词名称使用连字符（例如 "azure-ad" 而非 "Azure AD"）
- **面向技术**：名称表示具体技术，而非厂商或产品线
- **标准化**：DataHub 维护一份规范的平台名称列表以确保一致性

官方支持的数据平台完整列表维护在 DataHub 的引导配置 [data-platforms.yaml](https://github.com/datahub-project/datahub/blob/master/metadata-service/configuration/src/main/resources/bootstrap_mcps/data-platforms.yaml) 中。 中。

### 自定义平台

尽管 DataHub 内置了 100 多个预定义平台，你仍可以为以下场景创建自定义平台实体：

- 内部自建或专有的数据系统
- 尚未进入官方列表的新技术
- 相关系统的逻辑分组
- 具有特定配置的平台变体

创建自定义平台时，请遵循上述命名约定，并确保在你的 DataHub 实例内唯一。如果自定义平台上的数据集表示逻辑模型或规范而非物理资产，请在其 `dataPlatformInfo` aspect 中设置 `logical: true`。当 `logical` 缺失时，该平台被视为非逻辑平台。

## 重要能力

### 平台信息

`dataPlatformInfo` aspect 包含数据平台的核心元数据：

- **name**：平台的规范名称（最长 15 个字符，可搜索）
- **displayName**：用户友好的展示名称（例如平台 "bigquery" 对应 "Google BigQuery"）
- **type**：来自 PlatformType 枚举的平台类别
- **datasetNameDelimiter**：用于分隔数据集名称各组成部分的字符（例如 Oracle 用 "."，HDFS 用 "/"）
- **logical**：可选标志，指示该平台上的数据集表示逻辑模型或规范而非物理资产；缺失等同于 `false`
- **logoUrl**：可选的 logo 图片 URL，代表该平台

#### 平台类型

数据平台被归类为以下类别：

- **RELATIONAL_DB**：传统关系型数据库（MySQL、PostgreSQL、Oracle、SQL Server）
- **OLAP_DATASTORE**：联机分析处理系统（Pinot、Druid、ClickHouse）
- **KEY_VALUE_STORE**：键值与 NoSQL 数据库（Redis、DynamoDB、Cassandra）
- **SEARCH_ENGINE**：搜索与索引平台（Elasticsearch、Solr）
- **MESSAGE_BROKER**：事件流与消息系统（Kafka、Pulsar、RabbitMQ）
- **FILE_SYSTEM**：分布式文件系统（HDFS、NFS、本地文件系统）
- **OBJECT_STORE**：云对象存储（S3、GCS、Azure Blob Storage）
- **QUERY_ENGINE**：SQL 查询引擎（Presto、Trino、Athena、Hive）
- **OTHERS**：其他平台类型，包括 BI 工具、编排器、数据目录和专用系统

平台类型帮助 DataHub 理解如何与该平台交互，以及预期有哪些类型的元数据。

下面的代码片段展示了如何创建自定义数据平台。

**Python SDK：创建数据平台**

```python
# Inlined from /metadata-ingestion/examples/library/data_platform_create.py
# metadata-ingestion/examples/library/data_platform_create.py
import os

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DataPlatformInfoClass,
)

gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

platform_urn = "urn:li:dataPlatform:customdb"

platform_info = DataPlatformInfoClass(
    name="customdb",
    displayName="Custom Database Platform",
    type="RELATIONAL_DB",
    datasetNameDelimiter=".",
    logoUrl="https://company.com/logos/customdb.png",
)

event = MetadataChangeProposalWrapper(
    entityUrn=platform_urn,
    aspect=platform_info,
)

emitter.emit(event)
print(f"Created data platform {platform_urn}")

```

### 数据集名称分隔符

`datasetNameDelimiter` 字段对于理解各平台上的数据集命名约定至关重要：

- **"."**：大多数关系型数据库使用（例如 PostgreSQL 中的 `database.schema.table`）
- **"/"**：文件系统使用（例如 HDFS 中的 `/data/warehouse/customers`）
- **""**（空字符串）：数据集名称扁平、无层级时使用

该分隔符帮助 DataHub：

- 正确解析数据集名称
- 构建用于层级化导航的浏览路径
- 以用户友好的格式展示数据集名称
- 为平台上的数据集生成正确的 URN

### Logo URL

平台可以通过 `logoUrl` 字段提供自定义 logo，在 DataHub UI 中展示，帮助用户快速识别平台。DataHub 为所有官方支持的平台内置了 logo，而自定义平台可以指定自己的 logo URL。

## 集成点

### 与数据集的关系

数据平台是所有数据集的父实体。每个数据集 URN 都包含平台引用：

```
urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)
```

这一关系带来以下能力：

- **发现**：查找归属于特定平台的所有数据集
- **治理**：应用平台级策略与访问控制
- **血缘**：跟踪不同平台之间的数据流动
- **盘点**：了解数据在技术栈中的分布

### 与其他实体的关系

除数据集之外，平台还被许多其他实体类型引用：

- **Dashboards**：来自 Looker、Tableau、Superset 等平台的 BI 仪表板
- **Charts**：来自 BI 平台的可视化
- **DataFlows**：来自 Airflow、Prefect、Dagster 的编排工作流
- **DataJobs**：数据管道中的单个任务或作业
- **ML Models**：来自 SageMaker、MLflow 等平台的机器学习模型
- **DataProcesses**：来自 Flink、Spark 等平台的流式处理过程

所有这些实体的 URN 中都包含平台引用，从而形成一份完整的技术清单。

### 平台实例

对于运行同一平台多个实例的组织（例如多个 Snowflake 账号、多个生产 BigQuery 项目），DataHub 提供了 `dataPlatformInstance` 实体，从而可以区分：

- 平台：技术本身（例如 "snowflake"）
- 平台实例：该技术的某个具体部署（例如 "snowflake-prod-us-west"、"snowflake-dev-eu"）

平台实例引用其父平台，并添加环境、区域或账号等部署相关的元数据。

**Python SDK：创建平台实例**

```python
# Inlined from /metadata-ingestion/examples/library/platform_instance_create.py
# metadata-ingestion/examples/library/platform_instance_create.py
import os

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataPlatformInstancePropertiesClass

# Create the platform instance URN
platform_instance_urn = builder.make_dataplatform_instance_urn(
    platform="mysql", instance="production-mysql-cluster"
)

# Define properties for the platform instance
platform_properties = DataPlatformInstancePropertiesClass(
    name="Production MySQL Cluster",
    description="Primary MySQL database cluster serving production workloads in US West region",
    customProperties={
        "region": "us-west-2",
        "environment": "production",
        "cluster_size": "3-node",
        "version": "8.0.35",
    },
    externalUrl="https://cloud.mysql.com/console/clusters/prod-cluster",
)

# Create metadata change proposal
platform_instance_mcp = MetadataChangeProposalWrapper(
    entityUrn=platform_instance_urn,
    aspect=platform_properties,
)

# Emit metadata to DataHub
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")
emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
emitter.emit_mcp(platform_instance_mcp)

print(f"Created platform instance: {platform_instance_urn}")

```

### 摄取来源

数据平台通常通过两种机制自动创建：

1. **引导数据**：DataHub 启动时，从引导配置加载约 100 个预定义平台
2. **摄取连接器**：当你运行摄取源（例如 Snowflake 连接器）时，它会为所摄取的资产自动创建平台引用

除非你要添加标准引导列表未覆盖的自定义或内部系统，否则很少需要手动创建平台实体。

### 搜索与发现

平台在 DataHub 中完全可搜索：

- **平台名称搜索**：按规范名称查找平台
- **展示名称搜索**：使用用户友好的展示名称搜索
- **平台过滤**：按平台筛选数据集及其他实体
- **平台浏览**：在按平台组织的实体中导航

这使用户能够以平台为中心的视角探索数据全景。

### GraphQL API

可以通过 GraphQL API 查询数据平台，获取：

- 平台元数据（名称、类型、logo）
- 平台上的实体数量
- 平台配置信息

虽然平台很少通过 GraphQL 创建（它们大多是引导数据），但该 API 支持以编程方式访问平台信息。

## 值得注意的例外

### 引导平台与自定义平台

DataHub 区分以下两类：

- **引导平台**：启动时加载的约 100 个平台，由 DataHub 项目维护
- **自定义平台**：你为自己的使用场景创建的平台

引导平台：

- 拥有官方 logo 和展示名称
- 在 DataHub 升级过程中持续维护
- 与 DataHub 的摄取连接器一同测试
- 遵循一致的命名约定

自定义平台：

- 可能没有 logo（除非你提供 logoUrl）
- 需要你自己维护
- 可能没有预置的摄取连接器
- 应遵循相同的命名约定以避免混淆

### 平台名称不可变性

一旦平台创建完成且已有资产与之关联，平台名称在实践中即不可更改。更改平台名称需要：

- 迁移所有引用该平台的数据集 URN
- 更新所有血缘边
- 重新摄取来自该平台的全部元数据

如果需要重命名平台，通常更简单的做法是：

1. 用期望的名称创建新平台
2. 使用新的平台名称重新摄取所有资产
3. 弃用或删除旧平台

### 平台名称长度限制

平台名称限制为 15 个字符（由 `@validate.strlen.max = 15` 强制）。这是一个历史遗留约束，用于确保平台名称简洁，并能在 URN 与 UI 展示中良好呈现。

如果你的平台自然名称超过 15 个字符，请使用缩写或首字母缩写：

- "azure-synapse" → "synapse"
- "amazon-redshift" → "redshift"
- "google-bigquery" → "bigquery"

全名可以放入 `displayName` 字段，不受长度限制。

### 大小写敏感性

平台名称在 URN 中区分大小写，但约定上始终使用小写。避免创建仅大小写不同的平台（例如 "MySQL" 和 "mysql"），否则会造成混淆并可能引发 URN 冲突。

### 平台类型是描述性的，而非功能性的

`type` 字段（FILE_SYSTEM、RELATIONAL_DB 等）主要用于分类和展示。DataHub 不会根据平台类型施加不同行为。不同类型的两个平台在系统中被同等对待。

不过，连接器和摄取逻辑可能会利用平台类型来判定：

- 提取哪些元数据
- 如何解析数据集名称
- 预期哪些血缘模式
- 可进行哪些数据剖析或使用情况采集

## 常见平台类别

### 数据库与数据仓库

**RELATIONAL_DB 平台**：MySQL、PostgreSQL、Oracle、SQL Server、MariaDB、DB2

**OLAP_DATASTORE 平台**：Snowflake、BigQuery、Redshift、Clickhouse、Pinot、Druid

这些平台通常具备：

- 层级化的数据集名称（database.schema.table）
- 以 "." 作为分隔符
- Schema 元数据（列、类型、约束）
- 用于使用情况与血缘的查询日志元数据

### 商业智能工具

**OTHERS 平台类型**（BI 专用）：Looker、Tableau、Power BI、Metabase、Superset、Mode

这些平台通常具备：

- 仪表板与图表实体
- 从仪表板到底层数据集的血缘
- 视图与交互的使用统计
- 关于报表作者与调度计划的元数据

### 数据湖与对象存储

**OBJECT_STORE 平台**：S3、GCS、Azure Blob Storage、MinIO

**FILE_SYSTEM 平台**：HDFS、NFS、Azure Data Lake

这些平台通常具备：

- 以 "/" 作为分隔符
- 基于文件的数据集（Parquet、Avro、CSV、JSON）
- 基于路径的命名约定
- 读时模式（schema-on-read）元数据

### 流式平台

**MESSAGE_BROKER 平台**：Kafka、Pulsar、Kinesis、Event Hubs、RabbitMQ

这些平台通常具备：

- 主题（topic）或流数据集
- Schema 注册表集成
- 实时血缘跟踪
- 吞吐与延迟指标

### 编排与管道工具

**OTHERS 平台类型**（编排专用）：Airflow、Prefect、Dagster、Luigi、Argo

这些平台通常具备：

- DataFlow（管道）与 DataJob（任务）实体
- DAG 结构与依赖关系
- 执行统计与运行历史
- 基于作业依赖的血缘

### 转换工具

**OTHERS 平台类型**（转换专用）：dbt、Spark、Flink、Databricks

这些平台通常具备：

- 强大的列级血缘
- 转换逻辑元数据
- 模型/作业实体
- 测试与文档元数据

## 使用场景

数据平台在 DataHub 中支撑若干关键使用场景：

1. **技术盘点**：了解组织使用了哪些平台以及使用程度
2. **平台治理**：在平台级别应用策略与访问控制
3. **迁移规划**：在整合或替换平台时识别需要迁移的数据集
4. **成本优化**：跟踪哪些平台承载了最多/最少被使用的数据
5. **跨平台血缘**：在数据生态中跨不同技术追踪数据流
6. **技术标准化**：强制或监控对已批准平台的采用
7. **影响分析**：了解平台故障或变更的影响范围
8. **发现式导航**：按平台浏览和筛选资产，便于发现

通过将平台确立为一等实体，DataHub 为你所在组织的数据技术全景提供了完整视图。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](56-dataplatform.md)。。
