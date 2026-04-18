# Saleor 安装配置

## 简介

Saleor 是一个开源的电商平台，使用 Docker Compose 部署。

官方文档：https://docs.saleor.io/setup/docker-compose

## 环境准备

- Docker Desktop 已安装
- 至少 5GB 内存分配给 Docker

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/saleor/saleor-platform.git
cd saleor-platform
```

### 2. 配置 Docker Desktop（macOS）

Docker Desktop → Settings → Resources → File sharing
添加 `saleor-platform` 目录

### 3. 修复镜像版本问题

`ghcr.io/saleor/saleor-dashboard:3.23` 标签不存在，需要使用 `latest`：

```bash
sed -i '' 's/saleor-dashboard:3.23/saleor-dashboard:latest/' docker-compose.yml
```

### 4. 修复端口冲突

如果本地 6379 端口被占用（如 Docker Desktop 自带 Redis），需要修改 valkey 端口：

编辑 `docker-compose.yml`，将：
```yaml
- 6379:6379
```
改为：
```yaml
- 6380:6379
```

### 5. 拉取镜像

```bash
docker compose pull
```

### 6. 应用数据库迁移

```bash
docker compose run --rm api python3 manage.py migrate
```

### 7. 创建管理员账户和示例数据

```bash
docker compose run --rm api python3 manage.py populatedb --createsuperuser
```

### 8. 启动服务

```bash
docker compose up
```

## 服务地址

| 服务 | URL |
|------|-----|
| Dashboard | http://localhost:9000 |
| API | http://localhost:8000 |
| Jaeger (APM) | http://localhost:16686 |
| Mailpit (邮件测试) | http://localhost:8025 |

## 登录信息

- Email: `admin@example.com`
- Password: `admin`

## Docker Compose 服务说明

| 服务 | 镜像 | 用途 |
|------|------|------|
| api | saleor:3.23 | Saleor Core GraphQL API |
| dashboard | saleor-dashboard:latest | 管理后台 Web UI |
| db | postgres:15-alpine | PostgreSQL 数据库 |
| cache | valkey:8.1-alpine | Valkey（Redis fork）缓存 |
| worker | saleor:3.23 | Celery 异步任务处理器 |
| jaeger | jaegertracing/jaeger | 分布式追踪 |
| mailpit | axllent/mailpit | 本地 SMTP 测试服务器 |

## 常见问题

### Q: 端口 6379 被占用

A: 是 Docker Desktop 自带 Redis 占用，修改 docker-compose.yml 中 cache 服务的端口映射为 `6380:6379`

### Q: dashboard 镜像拉取失败

A: `3.23` 标签不存在，使用 `latest` 标签
