# ==================== postgres 监控配置（Prometheus + Grafana）====================

> 适用项目：`/Volumes/data/working/docker`（`busi` + `monitor` 两个 docker-compose）
> 服务：`busi/postgres`（pgvector/pgvector:pg16）→ `busi/postgres-exporter` → `monitor/prometheus` → `monitor/grafana`
> 实施日期：2026-09-03

---

## 背景

`busi` 工程里有 `postgres` 容器（pgvector/pgvector:pg16）已经跑业务数据。之前没有任何监控，
只能靠 `docker logs` 排错。`monitor` 工程（`prometheus + grafana + cadvisor`）已经搭起来，
但只监控了容器资源（cAdvisor），**看不到 postgres 内部指标**（连接数、QPS、缓存命中率等）。

> postgres 自身的指标（连接、查询、锁、复制、vacuum 等）需要 `postgres_exporter` 导出为 Prometheus 格式，
> 才能被 prometheus 抓取。`prometheus-community/postgres-exporter` 是社区标准实现。

---

## 目标

在 `monitor/grafana` 上看到 `PostgreSQL Overview` dashboard，包含：
- 活跃连接数 / 各库的连接数
- 所有库的总大小
- 每秒事务（commit/rollback）
- 缓存命中率
- 行操作速率（fetched / inserted / updated / deleted）
- 锁 / 死锁
- 最大连接数配置

> 访问入口：经过 `busi/nginx` 反代，`http://grafana.local`（需要 `busi` 工程的 nginx + monitor_default 网络已就绪）。

---

## 前置条件

- ✅ `busi` 工程已运行（`docker compose ps` 看到 `postgres` 是 Up + healthy）
- ✅ `monitor` 工程已运行（`prometheus` / `grafana` / `cadvisor` 都 Up）
- ✅ `busi` 工程的 nginx 已加入 `monitor_default` 网络（之前 `claudemem.local` / `openclaw.local` 的反代用同一套机制）
- ✅ `busi/postgres` 容器可以 exec 进去执行 psql

> ⚠️ 关键前置（不在前面列表）：`busi` 工程**没有**独立 `/etc/hosts`，但 `macOS` 自带
> `*.local` 域名的 fallback 解析（解析不到走 loopback），所以 `curl http://grafana.local` 能到 nginx。

---

## 架构

```
busi 工程:                                monitor 工程:
┌────────────────────┐                   ┌─────────────────────┐
│  postgres          │                   │  prometheus         │
│  (pgvector)        │                   │  (已有)             │
│      ↑             │                   │      ↑              │
│  postgres-exporter │─monitor_default──→│      │              │
│  (新加)            │  (external: true) │      │              │
└────────────────────┘                   │  grafana (已有)     │
        │                                 │      ↑              │
        └─ busi_default (默认)            │      │              │
                                          │  cadvisor (已有)    │
                                          └─────────────────────┘

busi 顶层 networks 已经声明了 monitor_default 为 external
```

**关键设计**：
- `postgres-exporter` 放 busi 工程（跟 postgres 同 docker network，连接最简单）
- `prometheus` 在 monitor 工程，通过 `monitor_default` external 网络连到 exporter
- 这两个工程是独立的 compose，靠 `monitor_default` 这个 external network 互通

---

## 实施步骤

### 1. 在 postgres 里建专用监控 user

**最小权限原则**：`postgres_exporter` 只需要 `pg_read_all_stats` 这个 role。

```bash
docker exec postgres psql -U postgres -c \
  "CREATE USER postgres_exporter WITH PASSWORD 'monitor_pass_2026';"
docker exec postgres psql -U postgres -c \
  "GRANT pg_read_all_stats TO postgres_exporter;"
docker exec postgres psql -U postgres -c \
  "ALTER USER postgres_exporter SET SEARCH_PATH TO postgres_exporter, public;"
docker exec postgres psql -U postgres -c \
  "GRANT CONNECT ON DATABASE postgres TO postgres_exporter;"
```

**验证**：
```bash
docker exec postgres psql -U postgres_exporter -d postgres -c "SELECT version();"
# 应该返回 PostgreSQL 版本（不报密码错或权限错）
```

### 2. 在 `busi/postgres/initdb.d/` 写持久化 SQL（给未来重建用）

**文件**：`busi/postgres/initdb.d/10-exporter-user.sql`

```sql
-- 10-exporter-user.sql
-- 为 prometheus postgres_exporter 创建专用监控账号
-- 此文件只在 postgres 第一次初始化（空数据卷）时执行
-- 存量数据卷请用 make exporter-user-bootstrap 手动执行（见 busi/postgres/Makefile）

CREATE USER postgres_exporter WITH PASSWORD 'monitor_pass_2026';
GRANT pg_read_all_stats TO postgres_exporter;
GRANT CONNECT ON DATABASE postgres TO postgres_exporter;
ALTER USER postgres_exporter SET SEARCH_PATH TO postgres_exporter, public;
```

> `initdb.d` 是 docker-entrypoint-initdb.d 的挂载，**只在空数据卷初始化时跑**。
> 已有数据的卷不会自动跑，所以步骤 1 必须手动执行。

### 3. 在 `busi/postgres/Makefile` 加存量数据卷的 bootstrap target

```makefile
exporter-user-bootstrap: ## 存量数据卷: 创建 prometheus postgres_exporter 账号
	docker exec -i postgres psql -U postgres -d postgres -f - < ./initdb.d/10-exporter-user.sql
```

将来重建数据卷时 `make exporter-user-bootstrap` 一次性跑完。

### 4. 在 `busi/docker-compose.yml` 加 `postgres-exporter` 服务

```yaml
postgres-exporter:
  # prometheus postgres_exporter - 导出 postgres 指标
  # 同时连 busi_default (连 postgres) 和 monitor_default (让 prometheus scrape)
  # 初始化用户见 ./postgres/initdb.d/10-exporter-user.sql
  # 存量数据卷手动执行 make exporter-user-bootstrap (在 busi/postgres/ 目录下)
  image: quay.io/prometheuscommunity/postgres-exporter:v0.15.0
  container_name: postgres-exporter
  restart: always
  environment:
    - DATA_SOURCE_URI=postgres:5432/postgres?sslmode=disable
    - DATA_SOURCE_USER=postgres_exporter
    - DATA_SOURCE_PASS=monitor_pass_2026
  networks:
    - default
    # 让 monitor 工程的 prometheus 能 scrape 到
    # busi 顶层 networks 已经把 monitor_default 声明为 external
    - monitor_default
```

`busi` 顶层 `networks` 块已经有 `monitor_default: external: true`（之前给 nginx 加的），不用再改。

### 5. 在 `monitor/prometheus/prometheus.yml` 加 scrape job

```yaml
# postgres_exporter (busi 工程, 通过 monitor_default 网络连入)
- job_name: 'postgres'
  static_configs:
    - targets: ['postgres-exporter:9187']
```

### 6. 启动 `busi` 工程的 exporter

```bash
cd /Volumes/data/working/docker/busi
docker compose up -d postgres-exporter
sleep 5

# 验证 exporter 暴露 pg_* 指标
docker exec postgres-exporter wget -q -O- http://localhost:9187/metrics | grep -E "^pg_" | head -5
# 应该看到 pg_database_size_bytes, pg_stat_activity_count 等
```

### 7. 重启 `monitor` 工程的 prometheus 让它 reload scrape config

```bash
cd /Volumes/data/working/docker/monitor
docker compose restart prometheus
sleep 5

# 验证 scrape target 是 up
docker exec prometheus wget -q -O- http://localhost:9090/api/v1/targets | \
  python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"{t['labels']['job']}: {t['health']}\") for t in d['data']['activeTargets']]"
# 应该看到 postgres: up
```

### 8. Grafana 准备：datasource provisioning

**文件**：`monitor/grafana/provisioning/datasources/datasource.yml`

> ⚠️ **不要**命名成 `prometheus.yml`——pi-lens 的 prometheus language server 会把同名文件当
> prometheus 配置校验，会报 `apiVersion` / `datasources` 是非法字段（实际是 Grafana provisioning 格式）。
> 用任意其他名字即可（`datasource.yml` / `datasource.yaml` 都行）。

```yaml
---
# Grafana datasource provisioning (不是 prometheus.yml, 不要按 prometheus schema 校验)
# yaml-language-server: $schema=
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    # 通过 monitor_default docker network 用容器名访问
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
```

### 9. Grafana 准备：dashboard 文件（先放着，步骤 10 用 API 导入）

**文件**：`monitor/grafana/dashboards/postgres.json`

10 个 panel 的自定义 dashboard，所有 query 都用 `instance="..."`（**不要**用 `release="..."`，
那是老的 `wrouesnel/postgres_exporter` 才有的 label，新版 `prometheuscommunity/postgres_exporter` 没有）：

```json
{
  "id": null,
  "uid": "pg-overview-v2",
  "title": "PostgreSQL Overview",
  "schemaVersion": 39,
  "templating": {
    "list": [
      {
        "name": "instance", "type": "query", "datasource": "Prometheus",
        "query": "label_values(pg_up, instance)", "refresh": 1
      },
      {
        "name": "datname", "type": "query", "datasource": "Prometheus",
        "query": "label_values(pg_stat_database_numbackends{instance=~\"$instance\"}, datname)",
        "refresh": 1, "includeAll": true, "multi": true
      }
    ]
  },
  "panels": [
    {
      "id": 1, "type": "stat", "title": "Active Connections",
      "datasource": "Prometheus",
      "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
      "targets": [
        {"expr": "sum(pg_stat_activity_count{instance=~\"$instance\", state=\"active\"})", "refId": "A"}
      ]
    },
    {
      "id": 2, "type": "timeseries", "title": "Connections by Database",
      "datasource": "Prometheus",
      "gridPos": {"x": 6, "y": 0, "w": 18, "h": 8},
      "targets": [
        {"expr": "sum by (datname) (pg_stat_activity_count{instance=~\"$instance\"})",
         "legendFormat": "{{datname}}", "refId": "A"}
      ]
    }
    /* ... 其余 8 个 panel 见 monitor/grafana/dashboards/postgres.json ... */
  ]
}
```

完整 JSON 在仓库里，不在此处复述。

### 10. Grafana dashboard provisioning（**绕开 Grafana 11.4 bug**）

**不要**用 dashboard provider provisioning（详见"问题 2"），改用 **HTTP API** 手动导入：

```bash
# 把 dashboard JSON 转成 API 需要的格式
cat /Volumes/data/working/docker/monitor/grafana/dashboards/postgres.json | \
  python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('id', None)
print(json.dumps({'dashboard': d, 'overwrite': True, 'message': 'manual import'}))
" > /tmp/dashboard-import.json

# 容器内用 wget 调 API（admin 密码见"关键信息"）
docker cp /tmp/dashboard-import.json grafana:/tmp/dashboard-import.json
docker exec grafana wget -q -O- --timeout=10 \
  --header='Authorization: Basic YWRtaW46YWJjMTIz' \
  --header='Content-Type: application/json' \
  --post-file=/tmp/dashboard-import.json \
  'http://localhost:3000/api/dashboards/db'

# 返回: {"folderUid":"","id":2,"slug":"postgresql-overview","status":"success",
#         "uid":"pg-overview-v2","url":"/d/pg-overview-v2/postgresql-overview","version":1}
```

**关键**：`YWRtaW46YWJjMTIz` 是 `admin:abc123` 的 base64。

### 11. 验证一切正常

```bash
# prometheus targets 都 up
docker exec prometheus wget -q -O- http://localhost:9090/api/v1/targets | \
  python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"{t['labels']['job']}: {t['health']}\") for t in d['data']['activeTargets']]"
# 期望: cadvisor: up, postgres: up, prometheus: up

# Grafana datasource
docker exec grafana wget -q -O- --header='Authorization: Basic YWRtaW46YWJjMTIz' \
  'http://localhost:3000/api/datasources' | python3 -c "import sys, json; print(json.load(sys.stdin))"
# 期望: [{"name":"Prometheus", "type":"prometheus", "url":"http://prometheus:9090", ...}]

# Grafana dashboard
docker exec grafana wget -q -O- --header='Authorization: Basic YWRtaW46YWJjMTIz' \
  'http://localhost:3000/api/search?query=PostgreSQL' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'total: {len(d)}'); [print(f\"  {x['title']} (uid: {x['uid']})\") for x in d]"
# 期望: PostgreSQL Overview (uid: pg-overview-v2)
```

**浏览器访问**：
```
http://grafana.local/d/pg-overview-v2/postgresql-overview
# admin / abc123
```

---

## 关键信息（记下来！）

| 项 | 值 |
|---|---|
| Grafana URL | `http://grafana.local`（busi/nginx 反代） |
| Grafana 端口 | 容器内 3000，host 没暴露（走 nginx 80） |
| **Grafana admin 密码** | **`abc123`**（不是默认的 admin，之前改过） |
| Grafana 内部 API | `http://localhost:3000/api/...`（容器内）或 `http://grafana.local/api/...`（host） |
| Prometheus URL | `http://prometheus.local`（busi/nginx 反代） |
| Prometheus 内部 | `http://prometheus:9090`（容器内），`http://localhost:9090`（容器内 root） |
| postgres_exporter 内部 | `http://postgres-exporter:9187/metrics`（在 monitor_default 网络里） |
| **postgres_exporter 密码** | `monitor_pass_2026`（在 busi/docker-compose.yml 里硬编码） |
| postgres 监控 user | `postgres_exporter` |
| dashboard uid | `pg-overview-v2` |
| dashboard URL path | `/d/pg-overview-v2/postgresql-overview` |

---

## 遇到的问题和解决方案

### 问题 1：dashboard 9628（社区最流行的）所有 panel N/A

**症状**：Grafana 看到 `PostgreSQL Database`（uid=000000039）dashboard，但所有 panel 都显示 N/A 或 "No data"。

**根因**：dashboard 9628 是基于**老的** `wrouesnel/postgres_exporter` 写的，那个版本的 metric 带 `release` label（postgres 版本号）。
但新版 `prometheus-community/postgres-exporter` v0.15+ **没有 `release` label**。

dashboard 9628 所有 query 形如 `pg_settings_max_connections{release="$release", instance="$instance"}`，
`{release=...}` 过滤后没有任何 series → 全部 N/A。

**解决**：
- ❌ 用 9628 后改 query 改 label（工作量巨大，35 个 panel）
- ❌ 用 12273（也用 `release` label，patsevanton 写的）— 同样不兼容
- ✅ 用 dashboard 14114（**Grafana Labs 官方 quickstart**）— 但 schemaVersion 26 触发 Grafana 11.4 provisioning bug
- ✅ **自己写一个 10 panel 的 dashboard**（步骤 9）— 用 `instance="..."` 不用 `release`

> 验证 dashboard 用什么 label：`curl http://prometheus:9090/api/v1/query?query=pg_settings_max_connules | python3 -c "..."`
> 看 `labels` 字段就知道新 exporter 实际有什么 label。

### 问题 2：Grafana 11.4 dashboard provisioning bug

**症状**：用 `monitor/grafana/provisioning/dashboards/dashboards.yml` 配 dashboard provider，
启动时日志一直报 `failed to save dashboard: could not resolve dashboards:uid:XXX: Dashboard not found`，
且**每 30 秒重试一次**（provider 的 `updateIntervalSeconds`）。

**根因**：[Grafana GitHub Issue 87342](https://github.com/grafana/grafana/issues/87342) —
Grafana 11.x 的 dashboard provisioning 有 bug。`disableDeletion: true` 也无效。

**解决**（workaround）：
- ❌ 升级/降级 Grafana（不可控）
- ❌ 改 provider 配置（试过 `allowUiUpdates: false`、`disableDeletion: true` 都无效）
- ✅ **直接用 Grafana HTTP API 手动导入 dashboard**（步骤 10），dashboard 落到 DB 里
- ✅ **`dashboards.yml` 重命名为 `.disabled`**（不让 Grafana 看到 provider 配置），错误日志消失

> **代价**：以后改 dashboard JSON 后，**不会自动同步到 Grafana**，需要重新跑一次步骤 10。
> 但开发阶段改 dashboard 不频繁，可接受。

### 问题 3：Grafana admin 密码不是 admin

**症状**：`docker exec grafana env` 显示 `GF_SECURITY_ADMIN_PASSWORD=admin`，但 `curl -u admin:admin` 报 401。

**根因**：GF_SECURITY_ADMIN_PASSWORD 只在**首次启动**（数据库为空）时设置 admin 密码。后续用 UI 改过密码后，环境变量就**不再生效**。

**解决**：当前 Grafana 实际密码是 **`abc123`**（之前手动改过），按这个登录。
> 鉴权 header：`Authorization: Basic YWRtaW46YWJjMTIz`

> 验证：登录 Grafana UI 改密码 → env 变量会被忽略。改后想从 env 重置密码，**只能删 grafana 持久化目录**（`/Volumes/data/working/docker/data/grafana/grafana.db`）。

### 问题 4：json decode error: Expecting value: line 1 column 1 (char 0)

**症状**：`wget -O- http://...api/...` 后用 `python3 -c "import sys, json; json.load(sys.stdin)"` 解析失败。

**根因**：
- **HTTP 401** 时 body 是 JSON error，但格式不一样
- **HTTP 404** 时 body 是 HTML
- **HTTP 200 但 Content-Type 不是 json**（比如 Grafana 在某些端点返回 empty body）

**解决**：
```bash
# 先看 raw 输出，确认是 401/404/200
docker exec grafana wget -v -O- --timeout=5 \
  --header='Authorization: Basic ...' \
  'http://localhost:3000/api/...'

# 看到 401 → 检查密码
# 看到 404 → 检查 URL 拼写
# 看到 200 + 空 → 检查 API 是否要特定 method (GET vs POST)
```

### 问题 5：`pi-lens` 校验阻塞 grafana provisioning 文件

**症状**：把 datasource 配在 `provisioning/datasources/prometheus.yml`，pi-lens 报
`Property datasources is not allowed. / Property apiVersion is not allowed.`

**根因**：`pi-lens` 的 prometheus language server 把 `prometheus.yml` 文件按 prometheus schema 校验，
发现 `apiVersion: 1` / `datasources:` 是 prometheus schema 里的非法字段。

**解决**：
- 文件改名：`provisioning/datasources/datasource.yml`（避开 prometheus schema 误判）
- 加 schema 提示（实测不一定生效）：`# yaml-language-server: $schema=`

---

## 验证 checklist

- [ ] `docker exec postgres psql -U postgres_exporter -d postgres -c "SELECT version();"` 返回正常
- [ ] `docker exec postgres-exporter wget -q -O- http://localhost:9187/metrics | grep pg_` 有 `pg_database_size_bytes` 等指标
- [ ] `prometheus` scrape target: `cadvisor: up`, `postgres: up`, `prometheus: up`
- [ ] Grafana datasource API 返回 `[{name: "Prometheus", url: "http://prometheus:9090"}]`
- [ ] Grafana search API 返回 `[PostgreSQL Overview (uid: pg-overview-v2)]`
- [ ] 浏览器 `http://grafana.local/d/pg-overview-v2/postgresql-overview` 打开能看到数据（不是 N/A）
- [ ] dashboard 的 `instance` 下拉框自动填充了 `postgres-exporter:9187`

---

## 回滚

```bash
# 1. 删 busi 的 exporter
cd /Volumes/data/working/docker/busi
docker compose stop postgres-exporter
docker compose rm -f postgres-exporter

# 2. 删 monitor 里的 scrape job（从 prometheus.yml 注释掉或删掉 postgres 段）
# 3. 删 Grafana 里的 dashboard
curl -X DELETE -u admin:abc123 http://grafana.local/api/dashboards/uid/pg-overview-v2

# 4. 删 postgres 里的 user（可选）
docker exec postgres psql -U postgres -c "DROP USER postgres_exporter;"
```

> ⚠️ 不要用 `rm -rf`，按个人偏好用 `mv` 到 `/tmp/claude/.delete.*`（如果回滚整个工程目录）。

---

## 关联项目文件

```
/Volumes/data/working/docker/
├── busi/
│   ├── docker-compose.yml                    # + postgres-exporter 服务
│   └── postgres/
│       ├── Makefile                          # + exporter-user-bootstrap target
│       └── initdb.d/
│           └── 10-exporter-user.sql          # 新建: 监控 user 的 SQL
└── monitor/
    ├── docker-compose.yml                    # grafana 加 provisioning 挂载
    ├── prometheus/
    │   └── prometheus.yml                    # + postgres scrape job
    └── grafana/
        ├── provisioning/
        │   └── datasources/
        │       └── datasource.yml            # 新建: prometheus 数据源
        ├── dashboards/
        │   ├── postgres.json                 # 10 panel 自定义 dashboard (source of truth)
        │   └── dashboards.yml.disabled       # 不启用 dashboard provisioning (避开 bug)
        └── (Grafana DB 里 uid=pg-overview-v2, 步骤 10 导入的副本)
```

---

## 关键经验总结

1. **dashboard 选型要看 exporter 版本**：
   - `wrouesnel/postgres_exporter`（旧）→ 用 `release` label
   - `prometheuscommunity/postgres-exporter`（新）→ 用 `instance` label
   - 装新版 exporter 就别用老版 dashboard

2. **Grafana 11.4 dashboard provisioning 不可靠**：能跑就跑，跑不通直接用 API 导入更稳。

3. **`*.local` 域名在 macOS 上天然解析到 127.0.0.1**：但 `host.docker.internal` 在 nginx 容器里会被错误解析成
   `0.250.250.254`（macOS Cloudflare DoH 干扰 docker DNS），影响走 host 反代的服务（claudemem / openclaw）。
   pg 监控这条链路不依赖 host，所以不受影响。

4. **pi-lens lint 误判 Grafana provisioning yml**：因为文件名带 `prometheus.yml` 被 prometheus language server 接管。
   改名 + 加 `# yaml-language-server: $schema=` 注释可绕过。

5. **环境变量和实际配置可能不同步**：GF_SECURITY_ADMIN_PASSWORD 只在首次启动生效，UI 改过的密码 env 管不了。
   重置只能清 DB。
