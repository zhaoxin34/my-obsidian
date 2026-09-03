# ==================== Debezium 加 Prometheus 和 Grafana 监控====================

> 适用项目：`/Volumes/data/working/docker/monitor` + `laop-data-bank` 跨工程
> 容器：`kafka-connect`（`quay.io/debezium/connect:2.5`，在 laop-data-bank 工程）
> 实施日期：2026-09-03
> **前置 playbook**：[Debezium 加 jmx_exporter (暴露Prometheus指标).md](./Debezium%20加%20jmx_exporter%20(暴露Prometheus指标).md)
> —— 本文不重复 jmx_exporter 注入步骤，只讲注入**之后**的 Prometheus + Grafana 链路

---

## 背景

`laop-data-bank` 工程的 `kafka-connect` 容器已经通过 jmx_exporter 在 host 的 7071 端口
暴露了 Prometheus 格式指标（`debezium_metrics_*` / `kafka_connect_metrics_*`）。
本 playbook 接上后链路：让 `/Volumes/data/working/docker/monitor` 工程的
Prometheus 抓 7071，加告警规则，在 Grafana 里可视化。

> 为什么不用 laop-data-bank 自己的 P+G？之前 `postgres 监控配置（Prometheus + Grafana）.md`
> playbook 已经把 `monitor` 工程搭成**整套 P+G 中心**。所有 exporter（postgres、kafka、debezium）
> 都接进来是顺理成章的，不另起炉灶。

---

## 目标

最终能在 Grafana 里看到：
- **Debezium Connector** dashboard（10 panel）：connector count / Connected / 错误数 /
  EventsProcessed / MilliSecondsBehindSource / Queue 容量 / I/O 等
- **CDC Pipeline Overview** dashboard（10 panel）：4 个 exporter Up 状态 + Active Alerts +
  3 个 lag stat（PG long tx / Debezium lag / Kafka consumer lag）+ 端到端 lag 趋势
- Prometheus 加载 18 个告警规则（3 个 group：debezium / kafka / postgres）

---

## 前置条件

- ✅ jmx_exporter 已经在 `kafka-connect` 容器里跑着，`curl http://localhost:7071/metrics` 返回 200
- ✅ `monitor` 工程的 Prometheus + Grafana 已经在跑（`http://prometheus.local` / `http://grafana.local`）
- ✅ 已有 `kafka_exporter`（监控 bigdata 工程的 Kafka broker）和 `postgres_exporter`（监控 busi 工程的 PG）
- ✅ 知道 connector 的 `topic.prefix`（决定 `debezium_metrics_*` 指标里 `name` label 的值——例如 `pgcdc`）

---

## 架构

```
laop-data-bank 工程 (kafka-connect 容器)
  └─ jmx_exporter (Java agent 注入)
     └─ :7071 端口映射到 host

                ↓ host.docker.internal:7071

/Volumes/data/working/docker/monitor 工程
  prometheus
    ├─ scrape_configs
    │  ├─ job: postgres        (busi/postgres-exporter:9187, 走 monitor_default)
    │  ├─ job: kafka           (bigdata/kafka-exporter:9308, 走 monitor_default)
    │  └─ job: debezium-connect (host.docker.internal:7071, 走 host)
    │
    ├─ rule_files: rules/*.yml
    │  ├─ debezium.yml  (6 rules)
    │  ├─ postgres.yml  (6 rules)
    │  └─ kafka.yml     (6 rules)
    │
    └─ 触发告警 → Alertmanager（**当前未部署**，告警规则在 Prometheus 里 evaluate 但无人接）

  grafana
    └─ dashboards (走 HTTP API 导入, 绕开 Grafana 11.4 provisioning bug)
       ├─ pg-overview-v2      (PostgreSQL Overview)
       ├─ kafka-overview-v1   (Kafka Overview)
       ├─ debezium-connector-v1 (Debezium Connector) ← 本次新增
       └─ pipeline-overview-v1 (CDC Pipeline Overview) ← 本次新增
```

---

## 实施步骤

### 1. 在 `monitor/prometheus/prometheus.yml` 加 scrape job

**关键决定**：

- **target 用 `host.docker.internal:7071`**（jmx_exporter 端口被 `kafka-connect.ports` 映射到 host）
- **不要用 `172.17.0.1` 或 `127.0.0.1`**：前者是 docker bridge gateway，不一定可访问 host 端口；
  后者在某些 Mac + Docker Desktop 下被错误解析为 Cloudflare DoH
- **prometheus 容器里 `host.docker.internal` 实际是工作的**（虽然在 nginx 容器里被 DNS 干扰）

```yaml
  # debezium / kafka-connect (laop-data-bank 工程, jmx_exporter 注入到
  # kafka-connect 容器, 7071 端口映射到 host)
  - job_name: "debezium-connect"
    static_configs:
      - targets: ["host.docker.internal:7071"]
        labels:
          connector: "pgcdc"
          component: "kafka-connect"
```

`connector` label 是 `topic.prefix`（这里是 `pgcdc`，**不是** connector name 本身）。
后续 dashboard PromQL 用 `name="pgcdc"` 过滤——文档 §6.5 里假设的 `pg-poc-source` 是错的。

### 2. 在 prometheus.yml 加 `rule_files` + 挂载 rules 目录

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  # ... (其他 job 不变)
```

`monitor/docker-compose.yml` 里 prometheus 容器加挂载：

```yaml
  prometheus:
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro    # ← 新增
      - /Volumes/data/working/docker/data/prometheus:/prometheus
```

### 3. 创建 rules 目录 + 3 个告警规则文件

`monitor/prometheus/rules/{debezium,postgres,kafka}.yml`。

**debezium.yml**（6 rules）的核心 PromQL：

| 告警 | 严重度 | 关键 expr |
|---|---|---|
| DebeziumConnectorDown | critical | `kafka_connect_worker_metrics_connector_count < 1` |
| DebeziumLagHigh | warning | `debezium_metrics_MilliSecondsBehindSource > 60000` |
| DebeziumLagCritical | critical | `> 600000` (10min) |
| DebeziumErrorsIncreasing | warning | `increase(debezium_metrics_NumberOfErrors[5m]) > 0` |
| DebeziumSourceTaskUnassigned | warning | `debezium_metrics_Connected == 0` |
| KafkaConnectWorkerDown | critical | `up{job="debezium-connect"} == 0` |

**postgres.yml**（6 rules）—— 用默认 `postgres_exporter` 能拿到的指标
（**不依赖** `custom queries.yaml`）：

- `up{job="postgres"}`, `pg_stat_activity_count`, `pg_stat_activity_max_tx_duration`, `pg_database_size_bytes`
- 关键：监控长事务（max_tx_duration > 300s warning / > 3600s critical）——
  这是 CDC 滞后的最常见杀手

**kafka.yml**（6 rules）—— 用 `danielqsj/kafka_exporter` 实际能拿到的指标：

| 文档 §6.3.3 假设 | 实际能用的 | 原因 |
|---|---|---|
| `kafka_server_broker_count` | `kafka_brokers` | JMX 风格，kafka_exporter 不暴露 |
| `kafka_consumergroup_lag` | `kafka_consumergroup_lag` ✅ | 直接可用 |
| `kafka_topic_partition_in_sync_replica_count` | `kafka_topic_partition_in_sync_replica` | label 名少 `_count` |
| `kafka_topic_partition_replica_count` | `kafka_topic_partition_replicas` | label 名少 `_count` |

### 4. 重启 prometheus + 验证

```bash
cd /Volumes/data/working/docker/monitor

# force-recreate 让 prometheus 加载新挂载的 rules 目录
docker compose up -d --force-recreate --no-deps prometheus
sleep 10

# 验证 5 个 target 全 up（含 debezium-connect）
docker exec prometheus wget -q -O- http://localhost:9090/api/v1/targets | \
  python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"  {t['labels']['job']}: {t['health']}\") for t in d['data']['activeTargets']]"

# 验证 18 个 rule 加载
docker exec prometheus wget -q -O- http://localhost:9090/api/v1/rules | \
  python3 -c "import sys, json; d=json.load(sys.stdin); [print(f'  {g[\"name\"]}: {len(g[\"rules\"])} rules') for g in d['data']['groups']]"
```

### 5. 写 2 个 dashboard JSON + 用 API 导入

**`monitor/grafana/dashboards/debezium.json`** —— 10 panel：

| Panel | 类型 | PromQL |
|---|---|---|
| Connector Count | stat | `kafka_connect_worker_metrics_connector_count` |
| Connected | stat | `debezium_metrics_Connected{name=~"$connector"}` |
| Total Errors | stat | `sum(debezium_metrics_NumberOfErrors{name=~"$connector"})` |
| Events Processed (Total) | stat | `sum(debezium_metrics_NumberOfEventsProcessed{name=~"$connector"})` |
| MilliSecondsBehindSource | timeseries | `debezium_metrics_MilliSecondsBehindSource{name=~"$connector", context=~"$context"}` |
| Events Processed Rate | timeseries | `sum by (name, context) (rate(debezium_metrics_NumberOfEventsProcessed[1m]))` |
| Queue Total Capacity | timeseries | `debezium_metrics_QueueTotalCapacity{...}` |
| kafka-connect Up | timeseries | `up{job="debezium-connect"}` |
| Kafka Connect I/O | timeseries | `kafka_connect_metrics_io_wait_ratio` 等 |
| Remaining Snapshot | timeseries | `debezium_metrics_RemainingSnapshotCount` |

**`monitor/grafana/dashboards/pipeline.json`** —— 10 panel：

- 4 个 stat: PG/Kafka/Debezium-Connect Up + Active Alerts
- 3 个 lag stat: PG long_tx / Debezium MilliSecondsBehindSource / Kafka consumer lag
- 2 个 timeseries: Debezium lag trend + Kafka consumer lag by group
- 1 个 all-up status timeseries

**导入（绕开 Grafana 11.4 dashboard provisioning bug）**：

```bash
MONITOR=/Volumes/data/working/docker/monitor
for name in debezium pipeline; do
  cat "$MONITOR/grafana/dashboards/$name.json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('id', None)
print(json.dumps({'dashboard': d, 'overwrite': True, 'message': 'monitoring v1'}))
" > /tmp/dash-import.json
  docker cp /tmp/dash-import.json grafana:/tmp/dash-import.json
  docker exec grafana wget -q -O- --timeout=10 \
    --header='Authorization: Basic YWRtaW46YWJjMTIz' \
    --header='Content-Type: application/json' \
    --post-file=/tmp/dash-import.json \
    'http://localhost:3000/api/dashboards/db'
done
```

### 6. 验证 dashboard 拉得到数据

```bash
# 浏览器: http://grafana.local/d/debezium-connector-v1/debezium-connector
# 浏览器: http://grafana.local/d/pipeline-overview-v1/cdc-pipeline-overview-end-to-end

# 或用 API 验证 dashboard 存在
docker exec grafana wget -q -O- --header='Authorization: Basic YWRtaW46YWJjMTIz' \
  'http://localhost:3000/api/search' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'total: {len(d)}')"
```

---

## 关键信息

| 项 | 值 |
|---|---|
| jmx_exporter 端点 | `http://localhost:7071/metrics` (host) / `http://host.docker.internal:7071/metrics` (从 monitor 容器) |
| Connector name label | **`pgcdc`**（不是 `pg-poc-source`）—— topic.prefix 值 |
| scrape job | `debezium-connect` |
| 主要指标前缀 | `debezium_metrics_*` / `kafka_connect_metrics_*` / `kafka_connect_worker_metrics_*` |
| dashboard UID | `debezium-connector-v1` / `pipeline-overview-v1` |
| Alertmanager | **未部署**（告警规则 evaluate 但无人接收） |
| Grafana 密码 | `abc123`（不是 admin） |

---

## 遇到的问题和解决方案

### 问题 1：`host.docker.internal` 在 prometheus 容器解析不出

**症状**：`docker exec prometheus nslookup host.docker.internal` 返回 `*** Can't find host.docker.internal: No answer`

**根因**：docker 容器内 DNS（127.0.0.11）查不到这个特殊名字——但实际访问**是通的**。

**解决**：
- ❌ 不要用 `172.17.0.1`（docker bridge gateway）—— 不一定通
- ❌ 不要用 `127.0.0.1`（在 Mac + Docker Desktop 下可能被错误解析为 Cloudflare DoH 0.250.250.254）
- ✅ **直接用 `host.docker.internal:7071`**——docker 内部有特殊机制处理（虽然 nslookup 看不到）

> 验证：之前 nginx 容器里 `host.docker.internal` 解析到 `0.250.250.254`（Cloudflare DoH）导致 claudemem/openclaw 502，
> prometheus 容器没遇到这个问题。**不同容器 DNS 行为可能不一样**。

### 问题 2：connector name label 是 `pgcdc` 不是 `pg-poc-source`

**症状**：dashboard PromQL 用 `name="pg-poc-source"` 查不到数据

**根因**：Debezium jmx_exporter 暴露的 `name` label 是 connector 配置里的 `topic.prefix`（这里是 `pgcdc`），
**不是** connector 自身名称（`pg-poc-source`）。文档 §6.5 dashboard spec 假设错了。

**解决**：

```promql
# 错（文档原版）
debezium_metrics_MilliSecondsBehindSource{name="pg-poc-source"}

# 对
debezium_metrics_MilliSecondsBehindSource{name="pgcdc"}
```

> 验证方法：`curl http://localhost:7071/metrics | grep debezium_metrics_MilliSecondsBehindSource | head -1`
> 实际看到的 `name="..."` 才是真值。

### 问题 3：Grafana 11.4 dashboard provisioning bug

**症状**：`monitor/grafana/provisioning/dashboards/*.yml` 配了 dashboard provider，
启动时报 `failed to save dashboard: could not resolve dashboards:uid:XXX: Dashboard not found`

**根因**：[Grafana GitHub Issue 87342](https://github.com/grafana/grafana/issues/87342) —
Grafana 11.x dashboard provisioning 有 bug。

**解决**（workaround，跟之前 postgres 监控一样）：
- ✅ **直接用 Grafana HTTP API 手动导入 dashboard**（步骤 5）
- ✅ **`dashboards.yml` 留空 / 不写 dashboard provider 配置**

> 代价：以后改 dashboard JSON 后**不会自动同步**，需要重新跑一次步骤 5 的 API 导入。

### 问题 4：postgres 告警不能完全照搬文档 §6.3.1

**症状**：照文档写 `pg_replication_slot_wal_lag_bytes` 告警规则，但 prometheus 查不到这个指标

**根因**：laop-data-bank 文档 §6.3.1 是为**带 custom queries.yaml 的 postgres_exporter** 设计的
（`pg_replication_slot_*` / `pg_long_transactions_*` 等 custom query 指标）。
我们的 busi 工程用**默认 postgres_exporter**（没 custom queries.yaml），不暴露这些。

**解决**：postgres.yml 用**默认 exporter 能拿到的指标**重写：
- `up{job="postgres"}` —— exporter 自身
- `pg_stat_activity_count` —— 当前活跃连接
- `pg_stat_activity_max_tx_duration` —— 最长事务时长
- `pg_database_size_bytes` —— 数据库大小

> 如果将来 busi 工程要监控 replication slot，需要给 postgres_exporter 加 `--extend.query-path` 参数挂载 `queries.yaml`。

### 问题 5：kafka 告警用错指标名（`kafka_server_*` 系列）

**症状**：照文档 §6.3.3 写 `kafka_server_broker_count < 1` 告警，prometheus 一直不触发

**根因**：laop-data-bank 文档是给**JMX 风格监控**写的（`kafka_server_*` / `kafka_controller_*` / `kafka_network_*`），
这些只有**注入 JMX exporter 才有**。`danielqsj/kafka_exporter` 不暴露。

**解决**：用 `kafka_exporter` 实际能拿到的：

| 文档 §6.3.3 | 实际 kafka_exporter 指标 |
|---|---|
| `kafka_server_broker_count` | `kafka_brokers` |
| `kafka_topic_partition_in_sync_replica_count` | `kafka_topic_partition_in_sync_replica` |
| `kafka_topic_partition_replica_count` | `kafka_topic_partition_replicas` |

### 问题 6：YAML `>-` 折行 + 算术表达式坑

**症状**：kafka.yml 里写 `expr: kafka_topic_partition_in_sync_replica < kafka_topic_partition_replicas` 触发了
80 字符 line-length lint 报错

**根因**：一行写不下 84 字符

**解决**：用 YAML `>-` folded scalar：

```yaml
expr: >-
  kafka_topic_partition_in_sync_replica
  < kafka_topic_partition_replicas
```

`>-` 把多个非空行折叠成单个空格，结果跟一行写完全等价。

> ⚠️ 别用 `|`（literal block scalar）—— 会保留换行字符，PromQL 会解析失败。

### 问题 7：告警规则需要的指标不在导出器里

**症状**：`busi` 工程的 `postgres_exporter` 用的是默认镜像，没装 `queries.yaml`，
所以文档 §6.3.1 里的 `pg_replication_slot_*` / `pg_long_transactions_*` 等指标**全无**

**根因**：`postgres_exporter` 默认只导出 `pg_stat_*` 等内置视图，自定义 SQL 才能导出
`pg_replication_slots` / `pg_stat_activity` 上的复杂 query 指标

**解决**（临时）：用 prometheus `up{}` 指标 + `pg_stat_activity_count` 写替代告警
**解决**（根本）：将来给 busi 的 postgres_exporter 加 `--extend.query-path=/etc/queries.yaml` 参数 + 挂载 `queries.yaml`
（laop-data-bank 文档 §6.1 已有现成的 queries.yaml 模板）

### 问题 8：datasource 配在 `prometheus.yml` 同名文件触发 pi-lens lint 误报

**症状**：`monitor/grafana/provisioning/datasources/prometheus.yml` 被 pi-lens 报
`Property datasources is not allowed`

**根因**：`prometheus.yml` 文件名让 prometheus language server 误以为是 prometheus 配置，
但 Grafana datasource provisioning 格式（`apiVersion: 1 / datasources:`）跟 prometheus 配置 schema 不一样

**解决**：改文件名 `datasource.yml`（避开 prometheus schema 误判）

> 这跟 `Debezium 加 jmx_exporter` playbook 里那个 jmx_config.yml lint 问题是同一类坑。

---

## 验证 checklist

- [ ] `curl http://localhost:7071/metrics | grep debeium_metrics_Connected` 返回 1.0
- [ ] prometheus targets 全 up：`cadvisor / kafka / postgres / prometheus / debezium-connect` 都 `up`
- [ ] prometheus `/api/v1/rules` 显示 3 个 group 共 18 rules
- [ ] `docker exec prometheus wget -q -O- 'http://localhost:9090/api/v1/query?query=debezium_metrics_Connected' | grep pgcdc` 有结果
- [ ] 浏览器打开 `http://grafana.local/d/debezium-connector-v1/debezium-connector` 能看到数据
- [ ] 浏览器打开 `http://grafana.local/d/pipeline-overview-v1/cdc-pipeline-overview-end-to-end` 能看到 4 个 Up 全绿
- [ ] Grafana 里搜 "PostgreSQL" / "Kafka" / "Debezium" / "Pipeline" 能找到 4 个 dashboard
- [ ] 故意 stop kafka-connect 容器，验证 `KafkaConnectWorkerDown` critical 告警能触发

---

## 回滚

```bash
cd /Volumes/data/working/docker

# 1. 从 prometheus.yml 删除 debezium-connect scrape job + rule_files
#    (用 git show HEAD:monitor/prometheus/prometheus.yml 拿 commit 前版本覆盖)

# 2. 从 docker-compose.yml 删除 rules bind mount

# 3. 删除 3 个 rules 文件和 2 个 dashboard 文件
mv monitor/prometheus/rules /tmp/claude/.delete.rules
mv monitor/grafana/dashboards/debezium.json /tmp/claude/.delete.debezium.json
mv monitor/grafana/dashboards/pipeline.json /tmp/claude/.delete.pipeline.json

# 4. 用 API 删 Grafana 里的 dashboard
curl -X DELETE -u admin:abc123 \
  http://grafana.local/api/dashboards/uid/debezium-connector-v1
curl -X DELETE -u admin:abc123 \
  http://grafana.local/api/dashboards/uid/pipeline-overview-v1

# 5. 重启 prometheus
cd monitor && docker compose restart prometheus
```

> ⚠️ 不要用 `rm -rf`，按个人偏好用 `mv` 到 `/tmp/claude/.delete.*`。
> 回滚对 CDC 数据流**无影响**（监控和数据流独立）。

---

## 关联项目文件

```
/Volumes/data/working/docker/monitor/
├── docker-compose.yml                          # prometheus 加 rules bind mount
├── prometheus/
│   ├── prometheus.yml                           # + debezium-connect scrape job + rule_files
│   └── rules/
│       ├── debezium.yml                         # 6 rules
│       ├── postgres.yml                         # 6 rules (用默认 exporter 指标)
│       └── kafka.yml                            # 6 rules (用 kafka_exporter 指标)
└── grafana/dashboards/
    ├── postgres.json                           # (老) PostgreSQL Overview
    ├── kafka.json                              # (老) Kafka Overview
    ├── debezium.json                           # (新) Debezium Connector
    └── pipeline.json                           # (新) CDC Pipeline Overview

# jmx_exporter 注入 (老 playbook 已覆盖, 不重复):
/Volumes/data/working/ai/laop-data-bank/infrastructure/poc/
├── docker-compose.override.yml                 # jmx_exporter 注入到 kafka-connect
└── ../monitoring/exporters/jmx/
    ├── jmx_prometheus_javaagent-0.20.0.jar
    └── jmx_config.yml                           # 6 条 Debezium 精准规则
```

---

## 关键经验总结

1. **跨工程用 shared docker network 或 host.docker.internal**：
   - 同 network 通信用容器名（`kafka-exporter:9308`）
   - 跨 host 通信用 `host.docker.internal`（验证后再用——不同容器 DNS 行为不一样）

2. **dashboard PromQL 用真实的 label 值**：文档假设的 label 经常是错的（`name="pgcdc"` vs `name="pg-poc-source"`），
   先用 `curl .../metrics | grep XXX` 看实际值

3. **Grafana 11.4 dashboard provisioning bug 是已知问题**，workaround 始终是 HTTP API 手动导入

4. **exporters 的"可观测指标"是动态的**：每个 exporter 默认指标不一样，要先 curl `/metrics` 确认实际输出，
   再写告警规则（不然规则永远不触发）

5. **告警规则要"对得上 exporter 实际能输出的指标"**：
   - 默认 `postgres_exporter` 没有 `pg_replication_slot_*`（需要 custom queries.yaml）
   - `kafka_exporter` 没有 `kafka_server_*`（需要 JMX exporter）
   - 别照文档原样抄——先 curl 验证

6. **YAML 折行（`>-` vs `|`）在 PromQL 里效果完全不同**：
   - `>-` 折叠成空格（推荐用于 PromQL 单行表达式）
   - `|` 保留换行（PromQL 解析会失败）

7. **文档常常滞后于实际**：laop-data-bank 文档 §6.5 dashboard spec 假设的 connector name、metric 名字都有错，
   实施时**以实际 curl 到的为准**

8. **commit message 详细记录"踩坑教训"**——比 commit message 写"加 X" 更有用，
   下次人看 git log 就知道为什么不用文档原版
