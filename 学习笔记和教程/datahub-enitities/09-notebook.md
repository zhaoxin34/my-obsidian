---
title: 笔记本
entity: notebook
order: 09
source: https://docs.datahub.com/docs/generated/metamodel/entities/notebook.md
---

# Notebook

Notebook 是一种元数据实体，代表将代码执行、文本说明、数据可视化和查询结果结合在一起的交互式计算文档。Notebook 是用于数据分析、探索和文档化的协作环境，常见于数据科学、分析和商业智能工作流中。

Notebook 实体同时记录结构化组件（包含文本、查询或图表的单元格）以及来自 Jupyter、Databricks、QueryBook、Hex、Mode、Deepnote 等基于笔记本工具的 notebook 元数据。

> **⚠️ 注意**：Notebook 实体目前处于 **BETA** 阶段。虽然核心功能已经稳定，但实体模型和 UI 功能可能会根据社区反馈继续演进。Notebook 支持正在积极开发与改进之中。

## 身份标识

Notebook 由两个组件唯一标识：

- **notebookTool**：notebook 平台或工具的名称（例如 "querybook"、"jupyter"、"databricks"、"hex"）
- **notebookId**：该 notebook 在对应工具内全局唯一的标识符

Notebook 的 URN 结构为：

```
urn:li:notebook:(<notebookTool>,<notebookId>)
```

### 示例

```
urn:li:notebook:(querybook,773)
urn:li:notebook:(jupyter,analysis_2024_q1)
urn:li:notebook:(databricks,/Users/analyst/customer_segmentation)
urn:li:notebook:(hex,a8b3c5d7-1234-5678-90ab-cdef12345678)
```

### 生成稳定的 Notebook ID

即便某个 notebook 工具存在多个部署，`notebookId` 也应在该工具内保持全局唯一。最佳实践包括：

- **基于 URL 的 ID**：使用 notebook 的 URL 或路径（例如 `querybook.com/notebook/773`）
- **平台 ID**：使用平台原生的 notebook 标识符（例如 Databricks workspace 路径）
- **UUID**：对于没有原生 ID 的平台，基于 notebook 元数据生成稳定的 UUID
- **文件路径**：对于 Jupyter notebook，使用相对于某个已知根目录的文件路径

关键要求是：同一个 notebook 在不同摄取运行中应始终产生相同的 URN。

## 重要能力

### Notebook 信息

`notebookInfo` aspect 包含 notebook 的核心元数据：

- **title**：notebook 的显示名称（可搜索并用于自动补全）
- **description**：对 notebook 行为或分析内容的详细描述
- **customProperties**：平台专属元数据的键值对
- **externalUrl**：指向原生平台中该 notebook 的链接
- **changeAuditStamps**：跟踪由谁在何时创建/修改了 notebook

以下代码片段展示了如何创建带有基本信息的 Notebook。


**Python SDK：创建 Notebook**

```python
# Inlined from /metadata-ingestion/examples/library/notebook_create.py
# metadata-ingestion/examples/library/notebook_create.py
import os
import time
from typing import Dict, Optional

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    ChangeAuditStampsClass,
    NotebookInfoClass,
)


def create_notebook_metadata(
    notebook_urn: str,
    title: str,
    description: str,
    external_url: str,
    custom_properties: Optional[Dict[str, str]] = None,
    actor: str = "urn:li:corpuser:data_scientist",
    timestamp_millis: Optional[int] = None,
) -> MetadataChangeProposalWrapper:
    """
    Create metadata for a notebook entity.

    Args:
        notebook_urn: URN of the notebook
        title: Title of the notebook
        description: Description of the notebook
        external_url: URL to access the notebook
        custom_properties: Optional dictionary of custom properties
        actor: URN of the actor creating the notebook
        timestamp_millis: Optional timestamp in milliseconds (defaults to current time)

    Returns:
        MetadataChangeProposalWrapper containing the notebook metadata
    """
    timestamp_millis = timestamp_millis or int(time.time() * 1000)

    audit_stamp = AuditStampClass(time=timestamp_millis, actor=actor)

    notebook_info = NotebookInfoClass(
        title=title,
        description=description,
        externalUrl=external_url,
        customProperties=custom_properties or {},
        changeAuditStamps=ChangeAuditStampsClass(
            created=audit_stamp,
            lastModified=audit_stamp,
        ),
    )

    return MetadataChangeProposalWrapper(
        entityUrn=notebook_urn,
        aspect=notebook_info,
    )


def main() -> None:
    """
    Main function to create a notebook example.

    Environment Variables:
        DATAHUB_GMS_URL: DataHub GMS server URL (default: http://localhost:8080)
        DATAHUB_GMS_TOKEN: DataHub access token (if authentication is required)
    """
    gms_server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
    token = os.getenv("DATAHUB_GMS_TOKEN")
    emitter = DatahubRestEmitter(gms_server=gms_server, token=token)

    notebook_urn = "urn:li:notebook:(querybook,customer_analysis_2024)"

    event = create_notebook_metadata(
        notebook_urn=notebook_urn,
        title="Customer Segmentation Analysis 2024",
        description="Comprehensive analysis of customer segments including RFM analysis, cohort analysis, and predictive scoring for marketing campaigns",
        external_url="https://querybook.company.com/notebook/customer_analysis_2024",
        custom_properties={
            "workspace": "analytics",
            "team": "growth",
            "last_run": "2024-01-15T10:30:00Z",
        },
    )

    emitter.emit(event)
    print(f"Created notebook {notebook_urn}")


if __name__ == "__main__":
    main()

```



### Notebook 内容

`notebookContent` aspect 通过一组单元格记录 notebook 的实际结构与内容。每个单元格代表 notebook 内的一个独立内容块。

#### 单元格类型

Notebook 支持三种单元格类型：

1. **TEXT_CELL**：用于文档、解释和叙述的 Markdown 或富文本内容

   - 包含格式化文本、标题、列表、图片和文档
   - 用于解释分析步骤、补充上下文和编写报告

2. **QUERY_CELL**：用于数据检索与转换的 SQL 或其他查询语言语句

   - 包含可执行的查询代码
   - 引用数据集并产生结果集
   - 可关联到具体的 query 实体以进行血缘追踪

3. **CHART_CELL**：基于查询结果构建的数据可视化与图表
   - 包含图表和可视化的配置
   - 可引用 chart 实体以保持元数据一致性
   - 表示数据分析的可视化输出

`notebookContent` aspect 中的每个单元格包括：

- **type**：单元格类型（TEXT_CELL、QUERY_CELL 或 CHART_CELL）
- **textCell**：文本单元格的内容（其他类型为 null）
- **queryCell**：查询单元格的内容（其他类型为 null）
- **chartCell**：图表单元格的内容（其他类型为 null）

该单元格列表表示 notebook 呈现给用户时的顺序结构。


**Python SDK：向 Notebook 添加内容**

```python
# Inlined from /metadata-ingestion/examples/library/notebook_add_content.py
# metadata-ingestion/examples/library/notebook_add_content.py
import time

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    AuditStampClass,
    ChangeAuditStampsClass,
    ChartCellClass,
    NotebookCellClass,
    NotebookCellTypeClass,
    NotebookContentClass,
    QueryCellClass,
    TextCellClass,
)

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

notebook_urn = "urn:li:notebook:(querybook,customer_analysis_2024)"

audit_stamp = AuditStampClass(
    time=int(time.time() * 1000), actor="urn:li:corpuser:data_scientist"
)
change_audit = ChangeAuditStampsClass(created=audit_stamp, lastModified=audit_stamp)

cells = [
    NotebookCellClass(
        type=NotebookCellTypeClass.TEXT_CELL,
        textCell=TextCellClass(
            cellId="cell-1",
            cellTitle="Introduction",
            text="# Customer Segmentation Analysis\n\nThis notebook analyzes customer behavior patterns to identify high-value segments.",
            changeAuditStamps=change_audit,
        ),
    ),
    NotebookCellClass(
        type=NotebookCellTypeClass.QUERY_CELL,
        queryCell=QueryCellClass(
            cellId="cell-2",
            cellTitle="Customer Activity Query",
            rawQuery="SELECT customer_id, SUM(revenue) as total_revenue, COUNT(*) as order_count FROM orders WHERE order_date >= '2024-01-01' GROUP BY customer_id ORDER BY total_revenue DESC LIMIT 1000",
            lastExecuted=audit_stamp,
            changeAuditStamps=change_audit,
        ),
    ),
    NotebookCellClass(
        type=NotebookCellTypeClass.CHART_CELL,
        chartCell=ChartCellClass(
            cellId="cell-3",
            cellTitle="Revenue Distribution by Segment",
            changeAuditStamps=change_audit,
        ),
    ),
]

notebook_content = NotebookContentClass(cells=cells)

event = MetadataChangeProposalWrapper(
    entityUrn=notebook_urn,
    aspect=notebook_content,
)

emitter.emit(event)
print(f"Added content to notebook {notebook_urn}")

```



### 可编辑属性

`editableNotebookProperties` aspect 允许用户通过 DataHub UI 添加或修改某些 notebook 属性，而不会影响源系统：

- **description**：用户可编辑的描述，用于补充或覆盖摄取而来的描述

这种分离机制让 DataHub 用户可以丰富 notebook 元数据，同时保留来自源平台的原始信息。

### 所有权

Notebook 通过 `ownership` aspect 支持所有权管理，便于跟踪谁负责维护和治理每个 notebook。所有权类型包括：

- **TECHNICAL_OWNER**：创建或维护该 notebook 的工程师或数据科学家
- **BUSINESS_OWNER**：拥有相关分析或洞察的业务相关方
- **DATA_STEWARD**：负责 notebook 质量与合规的数据治理人员


**Python SDK：为 Notebook 添加所有者**

```python
# Inlined from /metadata-ingestion/examples/library/notebook_add_owner.py
# metadata-ingestion/examples/library/notebook_add_owner.py

from datahub.emitter.mce_builder import make_user_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

notebook_urn = "urn:li:notebook:(querybook,customer_analysis_2024)"

owner_to_add = make_user_urn("data_scientist")
ownership_type = OwnershipTypeClass.TECHNICAL_OWNER

owners_to_add = [
    OwnerClass(owner=owner_to_add, type=ownership_type),
]

ownership = OwnershipClass(owners=owners_to_add)

event = MetadataChangeProposalWrapper(
    entityUrn=notebook_urn,
    aspect=ownership,
)

emitter.emit(event)
print(f"Added owner {owner_to_add} to notebook {notebook_urn}")

```



### 标签与术语表术语

Notebook 可以被打标签并关联术语表术语，以便组织和发现：

- **标签**（通过 `globalTags` aspect）：诸如 "exploratory"、"production"、"deprecated"、"customer-analysis" 的非正式分类标签
- **术语表术语**（通过 `glossaryTerms` aspect）：将 notebook 与业务概念关联的正式业务词汇


**Python SDK：为 Notebook 添加标签**

```python
# Inlined from /metadata-ingestion/examples/library/notebook_add_tags.py
# metadata-ingestion/examples/library/notebook_add_tags.py

from datahub.emitter.mce_builder import make_tag_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    TagAssociationClass,
)

emitter = DatahubRestEmitter(gms_server="http://localhost:8080")

notebook_urn = "urn:li:notebook:(querybook,customer_analysis_2024)"

tag_to_add = make_tag_urn("production")
tag_association = TagAssociationClass(tag=tag_to_add)

global_tags = GlobalTagsClass(tags=[tag_association])

event = MetadataChangeProposalWrapper(
    entityUrn=notebook_urn,
    aspect=global_tags,
)

emitter.emit(event)
print(f"Added tag {tag_to_add} to notebook {notebook_urn}")

```



### 领域

Notebook 可以通过 `domains` aspect 被分配到一个或多个领域，从而按业务单元、团队或职能领域进行组织。这有助于大规模场景下的发现与治理。

### 浏览路径

`browsePaths` 和 `browsePathsV2` aspect 支持在 DataHub 内对 notebook 进行层级导航，允许用户按平台、工作区、文件夹或其他组织结构浏览 notebook。

### 应用

`applications` aspect 允许将 notebook 关联到特定应用或用例，帮助跟踪哪些业务应用或工作流依赖特定 notebook。

### 子类型

`subTypes` aspect 支持将 notebook 归类到如下类别：

- "Data Analysis"
- "ML Training"
- "Reporting"
- "Data Exploration"
- "ETL Development"

这有助于用户找到与自己需求相关的 notebook。

### 机构记忆

通过 `institutionalMemory` aspect，notebook 可以关联外部文档、wiki、运行手册或其他为其用途提供补充上下文的资源链接。

### 测试结果

`testResults` aspect 可以记录在 notebook 内执行的数据质量测试或校验检查结果，将基于 notebook 的测试纳入 DataHub 的数据质量体系。

## 集成点

### 与 Dataset 的关系

Notebook 通过查询单元格与数据集产生关系：

- **查询主体**：当 notebook 的查询单元格引用数据集时，这些关系会被记录下来
- **血缘**：当 notebook 中的查询创建或转换数据时，notebook 可以成为血缘信息的来源
- **使用统计**：Notebook 的查询执行模式会计入数据集的使用统计

### 与 Chart 的关系

当 notebook 包含图表单元格时，这些单元格可以引用 chart 实体，从而在 notebook 与其产出的可视化之间建立关系。对于 Mode 或 Hex 等 BI notebook 工具尤其相关，因为这类 notebook 会生成可复用的图表。

### 与 Query 的关系

Notebook 中的查询单元格可以关联到 query 实体，从而支持：

- **查询复用**：跟踪特定查询在不同 notebook 中的使用情况
- **血缘传播**：利用 query 实体的 SQL 解析能力实现 notebook 血缘
- **使用分析**：在 notebook 工作流的上下文中理解查询模式

### 平台实例

`dataPlatformInstance` aspect 将 notebook 与某个特定的 notebook 平台实例（例如特定的 Databricks workspace 或 Hex 账户）关联，这在同一平台存在多个实例时必不可少。

### 摄取来源

多个 DataHub 连接器会抽取 notebook 元数据：

- **QueryBook**：摄取 notebook 及其单元格和元数据
- **Jupyter**：可处理来自代码仓库或文件系统的 notebook 文件
- **Databricks**：从 Databricks workspace 中抽取 notebook
- **Hex**：摄取 notebook 及其项目上下文
- **Mode**：抽取 notebook（在 Mode 中称为 "reports"）及其查询与可视化
- **Deepnote**：可从 Deepnote 项目摄取协作式 notebook

这些连接器通常会：

1. 从平台的 API 或文件系统中发现 notebook
2. 抽取 notebook 元数据（标题、描述、作者、时间戳）
3. 将 notebook 结构解析为相应类型的单元格
4. 创建到所引用数据集、查询和图表的关系
5. 跟踪所有权与协作信息

### GraphQL API

Notebook 可通过 DataHub 的 GraphQL API 访问，支持如下查询：

- Notebook 元数据与属性
- Notebook 内容与单元格结构
- 与数据集、图表和查询的关系
- 所有权与治理信息

## 值得注意的例外情况

### Beta 状态

作为 BETA 特性，notebook 存在一些限制：

- **UI 支持**：DataHub web 界面可能无法完整可视化所有 notebook 能力
- **血缘抽取**：来自 notebook 查询的自动血缘可能因平台而异
- **搜索与发现**：针对 notebook 的搜索功能仍在演进
- **单元格执行状态**：目前不会采集执行结果和输出单元格

用户应预期随着该特性成熟，还会有持续改进和可能的 schema 变更。

### 单元格内容存储

Notebook 单元格存储结构信息和元数据，但可能不会采集：

- **完整执行输出**：查询执行产生的大结果集
- **二进制附件**：嵌入 notebook 的图片或文件（通过 URL 引用除外）
- **交互式组件**：notebook 中的动态 UI 元素，例如 ipywidgets

其重点在于采集 notebook 的代码、结构和元数据，而非执行产物。

### 平台专属特性

不同 notebook 平台各自有一些可能无法完美映射到 DataHub 模型的特性：

- **Databricks**：协作特性、版本控制和作业调度
- **Hex**：应用构建特性和参数输入
- **Jupyter**：内核专属特性和扩展
- **Mode**：报告调度和共享配置

摄取连接器会采集通用特性，而平台专属能力可能保存在 `customProperties` 中。

### 单元格顺序

`notebookContent` 的单元格数组会保留单元格在源 notebook 中的出现顺序。不过，具有复杂分支逻辑或非线性执行流程的 notebook，可能无法被简单的有序列表完整表达。

### 版本控制

当前的 notebook 模型并未原生跟踪 notebook 版本或修订历史。`changeAuditStamps` 记录了最后修改信息，但完整的版本控制需要与源平台的版本系统集成（例如 Jupyter 使用 Git，Databricks 使用平台版本历史）。

### 大型 Notebook

包含数百个单元格的超大 notebook 可能带来性能方面的考虑：

- 摄取时间随 notebook 体积增长
- UI 渲染可能针对 notebook 元数据而非完整内容展示做优化
- 考虑将极大型的 notebook 拆分为更小、更聚焦的 notebook，以便管理

## 使用场景

DataHub 中的 Notebook 支持若干重要使用场景：

1. **发现**：查找与特定数据集、业务领域或分析主题相关的 notebook
2. **文档化**：通过自文档化的 notebook 代码理解数据如何被分析与转换
3. **血缘**：跟踪基于 notebook 的 ETL 和转换流水线中的数据流
4. **协作**：找出特定分析的 notebook 所有者和主题专家
5. **治理**：为基于 notebook 的分析应用标签、术语和分类
6. **影响分析**：当 notebook 所使用的数据集发生变化时，了解下游依赖
7. **知识管理**：沉淀嵌在分析 notebook 中的机构知识

将 notebook 纳入 DataHub 的元数据图谱后，组织便可以用与生产数据资产同等的严谨度来对待分析代码。



> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](09-notebook.md)。
