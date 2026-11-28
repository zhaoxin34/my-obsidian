---
title: 机器学习模型组
entity: mlmodelgroup
order: 20
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlmodelgroup.md
---

# 机器学习模型组

机器学习模型组（ML Model Groups）表示组织 ML 基础设施中一组相互关联的机器学习模型。它们是组织模型版本、实验变体或具有共同特征模型家族的逻辑容器。模型组对于管理 ML 模型的生命周期、追踪模型随时间的演进，以及按用途、架构或业务职能组织模型都至关重要。

## 身份

机器学习模型组由三部分信息标识：

- **Platform**：模型组所在的 ML 平台或工具。它表示承载该模型组的具体 ML 技术。例如 `mlflow`、`sagemaker`、`databricks`、`kubeflow`、`tensorflow`、`pytorch` 等。平台以类似 `urn:li:dataPlatform:mlflow` 的 URN 表示。

- **Name**：模型组在特定平台内的唯一名称。这通常是一个便于阅读的标识符，用于描述模型组的用途或模型家族。名称应具有意义并遵循你所在组织的命名约定。例如 `recommendation-models`、`fraud-detection-v2` 或 `customer-churn-prediction`。

- **Origin（Fabric）**：模型组所属或生成的环境。该限定符有助于区分不同环境中的模型，例如 Production（PROD）、Staging（QA）、Development（DEV）或 Testing 环境。支持的完整环境列表见 [FabricType.pdl](https://raw.githubusercontent.com/datahub-project/datahub/master/li-utils/src/main/pegasus/com/linkedin/common/FabricType.pdl)。

机器学习模型组标识符的一个示例是 `urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,recommendation-models,PROD)`。

## 重要能力

### 机器学习模型组属性

模型组属性存储在 `mlModelGroupProperties` aspect 中，包含模型组的核心元数据：

- **Name**：模型组的显示名称，可以比标识符更具描述性
- **Description**：关于模型组含义、用途及重要背景的详细文档
- **Version**：整个模型组的可选版本标签（区别于单个模型版本）
- **Created Timestamp**：关于模型组何时由谁创建的审计信息
- **Last Modified Timestamp**：模型组最后更新时间
- **Custom Properties**：可扩展的键值对，用于存储特定于你的组织或平台的额外元数据
- **External References**：指向外部系统或文档的链接（例如模型注册表 URL、实验跟踪系统）

以下是创建带属性的机器学习模型组的示例：

**Python SDK：创建机器学习模型组**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_create.py
from datahub.sdk import DataHubClient
from datahub.sdk.mlmodelgroup import MLModelGroup

client = DataHubClient.from_env()

mlmodel_group = MLModelGroup(
    id="my-recommendations-model-group",
    name="My Recommendations Model Group",
    platform="mlflow",
    description="Grouping of ml model related to home page recommendations",
    custom_properties={
        "framework": "pytorch",
    },
)

client.entities.upsert(mlmodel_group)
print(f"Created ML model group: {mlmodel_group.urn}")

```

### 血缘与训练信息

机器学习模型组从 `MLModelLineageInfo` 记录继承血缘能力，该记录捕获组内模型如何创建和使用的重要信息：

- **Training Jobs**：用于训练本组模型的数据任务或流程实例引用。这会创建显示模型来源的血缘关系。
- **Downstream Jobs**：消费或使用本组模型的数据任务或流程实例引用。这追踪模型如何部署和使用。

这些血缘关系在 DataHub 的血缘图中可见，有助于追踪 ML 模型从训练数据到部署的完整生命周期。

**Python SDK：向模型组添加训练血缘**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_lineage.py
from datahub.emitter import mce_builder
from datahub.metadata.urns import MlModelGroupUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

group_urn = MlModelGroupUrn(
    platform="mlflow",
    name="recommendation-models",
    env="PROD",
)

training_job_urn = mce_builder.make_data_job_urn(
    orchestrator="airflow",
    flow_id="train_recommendation_model",
    job_id="training_task",
)

group = client.entities.get(group_urn)

group.add_training_job(training_job_urn)

client.entities.update(group)

print(f"Added training job {training_job_urn} to ML model group {group_urn}")

```

### 所有权

与 DataHub 中其他实体一样，机器学习模型组可以使用 `ownership` aspect 分配所有者。模型组所有者通常负责：

- 管理哪些模型属于该组
- 维护模型组元数据与文档
- 监督模型质量与治理标准
- 作为模型相关问题的联系窗口
- 协调模型部署与监控

模型组的所有权类型与其他实体遵循相同的模式，包括 `TECHNICAL_OWNER`、`BUSINESS_OWNER`、`DATA_STEWARD`、`DATAOWNER`、`PRODUCER`、`DEVELOPER` 等。

**Python SDK：为模型组添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_owner.py
from datahub.sdk import CorpUserUrn, DataHubClient, MlModelGroupUrn

client = DataHubClient.from_env()

group = client.entities.get(
    MlModelGroupUrn(platform="mlflow", name="recommendation-models", env="PROD")
)

group.add_owner(CorpUserUrn("data_science_team"))

client.entities.update(group)

```

### 标签与术语表术语

机器学习模型组同时支持标签和术语表术语，用于分类与发现：

- **Tags**（通过 `globalTags` aspect）：用于快速分类的非正式标签。可用于 `experimental`、`production-ready`、`high-priority`、`computer-vision`、`nlp` 等属性。
- **Glossary Terms**（通过 `glossaryTerms` aspect）：提供标准化定义的正式业务词汇术语。可用于将模型组关联到业务概念。

**Python SDK：为模型组添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_tags.py
from datahub.metadata.urns import MlModelGroupUrn, TagUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

group = client.entities.get(
    MlModelGroupUrn(platform="mlflow", name="recommendation-models", env="PROD")
)
group.add_tag(TagUrn("production-ready"))

client.entities.update(group)

```

**Python SDK：为模型组添加术语表术语**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_terms.py
from datahub.metadata.urns import MlModelGroupUrn
from datahub.sdk import DataHubClient, GlossaryTermUrn

client = DataHubClient.from_env()

group_urn = MlModelGroupUrn(platform="mlflow", name="recommendation-models", env="PROD")

mlmodel_group = client.entities.get(group_urn)

mlmodel_group.add_term(GlossaryTermUrn("Recommendation"))

client.entities.update(mlmodel_group)

print(f"Added term {GlossaryTermUrn('Recommendation')} to ML model group {group_urn}")

```

### 文档与链接

模型组通过多个 aspect 支持文档：

- `mlModelGroupProperties` 中的 **Description**：描述模型组的主要文档字段
- **Institutional Memory**（通过 `institutionalMemory` aspect）：指向外部资源的链接，例如：
  - 描述模型组用途与架构的 Confluence 页面
  - 模型卡片与文档
  - 实验跟踪仪表板（MLflow、Weights & Biases 等）
  - 研究论文或技术规范
  - 团队 wiki 或运行手册

**Python SDK：为模型组添加文档链接**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_documentation.py
from datahub.sdk import DataHubClient
from datahub.sdk.mlmodelgroup import MLModelGroup

client = DataHubClient.from_env()

mlmodel_group = client.entities.get(
    MLModelGroup.get_urn_type()(
        platform="mlflow", name="recommendation-models", env="PROD"
    )
)

doc_url = "https://wiki.example.com/ml/recommendation-models"
doc_description = "Model architecture and training documentation"

mlmodel_group.add_link((doc_url, doc_description))

client.entities.update(mlmodel_group)

```

### 业务域

机器学习模型组可以使用 `domains` aspect 分配到业务域。这有助于按业务单元、部门或职能领域组织模型组。一个模型组在同一时间只能属于一个业务域。

**Python SDK：将模型组分配到业务域**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_add_domain.py
from datahub.metadata.urns import DomainUrn, MlModelGroupUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

mlmodel_group = client.entities.get(
    MlModelGroupUrn(platform="mlflow", name="recommendation-models", env="PROD")
)

# If you don't know the domain urn, you can look it up:
# domain_urn = client.resolve.domain(name="marketing")

# NOTE: This will overwrite the existing domain
mlmodel_group.set_domain(DomainUrn(id="marketing"))

client.entities.update(mlmodel_group)

```

### 废弃

当模型组不再积极维护或应当被替换时，可以使用 `deprecation` aspect 将其标记为已废弃。这有助于用户了解哪些模型家族仍在支持中。

**Python SDK：废弃一个模型组**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_deprecate.py
from datetime import datetime

import datahub.metadata.schema_classes as models
from datahub.sdk import DataHubClient, MlModelGroupUrn

client = DataHubClient.from_env()

group_urn = MlModelGroupUrn(
    platform="mlflow",
    name="legacy-recommendation-models",
    env="PROD",
)

mlmodel_group = client.entities.get(group_urn)

deprecation_aspect = models.DeprecationClass(
    deprecated=True,
    note="This model group has been replaced by the new transformer-based recommendation models",
    decommissionTime=int(datetime.now().timestamp() * 1000),
    actor="urn:li:corpuser:datahub",
)

mlmodel_group._set_aspect(deprecation_aspect)

client.entities.update(mlmodel_group)
print(f"Deprecated ML model group: {group_urn}")

```

### 结构化属性

模型组支持结构化属性，用于存储超越简单键值对的、类型化且经过 schema 校验的元数据。这对于围绕模型元数据强制执行组织标准很有用。

## 集成点

### 与机器学习模型的关系

机器学习模型组最主要的关系是与机器学习模型本身。模型可以通过 `mlModelProperties` aspect 中的 `groups` 字段关联到模型组，从而创建从模型到模型组的 `MemberOf` 关系。

将模型组织到组中的常见模式包括：

1. **基于版本的分组**：一个模型的所有版本（v1、v2、v3）属于同一组。注意，版本管理通过单个模型上的 `versionProperties` aspect 处理（其中包含版本号、versionSet URN 以及 "champion"、"challenger" 之类的别名），而模型组则充当组织容器。

2. **基于实验的分组**：模型的不同实验变体属于同一组

3. **基于架构的分组**：共享相同架构或方法的模型

4. **基于用途的分组**：服务于相同业务目的或用例的模型

**Python SDK：将模型添加到模型组**

```python
# Inlined from /metadata-ingestion/examples/library/mlgroup_add_to_mlmodel.py
from datahub.metadata.urns import MlModelGroupUrn
from datahub.sdk import DataHubClient
from datahub.sdk.mlmodel import MLModel

client = DataHubClient.from_env()

model = MLModel(
    id="my-recommendations-model",
    platform="mlflow",
)

model.set_model_group(
    MlModelGroupUrn(
        platform="mlflow",
        name="my-recommendations-model-group",
    )
)

client.entities.upsert(model)

```

### 与数据任务的关系

通过 `MLModelLineageInfo` 字段，模型组可以关联到：

- **Training Jobs**：生成组内模型的数据任务（上游血缘）
- **Downstream Jobs**：消费组内模型的数据任务（下游血缘）

这些关系支持从训练数据到模型部署的端到端血缘追踪。

### 与机器学习特征的关系

虽然机器学习模型组不直接引用机器学习特征，但组内的单个模型通常会消费机器学习特征。模型组充当模型与特征关系之上的一层组织结构。

### 与容器的关系

模型组可以使用 `container` aspect 在容器内组织。这对于表示如下层级结构很有用：

- ML 工作区 > 项目 > 模型组
- 注册中心 > 命名空间 > 模型组

### 查询模型组

你可以使用 REST API 和 Python SDK 查询模型组及其关联模型。

#### 通过 REST API 获取模型组信息

**REST API：按 URN 获取模型组**

```bash
curl 'http://localhost:8080/entities/urn%3Ali%3AmlModelGroup%3A(urn%3Ali%3AdataPlatform%3Amlflow,recommendation-models,PROD)' \
  -H 'Authorization: Bearer <token>'
```

这将返回包含所有 aspect 的模型组实体，其中包括：

- `mlModelGroupKey`：唯一标识符
- `mlModelGroupProperties`：名称、描述、版本、时间戳
- `ownership`：模型组的所有者
- `globalTags`：附加到该组的标签
- `glossaryTerms`：与该组关联的业务术语
- `domains`：业务域分配
- `institutionalMemory`：链接与文档

**Python SDK：读取模型组**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_group_read.py
from datahub.metadata.urns import MlModelGroupUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

# Or get this from the UI (share -> copy urn) and use MlModelGroupUrn.from_string(...)
mlmodel_group_urn = MlModelGroupUrn(
    platform="mlflow", name="my-recommendations-model-group"
)

mlmodel_group_entity = client.entities.get(mlmodel_group_urn)
print("Model Group Name: ", mlmodel_group_entity.name)
print("Model Group Description: ", mlmodel_group_entity.description)
print("Model Group Custom Properties: ", mlmodel_group_entity.custom_properties)

```

#### 查找模型组中的模型

要找出属于特定模型组的所有模型，可以查询关系。

**REST API：查找模型组中的所有模型**

```bash
curl 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3AmlModelGroup%3A(urn%3Ali%3AdataPlatform%3Amlflow,recommendation-models,PROD)&types=MemberOf' \
  -H 'Authorization: Bearer <token>'
```

这将返回作为指定模型组成员的全部机器学习模型实体。

## 与机器学习平台的集成

机器学习模型组可与主流 ML 平台无缝配合：

### MLflow

MLflow 的注册模型天然映射到 DataHub 模型组，模型版本则成为组内的单个 MLModel 实体。MLflow 摄取连接器会自动创建这些关系。

### SageMaker

Amazon SageMaker 的模型包与模型包组可以在 DataHub 中表示为模型组，从而提供跨 AWS 环境的统一视图。

### Databricks

在 Unity Catalog 中注册的 Databricks ML 模型可以组织到模型组中，以便更好地管理与治理。

### Kubeflow

Kubeflow 模型注册中心可以利用模型组按流水线或服务配置来组织模型。

### 自定义平台

任何自定义 ML 平台都可以使用模型组，只需在 URN 中指定适当的平台标识符即可。

## 值得注意的例外情况

### 模型组与单个模型

理解何时应使用模型组、何时应追踪单个模型很重要：

- **使用模型组的情形**：你有多个相互关联的模型版本或变体，应当归到一起组织。例如 "客户流失预测" 模型的所有版本。
- **使用单个模型的情形**：你有独立模型，它们没有多个版本，或不属于某个逻辑家族。

### 血缘继承

存储在模型组层级（通过 `trainingJobs` 与 `downstreamJobs`）的血缘信息表示组内所有模型共享的血缘。单个模型也可以在其 `mlModelProperties` aspect 中拥有自己特有的血缘信息。这两个层级的血缘是互补的：

- 模型组血缘：共享的训练流水线或共同的下游消费者
- 单个模型血缘：特定的训练运行或面向部署的消费者

### 命名注意事项

创建模型组时，请考虑你的命名策略：

- 名称应随时间保持稳定，因为它们是标识符的一部分
- 避免在组名中包含版本号（版本管理请使用单个模型名称）
- 使用清晰、具备描述性的名称来表明模型家族或用途
- 在组织内遵循一致的命名约定

### 平台实例支持

模型组通过 `dataPlatformInstance` aspect 支持平台实例。当你有同一平台的多个实例（例如多个 MLflow 注册中心）并需要区分其中的模型组时，这非常有用。

### 搜索与发现

模型组在 DataHub 中可按以下维度搜索：

- 名称（支持自动补全）
- 描述（全文搜索）
- 平台
- 来源/Fabric
- 标签与术语表术语
- 业务域
- 所有者

这使得通过 DataHub UI 或搜索 API 轻松发现相关模型组成为可能。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](20-mlmodelgroup.md)。
