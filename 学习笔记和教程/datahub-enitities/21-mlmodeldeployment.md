---
title: ML 模型部署
entity: mlmodeldeployment
order: 21
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlmodeldeployment.md
---

# ML 模型部署

ML 模型部署表示已部署的机器学习模型实例，它们运行在生产或其他环境中。它们跟踪 ML 模型的运维层面，包括部署状态、平台、配置和生命周期。模型部署与 ML 模型本身是不同的——ML 模型代表训练产出的制品，而部署代表该模型在特定环境中提供预测服务的具体实例。

## 标识

ML 模型部署由三部分信息唯一确定：

- **部署所在的平台**：承载该模型的具体部署或服务平台。例如 `sagemaker`、`azureml`、`vertexai`、`mlflow`、`seldon`、`kserve` 等。这对应一个数据平台 URN。
- **部署的名称**：每个平台都有自己的部署命名方式。例如 SageMaker 使用 endpoint 名称，而 Azure ML 使用工作区内的部署名称。
- **环境或来源**：该限定符表示部署运行所在的环境（PROD、DEV、TEST 等），类似于数据集所使用的 fabric 概念。

一个 ML 模型部署标识符的示例为 `urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,recommendation-endpoint,PROD)`。

## 重要能力

### 部署属性

关于部署的核心元数据存储在 `mlModelDeploymentProperties` 方面中，其中包括：

- **Description**：说明部署用途与配置的文档
- **Deployment Status**：部署当前的运行状态，可取以下值：
  - `IN_SERVICE`：正在提供预测服务的活跃部署
  - `OUT_OF_SERVICE`：当前不承载流量的部署
  - `CREATING`：正在置备的部署
  - `UPDATING`：正在使用新配置更新的部署
  - `ROLLING_BACK`：正在回滚到先前版本的部署
  - `DELETING`：正在被移除的部署
  - `FAILED`：处于错误状态的部署
  - `UNKNOWN`：状态未映射或未知的部署
- **Version**：部署配置的版本
- **Created At**：表示部署创建时间的时间戳
- **Custom Properties**：额外的平台特定配置细节
- **External URL**：在其原生平台中查看该部署的链接

下面的代码片段展示了如何创建 ML 模型部署。


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

ML 模型部署通过 `mlModelProperties.deployments` 字段与其底层 ML 模型相连。该关系带来以下能力：

- **部署追踪**：了解模型部署在哪里以及如何部署
- **版本管理**：跟踪每个环境中部署的是哪个模型版本
- **影响分析**：了解模型在生产环境的影响范围
- **回滚规划**：在模型出现问题时识别活跃的部署


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

ML 模型部署可以使用 `globalTags` 方面附加标签。标签有助于：

- 按用途对部署分类（生产、金丝雀、影子）
- 跟踪成本中心或团队
- 标记需要合规或安全审查的部署
- 按模型类型或使用场景组织部署

### 所有权

部署的所有权通过 `ownership` 方面关联。所有者可以是技术负责人（ML 工程师、MLOps 团队），也可以是对该部署负责的业务负责人（产品经理、数据科学家）。所有权有助于：

- 明确对部署健康状况与性能的负责关系
- 提供事件发生时的联系人信息
- 访问控制与权限管理
- 组织治理


**Python SDK：为部署添加所有者**

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

`dataPlatformInstance` 方面提供有关部署平台具体实例的额外上下文。当组织拥有同一平台的多个实例时（例如多个 SageMaker 账户、不同的 Azure ML 工作区、彼此独立的 Kubernetes 集群），这一点尤为重要。

### 弃用与生命周期管理

当部署计划下线时，可以使用 `deprecation` 方面将其标记为已弃用，其中包括：

- **弃用标记**：将部署标记为已弃用
- **下线时间**：计划移除该部署的日期
- **弃用说明**：关于为何弃用该部署以及由何替代的信息
- **替代者**：指向应当改用的新部署的引用

当部署已被下线但希望保留历史元数据时，也可以使用 `status` 方面软删除部署（标记为已移除）。

### 组织上下文

#### 容器

部署可以使用 `container` 方面归属于某个父容器（例如 ML 工作区、命名空间或项目），从而形成层级结构：

```
ML Workspace (Container)
├── Model Deployment 1
├── Model Deployment 2
└── Model Deployment 3
```

这种层级结构有助于：

- 按项目或团队组织部署
- 在工作区级别管理访问控制
- 了解资源利用率与成本
- 浏览相关部署

## 与外部系统的集成

### 从 ML 平台采集

ML 模型部署通常通过 DataHub 的采集连接器从 ML 平台自动采集：

- **SageMaker**：采集 endpoint 部署及其配置与状态
- **Azure ML**：从工作区采集模型部署
- **Vertex AI**：从 Google Cloud 采集 endpoint 部署
- **MLflow**：采集已注册的模型部署
- **Seldon Core / KServe**：从 Kubernetes 采集推理服务

每个连接器都会将平台特定的部署元数据映射到 DataHub 标准化的部署模型。

### 查询部署信息

你可以使用 DataHub 的 REST API 获取部署信息：


**获取部署实体快照**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AmlModelDeployment%3A(urn%3Ali%3AdataPlatform%3Asagemaker,recommendation-endpoint,PROD)'
```

响应包含该部署的所有方面，其中包括：

- 部署属性（状态、版本、描述）
- 所有权信息
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

这将返回被部署到指定部署上的 ML 模型。



## 值得注意的例外

### 部署与模型的区别

理解 ML 模型与 ML 模型部署之间的区别非常重要：

- **ML Model**：代表训练得到的模型制品，包含训练数据、指标、超参数和模型元数据。一个模型可以有多个版本，也可以独立于任何部署而存在。

- **ML Model Deployment**：代表一个正在运行并提供预测的模型实例。部署引用特定的模型版本，并包含状态、配置、服务平台等运维元数据。

这种划分带来以下能力：

- 跟踪同一模型部署到多个环境（dev、staging、prod）
- 了解部署历史与回滚情况
- 将运维生命周期与模型开发分开管理
- 支持对同一模型进行 A/B 测试和金丝雀发布

### 一个模型对应多个部署

单个 ML 模型可以同时拥有多个部署：

- 不同环境（生产、预发布、开发）
- 不同区域（美国、欧洲、亚洲）
- 不同配置（批处理与实时、不同实例类型）
- A/B 测试场景（挑战者与现役版本）

每个部署都作为独立实体进行跟踪，拥有各自的元数据。

### 临时部署

某些平台会创建临时或短生命周期的部署（例如用于批量推理作业）。这些部署存在时间可能很短，但仍然值得跟踪，用于：

- 成本归集
- 合规与审计留痕
- 了解模型使用模式
- 调试与排障

### 平台特定的部署概念

不同 ML 平台的概念各异，它们到部署的映射方式如下：

- **SageMaker Endpoints**：包含一个或多个模型变体的实时推理 endpoint
- **Azure ML Online Endpoints**：支持蓝绿部署的托管 endpoint
- **Vertex AI Endpoints**：具备流量拆分能力的已部署模型
- **Kubernetes Inference Services**：基于 Pod 的模型服务，支持自动扩缩容

DataHub 的部署模型对这些平台差异进行了抽象，同时在自定义属性中保留了重要的平台特定细节。

## 相关实体

ML 模型部署经常与以下其他 DataHub 实体交互：

- **MLModel**：被部署的底层训练模型
- **MLModelGroup**：一组可能共享部署基础设施的相关模型
- **DataPlatform**：承载部署的平台（SageMaker、Azure ML 等）
- **Container**：包含该部署的工作区、命名空间或项目
- **CorpUser / CorpGroup**：部署的所有者与运维人员
- **Tag**：分类与组织标签
- **DataPlatformInstance**：部署平台的具体实例


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](21-mlmodeldeployment.md)。
