---
title: 数据处理实例
entity: dataprocessinstance
order: 06
source: https://docs.datahub.com/docs/generated/metamodel/entities/dataprocessinstance.md
---

# DataProcessInstance

DataProcessInstance 表示数据管道或数据处理任务的一次具体执行过程。DataJob 和 DataFlow 实体定义了你数据管道的结构与逻辑，而 DataProcessInstance 则记录运行时行为，追踪每一次具体执行及其输入、输出、状态与时间信息。

可以这样理解：如果 DataJob 是一份菜谱，那么 DataProcessInstance 就是你某一次照着这份菜谱做菜的过程，记录了何时开始、用了哪些食材、做出了什么，以及最终是成功还是失败。

## 身份标识

DataProcessInstance 实体仅通过一个字段唯一标识：`id` 字符串。这使得其标识符结构比其他实体更简单，但在生成 ID 时需要仔细考虑。

URN 格式为：

```
urn:li:dataProcessInstance:<id>
```

`<id>` 字段必须在所有流程实例之间全局唯一，通常编码了编排器、执行上下文和运行标识等信息。Python SDK 提供了一个辅助方法，可由以下三个组成部分生成该 ID：

- **orchestrator**：执行该流程的平台（例如 `airflow`、`spark`、`dagster`）
- **cluster**：可选的环境标识（例如 `prod`、`dev`、`staging`）
- **id**：与具体执行相关的标识符（例如 DAG run ID、作业执行 ID）

URN 示例：

```
urn:li:dataProcessInstance:abc123def456...
```

实际的 ID 是由 orchestrator、cluster 和执行 id 确定性生成的 GUID：

```python
from datahub.api.entities.dataprocess.dataprocess_instance import DataProcessInstance

# The ID is automatically generated from these fields
instance = DataProcessInstance(
    id="scheduled__2024-01-15T10:00:00+00:00",
    orchestrator="airflow",
    cluster="prod"
)
# Results in: urn:li:dataProcessInstance:<deterministic-guid>
```

### 与 DataFlow 和 DataJob 的关系

DataProcessInstance 实体通过 `dataProcessInstanceRelationships` aspect 中的 `parentTemplate` 字段与其模板定义相互关联：

- **DataJob 实例**：追踪某个具体任务执行时，`parentTemplate` 指向 DataJob 的 URN
- **DataFlow 实例**：追踪整个管道运行（如一次 Airflow DAG run）时，`parentTemplate` 指向 DataFlow 的 URN
- **独立流程**：对于临时性或容器化的流程，`parentTemplate` 可以为 null

该关系带来若干重要能力：

- 从作业定义导航到其所有历史运行
- 跨同一作业的多次运行聚合指标
- 将当前执行与历史模式进行对比
- 通过检查过去成功的运行来排查失败

## 重要能力

### 执行追踪与监控

`dataProcessInstanceRunEvent` aspect（时序 aspect）以高粒度追踪每次执行的生命周期：

#### 运行状态

流程实例经历一个简单的生命周期：

- **STARTED**：流程执行已经开始
- **COMPLETE**：流程执行已经结束（并带有结果）

#### 运行结果

当流程完成时，结果类型表明最终结果：

- **SUCCESS**：流程成功完成
- **FAILURE**：流程因错误而失败
- **SKIPPED**：流程被跳过（例如由于条件未满足）
- **UP_FOR_RETRY**：流程失败但将被重试

#### 执行元数据

每个运行事件记录：

- **timestampMillis**：状态变更发生的时间
- **attempt**：尝试次数（用于重试）
- **durationMillis**：总执行耗时（毫秒）
- **nativeResultType**：平台特定的结果状态（例如来自 Airflow 的 "success"）

这使监控看板能够：

- 跟踪实时执行状态
- 计算成功率并分析失败模式
- 发现性能退化
- 对执行时长异常发出告警

### 流程属性

`dataProcessInstanceProperties` aspect 记录关于该次执行的元数据：

- **name**：人类可读的执行名称
- **type**：流程类型 —— BATCH_SCHEDULED、BATCH_AD_HOC 或 STREAMING
- **created**：表明实例创建时间的审计标记
- **customProperties**：用于存放平台特定元数据的任意键值对
- **externalUrl**：指向编排平台中该次执行的链接（例如 Airflow 的 task instance 页面）

customProperties 的使用示例：

```python
properties={
    "airflow_version": "2.7.0",
    "executor": "CeleryExecutor",
    "pool": "default_pool",
    "queue": "default",
    "operator": "PythonOperator"
}
```

### 实例级血缘

与定义静态血缘关系的 DataJob 不同，DataProcessInstance 捕获某次具体执行中实际消费和产出的输入与输出。

#### 输入追踪

`dataProcessInstanceInput` aspect 记录：

- **inputs**：本次运行中消费的数据集或 ML 模型的 URN
- **inputEdges**：包含时间戳与自定义属性的丰富边信息

#### 输出追踪

`dataProcessInstanceOutput` aspect 记录：

- **outputs**：本次运行中产出的数据集或 ML 模型的 URN
- **outputEdges**：包含时间戳与自定义属性的丰富边信息

这带来强大的能力：

- **时点血缘**：查看某次运行具体使用了哪些数据版本
- **影响分析**：当一次运行失败时，识别依赖其输出的下游流程
- **数据质量追踪**：将数据质量问题与具体流程执行关联
- **可复现性**：通过确切的输入重建完全相同的执行条件

示例：一个成功的 Airflow 任务可能显示其读取了 `dataset_v1` 并写入了 `dataset_v2`，而某次重试在数据演进后可能显示不同的输入/输出数据集。

### 层级化的流程关系

`dataProcessInstanceRelationships` aspect 支持复杂的执行层级：

#### 父实例

`parentInstance` 字段用于关联嵌套的执行：

```
DataFlow Instance (DAG Run)
└── DataJob Instance 1 (Task Run 1)
└── DataJob Instance 2 (Task Run 2)
└── DataJob Instance 3 (Task Run 3)
```

这带来：

- 查看某个 DAG run 内的所有任务运行
- 在 DAG run 层级聚合指标
- 理解多阶段管道中的失败传播

#### 上游实例

`upstreamInstances` 字段在流程实例之间建立依赖：

```
Process Instance A (completed) → Process Instance B (triggered)
```

这可以捕捉动态的执行依赖，例如：

- 事件驱动的触发
- 跨 DAG 依赖
- 动态的 fan-out/fan-in 模式

### 基于容器的流程

DataProcessInstance 可以表示在 Container（例如一次 ML 实验）内运行、且不绑定到特定 DataJob 或 DataFlow 的流程：

```python
from datahub.emitter.mcp_builder import ContainerKey

container_key = ContainerKey(
    platform="urn:li:dataPlatform:mlflow",
    name="experiment_123",
    env="PROD"
)

instance = DataProcessInstance.from_container(
    container_key=container_key,
    id="training_run_456"
)
```

这适用于：

- 实验跟踪系统中的 ML 训练运行
- Notebook 执行
- 临时性数据处理脚本
- Lambda/serverless 函数调用

## 代码示例

### 创建并追踪流程实例


**Python SDK：创建并追踪一个简单的流程实例**

```python
# metadata-ingestion/examples/library/data_process_instance_create_simple.py
import time

from datahub.api.entities.dataprocess.dataprocess_instance import (
    DataProcessInstance,
    InstanceRunResult,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataProcessTypeClass
from datahub.utilities.urns.data_job_urn import DataJobUrn
from datahub.utilities.urns.dataset_urn import DatasetUrn

# Create REST emitter
emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Define the parent DataJob that this instance is executing
parent_job_urn = DataJobUrn.create_from_string(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,sales_pipeline,prod),process_sales_data)"
)

# Create a process instance for a specific execution
# This might represent an Airflow task run on 2024-01-15 at 10:00:00
instance = DataProcessInstance(
    id="scheduled__2024-01-15T10:00:00+00:00",
    orchestrator="airflow",
    cluster="prod",
    template_urn=parent_job_urn,
    type=DataProcessTypeClass.BATCH_SCHEDULED,
    properties={
        "airflow_version": "2.7.0",
        "executor": "CeleryExecutor",
        "pool": "default_pool",
    },
    url="https://airflow.company.com/dags/sales_pipeline/grid?dag_run_id=scheduled__2024-01-15T10:00:00+00:00&task_id=process_sales_data",
    inlets=[
        DatasetUrn.create_from_string(
            "urn:li:dataset:(urn:li:dataPlatform:postgres,sales_db.raw_orders,PROD)"
        )
    ],
    outlets=[
        DatasetUrn.create_from_string(
            "urn:li:dataset:(urn:li:dataPlatform:postgres,sales_db.processed_orders,PROD)"
        )
    ],
)

# Record the start of execution
start_time = int(time.time() * 1000)
instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=start_time,
    attempt=1,
    emit_template=True,
    materialize_iolets=True,
)

print(f"Started tracking process instance: {instance.urn}")

# Simulate process execution
print("Process is running...")
time.sleep(2)

# Record the end of execution
end_time = int(time.time() * 1000)
instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=end_time,
    result=InstanceRunResult.SUCCESS,
    result_type="airflow",
    attempt=1,
    start_timestamp_millis=start_time,
)

print(f"Completed tracking process instance with result: SUCCESS")
print(f"Duration: {end_time - start_time}ms")
```



### 追踪失败并重试的流程


**Python SDK：追踪一次失败的流程执行及其重试**

```python
# metadata-ingestion/examples/library/data_process_instance_create_with_retry.py
import time

from datahub.api.entities.dataprocess.dataprocess_instance import (
    DataProcessInstance,
    InstanceRunResult,
)
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataProcessTypeClass
from datahub.utilities.urns.data_job_urn import DataJobUrn
from datahub.utilities.urns.dataset_urn import DatasetUrn

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

parent_job_urn = DataJobUrn.create_from_string(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,etl_pipeline,prod),load_customer_data)"
)

instance = DataProcessInstance(
    id="scheduled__2024-01-15T14:30:00+00:00",
    orchestrator="airflow",
    cluster="prod",
    template_urn=parent_job_urn,
    type=DataProcessTypeClass.BATCH_SCHEDULED,
    inlets=[
        DatasetUrn.create_from_string(
            "urn:li:dataset:(urn:li:dataPlatform:s3,customer_exports,PROD)"
        )
    ],
    outlets=[
        DatasetUrn.create_from_string(
            "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customers,PROD)"
        )
    ],
)

# First attempt
start_time_attempt1 = int(time.time() * 1000)
instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=start_time_attempt1,
    attempt=1,
    emit_template=True,
    materialize_iolets=True,
)
print("Attempt 1 started...")

time.sleep(1)

# First attempt fails
end_time_attempt1 = int(time.time() * 1000)
instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=end_time_attempt1,
    result=InstanceRunResult.UP_FOR_RETRY,
    result_type="airflow",
    attempt=1,
    start_timestamp_millis=start_time_attempt1,
)
print("Attempt 1 failed, will retry...")

time.sleep(2)

# Second attempt (retry)
start_time_attempt2 = int(time.time() * 1000)
instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=start_time_attempt2,
    attempt=2,
    emit_template=False,
    materialize_iolets=False,
)
print("Attempt 2 started (retry)...")

time.sleep(1)

# Second attempt succeeds
end_time_attempt2 = int(time.time() * 1000)
instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=end_time_attempt2,
    result=InstanceRunResult.SUCCESS,
    result_type="airflow",
    attempt=2,
    start_timestamp_millis=start_time_attempt2,
)
print("Attempt 2 succeeded!")
```



### 创建 DataFlow 实例（DAG Run）


**Python SDK：追踪一次完整的工作流执行**

```python
# metadata-ingestion/examples/library/data_process_instance_create_from_dataflow.py
import time

from datahub.api.entities.datajob import DataFlow
from datahub.api.entities.dataprocess.dataprocess_instance import (
    DataProcessInstance,
    InstanceRunResult,
)
from datahub.emitter.rest_emitter import DatahubRestEmitter

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Define the DataFlow (Airflow DAG)
dataflow = DataFlow(
    orchestrator="airflow",
    id="daily_reporting_pipeline",
    env="prod",
    description="Daily reporting pipeline that aggregates metrics",
)

# Create a DataProcessInstance for a specific DAG run
dag_run_instance = DataProcessInstance.from_dataflow(
    dataflow=dataflow,
    id="scheduled__2024-01-15T00:00:00+00:00"
)

# Set properties specific to this DAG run
dag_run_instance.properties = {
    "execution_date": "2024-01-15",
    "run_type": "scheduled",
    "external_trigger": "false",
}
dag_run_instance.url = "https://airflow.company.com/dags/daily_reporting_pipeline/grid?dag_run_id=scheduled__2024-01-15T00:00:00+00:00"

# Track DAG run start
start_time = int(time.time() * 1000)
dag_run_instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=start_time,
    attempt=1,
    emit_template=True,
    materialize_iolets=True,
)
print(f"DAG run started: {dag_run_instance.urn}")

# Simulate DAG execution
time.sleep(3)

# Track DAG run completion
end_time = int(time.time() * 1000)
dag_run_instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=end_time,
    result=InstanceRunResult.SUCCESS,
    result_type="airflow",
    attempt=1,
    start_timestamp_millis=start_time,
)
print(f"DAG run completed successfully in {end_time - start_time}ms")
```



### 追踪层级化的流程实例


**Python SDK：追踪一次带子任务实例的 DAG run**

```python
# metadata-ingestion/examples/library/data_process_instance_create_hierarchical.py
import time

from datahub.api.entities.datajob import DataFlow, DataJob
from datahub.api.entities.dataprocess.dataprocess_instance import (
    DataProcessInstance,
    InstanceRunResult,
)
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.utilities.urns.dataset_urn import DatasetUrn

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Define the DataFlow (Airflow DAG)
dataflow = DataFlow(
    orchestrator="airflow",
    id="etl_pipeline",
    env="prod",
    description="ETL pipeline with multiple tasks",
)

# Define DataJobs (Tasks in the DAG)
extract_job = DataJob(
    id="extract_data",
    flow_urn=dataflow.urn,
    description="Extract data from source",
)

# Create a DAG run instance (parent)
dag_run_id = "scheduled__2024-01-15T12:00:00+00:00"
dag_run_instance = DataProcessInstance.from_dataflow(dataflow=dataflow, id=dag_run_id)

# Track DAG run start
dag_start_time = int(time.time() * 1000)
dag_run_instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=dag_start_time,
    attempt=1,
    emit_template=True,
    materialize_iolets=False,
)
print(f"DAG run started: {dag_run_instance.urn}")

# Create task instance for extract_data (child of DAG run)
extract_instance = DataProcessInstance.from_datajob(
    datajob=extract_job,
    id=f"{dag_run_id}__extract_data",
)
extract_instance.parent_instance = dag_run_instance.urn
extract_instance.inlets = [
    DatasetUrn.create_from_string(
        "urn:li:dataset:(urn:li:dataPlatform:postgres,raw_db.orders,PROD)"
    )
]
extract_instance.outlets = [
    DatasetUrn.create_from_string(
        "urn:li:dataset:(urn:li:dataPlatform:s3,staging/orders,PROD)"
    )
]

# Track extract task execution
extract_start_time = int(time.time() * 1000)
extract_instance.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=extract_start_time,
    attempt=1,
    emit_template=True,
    materialize_iolets=True,
)
time.sleep(1)
extract_end_time = int(time.time() * 1000)
extract_instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=extract_end_time,
    result=InstanceRunResult.SUCCESS,
    attempt=1,
    start_timestamp_millis=extract_start_time,
)

# Track DAG run completion
dag_end_time = int(time.time() * 1000)
dag_run_instance.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=dag_end_time,
    result=InstanceRunResult.SUCCESS,
    attempt=1,
    start_timestamp_millis=dag_start_time,
)
print(f"DAG run completed successfully")
```



### 追踪容器中的 ML 训练运行

ML 训练运行是 DataProcessInstance 实体的一种专门用例。除标准的流程实例 aspect 外，训练运行还可以使用 ML 专用 aspect：

- **Subtype**：`MLAssetSubTypes.MLFLOW_TRAINING_RUN`，用于将该流程标识为 ML 训练运行
- **mlTrainingRunProperties**：ML 专用元数据，包括训练指标、超参数和输出 URL
- **Relationships**：指向 ML 模型（通过 `mlModelProperties.trainingJobs`）和实验（通过 `container` aspect）的关联

有关 ML 训练运行的完整文档（包括涉及实验、模型和数据集的完整工作流），请参阅 [ML Model 实体文档](19-mlmodel.md#training-runs-and-experiments)。


**Python SDK：追踪一次独立的 ML 训练运行**

```python
# metadata-ingestion/examples/library/data_process_instance_create_ml_training.py
import time

from datahub.api.entities.dataprocess.dataprocess_instance import (
    DataProcessInstance,
    InstanceRunResult,
)
from datahub.emitter.mcp_builder import ContainerKey
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DataProcessTypeClass
from datahub.utilities.urns.dataset_urn import DatasetUrn

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

# Define the ML experiment container
experiment_container = ContainerKey(
    platform="urn:li:dataPlatform:mlflow",
    name="customer_churn_experiment",
    env="PROD"
)

# Create a process instance for a training run
training_run = DataProcessInstance.from_container(
    container_key=experiment_container,
    id="run_abc123def456"
)

# Set training-specific properties
training_run.type = DataProcessTypeClass.BATCH_AD_HOC
training_run.properties = {
    "model_type": "RandomForestClassifier",
    "hyperparameters": "n_estimators=100,max_depth=10",
    "framework": "scikit-learn",
    "framework_version": "1.3.0",
}
training_run.url = "https://mlflow.company.com/experiments/5/runs/abc123def456"

# Set training data inputs
training_run.inlets = [
    DatasetUrn.create_from_string(
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,ml.training_data,PROD)"
    )
]

# Set model output
training_run.outlets = [
    DatasetUrn.create_from_string(
        "urn:li:mlModel:(urn:li:dataPlatform:mlflow,customer_churn_model_v2,PROD)"
    )
]

# Track training start
start_time = int(time.time() * 1000)
training_run.emit_process_start(
    emitter=emitter,
    start_timestamp_millis=start_time,
    attempt=1,
    emit_template=False,
    materialize_iolets=True,
)
print("ML training run started...")

# Simulate training
time.sleep(5)

# Track training completion
end_time = int(time.time() * 1000)
training_run.emit_process_end(
    emitter=emitter,
    end_timestamp_millis=end_time,
    result=InstanceRunResult.SUCCESS,
    result_type="mlflow",
    attempt=1,
    start_timestamp_millis=start_time,
)
print(f"ML training completed in {(end_time - start_time)/1000:.2f}s")
```



### 通过 REST API 查询流程实例历史


**REST API：查询某个 DataJob 的执行历史**

```bash
# Get all process instances for a specific DataJob
curl -X GET 'http://localhost:8080/relationships?direction=INCOMING&urn=urn%3Ali%3AdataJob%3A%28urn%3Ali%3AdataFlow%3A%28airflow%2Csales_pipeline%2Cprod%29%2Cprocess_sales_data%29&types=InstanceOf'
```

响应：

```json
{
  "start": 0,
  "count": 10,
  "relationships": [
    {
      "type": "InstanceOf",
      "entity": "urn:li:dataProcessInstance:abc123..."
    },
    {
      "type": "InstanceOf",
      "entity": "urn:li:dataProcessInstance:def456..."
    }
  ],
  "total": 25
}
```

若要获取每个实例的完整详情，可以查询相应实体：

```bash
curl 'http://localhost:8080/entitiesV2/urn%3Ali%3AdataProcessInstance%3Aabc123...'
```

响应包含所有 aspect：

```json
{
  "urn": "urn:li:dataProcessInstance:abc123...",
  "aspects": {
    "dataProcessInstanceProperties": {
      "name": "scheduled__2024-01-15T10:00:00+00:00",
      "type": "BATCH_SCHEDULED",
      "created": {
        "time": 1705318800000,
        "actor": "urn:li:corpuser:datahub"
      },
      "customProperties": {
        "airflow_version": "2.7.0"
      }
    },
    "dataProcessInstanceInput": {
      "inputs": [
        "urn:li:dataset:(urn:li:dataPlatform:postgres,sales_db.raw_orders,PROD)"
      ]
    },
    "dataProcessInstanceOutput": {
      "outputs": [
        "urn:li:dataset:(urn:li:dataPlatform:postgres,sales_db.processed_orders,PROD)"
      ]
    },
    "dataProcessInstanceRelationships": {
      "parentTemplate": "urn:li:dataJob:(urn:li:dataFlow:(airflow,sales_pipeline,prod),process_sales_data)"
    }
  }
}
```



### 查询流程实例运行事件


**GraphQL：查询带状态与时间信息的运行历史**

DataHub 的 GraphQL API 在 DataJob 实体上提供 `runs` 字段，用于查询执行历史：

```graphql
query GetJobRuns {
  dataJob(
    urn: "urn:li:dataJob:(urn:li:dataFlow:(airflow,sales_pipeline,prod),process_sales_data)"
  ) {
    runs(start: 0, count: 10) {
      total
      runs {
        urn
        created {
          time
        }
        properties {
          name
          type
          externalUrl
          customProperties {
            key
            value
          }
        }
        relationships {
          parentTemplate
          parentInstance
        }
        inputs {
          urn
          type
        }
        outputs {
          urn
          type
        }
      }
    }
  }
}
```

注意：时序的 `dataProcessInstanceRunEvent` aspect 才包含真实的运行状态、时间与结果。要查询这部分时序数据，请使用时序聚合 API 或直接查询时序索引。



## 集成点

### 编排平台

DataProcessInstance 是编排平台与 DataHub 元数据层之间的桥梁：

#### Airflow 集成

DataHub 的 Airflow 插件会自动为以下对象创建 DataProcessInstance 实体：

- **DAG runs**：每个 Airflow DagRun 都成为一个 DataProcessInstance，其父实体为 DataFlow
- **Task runs**：每个 TaskInstance 都成为一个 DataProcessInstance，其父实体为 DataJob

该插件会追踪：

- 来自 TaskInstance 的开始与结束时间
- 成功/失败状态
- 重试次数
- 实际读取/写入的数据集（通过血缘后端）

配置示例：

```python
from datahub_airflow_plugin.datahub_listener import DatahubListener

# In your airflow.cfg or environment:
# AIRFLOW__DATAHUB__ENABLED=true
# AIRFLOW__DATAHUB__DATAHUB_CONN_ID=datahub_rest_default
```

#### 其他编排器

类似模式适用于：

- **Dagster**：Dagster 运行与 step 执行
- **Prefect**：flow run 与 task run
- **Spark**：Spark 应用执行
- **dbt**：dbt run 执行
- **Fivetran**：Sync 执行

### 与 DataJob 和 DataFlow 的关系

DataProcessInstance 与 DataJob 和 DataFlow 实体互为补充：

| 实体                   | 用途       | 基数                         | 示例                            |
| ---------------------- | ---------- | ---------------------------- | ------------------------------- |
| DataFlow               | 管道定义   | 每个逻辑管道 1 个            | Airflow DAG "sales_pipeline"    |
| DataJob                | 任务定义   | 每个 DataFlow N 个           | Airflow Task "process_sales_data" |
| DataProcessInstance    | 执行运行   | 每个 DataJob/DataFlow M 个  | 2024-01-15 10:00 的任务运行      |

关键区别：

- **静态与动态**：DataJob/DataFlow 定义“应该发生什么”；DataProcessInstance 记录“实际发生了什么”
- **血缘**：DataJob 定义预期血缘；DataProcessInstance 捕获该次运行的真实血缘
- **元数据**：DataJob 描述任务；DataProcessInstance 描述执行

### 与数据集的关系

DataProcessInstance 为数据集建立实例级血缘：

```
Dataset Version 1 ─┐
                   ├─> DataProcessInstance (Run #1) ─> Dataset Version 2
Dataset Version 1 ─┘

Dataset Version 2 ─┐
                   ├─> DataProcessInstance (Run #2) ─> Dataset Version 3
Dataset Version 2 ─┘
```

这带来：

- **时点血缘**：哪次运行使用了哪个数据版本
- **数据溯源**：将数据质量问题追溯到具体执行
- **可复现性**：理解过去运行的确切条件

### GraphQL 解析器

DataProcessInstance 实体通过若干解析器在 GraphQL 中暴露：

1. **DataJobRunsResolver**：获取某个 DataJob 的流程实例

   - 按 `parentTemplate` 字段查询
   - 按创建时间排序（最新优先）
   - 仅返回带运行事件的实例

2. **EntityRunsResolver**：适用于任意实体运行的通用解析器

   - 用于 DataFlow 的运行
   - 使用类似的过滤与排序逻辑

3. **DataProcessInstanceMapper**：将内部表示转换为 GraphQL 类型
   - 将所有 aspect 映射为 GraphQL 字段
   - 处理与父实体的关系

GraphQL schema 暴露如下：

```graphql
type DataJob {
  runs(start: Int, count: Int): DataProcessInstanceResult
}

type DataFlow {
  runs(start: Int, count: Int): DataProcessInstanceResult
}

type DataProcessInstance {
  urn: String!
  properties: DataProcessInstanceProperties
  relationships: DataProcessInstanceRelationships
  inputs: [Entity]
  outputs: [Entity]
  # Note: Run events are in timeseries data
}
```

## 注意事项与例外

### 实例与定义的区别

一个常见误区是混淆实例级元数据与定义级元数据：

**错误**：给 DataProcessInstance 添加标签

```python
# Don't do this - tags belong on the DataJob
instance = DataProcessInstance(...)
# instance.tags = ["pii", "critical"]  # This doesn't exist
```

**正确**：给 DataJob 添加标签，用 properties 存放与运行相关的元数据

```python
# Tag the DataJob definition
datajob.tags = ["pii", "critical"]

# Use properties for run-specific metadata
instance = DataProcessInstance(...)
instance.properties = {"data_size_mb": "150", "row_count": "1000000"}
```

### 执行状态生命周期

DataProcessInstance 的状态遵循一个简单的状态机：

1. 执行开始时发出 STARTED 事件
2. 执行结束时发出 COMPLETE 事件（并带有 SUCCESS/FAILURE/SKIPPED/UP_FOR_RETRY 结果）

常见错误：

- **忘记发出 COMPLETE**：务必同时发出 START 和 END 事件
- **发出多个 COMPLETE 事件**：重试应使用同一实例但不同的 attempt 编号
- **结果类型错误**：UP_FOR_RETRY 用于将会重试的临时性失败；FAILURE 是最终结果

### 历史数据保留

在高频管道中，DataProcessInstance 实体可能迅速累积：

- 每 5 分钟运行一次的管道每天产生 288 个实例
- 含 10 个任务的管道每天产生 2,880 个实例
- 一年下来可能超过 100 万个实例

需要考虑：

- **保留策略**：考虑实现保留策略以删除旧实例
- **聚合**：对于长期分析，将实例数据聚合为汇总指标
- **采样**：对于极高频的流程，可考虑采样（例如只追踪每第 10 次执行）
- **存储成本**：时序数据（运行事件）可能增长很大，需监控索引大小

DataHub 不会自动清理旧的 DataProcessInstance 实体。你应当根据自身需求实现清理：

```python
# Example: Cleanup instances older than 90 days
import datetime
from datahub.emitter.rest_emitter import DatahubRestEmitter

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

cutoff_time = int((datetime.datetime.now() - datetime.timedelta(days=90)).timestamp() * 1000)

# Query for old instances and soft-delete them
# (Implementation depends on your retention requirements)
```

### 实例 URN 的稳定性

DataProcessInstance 的 URN 由 orchestrator、cluster 和 id 字段生成。这意味着：

- **相同的 id = 相同的 URN**：复用相同的 id 会覆盖先前的实例
- **必须唯一**：每次执行都必须有唯一的 id
- **编排器变更**：更改编排器名称会创建一条新的实体血缘

最佳实践：

- 使用与执行相关的 ID（时间戳、run ID、UUID）
- 不要在不同执行之间复用 ID
- 保持编排器名称一致
- 若同一管道运行在多个环境中，应在 ID 中包含环境（cluster）



> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](06-dataprocessinstance.md)。。
