> 本文档记录 Paperclip 从安装到成功运行的全过程，包括踩过的坑和解决方案。
> 系统环境：macOS Darwin 24.6.0，Apple Silicon M2

---

## 一、安装方式选择

Paperclip 提供三种安装方式：

| 方式 | 适合人群 | 复杂度 |
|------|----------|--------|
| npx 一键启动 | 新手、无技术背景 | ⭐ 最简单 |
| Docker Compose | 有服务器、追求部署可控 | ⭐⭐ 较简单 |
| 手动本地开发 | 开发者、需要二次开发 | ⭐⭐⭐ 复杂 |

**本次采用 Docker Compose 方式**，配置文件放在 `~/working/docker/paperclip/`。

---

## 二、先决条件

### 2.1 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 10 GB | 20 GB+ |

### 2.2 软件依赖

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Docker | 24.x+ | 必须 |
| Node.js | 18.x+ | 可选（开发用） |
| pnpm | 8.x+ | 可选（开发用） |

### 2.3 API Key 准备

Paperclip 不提供 LLM 模型，需要准备以下之一：

- **OpenAI API Key** - GPT 系列模型
- **Anthropic API Key** - Claude 系列模型
- **其他兼容 OpenAI API 格式的 provider**

本次使用 MiniMax 的 Anthropic 兼容 API：
```bash
ANTHROPIC_API_KEY=sk-cp-myfB6u4psXdcHDjTty3stOKIm8OcXJJ34cnPS6nT444CiOQu6vNBEq0WPIMhGXcBZqBPoeRbVF2vk9VU8kSXBRRd7RfnPg8ZjjvC9zdGuian3wiQoxF5JpU
ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
```

---

## 三、安装步骤

### 3.1 创建目录结构

```bash
mkdir -p /Users/zhaoxin/working/docker/paperclip/data
```

### 3.2 设置代理（如果网络无法访问 GitHub）

由于国内网络无法直接访问 GitHub，需要设置代理：

```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
```

### 3.3 克隆源码

```bash
cd /Users/zhaoxin/working/docker/paperclip
git clone https://github.com/paperclipai/paperclip.git --depth 1
```

### 3.4 创建 docker-compose.yml

```yaml
services:
  # PostgreSQL 数据库
  db:
    image: postgres:17-alpine
    container_name: paperclip-db
    restart: unless-stopped
    volumes:
      - ./data/pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: paperclip
      POSTGRES_PASSWORD: paperclip
      POSTGRES_DB: paperclip
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U paperclip -d paperclip"]
      interval: 2s
      timeout: 5s
      retries: 30

  # Paperclip 主服务（从本地源码构建）
  server:
    build:
      context: ./paperclip
      dockerfile: Dockerfile
    image: paperclip:local
    container_name: paperclip-web
    restart: unless-stopped
    ports:
      - "3100:3100"
    volumes:
      - ./data:/paperclip
    environment:
      DATABASE_URL: postgres://paperclip:paperclip@db:5432/paperclip
      PORT: "3100"
      SERVE_UI: "true"
      PAPERCLIP_DEPLOYMENT_MODE: "authenticated"
      PAPERCLIP_DEPLOYMENT_EXPOSURE: "private"
      PAPERCLIP_PUBLIC_URL: "http://localhost:3100"
      BETTER_AUTH_SECRET: "paperclip-dev-secret-change-in-production"
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
      ANTHROPIC_BASE_URL: "${ANTHROPIC_BASE_URL:-https://api.anthropic.com}"
    depends_on:
      db:
        condition: service_healthy
```

### 3.5 创建 .env 配置文件

```bash
# Paperclip 配置文件

# 数据库连接
DATABASE_URL=postgres://paperclip:paperclip@db:5432/paperclip

# 服务端口
PORT=3100

# 启用 UI
SERVE_UI=true

# 认证模式 - 私有部署
PAPERCLIP_DEPLOYMENT_MODE=authenticated
PAPERCLIP_DEPLOYMENT_EXPOSURE=private
PAPERCLIP_PUBLIC_URL=http://localhost:3100

# 认证密钥
BETTER_AUTH_SECRET=paperclip-dev-secret-change-in-production

# LLM API 配置
ANTHROPIC_API_KEY=sk-cp-myfB6u4psXdcHDjTty3stOKIm8OcXJJ34cnPS6nT444CiOQu6vNBEq0WPIMhGXcBZqBPoeRbVF2vk9VU8kSXBRRd7RfnPg8ZjjvC9zdGuian3wiQoxF5JpU
ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
```

### 3.6 修改 Dockerfile（重要！）

> ⚠️ **踩坑点 #1**：官方 Dockerfile 中的 GitHub CLI 安装步骤会导致构建失败

官方 Dockerfile 在安装 GitHub CLI 时会校验 GPG 密钥，由于网络问题会失败。需要修改 Dockerfile：

**原内容（第 4-15 行）：**
```dockerfile
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates gosu curl git wget ripgrep python3 \
  && mkdir -p -m 755 /etc/apt/keyrings \
  && wget -nv -O/etc/apt/keyrings/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && echo "20e0125d6f6e077a9ad46f03371bc26d90b04939fb95170f5a1905099cc6bcc0  /etc/apt/keyrings/githubcli-archive-keyring.gpg" | sha256sum -c - \
  && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends gh \
  && rm -rf /var/lib/apt/lists/* \
  && corepack enable
```

**修改为：**
```dockerfile
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates gosu curl git wget ripgrep python3 \
  && rm -rf /var/lib/apt/lists/* \
  && corepack enable
```

### 3.7 构建镜像

```bash
cd /Users/zhaoxin/working/docker/paperclip
docker compose build
```

### 3.8 启动服务

```bash
docker compose up -d
```

### 3.9 初始化配置

进入容器执行初始化：

```bash
docker exec paperclip-web pnpm paperclipai onboard --yes
```

会生成 CEO 邀请链接，格式如：
```
http://localhost:3100/invite/pcp_bootstrap_xxxxxxx
```

---

## 四、踩坑记录

### 坑 #1：预构建镜像缺少文件

**问题描述：**
使用 `tuyenvd/paperclip:latest` 预构建镜像时，创建 Agent 会报错：
```
ENOENT: no such file or directory, open '/app/server/dist/onboarding-assets/ceo/AGENTS.md'
```

**原因分析：**
预构建镜像 `tuyenvd/paperclip:latest` 缺少构建产物文件。

**解决方案：**
从 GitHub 克隆源码本地构建，不使用预构建镜像。

---

### 坑 #2：GitHub CLI GPG 密钥校验失败

**问题描述：**
Dockerfile 构建过程中，GitHub CLI 的 GPG 密钥校验失败：
```
sha256sum: WARNING: 1 computed checksum did NOT match
/etc/apt/keyrings/githubcli-archive-keyring.gpg: FAILED
```

**原因分析：**
网络问题导致 GPG 密钥下载不完整或被篡改。

**解决方案：**
修改 Dockerfile，移除 GitHub CLI 安装步骤（不是运行所必需的）。

---

### 坑 #3：国内网络无法访问 GitHub

**问题描述：**
直接执行 `git clone https://github.com/paperclipai/paperclip.git` 会失败：
```
fatal: unable to access 'https://github.com/paperclipai/paperclip.git/': Failed to connect to github.com port 443 after 29380 ms: Couldn't connect to server
```

**解决方案：**
使用代理：
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
```

---

### 坑 #4：端口被占用

**问题描述：**
启动时提示端口 3100 被占用：
```
! Server port: Port 3100 is already in use
```

**解决方案：**
```bash
# 查找占用进程
lsof -i :3100

# 杀死占用进程
kill -9 <PID>

# 或者修改 docker-compose.yml 使用其他端口
```

---

## 五、常用命令

### 启动服务
```bash
cd /Users/zhaoxin/working/docker/paperclip && docker compose up -d
```

### 停止服务
```bash
cd /Users/zhaoxin/working/docker/paperclip && docker compose down
```

### 查看日志
```bash
cd /Users/zhaoxin/working/docker/paperclip && docker compose logs -f
```

### 查看服务状态
```bash
cd /Users/zhaoxin/working/docker/paperclip && docker compose ps
```

### 进入容器
```bash
docker exec -it paperclip-web sh
```

### 关闭代理（用完 GitHub 后）
```bash
unset https_proxy http_proxy all_proxy
```

---

## 六、验证安装

访问 http://localhost:3100 ，正常情况下应该看到 Dashboard 页面，显示：

- 1 Agents Enabled
- 0 running, 0 paused, 0 errors
- $0.00 Month Spend
- 0 Pending Approvals

---

## 七、相关文档

- 官方文档：https://docs.paperclip.ing/
- GitHub 仓库：https://github.com/paperclipai/paperclip

---

*本文档最后更新：2026 年 4 月*
