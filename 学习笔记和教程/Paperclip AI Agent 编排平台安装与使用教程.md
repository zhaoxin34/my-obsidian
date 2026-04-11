> 本教程详细讲解 Paperclip 的安装、配置与核心使用方法。
> 配套分析报告：[[Paperclip AI Agent 编排平台分析报告]]

- [[#一、环境要求]]
- [[#二、安装方式]]
- [[#三、快速开始]]
- [[#四、Web 界面使用指南]]
- [[#五、核心概念与操作流程]]
- [[#六、集成 OpenClaw]]
- [[#七、配置与管理]]
- [[#八、常见问题]]
- [[#九、Docker 完整部署]]

---

## 一、环境要求

### 1.1 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 10 GB | 20 GB+ |
| 网络 | 稳定的互联网连接（用于调用 LLM API） | 同左 |

### 1.2 软件依赖

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Node.js | 18.x+ | 后端运行时 |
| pnpm | 8.x+ | 推荐使用 pnpm 作为包管理器 |
| PostgreSQL | 15.x+ | 数据库（内置 SQLite 或 Docker PostgreSQL） |
| Docker | 24.x+（可选） | 用于容器化部署 |

### 1.3 API Key 准备

Paperclip 本身不提供 LLM 模型，你需要准备以下 API Key 之一：

- **OpenAI API Key** - 用于 GPT 系列模型
- **Anthropic API Key** - 用于 Claude 系列模型
- **其他兼容 OpenAI API 格式的 provider**

---

## 二、安装方式

### 方式一：npx 一键启动（推荐新手）

最简单的安装方式，使用官方 CLI 一键配置：

```bash
# 全局安装 CLI 工具
npm install -g paperclipai

# 或者直接使用 npx（无需安装）
npx paperclipai onboard --yes
```

`--yes` 参数表示自动接受默认配置，跳过交互式问答。

> ⚠️ 注意：一键启动会自动下载并配置所有依赖，首次运行可能需要几分钟。

### 方式二：Git 克隆 + Docker Compose（推荐生产环境）

适合想要完全掌控部署的用户，支持群晖 NAS 或任何 Linux 服务器。

#### 2.2.1 克隆项目

```bash
# 克隆官方仓库
git clone https://github.com/paperclipai/paperclip.git

# 进入项目目录
cd paperclip
```

#### 2.2.2 目录结构

```
paperclip/
├── docker-compose.quickstart.yml   # 快速启动配置
├── docker-compose.yml              # 完整配置
├── server/                         # 后端服务
├── ui/                            # 前端界面
└── packages/                       # 共享包
```

### 方式三：手动本地开发

如果需要修改源码或进行二次开发：

```bash
# 1. 克隆项目
git clone https://github.com/paperclipai/paperclip.git
cd paperclip

# 2. 安装依赖
pnpm install

# 3. 配置环境变量
cp .env.example .env

# 4. 编辑 .env 文件，填入必要的配置
# DATABASE_URL=postgres://...
# OPENAI_API_KEY=sk-...
# BETTER_AUTH_SECRET=your-secret-key

# 5. 启动开发服务器
pnpm dev
```

#### .env 配置文件示例

```bash
# 数据库连接
DATABASE_URL=postgres://paperclip:paperclip@localhost:5432/paperclip

# 服务端口
PORT=3100

# 启用 UI
SERVE_UI=true

# 认证模式
PAPERCLIP_DEPLOYMENT_MODE=authenticated
PAPERCLIP_DEPLOYMENT_EXPOSURE=private
PAPERCLIP_PUBLIC_URL=http://localhost:3100

# 认证密钥（生成随机字符串）
BETTER_AUTH_SECRET=your-super-secret-key-here-min-32-chars

# LLM API Keys（至少需要一个）
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

---

## 三、快速开始

### 3.1 启动服务

```bash
# 使用 Docker Compose 快速启动
docker compose -f docker-compose.quickstart.yml up --build
```

### 3.2 访问 Web 界面

启动成功后，在浏览器中访问：

```
http://localhost:3100
```

首次访问时需要创建管理员账户。

### 3.3 Web 界面概览

```mermaid
graph LR
    A["侧边栏<br/>公司列表<br/>导航菜单"] --> B["主内容区<br/>组织架构图<br/>任务列表<br/>成本仪表盘"]
    B --> C["顶部栏<br/>搜索<br/>通知<br/>用户设置"]
```

---

## 四、Web 界面使用指南

### 4.1 仪表盘（Dashboard）

登录后的主界面，显示关键指标：

| 指标 | 说明 |
|------|------|
| **活跃 Agent** | 当前正在运行的 Agent 数量 |
| **本月成本** | 所有 Agent 本月累计消耗 |
| **待处理任务** | 等待执行的任务数 |
| **目标进度** | 公司级目标的完成度 |

### 4.2 组织架构（Org Chart）

查看和管理公司的组织结构：

1. 点击侧边栏「组织架构」
2. 查看公司层级图
3. 点击角色查看详情
4. 拖拽调整上下级关系

### 4.3 任务管理（Tasks）

#### 创建任务

1. 点击「新建任务」按钮
2. 填写任务信息：

```yaml
标题: "撰写产品介绍文章"
描述: "为我们的 SaaS 产品写一篇 1500 字的产品介绍"
分配给: [选择 Agent]
截止日期: [选择日期]
优先级: [高/中/低]
关联目标: [选择目标]
```

3. 点击「创建」

#### 任务状态流转

```mermaid
stateDiagram-v2
    [*] --> 待分配: 创建任务
    待分配 --> 进行中: Agent 接单
    进行中 --> 待审核: 完成
    待审核 --> 进行中: 退回修改
    待审核 --> 已完成: 审批通过
    已完成 --> [*]
```

### 4.4 成本管理（Costs）

#### 设置 Agent 预算

1. 进入「Agent」页面
2. 选择目标 Agent
3. 在「预算设置」中配置：

```yaml
月度预算: 100 美元
预警阈值: 80%
超限动作: 自动暂停
```

#### 查看成本报告

- **日/周/月视图**：切换时间维度查看成本趋势
- **按 Agent 分组**：查看每个 Agent 的成本占比
- **按任务分组**：查看每个任务的实际消耗

### 4.5 目标管理（Goals）

#### 创建公司目标

```yaml
目标名称: "Q2 月收入 50 万"
目标类型: OKR
关键结果:
  - KR1: 新增 100 个付费客户
  - KR2: 客户留存率达到 90%
  - KR3: 平均客单价提升 20%
截止日期: 2026-06-30
负责人: CEO Agent
```

目标会自动分解为子任务，并分配给相应的 Agent。

---

## 五、核心概念与操作流程

### 5.1 操作流程总览

```mermaid
flowchart TD
    A["1. 创建公司"] --> B["2. 定义组织架构"]
    B --> C["3. 雇佣 Agent"]
    C --> D["4. 设置预算"]
    D --> E["5. 设定目标"]
    E --> F["6. 分配任务"]
    F --> G["7. Agent 执行"]
    G --> H["8. 监控与审批"]
    H --> I["9. 审计与复盘"]
    I --> F

    H -->|"超预算| J["自动暂停"]
    J -->|"调整预算| F"
```

### 5.2 雇佣新 Agent

1. 进入「Agent」页面
2. 点击「雇佣 Agent」

#### 选择 Agent 类型

| 类型 | 说明 | 配置项 |
|------|------|--------|
| **OpenClaw** | 多渠道 AI 网关 | 设备密钥 |
| **Claude Code** | Anthropic CLI Agent | API Key |
| **Codex** | OpenAI 代码 Agent | API Key |
| **Cursor** | AI 代码编辑器 | 本地 API |
| **Bash** | 自定义脚本 | 命令模板 |
| **HTTP** | 外部 API 服务 | URL + 认证 |

3. 填写 Agent 配置
4. 选择岗位角色
5. 设置权限范围
6. 点击「雇佣」

### 5.3 配置审批流程

对于敏感操作，可以设置多级审批：

```yaml
审批规则配置:
  任务创建:
    - 金额 > $100: 需要 CEO 审批
    - 涉及外部 API: 需要人工确认

  预算调整:
    - 上调 > 20%: 需要董事会审批
    - 上调 <= 20%: 部门经理审批

  Agent 招聘:
    - 月成本 > $500: 董事会审批
    - 月成本 <= $500: 自动批准
```

---

## 六、集成 OpenClaw

OpenClaw 是 Paperclip 官方推荐的 Agent 运行时，提供多渠道接入（WhatsApp、Telegram、Discord 等）。

### 6.1 Docker 一键启动 OpenClaw UI

Paperclip 提供了便捷脚本，一键启动 OpenClaw Docker 容器：

```bash
# 在 paperclip 项目目录下执行
./scripts/smoke/openclaw-docker-ui.sh
```

该脚本会自动：
1. 拉取或构建 OpenClaw Docker 镜像
2. 配置网络确保与 Paperclip 的通信
3. 打印可在浏览器访问的仪表板 URL

### 6.2 生成 OpenClaw 邀请

作为 CEO 角色，按以下步骤生成 OpenClaw 邀请：

1. 访问 Paperclip 仪表板
2. 导航至公司设置
3. 选择「邀请新员工」→「OpenClaw」类型
4. 系统生成邀请链接和设备密钥

### 6.3 OpenClaw 端配置

在 OpenClaw 侧配置连接信息：

```bash
# 设置 Paperclip 服务器地址
PAPERCLIP_URL=http://your-paperclip-server:3100

# 设置设备密钥
PAPERCLIP_DEVICE_KEY=your-device-key

# 启动 OpenClaw
openclaw start
```

### 6.4 网络注意事项

> ⚠️ 在 Docker 环境中需要注意网络访问的特殊性：
>
> - OpenClaw 容器内部的 `127.0.0.1` 指向容器本身，而非主机的 Paperclip 服务器
> - 对于 OpenClaw Docker 使用的邀请/入职 URL，应使用脚本打印的 Paperclip URL（通常为 `http://host.docker.internal:3100`）

---

## 七、配置与管理

### 7.1 数据库配置

#### 使用嵌入式 SQLite（开发环境）

```bash
DATABASE_URL=file:./paperclip.db
```

#### 使用外部 PostgreSQL（生产环境）

```bash
DATABASE_URL=postgres://paperclip:paperclip@db:5432/paperclip
```

### 7.2 认证配置

```bash
# 公开部署（不推荐）
PAPERCLIP_DEPLOYMENT_MODE=public
PAPERCLIP_DEPLOYMENT_EXPOSURE=public

# 私有部署（推荐）
PAPERCLIP_DEPLOYMENT_MODE=authenticated
PAPERCLIP_DEPLOYMENT_EXPOSURE=private

# 公网部署 + 认证
PAPERCLIP_DEPLOYMENT_MODE=authenticated
PAPERCLIP_DEPLOYMENT_EXPOSURE=public
BETTER_AUTH_SECRET=your-32-char-secret
```

### 7.3 多公司配置

Paperclip 支持在同一实例中运行多个独立公司：

```bash
# 启用多租户
PAPERCLIP_MULTI_TENANT=true

# 公司数据隔离通过数据库 schema 实现
```

---

## 八、常见问题

### Q1: 端口 3100 被占用

```bash
# 方式一：修改端口
PORT=3101 docker compose -f docker-compose.quickstart.yml up

# 方式二：查找占用进程
lsof -i :3100

# 杀死占用进程
kill -9 <PID>
```

### Q2: 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 如果没有运行，启动它
docker compose up -d db

# 检查连接字符串是否正确
cat .env | grep DATABASE_URL
```

### Q3: 依赖安装失败

```bash
# 清理缓存
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install

# 如果还是失败，使用淘宝镜像
pnpm config set registry https://registry.npmmirror.com
pnpm install
```

### Q4: Agent 不工作

1. **检查心跳状态**：确认 Agent 已连接并能接收心跳
2. **检查 API Key**：验证 API Key 是否有效且有余额
3. **查看日志**：

```bash
# 查看服务器日志
docker compose logs -f server

# 查看特定 Agent 日志
docker compose logs -f --tail=100 server | grep "agent-name"
```

### Q5: 如何完全重置？

```bash
# 停止所有服务
docker compose down

# 删除数据卷（注意：这会删除所有数据！）
docker volume rm paperclip_pgdata

# 重新启动
docker compose -f docker-compose.quickstart.yml up --build
```

---

## 九、Docker 完整部署

### 9.1 docker-compose.quickstart.yml 详解

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  db:
    image: postgres:17-alpine
    container_name: paperclip-db
    restart: unless-stopped
    volumes:
      - ./pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: paperclip
      POSTGRES_PASSWORD: paperclip
      POSTGRES_DB: paperclip
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U paperclip -d paperclip"]
      interval: 2s
      timeout: 5s
      retries: 30

  # Paperclip 主服务
  server:
    image: tuyenvd/paperclip:latest
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
      PAPERCLIP_PUBLIC_URL: "http://你的IP:3100"
      BETTER_AUTH_SECRET: "请替换为你的密钥"
      OPENAI_API_KEY: "sk-your-openai-key"
    depends_on:
      db:
        condition: service_healthy
```

### 9.2 部署到云服务器

#### 部署到 Linux 服务器

```bash
# 1. 在服务器上安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 安装 Docker Compose
apt install docker-compose

# 3. 创建部署目录
mkdir -p /opt/paperclip
cd /opt/paperclip

# 4. 下载 docker-compose.yml
wget https://raw.githubusercontent.com/paperclipai/paperclip/main/docker-compose.quickstart.yml

# 5. 编辑配置
vim docker-compose.quickstart.yml

# 6. 启动服务
docker-compose up -d

# 7. 查看日志
docker-compose logs -f
```

#### 部署到群晖 NAS

1. 在「套件中心」安装 Docker
2. 在 File Station 创建共享文件夹：`/volume1/docker/paperclip/`
3. 下载 `docker-compose.quickstart.yml` 到该目录
4. 在 Docker 应用中使用「docker-compose」方式启动

### 9.3 使用 Zeabur 一键部署

Paperclip 支持在 Zeabur 平台一键部署：

1. 访问 [zeabur.com](https://zeabur.com)
2. 连接到 GitHub
3. 选择 Paperclip 仓库
4. 一键部署，无需配置服务器

---

## 附录：常用命令速查

```bash
# 启动服务
docker compose -f docker-compose.quickstart.yml up -d

# 停止服务
docker compose -f docker-compose.quickstart.yml down

# 查看日志
docker compose -f docker-compose.quickstart.yml logs -f

# 重启服务
docker compose -f docker-compose.quickstart.yml restart

# 进入容器
docker exec -it paperclip-web sh

# 数据库迁移
docker exec -it paperclip-web pnpm db:migrate

# 更新镜像
docker compose -f docker-compose.quickstart.yml pull
docker compose -f docker-compose.quickstart.yml up -d
```

---

*本文档由 Claude Code 生成，最后更新：2026 年 4 月*
