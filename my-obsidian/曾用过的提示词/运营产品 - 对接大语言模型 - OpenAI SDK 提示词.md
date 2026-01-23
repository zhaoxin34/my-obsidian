你是一名 **资深后端工程师 / LLM 系统工程师**。  
当前我已经有一个 **可运行的 Python 后端工程**，前后端已联调完成，文档可正常保存与版本管理。

现在请你 **在不破坏现有架构的前提下**，  
为该工程 **接入 OpenAI 大模型（通过官方 SDK，禁止使用 LangChain）**。

---

## 一、核心目标（必须明确）

- **真正调用 OpenAI API**
- 本阶段目标是：
    - 跑通 LLM 调用链路
    - 返回完整文本结果
        
- **不追求 Prompt 效果最优，只追求架构正确**

---

## 二、技术与架构约束（非常重要）

### 1️⃣ LLM 接入方式

- 使用 **OpenAI 官方 Python SDK**
- 使用 `Async` 调用方式
- 使用 **Chat Completions / Responses API（二选一，选官方推荐的）**
- 模型默认使用：
    - `gpt-4.1` 或 `gpt-4o-mini`（以当前 SDK 推荐为准）

❌ 禁止使用：
- LangChain
- LangGraph
- 任何 Agent 框架

---

### 2️⃣ 架构分层（必须遵守）

请新增 / 使用以下逻辑分层（如果目录不存在，请创建）：

```
backend/
└── src/
    └── llm/
        ├── client.py        # OpenAI SDK 封装（唯一接触 SDK 的地方）
        ├── prompts/
        │   └── document_edit.py   # 文档修改 Prompt（字符串）
        └── service.py       # 业务级 LLM 服务（组合 Prompt + 输入）
```
---

## 三、职责边界（这是重点）

### `llm/client.py`

- **只负责：**
    - 初始化 OpenAI Client
    - 调用模型
    - 返回纯文本结果
- 不包含任何业务逻辑
- 不关心 Markdown / 文档结构

示例职责（不是完整代码）：

```
class OpenAIClient:
    async def generate(
        self,
        system_prompt: str,
        user_messages: list[dict]
    ) -> str:
        ...
```
---

### `llm/prompts/document_edit.py`

- 只存放 **Prompt 文本**
- Prompt 目标：
    - 输入：当前 Markdown 文档 + 用户指令
    - 输出：**完整的新 Markdown 文档**
- Prompt 使用清晰的分隔符（如 `---`）
- 不做 Diff，不做 Patch

---

### `llm/service.py`

- 业务层：
    - 组装 Prompt
    - 调用 `OpenAIClient`
    - 返回模型生成的 Markdown 字符串
- 对上层暴露清晰方法，例如：

```
async def edit_document(
    current_markdown: str,
    user_input: str
) -> str:
    ...
```
---

## 四、环境变量与配置要求

- 使用环境变量读取 API Key，例如：
    

`OPENAI_API_KEY`

- 不要把 Key 写入代码
    
- 若工程已有配置模块，请复用
    

---

## 五、错误处理（最低要求）

- 捕获 OpenAI SDK 异常
    
- 抛出清晰的业务异常（如 `LLMServiceError`）
    
- 日志中：
    
    - 不记录 API Key
        
    - 不打印完整 Prompt（可以只打印 hash / 长度）
        

---

## 六、集成点说明（必须给我）

请在实现完成后 **明确指出**：

1. 目前哪个接口 / 方法：
    
    - 已经真正调用了 OpenAI
        
2. 从用户输入到模型返回的完整调用路径
    
3. 如果我想替换为 Anthropic，需要改哪一个文件
    

---

## 七、明确禁止事项（再次强调）

❌ 不要引入 LangChain  
❌ 不要提前设计 Agent  
❌ 不要做多模型封装  
❌ 不要优化 Prompt 效果

---

## 八、验收标准

当我配置好 `OPENAI_API_KEY` 后：

- 调用后端接口
    
- 能看到：
    
    - OpenAI 被真实调用
        
    - 返回一份新的 Markdown 文档
        
- 即使内容不完美，也算成功
    

---

## 九、设计原则（请遵守）

> **让 LLM 看起来像一个“纯函数”：  
> 输入文本 → 输出文本**

如果你发现有多个实现方案，请选择：

> **最简单、最直接、最可维护的方案**