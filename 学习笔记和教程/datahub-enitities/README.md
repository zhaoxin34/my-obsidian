---
title: DataHub 元模型实体说明（中文翻译）
source: https://docs.datahub.com/docs/generated/metamodel/entities/
---

# DataHub 元模型实体说明（中文翻译）

DataHub 官方文档 [Metadata Model → Entities](https://docs.datahub.com/docs/generated/metamodel/entities/) 全部实体说明页面的中文翻译，共 71 篇。 全部实体说明页面的中文翻译，共 71 篇。

- **编号规则**：文件名 `序号-实体名.md`（如 `01-dataset.md`），序号与官方文档左侧边栏中实体的排列顺序一致，从 01 到 71。
- 每篇包含实体的标识（Identity）、核心能力、示例代码等；原始页面末尾由工具自动生成的 *Technical Reference Guide*（各 Aspect 与字段参考表）仍为英文，未翻译，可查[原页面](https://docs.datahub.com/docs/generated/metamodel/entities/)。。
- 文件 frontmatter 中 `order` 字段与序号一致，Obsidian 中可按该字段排序。

## 实体清单（按官方顺序）

| 序号 | 中文名 | 实体名 | 本地笔记 | 说明 |
| --- | --- | --- | --- | --- |
| 01 | 数据集 | `dataset` | [[01-dataset]] | 元数据模型中最重要的实体：库中的表/视图、流、数据湖文件与目录 |
| 02 | 角色 | `role` | [[02-role]] | 角色（权限主体） |
| 03 | 数据作业 | `datajob` | [[03-datajob]] | 数据处理任务（Spark、Airflow Task 等） |
| 04 | 数据流 | `dataflow` | [[04-dataflow]] | 数据流/管道，由有依赖关系的 DataJob 组成 |
| 05 | 数据处理 | `dataprocess` | [[05-dataprocess]] | 数据处理逻辑 |
| 06 | 数据处理实例 | `dataprocessinstance` | [[06-dataprocessinstance]] | 一次具体的数据处理运行实例 |
| 07 | 图表 | `chart` | [[07-chart]] | 由数据集衍生的单个可视化图表 |
| 08 | 仪表板 | `dashboard` | [[08-dashboard]] | 由多个图表组成的仪表板 |
| 09 | 笔记本 | `notebook` | [[09-notebook]] | 交互式笔记本 |
| 10 | 企业用户 | `corpuser` | [[10-corpuser]] | 企业用户 |
| 11 | 用户组 | `corpgroup` | [[11-corpgroup]] | 企业用户组 |
| 12 | 领域 | `domain` | [[12-domain]] | 业务域（主题分组） |
| 13 | 容器 | `container` | [[13-container]] | 容器（嵌套数据集/工作区） |
| 14 | 标签 | `tag` | [[14-tag]] | 附加在实体上的标签 |
| 15 | 术语表术语 | `glossaryterm` | [[15-glossaryterm]] | 业务术语 |
| 16 | 术语表节点 | `glossarynode` | [[16-glossarynode]] | 术语表层级节点 |
| 17 | 文档 | `document` | [[17-document]] | 文档实体 |
| 18 | 断言 | `assertion` | [[18-assertion]] | 数据质量断言 |
| 19 | 机器学习模型 | `mlmodel` | [[19-mlmodel]] | 机器学习模型 |
| 20 | 机器学习模型组 | `mlmodelgroup` | [[20-mlmodelgroup]] | 模型分组 |
| 21 | ML 模型部署 | `mlmodeldeployment` | [[21-mlmodeldeployment]] | 模型部署实例 |
| 22 | 机器学习特征表 | `mlfeaturetable` | [[22-mlfeaturetable]] | 特征表 |
| 23 | 机器学习特征 | `mlfeature` | [[23-mlfeature]] | 特征定义 |
| 24 | ML 主键 | `mlprimarykey` | [[24-mlprimarykey]] | 特征表主键 |
| 25 | 测试 | `test` | [[25-test]] | 测试用例 |
| 26 | 模式字段 | `schemafield` | [[26-schemafield]] | 模式中的字段 |
| 27 | 版本集 | `versionset` | [[27-versionset]] | 实体版本集合 |
| 28 | 事件（故障） | `incident` | [[28-incident]] | 事件/故障 |
| 29 | DataHub 角色 | `datahubrole` | [[29-datahubrole]] | DataHub 平台角色 |
| 30 | 帖子 | `post` | [[30-post]] | 帖子 |
| 31 | DataHub 视图 | `datahubview` | [[31-datahubview]] | DataHub 视图 |
| 32 | ER 模型关系 | `ermodelrelationship` | [[32-ermodelrelationship]] | ER 模型中的实体关系 |
| 33 | 查询 | `query` | [[33-query]] | 查询记录 |
| 34 | 数据产品 | `dataproduct` | [[34-dataproduct]] | 数据产品 |
| 35 | 应用 | `application` | [[35-application]] | 应用 |
| 36 | 语义模型 | `semanticmodel` | [[36-semanticmodel]] | 语义模型 |
| 37 | 指标 | `metric` | [[37-metric]] | 指标 |
| 38 | 所有权类型 | `ownershiptype` | [[38-ownershiptype]] | 所有权类型（技术/业务负责人等） |
| 39 | 生命周期阶段类型 | `lifecyclestagetype` | [[39-lifecyclestagetype]] | 生命周期阶段类型 |
| 40 | 业务属性 | `businessattribute` | [[40-businessattribute]] | 业务属性 |
| 41 | 数据契约 | `datacontract` | [[41-datacontract]] | 数据契约 |
| 42 | 实体类型 | `entitytype` | [[42-entitytype]] | 实体类型 |
| 43 | 数据类型 | `datatype` | [[43-datatype]] | 数据类型 |
| 44 | 结构化属性 | `structuredproperty` | [[44-structuredproperty]] | 结构化属性（自定义元数据） |
| 45 | 表单 | `form` | [[45-form]] | 表单 |
| 46 | DataHub 页面模板 | `datahubpagetemplate` | [[46-datahubpagetemplate]] | 页面模板 |
| 47 | 搜索模板 | `searchtemplate` | [[47-searchtemplate]] | 搜索模板 |
| 48 | DataHub 页面模块 | `datahubpagemodule` | [[48-datahubpagemodule]] | 页面模块 |
| 49 | DataHub 文件 | `datahubfile` | [[49-datahubfile]] | DataHub 文件 |
| 50 | 平台资源 | `platformresource` | [[50-platformresource]] | 平台侧资源对象 |
| 51 | 服务 | `service` | [[51-service]] | 服务 |
| 52 | AI Agent | `aiagent` | [[52-aiagent]] | AI 智能体 |
| 53 | API | `api` | [[53-api]] | API 端点 |
| 54 | 代码仓库 | `repository` | [[54-repository]] | 代码仓库 |
| 55 | 智能体技能 | `agentskill` | [[55-agentskill]] | 智能体技能 |
| 56 | 数据平台 | `dataplatform` | [[56-dataplatform]] | 数据平台（Hive、BigQuery 等） |
| 57 | DataHub 策略 | `datahubpolicy` | [[57-datahubpolicy]] | 访问策略 |
| 58 | DataHub 摄取源 | `datahubingestionsource` | [[58-datahubingestionsource]] | 摄取任务源 |
| 59 | DataHub 密钥 | `datahubsecret` | [[59-datahubsecret]] | 密钥 |
| 60 | DataHub 执行请求 | `datahubexecutionrequest` | [[60-datahubexecutionrequest]] | 执行请求 |
| 61 | DataHub 保留策略 | `datahubretention` | [[61-datahubretention]] | 数据保留策略 |
| 62 | 数据平台实例 | `dataplatforminstance` | [[62-dataplatforminstance]] | 数据平台实例 |
| 63 | 遥测 | `telemetry` | [[63-telemetry]] | 遥测数据 |
| 64 | DataHub 访问令牌 | `datahubaccesstoken` | [[64-datahubaccesstoken]] | 访问令牌 |
| 65 | DataHub 升级 | `datahubupgrade` | [[65-datahubupgrade]] | 升级任务 |
| 66 | 邀请令牌 | `invitetoken` | [[66-invitetoken]] | 邀请令牌 |
| 67 | 全局设置 | `globalsettings` | [[67-globalsettings]] | 全局设置 |
| 68 | DataHub 步骤状态 | `datahubstepstate` | [[68-datahubstepstate]] | 流程步骤状态 |
| 69 | DataHub 画像 | `datahubpersona` | [[69-datahubpersona]] | 用户画像 |
| 70 | DataHub 连接 | `datahubconnection` | [[70-datahubconnection]] | 数据源连接 |
| 71 | DataHub OpenAPI Schema | `datahubopenapischema` | [[71-datahubopenapischema]] | OpenAPI Schema |

## 相关链接

- 官方实体目录：<https://docs.datahub.com/docs/generated/metamodel/entities/>
- DataHub 元模型总览：<https://docs.datahub.com/docs/modeling/metadata-model>
