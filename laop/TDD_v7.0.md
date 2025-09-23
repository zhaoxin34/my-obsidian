### **技术设计文档 (TDD): 观澜・深度传播分析平台**

*   **版本:** 7.0 (最终完整版)
*   **日期:** 2025年9月13日
*   **关联文档:** `PRD_v4.0.md`, `PDD_v3.0.md`

---

#### **1. 概述 (Overview)**
本文档旨在为“观澜・深度传播分析平台”第一个版本提供全面的技术设计方案。它将作为后续开发、测试和运维工作的核心技术指导。本文档基于最新的“项目-对象-数据源”三层架构思想，对系统的核心数据模型、服务交互和技术实现进行了详细的阐述。

#### **2. 核心设计思想 (Core Design Philosophy)**
为构建一个真正灵活、高效、可扩展的平台，我们确立了以“**研究对象**”为中心的三层信息结构：**研究项目(Project) -> 研究对象(Object) -> 数据源(Source)**。此设计的核心优势在于：

*   **1. 实体与研究的分离:** 清晰地将“**研究行为**”（由“研究项目”代表）与“**被研究的实体**”（由“研究对象”代表）分离开来。一个“研究对象”（如“A媒体”）可以被多个不同的“研究项目”复用。
*   **2. 可复用性与协作:** “研究对象”是平台级的、唯一的、可被所有用户搜索和复用的实体。这避免了重复定义，并将平台构建为一个**可成长的、协作式的知识库**。
*   **3. 采集效率的大幅提升:** 系统只需对平台唯一的“数据源”采集一次，即可将数据服务于所有引用了该数据源的项目，极大地节省了系统资源。
*   **4. 更强的扩展性与灵活性:** 能轻松应对“单一对象深度分析”和“多对象横向对比”等各类复杂研究场景。

#### **3. 系统架构 (System Architecture)**

##### **3.1 架构理念**
采用“**分层+微服务**”的架构。在逻辑上分为表现层（前端）、应用层（后端API）、数据处理层（采集、ETL）和数据存储层，在物理实现上，核心模块将作为可独立部署的微服务，通过明确的API和消息队列进行通信。

##### **3.2 核心服务模块**
*   **Web前端 (Frontend):** 用户交互的界面，负责数据可视化和用户操作。
*   **应用后端/API服务 (Backend/API Service):** 系统的“大脑”。负责处理用户请求、管理项目/对象/数据源的关系、用户身份认证与权限控制，并协调其他后台服务。
*   **采集调度服务 (Collector Dispatcher):** 核心的“任务中心”。根据配置生成采集任务，并智能地进行任务去重，然后将任务分发至Kafka。
*   **采集执行器集群 (Collector Executors):** 实际执行数据采集的工作节点集群，不同类型的采集器订阅不同的任务主题。
*   **ETL服务 (ETL Service):** 负责将采集到的原始数据进行清洗、转换、加载到最终的分析数据库中。

##### **3.3 技术选型 (Technology Stack)**
*   **Web前端:** **Vue.js**。不限定为单页应用(SPA)模式，可根据需要采用多页(MPA)或服务端渲染(SSR)等模式。
*   **应用后端/API服务:** **Java** 或 **Python**。
*   **采集执行器:** 以 **Python** 为主。
*   **消息队列:** **Apache Kafka**。
*   **数据库:**
    *   **PostgreSQL:** 主业务数据库，存储用户、项目、对象、数据源等核心关系模型。
    *   **ClickHouse:** 核心数据仓库和OLAP分析引擎，存储所有采集和处理后的数据。
*   **容器化:** **Docker**。
*   **容器编排:** **待定**。Kubernetes (K8s) 是首选方案，但最终方案需进一步讨论评估。

#### **4. 数据架构与核心模型设计 (Data Architecture & Core Model Design)**

##### **4.1 核心实体关系模型 (E-R Model)**
1.  **`projects` (研究项目):** `(project_id, name, description, user_id, ...)`
2.  **`research_objects` (研究对象):** `(object_id, name, type, description, ...)`
    *   **`type`字段枚举值:** `MEDIA`, `PERSON`, `INSTITUTION`, `EVENT`
3.  **`data_sources` (数据源):** `(source_id, object_id, type, identifier, ...)`
    *   **`type`字段枚举值:** `SOCIAL_ACCOUNT`, `WEBSITE`, `APP`, `GAME`, `VIDEO`, `MOVIE`, `KEYWORD`
    *   数据源覆盖：
        *   SOCIAL_ACCOUNT（Facebook、Twitter、YouTube、TikTok、Instagram）
        *   WEBSITE（几家国内新闻网站）
4.  **`project_object_mappings`:** `(project_id, object_id)` - 多对多关系映射表。

##### **4.2 采集任务定义 (Collector Job Definition)**
标准的、基于JSON的采集任务消息格式：
*   **核心字段详解:**
    *   **`job_id`**: `string` - **单次采集任务运行实例的唯一ID**。其核心作用是日志记录与端到端追踪。
    *   **`research_object_id`**: `string` - 核心关联字段，指明为哪个“研究对象”采集。
    *   **`data_source_id`**: `string` - 核心关联字段，指明为哪个“数据源”采集。
    *   **`target`**: `object` - `{type, identifier}`，采集目标的具体信息。
    *   **`task`**: `object` - `{type, mode, parameters}`，具体的任务描述。
    *   **`timestamp`**: `datetime` - 任务创建时间。
    *   **`project_id`**: `string` (可选) - 触发本次任务调度的上下文项目ID。
*   **`data_source_id`的设计哲学:** 采用代理键以保证**稳定性**（标识符可修改）和**性能**（JOIN效率高）。
*   **`task.parameters` 结构示例:**
    *   内容采集 (`HISTORICAL_BACKFILL`): `{"start_date": "...", "end_date": "..."}`
    *   内容采集 (`ONGOING_UPDATE`): `{"since_id": "..."}` (可选)
    *   元数据采集: `{}` (通常为空)
    *   关键词采集: `{"search_scope": [...], "language": "..."}` (可选)

##### **4.3 采集任务与研究项目的关联**
采集任务与研究项目是**间接关联**的，其关系链为：`项目` <-- `映射表` --> `对象` --> `数据源` --> `任务`。

##### **4.4 数据存储策略：混合模型 (Hybrid Model)**
采用“**专表存储 + 统一视图**”的混合模型。
*   **专表存储:** 为不同结构的数据源（社交媒体、新闻、App评论等）建立不同的物理表（如`fact_social_posts`, `fact_web_articles`），每张表都将遵循“快照+历史”的双表模式。
*   **统一视图:** 在ClickHouse中创建`view_all_content`视图，通过`UNION ALL`聚合所有专表中的通用字段，以支持便捷的跨源搜索。

##### **4.5 核心库表设计：快照与历史**
*   **快照表 (`_current`):** 使用ClickHouse的`ReplacingMergeTree`引擎，以源平台唯一ID为主键，存储每个内容条目的最新状态，用于快速查询。
*   **历史表 (`_history`):** 使用标准的`MergeTree`引擎，完整保留每一次采集的数据流水，并附加`collection_timestamp`字段，用于历史趋势分析。

#### **5. 核心服务设计详述**

##### **5.1 应用后端/API服务 (Backend/API Service)**
负责`projects`, `research_objects`, `data_sources`及其映射关系的CRUD，并提供权限控制和搜索服务。

##### **5.2 采集调度服务 (Collector Dispatcher)**
根据`data_sources`表的配置，周期性地生成采集任务，并基于`data_source_id`去重后，推送到Kafka指定的Topic。

##### **5.3 ETL服务**
消费Kafka中的原始数据，解析后，根据消息中的ID将数据`UPSERT`到对应的`_current`快照表，并`INSERT`到`_history`历史表中。

##### **5.4 采集执行器集群 (Collector Executors)**
*   **职责:** 订阅特定Kafka Topic，解析任务JSON，执行采集，并将结果推送到下游Topic。
*   **实现:** 将现有Python脚本重构为标准化的、可容器化的服务。并补充一个基于Scrapy等框架的“通用网站采集框架”。

#### **6. 关键技术挑战与方案**
*   **跨平台内容匹配:** 采用“URL强匹配 + 文本相似度弱匹配”的多阶段策略。
*   **高可用采集与反爬虫:** 建立动态代理IP池；维护User-Agent池；在调度中加入失败重试和指数退避机制。
*   **数据一致性:** 利用Kafka的at-least-once语义和ETL服务的幂等性设计来保证最终一致性。

#### **7. 可测试性与监控 (Testability & Monitoring)**
*   **独立测试:** 每个微服务都应能够脱离其他服务独立运行和测试。
*   **标准化监控:** 每个服务需通过`/health`端点暴露健康状态，并通过Prometheus上报核心业务指标。
*   **日志中心:** 所有服务日志聚合到ELK/Loki等系统中，便于统一查询和告警。

#### **8. 部署与运维 (Deployment & Operations)**
*   **容器化:** 所有服务均以**Docker**容器方式构建。
*   **部署方案:** 部署方案待定，初期可采用`docker-compose`在单机或少数几台服务器上部署，待业务规模扩大后，再评估迁移到**Kubernetes**集群的必要性和时机。