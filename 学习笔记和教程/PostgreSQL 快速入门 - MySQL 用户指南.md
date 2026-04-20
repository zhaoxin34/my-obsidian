# PostgreSQL 快速入门 - MySQL 用户指南

> 本教程专为熟悉 MySQL 并希望快速掌握 PostgreSQL 的命令行用户编写。

## 目录

- [1. 核心概念差异](#1-核心概念差异)
- [2. psql 基础入门](#2-psql-基础入门)
- [3. 常用命令对照表](#3-常用命令对照表)
- [4. 数据类型差异](#4-数据类型差异)
- [5. SQL 语法差异](#5-sql-语法差异)
- [6. 用户与权限管理](#6-用户与权限管理)
- [7. 数据导入导出](#7-数据导入导出)
- [8. PostgreSQL 特有功能](#8-postgresql-特有功能)
- [9. 快速参考卡片](#9-快速参考卡片)

---

## 1. 核心概念差异

### 1.1 架构对比

| 特性 | MySQL | PostgreSQL |
|------|-------|------------|
| **存储引擎** | 多引擎（InnoDB、MyISAM 等） | 统一引擎，可扩展 |
| **进程模型** | 每连接一个线程 | 多进程模型（postgres 进程） |
| **事务隔离** | READ COMMITTED、REPEATABLE READ、SERIALIZABLE | READ COMMITTED、READ COMMITTED、REPEATABLE READ、SERIALIZABLE、SNAPSHOT |
| **MVCC** | InnoDB 行级版本控制 | 完整 MVCC 实现 |

### 1.2 自动提交

```sql
-- MySQL: 自动提交默认开启
SET autocommit=0;
BEGIN;
-- statements
COMMIT;

-- PostgreSQL: 自动提交默认关闭（需显式 COMMIT）
BEGIN;
-- statements
COMMIT;
```

### 1.3 标识符大小写

- **MySQL**: 默认不敏感（Windows 下敏感）
- **PostgreSQL**: 默认敏感，单引号用于字符串，双引号用于标识符

```sql
-- PostgreSQL 字符串必须用单引号
SELECT 'hello';        -- 正确：字符串
SELECT "ColumnName";   -- 正确：标识符
```

---

## 2. psql 基础入门

### 2.1 连接数据库

```bash
# 基本连接
psql -d dbname

# 指定用户和主机
psql -U username -h hostname -d dbname -p 5432

# 连接后切换数据库
\c dbname
\conninfo  # 查看当前连接信息
```

### 2.2 退出 psql

```sql
\q
```

### 2.3 获取帮助

```sql
\?              -- psql 元命令帮助
\h SQL_COMMAND  -- SQL 命令帮助
```

---

## 3. 常用命令对照表

### 3.1 数据库操作

| 操作 | MySQL | PostgreSQL |
|------|-------|------------|
| 列出数据库 | `SHOW DATABASES;` | `\l` 或 `\list` |
| 创建数据库 | `CREATE DATABASE dbname;` | `CREATE DATABASE dbname;` |
| 删除数据库 | `DROP DATABASE dbname;` | `DROP DATABASE dbname;` |
| 使用数据库 | `USE dbname;` | `\c dbname` |
| 查看当前数据库 | `SELECT database();` | `SELECT current_database();` |

### 3.2 表操作

| 操作 | MySQL | PostgreSQL |
|------|-------|------------|
| 列出表 | `SHOW TABLES;` | `\dt` |
| 查看表结构 | `DESC table;` 或 `DESCRIBE table;` | `\d table` |
| 查看建表语句 | `SHOW CREATE TABLE table;` | `\d+ table`（含完整 SQL） |
| 查看详细表信息 | `SHOW TABLE STATUS;` | `\dt+` |
| 删除表 | `DROP TABLE table;` | `DROP TABLE table;` |
| 重命名表 | `RENAME TABLE t1 TO t2;` | `ALTER TABLE t1 RENAME TO t2;` |

### 3.3 索引操作

| 操作 | MySQL | PostgreSQL |
|------|-------|------------|
| 列出索引 | `SHOW INDEX FROM table;` | `\di` 或 `\d table` |
| 创建索引 | `CREATE INDEX idx ON t(col);` | `CREATE INDEX idx ON t(col);` |
| 删除索引 | `DROP INDEX idx;` | `DROP INDEX idx;` |
| 唯一索引 | `CREATE UNIQUE INDEX idx ON t(col);` | `CREATE UNIQUE INDEX idx ON t(col);` |

### 3.4 用户/角色操作

| 操作 | MySQL | PostgreSQL |
|------|-------|------------|
| 列出用户 | `SELECT user FROM mysql.user;` | `\du` |
| 创建用户 | `CREATE USER 'user'@'host';` | `CREATE USER user;` |
| 删除用户 | `DROP USER 'user'@'host';` | `DROP USER user;` |
| 修改密码 | `SET PASSWORD FOR 'user'@'host' = 'pwd';` | `ALTER USER user WITH PASSWORD 'pwd';` |
| 授予权限 | `GRANT ALL ON db.* TO 'user'@'host';` | `GRANT ALL ON DATABASE db TO user;` |

---

## 4. 数据类型差异

### 4.1 自增主键

**MySQL:**
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);
```

**PostgreSQL:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- 或 BIGSERIAL、SMALLSERIAL
    name VARCHAR(100)
);

-- 标准 SQL 语法也支持
CREATE TABLE users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);
```

> **注意**: PostgreSQL 的 SERIAL 底层创建了序列，可能出现"空洞"（事务回滚后序列值仍被占用）。

### 4.2 字符串类型

| MySQL | PostgreSQL | 说明 |
|-------|------------|------|
| `VARCHAR(255)` | `VARCHAR(255)` 或 `TEXT` | PostgreSQL TEXT 无长度限制 |
| `TEXT` | `TEXT` | 一致 |
| `CHAR(10)` | `CHAR(10)` | 定长，不足补空格 |
| `ENUM` | `ENUM` 或 `CHECK` | PostgreSQL 支持两种方式 |

### 4.3 数值类型

| MySQL | PostgreSQL | 说明 |
|-------|------------|------|
| `TINYINT` | `SMALLINT` | - |
| `INT` | `INT` 或 `INTEGER` | 一致 |
| `BIGINT` | `BIGINT` | 一致 |
| `FLOAT` | `REAL` | 单精度 |
| `DOUBLE` | `DOUBLE PRECISION` | 双精度 |
| `DECIMAL(10,2)` | `DECIMAL(10,2)` 或 `NUMERIC(10,2)` | PostgreSQL NUMERIC 更精确 |

### 4.4 日期时间类型

| MySQL | PostgreSQL | 说明 |
|-------|------------|------|
| `DATETIME` | `TIMESTAMP` | 日期时间 |
| `TIMESTAMP` | `TIMESTAMP WITH TIME ZONE` | 带时区 |
| `DATE` | `DATE` | 仅日期 |
| `TIME` | `TIME` | 仅时间 |
| 无 | `INTERVAL` | 时间间隔（PostgreSQL 特有） |

### 4.5 二进制数据

| MySQL | PostgreSQL |
|-------|------------|
| `BLOB` | `BYTEA` |

### 4.6 时间戳默认值

**MySQL:**
```sql
CREATE TABLE t (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**PostgreSQL:**
```sql
CREATE TABLE t (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- PostgreSQL 15+ 可用触发器实现 updated_at 自动更新
```

---

## 5. SQL 语法差异

### 5.1 字符串拼接

**MySQL:**
```sql
SELECT CONCAT('Hello', ' ', 'World');
SELECT 'Hello' + ' ' + 'World';  -- 隐式转换
```

**PostgreSQL:**
```sql
SELECT 'Hello' || ' ' || 'World';  -- 标准 SQL 语法
SELECT CONCAT('Hello', ' ', 'World');  -- 也支持
```

### 5.2 LIMIT 与分页

**MySQL:**
```sql
SELECT * FROM t LIMIT 10 OFFSET 20;
SELECT * FROM t LIMIT 20, 10;  -- 旧语法
```

**PostgreSQL:**
```sql
SELECT * FROM t LIMIT 10 OFFSET 20;
-- SQL:2008 标准语法
SELECT * FROM t OFFSET 20 FETCH FIRST 10 ROWS ONLY;
```

### 5.3 NULL 比较

> **危险**: MySQL 允许 `= NULL` 但结果总是 NULL，不会返回任何行！

**MySQL:**
```sql
-- 使用 <=> 做 NULL 安全比较
SELECT * FROM t WHERE col <=> NULL;
```

**PostgreSQL:**
```sql
-- 使用 IS DISTINCT FROM（推荐）
SELECT * FROM t WHERE col IS DISTINCT FROM NULL;
-- 或传统方式
SELECT * FROM t WHERE col IS NULL;
```

### 5.4 RETURNING 子句

PostgreSQL 特有：**在 INSERT/UPDATE/DELETE 后返回数据**

```sql
-- MySQL 需两次查询
INSERT INTO t (name) VALUES ('test');
SELECT LAST_INSERT_ID();

-- PostgreSQL 一步完成
INSERT INTO t (name) VALUES ('test') RETURNING id;
UPDATE t SET name = 'new' WHERE id = 1 RETURNING *;
DELETE FROM t WHERE id = 1 RETURNING *;
```

### 5.5 冲突处理 (Upsert)

**MySQL:**
```sql
INSERT INTO t (id, name) VALUES (1, 'a')
ON DUPLICATE KEY UPDATE name = 'a';
```

**PostgreSQL:**
```sql
INSERT INTO t (id, name) VALUES (1, 'a')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- 或简单忽略
INSERT INTO t (id, name) VALUES (1, 'a')
ON CONFLICT DO NOTHING;
```

### 5.6 EXPLAIN

```sql
-- MySQL
EXPLAIN sql_statement;

-- PostgreSQL（更详细）
EXPLAIN ANALYZE sql_statement;  -- 含实际执行时间
```

---

## 6. 用户与权限管理

### 6.1 创建用户与授权

```sql
-- 创建用户
CREATE USER myuser WITH PASSWORD 'mypassword';

-- 授予数据库权限
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

-- 授予表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO myuser;

-- 授予序列权限（自增主键需要）
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO myuser;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO myuser;
```

### 6.2 常用权限类型

| 权限 | 说明 |
|------|------|
| `SELECT` | 读取数据 |
| `INSERT` | 插入数据 |
| `UPDATE` | 更新数据 |
| `DELETE` | 删除数据 |
| `TRUNCATE` | 清空表 |
| `REFERENCES` | 外键引用 |
| `TRIGGER` | 创建触发器 |
| `CONNECT` | 连接数据库 |
| `TEMPORARY` | 创建临时表 |

---

## 7. 数据导入导出

### 7.1 执行 SQL 文件

```sql
-- MySQL
SOURCE /path/to/file.sql;

-- PostgreSQL
\i /path/to/file.sql
```

### 7.2 导出数据到 CSV

```sql
-- PostgreSQL psql 客户端命令（客户端执行）
\copy table TO '/tmp/data.csv' WITH (FORMAT csv, HEADER);

-- PostgreSQL SQL COPY 命令（服务器端执行，需超级用户）
COPY table TO '/tmp/data.csv' WITH (FORMAT csv, HEADER);
```

### 7.3 导入 CSV 数据

```sql
-- psql 客户端命令
\copy table FROM '/tmp/data.csv' WITH (FORMAT csv, HEADER);

-- SQL COPY 命令（服务器端）
COPY table FROM '/tmp/data.csv' WITH (FORMAT csv, HEADER);
```

> **区别**: `\copy` 是 psql 客户端命令，数据通过客户端传输；`COPY` 是 SQL 命令，数据在服务器端文件与数据库间传输。

---

## 8. PostgreSQL 特有功能

### 8.1 psql 扩展显示模式

```sql
\x  -- 切换扩展显示（竖排显示结果）
\x auto  -- 自动判断（超过列宽时竖排）
```

### 8.2 执行时间统计

```sql
\timing  -- 开启/关闭执行时间显示
SELECT * FROM big_table;
\timing
```

### 8.3 数组类型

PostgreSQL 原生支持数组：

```sql
CREATE TABLE sal_emp (
    name            text,
    pay_by_quarter  integer[]
);

INSERT INTO sal_emp VALUES ('Bill', ARRAY[10000, 10000, 10000]);

-- 查询包含特定值的数组元素
SELECT * FROM sal_emp WHERE 10000 = ANY (pay_by_quarter);
```

### 8.4 JSON/JSONB 类型

PostgreSQL 的 JSONB 是二进制格式，性能优于 MySQL 的 JSON：

```sql
CREATE TABLE t (data JSONB);
INSERT INTO t VALUES ('{"name": "test", "age": 30}');

-- 提取字段
SELECT data->>'name' FROM t;  -- 返回文本
SELECT data->'name' FROM t;   -- 返回 JSON

-- 包含查询（PostgreSQL 特有）
SELECT * FROM t WHERE data @> '{"name": "test"}';
```

### 8.5 物化视图

```sql
CREATE MATERIALIZED VIEW mv AS SELECT * FROM t;
REFRESH MATERIALIZED VIEW mv;
```

### 8.6 窗口函数

```sql
SELECT row_number() OVER (PARTITION BY col1 ORDER BY col2) FROM t;
SELECT sum(amount) OVER (ORDER BY date) FROM t;
```

### 8.7 通用表表达式 (CTE)

```sql
WITH RECURSIVE cte AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 10
) SELECT * FROM cte;
```

---

## 9. 快速参考卡片

### 9.1 常用元命令速查

```
数据库操作
  \l                    列出所有数据库
  \c dbname             切换数据库
  \conninfo             查看当前连接信息

表操作
  \dt                   列出所有表
  \d table              描述表结构
  \d+ table             详细表信息（含索引、注释）
  \dt+                  表详细信息

对象操作
  \di                   列出所有索引
  \df                   列出所有函数
  \dv                   列出所有视图
  \ds                   列出所有序列
  \dn                   列出所有 schema

用户/角色
  \du                   列出所有用户/角色

输出控制
  \x                    切换扩展显示模式
  \timing               开启/关闭执行时间
  \o file.txt           输出到文件
  \i file.sql           执行 SQL 文件
  \e                    编辑查询（外部编辑器）
```

### 9.2 快速对照速记

| 记忆法 | MySQL | PostgreSQL |
|--------|-------|------------|
| 退出 | `quit` 或 `exit` | `\q` |
| 列出 | `SHOW DATABASES` | `\l` |
| 切换 | `USE db` | `\c db` |
| 表 | `SHOW TABLES` | `\dt` |
| 结构 | `DESC table` | `\d table` |
| 索引 | `SHOW INDEX` | `\di` |
| 用户 | `mysql.user` | `\du` |
| 执行 | `SOURCE file` | `\i file` |
| 导出 | `INTO OUTFILE` | `\copy TO` |
| 导入 | `LOAD DATA` | `\copy FROM` |
| 时长 | `BENCHMARK` | `\timing` |

---

## 下一步学习

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/current/)
- [psql 完整参考](https://www.postgresql.org/docs/current/app-psql.html)
- [PostgreSQL vs MySQL 对比](https://www.digitalocean.com/community/tutorials/mysql-vs-postgresql)

---

*最后更新: 2026-04-20*
