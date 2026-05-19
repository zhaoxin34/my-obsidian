---
title: "LangChain学习笔记"
date: 2026-02-06
tags: [langchain, ai, llm, python, chains, agents]
category: AI框架
status: 进行中
difficulty: 中级
estimated_time: "3-4周"
last_updated: 2026-02-06
version: "0.1"
---

# LangChain学习笔记

## 📖 目录
- [概述](#概述)
- [核心概念](#核心概念)
- [安装与配置](#安装与配置)
- [基础组件](#基础组件)
- [链式操作](#链式操作)
- [提示词模板](#提示词模板)
- [模型集成](#模型集成)
- [向量存储](#向量存储)
- [代理与工具](#代理与工具)
- [实际应用示例](#实际应用示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 🎯 概述

LangChain是一个用于开发由语言模型驱动的应用程序的强大框架。它旨在帮助开发者快速构建复杂的AI应用，支持多种语言模型和外部数据源。

### 主要特性
- **模块化设计**：松耦合的组件，易于组合和扩展
- **多模型支持**：OpenAI、Anthropic、Hugging Face等
- **丰富的数据集成**：文档加载、向量数据库、搜索工具
- **强大的链式操作**：将多个步骤组合成复杂的AI工作流
- **代理系统**：让AI能够使用工具和进行推理

---

## 🏗️ 核心概念

### 1. Models（模型）
LangChain支持多种类型的模型：
- **LLMs**：大语言模型（如GPT、Claude）
- **Chat Models**：对话模型
- **Embedding Models**：嵌入模型

### 2. Prompts（提示词）
管理和优化发送给模型的提示词：
- Prompt Templates
- Few-shot examples
- Output parsers

### 3. Chains（链）
将多个组件串联起来形成完整的应用逻辑：
- Simple chains
- Sequential chains
- Custom chains

### 4. Retrievers（检索器）
从外部数据源检索相关信息：
- Document loaders
- Text splitters
- Vector stores

### 5. Agents（代理）
让模型能够自主决策和使用工具：
- ReAct agents
- Plan-and-execute agents
- Custom agents

---

## ⚙️ 安装与配置

### 基本安装
```bash
pip install langchain
```

### 完整安装
```bash
pip install langchain[all]
```

### 环境变量配置
```bash
# .env文件
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 导入测试
```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# 测试基本功能
llm = OpenAI(temperature=0.7)
response = llm("你好，请介绍一下LangChain")
print(response)
```

---

## 🧩 基础组件

### LLM接口
```python
from langchain.llms import OpenAI
from langchain.llms import Anthropic

# OpenAI LLM
llm = OpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000
)

# Anthropic LLM
claude = Anthropic(
    model="claude-2",
    temperature=0.7
)
```

### Chat Model接口
```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

chat_model = ChatOpenAI(temperature=0.7)

messages = [
    SystemMessage(content="你是一个有用的AI助手"),
    HumanMessage(content="请解释什么是机器学习")
]

response = chat_model(messages)
print(response.content)
```

### Embedding模型
```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# 生成文本嵌入
text = "LangChain是一个强大的AI框架"
vector = embeddings.embed_query(text)

# 生成文档嵌入
documents = ["文档1", "文档2", "文档3"]
doc_vectors = embeddings.embed_documents(documents)
```

---

## 🔗 链式操作

### 简单链
```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 创建LLM
llm = OpenAI(temperature=0.7)

# 创建提示词模板
prompt = PromptTemplate(
    input_variables=["topic"],
    template="请用100字解释{topic}"
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行链
result = chain.run(topic="人工智能")
print(result)
```

### 顺序链
```python
from langchain.chains import SimpleSequentialChain

# 第一步：生成产品描述
first_prompt = PromptTemplate(
    input_variables=["product"],
    template="为{product}生成一个吸引人的标题"
)

# 第二步：生成营销文案
second_prompt = PromptTemplate(
    input_variables=["title"],
    template="基于这个标题{title}，写一段营销文案"
)

# 创建链
chain1 = LLMChain(llm=llm, prompt=first_prompt)
chain2 = LLMChain(llm=llm, prompt=second_prompt)
overall_chain = SimpleSequentialChain(
    chains=[chain1, chain2],
    verbose=True
)

# 运行
result = overall_chain.run("智能手表")
```

---

## 📝 提示词模板

### 基础模板
```python
from langchain.prompts import PromptTemplate

template = """
你是一个专业的{role}。

任务：{task}
要求：{requirements}

请提供详细的解答。
"""

prompt = PromptTemplate(
    input_variables=["role", "task", "requirements"],
    template=template
)

# 格式化提示词
formatted_prompt = prompt.format(
    role="技术顾问",
    task="解释区块链技术",
    requirements="用通俗易懂的语言，适合初学者"
)
```

### Few-shot示例
```python
from langchain.prompts import FewShotPromptTemplate

examples = [
    {
        "input": "什么是AI？",
        "output": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统，如视觉感知、语音识别、决策制定和语言翻译。"
    },
    {
        "input": "什么是ML？",
        "output": "机器学习（ML）是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进，通过算法从数据中识别模式并做出预测或决策。"
    }
]

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="问题：{input}\n回答：{output}"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="以下是一些问题和对应的详细回答示例：\n",
    suffix="\n现在请回答这个问题：{input}",
    input_variables=["input"]
)
```

---

## 🤖 模型集成

### OpenAI集成
```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

# LLM
llm = OpenAI(
    model_name="gpt-3.5-turbo-instruct",
    temperature=0.9,
    max_tokens=1024
)

# Chat Model
chat = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

# Embeddings
embeddings = OpenAIEmbeddings(
    model_name="text-embedding-ada-002"
)
```

### Anthropic集成
```python
from langchain.llms import Anthropic
from langchain.chat_models import ChatAnthropic

# LLM
claude_llm = Anthropic(
    model="claude-2",
    temperature=0.7,
    max_tokens=1000
)

# Chat Model
claude_chat = ChatAnthropic(
    model="claude-2",
    temperature=0.7
)
```

### Hugging Face集成
```python
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_id = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=512,
    temperature=0.7
)

llm = HuggingFacePipeline(pipeline=pipe)
```

---

## 💾 向量存储

### Chroma向量存储
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

# 加载文档
loader = TextLoader("document.txt")
documents = loader.load()

# 文本分割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings
)

# 相似性搜索
docs = vectorstore.similarity_search("AI技术", k=3)
print(docs[0].page_content)
```

### FAISS向量存储
```python
from langchain.vectorstores import FAISS

# 创建向量存储
vectorstore = FAISS.from_documents(
    documents=splits,
    embedding=embeddings
)

# 保存到本地
vectorstore.save_local("faiss_index")

# 从本地加载
loaded_vectorstore = FAISS.load_local("faiss_index", embeddings)
```

### 文档检索链
```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# 创建检索QA链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 执行问答
query = "LangChain的主要功能是什么？"
result = qa_chain.run(query)
print(result)
```

---

## 🛠️ 代理与工具

### 基础代理
```python
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

# 定义工具
def calculator(expression):
    """执行数学计算"""
    try:
        return eval(expression)
    except:
        return "计算错误"

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="用于执行数学计算"
    )
]

# 创建代理
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# 运行代理
result = agent.run("计算(15 * 8) + 42")
print(result)
```

### 搜索工具
```python
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool

# Google搜索
serpapi = SerpAPIWrapper()
search_tool = Tool(
    name="Google Search",
    func=serpapi.run,
    description="用于搜索最新信息"
)

# 使用搜索工具的代理
agent_with_search = initialize_agent(
    [search_tool],
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

result = agent_with_search.run("LangChain的最新版本是什么？")
```

### 自定义工具
```python
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="城市名称")

class WeatherTool(BaseTool):
    name = "Weather Checker"
    description = "获取指定城市的天气信息"
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        # 这里可以调用真实的天气API
        weather_data = f"{location}的天气：晴朗，25°C"
        return weather_data

# 创建工具实例
weather_tool = WeatherTool()

# 在代理中使用
tools = [weather_tool]
agent = initialize_agent(tools, llm, verbose=True)
```

---

## 💡 实际应用示例

### 1. 文档问答系统
```python
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_document_qa_system(pdf_path):
    # 加载PDF文档
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    # 创建向量存储
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )

    # 创建QA链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4})
    )

    return qa_chain

# 使用示例
qa_system = create_document_qa_system("document.pdf")
answer = qa_system.run("文档中的主要结论是什么？")
```

### 2. 智能客服机器人
```python
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

class CustomerServiceBot:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory()

        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""
            你是一个专业的客服代表。请根据对话历史和客户问题提供有用、友好的回答。

            对话历史：{history}
            客户问题：{input}

            请提供详细、专业的回答：
            """
        )

        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )

    def ask(self, question):
        return self.conversation.predict(input=question)

    def get_history(self):
        return self.memory.buffer

# 使用示例
bot = CustomerServiceBot()
response = bot.ask("我的订单什么时候能发货？")
```

### 3. 内容生成流水线
```python
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate

class ContentPipeline:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)

        # 第一步：生成大纲
        outline_template = """
        为主题"{topic}"生成一个详细的文章大纲，包含5-7个主要章节。
        """
        self.outline_prompt = PromptTemplate(
            input_variables=["topic"],
            template=outline_template
        )

        # 第二步：生成内容
        content_template = """
        基于以下大纲，生成一篇详细的文章：

        {outline}

        要求：
        - 每个章节至少200字
        - 使用生动的例子
        - 语言通俗易懂
        """
        self.content_prompt = PromptTemplate(
            input_variables=["outline"],
            template=content_template
        )

        # 创建顺序链
        self.outline_chain = LLMChain(
            llm=self.llm,
            prompt=self.outline_prompt,
            output_key="outline"
        )

        self.content_chain = LLMChain(
            llm=self.llm,
            prompt=self.content_prompt,
            output_key="content"
        )

        self.pipeline = SequentialChain(
            chains=[self.outline_chain, self.content_chain],
            input_variables=["topic"],
            output_variables=["outline", "content"],
            verbose=True
        )

    def generate_content(self, topic):
        result = self.pipeline({"topic": topic})
        return result

# 使用示例
pipeline = ContentPipeline()
article = pipeline.generate_content("人工智能的发展历程")
print("大纲：", article["outline"])
print("内容：", article["content"])
```

---

## ✅ 最佳实践

### 1. 提示词优化
- **明确具体的指令**：提供清晰的指导
- **使用示例**：few-shot学习提高效果
- **结构化输出**：指定返回格式
- **错误处理**：处理边界情况

```python
# 好的提示词示例
template = """
你是一个专业的技术文档写作者。

任务：为{product}编写产品说明文档

要求：
1. 包含产品概述、核心功能、技术规格
2. 使用清晰的章节结构
3. 包含实际使用示例
4. 字数控制在500-800字

产品信息：
{product_info}

请按照以上要求生成文档：
"""

prompt = PromptTemplate(
    input_variables=["product", "product_info"],
    template=template
)
```

### 2. 链设计原则
- **单一职责**：每个链只负责一个特定任务
- **可组合性**：设计可重用的组件
- **错误处理**：添加适当的异常处理
- **性能优化**：合理使用缓存和批处理

```python
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler

class LoggingCallback(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"开始执行链: {serialized.get('name', 'Unknown')}")

    def on_chain_end(self, outputs, **kwargs):
        print(f"链执行完成: {outputs}")

# 使用回调
handler = LoggingCallback()
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
```

### 3. 向量存储优化
- **合适的分块策略**：根据内容类型调整chunk_size
- **重叠处理**：适当设置chunk_overlap避免上下文丢失
- **索引优化**：定期清理和重建索引
- **批量处理**：处理大量文档时使用批处理

```python
# 优化的文本分割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""],
    length_function=len
)

# 批量处理
def batch_process_documents(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        yield text_splitter.split_documents(batch)
```

### 4. 内存管理
- **对话记忆**：合理管理对话历史
- **缓存策略**：缓存常用查询结果
- **资源清理**：及时释放不需要的资源

```python
from langchain.memory import ConversationBufferWindowMemory

# 窗口记忆（只保留最近N轮对话）
memory = ConversationBufferWindowMemory(
    k=5,  # 只保留最近5轮对话
    return_messages=True
)
```

---

## ❓ 常见问题

### Q1: 如何处理API调用限制？
```python
import time
from langchain.llms import OpenAI

class RateLimitedLLM:
    def __init__(self, llm, max_calls_per_minute=60):
        self.llm = llm
        self.max_calls_per_minute = max_calls_per_minute
        self.call_times = []

    def __call__(self, *args, **kwargs):
        # 清理超过1分钟的调用记录
        current_time = time.time()
        self.call_times = [
            t for t in self.call_times
            if current_time - t < 60
        ]

        # 检查是否超过限制
        if len(self.call_times) >= self.max_calls_per_minute:
            sleep_time = 60 - (current_time - self.call_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # 记录调用时间
        self.call_times.append(current_time)

        return self.llm(*args, **kwargs)

# 使用示例
rate_limited_llm = RateLimitedLLM(llm, max_calls_per_minute=50)
```

### Q2: 如何优化大文档处理？
```python
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain

def process_large_document(file_path):
    # 加载文档
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()

    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    # Map-Reduce处理
    map_template = """
    请总结以下文档片段的要点：

    {docs}

    要点总结：
    """
    map_prompt = PromptTemplate.from_template(map_template)

    reduce_template = """
    将以下要点总结成一份完整的摘要：

    {doc_summaries}

    完整摘要：
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    # 创建处理链
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # 最终文档链
    combine_documents = StuffDocumentsChain(
        llm_chain=reduce_chain,
        document_variable_name="doc_summaries"
    )

    reduce_documents = ReduceDocumentsChain(
        combine_documents=combine_documents,
        collapse_documents=combine_documents,
        token_max=4000
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents,
        document_variable_name="docs"
    )

    return map_reduce_chain.run(splits)
```

### Q3: 如何调试LangChain应用？
```python
import logging
from langchain.callbacks.base import BaseCallbackHandler

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugCallback(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        logger.debug(f"链开始: {serialized}")
        logger.debug(f"输入: {inputs}")

    def on_chain_end(self, outputs, **kwargs):
        logger.debug(f"链结束: {outputs}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        logger.debug(f"LLM开始: {serialized}")
        logger.debug(f"提示词: {prompts}")

    def on_llm_end(self, response, **kwargs):
        logger.debug(f"LLM结束: {response}")

# 在应用中使用调试回调
debug_handler = DebugCallback()
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[debug_handler])
```

### Q4: 如何实现自定义代理？
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage

class CustomAgent:
    def __init__(self, llm, tools, prompt_template):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}

        prompt = PromptTemplate.from_template(prompt_template)
        self.agent = create_react_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            max_iterations=10
        )

    def run(self, query):
        return self.agent_executor.run(query)

# 自定义代理示例
tools = [
    Tool(
        name="Weather",
        func=self.get_weather,
        description="获取天气信息"
    ),
    Tool(
        name="Calculator",
        func=self.calculate,
        description="执行计算"
    )
]

prompt_template = """
使用以下工具回答用户问题。

可用工具: {tools}
工具描述: {tool_descriptions}

用户问题: {input}
{agent_scratchpad}
"""

agent = CustomAgent(llm, tools, prompt_template)
```

---

## 📚 学习资源

### 官方资源
- [LangChain官方文档](https://python.langchain.com/)
- [LangChain GitHub仓库](https://github.com/langchain-ai/langchain)
- [LangChain Hub](https://smith.langchain.com/)

### 推荐教程
- LangChain官方教程和示例
- YouTube上的LangChain实战教程
- 各大学习平台的LangChain课程

### 社区资源
- LangChain Discord社区
- Stack Overflow上的LangChain标签
- Reddit的r/LangChain社区

---

```mermaid theme={"theme":{"light":"catppuccin-latte","dark":"catppuccin-mocha"}}
%%{
  init: {
    "fontFamily": "monospace",
    "flowchart": {
      "curve": "curve"
    }
  }
}%%
graph TD
  %% Outside the agent
  QUERY([input])
  LLM{model}
  TOOL(tools)
  ANSWER([output])

  %% Main flows (no inline labels)
  QUERY --> LLM
  LLM --"action"--> TOOL
  TOOL --"observation"--> LLM
  LLM --"finish"--> ANSWER

  classDef blueHighlight fill:#E5F4FF,stroke:#006DDD,color:#030710;
  classDef greenHighlight fill:#F6FFDB,stroke:#6E8900,color:#2E3900;
  class QUERY blueHighlight;
  class ANSWER blueHighlight;
  class LLM greenHighlight;
  class TOOL greenHighlight;
```
## 🔄 持续学习

### 版本更新追踪
- 关注LangChain GitHub releases
- 订阅官方博客和通讯
- 参与社区讨论

### 实践项目建议
1. 构建个人知识库问答系统
2. 开发多模态AI应用
3. 创建自动化工作流
4. 集成多个数据源的智能助手

### 下一步学习方向
- LangGraph：构建复杂的多智能体系统
- LangServe：部署LangChain应用
- LangSmith：调试和监控工具
- 更多模型提供商集成

---

*本笔记将持续更新，记录LangChain的学习过程和实践经验。*

**创建时间**: 2026-02-06
**最后更新**: 2026-02-06
**版本**: v0.1