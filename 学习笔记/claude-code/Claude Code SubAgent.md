> ## 文档索引
> 在 https://code.claude.com/docs/llms.txt 获取完整的文档索引
> 使用此文件在进一步探索之前发现所有可用的页面。

# 子代理特性

* ***子代理都在自己的上下文窗口中运行**
* ***具有自定义系统提示、特定工具访问权限和独立权限**

* **保留上下文** - 通过将探索和实现保持在主对话之外
* **强制约束** - 通过限制子代理可以使用哪些工具
* **重用配置** - 通过用户级子代理在项目中重用
* **专业化行为** - 通过针对特定领域的专注系统提示
* **控制成本** - 通过将任务路由到更快、更便宜的模型，如 Haiku

	Claude Code 包括几个内置子代理，如 **Explore**、**Plan** 和 **general-purpose**。

## 内置子代理

Claude Code 包括当适当时 Claude 自动使用的内置子代理。每个子代理继承父对话的权限并具有额外的工具限制。

<Tabs>
  <Tab title="Explore">
    一个快速、只读代理，针对搜索和分析代码库进行了优化。

    * **模型**: Haiku（快速、低延迟）
    * **工具**: 只读工具（拒绝访问 Write 和 Edit 工具）
    * **目的**: 文件发现、代码搜索、代码库探索

    当 Claude 需要搜索或理解代码库而不进行更改时，它会委托给 Explore。这将探索结果保持在主对话上下文之外。

    调用 Explore 时，Claude 指定一个彻底性级别：**快速** 用于有针对性的查找，**中等** 用于平衡探索，或**非常彻底** 用于全面分析。
  </Tab>

  <Tab title="Plan">
    在 [计划模式](/en/common-workflows#use-plan-mode-for-safe-code-analysis) 中使用的研究代理，用于在呈现计划之前收集上下文。

    * **模型**: 继承自主对话
    * **工具**: 只读工具（拒绝访问 Write 和 Edit 工具）
    * **目的**: 计划用代码库研究

    当您处于计划模式且 Claude 需要理解您的代码库时，它会将研究委托给 Plan 子代理。这防止了无限嵌套（子代理不能生成其他子代理），同时仍然收集必要的上下文。
  </Tab>

  <Tab title="General-purpose">
    一个有能力的代理，用于需要探索和操作的复杂、多步骤任务。

    * **模型**: 继承自主对话
    * **工具**: 所有工具
    * **目的**: 复杂研究、多步骤操作、代码修改

    当任务需要探索和修改、解释结果的复杂推理或多个依赖步骤时，Claude 委托给通用代理。
  </Tab>

  <Tab title="Other">
    Claude Code 包括用于特定任务的其他辅助代理。这些通常自动调用，因此您不需要直接使用它们。

    | 代理             | 模型    | Claude 使用它的时间                                      |
    | :---------------- | :------- | :------------------------------------------------------- |
    | Bash              | Inherits | 在单独上下文中运行终端命令          |
    | statusline-setup  | Sonnet   | 当您运行 `/statusline` 配置状态行时 |
    | Claude Code Guide | Haiku    | 当您询问有关 Claude Code 功能的问题时 |
  </Tab>
</Tabs>

除了这些内置子代理，您还可以创建自己的自定义提示、工具限制、权限模式、钩子和技能。以下部分展示如何开始和自定义子代理。

## 快速开始：创建您的第一个子代理

子代理在带有 YAML 前言的 Markdown 文件中定义。您可以 [手动创建它们](#write-subagent-files) 或使用 `/agents` 命令。

本演练指导您使用 `/agent` 命令创建用户级子代理。子代理审查代码并为代码库建议改进。

<Steps>
  <Step title="打开子代理界面">
    在 Claude Code 中，运行：

    ```
    /agents
    ```
  </Step>

  <Step title="创建新的用户级代理">
    选择 **创建新代理**，然后选择 **用户级**。这会将子代理保存到 `~/.claude/agents/`，因此它在所有项目中都可用。
  </Step>

  <Step title="用 Claude 生成">
    选择 **用 Claude 生成**。出现提示时，描述子代理：

    ```
    一个代码改进代理，扫描文件并建议改进
    以提高可读性、性能和最佳实践。它应该解释
    每个问题，显示当前代码，并提供改进的版本。
    ```

    Claude 生成系统提示和配置。如果您想自定义它，按 `e` 在编辑器中打开它。
  </Step>

  <Step title="选择工具">
    对于只读审查器，取消选择除 **只读工具** 之外的所有内容。如果您保持所有工具选择，子代理将继承主对话可用的所有工具。
  </Step>

  <Step title="选择模型">
    选择子代理使用的模型。对于此示例代理，选择 **Sonnet**，它在分析代码模式时平衡能力和速度。
  </Step>

  <Step title="选择颜色">
    为子代理选择背景颜色。这有助于您识别 UI 中正在运行哪个子代理。
  </Step>

  <Step title="保存并试用">
    保存子代理。它立即可用（无需重启）。试用它：

    ```
    使用 code-improver 代理建议此项目中的改进
    ```

    Claude 委托给您的新子代理，它扫描代码库并返回改进建议。
  </Step>
</Steps>

现在您有了一个子代理，可以在机器上的任何项目中用于分析代码库并建议改进。

您也可以手动创建子代理作为 Markdown 文件，通过 CLI 标志定义它们，或通过插件分发它们。以下部分涵盖所有配置选项。

## 配置子代理

### 使用 /agents 命令

`/agents` 命令提供管理子代理的交互式界面。运行 `/agents` 来：

* 查看所有可用的子代理（内置、用户、项目和插件）
* 通过引导设置或 Claude 生成创建新的子代理
* 编辑现有子代理配置和工具访问
* 删除自定义子代理
* 当存在重复时查看哪些子代理处于活动状态

这是创建和管理子代理的推荐方法。对于手动创建或自动化，您也可以直接添加子代理文件。

### 选择子代理范围

子代理是带有 YAML 前言的 Markdown 文件。根据范围将它们存储在不同位置。当多个子代理共享相同名称时，较高优先级位置获胜。

| 位置                     | 范围                   | 优先级    | 如何创建                         |
| :--------------------------- | :---------------------- | :---------- | :------------------------------------ |
| `--agents` CLI 标志          | 当前会话         | 1 (最高) | 启动 Claude Code 时传递 JSON |
| `.claude/agents/`            | 当前项目         | 2           | 交互式或手动                 |
| `~/.claude/agents/`          | 所有您的项目       | 3           | 交互式或手动                 |
| 插件 `agents/` 目录 | 启用插件的位置 | 4 (最低)  | 与 [插件](/en/plugins) 一起安装 |

**项目子代理**（`.claude/agents/`）非常适合特定于代码库的子代理。将它们检入版本控制，以便您的团队可以协作使用和改进它们。

**用户子代理**（`~/.claude/agents/`）是可在所有项目中使用的个人子代理。

**CLI 定义的子代理**在启动 Claude Code 时作为 JSON 传递。它们仅存在于该会话中，不保存到磁盘，使其适用于快速测试或自动化脚本：

```bash  theme={null}
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

`--agents` 标志接受与基于文件的子代理相同的 [前言](#supported-frontmatter-fields) 字段的 JSON：`description`、`prompt`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills` 和 `memory`。使用 `prompt` 作为系统提示，等价于基于文件的子代理中的 markdown 正文。有关完整的 JSON 格式，请参阅 [CLI 参考](/en/cli-reference#agents-flag-format)。

**插件子代理**来自您安装的 [插件](/en/plugins)。它们与您的自定义子代理一起出现在 `/agents` 中。有关创建插件子代理的详细信息，请参阅 [插件组件参考](/en/plugins-reference#agents)。

### 编写子代理文件

子代理文件使用 YAML 前言进行配置，后跟 Markdown 中的系统提示：

<Note>
  子代理在会话开始时加载。如果您通过手动添加文件创建子代理，请重启会话或使用 `/agents` 立即加载它。
</Note>

```markdown  theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

前言定义子代理的元数据和配置。主体成为指导子代理行为的系统提示。子代理仅接收此系统提示（加上基本环境细节，如工作目录），而不是完整的 Claude Code 系统提示。

#### 支持的前言字段

以下字段可用于 YAML 前言。只有 `name` 和 `description` 是必需的。

| 字段             | 必需 | 描述                                                                                                                                                                                                                                                                 |
| :---------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`            | 是      | 使用小写字母和连字符的唯一标识符                                                                                                                                                                                                                       |
| `description`     | 是      | Claude 何时应该委托给此子代理                                                                                                                                                                                                                                |
| `tools`           | 否       | 子代理可以使用的 [工具](#available-tools)。如果省略，继承所有工具                                                                                                                                                                                               |
| `disallowedTools` | 否       | 要拒绝的工具，从继承或指定列表中移除                                                                                                                                                                                                                     |
| `model`           | 否       | 要使用的 [模型](#choose-a-model)：`sonnet`、`opus`、`haiku` 或 `inherit`。默认为 `inherit`                                                                                                                                                                             |
| `permissionMode`  | 否       | [权限模式](#permission-modes)：`default`、`acceptEdits`、`delegate`、`dontAsk`、`bypassPermissions` 或 `plan`                                                                                                                                                       |
| `maxTurns`        | 否       | 子代理停止前的最大代理轮数                                                                                                                                                                                                                   |
| `skills`          | 否       | 在启动时加载到子代理上下文中的 [技能](/en/skills)。注入完整的技能内容，而不仅仅是使其可供调用。子代理不继承父对话中的技能                                                                |
| `mcpServers`      | 否       | 此子代理可用的 [MCP 服务器](/en/mcp)。每个条目要么是引用已配置服务器的服务器名称（例如 `"slack"`），要么是内联定义，以服务器名称为键，以完整的 [MCP 服务器配置](/en/mcp#configure-mcp-servers) 作为值 |
| `hooks`           | 否       | 作用域到此子代理的 [生命周期钩子](#define-hooks-for-subagents)                                                                                                                                                                                                      |
| `memory`          | 否       | [持久内存范围](#enable-persistent-memory)：`user`、`project` 或 `local`。启用跨会话学习                                                                                                                                                         |

### 选择模型

`model` 字段控制子代理使用的 [AI 模型](/en/model-config)：

* **模型别名**：使用可用的别名之一：`sonnet`、`opus` 或 `haiku`
* **inherit**：使用与主对话相同的模型
* **省略**：如果未指定，默认为 `inherit`（使用与主对话相同的模型）

### 控制子代理能力

您可以通过工具访问、权限模式和条件规则来控制子代理可以做什么。

#### 可用工具

子代理可以使用 Claude Code 的任何 [内部工具](/en/settings#tools-available-to-claude)。默认情况下，子代理从主对话继承所有工具，包括 MCP 工具。

要限制工具，使用 `tools` 字段（允许列表）或 `disallowedTools` 字段（拒绝列表）：

```yaml  theme={null}
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
---
```

#### 限制可以生成哪些子代理

当代理作为主线程运行并带有 `claude --agent` 时，它可以使用 Task 工具生成子代理。要限制它可以生成哪些子代理类型，在 `tools` 字段中使用 `Task(agent_type)` 语法：

```yaml  theme={null}
---
name: coordinator
description: Coordinates work across specialized agents
tools: Task(worker, researcher), Read, Bash
---
```

这是一个允许列表：只能生成 `worker` 和 `researcher` 子代理。如果代理尝试生成任何其他类型，请求失败，代理在其提示中只能看到允许的类型。要在允许所有其他类型的同时阻止特定代理，改用 [`permissions.deny`](#disable-specific-subagents)。

要允许不受限制地生成任何子代理，使用不带括号的 `Task`：

```yaml  theme={null}
tools: Task, Read, Bash
```

如果 `Task` 完全从 `tools` 列表中省略，代理无法生成任何子代理。此限制仅适用于作为主线程运行并带有 `claude --agent` 的代理。子代理不能生成其他子代理，因此 `Task(agent_type)` 在子代理定义中没有效果。

#### 权限模式

`permissionMode` 字段控制子代理如何处理权限提示。子代理从主对话继承权限上下文，但可以覆盖模式。

| 模式                | 行为                                                                                                             |
| :------------------ | :------------------------------------------------------------------------------------------------------------------- |
| `default`           | 标准权限检查和提示                                                                            |
| `acceptEdits`       | 自动接受文件编辑                                                                                               |
| `dontAsk`           | 自动拒绝权限提示（明确允许的工具仍然工作）                                                   |
| `delegate`          | [代理团队](/en/agent-teams#use-delegate-mode) 领导的仅协调模式。限制为团队管理工具 |
| `bypassPermissions` | 跳过所有权限检查                                                                                           |
| `plan`              | 计划模式（只读探索）                                                                                    |

<Warning>
  谨慎使用 `bypassPermissions`。它跳过所有权限检查，允许子代理执行任何操作而无需批准。
</Warning>

如果父级使用 `bypassPermissions`，这优先于子级且无法覆盖。

#### 预加载技能到子代理

使用 `skills` 字段在启动时将技能内容注入子代理的上下文。这为子代理提供了领域知识，而不需要它在执行期间发现和加载技能。

```yaml  theme={null}
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

每个技能的完整内容被注入到子代理的上下文中，而不仅仅是使其可供调用。子代理不从父对话继承技能；您必须显式列出它们。

<Note>
  这与 [在子代理中运行技能](/en/skills#run-skills-in-a-subagent) 相反。使用子代理中的 `skills`，子代理控制系统提示并加载技能内容。在技能中使用 `context: fork`，技能内容被注入到您指定的代理中。两者使用相同的底层系统。
</Note>

#### 启用持久内存

`memory` 字段为子代理提供一个跨对话生存的持久目录。子代理使用此目录随着时间的推移建立知识，如代码库模式、调试洞察和架构决策。

```yaml  theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

根据内存应该应用的广泛程度选择范围：

| 范围     | 位置                                      | 在何时使用                                                                                    |
| :-------- | :-------------------------------------------- | :------------------------------------------------------------------------------------------ |
| `user`    | `~/.claude/agent-memory/<name-of-agent>/`     | 子代理应该在所有项目中记住学习                                  |
| `project` | `.claude/agent-memory/<name-of-agent>/`       | 子代理的知识是特定于项目的，可通过版本控制共享              |
| `local`   | `.claude/agent-memory-local/<name-of-agent>/` | 子代理的知识是特定于项目的，但不应检入版本控制 |

当启用内存时：

* 子代理的系统提示包含读取和写入内存目录的指令。
* 子代理的系统提示还包括内存目录中 `MEMORY.md` 的前 200 行，如果超过 200 行，则包含管理 `MEMORY.md` 的指令。
* Read、Write 和 Edit 工具自动启用，以便子代理可以管理其内存文件。

##### 持久内存提示

* `user` 是推荐的默认范围。当子代理的知识仅与特定代码库相关时，使用 `project` 或 `local`。
* 在开始工作之前询问子代理咨询其内存："审查此 PR，并检查您以前见过的模式记忆。"
* 完成任务后要求子代理更新其内存："现在您已完成，将所学到的保存到您的内存中。"随着时间的推移，这会建立一个知识库，使子代理更加有效。
* 将内存指令直接包含在子代理的 markdown 文件中，以便它主动维护自己的知识库：

  ```markdown  theme={null}
  Update your agent memory as you discover codepaths, patterns, library
  locations, and key architectural decisions. This builds up institutional
  knowledge across conversations. Write concise notes about what you found
  and where.
  ```

#### 使用钩子的条件规则

为了对工具使用进行更动态的控制，使用 `PreToolUse` 钩子在操作执行前验证它们。当您需要允许工具的一些操作而阻止其他操作时，这很有用。

此示例创建一个只允许只读数据库查询的子代理。`PreToolUse` 钩子在每个 Bash 命令执行前运行 `command` 中指定的脚本：

```yaml  theme={null}
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

Claude Code [通过 stdin 将钩子输入作为 JSON](/en/hooks#pretooluse-input) 传递给钩子命令。验证脚本读取此 JSON，提取 Bash 命令，并 [以代码 2 退出](/en/hooks#exit-code-2-behavior-per-event) 来阻止写操作：

```bash  theme={null}
#!/bin/bash
# ./scripts/validate-readonly-query.sh

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# 阻止 SQL 写操作（不区分大小写）
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

有关完整的输入架构，请参阅 [钩子输入](/en/hooks#pretooluse-input)，有关退出代码如何影响行为，请参阅 [退出代码](/en/hooks#exit-code-output)。

#### 禁用特定子代理

您可以通过在 [设置](/en/settings#permission-settings) 的 `deny` 数组中添加特定子代理来阻止 Claude 使用它们。使用格式 `Task(subagent-name)`，其中 `subagent-name` 与子代理的 name 字段匹配。

```json  theme={null}
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

这适用于内置和自定义子代理。您也可以使用 `--disallowedTools` CLI 标志：

```bash  theme={null}
claude --disallowedTools "Task(Explore)"
```

有关权限规则的更多详细信息，请参阅 [权限文档](/en/permissions#tool-specific-permission-rules)。

### 为子代理定义钩子

子代理可以定义在其生命周期期间运行的 [钩子](/en/hooks)。有两种配置钩子的方法：

1. **在子代理的前言中**：定义仅在该子代理处于活动状态时运行的钩子
2. **在 `settings.json` 中**：定义在子代理开始或停止时在主会话中运行的钩子

#### 子代理前言中的钩子

直接在子代理的 markdown 文件中定义钩子。这些钩子仅在该特定子代理处于活动状态时运行，并在其完成时清理。

所有 [钩子事件](/en/hooks#hook-events) 都支持。子代理最常见的事件是：

| 事件         | 匹配器输入 | 何时触发                                                       |
| :------------ | :------------ | :------------------------------------------------------------------ |
| `PreToolUse`  | 工具名称     | 子代理使用工具之前                                      |
| `PostToolUse` | 工具名称     | 子代理使用工具之后                                       |
| `Stop`        | (无)        | 子代理完成时（在运行时转换为 `SubagentStop`） |

此示例用 `PreToolUse` 钩子验证 Bash 命令，用 `PostToolUse` 在文件编辑后运行 linter：

```yaml  theme={null}
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

前言中的 `Stop` 钩子自动转换为 `SubagentStop` 事件。

#### 子代理事件的项目级钩子

在 `settings.json` 中配置钩子，以响应主会话中的子代理生命周期事件。

| 事件           | 匹配器输入   | 何时触发                    |
| :-------------- | :-------------- | :------------------------------- |
| `SubagentStart` | 代理类型名称 | 子代理开始执行时 |
| `SubagentStop`  | 代理类型名称 | 子代理完成时 |

两个事件都支持匹配器以按名称定位特定代理类型。此示例仅在 `db-agent` 子代理开始时运行设置脚本，在任何子代理停止时运行清理脚本：

```json  theme={null}
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

有关完整的钩子配置格式，请参阅 [钩子](/en/hooks)。

## 使用子代理

### 理解自动委托

Claude 根据您请求中的任务描述、子代理配置中的 `description` 字段和当前上下文自动委托任务。为了鼓励主动委托，在子代理的描述字段中包含"主动使用"等短语。

您也可以显式请求特定的子代理：

```
使用 test-runner 子代理修复失败的测试
让 code-reviewer 子代理查看我的最近更改
```

### 在前台或后台运行子代理

子代理可以在前台（阻塞）或后台（并发）运行：

* **前台子代理** 阻塞主对话直到完成。权限提示和澄清问题（如 [`AskUserQuestion`](/en/settings#tools-available-to-claude)）传递给您。
* **后台子代理** 在您继续工作时并发运行。在启动前，Claude Code 提示子代理将需要的任何工具权限，确保它提前获得必要的批准。一旦运行，子代理继承这些权限并自动拒绝任何未预先批准的内容。如果后台子代理需要询问澄清问题，该工具调用失败但子代理继续。MCP 工具在后台子代理中不可用。

如果后台子代理由于缺少权限而失败，您可以 [在前台恢复它](#resume-subagents) 重试并带有交互式提示。

Claude 根据任务决定是否在前台或后台运行子代理。您也可以：

* 要求 Claude "在后台运行这个"
* 按 **Ctrl+B** 将正在运行的任务置于后台

要禁用所有后台任务功能，将 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 环境变量设置为 `1`。请参阅 [环境变量](/en/settings#environment-variables)。

### 常见模式

#### 隔离高容量操作

子代理最有效的用途之一是隔离产生大量输出的操作。运行测试、获取文档或处理日志文件会消耗大量上下文。通过将这些委托给子代理，冗长输出保留在子代理的上下文中，而只有相关摘要返回您的主对话。

```
使用子代理运行测试套件，仅报告失败的测试及其错误消息
```

#### 运行并行研究

对于独立调查，生成多个子代理同时工作：

```
使用单独的子代理并行研究认证、数据库和 API 模块
```

每个子代理独立探索其区域，然后 Claude 综合发现。当研究路径不相互依赖时，这最有效。

<Warning>
  当子代理完成时，它们的结果返回您的主对话。运行许多各自返回详细结果的子代理会消耗大量上下文。
</Warning>

对于需要持续并行性或超出您上下文窗口的任务，[代理团队](/en/agent-teams) 为每个工作器提供其自己的独立上下文。

#### 链式子代理

对于多步骤工作流，要求 Claude 按顺序使用子代理。每个子代理完成其任务并将结果返回给 Claude，然后 Claude 将相关上下文传递给下一个子代理。

```
使用 code-reviewer 子代理查找性能问题，然后使用 optimizer 子代理修复它们
```

### 在子代理和主对话之间选择

在以下情况下使用**主对话**：

* 任务需要频繁的往返或迭代改进
* 多个阶段共享重要上下文（计划 → 实现 → 测试）
* 您正在做快速、有针对性的更改
* 延迟很重要。子代理全新开始，可能需要时间收集上下文

在以下情况下使用**子代理**：

* 任务产生您不需要在主上下文中的冗长输出
* 您想强制执行特定的工具限制或权限
* 工作是自包含的，可以返回摘要

当您想要在主对话上下文中而不是孤立的子代理上下文中运行的可重用提示或工作流时，考虑 [技能](/en/skills)。

<Note>
  子代理不能生成其他子代理。如果您的工作流需要嵌套委托，使用 [技能](/en/skills) 或从主对话 [链式子代理](#chain-subagents)。
</Note>

### 管理子代理上下文

#### 恢复子代理

每个子代理调用创建一个具有全新上下文的新实例。要继续现有子代理的工作而不是重新开始，要求 Claude 恢复它。

恢复的子代理保留其完整对话历史，包括所有先前的工具调用、结果和推理。子代理准确地从前停止的地方继续，而不是全新开始。

当子代理完成时，Claude 接收其代理 ID。要恢复子代理，要求 Claude 继续之前的工作：

```
使用 code-reviewer 子代理审查认证模块
[代理完成]

继续该代码审查，现在分析授权逻辑
[Claude 恢复子代理并带有先前对话的完整上下文]
```

如果明确想要引用代理 ID，您也可以要求 Claude 提供，或在转录文件 `~/.claude/projects/{project}/{sessionId}/subagents/` 中查找 ID。每个转录存储为 `agent-{agentId}.jsonl`。

子代理转录独立于主对话持久：

* **主对话压缩**：当主对话压缩时，子代理转录不受影响。它们存储在单独的文件中。
* **会话持久性**：子代理转录在其会话内持久。您可以在重启 Claude Code 后 [恢复子代理](#resume-subagents)，方法是恢复同一会话。
* **自动清理**：转录基于 `cleanupPeriodDays` 设置清理（默认：30 天）。

#### 自动压缩

子代理使用与主对话相同的逻辑支持自动压缩。默认情况下，自动压缩在约 95% 容量时触发。要更早触发压缩，将 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 设置为较低的百分比（例如，`50`）。有关详细信息，请参阅 [环境变量](/en/settings#environment-variables)。

压缩事件记录在子代理转录文件中：

```json  theme={null}
{
  "type": "system",
  "subtype": "compact_boundary",
  "compactMetadata": {
    "trigger": "auto",
    "preTokens": 167189
  }
}
```

`preTokens` 值显示压缩发生前使用了多少令牌。

## 示例子代理

这些示例展示构建子代理的有效模式。将它们用作起点，或用 Claude 生成定制版本。

<Tip>
  **最佳实践：**

  * **设计专注的子代理：** 每个子代理应该擅长一个特定任务
  * **编写详细描述：** Claude 使用描述来决定何时委托
  * **限制工具访问：** 仅授予安全性和焦点所需的必要权限
  * **检入版本控制：** 与您的团队分享项目子代理
</Tip>

### 代码审查器

一个只读子代理，审查代码而不修改它。此示例展示如何设计具有有限工具访问（无 Edit 或 Write）和详细提示的专注子代理，明确指定要查找什么以及如何格式化输出。

```markdown  theme={null}
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### 调试器

一个可以分析和修复问题的子代理。与代码审查器不同，这个包括 Edit，因为修复错误需要修改代码。提示提供从诊断到验证的清晰工作流。

```markdown  theme={null}
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### 数据科学家

用于数据分析工作的域特定子代理。此示例展示如何为典型编码任务之外的专业化工作流创建子代理。它显式设置 `model: sonnet` 以进行更有能力的分析。

```markdown  theme={null}
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

### 数据库查询验证器

一个允许 Bash 访问但验证命令以仅允许只读 SQL 查询的子代理。此示例展示如何使用 `PreToolUse` 钩子进行条件验证，当您需要比 `tools` 字段提供的更精细的控制时。

```markdown  theme={null}
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

Claude Code [通过 stdin 将钩子输入作为 JSON](/en/hooks#pretooluse-input) 传递给钩子命令。验证脚本读取此 JSON，提取正在执行的命令，并检查其是否在 SQL 写操作列表中。如果检测到写操作，脚本 [以代码 2 退出](/en/hooks#exit-code-2-behavior-per-event) 来阻止执行并通过 stderr 将错误消息返回给 Claude。

在项目中的任何位置创建验证脚本。路径必须与钩子配置中的 `command` 字段匹配：

```bash  theme={null}
#!/bin/bash
# Blocks SQL write operations, allows SELECT queries

# Read JSON input from stdin
INPUT=$(cat)

# Extract the command field from tool_input using jq
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi

exit 0
```

使脚本可执行：

```bash  theme={null}
chmod +x ./scripts/validate-readonly-query.sh
```

钩子通过 stdin 接收 JSON，Bash 命令在 `tool_input.command` 中。退出代码 2 阻止操作并将错误消息反馈给 Claude。有关退出代码的详细信息，请参阅 [钩子](/en/hooks#exit-code-output)，有关完整的输入架构，请参阅 [钩子输入](/en/hooks#pretooluse-input)。

## 下一步

现在您了解了子代理，探索这些相关功能：

* [用插件分发子代理](/en/plugins) 以在团队或项目间共享子代理
* [以编程方式运行 Claude Code](/en/headless) 与 Agent SDK 一起用于 CI/CD 和自动化
* [使用 MCP 服务器](/en/mcp) 为子代理提供对外部工具和数据的访问