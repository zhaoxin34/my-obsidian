# ==================== Debezium 加 jmx_exporter（暴露 Prometheus 指标）====================

> 适用项目：`laop-data-bank`（PG → Debezium → Kafka → StarRocks）
> 容器：`kafka-connect`（`quay.io/debezium/connect:2.5`）
> 实施日期：2026-09-03

---

## 背景

Debezium / Kafka Connect 默认只暴露 JMX 格式的指标（JVM、connector、worker 都有），
Prometheus 没法直接抓。需要一个 **JMX → Prometheus 桥接器**把指标转成 Prometheus 格式。

> 业界标准：`jmx_prometheus_javaagent`（[Prometheus 官方项目](https://github.com/prometheus/jmx_exporter)）。
> Debezium 团队的 reference 实现：[`debezium-examples/monitoring`](https://github.com/debezium/debezium-examples/tree/main/monitoring)。

---

## 目标

给 `kafka-connect` 容器注入 jmx_exporter，让 Prometheus 能从 `:7071/metrics` 抓到：
- `debezium_metrics_*`（`MilliSecondsBehindSource` / `NumberOfEventsProcessed` / `Connected` 等）
- `kafka_connect_worker_metrics_*`（worker 状态）
- `kafka_connect_metrics_*`（client 级别）

> 副作用：同时暴露 JMX 端口 `:1976`（给 JConsole 等工具用，可选）。

---

## 前置条件

- ✅ Debezium connector 已正常运行（`curl http://localhost:8083/connectors/<name>/status` 返回 RUNNING）
- ✅ 已知 connector 的 `topic.prefix`（决定指标 `name` label 的值）
- ✅ 宿主机端口 `7071` 和 `1976` 未被占用

---

## 实施步骤

### 1. 创建目录结构

```bash
cd /Volumes/data/working/ai/laop-data-bank
mkdir -p infrastructure/monitoring/exporters/jmx
```

### 2. 下载 jmx_prometheus_javaagent jar

```bash
cd infrastructure/monitoring/exporters/jmx

# 优先用阿里云镜像（Maven Central 国内直连经常 403）
curl -L --fail -o jmx_prometheus_javaagent-0.20.0.jar \
  https://maven.aliyun.com/repository/central/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar

# 验证是个有效 jar
file jmx_prometheus_javaagent-0.20.0.jar
# 应该输出: Java archive data (JAR)
```

> 直连 Maven Central 经常报 403（GFW）。阿里云镜像 / 清华镜像都可以。
> 版本对照 Kafka Connect 2.5 用 0.20.0 没问题。

### 3. 写 jmx_config.yml（**不要**用 `pattern: ".*"` 兜底）

**文件**：`infrastructure/monitoring/exporters/jmx/jmx_config.yml`

⚠️ **坑**：不要图省事写 `pattern: ".*"`，会把 JVM 内部所有 MBean 全暴露（几千个），Prometheus 存储会爆。
下面 6 条规则是 Debezium 官方 examples 仓库的精准规则，直接复制。

> 长 pattern 行的处理：Debezium 官方 pattern 本身就 >100 字符，regex 不能拆。
> 利用 **YAML 双引号字符串的流式折行**（line break 折成单个空格），JMX MBean 名字里
> `, ` 本来就有空格，折行后语义不变。**不要用 `>-` literal**（会破坏 JVM arg）。
>
> 如果 linter 还是超 80 字符限制，加 `# yamllint disable-file rule:line-length` 顶部注释。

### 4. 写 docker-compose override 文件

**文件**：`infrastructure/poc/docker-compose.override.yml`（**新建，不改原文件**）

关键点：
- 相对路径：从 `infrastructure/poc/` 出发是 `../monitoring/...`（**一个 `..`**）
- env var 用 `JMXPORT` / `JMXHOST`（**无下划线**，Debezium 镜像约定，Docker 下必填 `JMXHOST`）
- `KAFKA_OPTS` 必须**单行**（YAML `>-` 折行会插空格破坏 `-javaagent:` arg）
- 端口 `1976`（JMX）+ `7071`（Prometheus）；`8083` 在原文件里（ports 是合并语义）

### 5. 重启容器（**必须显式指定 override 文件**）

```bash
cd /Volumes/data/working/ai/laop-data-bank/infrastructure/poc

# ⚠️ 关键：docker compose v2 用 -f 时，override 不会自动加载，必须显式指定
docker compose -f docker-compose-connect.yml -f docker-compose.override.yml down
docker compose -f docker-compose-connect.yml -f docker-compose.override.yml up -d
```

### 6. 验证

```bash
# 端口和容器状态
docker ps --filter "name=kafka-connect" --format "{{.Names}} {{.Status}} {{.Ports}}"
# 应该看到 8083 + 1976 + 7071 三个端口都映射

# jmx_exporter 端点
curl -sf http://localhost:7071/metrics | head -5
# 应该返回 Prometheus 格式的指标

# Debezium 关键指标是否存在
curl -s http://localhost:7071/metrics | grep -E "debezium_metrics_(MilliSecondsBehindSource|Connected)" | head -5

# 确认 CDC 没断
curl -s http://localhost:8083/connectors/<connector-name>/status
# connector.state 和 tasks[0].state 都应该是 RUNNING
```

---

## 遇到的问题和解决方案

### 问题 1：Maven Central 直连 403

**症状**：`curl https://repo1.maven.org/...` 返回 `error 403`
**原因**：国内网络环境
**解决**：用阿里云镜像

```bash
# 阿里云 Maven 镜像
https://maven.aliyun.com/repository/central/...

# 其他备选
https://mirrors.tuna.tsinghua.edu.cn/maven/maven2/...
```

### 问题 2：容器重启后看不到 7071 端口

**症状**：`docker compose -f docker-compose-connect.yml up -d` 后，`docker ps` 看不到 7071
**原因**：用 `-f` 时 docker compose v2 **不会自动加载** `docker-compose.override.yml`
**解决**：显式带上 override 文件

```bash
# 错的（override 不生效）
docker compose -f docker-compose-connect.yml up -d

# 对的
docker compose -f docker-compose-connect.yml -f docker-compose.override.yml up -d
```

### 问题 3：JMXHOST 设成 127.0.0.1 导致 JMX 起不来

**症状**：jmx_exporter 起来了，但 `1976` 端口用 JConsole 连不上
**原因**：Debezium Docker 镜像警告 `JMXHOST` 不能是 `127.0.0.1`，要可被 JMX client 解析的地址
**解决**：

- 同容器内访问用 `localhost` OK（jmx_exporter 用 Java agent 模式，不需要 JMXHOST 也行）
- 容器外访问要写宿主机实际 IP（不能用 `127.0.0.1`）

### 问题 4：PromQL 里 `name` label 写错

**症状**：PromQL `debezium_metrics_xxx{name="pg-poc-source"}` 查不到数据
**原因**：`name` label 的值是 connector config 里的 **`topic.prefix`**（这里是 `pgcdc`），不是 connector 本身的名字（`pg-poc-source`）
**解决**：

```promql
# 错
debezium_metrics_MilliSecondsBehindSource{name="pg-poc-source"}

# 对
debezium_metrics_MilliSecondsBehindSource{name="pgcdc"}
```

> 验证方法：`curl http://localhost:7071/metrics | grep debezium_metrics_MilliSecondsBehindSource`
> 实际看到的 `name="..."` 才是真值。

### 问题 5：YAML `>-` 折行破坏 JVM arg

**症状**：jmx_exporter 启动失败，容器日志报 `Unable to parse Java agent`
**原因**：

```yaml
# 错（`>-` 把 line break 折成空格，JVM 看到两个参数）
KAFKA_OPTS: >-
  -javaagent:/kafka/etc/jmx_prometheus_javaagent.jar=7071
  :/kafka/etc/config.yml
```

变成 JVM 参数 `-javaagent:...=7071 :/kafka/etc/config.yml`（中间多了一个空格 = 两个参数）

**解决**：单行写，加 `# yamllint disable-line rule:line-length` 抑制 linter

```yaml
# yamllint disable-line rule:line-length
KAFKA_OPTS: -javaagent:/kafka/etc/jmx_prometheus_javaagent.jar=7071:/kafka/etc/config.yml
```

---

## 验证 checklist

- [ ] `docker ps` 看到 8083 + 1976 + 7071 三个端口
- [ ] `curl http://localhost:7071/metrics` 返回 200 且有数据（>10KB）
- [ ] 看到 `debezium_metrics_MilliSecondsBehindSource{...}` 系列
- [ ] `MilliSecondsBehindSource` 值是 `-1` 或接近 0（无延迟）
- [ ] `Connected = 1`
- [ ] Debezium connector state 仍是 `RUNNING`（**关键：CDC 没断**）

---

## 回滚

```bash
cd /Volumes/data/working/ai/laop-data-bank/infrastructure/poc

# 删除 override 文件（不修改原文件，零风险）
mv docker-compose.override.yml /tmp/claude/.delete.docker-compose.override.yml

# 重启用单 -f 命令
docker compose -f docker-compose-connect.yml down
docker compose -f docker-compose-connect.yml up -d
```

> ⚠️ 不要用 `rm -rf`，按个人偏好用 `mv` 到 `/tmp/claude/.delete.*`。
> 回滚对 CDC 数据流**无影响**（监控和数据流是独立的）。

---

## 参考资料

- [Debezium 官方监控文档](https://debezium.io/documentation/reference/stable/operations/monitoring.html)（只讲 JMX，不讲 jar）
- [Debezium examples/monitoring 仓库](https://github.com/debezium/debezium-examples/tree/main/monitoring)（jmx_config.yml 模板来源）
- [prometheus/jmx_exporter](https://github.com/prometheus/jmx_exporter)（JMX→Prometheus 桥接器官方仓库）
- 完整实施文档：`/Volumes/data/working/ai/laop-data-bank/docs/监控实施-prometheus-grafana.md`（v1.2）

---

## 关联项目文件

```
infrastructure/monitoring/exporters/jmx/
├── jmx_prometheus_javaagent-0.20.0.jar  # 563K，Java agent
└── jmx_config.yml                       # 6 条精准规则（官方）

infrastructure/poc/
├── docker-compose-connect.yml           # 原文件，未修改
└── docker-compose.override.yml          # 新建，注入 jmx_exporter
```
