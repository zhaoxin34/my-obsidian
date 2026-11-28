---
title: 机器学习模型
entity: mlmodel
order: 19
source: https://docs.datahub.com/docs/generated/metamodel/entities/mlmodel.md
---

# 机器学习模型（ML Model）

ML Model（机器学习模型）实体表示在各类机器学习平台与框架上训练出来的模型。ML 模型可以使用不同的算法与框架进行训练（TensorFlow、PyTorch、Scikit-learn 等），并部署到各类平台（MLflow、SageMaker、Vertex AI 等）。

## 标识

ML 模型由三部分信息唯一标识：

- 模型注册或部署所在的平台：即承载或管理该模型的具体 ML 平台。例如 `mlflow`、`sagemaker`、`vertexai`、`databricks` 等。更多细节参见 [dataplatform](56-dataplatform.md)。
- 模型名称：即模型在平台内部的唯一标识。命名规范因平台而异：
  - MLflow：通常使用注册模型名（例如 `recommendation-model`）
  - SageMaker：使用模型名或模型包组名（例如 `product-recommendation-v1`）
  - Vertex AI：使用模型资源名（例如 `projects/123/locations/us-central1/models/456`）
- 模型训练所处的环境或来源：这与数据集的 fabric 概念类似，便于区分不同环境（PROD、DEV、QA 等）中的模型。支持的完整环境列表见 [FabricType.pdl](https://raw.githubusercontent.com/datahub-project/datahub/master/li-utils/src/main/pegasus/com/linkedin/common/FabricType.pdl)。。

ML 模型标识符示例：`urn:li:mlModel:(urn:li:dataPlatform:mlflow,my-recommendation-model,PROD)`。

## 重要能力

### 基本模型信息

ML 模型的核心信息记录在 `mlModelProperties` 方面（aspect）中，包括：

- **名称与描述**：模型用途的可读名称与描述
- **模型类型**：所使用的算法或架构（例如 "Convolutional Neural Network"、"Random Forest"、"BERT"）
- **版本**：通过 `versionProperties` 方面记录的版本信息
- **时间戳**：创建时间与最后修改时间
- **自定义属性**：用于平台特定元数据（例如框架版本、模型格式）的灵活键值对

下面的代码片段展示了如何创建一个基本的 ML 模型：


**Python SDK：创建 ML 模型**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_create.py
from datahub.metadata.urns import MlModelGroupUrn
from datahub.sdk import DataHubClient
from datahub.sdk.mlmodel import MLModel

client = DataHubClient.from_env()

mlmodel = MLModel(
    id="customer-churn-predictor",
    name="Customer Churn Prediction Model",
    platform="mlflow",
    description="A gradient boosting model that predicts customer churn based on usage patterns and engagement metrics",
    custom_properties={
        "framework": "xgboost",
        "framework_version": "1.7.0",
        "model_format": "pickle",
    },
    model_group=MlModelGroupUrn(platform="mlflow", name="customer-churn-models"),
)

client.entities.upsert(mlmodel)

```

### 超参数与指标

ML 模型既可以记录训练过程中使用的超参数，也可以记录来自训练与生产环境的各类指标：

- **超参数**：控制训练过程的配置值（学习率、批大小、epoch 数等）
- **训练指标**：来自训练过程的性能指标（准确率、损失、F1 分数等）
- **在线指标**：来自生产部署的性能指标（延迟、吞吐量、漂移等）

这些以结构化的参数与指标列表形式存储在 `mlModelProperties` 方面中。


**Python SDK：为 ML 模型添加超参数与指标**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_add_metadata.py
from datahub.metadata.urns import CorpUserUrn, DomainUrn, MlModelUrn, TagUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

mlmodel = client.entities.get(
    MlModelUrn(platform="mlflow", name="customer-churn-predictor")
)

mlmodel.set_hyper_params(
    {
        "learning_rate": "0.1",
        "max_depth": "6",
        "n_estimators": "100",
        "subsample": "0.8",
        "colsample_bytree": "0.8",
    }
)

mlmodel.set_training_metrics(
    {
        "accuracy": "0.87",
        "precision": "0.84",
        "recall": "0.82",
        "f1_score": "0.83",
        "auc_roc": "0.91",
    }
)

mlmodel.add_owner(CorpUserUrn("data_science_team"))

mlmodel.add_tag(TagUrn("production"))
mlmodel.add_tag(TagUrn("classification"))

mlmodel.set_domain(DomainUrn("urn:li:domain:customer-analytics"))

client.entities.update(mlmodel)

```

### 预期用途与伦理考量

DataHub 遵循 ML 模型卡（model card）最佳实践，支持完整的模型文档化。这些方面帮助相关方理解模型的适用场景以及使用模型的伦理影响：

- **预期用途**（`intendedUse` 方面）：记录主要使用场景、目标用户以及不适用（超出范围）的应用
- **伦理考量**（`mlModelEthicalConsiderations` 方面）：记录敏感数据的使用、风险与危害、缓解策略
- **注意事项与建议**（`mlModelCaveatsAndRecommendations` 方面）：补充注意事项、理想的数据集特征以及使用建议

这些方面与负责任 AI 实践相契合，有助于确保模型被恰当地使用。

### 训练与评估数据

ML 模型可以通过两种互补方式记录其训练与评估数据集：

#### 直接的数据集引用

- **训练数据**（`mlModelTrainingData` 方面）：用于训练模型的数据集，包含预处理信息与选择该数据集的原因
- **评估数据**（`mlModelEvaluationData` 方面）：用于模型评估与测试的数据集

每个数据集引用包含数据集 URN、使用该数据集的原因，以及所应用的预处理步骤。这会在模型与其训练数据之间建立直接的血缘关系。

#### 通过训练运行（Training Run）建立血缘

训练运行（`dataProcessInstance` 实体）提供了另一种通常更为详细的方式来捕获训练血缘：

- 训练运行通过 `dataProcessInstanceInput` 方面声明其输入数据集
- 训练运行通过 `dataProcessInstanceOutput` 方面声明其输出数据集
- 模型通过 `trainingJobs` 字段引用训练运行

这会形成间接血缘：`数据集 → 训练运行 → 模型`

**两种方式各自的适用场景：**

- 使用**直接数据集引用**来简单记录使用了哪些数据
- 使用**训练运行**来进行完整的血缘跟踪，包括：
  - 多个训练/验证/测试数据集
  - 训练过程中的指标与超参数
  - 时间维度的追踪（训练发生的时间）
  - 与实验的关联，以便比较多次训练尝试

大多数生产级 ML 系统都应使用训练运行来进行完整的血缘跟踪。

### 因子提示与定量分析

用于详细的模型分析与性能报告：

- **因子提示**（`mlModelFactorPrompts` 方面）：可能影响模型性能的因素（人口群体、环境条件等）
- **定量分析**（`mlModelQuantitativeAnalyses` 方面）：指向仪表板或报告的链接，展示按不同因子拆分的性能指标
- **指标**（`mlModelMetrics` 方面）：比简单的训练/在线指标更详细的指标，并带有描述

### 源代码与成本

- **源代码**（`sourceCode` 方面）：指向模型训练代码、notebook 或代码仓库（GitHub、GitLab 等）的链接
- **成本**（`cost` 方面）：成本归集信息，用于跟踪模型训练与推理开销

### 训练运行与实验

在 DataHub 中，ML 模型可以与其训练运行和实验关联，从而提供从原始数据、经由训练、到已部署模型的完整血缘。

#### 训练运行

训练运行表示模型训练作业的某一次具体执行。在 DataHub 中，训练运行被建模为带特定子类型的 `dataProcessInstance` 实体：

- **实体类型**：`dataProcessInstance`
- **子类型**：`MLAssetSubTypes.MLFLOW_TRAINING_RUN`
- **关键方面**：
  - `dataProcessInstanceProperties`：名称、时间戳、自定义属性等基本属性
  - `mlTrainingRunProperties`：ML 专属属性，包括：
    - 训练指标（准确率、损失、F1 分数等）
    - 超参数（学习率、批大小、epoch 数等）
    - 输出 URL（模型产物、检查点）
    - 外部 URL（指向训练仪表板的链接）
  - `dataProcessInstanceInput`：用于训练的输入数据集
  - `dataProcessInstanceOutput`：输出数据集（预测结果、特征重要性等）
  - `dataProcessInstanceRunEvent`：开始、完成与失败事件

训练运行会创建如下血缘关系：

- **上游**：训练时使用了哪些数据集
- **下游**：该训练运行产出了哪些模型

模型通过 `mlModelProperties` 中的 `trainingJobs` 字段引用其训练运行；模型组也可以引用训练运行，以追踪某一模型族的全部训练活动。

#### 实验

实验将相关的训练运行组织成逻辑分组，通常代表一系列优化某个模型或比较不同方案的尝试。在 DataHub 中，实验被建模为 `container` 实体：

- **实体类型**：`container`
- **子类型**：`MLAssetSubTypes.MLFLOW_EXPERIMENT`
- **用途**：将相关训练运行分组，便于组织与比较

训练运行通过 `container` 方面归属于实验，从而形成如下层级结构：

```
Experiment: "Customer Churn Prediction"
├── Training Run 1: baseline model
├── Training Run 2: with feature engineering
├── Training Run 3: hyperparameter tuning
└── Training Run 4: final production model
```

这种结构与常见 ML 平台的模式（如 MLflow 的 experiment/run 层级）相一致，并带来以下能力：

- 比较多次训练尝试的指标
- 追踪模型在迭代过程中的演进
- 了解尝试过哪些方案及其结果
- 按项目或目标组织训练工作


**Python SDK：创建训练运行与实验**

```python
# Inlined from /metadata-ingestion/examples/ai/dh_ai_docs_demo.py
import argparse
from datetime import datetime

from dh_ai_client import DatahubAIClient

from datahub.emitter.mcp_builder import (
    ContainerKey,
)
from datahub.ingestion.source.common.subtypes import MLAssetSubTypes
from datahub.metadata.com.linkedin.pegasus2avro.dataprocess import RunResultType
from datahub.metadata.schema_classes import (
    AuditStampClass,
    DataProcessInstancePropertiesClass,
    MLHyperParamClass,
    MLMetricClass,
    MLTrainingRunPropertiesClass,
)
from datahub.metadata.urns import (
    CorpUserUrn,
    DataProcessInstanceUrn,
    GlossaryTermUrn,
    TagUrn,
)
from datahub.sdk.container import Container
from datahub.sdk.dataset import Dataset
from datahub.sdk.mlmodel import MLModel
from datahub.sdk.mlmodelgroup import MLModelGroup

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=False, help="DataHub access token")
parser.add_argument(
    "--server_url",
    required=False,
    default="http://localhost:8080",
    help="DataHub server URL (defaults to http://localhost:8080)",
)
args = parser.parse_args()

# Initialize client
client = DatahubAIClient(token=args.token, server_url=args.server_url)

# Use a unique prefix for all IDs to avoid conflicts
prefix = "test"

# Define all entity IDs upfront
# Basic entity IDs
basic_model_group_id = f"{prefix}_basic_group"
basic_model_id = f"{prefix}_basic_model"
basic_experiment_id = f"{prefix}_basic_experiment"
basic_run_id = f"{prefix}_basic_run"
basic_dataset_id = f"{prefix}_basic_dataset"

# Advanced entity IDs
advanced_model_group_id = f"{prefix}_airline_forecast_models_group"
advanced_model_id = f"{prefix}_arima_model"
advanced_experiment_id = f"{prefix}_airline_forecast_experiment"
advanced_run_id = f"{prefix}_simple_training_run"
advanced_input_dataset_id = f"{prefix}_iris_input"
advanced_output_dataset_id = f"{prefix}_iris_output"

# Display names with prefix
basic_model_group_name = f"{prefix} Basic Group"
basic_model_name = f"{prefix} Basic Model"
basic_experiment_name = f"{prefix} Basic Experiment"
basic_run_name = f"{prefix} Basic Run"
basic_dataset_name = f"{prefix} Basic Dataset"

advanced_model_group_name = f"{prefix} Airline Forecast Models Group"
advanced_model_name = f"{prefix} ARIMA Model"
advanced_experiment_name = f"{prefix} Airline Forecast Experiment"
advanced_run_name = f"{prefix} Simple Training Run"
advanced_input_dataset_name = f"{prefix} Iris Training Input Data"
advanced_output_dataset_name = f"{prefix} Iris Model Output Data"


def create_basic_model_group():
    """Create a basic model group."""
    print("Creating basic model group...")
    basic_model_group = MLModelGroup(
        id=basic_model_group_id,
        platform="mlflow",
        name=basic_model_group_name,
    )
    client._emit_mcps(basic_model_group.as_mcps())
    return basic_model_group


def create_advanced_model_group():
    """Create an advanced model group."""
    print("Creating advanced model group...")
    advanced_model_group = MLModelGroup(
        id=advanced_model_group_id,
        platform="mlflow",
        name=advanced_model_group_name,
        description="Group of models for airline passenger forecasting",
        created=datetime.now(),
        last_modified=datetime.now(),
        owners=[CorpUserUrn("urn:li:corpuser:datahub")],
        external_url="https://www.linkedin.com/in/datahub",
        tags=["urn:li:tag:forecasting", "urn:li:tag:arima"],
        terms=["urn:li:glossaryTerm:forecasting"],
        custom_properties={"team": "forecasting"},
    )
    client._emit_mcps(advanced_model_group.as_mcps())
    return advanced_model_group


def create_basic_model():
    """Create a basic model."""
    print("Creating basic model...")
    basic_model = MLModel(
        id=basic_model_id,
        platform="mlflow",
        name=basic_model_name,
    )
    client._emit_mcps(basic_model.as_mcps())
    return basic_model


def create_advanced_model():
    """Create an advanced model."""
    print("Creating advanced model...")
    advanced_model = MLModel(
        id=advanced_model_id,
        platform="mlflow",
        name=advanced_model_name,
        description="ARIMA model for airline passenger forecasting",
        created=datetime.now(),
        last_modified=datetime.now(),
        owners=[CorpUserUrn("urn:li:corpuser:datahub")],
        external_url="https://www.linkedin.com/in/datahub",
        tags=["urn:li:tag:forecasting", "urn:li:tag:arima"],
        terms=["urn:li:glossaryTerm:forecasting"],
        custom_properties={"team": "forecasting"},
        version="1",
        aliases=["champion"],
        hyper_params={"learning_rate": "0.01"},
        training_metrics={"accuracy": "0.9"},
    )
    client._emit_mcps(advanced_model.as_mcps())
    return advanced_model


def create_basic_experiment():
    """Create a basic experiment."""
    print("Creating basic experiment...")
    basic_experiment = Container(
        container_key=ContainerKey(platform="mlflow", name=basic_experiment_id),
        display_name=basic_experiment_name,
    )
    client._emit_mcps(basic_experiment.as_mcps())
    return basic_experiment


def create_advanced_experiment():
    """Create an advanced experiment."""
    print("Creating advanced experiment...")
    advanced_experiment = Container(
        container_key=ContainerKey(platform="mlflow", name=advanced_experiment_id),
        display_name=advanced_experiment_name,
        description="Experiment to forecast airline passenger numbers",
        extra_properties={"team": "forecasting"},
        created=datetime(2025, 4, 9, 22, 30),
        last_modified=datetime(2025, 4, 9, 22, 30),
        subtype=MLAssetSubTypes.MLFLOW_EXPERIMENT,
    )
    client._emit_mcps(advanced_experiment.as_mcps())
    return advanced_experiment


def create_basic_training_run():
    """Create a basic training run."""
    print("Creating basic training run...")
    basic_run_urn = client.create_training_run(
        run_id=basic_run_id,
        run_name=basic_run_name,
    )
    return basic_run_urn


def create_advanced_training_run():
    """Create an advanced training run."""
    print("Creating advanced training run...")
    advanced_run_urn = client.create_training_run(
        run_id=advanced_run_id,
        properties=DataProcessInstancePropertiesClass(
            name=advanced_run_name,
            created=AuditStampClass(
                time=1628580000000, actor="urn:li:corpuser:datahub"
            ),
            customProperties={"team": "forecasting"},
        ),
        training_run_properties=MLTrainingRunPropertiesClass(
            id=advanced_run_id,
            outputUrls=["s3://my-bucket/output"],
            trainingMetrics=[MLMetricClass(name="accuracy", value="0.9")],
            hyperParams=[MLHyperParamClass(name="learning_rate", value="0.01")],
            externalUrl="https:localhost:5000",
        ),
        run_result=RunResultType.FAILURE,
        start_timestamp=1628580000000,
        end_timestamp=1628580001000,
    )
    return advanced_run_urn


def create_basic_dataset():
    """Create a basic dataset."""
    print("Creating basic dataset...")
    basic_input_dataset = Dataset(
        platform="snowflake",
        name=basic_dataset_id,
        display_name=basic_dataset_name,
    )
    client._emit_mcps(basic_input_dataset.as_mcps())
    return basic_input_dataset


def create_advanced_datasets():
    """Create advanced datasets."""
    print("Creating advanced datasets...")
    advanced_input_dataset = Dataset(
        platform="snowflake",
        name=advanced_input_dataset_id,
        description="Raw Iris dataset used for training ML models",
        schema=[("id", "number"), ("name", "string"), ("species", "string")],
        display_name=advanced_input_dataset_name,
        tags=["urn:li:tag:ml_data", "urn:li:tag:iris"],
        terms=["urn:li:glossaryTerm:raw_data"],
        owners=[CorpUserUrn("urn:li:corpuser:datahub")],
        custom_properties={
            "data_source": "UCI Repository",
            "records": "150",
            "features": "4",
        },
    )
    client._emit_mcps(advanced_input_dataset.as_mcps())

    advanced_output_dataset = Dataset(
        platform="snowflake",
        name=advanced_output_dataset_id,
        description="Processed Iris dataset with model predictions",
        schema=[("id", "number"), ("name", "string"), ("species", "string")],
        display_name=advanced_output_dataset_name,
        tags=["urn:li:tag:ml_data", "urn:li:tag:predictions"],
        terms=["urn:li:glossaryTerm:model_output"],
        owners=[CorpUserUrn("urn:li:corpuser:datahub")],
        custom_properties={
            "model_version": "1.0",
            "records": "150",
            "accuracy": "0.95",
        },
    )
    client._emit_mcps(advanced_output_dataset.as_mcps())
    return advanced_input_dataset, advanced_output_dataset


# Split relationship functions into individual top-level functions
def add_model_to_model_group(model, model_group):
    """Add model to model group relationship."""
    print("Adding model to model group...")
    model.set_model_group(model_group.urn)
    client._emit_mcps(model.as_mcps())


def add_run_to_experiment(run_urn, experiment):
    """Add run to experiment relationship."""
    print("Adding run to experiment...")
    client.add_run_to_experiment(run_urn=run_urn, experiment_urn=str(experiment.urn))


def add_run_to_model(model, run_id):
    """Add run to model relationship."""
    print("Adding run to model...")
    model.add_training_job(DataProcessInstanceUrn(run_id))
    client._emit_mcps(model.as_mcps())


def add_run_to_model_group(model_group, run_id):
    """Add run to model group relationship."""
    print("Adding run to model group...")
    model_group.add_training_job(DataProcessInstanceUrn(run_id))
    client._emit_mcps(model_group.as_mcps())


def add_input_dataset_to_run(run_urn, input_dataset):
    """Add input dataset to run relationship."""
    print("Adding input dataset to run...")
    client.add_input_datasets_to_run(
        run_urn=run_urn, dataset_urns=[str(input_dataset.urn)]
    )


def add_output_dataset_to_run(run_urn, output_dataset):
    """Add output dataset to run relationship."""
    print("Adding output dataset to run...")
    client.add_output_datasets_to_run(
        run_urn=run_urn, dataset_urns=[str(output_dataset.urn)]
    )


def update_model_properties(model):
    """Update model properties."""
    print("Updating model properties...")

    # Update model version
    model.set_version("2")

    # Add tags and terms
    model.add_tag(TagUrn("marketing"))
    model.add_term(GlossaryTermUrn("marketing"))

    # Add version alias
    model.add_version_alias("challenger")

    # Save the changes
    client._emit_mcps(model.as_mcps())


def update_model_group_properties(model_group):
    """Update model group properties."""
    print("Updating model group properties...")

    # Update description
    model_group.set_description("Updated description for airline forecast models")

    # Add tags and terms
    model_group.add_tag(TagUrn("production"))
    model_group.add_term(GlossaryTermUrn("time-series"))

    # Update custom properties
    model_group.set_custom_properties(
        {"team": "forecasting", "business_unit": "operations", "status": "active"}
    )

    # Save the changes
    client._emit_mcps(model_group.as_mcps())


def update_experiment_properties():
    """Update experiment properties."""
    print("Updating experiment properties...")

    # Create a container object for the existing experiment
    existing_experiment = Container(
        container_key=ContainerKey(platform="mlflow", name=advanced_experiment_id),
        display_name=advanced_experiment_name,
    )

    # Update properties
    existing_experiment.set_description(
        "Updated experiment for forecasting passenger numbers"
    )
    existing_experiment.add_tag(TagUrn("time-series"))
    existing_experiment.add_term(GlossaryTermUrn("forecasting"))
    existing_experiment.set_custom_properties(
        {"team": "forecasting", "priority": "high", "status": "active"}
    )

    # Save the changes
    client._emit_mcps(existing_experiment.as_mcps())


def main():
    # Parse arguments
    print("Creating AI assets...")

    # Comment in/out the functions you want to run
    # Create basic entities
    create_basic_model_group()
    create_basic_model()
    create_basic_experiment()
    create_basic_training_run()
    create_basic_dataset()

    # Create advanced entities
    advanced_model_group = create_advanced_model_group()
    advanced_model = create_advanced_model()
    advanced_experiment = create_advanced_experiment()
    advanced_run_urn = create_advanced_training_run()
    advanced_input_dataset, advanced_output_dataset = create_advanced_datasets()

    # # Create relationships - each can be commented out independently
    add_model_to_model_group(advanced_model, advanced_model_group)
    add_run_to_experiment(advanced_run_urn, advanced_experiment)
    add_run_to_model(advanced_model, advanced_run_id)
    add_run_to_model_group(advanced_model_group, advanced_run_id)
    add_input_dataset_to_run(advanced_run_urn, advanced_input_dataset)
    add_output_dataset_to_run(advanced_run_urn, advanced_output_dataset)

    # # Update properties - each can be commented out independently
    update_model_properties(advanced_model)
    update_model_group_properties(advanced_model_group)
    update_experiment_properties()

    print("All done! AI entities created successfully.")


if __name__ == "__main__":
    main()

```

### 关系与血缘

ML 模型通过多个方面与字段支持丰富的关系建模：

#### 核心关系

- **模型组**（通过 `mlModelProperties` 中的 `groups` 字段）：模型可以属于 `mlModelGroup` 实体，形成 `MemberOf` 关系，从而将相关模型组织成逻辑族或集合。

- **训练运行**（通过 `mlModelProperties` 中的 `trainingJobs` 字段）：模型引用产出它的、带 `MLFLOW_TRAINING_RUN` 子类型的 `dataProcessInstance` 实体。这会创建上游血缘，展示：

  - 是哪个训练运行创建了该模型
  - 训练时使用了哪些数据集（通过训练运行的输入数据集）
  - 记录了哪些超参数与指标
  - 该训练运行属于哪个实验

- **特征**（通过 `mlModelProperties` 中的 `mlFeatures` 字段）：模型可以消费 `mlFeature` 实体，形成 `Consumes` 关系，从而记录：

  - 模型推理需要哪些特征
  - 训练期间使用的完整特征集合
  - 对特征存储或特征表的依赖

- **部署**（通过 `mlModelProperties` 中的 `deployments` 字段）：模型可以部署到 `mlModelDeployment` 实体，表示各环境（生产、预发等）中运行中的模型端点

- **训练数据集**（`mlModelTrainingData` 方面）：对训练所用数据集的直接引用，包含预处理信息与选择数据集的原因

- **评估数据集**（`mlModelEvaluationData` 方面）：对模型评估与测试所用数据集的引用

#### 血缘图结构

这些关系构成了一张完整的血缘图：

```
Training Datasets → Training Run → ML Model → ML Model Deployment
                         ↓
                    Experiment

Feature Tables → ML Features → ML Model

ML Model Group ← ML Model
```

这使得如下强大查询成为可能：

- "展示所有影响该模型预测的数据集"
- "如果这个数据集的 schema 发生变化，哪些模型会受到影响？"
- "创建该模型各版本的训练运行的完整历史是什么？"
- "哪些生产端点正在提供该模型的服务？"


**Python SDK：更新模型专属方面**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_update_aspects.py
import datahub.metadata.schema_classes as models
from datahub.metadata.urns import DatasetUrn, MlModelUrn
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()

model_urn = MlModelUrn(platform="mlflow", name="customer-churn-predictor")

mlmodel = client.entities.get(model_urn)

intended_use = models.IntendedUseClass(
    primaryUses=[
        "Predict customer churn to enable proactive retention campaigns",
        "Identify high-risk customers for targeted interventions",
    ],
    primaryUsers=[models.IntendedUserTypeClass.ENTERPRISE],
    outOfScopeUses=[
        "Not suitable for real-time predictions (batch inference only)",
        "Not trained on international markets outside North America",
    ],
)

mlmodel._set_aspect(intended_use)

training_data = models.TrainingDataClass(
    trainingData=[
        models.BaseDataClass(
            dataset=str(
                DatasetUrn(
                    platform="snowflake", name="prod.analytics.customer_features"
                )
            ),
            motivation="Historical customer data with confirmed churn labels",
            preProcessing=[
                "Removed customers with less than 30 days of history",
                "Standardized numerical features using StandardScaler",
                "One-hot encoded categorical variables",
            ],
        )
    ]
)

mlmodel._set_aspect(training_data)

source_code = models.SourceCodeClass(
    sourceCode=[
        models.SourceCodeUrlClass(
            type=models.SourceCodeUrlTypeClass.ML_MODEL_SOURCE_CODE,
            sourceCodeUrl="https://github.com/example/ml-models/tree/main/churn-predictor",
        )
    ]
)

mlmodel._set_aspect(source_code)

ethical_considerations = models.EthicalConsiderationsClass(
    data=["Model uses demographic data (age, location) which may be sensitive"],
    risksAndHarms=[
        "Predictions may disproportionately affect certain customer segments",
        "False positives could lead to unnecessary retention spending",
    ],
    mitigations=[
        "Regular bias audits conducted quarterly",
        "Human review required for high-value customer interventions",
    ],
)

mlmodel._set_aspect(ethical_considerations)

client.entities.update(mlmodel)

print(f"Updated aspects for model: {model_urn}")

```

### 标签、术语与归属

与其他 DataHub 实体一样，ML 模型支持：

- **标签**（`globalTags` 方面）：灵活的分类（例如 "pii-model"、"production-ready"、"experimental"）
- **术语表术语**（`glossaryTerms` 方面）：业务概念（例如 "Customer Churn"、"Fraud Detection"）
- **归属**（`ownership` 方面）：对模型负责的个人或团队（数据科学家、ML 工程师等）
- **域**（`domains` 方面）：组织分组（例如 "Recommendations"、"Risk Management"）

### 完整 ML 工作流示例

下面的示例演示了 DataHub 中完整的 ML 模型生命周期，展示了各部分如何协同工作：

```
1. Create Model Group
   ↓
2. Create Experiment (Container)
   ↓
3. Create Training Run (DataProcessInstance)
   ├── Link input datasets
   ├── Link output datasets
   └── Add metrics and hyperparameters
   ↓
4. Create Model
   ├── Set version and aliases
   ├── Link to model group
   ├── Link to training run
   ├── Add hyperparameters and metrics
   └── Add ownership and tags
   ↓
5. Link Training Run to Experiment
   ↓
6. Update Model properties as needed
   ├── Change version aliases (champion → challenger)
   ├── Add additional tags/terms
   └── Update metrics from production
```

该工作流创建了丰富的血缘，展示：

- 哪些数据集训练了该模型
- 涉及了哪些实验与训练运行
- 模型如何通过版本演进
- 哪个版本已部署（通过别名体现）
- 谁拥有并维护该模型


**完整 Python 示例：全流程 ML 工作流**

参见 `/metadata-ingestion/examples/ai/dh_ai_docs_demo.py` 中的综合示例，它演示了：

- 创建带元数据的模型组
- 创建实验以组织训练运行
- 创建带指标、超参数与数据集血缘的训练运行
- 创建带版本与别名的模型
- 将所有实体相互关联，形成完整血缘
- 更新属性并管理模型生命周期

该示例既展示了入门用的基础模式，也展示了生产级 ML 系统的高级模式。



## 代码示例

### 查询 ML 模型信息

可以使用 Python SDK 获取 ML Model 实体及其各方面：


**Python SDK：查询 ML 模型**

```python
# Inlined from /metadata-ingestion/examples/library/mlmodel_query_rest_api.py
from datahub.ingestion.graph.client import get_default_graph
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    IntendedUseClass,
    MLModelPropertiesClass,
    OwnershipClass,
)
from datahub.metadata.urns import MlModelUrn

graph = get_default_graph()

model_urn = MlModelUrn(platform="mlflow", name="customer-churn-predictor", env="PROD")

print(f"Entity URN: {model_urn}")
print("\nAspects:")

props = graph.get_aspect(entity_urn=str(model_urn), aspect_type=MLModelPropertiesClass)
if props is None:
    raise SystemExit(f"ML model not found: {model_urn}")

print(f"  Name: {props.name}")
print(f"  Description: {props.description}")
print(f"  Type: {props.type}")

if props.hyperParams:
    print("\n  Hyperparameters:")
    for param in props.hyperParams:
        print(f"    - {param.name}: {param.value}")

if props.trainingMetrics:
    print("\n  Training Metrics:")
    for metric in props.trainingMetrics:
        print(f"    - {metric.name}: {metric.value}")

tags = graph.get_aspect(entity_urn=str(model_urn), aspect_type=GlobalTagsClass)
if tags is not None:
    print(f"\n  Tags: {[tag.tag for tag in tags.tags]}")

ownership = graph.get_aspect(entity_urn=str(model_urn), aspect_type=OwnershipClass)
if ownership is not None:
    print(f"\n  Owners: {[owner.owner for owner in ownership.owners]}")

intended = graph.get_aspect(entity_urn=str(model_urn), aspect_type=IntendedUseClass)
if intended is not None:
    print(f"\n  Primary Uses: {intended.primaryUses}")
    print(f"  Out of Scope Uses: {intended.outOfScopeUses}")

```

## 集成点

### 相关实体

ML 模型与 DataHub 元数据模型中的其他多个实体集成：

- **mlModelGroup**：相关模型版本的逻辑分组（例如某个推荐模型的所有版本）
- **mlModelDeployment**：已部署模型的运行实例，包含状态、端点 URL 与部署元数据
- **mlFeature**：模型在推理时消费的单条特征
- **mlFeatureTable**：特征的集合，通常来自特征存储
- **dataset**：模型使用的训练与评估数据集
- **dataProcessInstance**（子类型为 `MLFLOW_TRAINING_RUN`）：创建模型版本的具体训练运行，包含指标、超参数以及到输入/输出数据集的血缘
- **container**（子类型为 `MLFLOW_EXPERIMENT`）：为某个模型或项目组织相关训练运行的实验
- **versionSet**：将一个模型的所有版本归组在一起，便于版本管理

### GraphQL 解析器

GraphQL API 通过 `datahub-graphql-core/src/main/java/com/linkedin/datahub/graphql/types/mlmodel/` 下的解析器为 ML 模型提供丰富的查询能力。这些解析器支持：

- 获取包含所有方面的模型详情
- 沿关系到特征、模型组与部署进行导航
- 按标签、术语、平台等条件搜索与过滤模型

### 事件（Incidents）

ML 模型参与共享的事件子系统。可以通过 `raiseIncident` GraphQL mutation（或 Python SDK）在模型上触发事件，通过 `MLModel` GraphQL 类型的 `incidents` 字段列出事件，模型还会携带一个汇总的 `incidentsSummary` 方面，随着事件的触发与解决自动维护。由于一个事件可以引用多个实体，因此单个事件可以在同一生命周期下同时关联上游数据集与受影响模型。

### 摄取源

多个摄取源会自动抽取 ML 模型元数据：

- **MLflow**：从 MLflow 跟踪服务器抽取注册模型、版本、指标、参数与血缘
- **SageMaker**：从 AWS SageMaker 摄取模型、模型包与端点
- **Vertex AI**：从 Google Cloud Vertex AI 抽取模型与端点
- **Databricks**：从 Databricks 工作区摄取 MLflow 模型
- **Unity Catalog**：抽取在 Unity Catalog 中注册的 ML 模型

这些源位于 `/metadata-ingestion/src/datahub/ingestion/source/`，会自动填充模型属性、关系与血缘。

## 值得注意的例外

### 模型版本管理

DataHub 中 ML 模型的版本管理使用 `versionProperties` 方面，它为跨生命周期的模型版本追踪提供了稳健的框架。这是生产级 ML 平台中展示的标准做法。

#### 版本属性方面

每个 ML 模型都应使用 `versionProperties` 方面，其中包括：

- **version**：包含版本标识符的 `VersionTagClass`（例如 "1"、"2"、"v1.0.0"）
- **versionSet**：将一个模型所有版本归组在一起的 URN（例如 `urn:li:versionSet:(mlModel,mlmodel_my-model_versions)`）
- **sortId**：用于对版本排序的字符串（通常是补零后的版本号）
- **aliases**：用于命名版本引用的可选 `VersionTagClass` 数组

#### 用于 A/B 测试的版本别名

版本别名支持灵活的模型生命周期管理与 A/B 测试流程。常见别名包括：

- **"champion"**：当前已部署的生产模型
- **"challenger"**：正在测试或评估的候选模型
- **"baseline"**：用于性能对比的参考模型
- **"latest"**：最近一次训练产出的版本

这些别名让你可以按角色而非具体版本号引用模型，从而实现顺畅的模型晋级流程：

```
Model v1 (alias: "champion")     # Currently in production
Model v2 (alias: "challenger")   # Being tested in canary deployment
Model v3 (alias: "latest")       # Just completed training
```

当 v2 被证明更优时，无需改动基础设施即可更新别名：

```
Model v1 (no alias)              # Retired
Model v2 (alias: "champion")     # Promoted to production
Model v3 (alias: "challenger")   # Now being tested
```

#### 模型组与版本管理

模型组（`mlModelGroup` 实体）作为组织相关模型的逻辑容器。虽然模型组可以包含同一模型的多个版本，但版本管理是通过各个模型上的 `versionProperties` 方面处理的，而非通过组结构本身。模型组适用于：

- 组织一个模型族的所有版本
- 对实验变体或解决同一问题的不同架构进行分组
- 管理多个相关模型共有的血缘与元数据

模型与模型组之间的关系通过 `mlModelProperties` 中的 `groups` 字段建立，形成 `MemberOf` 关系。

### 平台特定命名

不同 ML 平台有各自的命名约定：

- **MLflow**：使用两级层级（注册模型名 + 版本号）。在 DataHub 中，每个版本可以是独立实体，也可以在单个实体中跟踪各版本。
- **SageMaker**：有多个模型概念（模型、模型包、模型包组）。DataHub 可以将它们建模为独立实体，也可以合并处理。
- **Vertex AI**：使用完全限定资源名。应尽可能将其简化为便于阅读的名称。

从这些平台摄取数据时，连接器会处理平台特定的命名并转换为相应的 DataHub URN。

### 模型卡

各个方面（`intendedUse`、`mlModelFactorPrompts`、`mlModelEthicalConsiderations` 等）遵循 Model Cards for Model Reporting 框架（Mitchell 等，2019）。虽然这些方面是可选的，但对于生产模型强烈建议使用，以确保负责任的 AI 实践与透明的模型文档化。


> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](19-mlmodel.md)。。
