# Pi Coding Agent 入门教程

> 一个极简终端编码助手，让你的工作流适应你，而不是反过来。

## 简介

Pi 是一个极简的终端编码助手，核心理念是「原语（Primitives），不是功能」——其他 Agent 内置的功能，你可以自己构建。Pi 保持核心精简，通过扩展（Extensions）、技能（Skills）、提示模板（Prompt Templates）和主题（Themes）来适应你的工作流。

### 主要特点

| 特性 | 说明 |
|------|------|
| **15+ 提供商，百种模型** | Anthropic、OpenAI、Google、Azure、Bedrock、Mistral、Groq、Cerebras、xAI、MiniMax 等 |
| **四 种模式** | 交互模式、打印/JSON 模式、RPC 模式、SDK 模式 |
| **树形会话历史** | 可回溯、可分支、可分享的会话树 |
| **渐进式上下文** | Skills 按需加载，不撑爆提示词缓存 |
| **自举能力强** | 让 Pi 自己构建扩展，修改自身 |

### 设计原则

Pi 刻意不内置以下功能，保持核心精简：

- **无 MCP** — 用 Skills 构建 CLI 工具，或构建扩展添加 MCP 支持
- **无子代理** — 通过 tmux 或扩展实现
- **无权限弹窗** — 在容器中运行或自行构建确认流程
- **无计划模式** — 写计划到文件，或构建扩展实现
- **无内置待办** — 使用 TODO.md 或扩展

## 安装

### 方式一：安装脚本

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

### 方式二：npm/pnpm/bun

```bash
npm install -g @mariozechner/pi-coding-agent
# 或
pnpm add -g @mariozechner/pi-coding-agent
# 或
bun add -g @mariozechner/pi-coding-agent
```

安装完成后，在项目目录中运行：

```bash
cd /path/to/project
pi
```

## 认证配置

### 方式一：订阅登录

```bash
pi
/login
```

然后选择提供商。支持：
- ChatGPT Plus/Pro (Codex)
- Claude Pro/Max
- GitHub Copilot

### 方式二：API Key

通过环境变量设置：

```bash
export ANTHROPIC_API_KEY=sk-ant-... pi
```

或在 `~/.pi/agent/auth.json` 中存储：

```json
{
  "anthropic": {
    "type": "api_key",
    "key": "sk-ant-..."
  }
}
```

支持的 API Key 提供商：

| 提供商 | 环境变量 |
|--------|----------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| xAI | `XAI_API_KEY` |
| MiniMax | `MINIMAX_API_KEY` |
| Hugging Face | `HF_TOKEN` |

## 交互模式

启动后，你会看到四个主要区域：

- **启动头部** — 快捷键、加载的上下文文件、提示模板、Skills、扩展
- **消息区** — 用户消息、助手响应、工具调用、通知、错误
- **编辑器** — 输入区域，边框颜色表示当前思考级别
- **底部栏** — 工作目录、会话名、Token/缓存使用量、成本、上下文使用量、当前模型

### 编辑器功能

| 功能 | 操作方式 |
|------|----------|
| 引用文件 | 输入 `@` 模糊搜索项目文件 |
| 路径补全 | 按 Tab 补全路径 |
| 多行输入 | Shift+Enter 或 Ctrl+Enter |
| 图片粘贴 | Ctrl+V（Windows 为 Alt+V）或拖拽 |
| 执行命令 | `!command` 执行并发送给模型 |
| 隐藏命令 | `!!command` 执行但不发送给模型 |
| 外部编辑器 | Ctrl+G 打开 `$VISUAL` 或 `$EDITOR` |

### 斜杠命令

| 命令 | 说明 |
|------|------|
| `/login`, `/logout` | 管理 OAuth 或 API Key 凭证 |
| `/model` | 切换模型 |
| `/scoped-models` | 启用/禁用 Ctrl+P 循环的模型 |
| `/settings` | 思考级别、主题、消息传递、传输方式 |
| `/resume` | 选择之前的会话继续 |
| `/new` | 开始新会话 |
| `/session` | 显示会话文件、ID、消息、Token、成本 |
| `/tree` | 跳转到会话树中的任意点继续 |
| `/fork` | 从之前的用户消息创建新会话 |
| `/clone` | 将当前活跃分支复制到新会话文件 |
| `/compact` | 手动压缩上下文 |
| `/export` | 将会话导出为 HTML |
| `/share` | 上传到 GitHub Gist 获取分享链接 |
| `/reload` | 重新加载快捷键、扩展、Skills、提示模板和上下文文件 |
| `/quit` | 退出 Pi |

### 消息队列

在 agent 工作时可以提交消息：

- **Enter** — 排队转向消息，在当前助手完成工具调用后送达
- **Alt+Enter** — 排队后续消息，在 agent 完成所有工作后送达
- **Escape** — 中止并将排队的消息恢复到编辑器
- **Alt+Up** — 将排队的消息取回编辑器

## 四种运行模式

### 1. 交互模式（默认）

```bash
pi
```

完整的 TUI 体验。

### 2. 打印/JSON 模式

```bash
pi -p " Summarize this codebase"
cat README.md | pi -p "Summarize this text"
pi -p @screenshot.png "What's in this image?"
pi --mode json  # JSON 事件流
```

用于脚本和非交互式场景。

### 3. RPC 模式

```bash
pi --mode rpc
```

通过 stdin/stdout 的 JSON 协议集成到其他应用。参见 [OpenClaw](https://github.com/OpenClaw/OpenClaw) 真实案例。

### 4. SDK 模式

将 Pi 嵌入 Node.js 应用。

## 会话管理

Sessions 保存在 `~/.pi/agent/sessions/`，按工作目录组织。

```bash
pi -c           # 继续最近的会话
pi -r           # 浏览并选择会话
pi --session <id>   # 打开特定会话
pi --no-session # 临时模式，不保存
pi --fork <id>  # 分叉会话到新会话文件
```

## 上下文工程

Pi 的最小系统提示和可扩展性让你实现真正的上下文工程。

### AGENTS.md / CLAUDE.md

在以下位置添加项目指令：

- `~/.pi/agent/AGENTS.md` — 全局指令
- 父目录和当前目录 — 项目指令

```markdown
# 项目指令
- 代码修改后运行 `npm run check`
- 不要在本地运行生产环境迁移
- 保持回复简洁
```

### SYSTEM.md

替换或追加系统提示：

- `.pi/SYSTEM.md` — 项目级别
- `~/.pi/agent/SYSTEM.md` — 全局级别

使用 `APPEND_SYSTEM.md` 可以追加到默认提示而不是替换。

### 压缩（Compaction）

当接近上下文限制时，Pi 自动压缩旧消息。可以自定义压缩逻辑：

- 实现基于主题的压缩
- 代码感知摘要
- 使用不同的摘要模型

## 扩展（Extensions）

扩展是 TypeScript 模块，可访问工具、命令、键盘快捷键、事件和完整 TUI。

### 内置功能示例

你可以通过扩展构建以下功能：

- **子代理** — 参见 `subagent/` 示例
- **计划模式** — 参见 `plan-mode/` 示例
- **权限门** — 执行 `rm -rf`、`sudo` 等前确认
- **路径保护** — 阻止写入 `.env`、`node_modules/`
- **SSH 执行** — 远程执行命令
- **沙箱** — 隔离执行环境
- MCP 集成、自定义编辑器、状态栏、覆盖层

### 示例：让 Pi 自己构建扩展

```
pi can create extensions. Ask it to build one for your use case.
```

Pi 可以自己构建扩展！直接让它为你构建。

### 安装位置

```bash
~/.pi/agent/extensions/  # 全局
.pi/extensions/          # 项目本地
```

使用 `/reload` 热重载。

## 技能（Skills）

Skills 是按需加载的能力包，提供专业工作流、设置说明、辅助脚本和参考文档。

### 安装 Skills

Pi 实现 [Agent Skills 标准](https://agentskills.io/specification)。

```bash
~/.pi/agent/skills/
~/.agents/skills/
.pi/skills/
.agents/skills/
skills/
```

### 使用 Skills

```
/skill:brave-search         # 加载并执行
/skill:pdf-tools extract    # 带参数执行
```

### 与 Claude Code Skills 兼容

```json
// settings.json
{
  "skills": ["~/.claude/skills"]
}
```

## 提示模板（Prompt Templates）

可重用的提示模板，输入 `/name` 展开。

```bash
.prompt-templates/
```

## 主题（Themes）

```bash
pi --theme <theme-name>
```

## 切换模型

```bash
/model       # 选择模型
Ctrl+L       # 同上
Ctrl+P       # 在 scoped models 中循环
Shift+Tab    # 循环思考级别
```

支持的提供商（15+）：

- Anthropic
- OpenAI
- Google
- Azure
- Bedrock
- Mistral
- Groq
- Cerebras
- xAI
- Hugging Face
- Kimi For Coding
- MiniMax
- OpenRouter
- Ollama

## CLI 参考

### 基本用法

```bash
pi [options] [@files...] [messages...]
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `-p`, `--print` | 打印响应并退出 |
| `--mode json` | JSON 事件流输出 |
| `--mode rpc` | RPC 模式 |
| `-c`, `--continue` | 继续最近会话 |
| `-r`, `--resume` | 浏览并选择会话 |
| `--session <id>` | 使用特定会话 |
| `--no-session` | 临时模式，不保存 |
| `--provider <p>` | 提供商，如 `anthropic`、`openai` |
| `--model <m>` | 模型模式或 ID |
| `--thinking <level>` | 思考级别：`off`、`minimal`、`low`、`medium`、`high`、`xhigh` |
| `-e`, `--extension` | 从路径、npm 或 git 加载扩展 |
| `--skill <name>` | 加载技能 |
| `-h`, `--help` | 显示帮助 |
| `-v`, `--version` | 显示版本 |

### 工具选项

| 选项 | 说明 |
|------|------|
| `--tools, -t` | 允许特定工具 |
| `--no-builtin-tools, -nbt` | 禁用内置工具 |
| `--no-tools, -nt` | 禁用所有工具 |

内置工具：`read`、`bash`、`edit`、`write`、`grep`、`find`、`ls`

### 环境变量

| 变量 | 说明 |
|------|------|
| `PI_CODING_AGENT_DIR` | 覆盖配置目录（默认 `~/.pi/agent`） |
| `PI_CODING_AGENT_SESSION_DIR` | 覆盖会话存储目录 |
| `ANTHROPIC_API_KEY` | Anthropic API Key |
| `OPENAI_API_KEY` | OpenAI API Key |
| `PI_OFFLINE` | 禁用启动时网络操作 |
| `PI_SKIP_VERSION_CHECK` | 跳过版本更新检查 |
| `PI_TELEMETRY` | 覆盖安装/更新遥测 |

## 实际应用示例

### 示例 1：自定义工作流扩展

让 Pi 构建一个自定义工作流扩展来简化提交流程：

```
Here we ask Pi to build a custom workflow extension with custom TUI to streamline the commit and push process.
```

### 示例 2：第三方扩展

使用 [@termdraw/pi](https://github.com/benvinegar/termdraw/) 第三方扩展实现绘图功能。

### 示例 3：玩游戏

Pi 甚至可以运行 DOOM！通过第三方扩展实现。

## 参考资源

- **官网**: https://pi.dev/
- **文档**: https://pi.dev/docs/latest
- **GitHub**: https://github.com/badlogic/pi-mono
- **Discord**: [社区服务器](https://discord.com/invite/nKXTsAcmbT)
- **包列表**: https://pi.dev/packages
- **博客文章**: [What we didn't build](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

## 总结

Pi 的核心理念是「让工具适应你，而不是反过来」。与 Claude Code 等功能完备的 Agent 框架不同，Pi 选择保持核心精简，把功能实现的选择权交给你。通过扩展、Skills、提示模板和主题，你可以打造完全符合自己工作流的 AI 编码助手。

如果你喜欢高度可定制、极简风格的终端编码工具，Pi 值得一试。
