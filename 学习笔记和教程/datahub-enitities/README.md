---
title: DataHub 元模型实体说明（中文翻译）
source: https://docs.datahub.com/docs/generated/metamodel/entities/
---

# DataHub 元模型实体说明（中文翻译）

本文档是 DataHub 官方文档 [Metadata Model → Entities](https://docs.datahub.com/docs/generated/metamodel/entities/) 全部实体说明页面的中文翻译。

每篇笔记对应一个实体，文件名为英文实体名，内容包含：实体的身份标识（Identity）、核心能力（Capabilities）、示例代码等。原始页面末尾由工具自动生成的 “Technical Reference Guide”（各 Aspect 与字段的参考表）仍为英文，未翻译，可查阅[原页面](https://docs.datahub.com/docs/generated/metamodel/entities/)。

## 核心数据资产实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 数据集 Dataset | [[dataset]] | 最重要的实体，数据库中的表/视图、流处理中的流、数据湖中的文件与目录 |
| 数据产品 DataProduct | [[dataproduct]] | 面向业务消费的数据资产集合 |
| 数据契约 DataContract | [[datacontract]] | 数据质量与消费约定 |
| 数据流 DataFlow | [[dataflow]] | 数据在系统间的流转 |
| 数据任务 DataJob | [[datajob]] | 产出数据的任务（Spark、Airflow 等） |
| 数据处理 DataProcess | [[dataprocess]] | 数据处理逻辑 |
| 数据处理实例 DataProcessInstance | [[dataprocessinstance]] | 一次具体的数据处理运行 |
| 数据流图 DataFlowNode | — | 见 [[dataflow]] |

## 平台与数据模型实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 数据平台 DataPlatform | [[dataplatform]] | 托管数据资产的技术平台（Hive、BigQuery、Snowflake 等） |
| 数据平台实例 DataPlatformInstance | [[dataplatforminstance]] | 同一平台的具体部署实例 |
| 数据类型 DataType | [[datatype]] | 类型定义 |
| 模式字段 SchemaField | [[schemafield]] | 模式中的字段 |
| 平台资源 PlatformResource | [[platformresource]] | 平台侧的资源对象 |

## 治理与分类实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 业务域 Domain | [[domain]] | 业务领域的分组 |
| 标签 Tag | [[tag]] | 附加在实体上的标签 |
| 术语 GlossaryTerm | [[glossaryterm]] | 业务术语 |
| 术语节点 GlossaryNode | [[glossarynode]] | 术语表的层级节点 |
| 结构化属性 StructuredProperty | [[structuredproperty]] | 自定义的结构化元数据 |
| 所有权类型 OwnershipType | [[ownershiptype]] | 所有者分类（技术/业务/数据 steward 等） |
| 生命周期阶段类型 LifecycleStageType | [[lifecyclestagetype]] | 生命周期阶段（生产、测试等） |
| 断言 Assertion | [[assertion]] | 数据质量断言 |
| 版本集 VersionSet | [[versionset]] | 实体的版本集合 |

## 机器学习实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 模型 MLModel | [[mlmodel]] | 机器学习模型 |
| 模型组 MLModelGroup | [[mlmodelgroup]] | 模型分组 |
| 模型部署 MLModelDeployment | [[mlmodeldeployment]] | 模型的部署实例 |
| 特征 MLFeature | [[mlfeature]] | 特征定义 |
| 特征表 MLFeatureTable | [[mlfeaturetable]] | 特征表 |
| 主键 MLPrimaryKey | [[mlprimarykey]] | 特征表主键 |

## 应用与消费实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 仪表板 Dashboard | [[dashboard]] | 仪表板 |
| 图表 Chart | [[chart]] | 仪表板中的图表 |
| 笔记本 Notebook | [[notebook]] | 交互式笔记本 |
| 查询 Query | [[query]] | 查询记录 |
| 表单 Form | [[form]] | 表单 |
| 应用 Application | [[application]] | 应用 |
| API | [[api]] | API 端点 |
| 服务 Service | [[service]] | 服务 |
| 仓库 Repository | [[repository]] | 代码仓库 |
| 文档 Document | [[document]] | 文档 |
| 帖子 Post | [[post]] | 帖子 |

## 组织与人员实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 企业用户 CorpUser | [[corpuser]] | 企业成员 |
| 企业用户组 CorpGroup | [[corpgroup]] | 用户组 |
| 角色 Role | [[role]] | 角色 |
| 指标 Metric | [[metric]] | 指标 |
| 业务属性 BusinessAttribute | [[businessattribute]] | 业务属性 |
| ER 模型关系 ERModelRelationship | [[ermodelrelationship]] | 实体关系模型中的关系 |
| 事件 Incident | [[incident]] | 事件/事故 |
| 实体类型 EntityType | [[entitytype]] | 实体类型定义 |

## AI 与 Agent 实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| AI 智能体 AIAgent | [[aiagent]] | AI 智能体 |
| Agent 技能 AgentSkill | [[agentskill]] | 智能体技能 |

## DataHub 平台自身实体

| 实体 | 文件 | 说明 |
| --- | --- | --- |
| 全局设置 GlobalSettings | [[globalsettings]] | 全局设置 |
| 访问令牌 DataHubAccessToken | [[datahubaccesstoken]] | 访问令牌 |
| 邀请令牌 InviteToken | [[invitetoken]] | 邀请令牌 |
| 连接 DataHubConnection | [[datahubconnection]] | 数据源连接 |
| 执行请求 DataHubExecutionRequest | [[datahubexecutionrequest]] | 执行请求 |
| 文件 DataHubFile | [[datahubfile]] | 文件 |
| 摄取源 DataHubIngestionSource | [[datahubingestionsource]] | 摄取任务源 |
| OpenAPI Schema DataHubOpenApiSchema | [[datahubopenapischema]] | OpenAPI 描述 |
| 页面模块 DataHubPageModule | [[datahubpagemodule]] | 页面模块 |
| 页面模板 DataHubPageTemplate | [[datahubpagetemplate]] | 页面模板 |
| 角色画像 DataHubPersona | [[datahubpersona]] | 用户画像 |
| 策略 DataHubPolicy | [[datahubpolicy]] | 访问策略 |
| 保留策略 DataHubRetention | [[datahubretention]] | 数据保留策略 |
| 角色 DataHubRole | [[datahubrole]] | 平台角色 |
| 密钥 DataHubSecret | [[datahubsecret]] | 密钥 |
| 步骤状态 DataHubStepState | [[datahubstepstate]] | 流程步骤状态 |
| 升级 DataHubUpgrade | [[datahubupgrade]] | 升级任务 |
| 视图 DataHubView | [[datahubview]] | 视图 |
| 搜索模板 SearchTemplate | [[searchtemplate]] | 搜索模板 |
| 遥测 Telemetry | [[telemetry]] | 遥测数据 |
| 测试 Test | [[test]] | 测试用例 |

## 相关链接

- 官方文档：<https://docs.datahub.com/docs/generated/metamodel/entities/>
- DataHub 元模型总览：<https://docs.datahub.com/docs/metadata-model/>
