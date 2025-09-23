# PostgreSQL 数据库设计文档 v2.0

本文档定义了“观澜・深度传播分析平台”核心业务逻辑与数据暂存在PostgreSQL数据库中的表结构。

---

## 数据库表设计 (DDL)

```sql
-- 启用 pgcrypto 扩展以生成 UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建一个可重用的函数，用于在行更新时自动更新 updated_at 时间戳
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. 用户表 (Users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER set_timestamp BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- 2. 研究对象表 (Research Objects)
CREATE TABLE research_objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'MEDIA', 'PERSON', 'INSTITUTION', 'EVENT'
    description TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name, type)
);
CREATE TRIGGER set_timestamp BEFORE UPDATE ON research_objects FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- 3. 数据源表 (Data Sources)
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_object_id UUID NOT NULL REFERENCES research_objects(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'SOCIAL_ACCOUNT', 'WEBSITE', 'APP', etc.
    identifier TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (type, identifier)
);
CREATE TRIGGER set_timestamp BEFORE UPDATE ON data_sources FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- 4. 研究项目表 (Projects)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER set_timestamp BEFORE UPDATE ON projects FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- 5. 项目与对象的映射表 (Project-Object Mappings)
CREATE TABLE project_object_mappings (
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    object_id UUID NOT NULL REFERENCES research_objects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, object_id)
);

-- 6. 采集任务日志表 (Collection Jobs Log)
CREATE TABLE collection_jobs_log (
    id UUID PRIMARY KEY,
    data_source_id UUID NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL,
    task_mode VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'STARTED', 'COMPLETED', 'FAILED'
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    summary TEXT
);
CREATE INDEX idx_collection_jobs_log_data_source_id ON collection_jobs_log(data_source_id);

-- 7. 数据源元数据历史表 (Source Metadata History)
CREATE TABLE source_metadata_history (
    id BIGSERIAL PRIMARY KEY,
    data_source_id UUID NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    collection_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_payload JSONB NOT NULL
);
CREATE INDEX idx_source_metadata_history_data_source_id ON source_metadata_history(data_source_id);

-- 8. 内容条目原始数据表 (Content Items Raw)
CREATE TABLE content_items_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_source_id UUID NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    source_item_id VARCHAR(255) NOT NULL,
    publish_timestamp TIMESTAMPTZ,
    collection_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content_payload JSONB NOT NULL,
    etl_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'PROCESSED', 'FAILED'
    UNIQUE (data_source_id, source_item_id)
);
CREATE INDEX idx_content_items_raw_data_source_id ON content_items_raw(data_source_id);
CREATE INDEX idx_content_items_raw_etl_status ON content_items_raw(etl_status);

-- 9. 数据源元数据快照表 (Source Metadata Current)
-- 用于存储每个数据源当前最新的基础信息，提供高效的“最新状态”查询
CREATE TABLE source_metadata_current (
    -- 每个数据源在这里只有一条记录，因此data_source_id是主键
    data_source_id UUID PRIMARY KEY REFERENCES data_sources(id) ON DELETE CASCADE,
    -- 最新一次的采集时间
    collection_timestamp TIMESTAMPTZ NOT NULL,
    -- 最新的元数据
    metadata_payload JSONB NOT NULL
);

```

## 设计说明

1.  **主键策略:** 全部采用 `UUID` 作为主键（历史流水表除外），对未来系统扩展、分布式部署友好。

2.  **时间戳:** 全部使用 `TIMESTAMPTZ` (Timestamp with Time Zone)，避免任何时区问题。

3.  **数据完整性:** 通过外键约束 (`REFERENCES`) 和级联删除 (`ON DELETE CASCADE`) 保证核心实体之间的引用完整性。

4.  **唯一性约束:** 在`research_objects`, `data_sources`, `content_items_raw`等表上都建立了`UNIQUE`约束，从数据库层面保证了核心实体的唯一性。

5.  **自动更新时间戳:** 通过可重用的`trigger_set_timestamp`函数，实现了核心模型表在更新时自动更新`updated_at`字段。

6.  **快照与历史分离模式 (Snapshot & History Pattern):** 对于需要追踪其变化的数据（如`source_metadata`），我们都采用了“快照表 (`_current`) + 历史表 (`_history`)”的双表设计。快照表仅保存最新记录，用于高性能的当前状态查询；历史表保存所有采集记录，用于进行时间趋势分析。这确保了两种核心查询场景下的最佳性能。（注：内容数据的双表模式主要在ClickHouse分析层实现，PostgreSQL中的`content_items_raw`作为统一的原始数据着陆区）。

7.  **灵活性:** 核心数据存储表（`source_metadata_history`, `content_items_raw`等）使用`JSONB`字段来保存原始数据，这提供了极大的灵活性，未来即使分析需求变更，也无需重新采集数据。
