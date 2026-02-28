---
title: 从 nanobot 和 pi-mono 解剖 LLM Agent 核心
tags:
  - AI
  - Agent
  - LLM
  - nanobot
  - pi-mono
  - 技术架构
date: 2026-02-27
author: 沈一鸣
source: 知乎专栏
url: https://zhuanlan.zhihu.com/p/2007047649933693864
---

> **摘要**：本文通过对比两个开源 Agent 项目——**nanobot**（Python）和 **pi-mono**（TypeScript）——的核心实现，带你理解 Agent 循环、消息模型和 LLM 边界这三个关键设计决策。适合刚入门 Agent 开发的读者。

---

## 目录

1. [最简单的 Agent：一个 while 循环](#一最简单的-agent一个-while-循环)
2. [当用户坐在屏幕前：新的需求](#二当用户坐在屏幕前新的需求)
3. [双层循环：区分"打断"和"追加"](#三双层循环区分打断和追加)
4. [双层消息：LLM 的世界 vs 应用的世界](#四双层消息llm-的世界-vs-应用的世界)
5. [架构的灵活性：SDK 不等于绑定 UI](#五架构的灵活性sdk-不等于绑定-ui)
6. [设计决策总结：没有最好，只有最匹配](#六设计决策总结没有最好只有最匹配)
7. [给新手的建议](#七给新手的建议)

---

## 一、最简单的 Agent：一个 while 循环

> [!note]
> 抛开所有框架术语，一个 LLM Agent 的核心就是一个循环。所有更复杂的设计都是在这个基础上叠加的。

### 核心流程

```
用户说话 → 调用 LLM → LLM 要用工具？
  是 → 执行工具 → 把结果告诉 LLM → 再次调用 LLM → ...
  否 → 返回最终回复
```

这就是学术界说的 **ReAct（Reasoning + Acting）** 模式。nanobot 的实现非常忠实于这个模式：

```python
# nanobot/agent/loop.py（简化）
async def _run_agent_loop(self, messages):
    for i in range(self.max_iterations):       # 最多 20 次
        response = await self.provider.chat(
            messages=messages,
            tools=self.tools.to_schema(),
            model=self.model,
        )

        if not response.tool_calls:
            return response.content            # 没有工具调用，结束

        # 执行工具
        for tool_call in response.tool_calls:
            result = await self.tools.execute(tool_call.name, tool_call.arguments)
            messages.add_tool_result(tool_call.id, tool_call.name, result)

        # 注入反思提示，引导 LLM 思考下一步
        messages "user", ".append({"role":content": "Reflect on the results and decide next steps."})
```

**20 行代码，就是一个完整的 Agent 核心。**

### 几个值得注意的设计选择

| 设计选择 | 说明 |
|---------|------|
| `max_iterations = 20` | 防止 Agent 无限循环。这是"无人值守"场景下的安全网——如果 LLM 一直觉得需要用工具，总得有个刹车 |
| **反思提示（Reflect prompt）** | 每次工具调用后注入一句 "Reflect on the results and decide next steps"。为什么？因为 LLM 有时候会机械地连续调工具而不思考。这句提示迫使它停下来评估当前状态 |
| **非流式调用** | `provider.chat()` 等待完整响应返回。用户发完消息就等结果，不需要看到 LLM "正在打字…" |

> [!tip]
> 这个设计完全够用吗？如果你的 Agent 是一个 Telegram 机器人——用户发条消息，等着回复——**完全够用**。简洁、可靠、容易调试。

---

## 二、当用户坐在屏幕前：新的需求

想象你在用一个类似 Claude / ChatGPT 的对话界面，Agent 正在帮你写代码。LLM 决定连续调用 5 个工具（读文件、搜索、读文件、写文件、运行测试）。

### 场景 A：你发现方向错了

Agent 读完第 2 个文件后，你已经看出来它理解错了需求。你想说"停，别继续了，我要的不是这个"。

在 nanobot 的简单循环里，你只能等 5 个工具全部执行完。因为循环在 `for tool_call in response.tool_calls` 里跑，没有任何检查用户输入的窗口。

### 场景 B：你想追加一句话

Agent 回复完了，正要停下来。你突然想到"对了，还有一个要求…"，在它结束前的一瞬间发出消息。

在简单循环里，这条消息无处可去。循环已经退出了，消息只能等下一次 `prompt()` 调用。

> [!info]
> 这两个场景催生了 pi-mono 的核心设计：**双层循环**。

---

## 三、双层循环：区分"打断"和"追加"

pi-mono 的 Agent 循环长这样：

```typescript
// pi-mono/packages/agent/src/agent-loop.ts（简化）
async function runLoop(context, config, signal, stream) {
    let pendingMessages = await config.getSteeringMessages?.() || [];

    // ===== 外层循环：处理 follow-up（追加消息）=====
    while (true) {
        let hasMoreToolCalls = true;

        // ===== 内层循环：处理 tool calls + steering（打断消息）=====
        while (hasMoreToolCalls || pendingMessages.length > 0) {
            // 注入等待中的消息
            if (pendingMessages.length > 0) {
                for (const msg of pendingMessages) {
                    context.messages.push(msg);
                }
                pendingMessages = [];
            }

            // 调用 LLM，获取响应
            const message = await streamAssistantResponse(context, config, signal, stream);

            // 检查是否有工具调用
            const toolCalls = message.content.filter(c => c.type === "toolCall");
            hasMoreToolCalls = toolCalls.length > 0;

            if (hasMoreToolCalls) {
                // 执行工具（每个工具执行后检查 steering）
                const result = await executeToolCalls(tools, message, signal, stream,
                    config.getSteeringMessages);  // ← 关键：传入 steering 检查函数
            }

            // 获取新的 steering 消息
            pendingMessages = await config.getSteeringMessages?.() || [];
        }

        // ===== 内层循环结束，Agent 准备停下来 =====
        // 检查有没有 follow-up 消息
        const followUp = await config.getFollowUpMessages?.() || [];
        if (followUp.length > 0) {
            pendingMessages = followUp;
            continue;  // ← 回到外层循环，开始新一轮
        }

        break;  // 真正结束
    }
}
```

### 打断检查的实现

在工具执行中，每个工具执行完毕后都会检查用户是否发来了打断消息：

```typescript
// pi-mono/packages/agent/src/agent-loop.ts（简化）
async function executeToolCalls(tools, assistantMessage, signal, stream, getSteeringMessages) {
    const toolCalls = assistantMessage.content.filter(c => c.type === "toolCall");

    for (let i = 0; i < toolCalls.length; i++) {
        const tool = tools.find(t => t.name === toolCalls[i].name);
        const result = await tool.execute(toolCalls[i].id, toolCalls[i].arguments, signal);

        // ===== 关键：每执行完一个工具，检查用户有没有打断 =====
        if (getSteeringMessages) {
            const steering = await getSteeringMessages();
            if (steering.length > 0) {
                // 跳过剩余工具，返回打断消息
                const remaining = toolCalls.slice(i + 1);
                for (const skipped of remaining) {
                    results.push(skipToolCall(skipped));  // 标记为 "Skipped due to queued user message"
                }
                return { toolResults: results, steeringMessages: steering };
            }
        }
    }
    return { toolResults: results };
}
```

### 为什么必须是两层，不能合成一层？

> [!important]
> 因为两种消息的**语义完全不同**：

| | Steering（打断）| Follow-up（追加）|
|---|---|---|
| 时机 | Agent 正在执行工具时到达 | Agent 即将停止时到达 |
| 行为 | 跳过剩余工具，LLM 立即转向 | 等当前轮次完成，开始新一轮 |
| 类比 | 你正在写代码，同事拍肩膀说"需求变了" | 你刚提交代码，同事说"还有个小功能" |

一层循环无法表达"我要不要丢掉剩余工具调用"这个决策点。双层循环通过物理隔离，让控制流非常清晰。

### 新手常见误区

> [!warning]
> "我加个 flag 不就行了？`if (userInterrupted) break;`"
>
> 这样做在简单场景下确实可行。但当你需要处理以下情况时，flag 方案会迅速变成意大利面条：
>
> - 打断消息到了，但还需要等当前工具执行完（不能中途终止正在写文件的操作）
> - 打断消息到了，剩余工具需要返回 "Skipped" 结果给 LLM（否则 LLM 不知道为什么 tool call 没有 result）
> - 追加消息和打断消息同时到达，谁优先？
> - 多条打断消息排队（one-at-a-time vs all-at-once）
>
> pi-mono 用两层循环 + 两个队列（steeringQueue / followUpQueue）把这些状态管理得很干净。

---

## 四、双层消息：LLM 的世界 vs 应用的世界

现在来看第二个设计差异：消息模型。

### nanobot 的做法：直接用 LLM 的消息格式

```python
# nanobot：消息就是 OpenAI 格式
messages = [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "帮我写个排序函数"},
    {"role": "assistant", "content": "好的...", "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "xxx", "content": "函数已写入 sort.py"},
]
```

简单直接，消息列表就是给 LLM 看的。

### pi-mono 的做法：引入"应用消息"层

```typescript
// pi-mono：LLM 只认三种消息
type Message = UserMessage | AssistantMessage | ToolResultMessage;

// 但应用层可以有更多消息类型
type AgentMessage = Message | CustomAgentMessages[keyof CustomAgentMessages];

// 宿主应用通过 TypeScript declaration merging 扩展
declare module "@mariozechner/pi-agent-core" {
    interface CustomAgentMessages {
        "user-with-attachments": UserMessageWithAttachments;  // 带附件的用户消息
        artifact: ArtifactMessage;                             // Artifact 操作记录
    }
}
```

### 两步转换

每次调用 LLM 前，经过两步转换：

```typescript
// 第一步：transformContext（AgentMessage[] → AgentMessage[]）
// 在应用消息层面操作：裁剪旧消息、注入外部知识
let messages = context.messages;
if (config.transformContext) {
    messages = await config.transformContext(messages, signal);
}

// 第二步：convertToLlm（AgentMessage[] → Message[]）
// 过滤自定义类型，转换为 LLM 格式
const llmMessages = await config.convertToLlm(messages);
```

### 为什么要多这一层？

用一个具体例子说明。pi-mono 的 web-ui 包实现了一个 **Artifact 系统**——LLM 可以通过工具调用创建 HTML、SVG、Markdown 等文件，实时渲染在 UI 侧面板中。

当 LLM 创建一个 Artifact 时，消息历史中实际产生了这些记录：

```
1. [assistant]   toolCall: { name: "artifacts", args: { command: "create",
                    filename: "index.html", content: "<html>..." } }
   → LLM 发出的工具调用请求

2. [toolResult]  "Created file index.html"
   → 工具执行结果

3. [artifact]    { role: "artifact", action: "create", filename: "index.html",
                   content: "<html>..." }
   → 额外的 UI 专用记录
```

LLM 只需要看第 1、2 条——它通过自己的 toolCall 和 toolResult 已经完全知道发生了什么。

第 3 条 `ArtifactMessage` 是给 **UI 做会话恢复用的**。当用户刷新页面，UI 需要从消息历史重建侧面板的 Artifact 状态。如果只有 toolCall + toolResult，就需要反查 assistant 消息的 toolCall.arguments 才能拿到文件内容——而 ArtifactMessage 把内容直接存好了，一条记录就够。

在 `convertToLlm` 中，这类 UI 专用消息被过滤掉：

```typescript
export function defaultConvertToLlm(messages: AgentMessage[]): Message[] {
    return messages
        .filter((m) => {
            // 过滤掉 artifact 消息——它们只用于会话重建
            if (isArtifactMessage(m)) return false;
            return true;
        })
        .map((m): Message | null => {
            // 把带附件的用户消息转为标准 user 消息
            if (isUserMessageWithAttachments(m)) {
                return { role: "user", content: convertAttachments(m), timestamp: m.timestamp };
            }
            // 标准 LLM 消息直接通过
            if (m.role === "user" || m.role === "assistant" || m.role === "toolResult") {
                return m;
            }
            return null;  // 过滤掉其他未知类型
        })
        .filter(Boolean);
}
```

### 这个分层的本质

> [!summary]
> **同一份消息历史，同时服务于两个消费者——UI 和 LLM——它们各取所需，互不干扰。**

```
AgentMessage[]
                   （完整的消息历史）
                    /            \
                   /              \
    transformContext()         UI 直接读取
    convertToLlm()            渲染所有消息类型
          |                   （包括 artifact、附件等）
          v
      Message[]
   （LLM 能理解的子集）
```

如果不做这个分层，你只有两个选择：

1. **只用 LLM 格式**：UI 无法存储/渲染自定义内容（比如 Artifact 状态、附件元数据）
2. **把所有信息都发给 LLM**：浪费 token，可能干扰推理，而且 LLM 会看到它不理解的 role 类型而报错

### 两步转换为什么不合成一步？

因为操作对象不同：

- `transformContext` 在 **AgentMessage 层面**工作：它可能需要根据自定义消息类型做决策，比如"保留最近 3 个 Artifact 的创建记录，把更早的裁掉"。如果已经转成 Message 了，Artifact 消息已经被过滤掉了，无从裁剪。
- `convertToLlm` 是**格式转换**：把应用层面的丰富消息映射为 LLM 能理解的三种类型。

> [!tip]
> 先裁剪（在丰富类型上操作），再转换（映射到 LLM 格式），顺序不能反。

---

## 五、架构的灵活性：SDK 不等于绑定 UI

> [!info]
> 一个常见的误解：pi-mono 有 streaming、有 steering、有 Artifact——它是不是就和 web UI 绑死了？**不是。**

看它的包结构：

```
pi-mono/packages/
  ai/              ← LLM 调用层（纯逻辑，零 UI 依赖）
  agent/           ← Agent 循环（纯逻辑，零 UI 依赖）
  web-ui/          ← Web UI 组件（可选的宿主应用）
  coding-agent/    ← Coding Agent（另一个可选的宿主应用）
```

`agent` 包不依赖 `web-ui`。Artifact、ChatPanel 这些都在 `web-ui` 里。Agent 核心就是一个循环 + 事件流 + 可扩展消息类型。

### 异步场景用法

如果你要用 pi-mono 做一个 Telegram 机器人：

```typescript
// 完全可行的异步场景用法
const agent = new Agent({ convertToLlm: defaultConvertToLlm });
agent.setModel(getModel("anthropic", "claude-sonnet-4-5-20250929"));
agent.setSystemPrompt("You are a helpful assistant.");
agent.setTools([searchTool, fileTool]);

// Telegram webhook 收到消息
app.post("/webhook", async (req, res) => {
    const userText = req.body.message.text;

    // 直接调用，等待完成
    await agent.prompt(userText);

    // 从消息历史中取最后一条 assistant 消息
    const lastMessage = agent.state.messages.findLast(m => m.role === "assistant");
    const reply = lastMessage.content.find(c => c.type === "text")?.text;

    await sendTelegramMessage(req.body.message.chat.id, reply);
});
```

> [!note]
> - streaming？没人消费事件，EventStream 队列在内存里堆着，最终被 GC。开销：几乎为零。
> - steering？`getSteeringMessages` 默认返回空数组。开销：一次函数调用。
>
> 这些机制在异步场景下**静默存在**，不碍事，不需要删除。

---

## 六、设计决策总结：没有最好，只有最匹配

回顾两个项目的核心选择：

### nanobot 的选择

| 设计决策 | 选择 | 为什么 |
|---|---|---|
| 循环模式 | 单层 ReAct + 反思提示 | 用户不在屏幕前，不需要打断能力；反思提示弥补无人纠偏的缺陷 |
| 消息模型 | 直接用 LLM 格式 | 没有复杂 UI，不需要自定义消息类型 |
| LLM 调用 | 非流式，LiteLLM 封装 | 异步消息场景不需要实时输出，LiteLLM 提供开箱即用的多 provider 支持 |
| 记忆系统 | 内置（MEMORY.md + HISTORY.md） | 作为长期助手，跨会话记忆是核心能力 |
| 安全机制 | 迭代上限 + 危险命令过滤 | 无人值守运行，必须有兜底 |

### pi-mono 的选择

| 设计决策 | 选择 | 为什么 |
|---|---|---|
| 循环模式 | 双层（steering + follow-up） | 交互式场景，用户可能随时打断或追加 |
| 消息模型 | 双层（AgentMessage → Message） | 需要在消息历史中存储 UI 专用信息（Artifact 等） |
| LLM 调用 | 流式 EventStream | 用户坐在屏幕前，实时输出是核心体验 |
| 记忆系统 | 无内置（交给宿主应用） | SDK 定位，不应替宿主决定持久化策略 |
| 安全机制 | 无内置（用户可实时纠偏） | 交互式场景下用户本身就是安全网 |

### 关键洞察

> [!important]
> 这两组选择不是"谁对谁错"，而是**同一个根本问题的不同回答**：
>
> **你的用户在不在屏幕前？**
>
> - **在**：流式输出有意义、打断能力有意义、反思提示多余（用户自己会纠偏）、迭代上限可以没有（用户自己会喊停）。
> - **不在**：流式输出是浪费、打断能力用不上、反思提示很重要（没人纠偏）、迭代上限必须有（没人喊停）。

但这不意味着两个架构互斥。pi-mono 的核心是一个不绑定任何 IO 的纯逻辑引擎，完全可以在异步场景下使用。nanobot 的功能（记忆、多通道、安全防护）也完全可以在 pi-mono 上构建——通过 `transformContext`、`convertToLlm`、事件订阅等现成的扩展点。

架构的好坏不在于它"能不能"做某件事，而在于它让**最常见的场景**变得多简单。nanobot 让"接入 Telegram 跑一个助手"非常简单；pi-mono 让"嵌入 Web UI 做交互式 Agent"非常简单。选择哪个，取决于你要做什么。

---

## 七、给新手的建议

1. **先写最简单的 Agent。** 一个 while 循环 + 工具调用，不到 50 行代码。确保你理解 ReAct 模式之后，再看更复杂的设计。

2. **设计前先问自己：用户在不在屏幕前？** 这个问题的答案会决定你的 Agent 需不需要 streaming、steering、反思提示、迭代上限。

3. **消息历史是 Agent 最重要的数据结构。** 不管用什么框架，理解"消息列表是怎么构建的、谁在消费它"是理解 Agent 核心的关键。

4. **分层不是过度设计，是边界划分。** 当你发现"这个信息 UI 需要但 LLM 不需要"时，说明你需要在 LLM 边界做一次转换。这不是一开始就需要的——等需求出现了再加。

5. **不要过早选择框架。** 先用裸 API 写一个能跑的 Agent，体会到痛点之后，再看框架是怎么解决这些痛点的。本文讨论的所有设计——双层循环、双层消息、事件流——都是从真实痛点中长出来的，不是凭空设计的。

---

## 相关资源

- [nanobot GitHub](https://github.com/HKUDS/nanobot)
- [从 pi-mono 到 OpenClaw: 源码拆解](https://www.yeyulingfeng.com/347315.html)
- [NanoBot 架构拆解](https://zhuanlan.zhihu.com/p/2009692110580900352)

---

> [!meta]
> - 作者：沈一鸣
> - 来源：知乎专栏
> - 整理：Claude Opus 4.6
