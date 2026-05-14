> Pi Coding Agent 的子代理扩展，支持链式调用、并行执行和 TUI 澄清流程。

## 简介

pi-subagents 让 Pi 能够将工作委托给专注的子代理（child agents）。适用于代码审查、代码侦查（Scouting）、实现工作、并行审计、保存的工作流、后台任务，以及任何需要多个模型视角的场景。

## 安装

```bash
pi install npm:pi-subagents
```

这是唯一必需的步骤，可以后续再添加可选组件。

## 快速上手

安装后，用自然语言让 Pi 委托任务：

```
让 reviewer 审查这个 diff。
问问 oracle 对我当前计划的看法。
用 scout 理解这段代码，然后问我澄清问题。
运行并行 reviewer：一个审查正确性，一个审查测试，一个审查不必要的复杂性。
```

## 工作原理

- **Pi** 是父会话（parent session）
- **子代理** 是一个专注的子 Pi 会话，有自己的任务

当你请求子代理时，Pi 启动子代理、给它任务，然后把结果带回来。前台运行在对话中流式输出。后台运行继续工作，可以稍后检查结果。

## 推荐工作流

推荐的实现循环模式：

```
clarify → planner → worker → fresh reviewers → worker
```

## 内置代理（用自然语言描述）

| 代理 | 使用场景 |
|------|---------|
| **scout** | 快速的本地代码库侦查：相关文件、入口点、数据流、风险，以及其他代理应该从哪里开始。 |
| **researcher** | 网络/文档研究，带来源：官方文档、规格说明、基准测试、最近变更，以及简洁的研究摘要。 |
| **planner** | 基于现有上下文的具体实现计划。它只读取和规划，不编辑代码。 |
| **worker** | 实现工作，包括已批准的 oracle 移交。它编辑文件、验证，并在未批准决策时升级而不是猜测。 |
| **reviewer** | 代码审查和小修复。它根据任务/计划、测试、边缘情况和简洁性检查实现。 |
| **context-builder** | 规划前的更强设置传递：收集代码上下文，编写交接材料如 context.md 和 meta-prompt.md。 |
| **oracle** | 行动前的第二意见。它挑战假设、捕捉漂移，推荐最安全的下一步行动，不编辑文件。 |
| **delegate** | 轻量级通用委托代理，当你想要一个行为接近父会话的子代理时使用。 |

## 常用提示词

| 需求 | 自然语言 |
|------|---------|
| 获取第二意见 | "Ask oracle to review this plan and challenge assumptions." |
| 解决难题 | "Use oracle to investigate this bug before we edit." |
| 审查 diff | "Use reviewer to review this diff." |
| 并行审查 | "Run reviewers for correctness, tests, and cleanup." |
| 实现后审查 | "Implement this, then review it." |
| 谨慎执行计划 | "Have worker implement this approved plan, then run reviewers and apply the feedback." |
| 侦查后再规划 | "Use scout to inspect the auth flow before planning." |
| 后台运行 | "Run this in the background." |
| 浏览代理 | "Show me the available subagents." |
| 使用保存的工作流 | "Run the review chain on this branch." |
| 查看运行中的工作 | "Show active async runs." |
| 检查设置 | "Check whether subagents are configured correctly." |

## 直接命令

| 命令 | 描述 |
|------|------|
| `/run <agent> [task]` | 运行单个代理；省略任务适用于自包含的代理 |
| `/chain agent1 "task1" -> agent2 "task2"` | 按顺序运行代理 |
| `/parallel agent1 "task1" -> agent2 "task2"` | 并行运行代理 |
| `/run-chain <chainName> -- <task>` | 启动保存的 .chain.md 工作流 |
| `/subagents-doctor` | 显示只读设置诊断 |

## 快捷命令

| 提示词 | 用途 |
|--------|------|
| `/parallel-review` | 启动不同角度的新上下文审查器，然后综合需要修复的内容 |
| `/parallel-research` | 结合 researcher 和 scout 获取外部证据、本地代码上下文和实用权衡 |
| `/parallel-context-build` | 并行运行 context-builder 代理，生成规划交接上下文和 meta-prompt |
| `/parallel-handoff-plan` | 将外部研究和 context-builder 传递组合成实现交接计划和 meta-prompt |
| `/gather-context-and-clarify` | 先 scout/research，然后问用户需要澄清的问题 |
| `/parallel-cleanup` | 实现后运行仅审查的清理传递 |

## 链式调用步骤配置

使用 `->` 分隔步骤，每个步骤可以有自己的任务：

```bash
/chain scout "scan the codebase" -> planner "create an implementation plan"
/parallel scanner "find security issues" -> reviewer "check code style"
```

### 内联步骤配置

在代理名称后附加 `[key=value,...]` 来覆盖该步骤的默认值：

```bash
/chain scout[output=context.md] "scan code" -> planner[reads=context.md] "analyze auth"
```

| 参数 | 示例 | 描述 |
|------|------|------|
| output | `output=context.md` | 将结果写入文件 |
| outputMode | `outputMode=file-only` | 只返回文件引用而不是完整内容 |
| reads | `reads=a.md+b.md` | 执行前读取的文件 |
| model | `model=anthropic/claude-sonnet-4` | 覆盖该步骤的模型 |
| skills | `skills=planning+review` | 覆盖注入的技能 |
| progress | `progress` | 启用进度跟踪 |

## 后台和分叉运行

```bash
/run scout "audit the codebase" --bg
/chain scout "analyze auth" -> planner "design refactor" -> worker --bg
```

添加 `--fork` 从父会话的当前叶子创建真正的分支会话：

```bash
/run reviewer "review this diff" --fork
```

## 代理存放位置

| 范围 | 路径 |
|------|------|
| 内置 | `~/.pi/agent/extensions/subagent/agents/` |
| 用户 | `~/.pi/agent/agents/**/*.md` |
| 项目 | `.pi/agents/**/*.md` |

## 代理 frontmatter 字段

```yaml
---
name: scout
package: code-analysis  # 可选包标识符
description: Fast codebase recon
tools: read, grep, find, ls, bash, mcp:chrome-devtools
model: claude-haiku-4-5
fallbackModels: openai/gpt-5-mini, anthropic/claude-sonnet-4
thinking: high
systemPromptMode: replace  # replace 或 append
inheritProjectContext: false
inheritSkills: false
skills: safe-bash, chrome-devtools
output: context.md
defaultReads: context.md
defaultProgress: true
maxSubagentDepth: 1
---
```

## 链式文件 (.chain.md)

链是可重用的 `.chain.md` 工作流，存储在：

| 范围 | 路径 |
|------|------|
| 用户 | `~/.pi/agent/chains/**/*.chain.md` |
| 项目 | `.pi/chains/**/*.chain.md` |

示例：

```markdown
---
name: scout-planner
description: 收集上下文然后规划实现
---

## scout
output: context.md

分析代码库 {task}

## planner
reads: context.md
model: anthropic/claude-sonnet-4-5:high
progress: true

基于 {previous} 创建实现计划
```

### 链变量

| 变量 | 描述 |
|------|------|
| `{task}` | 第一步的原始任务 |
| `{previous}` | 前一步的输出，或并行步骤的聚合输出 |
| `{chain_dir}` | 链 artifacts 目录的路径 |

## 工作树隔离

并行代理编辑同一仓库时可能互相覆盖。`worktree: true` 给每个并行子代理自己的 git worktree：

```javascript
{ tasks: [
  { agent: "worker", task: "Implement auth" },
  { agent: "worker", task: "Implement API" }
], worktree: true }
```

## 配置选项

在 `~/.pi/agent/extensions/subagent/config.json` 中配置：

```json
{
  "asyncByDefault": true,          // 默认后台执行
  "forceTopLevelAsync": true,      // 强制顶层异步
  "parallel": {
    "maxTasks": 12,
    "concurrency": 6
  },
  "defaultSessionDir": "~/.pi/agent/sessions/subagent/",
  "maxSubagentDepth": 2,
  "intercomBridge": {
    "mode": "always",
    "instructionFile": "./intercom-bridge.md"
  }
}
```

## 可选：pi-intercom 配套组件

安装 pi-intercom 可以让子代理在运行时与父 Pi 会话通信：

```bash
pi install npm:pi-intercom
```

## 运行时文件

| 文件 | 用途 |
|------|------|
| `src/extension/index.ts` | 扩展注册、工具注册、消息/渲染连接 |
| `src/agents/agents.ts` | 代理和链发现、frontmatter 解析 |
| `src/runs/foreground/subagent-executor.ts` | 主执行路由 |
| `src/runs/background/subagent-runner.ts` | 分离的异步运行器 |
| `src/runs/shared/worktree.ts` | Git worktree 隔离 |

## 进度和观察

- 前台运行显示紧凑的实时进度：当前工具、最近输出、token 计数、时长
- 按 `Ctrl+O` 展开完整流式视图
- 后台运行写入 `<tmpdir>/pi-subagents-<scope>/async-subagent-runs/<id>/`

## 递归保护

默认限制嵌套深度为 2 层：主会话 → 子代理 → 子子代理。

```bash
export PI_SUBAGENT_MAX_DEPTH=3  # 增加限制
export PI_SUBAGENT_MAX_DEPTH=0   # 禁用子代理
```

## 改变内置代理的模型

```bash
/run reviewer[model=anthropic/claude-sonnet-4:high] "Review this diff"
```

或在设置中持久化覆盖：

```json
{
  "subagents": {
    "agentOverrides": {
      "reviewer": {
        "model": "anthropic/claude-sonnet-4",
        "thinking": "high",
        "fallbackModels": ["openai/gpt-5-mini"]
      }
    }
  }
}
```

---

> 来源：[pi-subagents - pi.dev](https://pi.dev/packages/pi-subagents)