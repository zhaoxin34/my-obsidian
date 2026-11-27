---
title: 笔记本
entity: notebook
order: 09
source: https://docs.datahub.com/docs/generated/metamodel/entities/notebook.md
---

# Notebook

Notebook（笔记本）是一个元数据实体，用于表示结合了代码执行、文本文档、数据可视化和查询结果的交互式计算文档。笔记本是用于数据分析、探索与文档化的协作环境，常见于数据科学、分析与商业智能工作流中。

Notebook 实体同时捕获结构组成部分（包含文本、查询或图表的单元格）以及来自 Jupyter、Databricks、QueryBook、Hex、Mode、Deepnote 等平台的笔记本元数据。

> **⚠️ 注意**：Notebook 实体目前处于 **BETA** 阶段。虽然核心功能是稳定的，但实体模型与 UI 功能可能会根据社区反馈而演进。Notebook 支持正在被积极开发与改进。

## 标识

Notebook 由两个组成部分唯一标识：

- **notebookTool**：笔记本平台或工具的名称（如 "querybook"、"jupyter"、"databricks"、"hex"）
- **notebookId**：该笔记本在该工具内部全局唯一的标识符

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

`notebookId` 应当在某个笔记本工具内全局唯一，即使该工具存在多个部署也是如此。最佳实践包括：

- **基于 URL 的 ID**：使用笔记本的 URL 或路径（如 `querybook.com/notebook/773`）
- **平台 ID**：使用平台原生的笔记本标识符（如 Databricks workspace 路径）
- **UUID**：对于没有原生 ID 的平台，基于笔记本元数据生成稳定的 UUID
- **文件路径**：对于 Jupyter 笔记本，使用相对于某个已知根目录的文件路径

关键要求是：同一个笔记本在不同的摄取运行中始终应产生相同的 URN。

## 重要能力

### Notebook 信息

`notebookInfo` aspect 包含笔记本的核心元数据：

- **title**：笔记本的显示名称（可搜索并用于自动补全）
- **description**：详细描述该笔记本做了什么或分析了什么
- **customProperties**：用于平台特定元数据的键值对
- **externalUrl**：指向其原生平台中笔记本的链接
- **changeAuditStamps**：跟踪谁创建/修改了笔记本以及何时修改

下面的代码片段展示了如何创建带有基本信息的 Notebook。

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

`notebookContent` aspect 通过单元格列表捕获笔记本的实际结构与内容。每个单元格代表笔记本内的一个独立内容块。

#### 单元格类型

笔记本支持三种类型的单元格：

1. **TEXT_CELL**：用于文档、说明与叙述的 Markdown 或富文本内容

   - 包含格式化文本、标题、列表、图片和文档
   - 用于解释分析步骤、提供上下文并生成报告

2. **QUERY_CELL**：用于数据获取与转换的 SQL 或其他查询语言语句

   - 包含可执行的查询代码
   - 引用数据集并产生结果集
   - 可关联到具体的 query 实体以进行血缘追踪

3. **CHART_CELL**：基于查询结果构建的数据可视化与图表
   - 包含图表与可视化的配置
   - 可引用 chart 实体以保持元数据一致性
   - 表示数据分析的可视化输出

`notebookContent` aspect 中的每个单元格包含：

- **type**：单元格类型（TEXT_CELL、QUERY_CELL 或 CHART_CELL）
- **textCell**：文本单元格的内容（其他类型为 null）
- **queryCell**：查询单元格的内容（其他类型为 null）
- **chartCell**：图表单元格的内容（其他类型为 null）

该单元格列表表示了笔记本在用户看来所呈现的顺序结构。

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

`editableNotebookProperties` aspect 允许用户通过 DataHub UI 添加或修改某些笔记本属性，而不会影响源系统：

- **description**：用户可编辑的描述，可补充或覆盖摄取而来的描述

这种分离让 DataHub 用户能够丰富笔记本元数据，同时保留来自源平台的原始信息。

### 所有权

笔记本通过 `ownership` aspect 支持所有权，从而可以跟踪谁负责维护与治理每个笔记本。所有权类型包括：

- **TECHNICAL_OWNER**：创建或维护该笔记本的工程师或数据科学家
- **BUSINESS_OWNER**：拥有该分析或洞察的业务相关方
- **DATA_STEWARD**：负责笔记本质量与合规性的数据治理人员

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

### 标签与术语表项

笔记本可以被打标签并关联术语表项，以便组织与发现：

- **标签**（通过 `globalTags` aspect）：非正式的分类标签，如 "exploratory"、"production"、"deprecated"、"customer-analysis"
- **术语表项**（通过 `glossaryTerms` aspect）：将笔记本关联到业务概念的正式业务词汇

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

`browsePaths` 与 `browsePathsV2` aspect 支持在 DataHub 内对笔记本进行层级导航，使用户可以按平台、工作区、文件夹或其他组织结构浏览笔记本。

### 应用

`applications` aspect 允许将笔记本关联到特定应用或使用场景，有助于跟踪哪些业务应用或工作流依赖特定笔记本。

### 子类型

`subTypes` aspect 支持将笔记本归类为以下类别：

- "Data Analysis"
- "ML Training"
- "Reporting"
- "Data Exploration"
- "ETL Development"

这有助于用户找到与自己具体需求相关的笔记本。

### 机构记忆

通过 `institutionalMemory` aspect，笔记本可以拥有指向外部文档、wiki、运行手册或其他资源的链接，以提供关于其用途与使用方式的额外上下文。

### 测试结果

`testResults` aspect 可以捕获在笔记本内执行的数据质量测试或校验检查结果，将基于笔记本的测试纳入 DataHub 的数据质量框架。

## 集成点

### 与 Dataset 的关系

Notebook 通过查询单元格与数据集建立关系：

- **查询主题**：当笔记本的查询单元格引用数据集时，这些关系会被捕获
- **血缘**：当笔记本的查询创建或转换数据时，笔记本可以作为血缘信息的来源
- **使用统计**：笔记本通过其查询执行模式为数据集使用统计贡献数据

### 与 Chart 的关系

当笔记本包含图表单元格时，这些单元格可以引用 chart 实体，从而在笔记本与其产出的可视化之间建立关系。这对于 Mode 或 Hex 等 BI 笔记本工具尤其相关，因为它们会生成可复用的图表。

### 与 Query 的关系

笔记本中的查询单元格可以关联到 query 实体，从而实现：

- **查询复用**：跟踪特定查询在不同笔记本中的使用情况
- **血缘传播**：利用 query 实体的 SQL 解析能力来生成笔记本血缘
- **使用分析**：在笔记本工作流的上下文中理解查询模式

### 平台实例

`dataPlatformInstance` aspect 将笔记本与某个特定的笔记本平台实例关联起来（如特定的 Databricks workspace 或 Hex 账户），当同一平台存在多个实例时这尤为关键。

### 摄取来源

多个 DataHub 连接器会提取笔记本元数据：

- **QueryBook**：摄取笔记本及其单元格与元数据
- **Jupyter**：可处理来自代码仓库或文件系统的笔记本文件
- **Databricks**：从 Databricks workspace 中提取笔记本
- **Hex**：摄取笔记本及其项目上下文
- **Mode**：提取笔记本（在 Mode 中称为 "reports"）及其查询与可视化
- **Deepnote**：可从 Deepnote 项目中摄取协作式笔记本

这些连接器通常会：

1. 从平台的 API 或文件系统中发现笔记本
2. 提取笔记本元数据（标题、描述、作者、时间戳）
3. 将笔记本结构解析为相应类型的单元格
4. 创建到所引用的数据集、查询与图表的关系
5. 跟踪所有权与协作信息

### GraphQL API

笔记本可通过 DataHub 的 GraphQL API 访问，支持以下查询：

- 笔记本元数据与属性
- 笔记本内容与单元格结构
- 与数据集、图表和查询的关系
- 所有权与治理信息

## 重要例外

### Beta 状态

作为 BETA 功能，笔记本存在一些限制：

- **UI 支持**：DataHub Web 界面可能无法完整可视化所有笔记本能力
- **血缘提取**：来自笔记本查询的自动血缘可能因平台而异
- **搜索与发现**：针对笔记本的搜索功能仍在演进中
- **单元格执行状态**：目前不捕获执行结果与输出单元格

用户应预期随着该功能成熟而持续改进，并可能出现 schema 变更。

### 单元格内容存储

笔记本单元格存储结构信息与元数据，但可能不会捕获：

- **完整执行输出**：查询执行产生的大规模结果集
- **二进制附件**：嵌入在笔记本中的图片或文件（通过 URL 引用除外）
- **交互式组件**：笔记本中的动态 UI 元素，如 ipywidgets

其重点在于捕获笔记本的代码、结构与元数据，而非执行产物。

### 平台专属特性

不同的笔记本平台拥有一些可能无法完美映射到 DataHub 模型的独特特性：

- **Databricks**：协作特性、版本控制与作业调度
- **Hex**：应用构建特性与参数输入
- **Jupyter**：内核专属特性与扩展
- **Mode**：报表调度与共享配置

摄取连接器会捕获通用特性，而平台专属能力可能存储在 `customProperties` 中。

### 单元格顺序

`notebookContent` 的单元格数组会保留单元格在源笔记本中出现的顺序。不过，具有复杂分支逻辑或非线性执行流程的笔记本，可能无法被简单的有序列表完整表达。

### 版本控制

当前的笔记本模型并不原生跟踪笔记本版本或修订历史。`changeAuditStamps` 捕获了最后修改的信息，但完整的版本控制需要与源平台的版本系统集成（如 Jupyter 的 Git、Databricks 的平台版本历史）。

### 大型笔记本

包含数百个单元格的超大型笔记本可能存在性能方面的考虑：

- 摄取时间随笔记本体积增加
- UI 渲染可能针对笔记本元数据而非完整内容展示做了优化
- 考虑将极大型笔记本拆分为更小、更聚焦的笔记本，以便更好管理

## 使用场景

DataHub 中的笔记本支持若干重要使用场景：

1. **发现**：找到与特定数据集、业务领域或分析主题相关的笔记本
2. **文档化**：通过自文档化的笔记本代码了解数据是如何被分析与转换的
3. **血缘**：追踪基于笔记本的 ETL 与转换管道中的数据流
4. **协作**：识别特定分析的笔记本负责人与领域专家
5. **治理**：对基于笔记本的分析应用标签、术语与分类
6. **影响分析**：当笔记本所使用的数据集发生变化时，了解下游依赖
7. **知识管理**：保留嵌在分析笔记本中的机构知识

将笔记本纳入 DataHub 的元数据图谱后，组织便可以像对待生产数据资产一样，以同样的严谨度来管理分析代码。

> 本文为 DataHub 官方文档的中文翻译。原始页面末尾的 “Technical Reference Guide”（自动生成的 Aspects/字段参考表）仍为英文，未包含在本文中，可查阅 [原页面](09-notebook.md)。
