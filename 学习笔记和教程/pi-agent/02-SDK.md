# SDK

> 原文: https://pi.dev/docs/latest/sdk

SDK 提供了对 pi 的 agent 能力的编程访问。用于将 pi 嵌入其他应用程序、构建自定义界面或与自动化工作流程集成。

**示例使用场景:**

- 构建自定义 UI (web、desktop、mobile)
- 将 agent 能力集成到现有应用程序
- 创建带 agent 推理的自动化管道
- 构建生成子 agent 的自定义工具
- 以编程方式测试 agent 行为

更多示例见 [examples/sdk/](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/sdk)，从最小化到完全控制都有。

## 快速开始

```typescript
import {
  AuthStorage,
  createAgentSession,
  ModelRegistry,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

// 设置凭证存储和模型注册表
const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage,
  modelRegistry,
});

session.subscribe((event) => {
  if (
    event.type === "message_update" &&
    event.assistantMessageEvent.type === "text_delta"
  ) {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("What files are in the current directory?");
```

## 安装

```bash
npm install @earendil-works/pi-coding-agent
```

SDK 已包含在主包中。无需单独安装。

## 核心概念

### createAgentSession()

创建单个 `AgentSession` 的主工厂函数。

`createAgentSession()` 使用 `ResourceLoader` 来提供扩展、技能、提示模板、主题和上下文文件。如果不提供，则使用标准发现的 `DefaultResourceLoader`。

```typescript
import {
  createAgentSession,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

// 最小化: 使用 DefaultResourceLoader 的默认值
const { session } = await createAgentSession();

// 自定义: 覆盖特定选项
const { session } = await createAgentSession({
  model: myModel,
  tools: ["read", "bash"],
  sessionManager: SessionManager.inMemory(),
});
```

### AgentSession

会话管理 agent 生命周期、消息历史、模型状态、压缩和事件流。

```typescript
interface AgentSession {
  // 发送提示并等待完成
  prompt(text: string, options?: PromptOptions): Promise<void>;

  // 流式传输时排队消息
  steer(text: string): Promise<void>;
  followUp(text: string): Promise<void>;

  // 订阅事件 (返回取消订阅函数)
  subscribe(listener: (event: AgentSessionEvent) => void): () => void;

  // 会话信息
  sessionFile: string | undefined;
  sessionId: string;

  // 模型控制
  setModel(model: Model): Promise<void>;
  setThinkingLevel(level: ThinkingLevel): void;
  cycleModel(): Promise<ModelCycleResult | undefined>;
  cycleThinkingLevel(): ThinkingLevel | undefined;

  // 状态访问
  agent: Agent;
  model: Model | undefined;
  thinkingLevel: ThinkingLevel;
  messages: AgentMessage[];
  isStreaming: boolean;

  // 在当前会话文件内的原地树导航
  navigateTree(targetId: string, options?: {...}): Promise<{...}>;

  // 压缩
  compact(customInstructions?: string): Promise<CompactionResult>;
  abortCompaction(): void;

  // 中止当前操作
  abort(): Promise<void>;

  // 清理
  dispose(): void;
}
```

会话替换 API 如新会话、恢复、分叉和导入位于 `AgentSessionRuntime` 上，而非 `AgentSession`。

### createAgentSessionRuntime() 和 AgentSessionRuntime

当需要替换活动会话并重建 cwd 绑定运行时状态时，使用 runtime API。这与内置交互、打印和 RPC 模式使用的层相同。

```typescript
import {
  type CreateAgentSessionRuntimeFactory,
  createAgentSessionFromServices,
  createAgentSessionRuntime,
  createAgentSessionServices,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

const createRuntime: CreateAgentSessionRuntimeFactory = async ({
  cwd,
  sessionManager,
  sessionStartEvent,
}) => {
  const services = await createAgentSessionServices({ cwd });
  return {
    ...(await createAgentSessionFromServices({
      services,
      sessionManager,
      sessionStartEvent,
    })),
    services,
    diagnostics: services.diagnostics,
  };
};

const runtime = await createAgentSessionRuntime(createRuntime, {
  cwd: process.cwd(),
  agentDir: getAgentDir(),
  sessionManager: SessionManager.create(process.cwd()),
});
```

`AgentSessionRuntime` 拥有跨以下操作的活动运行时替换:

- `newSession()`
- `switchSession()`
- `fork()`
- 通过 `fork(entryId, { position: "at" })` 的克隆流
- `importFromJsonl()`

重要行为:

- 那些操作后 `runtime.session` 会改变
- 事件订阅附加到特定的 `AgentSession`，因此替换后重新订阅
- 如果使用扩展，为新会话再次调用 `runtime.session.bindExtensions(...)`
- 创建返回 `runtime.diagnostics` 上的诊断
- 如果运行时创建或替换失败，方法抛出，由调用者决定如何处理

### 提示和消息排队

`PromptOptions` 控制提示扩展、流式传输时的排队行为和提示预检通知:

```typescript
interface PromptOptions {
  expandPromptTemplates?: boolean;
  images?: ImageContent[];
  streamingBehavior?: "steer" | "followUp";
  source?: InputSource;
  preflightResult?: (success: boolean) => void;
}
```

**行为:**

- **扩展命令** (如 `/mycommand`): 立即执行，即使在流式传输期间
- **基于文件的提示模板**: 在发送或排队前扩展为其内容
- **流式传输期间无 `streamingBehavior`**: 抛出错误
- **`preflightResult(true)`**: 提示被接受、排队或立即处理

流式传输期间显式排队:

```typescript
// 排队一个转向消息，在当前 assistant turn 完成其工具调用后传递
await session.steer("New instruction");

// 等待 agent 结束 (仅在 agent 停止时传递)
await session.followUp("After you're done, also do this");
```

### Agent 和 AgentState

`Agent` 类处理核心 LLM 交互。通过 `session.agent` 访问。

```typescript
// 访问当前状态
const state = session.agent.state;

// state.messages: AgentMessage[] - 对话历史
// state.model: Model - 当前模型
// state.thinkingLevel: ThinkingLevel - 当前 thinking level
// state.systemPrompt: string - 系统提示
// state.tools: AgentTool[] - 可用工具
// state.streamingMessage?: AgentMessage - 当前部分 assistant 消息
// state.errorMessage?: string - 最新 assistant 错误

// 替换消息 (用于分支或恢复)
session.agent.state.messages = messages;

// 替换工具
session.agent.state.tools = tools;

// 等待 agent 完成处理
await session.agent.waitForIdle();
```

### 事件

订阅事件以接收流式输出和生命周期通知。

```typescript
session.subscribe((event) => {
  switch (event.type) {
    // 流式文本来自 assistant
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
      break;

    // 工具执行
    case "tool_execution_start":
      console.log(`Tool: ${event.toolName}`);
      break;
    case "tool_execution_end":
      console.log(`Result: ${event.isError ? "error" : "success"}`);
      break;

    // Agent 生命周期
    case "agent_start":
    case "agent_end":
    case "turn_start":
    case "turn_end":
      break;
  }
});
```

## 选项参考

### 目录

```typescript
const { session } = await createAgentSession({
  // 用于 DefaultResourceLoader 发现的 working directory
  cwd: process.cwd(), // 默认

  // 全局配置目录
  agentDir: "~/.pi/agent", // 默认 (展开 ~)
});
```

`cwd` 用于:

- 项目扩展 (`.pi/extensions/`)
- 项目技能、提示、上下文文件
- 会话目录命名

`agentDir` 用于:

- 全局扩展、技能、提示
- 全局上下文文件
- 设置、凭据、会话

### 模型

```typescript
import { getModel } from "@earendil-works/pi-ai";
import { AuthStorage, ModelRegistry } from "@earendil-works/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

// 查找特定内置模型 (不检查 API 密钥是否存在)
const opus = getModel("anthropic", "claude-opus-4-5");
if (!opus) throw new Error("Model not found");

// 获取有有效 API 密钥配置的模型
const available = await modelRegistry.getAvailable();

const { session } = await createAgentSession({
  model: opus,
  thinkingLevel: "medium", // off, minimal, low, medium, high, xhigh
  authStorage,
  modelRegistry,
});
```

### API 密钥和 OAuth

API 密钥解析优先级 (由 AuthStorage 处理):

1. 运行时覆盖 (通过 `setRuntimeApiKey`，不持久化)
2. `auth.json` 中存储的凭据
3. 环境变量 (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY` 等)
4. 自定义提供者密钥的回退解析器

```typescript
import { AuthStorage, ModelRegistry } from "@earendil-works/pi-coding-agent";

// 运行时 API 密钥覆盖 (不持久化到磁盘)
authStorage.setRuntimeApiKey("anthropic", "sk-my-temp-key");

// 自定义 auth 存储位置
const customAuth = AuthStorage.create("/my/app/auth.json");
const customRegistry = ModelRegistry.create(customAuth, "/my/app/models.json");
```

### 系统提示

使用 `ResourceLoader` 覆盖系统提示:

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
} from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  systemPromptOverride: () => "You are a helpful assistant.",
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

### 工具

指定启用哪些内置工具:

- 内置工具名称: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`
- 默认内置: `read`, `bash`, `edit`, `write`
- `noTools: "all"` 禁用所有工具

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

// 只读模式
const { session } = await createAgentSession({
  tools: ["read", "grep", "find", "ls"],
});

// 选择特定工具
const { session } = await createAgentSession({
  tools: ["read", "bash", "grep"],
});
```

### 自定义工具

```typescript
import { Type } from "typebox";
import {
  createAgentSession,
  defineTool,
} from "@earendil-works/pi-coding-agent";

// 内联自定义工具
const myTool = defineTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({
    input: Type.String({ description: "Input value" }),
  }),
  execute: async (_toolCallId, params) => ({
    content: [{ type: "text", text: `Result: ${params.input}` }],
    details: {},
  }),
});

// 直接传递自定义工具
const { session } = await createAgentSession({
  customTools: [myTool],
});
```

### 扩展

扩展由 `ResourceLoader` 加载。`DefaultResourceLoader` 从 `~/.pi/agent/extensions/`、`.pi/extensions/` 和 settings.json 扩展源发现。

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
} from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  additionalExtensionPaths: ["/path/to/my-extension.ts"],
  extensionFactories: [
    (pi) => {
      pi.on("agent_start", () => {
        console.log("[Inline Extension] Agent starting");
      });
    },
  ],
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

### 技能

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  type Skill,
} from "@earendil-works/pi-coding-agent";

const customSkill: Skill = {
  name: "my-skill",
  description: "Custom instructions",
  filePath: "/path/to/SKILL.md",
  baseDir: "/path/to",
  source: "custom",
};

const loader = new DefaultResourceLoader({
  skillsOverride: (current) => ({
    skills: [...current.skills, customSkill],
    diagnostics: current.diagnostics,
  }),
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

### 上下文文件

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
} from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  agentsFilesOverride: (current) => ({
    agentsFiles: [
      ...current.agentsFiles,
      { path: "/virtual/AGENTS.md", content: "# Guidelines\n\n- Be concise" },
    ],
  }),
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

### 斜杠命令

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  type PromptTemplate,
} from "@earendil-works/pi-coding-agent";

const customCommand: PromptTemplate = {
  name: "deploy",
  description: "Deploy the application",
  source: "(custom)",
  content: "# Deploy\n\n1. Build\n2. Test\n3. Deploy",
};

const loader = new DefaultResourceLoader({
  promptsOverride: (current) => ({
    prompts: [...current.prompts, customCommand],
    diagnostics: current.diagnostics,
  }),
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

### 会话管理

会话使用带有 `id`/`parentId` 链接的树结构，支持原地分支。

```typescript
import { SessionManager } from "@earendil-works/pi-coding-agent";

// 内存中 (无持久化)
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
});

// 新持久化会话
const { session: persisted } = await createAgentSession({
  sessionManager: SessionManager.create(process.cwd()),
});

// 继续最近的
const { session: continued, modelFallbackMessage } = await createAgentSession({
  sessionManager: SessionManager.continueRecent(process.cwd()),
});

// 打开特定文件
const { session: opened } = await createAgentSession({
  sessionManager: SessionManager.open("/path/to/session.jsonl"),
});

// 列出会话
const currentProjectSessions = await SessionManager.list(process.cwd());
const allSessions = await SessionManager.listAll(process.cwd());

// SessionManager 树 API
const sm = SessionManager.open("/path/to/session.jsonl");

const entries = sm.getEntries(); // 所有条目
const tree = sm.getTree(); // 完整树结构
const path = sm.getPath(); // 从根到当前叶子的路径
const leaf = sm.getLeafEntry(); // 当前叶子条目

// 分支
sm.branch(entryId); // 将叶子移动到更早的条目
sm.branchWithSummary(id, "Summary..."); // 带上下文摘要的分叉
sm.createBranchedSession(leafId); // 提取路径到新文件
```

### 设置管理

```typescript
import {
  createAgentSession,
  SettingsManager,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

// 默认: 从文件加载 (全局 + 项目合并)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create(),
});

// 带覆盖
const settingsManager = SettingsManager.create();
settingsManager.applyOverrides({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 5 },
});
const { session } = await createAgentSession({ settingsManager });

// 内存中 (无文件 I/O，用于测试)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  sessionManager: SessionManager.inMemory(),
});
```

**静态工厂:**

- `SettingsManager.create(cwd?, agentDir?)` - 从文件加载
- `SettingsManager.inMemory(settings?)` - 无文件 I/O

## ResourceLoader

使用 `DefaultResourceLoader` 发现扩展、技能、提示、主题和上下文文件。

```typescript
import {
  DefaultResourceLoader,
  getAgentDir,
} from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  cwd,
  agentDir: getAgentDir(),
});
await loader.reload();

const extensions = loader.getExtensions();
const skills = loader.getSkills();
const prompts = loader.getPrompts();
const themes = loader.getThemes();
const contextFiles = loader.getAgentsFiles().agentsFiles;
```

## 返回值

`createAgentSession()` 返回:

```typescript
interface CreateAgentSessionResult {
  // 会话
  session: AgentSession;

  // 扩展结果 (用于 runner 设置)
  extensionsResult: LoadExtensionsResult;

  // 如果会话模型无法恢复的警告
  modelFallbackMessage?: string;
}
```

## 完整示例

```typescript
import { getModel } from "@earendil-works/pi-ai";
import { Type } from "typebox";
import {
  AuthStorage,
  createAgentSession,
  DefaultResourceLoader,
  defineTool,
  ModelRegistry,
  SessionManager,
  SettingsManager,
} from "@earendil-works/pi-coding-agent";

// 设置 auth 存储 (自定义位置)
const authStorage = AuthStorage.create("/custom/agent/auth.json");

// 运行时 API 密钥覆盖 (不持久化)
if (process.env.MY_KEY) {
  authStorage.setRuntimeApiKey("anthropic", process.env.MY_KEY);
}

// 模型注册表 (无自定义 models.json)
const modelRegistry = ModelRegistry.create(authStorage);

// 内联工具
const statusTool = defineTool({
  name: "status",
  label: "Status",
  description: "Get system status",
  parameters: Type.Object({}),
  execute: async () => ({
    content: [{ type: "text", text: `Uptime: ${process.uptime()}s` }],
    details: {},
  }),
});

const model = getModel("anthropic", "claude-opus-4-5");
if (!model) throw new Error("Model not found");

// 带覆盖的内存设置
const settingsManager = SettingsManager.inMemory({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 2 },
});

const loader = new DefaultResourceLoader({
  cwd: process.cwd(),
  agentDir: "/custom/agent",
  settingsManager,
  systemPromptOverride: () => "You are a minimal assistant. Be concise.",
});
await loader.reload();

const { session } = await createAgentSession({
  cwd: process.cwd(),
  agentDir: "/custom/agent",

  model,
  thinkingLevel: "off",
  authStorage,
  modelRegistry,

  tools: ["read", "bash", "status"],
  customTools: [statusTool],
  resourceLoader: loader,

  sessionManager: SessionManager.inMemory(),
  settingsManager,
});

session.subscribe((event) => {
  if (
    event.type === "message_update" &&
    event.assistantMessageEvent.type === "text_delta"
  ) {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("Get status and list files.");
```

## 运行模式

SDK 导出运行模式工具，用于在 `createAgentSession()` 之上构建自定义界面:

### InteractiveMode

带编辑器、聊天历史和所有内置命令的完整 TUI 交互模式:

```typescript
import {
  createAgentSession,
  createAgentSessionRuntime,
  InteractiveMode,
} from "@earendil-works/pi-coding-agent";
```

### PrintMode

单次提示-响应，无会话持久化:

```typescript
import {
  createAgentSession,
  createAgentSessionRuntime,
  PrintMode,
} from "@earendil-works/pi-coding-agent";
```

### RPCMode

JSON over stdin/stdout 的 headless 操作:

```typescript
import {
  createAgentSession,
  createAgentSessionRuntime,
  RPCMode,
} from "@earendil-works/pi-coding-agent";
```

详见 [RPC 模式](/docs/latest/rpc) 了解完整的协议规格。
