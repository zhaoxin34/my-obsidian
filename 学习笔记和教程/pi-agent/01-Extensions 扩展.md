# Extensions 扩展

> 原文: https://pi.dev/docs/latest/extensions

Extensions 是 TypeScript 模块，用于扩展 pi 的行为。它们可以订阅生命周期事件、注册 LLM 可调用的自定义工具、添加命令等。

> **放置位置 /reload**: 将扩展放在 `~/.pi/agent/extensions/` (全局) 或 `.pi/extensions/` (项目本地) 以便自动发现。使用 `pi -e ./path.ts` 仅用于快速测试。自动发现位置的扩展可以通过 `/reload` 热重载。

## 核心能力

- **自定义工具** - 通过 `pi.registerTool()` 注册 LLM 可调用的工具
- **事件拦截** - 阻止或修改工具调用、注入上下文、自定义压缩
- **用户交互** - 通过 `ctx.ui` 提示用户 (select, confirm, input, notify)
- **自定义 UI 组件** - 通过 `ctx.ui.custom()` 使用完整 TUI 组件进行键盘输入，实现复杂交互
- **自定义命令** - 通过 `pi.registerCommand()` 注册命令如 `/mycommand`
- **会话持久化** - 通过 `pi.appendEntry()` 存储跨重启的状态
- **自定义渲染** - 控制工具调用/结果和消息在 TUI 中的显示方式

## 示例使用场景

- 权限门控 (在 `rm -rf`、`sudo` 等之前确认)
- Git 检查点 (每次对话时 stash，恢复到分支)
- 路径保护 (阻止写入 `.env`、`node_modules/`)
- 自定义压缩 (用自定义方式总结对话)
- 对话摘要 (见 `summarize.ts` 示例)
- 交互式工具 (问题、向导、自定义对话框)
- 有状态工具 (待办事项列表、连接池)
- 外部集成 (文件监视器、webhook、CI 触发器)
- 等待时玩游戏 (见 `snake.ts` 示例)

更多实现示例见 [examples/extensions/](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions)。

## 目录

- [快速开始](#快速开始)
- [扩展位置](#扩展位置)
- [可用导入](#可用导入)
- [编写扩展](#编写扩展)
  - [扩展样式](#扩展样式)
- [事件](#事件)
  - [生命周期概览](#生命周期概览)
  - [资源事件](#资源事件)
  - [会话事件](#会话事件)
  - [Agent 事件](#agent-事件)
  - [模型事件](#模型事件)
  - [工具事件](#工具事件)
- [ExtensionContext](#extensioncontext)
- [ExtensionCommandContext](#extensioncommandcontext)
- [ExtensionAPI 方法](#extensionapi-方法)
- [状态管理](#状态管理)
- [自定义工具](#自定义工具)
- [自定义 UI](#自定义-ui)
- [错误处理](#错误处理)
- [模式行为](#模式行为)
- [示例参考](#示例参考)

## 快速开始

创建 `~/.pi/agent/extensions/my-extension.ts`:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  // 响应事件
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) {
      const ok = await ctx.ui.confirm("Dangerous!", "Allow rm -rf?");
      if (!ok) return { block: true, reason: "Blocked by user" };
    }
  });

  // 注册自定义工具
  pi.registerTool({
    name: "greet",
    label: "Greet",
    description: "Greet someone by name",
    parameters: Type.Object({
      name: Type.String({ description: "Name to greet" }),
    }),
    async execute(toolCallId, params, signal, onUpdate, ctx) {
      return {
        content: [{ type: "text", text: `Hello, ${params.name}!` }],
        details: {},
      };
    },
  });

  // 注册命令
  pi.registerCommand("hello", {
    description: "Say hello",
    handler: async (args, ctx) => {
      ctx.ui.notify(`Hello ${args || "world"}!`, "info");
    },
  });
}
```

使用 `--extension` (或 `-e`) 标志测试:

```
pi -e ./my-extension.ts
```

## 扩展位置

> **安全**: 扩展以完整系统权限运行，可以执行任意代码。只安装来自可信来源的扩展。

扩展自动发现位置:

| 位置                                | 范围              |
| ----------------------------------- | ----------------- |
| `~/.pi/agent/extensions/*.ts`       | 全局 (所有项目)   |
| `~/.pi/agent/extensions/*/index.ts` | 全局 (子目录)     |
| `.pi/extensions/*.ts`               | 项目本地          |
| `.pi/extensions/*/index.ts`         | 项目本地 (子目录) |

通过 `settings.json` 添加额外路径:

```json
{
  "packages": ["npm:@foo/bar@1.0.0", "git:github.com/user/repo@v1"],
  "extensions": ["/path/to/local/extension.ts", "/path/to/local/extension/dir"]
}
```

通过 npm 或 git 共享扩展为 pi 包，见 [packages.md](/docs/latest/packages)。

## 可用导入

| 包                                | 用途                                                  |
| --------------------------------- | ----------------------------------------------------- |
| `@earendil-works/pi-coding-agent` | 扩展类型 (`ExtensionAPI`, `ExtensionContext`, events) |
| `typebox`                         | 工具参数的模式定义                                    |
| `@earendil-works/pi-ai`           | AI 工具 (`StringEnum` for Google-compatible enums)    |
| `@earendil-works/pi-tui`          | TUI 组件用于自定义渲染                                |

npm 依赖也可以使用。在扩展旁边添加 `package.json` (或在父目录)，运行 `npm install`，然后从 `node_modules/` 导入自动工作。

对于通过 `pi install` 安装的分布式 pi 包 (npm 或 git)，运行时依赖必须在 `dependencies` 中。包安装使用生产安装 (`npm install --omit=dev`)，因此 `devDependencies` 在运行时不可用；当配置了 `npmCommand` 时，git 包使用普通 `install` 以兼容包装器。

Node.js 内置模块 (`node:fs`, `node:path` 等) 也可用。

## 编写扩展

扩展导出接收 `ExtensionAPI` 的默认工厂函数。工厂可以是同步或异步的:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // 订阅事件
  pi.on("event_name", async (event, ctx) => {
    // ctx.ui 用于用户交互
    const ok = await ctx.ui.confirm("Title", "Are you sure?");
    ctx.ui.notify("Done!", "info");
    ctx.ui.setStatus("my-ext", "Processing...");  // Footer 状态
    ctx.ui.setWidget("my-ext", ["Line 1", "Line 2"]);  // 编辑器上方的小部件 (默认)
  });

  // 注册工具、命令、快捷键、标志
  pi.registerTool({ ... });
  pi.registerCommand("name", { ... });
  pi.registerShortcut("ctrl+x", { ... });
  pi.registerFlag("my-flag", { ... });
}
```

扩展通过 [jiti](https://github.com/unjs/jiti) 加载，因此 TypeScript 无需编译即可工作。

如果工厂返回 `Promise`，pi 会等待它完成后再继续启动。这意味着异步初始化在 `session_start`、`resources_discover` 之前完成，并通过 `pi.registerProvider()` 排队的提供者注册被刷新。

### 异步工厂函数

使用异步工厂进行一次性启动工作，例如获取远程配置或动态发现可用模型:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default async function (pi: ExtensionAPI) {
  const response = await fetch("http://localhost:1234/v1/models");
  const payload = (await response.json()) as {
    data: Array<{
      id: string;
      name?: string;
      context_window?: number;
      max_tokens?: number;
    }>;
  };

  pi.registerProvider("local-openai", {
    baseUrl: "http://localhost:1234/v1",
    apiKey: "LOCAL_OPENAI_API_KEY",
    api: "openai-completions",
    models: payload.data.map((model) => ({
      id: model.id,
      name: model.name ?? model.id,
      reasoning: false,
      input: ["text"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: model.context_window ?? 128000,
      maxTokens: model.max_tokens ?? 4096,
    })),
  });
}
```

此模式使获取的模型在正常启动期间和 `pi --list-models` 时都可用。

### 扩展样式

**单文件** - 最简单，适用于小型扩展:

```
~/.pi/agent/extensions/
└── my-extension.ts
```

**带 index.ts 的目录** - 适用于多文件扩展:

```
~/.pi/agent/extensions/
└── my-extension/
    ├── index.ts        # 入口点 (导出默认函数)
    ├── tools.ts        # 辅助模块
    └── utils.ts        # 辅助模块
```

**带依赖的包** - 适用于需要 npm 包的扩展:

```
~/.pi/agent/extensions/
└── my-extension/
    ├── package.json    # 声明依赖和入口点
    ├── package-lock.json
    ├── node_modules/   # npm install 后
    └── src/
        └── index.ts
```

```json
// package.json
{
  "name": "my-extension",
  "dependencies": {
    "zod": "^3.0.0",
    "chalk": "^5.0.0"
  },
  "pi": {
    "extensions": ["./src/index.ts"]
  }
}
```

在扩展目录运行 `npm install`，然后从 `node_modules/` 导入自动工作。

## 事件

### 生命周期概览

```
pi 启动
  │
  ├─► session_start { reason: "startup" }
  └─► resources_discover { reason: "startup" }
      │
      ▼
用户发送提示 ─────────────────────────────────────────┐
  │                                                   │
  ├─► (扩展命令优先检查，找到则绕过)                    │
  ├─► input (可拦截、转换或处理)                       │
  ├─► (如果不处理则进行技能/模板扩展)                  │
  ├─► before_agent_start (可注入消息、修改系统提示)   │
  ├─► agent_start                                    │
  ├─► message_start / message_update / message_end   │
  │                                                  │
  │   ┌─── turn (LLM 调用工具时重复) ───┐            │
  │   │                                  │            │
  │   ├─► turn_start                     │            │
  │   ├─► context (可修改消息)           │            │
  │   ├─► before_provider_request       │            │
  │   ├─► after_provider_response        │            │
  │   │                                  │            │
  │   │   LLM 响应，可能调用工具:        │            │
  │   │     ├─► tool_execution_start     │            │
  │   │     ├─► tool_call (可阻止)       │            │
  │   │     ├─► tool_execution_update    │            │
  │   │     ├─► tool_result (可修改)     │            │
  │   │     └─► tool_execution_end       │            │
  │   │                                  │            │
  │   └─► turn_end                        │            │
  │                                                  │
  └─► agent_end                                      │
                                                    │
用户发送另一个提示 ◄────────────────────────────────┘

/new (新会话) 或 /resume (切换会话)
  ├─► session_before_switch (可取消)
  ├─► session_shutdown
  ├─► session_start { reason: "new" | "resume", previousSessionFile? }
  └─► resources_discover { reason: "startup" }

/fork 或 /clone
  ├─► session_before_fork (可取消)
  ├─► session_shutdown
  ├─► session_start { reason: "fork", previousSessionFile }
  └─► resources_discover { reason: "startup" }

/compact 或自动压缩
  ├─► session_before_compact (可取消或自定义)
  └─► session_compact

/tree 导航
  ├─► session_before_tree (可取消或自定义)
  └─► session_tree

/model 或 Ctrl+P (模型选择/循环)
  ├─► thinking_level_select
  └─► model_select

thinking level 变化
  └─► thinking_level_select

exit (Ctrl+C, Ctrl+D, SIGHUP, SIGTERM)
  └─► session_shutdown
```

### 资源事件

#### resources_discover

在 `session_start` 之后触发，以便扩展贡献额外的技能、提示和主题路径。启动路径使用 `reason: "startup"`。重载使用 `reason: "reload"`。

```typescript
pi.on("resources_discover", async (event, _ctx) => {
  // event.cwd - 当前工作目录
  // event.reason - "startup" | "reload"
  return {
    skillPaths: ["/path/to/skills"],
    promptPaths: ["/path/to/prompts"],
    themePaths: ["/path/to/themes"],
  };
});
```

### 会话事件

参见 [Session Format](/docs/latest/session-format) 了解会话存储内部结构和 SessionManager API。

#### session_start

当会话启动、加载或重新加载时触发。

```typescript
pi.on("session_start", async (event, ctx) => {
  // event.reason - "startup" | "reload" | "new" | "resume" | "fork"
  // event.previousSessionFile - 对于 "new", "resume" 和 "fork" 存在
  ctx.ui.notify(
    `Session: ${ctx.sessionManager.getSessionFile() ?? "ephemeral"}`,
    "info",
  );
});
```

#### session_before_switch

在启动新会话 (`/new`) 或切换会话 (`/resume`) 之前触发。

```typescript
pi.on("session_before_switch", async (event, ctx) => {
  // event.reason - "new" 或 "resume"
  // event.targetSessionFile - 我们要切换到的会话 (仅用于 "resume")

  if (event.reason === "new") {
    const ok = await ctx.ui.confirm("Clear?", "Delete all messages?");
    if (!ok) return { cancel: true };
  }
});
```

成功切换或新会话操作后，pi 为旧扩展实例发出 `session_shutdown`，重新加载并重新绑定新会话的扩展，然后发出带有 `reason: "new" | "resume"` 和 `previousSessionFile` 的 `session_start`。在 `session_shutdown` 中做清理工作，然后在 `session_start` 中重新建立任何内存状态。

#### session_before_fork

当通过 `/fork` 分叉或通过 `/clone` 克隆时触发。

```typescript
pi.on("session_before_fork", async (event, ctx) => {
  // event.entryId - 所选条目的 ID
  // event.position - /fork 为 "before"，/clone 为 "at"
  return { cancel: true }; // 取消分叉/克隆
});
```

成功分叉或克隆后，pi 为旧扩展实例发出 `session_shutdown`，重新加载并重新绑定新会话的扩展，然后发出带有 `reason: "fork"` 和 `previousSessionFile` 的 `session_start`。

#### session_before_compact / session_compact

在压缩时触发。详见 [compaction.md](/docs/latest/compaction)。

```typescript
pi.on("session_before_compact", async (event, ctx) => {
  const { preparation, branchEntries, customInstructions, signal } = event;

  // 取消:
  return { cancel: true };

  // 自定义摘要:
  return {
    compaction: {
      summary: "...",
      firstKeptEntryId: preparation.firstKeptEntryId,
      tokensBefore: preparation.tokensBefore,
    },
  };
});

pi.on("session_compact", async (event, ctx) => {
  // event.compactionEntry - 保存的压缩
  // event.fromExtension - 扩展是否提供了它
});
```

#### session_before_tree / session_tree

在 `/tree` 导航时触发。详见 [Sessions](/docs/latest/sessions)。

```typescript
pi.on("session_before_tree", async (event, ctx) => {
  const { preparation, signal } = event;
  return { cancel: true };
});

pi.on("session_tree", async (event, ctx) => {
  // event.newLeafId, oldLeafId, summaryEntry, fromExtension
});
```

#### session_shutdown

在扩展运行时被拆除之前触发。

```typescript
pi.on("session_shutdown", async (event, ctx) => {
  // event.reason - "quit" | "reload" | "new" | "resume" | "fork"
  // event.targetSessionFile - 会话替换流的目标会话
  // 清理、保存状态等
});
```

### Agent 事件

#### before_agent_start

在用户提交提示后、agent 循环之前触发。可以注入消息和/或修改系统提示。

```typescript
pi.on("before_agent_start", async (event, ctx) => {
  // event.prompt - 用户提示文本
  // event.images - 附加的图像 (如果有)
  // event.systemPrompt - 此处理程序当前链接的系统提示
  // event.systemPromptOptions - 用于构建系统提示的结构化选项

  return {
    // 注入持久消息 (存储在会话中，发送给 LLM)
    message: {
      customType: "my-extension",
      content: "Additional context for the LLM",
      display: true,
    },
    // 替换此轮的系统提示 (跨扩展链接)
    systemPrompt:
      event.systemPrompt + "\n\nExtra instructions for this turn...",
  };
});
```

`systemPromptOptions` 字段让扩展访问 Pi 用于构建系统提示的相同结构化数据。这让你可以检查 Pi 加载的内容——自定义提示、指南、工具片段、上下文文件、技能——而无需重新发现资源或重新解析标志。

#### agent_start / agent_end

每个用户提示触发一次。

```typescript
pi.on("agent_start", async (_event, ctx) => {});

pi.on("agent_end", async (event, ctx) => {
  // event.messages - 此提示的消息
});
```

#### turn_start / turn_end

每个 turn 触发一次 (一个 LLM 响应 + 工具调用)。

```typescript
pi.on("turn_start", async (event, ctx) => {
  // event.turnIndex, event.timestamp
});

pi.on("turn_end", async (event, ctx) => {
  // event.turnIndex, event.message, event.toolResults
});
```

#### message_start / message_update / message_end

消息生命周期更新时触发。

- `message_start` 和 `message_end` 为 user、assistant 和 toolResult 消息触发
- `message_update` 为 assistant 流式更新触发
- `message_end` 处理程序可以返回 `{ message }` 来替换最终确定的消息

```typescript
pi.on("message_start", async (event, ctx) => {
  // event.message
});

pi.on("message_update", async (event, ctx) => {
  // event.message
  // event.assistantMessageEvent (逐标记流事件)
});

pi.on("message_end", async (event, ctx) => {
  if (event.message.role !== "assistant") return;

  return {
    message: {
      ...event.message,
      usage: {
        ...event.message.usage,
        cost: {
          ...event.message.usage.cost,
          total: 0.123,
        },
      },
    },
  };
});
```

#### tool_execution_start / tool_execution_update / tool_execution_end

工具执行生命周期更新时触发。

在并行工具模式下:

- `tool_execution_start` 在预检阶段按 assistant 源顺序发出
- `tool_execution_update` 事件可能在工具之间交错
- `tool_execution_end` 在每个工具最终确定后按工具完成顺序发出
- 最终 `toolResult` 消息事件稍后在 assistant 源顺序中发出

```typescript
pi.on("tool_execution_start", async (event, ctx) => {
  // event.toolCallId, event.toolName, event.args
});

pi.on("tool_execution_update", async (event, ctx) => {
  // event.toolCallId, event.toolName, event.args, event.partialResult
});

pi.on("tool_execution_end", async (event, ctx) => {
  // event.toolCallId, event.toolName, event.result, event.isError
});
```

#### context

在每次 LLM 调用之前触发。非破坏性地修改消息。

```typescript
pi.on("context", async (event, ctx) => {
  // event.messages - 深拷贝，可以安全修改
  const filtered = event.messages.filter((m) => !shouldPrune(m));
  return { messages: filtered };
});
```

#### before_provider_request

在构建特定于提供者的 payload 后、发送请求之前触发。

```typescript
pi.on("before_provider_request", (event, ctx) => {
  console.log(JSON.stringify(event.payload, null, 2));

  // 可选: 替换 payload
  // return { ...event.payload, temperature: 0 };
});
```

#### after_provider_response

在收到 HTTP 响应且其流主体被消费之前触发。

```typescript
pi.on("after_provider_response", (event, ctx) => {
  // event.status - HTTP 状态码
  // event.headers - 规范化的响应头
  if (event.status === 429) {
    console.log("rate limited", event.headers["retry-after"]);
  }
});
```

### 模型事件

#### model_select

当模型通过 `/model` 命令、模型循环 (`Ctrl+P`) 或会话恢复更改时触发。

```typescript
pi.on("model_select", async (event, ctx) => {
  // event.model - 新选择的模型
  // event.previousModel - 上一个模型 (如果是首次选择则为 undefined)
  // event.source - "set" | "cycle" | "restore"

  const prev = event.previousModel
    ? `${event.previousModel.provider}/${event.previousModel.id}`
    : "none";
  const next = `${event.model.provider}/${event.model.id}`;

  ctx.ui.notify(`Model changed (${event.source}): ${prev} -> ${next}`, "info");
});
```

#### thinking_level_select

当 thinking level 更改时触发。这是通知性质的；处理程序返回值被忽略。

```typescript
pi.on("thinking_level_select", async (event, ctx) => {
  // event.level - 新选择的 thinking level
  // event.previousLevel - 上一个 thinking level

  ctx.ui.setStatus("thinking", `thinking: ${event.level}`);
});
```

### 工具事件

#### tool_call

在 `tool_execution_start` 之后、工具执行之前触发。**可阻止。** 使用 `isToolCallEventType` 缩小范围并获取类型化输入。

```typescript
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";

pi.on("tool_call", async (event, ctx) => {
  // event.toolName - "bash", "read", "write", "edit" 等
  // event.toolCallId
  // event.input - 工具参数 (可变)

  // 内置工具: 不需要类型参数
  if (isToolCallEventType("bash", event)) {
    // event.input 是 { command: string; timeout?: number }
    event.input.command = `source ~/.profile\n${event.input.command}`;

    if (event.input.command.includes("rm -rf")) {
      return { block: true, reason: "Dangerous command" };
    }
  }

  if (isToolCallEventType("read", event)) {
    // event.input 是 { path: string; offset?: number; limit?: number }
    console.log(`Reading: ${event.input.path}`);
  }
});
```

#### 工具结果

工具执行完成、`tool_execution_end` 和最终 tool result 消息事件发出后触发。**可修改结果。**

`tool_result` 处理程序像中间件一样链式工作:

- 处理程序按扩展加载顺序运行
- 每个处理程序看到前一个处理程序更改后的最新结果
- 处理程序可以返回部分补丁 (`content`, `details` 或 `isError`)；省略的字段保持当前值

```typescript
import { isBashToolResult } from "@earendil-works/pi-coding-agent";

pi.on("tool_result", async (event, ctx) => {
  // event.toolName, event.toolCallId, event.input
  // event.content, event.details, event.isError

  if (isBashToolResult(event)) {
    // event.details 是类型化的 BashToolDetails
  }

  // 修改结果:
  return { content: [...], details: {...}, isError: false };
});
```

### 用户 Bash 事件

#### user_bash

当用户执行 `!` 或 `!!` 命令时触发。**可拦截。**

```typescript
import { createLocalBashOperations } from "@earendil-works/pi-coding-agent";

pi.on("user_bash", (event, ctx) => {
  // event.command - bash 命令
  // event.excludeFromContext - 如果 !! 前缀则为 true
  // event.cwd - 工作目录

  // 选项 1: 提供自定义操作 (例如 SSH)
  return { operations: remoteBashOps };

  // 选项 2: 包装 pi 的内置本地 bash 后端
  const local = createLocalBashOperations();
  return {
    operations: {
      exec(command, cwd, options) {
        return local.exec(`source ~/.profile\n${command}`, cwd, options);
      },
    },
  };

  // 选项 3: 完全替换 - 直接返回结果
  return {
    result: { output: "...", exitCode: 0, cancelled: false, truncated: false },
  };
});
```

### 输入事件

#### input

当收到用户输入时触发，在扩展命令检查之后、技能和模板扩展之前。

**处理顺序:**

1. 扩展命令 (`/cmd`) 优先检查 - 如果找到，处理程序运行且跳过输入事件
2. `input` 事件触发 - 可拦截、转换或处理
3. 如果未处理: 技能命令 (`/skill:name`) 扩展为技能内容
4. 如果未处理: 提示模板 (`/template`) 扩展为模板内容
5. Agent 处理开始 (`before_agent_start` 等)

```typescript
pi.on("input", async (event, ctx) => {
  // event.text - 原始输入 (在技能/模板扩展之前)
  // event.images - 附加的图像 (如果有)
  // event.source - "interactive" (输入), "rpc" (API) 或 "extension"

  // 转换: 在扩展前重写输入
  if (event.text.startsWith("?quick "))
    return {
      action: "transform",
      text: `Respond briefly: ${event.text.slice(7)}`,
    };

  // 处理: 无需 LLM 响应 (扩展显示自己的反馈)
  if (event.text === "ping") {
    ctx.ui.notify("pong", "info");
    return { action: "handled" };
  }

  return { action: "continue" }; // 默认: 传递通过
});
```

**结果:**

- `continue` - 传递不变 (默认)
- `transform` - 修改文本/图像，然后继续扩展
- `handled` - 完全跳过 agent (返回此值的第一个处理程序获胜)

## ExtensionContext

所有处理程序接收 `ctx: ExtensionContext`。

### ctx.ui

用户交互的 UI 方法。详见 [自定义 UI](#自定义-ui)。

### ctx.hasUI

在打印模式 (`-p`) 和 JSON 模式下为 `false`。在交互和 RPC 模式下为 `true`。

### ctx.signal

用于嵌套异步工作的 AbortSignal。这允许 Esc 取消模型调用、`fetch()` 和扩展启动的其他支持中止的操作。

### ctx.sessionManager

SessionManager 实例，用于会话持久化和树操作。

### ctx.getSystemPrompt()

返回当前链接的系统提示字符串。

## ExtensionCommandContext

命令处理程序接收的上下文扩展。

### ctx.ui

用户交互的 UI 方法。

### ctx.signal

用于取消操作的 AbortSignal。

### ctx.messageId

当前输入条目的消息 ID。

### ctx.sessionManager

SessionManager 实例。

## ExtensionAPI 方法

### pi.on(event, handler)

订阅事件。返回取消函数。

```typescript
const unsubscribe = pi.on("session_start", async (event, ctx) => {
  // 处理事件
});

// 稍后取消订阅
unsubscribe();
```

### pi.registerTool(tool)

注册 LLM 可调用的工具。

### pi.registerCommand(name, options)

注册扩展命令。

### pi.registerShortcut(key, options)

注册键盘快捷键。

### pi.registerFlag(name, options)

注册命令行标志。

### pi.registerProvider(provider, config)

注册模型提供者。

### pi.appendEntry(entry)

向会话追加条目 (持久化)。

### pi.setThinkingLevel(level)

设置 thinking level。

## 状态管理

扩展可以使用内存存储和会话持久化。

**内存存储**: 在处理程序中直接使用变量。

**会话持久化**: 使用 `pi.appendEntry()` 存储跨重启的状态。

```typescript
// 内存状态
let counter = 0;

pi.on("tool_result", async (event, ctx) => {
  counter++;
});

// 会话持久化
pi.on("session_shutdown", async (event, ctx) => {
  ctx.sessionManager.appendEntry({
    type: "custom",
    data: { counter },
  });
});
```

## 自定义工具

使用 `pi.registerTool()` 注册工具:

```typescript
import { Type } from "typebox";

pi.registerTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({
    input: Type.String({ description: "Input value" }),
  }),
  execute: async (_toolCallId, params, _signal, _onUpdate, _ctx) => ({
    content: [{ type: "text", text: `Result: ${params.input}` }],
    details: {},
  }),
});
```

## 自定义 UI

使用 `ctx.ui.custom()` 显示自定义 TUI 组件:

```typescript
pi.registerCommand("pick", {
  handler: async (_args, ctx) => {
    const result = await ctx.ui.custom<string | null>(
      (tui, theme, keybindings, done) => new MyDialog({ onClose: done }),
      { overlay: true },
    );

    if (result) {
      ctx.ui.notify(`Selected: ${result}`, "info");
    }
  },
});
```

## 错误处理

扩展处理程序中的错误会发出 `extension_error` 事件:

```typescript
pi.on("extension_error", (event, ctx) => {
  console.error(`Extension error in ${event.extensionPath}: ${event.error}`);
});
```

## 模式行为

扩展在不同模式下可能有不同的行为:

- 在打印模式 (`-p`) 中，`ctx.hasUI` 为 `false`
- 在 RPC 模式下，对话方法通过扩展 UI 子协议工作

## 示例参考

- **选择 UI**: [preset.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/preset.ts) - 带 DynamicBorder 框架的 SelectList
- **异步取消**: [qna.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/qna.ts) - 用于 LLM 调用的 BorderedLoader
- **设置切换**: [tools.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/tools.ts) - 用于工具启用/禁用的 SettingsList
- **状态指示器**: [plan-mode.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/plan-mode.ts) - setStatus 和 setWidget
- **自定义编辑器**: [modal-editor.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/modal-editor.ts) - 类 vim 的模态编辑
- **贪吃蛇游戏**: [snake.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/snake.ts) - 完整游戏带键盘输入、游戏循环
