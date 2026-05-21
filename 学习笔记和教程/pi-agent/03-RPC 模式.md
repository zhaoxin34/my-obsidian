# RPC Mode

> 原文: https://pi.dev/docs/latest/rpc

RPC 模式通过 stdin/stdout 上的 JSON 协议实现 coding agent 的 headless 操作。这用于将 agent 嵌入其他应用程序、IDE 或自定义 UI。

**注意**: 如果你正在构建 Node.js 应用程序，考虑直接使用 `@earendil-works/pi-coding-agent` 中的 `AgentSession`，而不是生成子进程。

## 启动 RPC 模式

```
pi --mode rpc [options]
```

常用选项:
- `--provider <name>`: 设置 LLM 提供者 (anthropic, openai, google 等)
- `--model <pattern>`: 模型模式或 ID (支持 `provider/id` 和可选的 `:<thinking>`)
- `--no-session`: 禁用会话持久化
- `--session-dir <path>`: 自定义会话存储目录

## 协议概览

- **命令**: JSON 对象发送到 stdin，每行一个
- **响应**: JSON 对象带 `type: "response"` 表示命令成功/失败
- **事件**: Agent 事件作为 JSON 行流式传输到 stdout

所有命令支持可选的 `id` 字段用于请求/响应关联。如果提供，相应响应将包含相同的 `id`。

### 帧

RPC 模式使用严格的 JSONL 语义，以 LF (`\n`) 作为唯一的记录分隔符。

这意味着客户端:
- 仅在 `\n` 上分割记录
- 接受可选的 `\r\n` 输入 (剥离尾随 `\r`)
- 不使用将 Unicode 分隔符视为换行的通用行读取器

特别是，Node `readline` 对 RPC 模式不符合协议，因为它也在 `U+2028` 和 `U+2029` 上分割，这在 JSON 字符串内是有效的。

## 命令

### 提示

#### prompt

向 agent 发送用户提示。命令响应在提示被接受、排队或处理后发出。事件在接受后继续异步流式传输。

```json
{"id": "req-1", "type": "prompt", "message": "Hello, world!"}
```

带图像:
```json
{"type": "prompt", "message": "What's in this image?", "images": [{"type": "image", "data": "base64-encoded-data", "mimeType": "image/png"}]}
```

**流式传输期间**: 如果 agent 已经流式传输，必须指定 `streamingBehavior` 来排队消息:

```json
{"type": "prompt", "message": "New instruction", "streamingBehavior": "steer"}
```

- `"steer"`: 在 agent 运行时排队消息。它在当前 assistant turn 完成其工具调用执行后、下一个 LLM 调用之前传递。
- `"followUp"`: 等待 agent 结束。消息仅在 agent 停止时传递。

**扩展命令**: 如果消息是扩展命令 (如 `/mycommand`)，它会立即执行，即使在流式传输期间。

响应:
```json
{"id": "req-1", "type": "response", "command": "prompt", "success": true}
```

`success: true` 表示提示被接受、排队或立即处理。`success: false` 表示提示在接受前被拒绝。接受后的失败通过正常的事件和消息流报告，而非第二次 `response`。

#### steer

在 agent 运行时排队转向消息。

```json
{"type": "steer", "message": "Stop and do this instead"}
```

#### follow_up

排队在 agent 结束后处理的跟进消息。

```json
{"type": "follow_up", "message": "After you're done, also do this"}
```

#### abort

中止当前 agent 操作。

```json
{"type": "abort"}
```

#### new_session

启动新的会话。可被 `session_before_switch` 扩展事件处理程序取消。

```json
{"type": "new_session"}
```

### 状态

#### get_state

获取当前会话状态。

```json
{"type": "get_state"}
```

响应:
```json
{
  "type": "response",
  "command": "get_state",
  "success": true,
  "data": {
    "model": {...},
    "thinkingLevel": "medium",
    "isStreaming": false,
    "isCompacting": false,
    "steeringMode": "all",
    "followUpMode": "one-at-a-time",
    "sessionFile": "/path/to/session.jsonl",
    "sessionId": "abc123",
    "sessionName": "my-feature-work",
    "autoCompactionEnabled": true,
    "messageCount": 5,
    "pendingMessageCount": 0
  }
}
```

#### get_messages

获取对话中的所有消息。

```json
{"type": "get_messages"}
```

### 模型

#### set_model

切换到特定模型。

```json
{"type": "set_model", "provider": "anthropic", "modelId": "claude-sonnet-4-20250514"}
```

#### cycle_model

循环到下一个可用模型。

```json
{"type": "cycle_model"}
```

#### get_available_models

列出所有配置的模型。

```json
{"type": "get_available_models"}
```

### Thinking

#### set_thinking_level

设置支持 thinking 的模型的推理/thinking level。

```json
{"type": "set_thinking_level", "level": "high"}
```

级别: `"off"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`

#### cycle_thinking_level

循环可用的 thinking level。

```json
{"type": "cycle_thinking_level"}
```

### 队列模式

#### set_steering_mode

控制转向消息的传递方式。

```json
{"type": "set_steering_mode", "mode": "one-at-a-time"}
```

模式:
- `"all"`: 在当前 assistant turn 完成其工具调用后传递所有转向消息
- `"one-at-a-time"`: 每个完成的 assistant turn 传递一个转向消息 (默认)

#### set_follow_up_mode

控制跟进消息的传递方式。

```json
{"type": "set_follow_up_mode", "mode": "one-at-a-time"}
```

模式:
- `"all"`: agent 结束时传递所有跟进消息
- `"one-at-a-time"`: 每个 agent 完成传递一个跟进消息 (默认)

### 压缩

#### compact

手动压缩对话上下文以减少 token 使用。

```json
{"type": "compact"}
```

带自定义指令:
```json
{"type": "compact", "customInstructions": "Focus on code changes"}
```

#### set_auto_compaction

启用或禁用接近满时上下文时的自动压缩。

```json
{"type": "set_auto_compaction", "enabled": true}
```

### 重试

#### set_auto_retry

启用或禁用瞬态错误时的自动重试 (超载、限流、5xx)。

```json
{"type": "set_auto_retry", "enabled": true}
```

#### abort_retry

中止进行中的重试。

```json
{"type": "abort_retry"}
```

### Bash

#### bash

执行 shell 命令并将输出添加到对话上下文。

```json
{"type": "bash", "command": "ls -la"}
```

**bash 结果如何到达 LLM:**

`bash` 命令立即执行并返回 `BashResult`。内部，创建一个 `BashExecutionMessage` 并存储在 agent 的消息状态中。此消息**不发出事件**。

当发送下一个 `prompt` 命令时，所有消息 (包括 `BashExecutionMessage`) 在发送给 LLM 之前被转换。`BashExecutionMessage` 被转换为格式如下的 `UserMessage`:

```
Ran `ls -la`
```
total 48
...
```
```

这意味着:
1. Bash 输出在**下一个 prompt** 时包含在 LLM 上下文中，而非立即
2. 可以在 prompt 前执行多个 bash 命令；所有输出都将被包含
3. `BashExecutionMessage` 本身不发出事件

#### abort_bash

中止正在运行的 bash 命令。

```json
{"type": "abort_bash"}
```

### 会话

#### get_session_stats

获取 token 使用、成本统计和当前上下文窗口使用情况。

```json
{"type": "get_session_stats"}
```

#### export_html

将会话导出为 HTML 文件。

```json
{"type": "export_html"}
```

#### switch_session

加载不同的会话文件。可被 `session_before_switch` 扩展事件处理程序取消。

```json
{"type": "switch_session", "sessionPath": "/path/to/session.jsonl"}
```

#### fork

从活动分支上的前一个用户消息创建新分叉。可被 `session_before_fork` 扩展事件处理程序取消。

```json
{"type": "fork", "entryId": "abc123"}
```

#### clone

在当前位置将当前活动分支复制到新会话。可被 `session_before_fork` 扩展事件处理程序取消。

```json
{"type": "clone"}
```

#### get_fork_messages

获取可用于分叉的用户消息。

```json
{"type": "get_fork_messages"}
```

#### get_last_assistant_text

获取最后一个 assistant 消息的文本内容。

```json
{"type": "get_last_assistant_text"}
```

#### set_session_name

为当前会话设置显示名称。

```json
{"type": "set_session_name", "name": "my-feature-work"}
```

### 命令

#### get_commands

获取可用命令 (扩展命令、提示模板和技能)。可以通过在 `prompt` 命令前加 `/` 来调用。

```json
{"type": "get_commands"}
```

响应:
```json
{
  "type": "response",
  "command": "get_commands",
  "success": true,
  "data": {
    "commands": [
      {"name": "session-name", "description": "Set or clear session name", "source": "extension"},
      {"name": "fix-tests", "description": "Fix failing tests", "source": "prompt", "location": "project"},
      {"name": "skill:brave-search", "description": "Web search via Brave API", "source": "skill", "location": "user"}
    ]
  }
}
```

每个命令有:
- `name`: 命令名 (用 `/name` 调用)
- `description`: 人类可读的描述
- `source`: 命令类型: `"extension"`, `"prompt"`, `"skill"`
- `location`: 加载位置: `"user"`, `"project"`, `"path"`

**注意**: 内置 TUI 命令 (`/settings`, `/hotkeys` 等) 不包含在内。它们仅在交互模式下处理。

## 事件

事件作为 JSON 行在 agent 操作期间流式传输到 stdout。事件**不包含** `id` 字段 (只有响应有)。

### 事件类型

| 事件 | 描述 |
|------|------|
| `agent_start` | Agent 开始处理 |
| `agent_end` | Agent 完成 (包含所有生成的消息) |
| `turn_start` | 新 turn 开始 |
| `turn_end` | Turn 完成 (包含 assistant 消息和工具结果) |
| `message_start` | 消息开始 |
| `message_update` | 流式更新 (text/thinking/toolcall delta) |
| `message_end` | 消息完成 |
| `tool_execution_start` | 工具开始执行 |
| `tool_execution_update` | 工具执行进度 (流式输出) |
| `tool_execution_end` | 工具完成 |
| `queue_update` | 待处理 steering/follow-up 队列更改 |
| `compaction_start` | 压缩开始 |
| `compaction_end` | 压缩完成 |
| `auto_retry_start` | 自动重试开始 (瞬态错误后) |
| `auto_retry_end` | 自动重试完成 (成功或最终失败) |
| `extension_error` | 扩展抛出错误 |

### agent_start / agent_end

```json
{"type": "agent_start"}
```

```json
{"type": "agent_end", "messages": [...]}
```

### turn_start / turn_end

一个 turn 由一个 assistant 响应加上任何产生的工具调用和结果组成。

```json
{"type": "turn_start"}
```

```json
{"type": "turn_end", "message": {...}, "toolResults": [...]}
```

### message_start / message_end / message_update

当消息开始、完成和流式更新时触发。

```json
{"type": "message_start", "message": {...}}
{"type": "message_end", "message": {...}}
```

`message_update` 包含:
```json
{
  "type": "message_update",
  "message": {...},
  "assistantMessageEvent": {
    "type": "text_delta",
    "contentIndex": 0,
    "delta": "Hello ",
    "partial": {...}
  }
}
```

`assistantMessageEvent` 字段包含一种 delta 类型:
- `start` - 消息生成开始
- `text_start` / `text_delta` / `text_end` - 文本内容块
- `thinking_start` / `thinking_delta` / `thinking_end` - Thinking 块
- `toolcall_start` / `toolcall_delta` / `toolcall_end` - 工具调用
- `done` - 消息完成
- `error` - 错误发生

### tool_execution_start / tool_execution_update / tool_execution_end

当工具开始、流式传输进度和完成执行时触发。

```json
{
  "type": "tool_execution_start",
  "toolCallId": "call_abc123",
  "toolName": "bash",
  "args": {"command": "ls -la"}
}
```

```json
{
  "type": "tool_execution_update",
  "toolCallId": "call_abc123",
  "toolName": "bash",
  "partialResult": {
    "content": [{"type": "text", "text": "partial output so far..."}]
  }
}
```

```json
{
  "type": "tool_execution_end",
  "toolCallId": "call_abc123",
  "toolName": "bash",
  "result": {
    "content": [{"type": "text", "text": "..."}],
    "details": {...}
  },
  "isError": false
}
```

### compaction_start / compaction_end

当压缩运行时触发，无论是手动还是自动。

```json
{"type": "compaction_start", "reason": "threshold"}
```

`reason` 字段是 `"manual"`, `"threshold"`, 或 `"overflow"`。

```json
{
  "type": "compaction_end",
  "reason": "threshold",
  "result": {
    "summary": "Summary of conversation...",
    "firstKeptEntryId": "abc123",
    "tokensBefore": 150000,
    "details": {}
  },
  "aborted": false,
  "willRetry": false
}
```

### auto_retry_start / auto_retry_end

当瞬态错误 (超载、限流、5xx) 后自动重试被触发时发出。

```json
{
  "type": "auto_retry_start",
  "attempt": 1,
  "maxAttempts": 3,
  "delayMs": 2000,
  "errorMessage": "529 {\"type\":\"error\",\"error\":{\"type\":\"overloaded_error\"}}"
}
```

```json
{
  "type": "auto_retry_end",
  "success": true,
  "attempt": 2
}
```

### extension_error

当扩展抛出错误时发出。

```json
{
  "type": "extension_error",
  "extensionPath": "/path/to/extension.ts",
  "event": "tool_call",
  "error": "Error message..."
}
```

## 扩展 UI 协议

扩展可以通过 `ctx.ui.select()`、`ctx.ui.confirm()` 等请求用户交互。在 RPC 模式下，这些通过基于基本命令/事件流的请求/响应子协议转换。

有两类扩展 UI 方法:

- **对话框方法** (`select`, `confirm`, `input`, `editor`): 在 stdout 上发出 `extension_ui_request` 并阻塞直到客户端在 stdin 上发送带匹配 `id` 的 `extension_ui_response`。
- **即发即忘方法** (`notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`): 在 stdout 上发出 `extension_ui_request` 但不期望响应。客户端可以显示信息或忽略它。

### 扩展 UI 请求 (stdout)

所有请求有 `type: "extension_ui_request"`、唯一 `id` 和 `method` 字段。

#### select

提示用户从列表中选择。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-1",
  "method": "select",
  "title": "Allow dangerous command?",
  "options": ["Allow", "Block"],
  "timeout": 10000
}
```

#### confirm

提示用户是/否确认。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-2",
  "method": "confirm",
  "title": "Clear session?",
  "message": "All messages will be lost.",
  "timeout": 5000
}
```

#### input

提示用户输入自由形式文本。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-3",
  "method": "input",
  "title": "Enter a value",
  "placeholder": "type something..."
}
```

#### editor

打开带可选预填充内容的多行文本编辑器。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-4",
  "method": "editor",
  "title": "Edit some text",
  "prefill": "Line 1\nLine 2\nLine 3"
}
```

#### notify

显示通知。即发即忘，不期望响应。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-5",
  "method": "notify",
  "message": "Command blocked by user",
  "notifyType": "warning"
}
```

`notifyType` 字段是 `"info"`, `"warning"`, 或 `"error"`。

#### setStatus

在 footer/状态栏设置或清除状态条目。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-6",
  "method": "setStatus",
  "statusKey": "my-ext",
  "statusText": "Turn 3 running..."
}
```

#### setWidget

设置或清除显示在编辑器上方或下方的 widget (文本行块)。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-7",
  "method": "setWidget",
  "widgetKey": "my-ext",
  "widgetLines": ["--- My Widget ---", "Line 1", "Line 2"],
  "widgetPlacement": "aboveEditor"
}
```

#### setTitle

设置终端窗口/标签标题。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-8",
  "method": "setTitle",
  "title": "pi - my project"
}
```

#### set_editor_text

设置输入编辑器中的文本。

```json
{
  "type": "extension_ui_request",
  "id": "uuid-9",
  "method": "set_editor_text",
  "text": "prefilled text for the user"
}
```

### 扩展 UI 响应 (stdin)

响应仅用于对话框方法。`id` 必须匹配请求。

#### 值响应 (select, input, editor)

```json
{"type": "extension_ui_response", "id": "uuid-1", "value": "Allow"}
```

#### 确认响应 (confirm)

```json
{"type": "extension_ui_response", "id": "uuid-2", "confirmed": true}
```

#### 取消响应 (任何对话框)

```json
{"type": "extension_ui_response", "id": "uuid-3", "cancelled": true}
```

## 错误处理

失败的命令返回带 `success: false` 的响应:

```json
{
  "type": "response",
  "command": "set_model",
  "success": false,
  "error": "Model not found: invalid/model"
}
```

解析错误:

```json
{
  "type": "response",
  "command": "parse",
  "success": false,
  "error": "Failed to parse command: Unexpected token..."
}
```

## 类型

源码文件:
- [`packages/coding-agent/src/core/agent-session.ts`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/agent-session.ts) - AgentSession API
- [`packages/coding-agent/src/modes/rpc/rpc-client.ts`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/modes/rpc/rpc-client.ts) - TypeScript RPC 客户端实现
- [`packages/coding-agent/src/modes/rpc/types.ts`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/modes/rpc/types.ts) - RPC 类型定义