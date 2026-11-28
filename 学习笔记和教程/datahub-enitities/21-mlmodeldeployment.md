---
title: ML 模型部署
entity: mlmodeldeployment
order: 21
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlmodeldeployment.md
---

# ML 模型部署（ML Model Deployment）

ML 模型部署表示在生产或其他环境中运行的机器学习模型实例。它们追踪 ML 模型的运维方面，包括部署状态、平台、配置与生命周期。模型部署与 ML 模型本身不同——ML 模型代表已训练出的制品，而部署则代表该模型在特定环境中提供预测服务的具体实例。

## 身份（Identity）

ML 模型部署由三部分信息标识：

- **部署所托管的平台**：承载该模型的具体部署或服务平台。例如 `sagemaker`、`azureml`、`vertexai`、`mlflow`、`seldon`、`kserve` 等，对应一个数据平台 URN。
- **部署名称**：每个平台都有自己的部署命名方式。例如 SageMaker 使用 endpoint 名称，而 Azure ML 使用工作区内的部署名称。
- **环境或来源**：该限定符指示部署运行所在的环境（PROD、DEV、TEST 等），类似于数据集使用的 fabric 概念。

ML 模型部署标识符的示例为 `urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,recommendation-endpoint,PROD)`。

## 重要能力

### 部署属性

关于部署的核心元数据存储在 `mlModelDeploymentProperties` 方面中，包括：

- **Description**：说明部署用途与配置的文档
- **Deployment Status**：部署当前的运行状态，可以是：
  - `IN_SERVICE`：正在提供预测服务的活跃部署
  - `OUT_OF_SERVICE`：当前不提供流量的部署
  - `CREATING`：正在置备的部署
  - `UPDATING`：正在以新配置更新的部署
  - `ROLLING_BACK`：正在回滚到先前版本的部署
  - `DELETING`：正在移除的部署
  - `FAILED`：处于错误状态的部署
  - `UNKNOWN`：状态未映射或未知的部署
- **Version**：部署配置的版本
- **Created At**：指示部署创建时间的时间戳
- **Custom Properties**：附加的平台特定配置细节
- **External URL**：在原生平台中查看该部署的链接

以下代码片段展示如何创建 ML 模型部署。

**Python SDK：创建 ML 模型部署**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_deployment_create.py
import os

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Get DataHub connection details from environment
gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
token = os.getenv("DATAHUB_GMS_TOKEN")

# Create a deployment URN - the unique identifier for the ML model deployment
deployment_urn = builder.make_ml_model_deployment_urn(
    platform="sagemaker",
    deployment_name="recommendation-endpoint",
    env="PROD",
)

# Define deployment properties with status and custom properties
deployment_properties = models.MLModelDeploymentPropertiesClass(
    description="Production deployment of recommendation model on SageMaker",
    customProperties={
        "instance_type": "ml.m5.xlarge",
        "instance_count": "3",
        "endpoint_config": "recommendation-endpoint-config-v1",
    },
    externalUrl="https://console.aws.amazon.com/sagemaker/home#/endpoints/recommendation-endpoint",
    status=models.DeploymentStatusClass.IN_SERVICE,
)

# Create a metadata change proposal
event = MetadataChangeProposalWrapper(
    entityUrn=deployment_urn,
    aspect=deployment_properties,
)

# Emit the metadata
rest_emitter = DatahubRestEmitter(gms_server=gms_server, token=token)
rest_emitter.emit(event)
print(f"Created ML model deployment: {deployment_urn}")

```

### 将部署与模型关联

ML 模型部署通过 `mlModelProperties.deployments` 字段与其底层 ML 模型建立连接。这一关系带来以下能力：

- **部署追踪**：了解模型部署在何处、以何种方式运行
- **版本管理**：追踪每个环境中部署的是哪个模型版本
- **影响分析**：了解模型在生产环境的影响范围
- **回滚规划**：在模型出现问题时定位活跃的部署

**Python SDK：将部署关联到 ML 模型**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_deployment_add_to_model.py
from datahub.emitter import mce_builder
from datahub.metadata.urns import MlModelUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

mlmodel_urn = MlModelUrn(platform="sagemaker", name="recommendation-model")

deployment_urn = mce_builder.make_ml_model_deployment_urn(
    platform="sagemaker",
    deployment_name="recommendation-endpoint",
    env="PROD",
)

mlmodel = client.entities.get(mlmodel_urn)
mlmodel.add_deployment(deployment_urn)

client.entities.update(mlmodel)

```

### 标签与分类

ML 模型部署可通过 `globalTags` 方面附加标签。标签可用于：

- 按用途对部署分类（生产、金丝雀、影子）
- 追踪成本中心或团队
- 标记需要合规或安全审查的部署
- 按模型类型或使用场景组织部署

### 负责人

负责人通过 `ownership` 方面与部署关联。负责人可以是技术负责人（ML 工程师、MLOps 团队），也可以是业务负责人（产品经理、数据科学家），他们对部署负责。负责人信息有助于：

- 对部署健康状况与性能负责
- 在事件发生时提供联系信息
- 访问控制与权限管理
- 组织治理

**Python SDK：为部署添加负责人**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_deployment_add_owner.py
import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

gms_endpoint = "http://localhost:8080"
emitter = DatahubRestEmitter(gms_server=gms_endpoint, extra_headers={})
graph = DataHubGraph(DatahubClientConfig(server=gms_endpoint))

deployment_urn = builder.make_ml_model_deployment_urn(
    platform="sagemaker",
    deployment_name="recommendation-endpoint",
    env="PROD",
)

owner_to_add = builder.make_user_urn("mlops_team")

current_ownership = graph.get_aspect(
    entity_urn=deployment_urn, aspect_type=models.OwnershipClass
)

if current_ownership:
    if owner_to_add not in [owner.owner for owner in current_ownership.owners]:
        current_ownership.owners.append(
            models.OwnerClass(
                owner=owner_to_add,
                type=models.OwnershipTypeClass.TECHNICAL_OWNER,
            )
        )
else:
    current_ownership = models.OwnershipClass(
        owners=[
            models.OwnerClass(
                owner=owner_to_add,
                type=models.OwnershipTypeClass.TECHNICAL_OWNER,
            )
        ]
    )

emitter.emit(
    MetadataChangeProposalWrapper(
        entityUrn=deployment_urn,
        aspect=current_ownership,
    )
)

```

### 平台实例

`dataPlatformInstance` 方面提供有关部署平台具体实例的额外上下文。当组织存在同一平台的多个实例时（例如多个 SageMaker 账号、不同的 Azure ML 工作区、独立的 Kubernetes 集群），这一点尤为重要。

### 弃用与生命周期管理

当部署计划下线时，可使用 `deprecation` 方面将其标记为已弃用，包括：

- **Deprecation Flag**：将部署标记为已弃用
- **Decommission Time**：计划移除部署的日期
- **Deprecation Note**：关于为何弃用该部署以及由什么替代的信息
- **Replacement**：指向应改用的新部署的引用

`status` 方面也可用于对部署进行软删除（标记为已移除），适用于部署已下线但希望保留历史元数据的情况。

### 组织上下文

#### 容器

部署可以通过 `container` 方面归属于某个父容器（例如 ML 工作区、命名空间或项目），从而形成层级结构：

```
ML Workspace（Container）
├── Model Deployment 1
├── Model Deployment 2
└── Model Deployment 3
```

这种层级有助于：

- 按项目或团队组织部署
- 在工作区层级进行访问控制管理
- 了解资源利用率与成本
- 导航相关部署

## 与外部系统的集成

### 从 ML 平台摄取

ML 模型部署通常使用 DataHub 的摄取连接器从 ML 平台自动摄取：

- **SageMaker**：摄取 endpoint 部署及其配置与状态
- **Azure ML**：从工作区摄取模型部署
- **Vertex AI**：从 Google Cloud 摄取 endpoint 部署
- **MLflow**：摄取已注册的模型部署
- **Seldon Core / KServe**：从 Kubernetes 摄取推理服务

每个连接器都会将平台特定的部署元数据映射到 DataHub 的标准化部署模型。

### 查询部署信息

可以使用 DataHub 的 REST API 获取部署信息：

**获取部署实体快照**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AmlModelDeployment%3A(urn%3Ali%3AdataPlatform%3Asagemaker,recommendation-endpoint,PROD)'
```

响应包含该部署的所有方面，包括：

- 部署属性（状态、版本、描述）
- 负责人信息
- 标签与分类
- 平台实例详情
- 弃用状态

### Relationships API

你可以查询部署关系，以了解它与其他实体的连接：

**查找某个 ML 模型的所有部署**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3AmlModel%3A(urn%3Ali%3AdataPlatform%3Asagemaker,recommendation-model,PROD)&types=DeployedTo'
```

这将返回指定 ML 模型的所有部署。

**查找某个部署对应的 ML 模型**

```bash
curl 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3AmlModel%3A(urn%3Ali%3AdataPlatform%3Asagemaker,recommendation-model,PROD)&types=DeployedTo'
```

这将返回部署到该指定部署上的 ML 模型。

## 值得注意的例外

### 部署与模型的区别

理解 ML 模型与 ML 模型部署之间的区别非常重要：

- **ML Model**：代表已训练出的模型制品，包含训练数据、指标、超参数与模型元数据。一个模型可以有多个版本，并且可以独立于任何部署而存在。

- **ML Model Deployment**：代表模型的一个运行实例，正在提供预测服务。部署引用特定的模型版本，并包含状态、配置与服务平台细节等运维元数据。

这种分离带来以下能力：

- 追踪同一模型部署到多个环境（dev、staging、prod）
- 了解部署历史与回滚情况
- 将运维生命周期与模型开发生命周期分开管理
- 支持对同一模型进行 A/B 测试与金丝雀发布

### 每个模型可有多个部署

单个 ML 模型可以同时拥有多个部署：

- 不同环境（生产、预发布、开发）
- 不同区域（美国、欧洲、亚洲）
- 不同配置（批处理与实时、不同实例类型）
- A/B 测试场景（挑战者与当前版本）

每个部署都作为独立实体进行追踪，拥有自己的元数据。

### 临时性部署

某些平台会创建临时的或短生命周期的部署（例如用于批量推理作业）。这些部署生命周期虽短，但仍然值得追踪，原因包括：

- 成本归集
- 合规与审计留痕
- 了解模型使用模式
- 调试与排障

### 平台特定的部署概念

不同 ML 平台的部署概念各有差异：

- **SageMaker Endpoints**：实时推理端点，可包含一个或多个模型变体
- **Azure ML Online Endpoints**：托管端点，支持蓝绿部署
- **Vertex AI Endpoints**：已部署的模型，具备流量切分能力
- **Kubernetes Inference Services**：基于 Pod 的模型服务，支持自动扩缩容

DataHub 的部署模型抽象了这些平台差异，同时在自定义属性中保留重要的平台特定细节。

## 相关实体

ML 模型部署经常与以下其他 DataHub 实体交互：

- **MLModel**：被部署的底层已训练模型
- **MLModelGroup**：一组可能共享部署基础设施的相关模型
- **DataPlatform**：承载部署的平台（SageMaker、Azure ML 等）
- **Container**：包含该部署的工作区、命名空间或项目
- **CorpUser / CorpGroup**：部署的负责人与运维人员
- **Tag**：分类与组织标签
- **DataPlatformInstance**：部署平台的具体实例

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](21-mlmodeldeployment.md)。。
