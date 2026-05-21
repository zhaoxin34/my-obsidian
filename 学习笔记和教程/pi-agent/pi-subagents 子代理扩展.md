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

## 技能（Skills）

技能是注入到代理系统提示词中的 SKILL.md 文件。

发现顺序（项目优先）：

1. `.pi/skills/{name}/SKILL.md`
2. 项目包设置中的 `package.json -> pi.skills`
3. 当前任务工作目录包的 `package.json -> pi.skills`
4. `.pi/settings.json -> skills`
5. `~/.pi/agent/skills/{name}/SKILL.md`
6. 用户包设置中的 `package.json -> pi.skills`
7. `~/.pi/agent/settings.json -> skills`

使用方法：使用代理默认值、在运行时覆盖，或禁用：

```javascript
{ agent: "scout", task: "..." }
{ agent: "scout", task: "...", skill: "tmux, safe-bash" }
{ agent: "scout", task: "...", skill: false }
```

对于链，顶层的 skill 是累加的。步骤级别的 skill 覆盖该步骤；`false` 禁用该步骤的技能。

注入的技能使用以下格式：

```xml
<skill name="safe-bash">
[技能内容，来自 SKILL.md，去除了 frontmatter]
</skill>
```

缺失的技能不会导致执行失败，结果摘要会显示警告。

### 绑定的技能

该包绑定了 pi-subagents 技能，扩展安装后自动对父代理可用。这仅适用于编排父代理：子代理永远不会收到它，其上下文被明确过滤以去除父级专用的编排指令。

绑定的技能涵盖以下内容：

- **委托模式**：何时启动哪个代理，是否使用 single、parallel、chain 或 async 模式，以及是否使用 fresh 或 forked 上下文
- **提示词工作流配方**：如何直接使用 `subagent(...)` 应用打包的技术（当用户用自然语言描述工作流而非调用斜杠命令时），包括并行审查、并行研究、并行 context-build、并行 handoff-plan、gather-context-and-clarify 和并行清理
- **角色代理提示词指导**：紧凑的契约提示词而非长脚本，角色特定 meta prompt 中应包含什么，以及研究人员的检索预算
- **安全边界**：子代理不得运行子代理，不得杜撰 intercom 目标，必须升级未批准的决策
- **Intercom 约定**：何时问 vs 发送，以及 pi-intercom 如何在父端进行结果传递
- **控制和诊断**：注意信号、软中断、状态和 doctor 操作

## 程序化工具调用

以下是 LLM 调用 subagent 工具时传递的参数。大多数用户用自然语言询问或使用斜杠命令。

### 执行示例

```javascript
// 单个代理
{ agent: "worker", task: "refactor auth" }
{ agent: "scout", task: "find todos", maxOutput: { lines: 1000 } }
{ agent: "scout", task: "investigate", output: false }
{ agent: "scout", task: "write a large report", output: "reports/scout.md", outputMode: "file-only" }

// 分叉上下文
{ agent: "worker", task: "continue this thread", context: "fork" }

// 并行
{ tasks: [{ agent: "scout", task: "a" }, { agent: "reviewer", task: "b" }] }
{ tasks: [{ agent: "scout", task: "audit auth", count: 3 }] }
{ tasks: [{ agent: "scout", task: "audit frontend" }, { agent: "reviewer", task: "audit backend" }], context: "fork" }

// 链式
{ chain: [
  { agent: "scout", task: "Gather context for auth refactor" },
  { agent: "planner" },
  { agent: "worker" },
  { agent: "reviewer" }
]}

// 无 TUI 的链（适合后台执行）
{ chain: [...], clarify: false, async: true }

// 带扇出/扇入的链
{ chain: [
  { agent: "scout", task: "Gather context" },
  { parallel: [
    { agent: "worker", task: "Implement feature A from {previous}" },
    { agent: "worker", task: "Implement feature B from {previous}" }
  ], concurrency: 2, failFast: true },
  { agent: "reviewer", task: "Review all changes from {previous}" }
]}

// Worktree 隔离
{ tasks: [
  { agent: "worker", task: "Implement auth" },
  { agent: "worker", task: "Implement API" }
], worktree: true }
```

## 管理操作

代理定义默认不会加载到上下文中。管理操作让 LLM 在运行时发现、检查、创建、更新和删除代理和链。

```javascript
// 列出代理
{ action: "list" }
{ action: "list", agentScope: "project" }

// 获取代理/链详情
{ action: "get", agent: "scout" }
{ action: "get", agent: "code-analysis.scout" }
{ action: "get", chainName: "review-pipeline" }

// 创建代理
{ action: "create", config: {
  name: "Code Scout",
  package: "code-analysis",
  description: "Scans codebases for patterns and issues",
  scope: "user",
  systemPrompt: "You are a code scout...",
  systemPromptMode: "replace",
  inheritProjectContext: false,
  inheritSkills: false,
  model: "anthropic/claude-sonnet-4",
  fallbackModels: ["openai/gpt-5-mini", "anthropic/claude-haiku-4-5"],
  tools: "read, bash, mcp:github/search_repositories",
  extensions: "",
  skills: "parallel-scout",
  thinking: "high",
  output: "context.md",
  reads: "shared-context.md",
  progress: true
}}

// 创建链
{ action: "create", config: {
  name: "review-pipeline",
  description: "Scout then review",
  scope: "project",
  steps: [
    { agent: "scout", task: "Scan {task}", output: "context.md" },
    { agent: "reviewer", task: "Review {previous}", reads: ["context.md"] }
  ]
}}

// 更新
{ action: "update", agent: "code-analysis.scout", config: { model: "openai/gpt-4o" } }
{ action: "update", chainName: "review-pipeline", config: { steps: [...] } }

// 删除
{ action: "delete", agent: "scout" }
{ action: "delete", chainName: "review-pipeline" }
```

## 参数参考

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `agent` | string | - | 单模式下的代理名称，或管理操作的目标 |
| `task` | string | - | 单模式下的任务字符串 |
| `action` | string | - | `list`, `get`, `create`, `update`, `delete`, `status`, `interrupt`, `resume`, `doctor` |
| `chainName` | string | - | 管理操作的链名称 |
| `config` | object/string | - | 创建/更新的代理或链配置 |
| `output` | string \| false | 代理默认 | 覆盖单代理输出文件 |
| `outputMode` | "inline" \| "file-only" | inline | 内联返回或简洁文件引用 |
| `skill` | string \| string[] \| false | 代理默认 | 覆盖技能或禁用全部 |
| `model` | string | 代理默认 | 覆盖模型 |
| `tasks` | array | - | 顶层并行任务 |
| `concurrency` | number | config 或 4 | 顶层并行并发数 |
| `worktree` | boolean | false | 为并行任务创建隔离的 git worktree |
| `chain` | array | - | 顺序和并行链步骤 |
| `context` | fresh \| fork | 代理默认或 fresh | fork 从父叶子创建真正的分支会话 |
| `chainDir` | string | temp chain dir | 链 artifacts 的持久目录 |
| `clarify` | boolean | true for chains | 显示 TUI 预览/编辑流程 |
| `agentScope` | user \| project \| both | both | 代理发现范围 |
| `async` | boolean | false | 后台执行 |
| `cwd` | string | runtime cwd | 覆盖工作目录 |
| `maxOutput` | object | 200KB, 5000 lines | 最终输出截断限制 |
| `artifacts` | boolean | true | 写入调试 artifacts |
| `includeProgress` | boolean | false | 在结果中包含完整进度 |
| `share` | boolean | false | 上传会话导出到 GitHub Gist |
| `sessionDir` | string | derived | 覆盖会话日志目录 |

### 状态和控制操作

```javascript
subagent({ action: "status" })
subagent({ action: "status", id: "<run-id>" })
subagent({ action: "interrupt", id: "<run-id>" })
subagent({ action: "resume", id: "<run-id>", message: "follow-up question" })
subagent({ action: "resume", id: "<run-id>", index: 1, message: "follow-up for child 2" })
subagent({ action: "doctor" })
```

`resume` 在异步子代理仍可通过 intercom 联系时直接发送后续消息。完成后，通过从存储的子会话文件启动新的异步子代理来恢复子代理。多子代理异步运行和记住的前台单代理、并行或链运行可以通过传递 `index` 选择子代理来恢复。

## 工作树隔离

并行代理编辑同一仓库时可能互相覆盖。`worktree: true` 给每个并行子代理自己的 git worktree（从 HEAD 分支）：

```javascript
{ tasks: [
  { agent: "worker", task: "Implement auth", count: 2 },
  { agent: "worker", task: "Implement API" }
], worktree: true }
```

### 要求

- 在 git 仓库内运行
- 工作树必须干净（clean）
- 存在时，`node_modules/` 会被符号链接到每个 worktree
- 任务级别的 cwd 覆盖必须省略或匹配共享 cwd
- 配置的 `worktreeSetupHook` 必须在超时前返回有效 JSON

工作树并行步骤完成后，每个代理的差异统计会被追加到输出中，完整的补丁文件会被写入 artifacts。工作树和临时分支在 finally 块中清理。

### worktreeSetupHook

```json
{
  "worktreeSetupHook": "./scripts/setup-worktree.mjs",
  "worktreeSetupHookTimeoutMs": 45000
}
```

钩子每个创建的工作树运行一次。路径必须是绝对路径、`~/...` 或仓库相对路径；裸命令名被拒绝。

stdin 是一个 JSON 对象，包含 `repoRoot`, `worktreePath`, `agentCwd`, `branch`, `index`, `runId`, `baseCommit`。stdout 必须是单个 JSON 对象，例如：

```json
{ "syntheticPaths": [".venv", ".env.local"] }
```

`syntheticPaths` 必须相对于工作树根目录。它们在差异捕获前被移除，以免辅助文件污染补丁。跟踪的文件永远不会被排除；将跟踪的路径标记为 synthetic 会导致设置失败。默认超时 30000ms。

## 文件、日志和可观察性

每个链运行创建用户范围的临时目录，如：

```
<tmpdir>/pi-subagents-<scope>/chain-runs/{runId}/
```

可能包含 `context.md`、`plan.md`、`progress.md` 和 `parallel-{stepIndex}/.../output.md` 等文件。超过 24 小时的目录在扩展启动时被清理。

调试 artifacts 位于 `{sessionDir}/subagent-artifacts/` 或用户范围的临时 artifacts 目录中。每个任务可能看到：

- `{runId}_{agent}_input.md`
- `{runId}_{agent}_output.md`
- `{runId}_{agent}.jsonl`
- `{runId}_{agent}_meta.json`

元数据记录时间、使用量、退出码、最终模型、尝试的模型和回退尝试结果。

会话文件存储在每个运行的会话目录下。使用 `context: "fork"` 时，每个子代理从父级的当前叶子使用 `--session <branched-session-file>` 启动。这是一个真正的会话分叉，而不是注入的摘要。

### 异步运行输出

```
<tmpdir>/pi-subagents-<scope>/async-subagent-runs/<id>/
  status.json
  events.jsonl
  output-<n>.log
  subagent-log-<id>.md
```

`status.json` 为小组件和 `subagent({ action: "status" })` 输出提供支持。`events.jsonl` 包含包装事件加上带有运行和步骤元数据注释的子 Pi JSON 事件。`output-<n>.log` 是实时人类可读的尾部。回退信息被持久化，以便后台运行在完成后可调试。

## 实时进度

前台运行显示紧凑的实时进度：当前工具、最近输出、token 计数、时长、活动新鲜度和当前工具时长。

按 `Ctrl+O` 展开完整流式视图，包含每步的完整输出。

顺序链显示流程线，如 `done scout → running planner`。带并行步骤的链显示每步卡片。

## 会话分享

传递 `share: true` 可导出完整会话到 HTML，通过你的 gh 凭据上传到秘密 GitHub Gist，并返回 `https://shittycodingagent.ai/session/?<gistId>` URL。

```javascript
{ agent: "scout", task: "...", share: true }
```

这默认禁用。会话数据可能包含源代码、路径、环境变量、凭据或其他敏感输出。你需要安装并认证 `gh`。

## 递归保护

子代理可以调用 subagent，这可能变得昂贵且难以观察。深度守卫防止无限制嵌套。

默认限制嵌套深度为 2 层：主会话 → 子代理 → 子子代理。更深的调用会被阻止，并指导直接完成当前任务。

配置限制的方式：

- 启动 Pi 前设置 `PI_SUBAGENT_MAX_DEPTH`
- `config.maxSubagentDepth`
- 代理 frontmatter 中的 `maxSubagentDepth`（只能收紧继承的限制）

```bash
export PI_SUBAGENT_MAX_DEPTH=3  # 增加限制
export PI_SUBAGENT_MAX_DEPTH=1  # 减少限制
export PI_SUBAGENT_MAX_DEPTH=0  # 禁用子代理
```

`PI_SUBAGENT_DEPTH` 是内部变量，自动传播，不要手动设置。

## 事件

### 异步事件

- `subagent:async-started`
- `subagent:async-complete`

### Intercom 投递事件

- `subagent:control-intercom`
- `subagent:result-intercom`

结果观察器发出 `subagent:async-complete`；`src/extension/index.ts` 注册消费它的事件通知处理器。控制/注意事件作为可见的父级通知呈现，并为异步运行持久化。使用 pi-intercom 时，需要注意的通知和分组的父端子代理结果投递可以通过 intercom 到达编排器。

## 提示词模板集成

pi-subagents 可独立工作，通过自然语言、subagent 工具、斜杠命令和上面列出的打包提示词快捷方式。如果你使用 pi-prompt-template-model，你也可以将子代理委托包装在你自己的可重用提示词模板中。

示例：

```yaml
---
description: Take a screenshot
model: claude-sonnet-4-20250514
subagent: browser-screenshoter
cwd: /tmp/screenshots
---
Use url in the prompt to take screenshot: $@
```

然后 `/take-screenshot https://example.com` 切换到 Sonnet，将任务委托给 `browser-screenshoter` 子代理（以 `/tmp/screenshots` 作为 cwd），完成后恢复你的模型。运行时覆盖如 `--cwd=<path>` 和 `--subagent=<name>` 也能正常工作。

## 完整配置选项

在 `~/.pi/agent/extensions/subagent/config.json` 中配置：

### asyncByDefault

```json
{ "asyncByDefault": true }
```

当请求未明确设置 async 时，使顶层调用使用后台执行。除非 `forceTopLevelAsync` 已启用，否则调用者仍可强制前台执行 `async: false`。

### forceTopLevelAsync

```json
{ "forceTopLevelAsync": true }
```

强制深度 0 的单代理、并行和链运行进入后台模式，并通过强制 `clarify: false` 绕过澄清 UI。嵌套调用保持自己的继承设置。

### parallel

```json
{
  "parallel": {
    "maxTasks": 12,
    "concurrency": 6
  }
}
```

`maxTasks` 默认为 8；`concurrency` 默认为 4。调用级别的并发优先。

### defaultSessionDir

```json
{ "defaultSessionDir": "~/.pi/agent/sessions/subagent/" }
```

会话目录优先级：`params.sessionDir` > `config.defaultSessionDir` > 来自父会话派生的目录。会话始终启用。

### intercomBridge

```json
{
  "intercomBridge": {
    "mode": "always",
    "instructionFile": "./intercom-bridge.md"
  }
}
```

控制子代理是否接收运行时 intercom 协调指令，以及 intercom 和 `contact_supervisor` 是否在需要时自动添加到它们的工具许可列表。

字段：

- `mode`：默认 `always`；使用 `fork-only` 仅对分叉运行注入，或使用 `off` 禁用桥接
- `instructionFile`：可选的 Markdown 模板，替换默认桥接指令。`{orchestratorTarget}` 被插值。相对路径从 `~/.pi/agent/extensions/subagent/` 解析

桥接激活还需要 pi-intercom 已安装并通过 `pi install npm:pi-intercom` 或旧版本地扩展检出来启用，一个可定位的当前会话名称或备用别名，以及在任意显式代理扩展允许列表中的 pi-intercom。

---

> 来源：[pi-subagents - pi.dev](https://pi.dev/packages/pi-subagents)


---


 问题分析

 找到了根本原因！查看 session-manager.js 的 createBranchedSession 方法（第 928-934 行）：

 ```javascript
   const hasAssistant = this.fileEntries.some((e) => e.type === "message" && e.message.role === "assistant");
   if (hasAssistant) {
       this._rewriteFile();
       this.flushed = true;
   }
   else {
       this.flushed = false;  // 文件不会被写入！
   }
   return newSessionFile;     // 但仍然返回路径！
 ```

 问题所在：当你尝试 fork 时，如果当前会话还没有任何 assistant 回复，文件不会被写入磁盘，但路径仍然被返回。然后 pi-subagents
 检查文件是否存在时就会失败。

 解决方案

 根据 pi-subagents 文档的建议，有两个选项：

 ### 选项 1: 改用 context: "fresh" (推荐)

 不使用 fork 而是用 fresh context，这样不需要会话文件：

 ```typescript
   subagent({
     agent: "ui-developer",
     task: "...",
     context: "fresh"  // 改为 fresh
   })
 ```

 缺点：子代理不会继承父会话的历史记录。

 ### 选项 2: 手动触发一次 assistant 回复

 在当前的父会话中，让我先发送一条消息让模型产生回复，然后再尝试 fork。

 你想选择哪个方案？