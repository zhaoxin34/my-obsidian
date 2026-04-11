---
title: "LangGraph学习教程"
date: 2026-02-06
tags: [langgraph, ai, workflows, state-machines, python, tutorial]
category: AI框架
status: 进行中
difficulty: 高级
estimated_time: "4-6周"
last_updated: 2026-02-06
version: "0.1"
---

# LangGraph学习教程

## 📖 目录
- [概述](#概述)
- [为什么选择LangGraph](#为什么选择langgraph)
- [安装与配置](#安装与配置)
- [核心概念](#核心概念)
- [基础组件](#基础组件)
- [状态管理](#状态管理)
- [图结构设计](#图结构设计)
- [工作流程](#工作流程)
- [实际应用示例](#实际应用示例)
- [高级特性](#高级特性)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [扩展资源](#扩展资源)

---

## 🎯 概述

LangGraph是LangChain生态系统中的一个强大框架，专门用于构建**复杂的有状态多Agent应用**。它基于**状态图（StateGraph）**的概念，允许开发者创建动态、可控的AI工作流。

### 核心特性
- **状态化工作流**: 每个节点都维护和更新应用状态
- **条件分支**: 根据状态动态决定下一个执行节点
- **多Agent协调**: 轻松管理多个Agent之间的交互
- **可观察性**: 内置的调试和监控功能
- **可扩展性**: 模块化设计，易于扩展和定制

### 应用场景
- **多步骤AI任务**: 需要多轮对话和推理的复杂任务
- **Agent团队协作**: 多个专业化Agent协同工作
- **动态决策流程**: 需要根据上下文动态调整执行路径
- **业务流程自动化**: AI驱动的业务流程和工作流

---

## 🤔 为什么选择LangGraph

### vs 传统LangChain Chain

| 特性 | LangChain Chain | LangGraph |
|------|-----------------|-----------|
| **状态管理** | 无状态或有限状态 | 完整状态管理 |
| **分支逻辑** | 线性流程 | 动态条件分支 |
| **Agent协调** | 困难 | 自然支持 |
| **错误处理** | 基础 | 高级错误恢复 |
| **调试性** | 有限 | 完整执行追踪 |
| **复杂度** | 简单任务 | 复杂工作流 |

### 主要优势

#### 1. **状态感知**
```python
# LangChain - 无状态
result = chain.run("用户输入")

# LangGraph - 有状态
state = graph.invoke({"messages": ["用户输入"]})
# 状态在整个执行过程中被维护和更新
```

#### 2. **动态路由**
```python
# 根据条件动态选择下一个节点
def route_after_analysis(state):
    if state["confidence"] > 0.8:
        return "high_confidence"
    elif state["needs_human"] == True:
        return "human_review"
    else:
        return "additional_research"
```

#### 3. **Agent编排**
```python
# 多Agent协作
researcher_agent = create_researcher_agent()
writer_agent = create_writer_agent()
reviewer_agent = create_reviewer_agent()

# Agent间的状态传递
def research_step(state):
    # Researcher完成研究，更新状态
    return {"research_data": researcher_agent.run(state["topic"])}

def write_step(state):
    # Writer基于research_data写作
    return {"draft": writer_agent.run(state["research_data"])}

def review_step(state):
    # Reviewer审阅并决定下一步
    feedback = reviewer_agent.run(state["draft"])
    return {"feedback": feedback, "approved": feedback["score"] > 8}
```

---

## ⚙️ 安装与配置

### 基本安装

```bash
# 安装LangGraph
pip install langgraph

# 或使用conda
conda install -c conda-forge langgraph

# 验证安装
python -c "import langgraph; print(langgraph.__version__)"
```

### 完整安装（含可选依赖）

```bash
pip install langgraph[all]

# 包含的依赖：
# - langchain: 核心框架
# - langchain-community: 社区集成
# - langchain-core: 核心组件
# - pydantic: 数据验证
# - python-dotenv: 环境变量管理
```

### 环境配置

```bash
# .env文件
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=langgraph-tutorial
```

### 基本测试

```python
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 检查安装
print("LangGraph版本:", __import__langgraph__).__version__)

# 创建简单的状态图
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def test_graph():
    graph = StateGraph(AgentState)

    def node_1(state):
        return {"messages": ["Node 1 processed"]}

    def node_2(state):
        return {"messages": ["Node 2 processed"]}

    graph.add_node("node_1", node_1)
    graph.add_node("node_2", node_2)
    graph.add_edge("node_1", "node_2")
    graph.add_edge("node_2", END)

    app = graph.compile()

    result = app.invoke({"messages": []})
    print("测试结果:", result)

test_graph()
```

---

## 🏗️ 核心概念

### 1. StateGraph（状态图）

StateGraph是LangGraph的核心概念，它定义了一个**有状态的工作流**：

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class MyState(TypedDict):
    current_step: str
    data: dict
    messages: list[str]

# 创建状态图
graph = StateGraph(MyState)

# 添加节点和边
graph.add_node("start", start_node)
graph.add_node("process", process_node)
graph.add_node("end", end_node)

graph.add_edge("start", "process")
graph.add_edge("process", "end")
graph.add_edge("end", END)
```

### 2. Nodes（节点）

节点是工作流中的**处理单元**，可以是函数、类或Agent：

```python
# 函数式节点
def research_node(state: MyState) -> MyState:
    """研究步骤节点"""
    topic = state["data"]["topic"]
    research = perform_research(topic)

    return {
        "current_step": "research",
        "data": {**state["data"], "research": research}
    }

# Agent节点
from langchain.agents import create_openai_functions_agent

def agent_node(state: MyState, agent, prompt) -> MyState:
    """Agent处理节点"""
    response = agent.invoke({
        "input": state["data"]["question"],
        "chat_history": state["messages"]
    })

    return {
        "messages": state["messages"] + [response["output"]],
        "data": {**state["data"], "last_response": response}
    }
```

### 3. Edges（边）

边定义节点间的**连接关系**：

```python
# 固定边
graph.add_edge("node_a", "node_b")

# 条件边
def route_function(state: MyState) -> str:
    if state["confidence"] > 0.8:
        return "high_confidence_path"
    else:
        return "low_confidence_path"

graph.add_conditional_edges(
    "decision_node",
    route_function,
    {
        "high_confidence_path": "approve_node",
        "low_confidence_path": "review_node"
    }
)
```

### 4. State（状态）

状态是**在整个工作流中维护的数据结构**：

```python
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator

class WorkflowState(TypedDict):
    # 基本状态
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 业务数据
    user_query: str
    research_data: Optional[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]]

    # 控制流
    confidence: float
    needs_human_review: bool
    error_count: int

    # 元数据
    metadata: Dict[str, Any]
    step_count: int

def update_state(state: WorkflowState, updates: Dict[str, Any]) -> WorkflowState:
    """状态更新函数"""
    return {
        **state,
        **updates,
        "step_count": state["step_count"] + 1,
        "metadata": {**state["metadata"], "last_update": updates.get("current_step")}
    }
```

---

## 🧩 基础组件

### 1. 节点类型

#### A. Function Node（函数节点）

```python
def simple_node(state: MyState) -> MyState:
    """简单函数节点"""
    return {
        "current_step": "completed",
        "messages": state["messages"] + ["处理完成"]
    }

# 添加到图
graph.add_node("process", simple_node)
```

#### B. Agent Node（Agent节点）

```python
from langchain.agents import create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

def create_researcher_agent():
    """创建研究Agent"""
    tools = [
        Tool(
            name="web_search",
            description="搜索网络信息",
            func=web_search_tool
        ),
        Tool(
            name="data_analysis",
            description="分析数据",
            func=analyze_data_tool
        )
    ]

    prompt = PromptTemplate.from_template("""
    你是一个专业的研究助手。

    任务：{task}
    当前上下文：{context}

    请使用可用的工具进行研究，并将结果以结构化格式返回。
    """)

    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    return agent

def research_agent_node(state: WorkflowState) -> WorkflowState:
    """研究Agent节点"""
    agent = create_researcher_agent()

    response = agent.invoke({
        "task": state["user_query"],
        "context": str(state.get("metadata", {}))
    })

    return {
        **state,
        "current_step": "research",
        "research_data": parse_research_response(response["output"]),
        "messages": state["messages"] + [f"研究完成: {response['output']}"]
    }

graph.add_node("research", research_agent_node)
```

#### C. Router Node（路由器节点）

```python
def intelligent_router(state: WorkflowState) -> str:
    """智能路由器节点"""
    query = state["user_query"].lower()
    confidence = state["confidence"]

    # 根据查询类型路由
    if any(keyword in query for keyword in ["搜索", "查找", "什么"]):
        return "search"
    elif any(keyword in query for keyword in ["计算", "数学", "等于"]):
        return "calculate"
    elif any(keyword in query for keyword in ["分析", "比较", "评估"]):
        return "analyze"
    elif confidence < 0.7:
        return "clarify"
    else:
        return "general_processing"

graph.add_conditional_edges(
    "router",
    intelligent_router,
    {
        "search": "web_search",
        "calculate": "calculator",
        "analyze": "data_analysis",
        "clarify": "human_input",
        "general_processing": "llm_processing"
    }
)
```

### 2. 边类型

#### A. 固定边（Fixed Edges）

```python
# 简单的线性流程
graph.add_edge("start", "process")
graph.add_edge("process", "review")
graph.add_edge("review", "end")
```

#### B. 条件边（Conditional Edges）

```python
def quality_check(state: WorkflowState) -> str:
    """质量检查路由器"""
    score = state.get("quality_score", 0)
    human_review_needed = state.get("needs_human_review", False)

    if human_review_needed:
        return "human_review"
    elif score >= 8.0:
        return "approve"
    elif score >= 6.0:
        return "revision"
    else:
        return "reject"

# 添加条件边
graph.add_conditional_edges(
    "quality_check",
    quality_check,
    {
        "human_review": "human_input",
        "approve": "finalize",
        "revision": "improve",
        "reject": "restart"
    }
)
```

#### C. 循环边（Loop Edges）

```python
def should_continue(state: WorkflowState) -> bool:
    """判断是否继续循环"""
    max_iterations = state.get("max_iterations", 5)
    current_iteration = state.get("step_count", 0)

    # 继续条件
    should_continue = (
        current_iteration < max_iterations and
        state.get("needs_improvement", True) and
        not state.get("converged", False)
    )

    return should_continue

# 创建循环
graph.add_edge("improve", "quality_check")
graph.add_edge("quality_check", "finalize", condition=should_continue)
```

### 3. 特殊节点

#### A. 错误处理节点

```python
def error_handler(state: WorkflowState, error: Exception) -> WorkflowState:
    """错误处理节点"""
    error_count = state.get("error_count", 0) + 1

    # 根据错误类型决定处理策略
    if isinstance(error, TimeoutError):
        strategy = "retry_with_timeout"
    elif isinstance(error, ValueError):
        strategy = "validate_input"
    elif isinstance(error, ConnectionError):
        strategy = "retry_with_backoff"
    else:
        strategy = "escalate_to_human"

    return {
        **state,
        "current_step": "error_handling",
        "error": str(error),
        "error_count": error_count,
        "recovery_strategy": strategy,
        "needs_improvement": True
    }

# 添加错误处理
graph.add_node("handle_error", error_handler)
```

#### B. 人工干预节点

```python
def human_intervention(state: WorkflowState) -> WorkflowState:
    """人工干预节点"""
    print("需要人工干预:")
    print(f"当前状态: {state}")

    # 这里可以集成UI界面或聊天界面
    user_input = input("请提供输入 (或输入 'skip' 跳过): ")

    if user_input.lower() == 'skip':
        return {**state, "human_input": None, "skipped": True}
    else:
        return {
            **state,
            "human_input": user_input,
            "needs_human_review": False
        }

graph.add_node("human_review", human_intervention)
```

---

## 💾 状态管理

### 1. 状态结构设计

#### 基础状态类

```python
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator

class BaseWorkflowState(TypedDict):
    # 必需字段
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 可选字段
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: Optional[str]

# 扩展状态
class ResearchWorkflowState(BaseWorkflowState):
    # 业务数据
    research_topic: str
    research_data: Optional[Dict[str, Any]]
    sources: List[str]

    # 分析结果
    analysis: Optional[Dict[str, Any]]
    confidence_score: float

    # 控制流
    requires_human_review: bool
    revision_count: int
    max_revisions: int

    # 质量控制
    quality_score: Optional[float]
    plagiarism_check: Optional[bool]
    fact_check_status: Optional[str]
```

#### 状态更新器

```python
def create_state_updater(state_class):
    """创建状态更新器"""
    def update_state(current_state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        # 验证更新
        validated_updates = validate_updates(updates, state_class)

        # 合并状态
        new_state = {**current_state, **validated_updates}

        # 添加元数据
        if "step_count" not in new_state:
            new_state["step_count"] = 0

        new_state["step_count"] += 1
        new_state["last_updated"] = str(datetime.now())

        return new_state

    return update_state

def validate_updates(updates: Dict[str, Any], state_class) -> Dict[str, Any]:
    """验证状态更新"""
    # 这里可以添加更复杂的验证逻辑
    validated = {}

    for key, value in updates.items():
        # 基本类型检查
        if key in state_class.__annotations__:
            expected_type = state_class.__annotations__[key]

            if isinstance(expected_type._name, str) and expected_type._name.startswith("Optional"):
                if value is not None:
                    validated[key] = value
            elif isinstance(expected_type, type):
                if isinstance(value, expected_type):
                    validated[key] = value
                else:
                    raise ValueError(f"类型不匹配: {key}")
            else:
                validated[key] = value
        else:
            # 允许额外的字段
            validated[key] = value

    return validated
```

### 2. 状态持久化

#### 内存存储

```python
from typing import Union
import json
import uuid
from datetime import datetime

class InMemoryStateStore:
    """内存状态存储"""

    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}

    def save_state(self, session_id: str, state: Dict[str, Any]) -> None:
        """保存状态"""
        self.states[session_id] = {
            **state,
            "saved_at": datetime.now().isoformat()
        }

    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """加载状态"""
        return self.states.get(session_id)

    def delete_state(self, session_id: str) -> bool:
        """删除状态"""
        if session_id in self.states:
            del self.states[session_id]
            return True
        return False

    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        return list(self.states.keys())

# 全局状态存储实例
state_store = InMemoryStateStore()

def with_persistence(func):
    """状态持久化装饰器"""
    def wrapper(state: Dict[str, Any], *args, **kwargs):
        session_id = state.get("session_id", str(uuid.uuid4()))

        # 加载之前的状态
        previous_state = state_store.load_state(session_id)
        if previous_state:
            state = {**previous_state, **state}

        # 执行函数
        result = func(state, *args, **kwargs)

        # 保存新状态
        state_store.save_state(session_id, result)

        return result

    return wrapper

# 使用示例
@with_persistence
def persistent_node(state: WorkflowState) -> WorkflowState:
    """持久化节点"""
    return {
        **state,
        "current_step": "processed",
        "messages": state["messages"] + ["状态已持久化"]
    }
```

#### Redis存储

```python
import redis
import json
from typing import Any

class RedisStateStore:
    """Redis状态存储"""

    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def save_state(self, session_id: str, state: Dict[str, Any], ttl: int = 3600) -> None:
        """保存状态到Redis"""
        serialized_state = json.dumps(state, default=str)
        self.redis_client.setex(
            f"langgraph:{session_id}",
            ttl,
            serialized_state
        )

    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """从Redis加载状态"""
        serialized_state = self.redis_client.get(f"langgraph:{session_id}")
        if serialized_state:
            try:
                return json.loads(serialized_state)
            except json.JSONDecodeError:
                return None
        return None

    def delete_state(self, session_id: str) -> bool:
        """从Redis删除状态"""
        return bool(self.redis_client.delete(f"langgraph:{session_id}"))

# Redis状态存储
redis_store = RedisStateStore()

def with_redis_persistence(ttl: int = 3600):
    """Redis持久化装饰器"""
    def decorator(func):
        def wrapper(state: Dict[str, Any], *args, **kwargs):
            session_id = state.get("session_id")
            if not session_id:
                return func(state, *args, **kwargs)

            # 加载之前的状态
            previous_state = redis_store.load_state(session_id)
            if previous_state:
                state = {**previous_state, **state}

            # 执行函数
            result = func(state, *args, **kwargs)

            # 保存新状态
            redis_store.save_state(session_id, result, ttl)

            return result

        return wrapper
    return decorator
```

### 3. 状态验证

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class WorkflowStateModel(BaseModel):
    """状态验证模型"""
    current_step: str = Field(..., min_length=1)
    messages: List[str] = Field(default_factory=list)

    research_topic: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_human_review: bool = Field(default=False)

    class Config:
        extra = "allow"  # 允许额外字段

    @validator('current_step')
    def validate_step(cls, v):
        allowed_steps = [
            'start', 'research', 'analysis', 'review',
            'revision', 'finalize', 'error', 'end'
        ]
        if v not in allowed_steps:
            raise ValueError(f'无效的步骤: {v}')
        return v

def validate_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """验证状态"""
    try:
        validated_model = WorkflowStateModel(**state)
        return validated_model.dict()
    except Exception as e:
        raise ValueError(f"状态验证失败: {e}")

# 在节点中使用验证
def validated_research_node(state: WorkflowState) -> WorkflowState:
    """带验证的研究节点"""
    # 验证输入状态
    validated_state = validate_state(state)

    # 执行处理
    result = perform_research(validated_state["research_topic"])

    # 验证输出状态
    output_state = {
        **validated_state,
        "current_step": "research",
        "research_data": result,
        "messages": validated_state["messages"] + ["研究完成"]
    }

    return validate_state(output_state)
```

---

## 🔀 图结构设计

### 1. 线性图（Linear Graph）

最简单的图结构，节点按顺序执行：

```python
from langgraph.graph import StateGraph, END

def create_linear_workflow():
    """创建线性工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("start", start_node)
    graph.add_node("research", research_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("write", write_node)
    graph.add_node("review", review_node)
    graph.add_node("finalize", finalize_node)

    # 添加边
    graph.add_edge("start", "research")
    graph.add_edge("research", "analyze")
    graph.add_edge("analyze", "write")
    graph.add_edge("write", "review")
    graph.add_edge("review", "finalize")
    graph.add_edge("finalize", END)

    # 设置入口点
    graph.set_entry_point("start")

    return graph.compile()

# 节点定义
def start_node(state: WorkflowState) -> WorkflowState:
    return {
        **state,
        "current_step": "start",
        "messages": state["messages"] + ["工作流开始"]
    }

def research_node(state: WorkflowState) -> WorkflowState:
    # 执行研究
    research_data = perform_research(state["research_topic"])
    return {
        **state,
        "current_step": "research",
        "research_data": research_data,
        "messages": state["messages"] + ["研究完成"]
    }

# 其他节点类似定义...
```

### 2. 分支图（Branch Graph）

支持根据条件选择不同路径：

```python
def create_branching_workflow():
    """创建分支工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("classify", classify_query_node)
    graph.add_node("research", research_node)
    graph.add_node("calculate", calculator_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("search", search_node)
    graph.add_node("general", general_llm_node)
    graph.add_node("finalize", finalize_node)

    # 设置入口点
    graph.set_entry_point("classify")

    # 添加条件分支
    def route_by_type(state: WorkflowState) -> str:
        query_type = state.get("query_type", "general")

        type_mapping = {
            "research": "research",
            "calculation": "calculate",
            "analysis": "analyze",
            "search": "search",
            "general": "general"
        }

        return type_mapping.get(query_type, "general")

    graph.add_conditional_edges(
        "classify",
        route_by_type,
        {
            "research": "research",
            "calculate": "calculate",
            "analyze": "analyze",
            "search": "search",
            "general": "general"
        }
    )

    # 所有分支都汇聚到finalize
    for node in ["research", "calculate", "analyze", "search", "general"]:
        graph.add_edge(node, "finalize")

    graph.add_edge("finalize", END)

    return graph.compile()

def classify_query_node(state: WorkflowState) -> WorkflowState:
    """查询分类节点"""
    query = state["user_query"]

    # 简单的分类逻辑
    if any(word in query.lower() for word in ["研究", "调查", "分析"]):
        query_type = "research"
    elif any(word in query.lower() for word in ["计算", "数学", "等于", "+", "-", "*", "/"]):
        query_type = "calculation"
    elif any(word in query.lower() for word in ["比较", "评估", "分析"]):
        query_type = "analysis"
    elif any(word in query.lower() for word in ["搜索", "查找", "什么"]):
        query_type = "search"
    else:
        query_type = "general"

    return {
        **state,
        "current_step": "classify",
        "query_type": query_type,
        "messages": state["messages"] + [f"查询类型: {query_type}"]
    }
```

### 3. 循环图（Loop Graph）

支持迭代处理，直到满足终止条件：

```python
def create_iterative_workflow():
    """创建迭代工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("analyze", analyze_node)
    graph.add_node("improve", improve_node)
    graph.add_node("review", quality_check_node)
    graph.add_node("finalize", finalize_node)

    # 设置入口点
    graph.set_entry_point("analyze")

    # 条件边用于循环
    def should_continue_loop(state: WorkflowState) -> str:
        """判断是否继续循环"""
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 3)
        quality_score = state.get("quality_score", 0)

        if iteration_count >= max_iterations:
            return "finalize"
        elif quality_score >= 8.0:
            return "finalize"
        else:
            return "improve"

    # 添加循环边
    graph.add_conditional_edges(
        "review",
        should_continue_loop,
        {
            "improve": "improve",
            "finalize": "finalize"
        }
    )

    # 改进后回到分析
    graph.add_edge("improve", "analyze")
    graph.add_edge("analyze", "review")
    graph.add_edge("finalize", END)

    return graph.compile()

def quality_check_node(state: WorkflowState) -> WorkflowState:
    """质量检查节点"""
    iteration_count = state.get("iteration_count", 0)

    # 模拟质量评分
    quality_score = min(9.0 - iteration_count * 1.5, 10.0)

    return {
        **state,
        "current_step": "review",
        "quality_score": quality_score,
        "iteration_count": iteration_count + 1,
        "messages": state["messages"] + [
            f"第{iteration_count + 1}次迭代，质量评分: {quality_score:.1f}"
        ]
    }

def improve_node(state: WorkflowState) -> WorkflowState:
    """改进节点"""
    quality_score = state["quality_score"]
    current_output = state.get("current_output", "")

    # 基于质量分数决定改进策略
    if quality_score < 5.0:
        strategy = "major_revision"
        improvement = "进行重大修改"
    elif quality_score < 7.0:
        strategy = "minor_revision"
        improvement = "进行小幅调整"
    else:
        strategy = "fine_tuning"
        improvement = "进行精细调优"

    return {
        **state,
        "current_step": "improve",
        "improvement_strategy": strategy,
        "current_output": current_output + f"\n[{strategy}] {improvement}",
        "messages": state["messages"] + [f"改进策略: {improvement}"]
    }
```

### 4. 并行图（Parallel Graph）

支持并行执行多个分支：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

def create_parallel_workflow():
    """创建并行工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("parallel_research", parallel_research_node)
    graph.add_node("synthesize", synthesize_results_node)
    graph.add_node("finalize", finalize_node)

    # 设置入口点
    graph.set_entry_point("parallel_research")

    # 添加边
    graph.add_edge("parallel_research", "synthesize")
    graph.add_edge("synthesize", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()

def parallel_research_node(state: WorkflowState) -> WorkflowState:
    """并行研究节点"""
    research_topics = state.get("research_topics", [])

    if not research_topics:
        return {
            **state,
            "current_step": "parallel_research",
            "research_results": {},
            "messages": state["messages"] + ["没有研究主题"]
        }

    # 并行执行研究
    research_results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交所有研究任务
        future_to_topic = {
            executor.submit(perform_research, topic): topic
            for topic in research_topics
        }

        # 收集结果
        for future in as_completed(future_to_topic):
            topic = future_to_topic[future]
            try:
                result = future.result()
                research_results[topic] = result
            except Exception as e:
                research_results[topic] = {"error": str(e)}

    return {
        **state,
        "current_step": "parallel_research",
        "research_results": research_results,
        "messages": state["messages"] + [
            f"并行研究完成，处理了{len(research_topics)}个主题"
        ]
    }

def synthesize_results_node(state: WorkflowState) -> WorkflowState:
    """综合结果节点"""
    research_results = state.get("research_results", {})

    # 综合所有研究结果
    synthesis = []
    for topic, result in research_results.items():
        if "error" not in result:
            synthesis.append(f"## {topic}\n{result.get('summary', '')}")
        else:
            synthesis.append(f"## {topic}\n错误: {result['error']}")

    final_synthesis = "\n\n".join(synthesis)

    return {
        **state,
        "current_step": "synthesize",
        "synthesis": final_synthesis,
        "messages": state["messages"] + ["结果综合完成"]
    }

def perform_research(topic: str) -> Dict[str, Any]:
    """执行单个研究任务"""
    # 模拟研究过程
    import time
    import random

    time.sleep(random.uniform(1, 3))  # 模拟处理时间

    return {
        "topic": topic,
        "summary": f"关于'{topic}'的研究总结",
        "key_findings": [f"发现{i}" for i in range(1, 4)],
        "confidence": random.uniform(0.7, 0.95)
    }
```

---

## ⚡ 工作流程

### 1. 基本执行流程

```python
# 创建工作流
workflow = create_linear_workflow()

# 准备初始状态
initial_state = {
    "current_step": "start",
    "messages": [],
    "user_query": "分析人工智能的发展趋势",
    "research_topic": "人工智能发展",
    "session_id": "session_123"
}

# 执行工作流
result = workflow.invoke(initial_state)

print("执行结果:")
print(f"最终步骤: {result['current_step']}")
print(f"消息: {result['messages']}")
print(f"研究数据: {result.get('research_data', 'N/A')}")
```

### 2. 流式执行

```python
def stream_execution(workflow, initial_state):
    """流式执行工作流"""
    print("开始流式执行...")

    # 获取生成器
    generator = workflow.stream(initial_state)

    for step in generator:
        node_name = list(step.keys())[0]
        node_state = step[node_name]

        print(f"\n=== 执行节点: {node_name} ===")
        print(f"状态: {node_state.get('current_step', 'unknown')}")
        print(f"消息: {node_state.get('messages', [])}")

        # 可以在这里添加自定义处理逻辑
        if node_state.get("confidence", 0) < 0.5:
            print("⚠️  置信度较低，可能需要人工干预")

    print("\n=== 执行完成 ===")

# 使用流式执行
stream_execution(workflow, initial_state)
```

### 3. 错误处理和恢复

```python
from functools import wraps

def with_error_handling(max_retries: int = 3):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(state: WorkflowState, *args, **kwargs):
            error_count = state.get("error_count", 0)

            for attempt in range(max_retries):
                try:
                    return func(state, *args, **kwargs)
                except Exception as e:
                    error_count += 1
                    print(f"尝试 {attempt + 1} 失败: {e}")

                    if attempt == max_retries - 1:
                        # 最后一次尝试失败，进入错误处理流程
                        return handle_critical_error(state, e)

                    # 更新状态并重试
                    state = {
                        **state,
                        "error_count": error_count,
                        "last_error": str(e),
                        "retry_attempt": attempt + 1
                    }

            return state

        return wrapper
    return decorator

def handle_critical_error(state: WorkflowState, error: Exception) -> WorkflowState:
    """处理关键错误"""
    return {
        **state,
        "current_step": "error",
        "error": str(error),
        "error_handled": False,
        "messages": state["messages"] + [
            f"遇到关键错误: {error}",
            "需要人工干预"
        ]
    }

@with_error_handling(max_retries=2)
def robust_research_node(state: WorkflowState) -> WorkflowState:
    """带错误处理的稳健研究节点"""
    topic = state["research_topic"]

    # 可能失败的操作
    research_data = perform_unreliable_research(topic)

    return {
        **state,
        "current_step": "research",
        "research_data": research_data,
        "messages": state["messages"] + ["研究成功完成"]
    }

def perform_unreliable_research(topic: str) -> Dict[str, Any]:
    """模拟可能失败的研究操作"""
    import random

    if random.random() < 0.3:  # 30%失败率
        raise ConnectionError("网络连接失败")

    return {
        "topic": topic,
        "findings": ["发现1", "发现2", "发现3"],
        "confidence": random.uniform(0.8, 0.95)
    }
```

### 4. 条件中断和恢复

```python
def create_interruptible_workflow():
    """创建可中断的工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("process", process_node)
    graph.add_node("check_approval", check_approval_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("continue", continue_node)
    graph.add_node("finalize", finalize_node)

    # 设置入口点
    graph.set_entry_point("process")

    # 添加边
    graph.add_edge("process", "check_approval")

    # 条件边用于人工干预
    def route_for_approval(state: WorkflowState) -> str:
        requires_approval = state.get("requires_approval", False)
        confidence = state.get("confidence", 1.0)

        if requires_approval or confidence < 0.8:
            return "human_review"
        else:
            return "continue"

    graph.add_conditional_edges(
        "check_approval",
        route_for_approval,
        {
            "human_review": "human_review",
            "continue": "continue"
        }
    )

    # 人工审查后可能继续或需要进一步修改
    graph.add_edge("human_review", "check_approval")
    graph.add_edge("continue", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()

def check_approval_node(state: WorkflowState) -> WorkflowState:
    """检查是否需要审批"""
    confidence = state.get("confidence", 0.0)
    requires_approval = confidence < 0.8

    return {
        **state,
        "current_step": "check_approval",
        "requires_approval": requires_approval,
        "messages": state["messages"] + [
            f"检查审批需求: {'是' if requires_approval else '否'} (置信度: {confidence:.2f})"
        ]
    }

def human_review_node(state: WorkflowState) -> WorkflowState:
    """人工审查节点"""
    print("🔴 需要人工干预")
    print(f"当前状态: {state}")

    # 模拟人工输入
    user_feedback = input("请提供审查意见 (或输入 'approve' 批准): ")

    if user_feedback.lower() == "approve":
        approval_status = "approved"
        confidence = min(state.get("confidence", 0.0) + 0.2, 1.0)
    else:
        approval_status = "rejected"
        confidence = state.get("confidence", 0.0) - 0.1

    return {
        **state,
        "current_step": "human_review",
        "human_feedback": user_feedback,
        "approval_status": approval_status,
        "confidence": max(0.0, confidence),
        "messages": state["messages"] + [
            f"人工审查: {user_feedback}",
            f"审批状态: {approval_status}"
        ]
    }
```

---

## 💡 实际应用示例

### 1. 研究报告生成系统

```python
def create_research_report_workflow():
    """创建研究报告生成工作流"""
    graph = StateGraph(ResearchReportState)

    # 添加节点
    graph.add_node("plan", plan_research_node)
    graph.add_node("collect_data", collect_data_node)
    graph.add_node("analyze", analyze_data_node)
    graph.add_node("write_draft", write_draft_node)
    graph.add_node("peer_review", peer_review_node)
    graph.add_node("revise", revise_draft_node)
    graph.add_node("finalize", finalize_report_node)

    # 设置入口点
    graph.set_entry_point("plan")

    # 条件边
    def route_after_review(state: ResearchReportState) -> str:
        review_score = state.get("review_score", 0.0)

        if review_score >= 8.0:
            return "finalize"
        elif state.get("revision_count", 0) >= 3:
            return "finalize"  # 最多修订3次
        else:
            return "revise"

    # 添加边
    graph.add_edge("plan", "collect_data")
    graph.add_edge("collect_data", "analyze")
    graph.add_edge("analyze", "write_draft")
    graph.add_edge("write_draft", "peer_review")
    graph.add_conditional_edges(
        "peer_review",
        route_after_review,
        {
            "revise": "revise",
            "finalize": "finalize"
        }
    )
    graph.add_edge("revise", "write_draft")  # 修订后重新写作
    graph.add_edge("finalize", END)

    return graph.compile()

class ResearchReportState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 研究相关
    research_topic: str
    research_plan: Optional[Dict[str, Any]]
    collected_data: List[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]

    # 写作相关
    draft_content: Optional[str]
    review_score: Optional[float]
    revision_count: int

    # 质量控制
    plagiarism_check_passed: bool
    fact_check_passed: bool
    quality_metrics: Dict[str, float]

def plan_research_node(state: ResearchReportState) -> ResearchReportState:
    """研究规划节点"""
    topic = state["research_topic"]

    # 创建研究计划
    research_plan = {
        "objectives": [
            f"分析{topic}的现状",
            f"识别{topic}的发展趋势",
            f"评估{topic}的影响"
        ],
        "data_sources": ["学术论文", "新闻报道", "行业报告"],
        "methodology": "综合文献综述和数据分析",
        "timeline": "2周",
        "resources_needed": ["搜索工具", "分析软件"]
    }

    return {
        **state,
        "current_step": "plan",
        "research_plan": research_plan,
        "messages": state["messages"] + [
            f"研究规划完成: {topic}",
            "规划了4个主要目标"
        ]
    }

def collect_data_node(state: ResearchReportState) -> ResearchReportState:
    """数据收集节点"""
    research_plan = state["research_plan"]
    topic = state["research_topic"]

    # 模拟数据收集
    collected_data = []

    for source in research_plan["data_sources"]:
        data = {
            "source": source,
            "items_collected": f"从{source}收集了20篇相关文章",
            "key_insights": [
                f"关键洞察1来自{source}",
                f"关键洞察2来自{source}"
            ],
            "quality_score": 0.85,
            "relevance_score": 0.9
        }
        collected_data.append(data)

    return {
        **state,
        "current_step": "collect_data",
        "collected_data": collected_data,
        "messages": state["messages"] + [
            "数据收集完成",
            f"从{len(collected_data)}个数据源收集信息"
        ]
    }

def analyze_data_node(state: ResearchReportState) -> ResearchReportState:
    """数据分析节点"""
    collected_data = state["collected_data"]

    # 分析收集的数据
    analysis_results = {
        "summary": "基于收集的数据进行分析",
        "key_findings": [],
        "trends": [],
        "recommendations": [],
        "confidence_level": 0.88
    }

    # 提取关键发现
    for data in collected_data:
        analysis_results["key_findings"].extend(data["key_insights"])

    # 识别趋势
    analysis_results["trends"] = [
        "技术快速发展",
        "市场需求增长",
        "竞争加剧"
    ]

    # 生成建议
    analysis_results["recommendations"] = [
        "继续投入研发",
        "关注市场变化",
        "加强合作"
    ]

    return {
        **state,
        "current_step": "analyze",
        "analysis_results": analysis_results,
        "messages": state["messages"] + [
            "数据分析完成",
            f"识别出{len(analysis_results['key_findings'])}个关键发现"
        ]
    }

def write_draft_node(state: ResearchReportState) -> ResearchReportState:
    """写作草稿节点"""
    research_plan = state["research_plan"]
    collected_data = state["collected_data"]
    analysis_results = state["analysis_results"]

    # 生成报告草稿
    draft_content = f"""
# {state['research_topic']}研究报告

## 执行摘要
本报告基于对{state['research_topic']}的深入研究，分析了当前状况和发展趋势。

## 研究方法
- 数据来源: {', '.join(research_plan['data_sources'])}
- 研究方法: {research_plan['methodology']}
- 数据量: {len(collected_data)}个数据源

## 主要发现
{chr(10).join(f"- {finding}" for finding in analysis_results['key_findings'])}

## 趋势分析
{chr(10).join(f"- {trend}" for trend in analysis_results['trends'])}

## 建议
{chr(10).join(f"- {rec}" for rec in analysis_results['recommendations'])}

## 结论
本研究提供了对{state['research_topic']}的深入洞察，建议相关方面根据发现制定策略。
"""

    return {
        **state,
        "current_step": "write_draft",
        "draft_content": draft_content,
        "messages": state["messages"] + [
            "报告草稿完成",
            "包含执行摘要、主要发现和建议"
        ]
    }

def peer_review_node(state: ResearchReportState) -> ResearchReportState:
    """同行评审节点"""
    draft_content = state["draft_content"]

    # 模拟同行评审
    import random

    # 评分标准：内容质量、逻辑性、创新性、可读性
    quality_metrics = {
        "content_quality": random.uniform(7.0, 9.5),
        "logic": random.uniform(7.5, 9.0),
        "originality": random.uniform(6.5, 8.5),
        "readability": random.uniform(8.0, 9.5)
    }

    review_score = sum(quality_metrics.values()) / len(quality_metrics)

    # 模拟反馈
    feedback = {
        "overall_score": review_score,
        "strengths": [
            "内容丰富，涵盖了主要方面",
            "结构清晰，逻辑性强",
            "建议具体可操作"
        ],
        "weaknesses": [
            "可以增加更多具体数据支持",
            "某些结论需要更多论证",
            "可以补充国际视野"
        ],
        "recommendations": [
            "添加更多定量分析",
            "增强论证逻辑",
            "完善结论部分"
        ]
    }

    return {
        **state,
        "current_step": "peer_review",
        "review_score": review_score,
        "quality_metrics": quality_metrics,
        "peer_feedback": feedback,
        "revision_count": state.get("revision_count", 0) + 1,
        "messages": state["messages"] + [
            f"同行评审完成，评分: {review_score:.1f}/10",
            f"收到{len(feedback['recommendations'])}条改进建议"
        ]
    }

# 编译并使用工作流
research_workflow = create_research_report_workflow()

# 示例执行
initial_state = {
    "current_step": "start",
    "messages": [],
    "research_topic": "人工智能在医疗领域的应用",
    "revision_count": 0
}

result = research_workflow.invoke(initial_state)
print("最终报告评分:", result.get("review_score", "N/A"))
```

### 2. 多Agent协作系统

```python
def create_multi_agent_workflow():
    """创建多Agent协作工作流"""
    graph = StateGraph(MultiAgentState)

    # 添加Agent节点
    graph.add_node("coordinator", coordinator_agent_node)
    graph.add_node("researcher", researcher_agent_node)
    graph.add_node("writer", writer_agent_node)
    graph.add_node("reviewer", reviewer_agent_node)
    graph.add_node("editor", editor_agent_node)

    # 设置入口点
    graph.set_entry_point("coordinator")

    # Agent间的协作流程
    graph.add_edge("coordinator", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")

    # 条件边：审稿决定
    def route_after_review(state: MultiAgentState) -> str:
        review_decision = state.get("review_decision", "revise")

        if review_decision == "approve":
            return "editor"
        elif review_decision == "revise":
            return "writer"
        else:
            return "coordinator"

    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "editor": "editor",
            "revise": "writer",
            "escalate": "coordinator"
        }
    )

    graph.add_edge("editor", END)

    return graph.compile()

class MultiAgentState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 任务相关
    task_description: str
    task_type: str
    priority: str

    # Agent结果
    research_results: Optional[Dict[str, Any]]
    draft_content: Optional[str]
    review_feedback: Optional[Dict[str, Any]]
    final_edit: Optional[str]

    # 协作控制
    assigned_agent: Optional[str]
    agent_status: Dict[str, str]
    coordination_decisions: List[str]

def coordinator_agent_node(state: MultiAgentState) -> MultiAgentState:
    """协调员Agent节点"""
    task_description = state["task_description"]

    # 任务分析
    task_analysis = analyze_task(task_description)

    # 分配给合适的Agent
    primary_agent = determine_primary_agent(task_analysis)

    coordination_decision = f"分配任务给{primary_agent}"

    return {
        **state,
        "current_step": "coordinator",
        "task_analysis": task_analysis,
        "assigned_agent": primary_agent,
        "coordination_decisions": state.get("coordination_decisions", []) + [coordination_decision],
        "agent_status": {
            **state.get("agent_status", {}),
            "coordinator": "completed"
        },
        "messages": state["messages"] + [
            f"协调员分析任务: {task_description}",
            f"分配给{primary_agent}"
        ]
    }

def researcher_agent_node(state: MultiAgentState) -> MultiAgentState:
    """研究员Agent节点"""
    task_analysis = state.get("task_analysis", {})
    task_description = state["task_description"]

    # 模拟研究过程
    research_results = {
        "sources": [
            {"title": "相关论文1", "relevance": 0.9},
            {"title": "相关论文2", "relevance": 0.8},
            {"title": "行业报告", "relevance": 0.85}
        ],
        "key_findings": [
            "发现A支持主要论点",
            "发现B提供补充信息",
            "发现C展示应用案例"
        ],
        "data_quality": 0.88,
        "completeness": 0.92
    }

    return {
        **state,
        "current_step": "researcher",
        "research_results": research_results,
        "agent_status": {
            **state.get("agent_status", {}),
            "researcher": "completed"
        },
        "messages": state["messages"] + [
            "研究员完成信息收集",
            f"收集到{len(research_results['sources'])}个高质量资源"
        ]
    }

def writer_agent_node(state: MultiAgentState) -> MultiAgentState:
    """写作Agent节点"""
    research_results = state.get("research_results", {})
    task_description = state["task_description"]

    # 基于研究结果写作
    draft_content = f"""
任务：{task_description}

研究总结：
基于收集的资料，我们发现：

主要发现：
{chr(10).join(f"- {finding}" for finding in research_results.get('key_findings', []))}

结论：
本研究为相关决策提供了有价值的参考。
"""

    return {
        **state,
        "current_step": "writer",
        "draft_content": draft_content,
        "agent_status": {
            **state.get("agent_status", {}),
            "writer": "completed"
        },
        "messages": state["messages"] + [
            "写作Agent完成初稿",
            "基于研究结果生成了结构化内容"
        ]
    }

def reviewer_agent_node(state: MultiAgentState) -> MultiAgentState:
    """审稿Agent节点"""
    draft_content = state.get("draft_content", "")

    # 模拟审稿过程
    import random

    review_criteria = {
        "accuracy": random.uniform(7.0, 9.5),
        "completeness": random.uniform(7.5, 9.0),
        "clarity": random.uniform(8.0, 9.5),
        "coherence": random.uniform(7.8, 9.2)
    }

    overall_score = sum(review_criteria.values()) / len(review_criteria)

    # 决定
    if overall_score >= 8.5:
        review_decision = "approve"
    elif overall_score >= 7.0:
        review_decision = "revise"
    else:
        review_decision = "reject"

    review_feedback = {
        "scores": review_criteria,
        "overall_score": overall_score,
        "decision": review_decision,
        "comments": {
            "strengths": ["内容准确", "逻辑清晰"],
            "improvements": ["可以增加更多细节", "某些表述可以优化"]
        }
    }

    return {
        **state,
        "current_step": "reviewer",
        "review_feedback": review_feedback,
        "review_decision": review_decision,
        "agent_status": {
            **state.get("agent_status", {}),
            "reviewer": "completed"
        },
        "messages": state["messages"] + [
            f"审稿完成，评分: {overall_score:.1f}/10",
            f"决定: {review_decision}"
        ]
    }

def editor_agent_node(state: MultiAgentState) -> MultiAgentState:
    """编辑Agent节点"""
    draft_content = state.get("draft_content", "")
    review_feedback = state.get("review_feedback", {})

    # 基于审稿意见进行最终编辑
    final_edit = f"""
{state['task_description']}

--- 编辑版本 ---
{draft_content}

编辑说明：
- 根据审稿意见进行了优化
- 改进了表述的准确性
- 增强了逻辑连贯性

质量检查：通过 ✅
"""

    return {
        **state,
        "current_step": "editor",
        "final_edit": final_edit,
        "agent_status": {
            **state.get("agent_status", {}),
            "editor": "completed"
        },
        "messages": state["messages"] + [
            "编辑完成",
            "最终版本已准备就绪"
        ]
    }

# 使用示例
multi_agent_workflow = create_multi_agent_workflow()

task_state = {
    "current_step": "start",
    "messages": [],
    "task_description": "编写一份关于区块链技术发展趋势的分析报告",
    "task_type": "research_report",
    "priority": "high",
    "agent_status": {}
}

result = multi_agent_workflow.invoke(task_state)
print("最终结果:")
print(result.get("final_edit", "N/A"))
```

### 3. 客户服务聊天机器人

```python
def create_customer_service_workflow():
    """创建客户服务工作流"""
    graph = StateGraph(CustomerServiceState)

    # 添加节点
    graph.add_node("intention_detection", detect_intention_node)
    graph.add_node("knowledge_search", search_knowledge_node)
    graph.add_node("workflow_routing", route_workflow_node)
    graph.add_node("technical_support", technical_support_node)
    graph.add_node("billing_inquiry", billing_inquiry_node)
    graph.add_node("product_info", product_info_node)
    graph.add_node("human_handoff", human_handoff_node)
    graph.add_node("resolution_check", check_resolution_node)
    graph.add_node("follow_up", follow_up_node)

    # 设置入口点
    graph.set_entry_point("intention_detection")

    # 意图路由
    def route_by_intention(state: CustomerServiceState) -> str:
        intention = state.get("detected_intention", "general")

        intention_mapping = {
            "technical_issue": "technical_support",
            "billing": "billing_inquiry",
            "product_info": "product_info",
            "complaint": "human_handoff",
            "general": "knowledge_search"
        }

        return intention_mapping.get(intention, "knowledge_search")

    graph.add_conditional_edges(
        "intention_detection",
        route_by_intention,
        {
            "technical_support": "technical_support",
            "billing_inquiry": "billing_inquiry",
            "product_info": "product_info",
            "human_handoff": "human_handoff",
            "knowledge_search": "knowledge_search"
        }
    )

    # 检查解决状态
    def check_resolution(state: CustomerServiceState) -> str:
        resolved = state.get("issue_resolved", False)
        satisfaction = state.get("satisfaction_score", 0)

        if resolved and satisfaction >= 4:
            return "follow_up"
        elif resolved:
            return "end"
        else:
            return "human_handoff"

    # 从各种处理节点到解决检查
    for node in ["technical_support", "billing_inquiry", "product_info", "knowledge_search"]:
        graph.add_edge(node, "resolution_check")

    graph.add_conditional_edges(
        "resolution_check",
        check_resolution,
        {
            "follow_up": "follow_up",
            "human_handoff": "human_handoff",
            "end": END
        }
    )

    graph.add_edge("human_handoff", "end")
    graph.add_edge("follow_up", END)

    return graph.compile()

class CustomerServiceState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 客户信息
    customer_id: Optional[str]
    customer_tier: str

    # 问题相关
    original_query: str
    detected_intention: Optional[str]
    confidence: float

    # 处理结果
    search_results: Optional[List[Dict[str, Any]]]
    resolution: Optional[str]
    issue_resolved: bool
    satisfaction_score: Optional[float]

    # 升级控制
    escalation_count: int
    requires_human: bool

    # 上下文
    conversation_context: List[str]
    previous_resolutions: List[str]

def detect_intention_node(state: CustomerServiceState) -> CustomerServiceState:
    """意图检测节点"""
    query = state["original_query"]

    # 意图检测逻辑
    intention_patterns = {
        "technical_issue": ["错误", "无法", "故障", "问题", "bug"],
        "billing": ["账单", "收费", "价格", "退款", "支付"],
        "product_info": ["功能", "特性", "如何使用", "规格"],
        "complaint": ["投诉", "不满", "糟糕", "失望"],
        "general": ["你好", "帮助", "请问"]
    }

    detected_intention = "general"
    max_matches = 0

    for intention, keywords in intention_patterns.items():
        matches = sum(1 for keyword in keywords if keyword in query)
        if matches > max_matches:
            max_matches = matches
            detected_intention = intention

    # 计算置信度
    confidence = min(max_matches * 0.3 + 0.5, 1.0)

    return {
        **state,
        "current_step": "intention_detection",
        "detected_intention": detected_intention,
        "confidence": confidence,
        "messages": state["messages"] + [
            f"检测到意图: {detected_intention} (置信度: {confidence:.2f})"
        ]
    }

def search_knowledge_node(state: CustomerServiceState) -> CustomerServiceState:
    """知识库搜索节点"""
    query = state["original_query"]
    intention = state["detected_intention"]

    # 模拟知识库搜索
    knowledge_base = {
        "technical_issue": [
            {"question": "应用无法启动", "answer": "请尝试重启应用或清除缓存"},
            {"question": "登录失败", "answer": "请检查用户名和密码是否正确"}
        ],
        "billing": [
            {"question": "如何取消订阅", "answer": "可以在账户设置中取消订阅"},
            {"question": "账单查询", "answer": "账单信息可以在账户页面查看"}
        ],
        "product_info": [
            {"question": "功能介绍", "answer": "产品具有以下核心功能..."},
            {"question": "使用教程", "answer": "详细使用教程请查看帮助文档"}
        ]
    }

    relevant_results = knowledge_base.get(intention, [])

    return {
        **state,
        "current_step": "knowledge_search",
        "search_results": relevant_results,
        "messages": state["messages"] + [
            f"搜索到{len(relevant_results)}个相关结果"
        ]
    }

def check_resolution_node(state: CustomerServiceState) -> CustomerServiceState:
    """解决状态检查节点"""
    satisfaction = input(f"客户满意度评分 (1-5): ")

    try:
        satisfaction_score = float(satisfaction)
        issue_resolved = satisfaction_score >= 4
    except ValueError:
        satisfaction_score = 3.0
        issue_resolved = False

    return {
        **state,
        "current_step": "resolution_check",
        "satisfaction_score": satisfaction_score,
        "issue_resolved": issue_resolved,
        "messages": state["messages"] + [
            f"满意度评分: {satisfaction_score}",
            f"问题解决状态: {'是' if issue_resolved else '否'}"
        ]
    }

def follow_up_node(state: CustomerServiceState) -> CustomerServiceState:
    """跟进节点"""
    customer_id = state.get("customer_id", "未知客户")

    follow_up_message = f"""
感谢您的反馈！我们会继续改进服务质量。
如果您还有其他问题，请随时联系我们。

跟进安排：24小时内电话回访
联系人：客服代表 {state.get('assigned_agent', '客服')}
"""

    return {
        **state,
        "current_step": "follow_up",
        "follow_up_message": follow_up_message,
        "messages": state["messages"] + [
            "已安排跟进服务",
            "24小时内电话回访"
        ]
    }

# 使用示例
service_workflow = create_customer_service_workflow()

customer_state = {
    "current_step": "start",
    "messages": [],
    "customer_id": "CUST_12345",
    "customer_tier": "premium",
    "original_query": "我的应用总是崩溃，怎么解决？",
    "escalation_count": 0,
    "conversation_context": []
}

result = service_workflow.invoke(customer_state)
print("服务结果:", result.get("messages", []))
```

---

## 🚀 高级特性

### 1. 条件执行和动态路由

```python
from typing import Callable, Any

def create_advanced_routing_workflow():
    """创建高级路由工作流"""
    graph = StateGraph(AdvancedRoutingState)

    # 添加节点
    graph.add_node("analyze", analyze_request_node)
    graph.add_node("route", dynamic_router_node)
    graph.add_node("process_a", process_type_a_node)
    graph.add_node("process_b", process_type_b_node)
    graph.add_node("aggregate", aggregate_results_node)

    # 设置入口点
    graph.set_entry_point("analyze")

    # 复杂的条件路由
    def advanced_router(state: AdvancedRoutingState) -> str:
        """高级路由器"""
        request_type = state.get("request_type", "unknown")
        priority = state.get("priority", "normal")
        complexity = state.get("complexity_score", 0.5)
        available_resources = state.get("available_resources", [])

        # 复杂的路由逻辑
        if request_type == "complex_analysis" and complexity > 0.8:
            return "process_b"
        elif request_type == "simple_query" and priority == "high":
            return "process_a"
        elif len(available_resources) < 2:
            return "process_a"  # 资源不足，使用简单处理
        else:
            return "process_a"

    graph.add_conditional_edges(
        "route",
        advanced_router,
        {
            "process_a": "process_a",
            "process_b": "process_b"
        }
    )

    # 汇聚到聚合节点
    graph.add_edge("process_a", "aggregate")
    graph.add_edge("process_b", "aggregate")
    graph.add_edge("aggregate", END)

    return graph.compile()

class AdvancedRoutingState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 请求信息
    request_type: str
    priority: str
    complexity_score: float
    available_resources: List[str]

    # 处理结果
    processing_path: List[str]
    partial_results: Dict[str, Any]
    final_result: Optional[Any]

def dynamic_router_node(state: AdvancedRoutingState) -> AdvancedRoutingState:
    """动态路由器节点"""
    route_decision = f"基于{len(state.get('available_resources', []))}个可用资源进行路由"

    return {
        **state,
        "current_step": "route",
        "route_decision": route_decision,
        "processing_path": state.get("processing_path", []) + ["routed"],
        "messages": state["messages"] + [route_decision]
    }
```

### 2. 子图和工作流嵌套

```python
def create_subgraph_workflow():
    """创建包含子图的工作流"""

    # 创建子图
    subgraph = StateGraph(SubgraphState)
    subgraph.add_node("sub_task_1", sub_task_1_node)
    subgraph.add_node("sub_task_2", sub_task_2_node)
    subgraph.add_edge("sub_task_1", "sub_task_2")
    subgraph.add_edge("sub_task_2", END)
    subgraph.set_entry_point("sub_task_1")

    # 编译子图
    compiled_subgraph = subgraph.compile()

    # 创建主图
    graph = StateGraph(MainGraphState)
    graph.add_node("main_task", main_task_node)
    graph.add_node("subgraph", subgraph_node(compiled_subgraph))
    graph.add_node("post_process", post_process_node)

    graph.set_entry_point("main_task")
    graph.add_edge("main_task", "subgraph")
    graph.add_edge("subgraph", "post_process")
    graph.add_edge("post_process", END)

    return graph.compile()

def subgraph_node(subgraph):
    """创建子图节点"""
    def wrapper(state: MainGraphState) -> MainGraphState:
        # 准备子图输入
        subgraph_input = {
            "sub_tasks": state.get("sub_tasks", []),
            "sub_messages": []
        }

        # 执行子图
        subgraph_result = subgraph.invoke(subgraph_input)

        # 处理子图结果
        return {
            **state,
            "current_step": "subgraph",
            "subgraph_result": subgraph_result,
            "messages": state["messages"] + ["子图执行完成"]
        }

    return wrapper
```

### 3. 事件驱动和监听器

```python
from typing import Dict, Callable, List
import asyncio

class EventSystem:
    """事件系统"""

    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """注册事件监听器"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    async def emit(self, event: str, data: Any):
        """触发事件"""
        if event in self.listeners:
            for callback in self.listeners[event]:
                await callback(data)

# 全局事件系统
event_system = EventSystem()

def create_event_driven_workflow():
    """创建事件驱动工作流"""
    graph = StateGraph(EventDrivenState)

    # 添加事件监听器
    @event_system.on("high_confidence")
    async def handle_high_confidence(data):
        print(f"🎉 高置信度结果: {data}")

    @event_system.on("error_occurred")
    async def handle_error(data):
        print(f"⚠️  发生错误: {data}")

    graph.add_node("process", event_driven_process_node)
    graph.add_node("validate", validation_node)
    graph.add_node("handle_error", error_handler_node)

    graph.set_entry_point("process")
    graph.add_edge("process", "validate")
    graph.add_edge("validate", END)

    return graph.compile()

async def event_driven_process_node(state: EventDrivenState) -> EventDrivenState:
    """事件驱动处理节点"""
    confidence = state.get("confidence", 0.5)

    # 模拟处理
    if confidence > 0.8:
        await event_system.emit("high_confidence", {"confidence": confidence})
    elif confidence < 0.3:
        await event_system.emit("low_confidence", {"confidence": confidence})

    return {
        **state,
        "current_step": "process",
        "messages": state["messages"] + [f"处理完成，置信度: {confidence}"]
    }

class EventDrivenState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]
    confidence: float
    event_history: List[Dict[str, Any]]
```

### 4. 缓存和性能优化

```python
import hashlib
import json
from functools import wraps

class ResultCache:
    """结果缓存"""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.max_size = max_size

    def _get_cache_key(self, state: Dict[str, Any], node_name: str) -> str:
        """生成缓存键"""
        # 移除可变字段
        cacheable_state = {
            k: v for k, v in state.items()
            if k not in ["messages", "current_step", "step_count"]
        }

        key_data = {
            "node": node_name,
            "state": cacheable_state
        }

        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def get(self, state: Dict[str, Any], node_name: str) -> Any:
        """获取缓存"""
        cache_key = self._get_cache_key(state, node_name)

        if cache_key in self.cache:
            # 更新访问顺序
            if cache_key in self.access_order:
                self.access_order.remove(cache_key)
            self.access_order.append(cache_key)

            return self.cache[cache_key]

        return None

    def set(self, state: Dict[str, Any], node_name: str, result: Any):
        """设置缓存"""
        cache_key = self._get_cache_key(state, node_name)

        # 检查缓存大小
        if len(self.cache) >= self.max_size:
            # 移除最旧的条目
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[cache_key] = result
        self.access_order.append(cache_key)

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()

# 全局缓存实例
result_cache = ResultCache()

def with_caching(ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(state: Dict[str, Any], *args, **kwargs):
            node_name = func.__name__

            # 尝试从缓存获取
            cached_result = result_cache.get(state, node_name)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = func(state, *args, **kwargs)

            # 缓存结果
            result_cache.set(state, node_name, result)

            return result

        return wrapper
    return decorator

@with_caching()
def cached_research_node(state: WorkflowState) -> WorkflowState:
    """带缓存的研究节点"""
    # 耗时的研究操作
    topic = state["research_topic"]
    result = perform_expensive_research(topic)

    return {
        **state,
        "current_step": "research",
        "research_data": result,
        "messages": state["messages"] + ["研究完成（从缓存或重新计算）"]
    }
```

### 5. 监控和可观察性

```python
import time
from datetime import datetime
from typing import Dict, Any, List

class WorkflowMonitor:
    """工作流监控"""

    def __init__(self):
        self.executions: List[Dict[str, Any]] = []
        self.node_performance: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}

    def start_execution(self, workflow_id: str, initial_state: Dict[str, Any]):
        """开始执行监控"""
        self.current_execution = {
            "workflow_id": workflow_id,
            "start_time": datetime.now().isoformat(),
            "initial_state": initial_state,
            "node_executions": [],
            "errors": []
        }

    def record_node_execution(self, node_name: str, start_time: float, end_time: float, result: Any):
        """记录节点执行"""
        execution_time = end_time - start_time

        # 记录节点性能
        if node_name not in self.node_performance:
            self.node_performance[node_name] = []
        self.node_performance[node_name].append(execution_time)

        # 记录当前执行
        node_execution = {
            "node_name": node_name,
            "start_time": start_time,
            "end_time": end_time,
            "execution_time": execution_time,
            "result_summary": str(result)[:100]  # 只保存结果摘要
        }

        self.current_execution["node_executions"].append(node_execution)

    def record_error(self, node_name: str, error: Exception):
        """记录错误"""
        self.error_counts[node_name] = self.error_counts.get(node_name, 0) + 1

        error_record = {
            "node_name": node_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat()
        }

        self.current_execution["errors"].append(error_record)

    def end_execution(self, final_state: Dict[str, Any]):
        """结束执行监控"""
        self.current_execution["end_time"] = datetime.now().isoformat()
        self.current_execution["final_state"] = final_state
        self.current_execution["total_execution_time"] = (
            datetime.fromisoformat(self.current_execution["end_time"]) -
            datetime.fromisoformat(self.current_execution["start_time"])
        ).total_seconds()

        self.executions.append(self.current_execution.copy())

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            "total_executions": len(self.executions),
            "average_execution_time": 0,
            "node_performance": {},
            "error_statistics": self.error_counts
        }

        if self.executions:
            # 计算平均执行时间
            total_time = sum(exec["total_execution_time"] for exec in self.executions)
            report["average_execution_time"] = total_time / len(self.executions)

        # 节点性能统计
        for node, times in self.node_performance.items():
            if times:
                report["node_performance"][node] = {
                    "average_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "execution_count": len(times)
                }

        return report

# 全局监控实例
monitor = WorkflowMonitor()

def with_monitoring(func):
    """监控装饰器"""
    def wrapper(state: Dict[str, Any], *args, **kwargs):
        node_name = func.__name__
        start_time = time.time()

        try:
            result = func(state, *args, **kwargs)
            end_time = time.time()

            # 记录成功的执行
            monitor.record_node_execution(node_name, start_time, end_time, result)

            return result

        except Exception as e:
            end_time = time.time()

            # 记录错误
            monitor.record_error(node_name, e)
            raise

        finally:
            # 确保状态更新
            pass

    return wrapper

@with_monitoring()
def monitored_research_node(state: WorkflowState) -> WorkflowState:
    """带监控的研究节点"""
    # 执行研究操作
    topic = state["research_topic"]
    result = perform_research(topic)

    return {
        **state,
        "current_step": "research",
        "research_data": result,
        "messages": state["messages"] + ["研究完成"]
    }

def create_monitored_workflow():
    """创建带监控的工作流"""
    graph = StateGraph(WorkflowState)

    # 添加节点
    graph.add_node("start", start_node)
    graph.add_node("research", monitored_research_node)
    graph.add_node("analyze", monitored_analyze_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("start")
    graph.add_edge("start", "research")
    graph.add_edge("research", "analyze")
    graph.add_edge("analyze", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()

@with_monitoring()
def monitored_analyze_node(state: WorkflowState) -> WorkflowState:
    """带监控的分析节点"""
    research_data = state.get("research_data", {})

    # 执行分析
    analysis = analyze_data(research_data)

    return {
        **state,
        "current_step": "analyze",
        "analysis": analysis,
        "messages": state["messages"] + ["分析完成"]
    }

# 使用示例
def run_monitored_workflow():
    """运行带监控的工作流"""
    workflow = create_monitored_workflow()

    # 开始监控
    monitor.start_execution("research_workflow_1", {"topic": "AI发展"})

    initial_state = {
        "current_step": "start",
        "messages": [],
        "research_topic": "AI发展",
        "step_count": 0
    }

    try:
        result = workflow.invoke(initial_state)
        monitor.end_execution(result)

        # 获取性能报告
        performance_report = monitor.get_performance_report()
        print("性能报告:", performance_report)

    except Exception as e:
        monitor.end_execution({"error": str(e)})
        print(f"工作流执行失败: {e}")
```

---

## ✅ 最佳实践

### 1. 状态设计最佳实践

#### A. 状态结构设计

```python
# ✅ 好的状态设计
class WellDesignedState(TypedDict):
    # 必需的元数据
    current_step: str
    session_id: str
    step_count: int

    # 业务数据（分层组织）
    user_input: str
    processing_results: Dict[str, Any]

    # 控制流状态
    confidence: float
    requires_review: bool
    retry_count: int

    # 上下文信息
    metadata: Dict[str, Any]
    error_log: List[str]

# ❌ 避免的状态设计
class PoorlyDesignedState(TypedDict):
    # 混合了太多不相关的字段
    random_data: Any
    temp_variables: List[Any]
    debug_info: Dict[str, Any]
    # 缺乏明确的语义
```

#### B. 状态更新策略

```python
def safe_state_update(state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """安全的状态更新"""
    # 验证更新
    validated_updates = validate_state_updates(updates)

    # 原子更新
    new_state = {**state, **validated_updates}

    # 添加审计信息
    new_state["last_updated"] = datetime.now().isoformat()
    new_state["step_count"] = state.get("step_count", 0) + 1

    return new_state

def validate_state_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
    """验证状态更新"""
    validated = {}

    for key, value in updates.items():
        # 基本验证
        if value is None:
            continue

        # 类型检查
        if key == "confidence" and not isinstance(value, (int, float)):
            raise ValueError("confidence必须是数字")
        elif key == "messages" and not isinstance(value, list):
            raise ValueError("messages必须是列表")
        elif key == "metadata" and not isinstance(value, dict):
            raise ValueError("metadata必须是字典")

        validated[key] = value

    return validated
```

### 2. 节点设计最佳实践

#### A. 单一职责原则

```python
# ✅ 好的节点设计：单一职责
def validate_input_node(state: WorkflowState) -> WorkflowState:
    """仅负责输入验证"""
    user_input = state["user_input"]

    if not user_input or len(user_input.strip()) < 3:
        return {
            **state,
            "current_step": "validation",
            "is_valid": False,
            "validation_errors": ["输入太短"],
            "messages": state["messages"] + ["输入验证失败"]
        }

    return {
        **state,
        "current_step": "validation",
        "is_valid": True,
        "messages": state["messages"] + ["输入验证通过"]
    }

# ❌ 避免：职责过多的节点
def over_loaded_node(state: WorkflowState) -> WorkflowState:
    """这个节点做了太多事情"""
    # 输入验证
    # 数据处理
    # 业务逻辑
    # 结果生成
    # 状态更新
    # 错误处理
    # 日志记录
    # 通知发送
    # ...
    pass
```

#### B. 错误处理

```python
def resilient_node(state: WorkflowState) -> WorkflowState:
    """具有错误处理能力的节点"""
    try:
        # 执行主要逻辑
        result = perform_operation(state["data"])

        return {
            **state,
            "current_step": "processing",
            "result": result,
            "messages": state["messages"] + ["处理成功"]
        }

    except ValidationError as e:
        # 输入验证错误
        return {
            **state,
            "current_step": "error",
            "error_type": "validation",
            "error_message": str(e),
            "retry_count": state.get("retry_count", 0) + 1,
            "messages": state["messages"] + [f"验证错误: {e}"]
        }

    except TimeoutError:
        # 超时错误
        return {
            **state,
            "current_step": "timeout",
            "retry_count": state.get("retry_count", 0) + 1,
            "messages": state["messages"] + ["处理超时"]
        }

    except Exception as e:
        # 未知错误
        return {
            **state,
            "current_step": "error",
            "error_type": "unknown",
            "error_message": str(e),
            "needs_manual_review": True,
            "messages": state["messages"] + [f"处理错误: {e}"]
        }
```

### 3. 性能优化最佳实践

#### A. 避免不必要的计算

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(task_id: str, parameters: tuple) -> Dict[str, Any]:
    """带缓存的昂贵计算"""
    # 模拟耗时操作
    time.sleep(2)
    return {"result": f"计算结果 for {task_id}"}

def optimized_node(state: WorkflowState) -> WorkflowState:
    """优化的节点"""
    task_id = state["task_id"]
    parameters = tuple(sorted(state.get("parameters", {}).items()))

    # 使用缓存避免重复计算
    if task_id in state.get("cached_results", {}):
        cached_result = state["cached_results"][task_id]
    else:
        cached_result = expensive_computation(task_id, parameters)

        # 更新缓存
        cached_results = state.get("cached_results", {})
        cached_results[task_id] = cached_result

        return {
            **state,
            "current_step": "processing",
            "result": cached_result,
            "cached_results": cached_results,
            "messages": state["messages"] + ["使用缓存结果" if task_id in state.get("cached_results", {}) else "计算新结果"]
        }
```

#### B. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_processing_node(state: WorkflowState) -> WorkflowState:
    """并行处理节点"""
    tasks = state.get("parallel_tasks", [])

    if not tasks:
        return {
            **state,
            "current_step": "parallel_processing",
            "results": {},
            "messages": state["messages"] + ["没有并行任务"]
        }

    results = {}

    with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(process_individual_task, task): task
            for task in tasks
        }

        # 收集结果
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                results[task["id"]] = result
            except Exception as e:
                results[task["id"]] = {"error": str(e)}

    return {
        **state,
        "current_step": "parallel_processing",
        "results": results,
        "messages": state["messages"] + [
            f"并行处理完成，处理了{len(tasks)}个任务"
        ]
    }
```

### 4. 可测试性最佳实践

#### A. 单元测试

```python
import pytest
from unittest.mock import Mock, patch

def test_research_node():
    """测试研究节点"""
    # 准备测试状态
    test_state = {
        "current_step": "start",
        "messages": [],
        "research_topic": "人工智能",
        "step_count": 0
    }

    # 模拟外部依赖
    with patch('your_module.perform_research') as mock_research:
        mock_research.return_value = {
            "findings": ["发现1", "发现2"],
            "confidence": 0.9
        }

        # 执行节点
        result = research_node(test_state)

        # 验证结果
        assert result["current_step"] == "research"
        assert "research_data" in result
        assert len(result["research_data"]["findings"]) == 2
        assert mock_research.called
        assert mock_research.call_args[0][0] == "人工智能"

def test_state_validation():
    """测试状态验证"""
    valid_updates = {
        "confidence": 0.8,
        "messages": ["测试消息"],
        "metadata": {"key": "value"}
    }

    invalid_updates = {
        "confidence": "invalid",  # 类型错误
        "messages": "not_a_list"  # 类型错误
    }

    # 验证有效更新
    validated = validate_state_updates(valid_updates)
    assert validated == valid_updates

    # 验证无效更新（应该抛出异常）
    with pytest.raises(ValueError):
        validate_state_updates(invalid_updates)
```

#### B. 集成测试

```python
def test_workflow_integration():
    """测试工作流集成"""
    workflow = create_research_workflow()

    initial_state = {
        "current_step": "start",
        "messages": [],
        "research_topic": "机器学习",
        "step_count": 0
    }

    # 执行工作流
    result = workflow.invoke(initial_state)

    # 验证完整流程
    assert result["current_step"] == "end"
    assert "research_data" in result
    assert "analysis" in result
    assert len(result["messages"]) > 0

    # 验证消息顺序
    expected_messages = ["工作流开始", "研究完成", "分析完成"]
    for expected_msg in expected_messages:
        assert any(expected_msg in msg for msg in result["messages"])

def test_error_handling():
    """测试错误处理"""
    workflow = create_robust_workflow()

    # 测试错误状态
    error_state = {
        "current_step": "start",
        "messages": [],
        "error": "模拟错误",
        "retry_count": 0
    }

    result = workflow.invoke(error_state)

    # 验证错误处理
    assert result["current_step"] == "error_handled"
    assert "error_logged" in result
```

### 5. 文档和注释最佳实践

```python
def complex_business_logic_node(state: ComplexWorkflowState) -> ComplexWorkflowState:
    """
    执行复杂的业务逻辑处理

    该节点负责：
    1. 验证输入数据的完整性和正确性
    2. 根据业务规则进行数据转换
    3. 调用外部API获取补充信息
    4. 生成业务决策建议

    Args:
        state (ComplexWorkflowState): 当前工作流状态，必须包含：
            - user_input: 用户输入数据
            - business_context: 业务上下文信息
            - validation_rules: 验证规则配置

    Returns:
        ComplexWorkflowState: 更新后的状态，包含：
            - processing_result: 处理结果
            - business_decision: 业务决策
            - confidence_score: 置信度评分
            - validation_report: 验证报告

    Raises:
        ValidationError: 当输入数据验证失败时
        BusinessRuleError: 当业务规则检查失败时
        ExternalAPIError: 当外部API调用失败时

    Example:
        >>> state = {"user_input": "purchase_request", "business_context": {...}}
        >>> result = complex_business_logic_node(state)
        >>> print(result["business_decision"])
        "approved_with_conditions"
    """
    # 实现逻辑...
    pass

# 状态类文档
class ComplexWorkflowState(TypedDict):
    """
    复杂工作流状态定义

    Attributes:
        current_step (str): 当前执行步骤
        user_input (Dict[str, Any]): 用户输入数据
        business_context (Dict[str, Any]): 业务上下文信息
        validation_rules (Dict[str, Any]): 验证规则配置
        processing_result (Optional[Dict[str, Any]]): 处理结果
        business_decision (Optional[str]): 业务决策
        confidence_score (Optional[float]): 置信度评分 (0.0-1.0)
        validation_report (Optional[Dict[str, Any]]): 验证报告
        error_log (List[str]): 错误日志
        retry_count (int): 重试次数
    """

    current_step: str
    user_input: Dict[str, Any]
    business_context: Dict[str, Any]
    validation_rules: Dict[str, Any]

    # 可选字段
    processing_result: Optional[Dict[str, Any]]
    business_decision: Optional[str]
    confidence_score: Optional[float]
    validation_report: Optional[Dict[str, Any]]
    error_log: List[str]
    retry_count: int
```

---

## ❓ 常见问题

### Q1: 如何调试LangGraph工作流？

```python
import logging
from typing import Any, Dict

# 设置调试日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_node(state: WorkflowState) -> WorkflowState:
    """带调试信息的节点"""
    logger.debug(f"进入节点，当前状态: {state}")

    try:
        result = process_data(state["data"])
        logger.info(f"节点处理成功，结果: {result}")

        return {
            **state,
            "current_step": "processed",
            "processed_data": result,
            "messages": state["messages"] + ["处理成功"]
        }

    except Exception as e:
        logger.error(f"节点处理失败: {e}")
        logger.debug(f"失败时的状态: {state}")

        return {
            **state,
            "current_step": "error",
            "error": str(e),
            "messages": state["messages"] + [f"错误: {e}"]
        }

# 状态追踪装饰器
def trace_state_changes(func):
    """追踪状态变化的装饰器"""
    def wrapper(state: Dict[str, Any], *args, **kwargs):
        initial_state = state.copy()
        logger.debug(f"执行 {func.__name__} 前状态: {initial_state}")

        result = func(state, *args, **kwargs)

        # 追踪变化
        changes = {}
        for key in set(initial_state.keys()) | set(result.keys()):
            old_val = initial_state.get(key)
            new_val = result.get(key)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}

        if changes:
            logger.debug(f"状态变化: {changes}")

        logger.debug(f"执行 {func.__name__} 后状态: {result}")

        return result

    return wrapper

@trace_state_changes
def traced_node(state: WorkflowState) -> WorkflowState:
    """带状态追踪的节点"""
    return process_with_tracing(state)

# 断点调试
def debug_workflow_execution(workflow, initial_state: Dict[str, Any]):
    """调试工作流执行"""
    print(f"开始调试工作流...")
    print(f"初始状态: {initial_state}")

    # 流式执行以观察每一步
    for step in workflow.stream(initial_state):
        node_name = list(step.keys())[0]
        node_state = step[node_name]

        print(f"\n=== {node_name} ===")
        print(f"状态: {node_state}")

        # 允许用户在每个步骤设置断点
        user_input = input("继续? (y/n/q): ")
        if user_input.lower() == 'q':
            print("调试结束")
            break
        elif user_input.lower() == 'n':
            print("跳过到下一步")
            continue
```

### Q2: 如何处理长时间运行的任务？

```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def async_research_node(state: WorkflowState) -> WorkflowState:
    """异步研究节点"""
    topics = state.get("research_topics", [])

    if not topics:
        return {
            **state,
            "current_step": "async_research",
            "messages": state["messages"] + ["没有研究主题"]
        }

    # 异步执行多个研究任务
    async with aiohttp.ClientSession() as session:
        tasks = [
            research_topic_async(topic, session)
            for topic in topics
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    research_results = {}
    for topic, result in zip(topics, results):
        if isinstance(result, Exception):
            research_results[topic] = {"error": str(result)}
        else:
            research_results[topic] = result

    return {
        **state,
        "current_step": "async_research",
        "research_results": research_results,
        "messages": state["messages"] + [
            f"异步研究完成，处理了{len(topics)}个主题"
        ]
    }

async def research_topic_async(topic: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
    """异步研究单个主题"""
    try:
        # 模拟API调用
        async with session.get(f"https://api.example.com/research/{topic}") as response:
            data = await response.json()
            return data
    except Exception as e:
        raise Exception(f"研究主题 '{topic}' 失败: {e}")

# 长时间运行任务的检查点机制
def create_checkpoint_workflow():
    """创建带检查点的工作流"""
    graph = StateGraph(CheckpointState)

    graph.add_node("long_task", long_running_task_node)
    graph.add_node("checkpoint", checkpoint_node)
    graph.add_node("resume", resume_task_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("long_task")
    graph.add_edge("long_task", "checkpoint")
    graph.add_edge("checkpoint", "resume")
    graph.add_edge("resume", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()

class CheckpointState(TypedDict):
    current_step: str
    task_id: str
    progress: float
    partial_results: Dict[str, Any]
    checkpoint_data: Dict[str, Any]
    is_resuming: bool

def long_running_task_node(state: CheckpointState) -> CheckpointState:
    """长时间运行任务节点"""
    task_id = state["task_id"]
    total_steps = state.get("total_steps", 100)

    # 模拟长时间任务，每10步保存一次检查点
    for step in range(1, total_steps + 1):
        # 执行工作单元
        process_work_unit(task_id, step)

        # 每10步保存检查点
        if step % 10 == 0:
            progress = step / total_steps

            checkpoint_data = {
                "task_id": task_id,
                "current_step": step,
                "progress": progress,
                "partial_results": get_partial_results(task_id, step),
                "timestamp": datetime.now().isoformat()
            }

            # 保存检查点
            save_checkpoint(task_id, checkpoint_data)

            # 更新状态
            state = {
                **state,
                "current_step": "checkpoint",
                "progress": progress,
                "checkpoint_data": checkpoint_data,
                "messages": state["messages"] + [
                    f"检查点已保存，进度: {progress:.1%}"
                ]
            }

            return state  # 暂停执行

    # 任务完成
    return {
        **state,
        "current_step": "long_task",
        "progress": 1.0,
        "final_results": get_final_results(task_id),
        "messages": state["messages"] + ["长时间任务完成"]
    }

def resume_task_node(state: CheckpointState) -> CheckpointState:
    """恢复任务节点"""
    checkpoint_data = state["checkpoint_data"]
    task_id = checkpoint_data["task_id"]

    # 从检查点恢复
    start_step = checkpoint_data["current_step"]
    remaining_steps = state.get("total_steps", 100) - start_step

    # 继续执行剩余工作
    for step in range(start_step + 1, start_step + remaining_steps + 1):
        process_work_unit(task_id, step)

        # 每10步保存检查点
        if step % 10 == 0:
            progress = step / state.get("total_steps", 100)

            return {
                **state,
                "current_step": "checkpoint",
                "progress": progress,
                "messages": state["messages"] + [
                    f"从检查点恢复，进度: {progress:.1%}"
                ]
            }

    # 任务完成
    return {
        **state,
        "current_step": "resume",
        "progress": 1.0,
        "final_results": get_final_results(task_id),
        "messages": state["messages"] + ["任务恢复并完成"]
    }
```

### Q3: 如何优化内存使用？

```python
import gc
from typing import Iterator

class MemoryEfficientWorkflow:
    """内存高效的工作流"""

    def __init__(self):
        self.state_history = []
        self.max_history = 10  # 只保留最近10个状态

    def stream_with_cleanup(self, initial_state: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """流式执行并清理内存"""
        current_state = initial_state.copy()

        for step_name, step_state in self._execute_steps(current_state):
            # 更新状态历史
            self.state_history.append({
                "step": step_name,
                "state": step_state.copy(),
                "timestamp": datetime.now().isoformat()
            })

            # 限制历史记录数量
            if len(self.state_history) > self.max_history:
                self.state_history.pop(0)

            # 清理大型对象
            self._cleanup_large_objects(step_state)

            yield {step_name: step_state}

    def _cleanup_large_objects(self, state: Dict[str, Any]):
        """清理大型对象"""
        # 将大型结果转换为引用
        for key, value in state.items():
            if isinstance(value, list) and len(value) > 1000:
                # 大列表转换为分块
                state[key] = {
                    "type": "chunked_list",
                    "chunk_size": 100,
                    "total_count": len(value),
                    "chunks": [value[i:i+100] for i in range(0, len(value), 100)]
                }
            elif isinstance(value, dict) and len(str(value)) > 10000:
                # 大字典压缩
                state[key] = {
                    "type": "compressed_dict",
                    "compressed": True,
                    "keys": list(value.keys())[:10],  # 只保留前10个键
                    "total_keys": len(value)
                }

    def get_state_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """获取状态摘要"""
        summary = {
            "current_step": state.get("current_step", "unknown"),
            "step_count": state.get("step_count", 0),
            "message_count": len(state.get("messages", [])),
            "data_size": self._estimate_data_size(state)
        }

        # 添加关键指标
        if "confidence" in state:
            summary["confidence"] = state["confidence"]
        if "error_count" in state:
            summary["error_count"] = state["error_count"]

        return summary

    def _estimate_data_size(self, state: Dict[str, Any]) -> str:
        """估算数据大小"""
        import sys

        size_bytes = sys.getsizeof(str(state))

        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

# 使用内存监控
def memory_monitored_node(state: WorkflowState) -> WorkflowState:
    """带内存监控的节点"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024  # MB

    # 执行主要逻辑
    result = perform_memory_intensive_operation(state)

    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_delta = memory_after - memory_before

    return {
        **state,
        "current_step": "processed",
        "result": result,
        "memory_usage": {
            "before_mb": memory_before,
            "after_mb": memory_after,
            "delta_mb": memory_delta
        },
        "messages": state["messages"] + [
            f"内存使用: {memory_delta:.1f}MB"
        ]
    }
```

### Q4: 如何实现自定义节点类型？

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

class BaseCustomNode(ABC, Generic[T]):
    """自定义节点基类"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state_schema = config.get("state_schema", {})

    @abstractmethod
    def process(self, state: T) -> T:
        """处理状态"""
        pass

    @abstractmethod
    def validate_state(self, state: T) -> bool:
        """验证状态"""
        pass

    def pre_process(self, state: T) -> T:
        """预处理钩子"""
        return state

    def post_process(self, state: T) -> T:
        """后处理钩子"""
        return state

    def handle_error(self, state: T, error: Exception) -> T:
        """错误处理钩子"""
        return {
            **state,
            "current_step": f"{self.name}_error",
            "error": str(error),
            "messages": state.get("messages", []) + [f"{self.name}错误: {error}"]
        }

class DataValidationNode(BaseCustomNode[WorkflowState]):
    """数据验证节点"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("data_validation", config)
        self.validation_rules = config.get("validation_rules", {})

    def process(self, state: WorkflowState) -> WorkflowState:
        """执行数据验证"""
        try:
            # 预处理
            state = self.pre_process(state)

            # 执行验证
            validation_results = self._validate_data(state)

            # 后处理
            state = self.post_process(state)

            return {
                **state,
                "current_step": "validation",
                "validation_results": validation_results,
                "is_valid": validation_results["is_valid"],
                "messages": state["messages"] + ["数据验证完成"]
            }

        except Exception as e:
            return self.handle_error(state, e)

    def validate_state(self, state: WorkflowState) -> bool:
        """验证状态格式"""
        required_fields = ["user_input", "current_step"]
        return all(field in state for field in required_fields)

    def _validate_data(self, state: WorkflowState) -> Dict[str, Any]:
        """执行具体的数据验证"""
        user_input = state.get("user_input", "")

        results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "confidence": 0.0
        }

        # 长度检查
        if len(user_input) < 3:
            results["errors"].append("输入太短")
            results["is_valid"] = False

        # 内容检查
        if not user_input.strip():
            results["errors"].append("输入为空")
            results["is_valid"] = False

        # 计算置信度
        if results["is_valid"]:
            results["confidence"] = min(len(user_input) / 100.0, 1.0)

        return results

# 自定义节点工厂
class CustomNodeFactory:
    """自定义节点工厂"""

    _node_types = {
        "data_validation": DataValidationNode,
        # 可以添加更多节点类型
    }

    @classmethod
    def create_node(cls, node_type: str, name: str, config: Dict[str, Any]) -> BaseCustomNode:
        """创建自定义节点"""
        if node_type not in cls._node_types:
            raise ValueError(f"未知的节点类型: {node_type}")

        node_class = cls._node_types[node_type]
        return node_class(config)

    @classmethod
    def register_node_type(cls, node_type: str, node_class: type):
        """注册新的节点类型"""
        cls._node_types[node_type] = node_class

# 使用自定义节点
def create_custom_workflow():
    """创建使用自定义节点的工作流"""
    graph = StateGraph(WorkflowState)

    # 创建自定义节点
    validation_node = CustomNodeFactory.create_node(
        "data_validation",
        "input_validation",
        {"validation_rules": {"min_length": 3}}
    )

    # 将自定义节点包装为LangGraph节点
    def validation_wrapper(state: WorkflowState) -> WorkflowState:
        return validation_node.process(state)

    # 添加到图
    graph.add_node("validate", validation_wrapper)

    # 设置流程
    graph.set_entry_point("validate")
    graph.add_edge("validate", END)

    return graph.compile()
```

### Q5: 如何集成外部系统？

```python
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ExternalSystemConfig:
    """外部系统配置"""
    name: str
    base_url: str
    auth_token: str
    timeout: int = 30
    retry_count: int = 3

class ExternalSystemConnector:
    """外部系统连接器"""

    def __init__(self, config: ExternalSystemConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_api(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """调用外部API"""
        url = f"{self.config.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.config.auth_token}"}

        for attempt in range(self.config.retry_count):
            try:
                async with self.session.request(method, url, json=data, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()

            except aiohttp.ClientError as e:
                if attempt == self.config.retry_count - 1:
                    raise ExternalAPIError(f"API调用失败: {e}")
                await asyncio.sleep(2 ** attempt)  # 指数退避

    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        return await self.call_api(f"customers/{customer_id}")

    async def update_case_status(self, case_id: str, status: str) -> Dict[str, Any]:
        """更新案例状态"""
        return await self.call_api(f"cases/{case_id}/status", "PUT", {"status": status})

class ExternalAPIError(Exception):
    """外部API错误"""
    pass

def create_external_integration_workflow():
    """创建外部系统集成工作流"""
    graph = StateGraph(ExternalIntegrationState)

    # 添加节点
    graph.add_node("fetch_customer", fetch_customer_node)
    graph.add_node("process_request", process_request_node)
    graph.add_node("update_external_system", update_external_system_node)
    graph.add_node("sync_data", sync_data_node)

    graph.set_entry_point("fetch_customer")
    graph.add_edge("fetch_customer", "process_request")
    graph.add_edge("process_request", "update_external_system")
    graph.add_edge("update_external_system", "sync_data")
    graph.add_edge("sync_data", END)

    return graph.compile()

class ExternalIntegrationState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 客户信息
    customer_id: str
    customer_info: Optional[Dict[str, Any]]

    # 请求信息
    request_data: Dict[str, Any]
    processing_result: Optional[Dict[str, Any]]

    # 外部系统
    external_case_id: Optional[str]
    external_status: Optional[str]

    # 同步状态
    sync_status: str
    sync_errors: List[str]

async def fetch_customer_node(state: ExternalIntegrationState) -> ExternalIntegrationState:
    """获取客户信息节点"""
    customer_id = state["customer_id"]

    # 外部系统配置
    external_config = ExternalSystemConfig(
        name="crm_system",
        base_url="https://api.crm.example.com",
        auth_token="your_auth_token"
    )

    try:
        async with ExternalSystemConnector(external_config) as connector:
            customer_info = await connector.get_customer_info(customer_id)

        return {
            **state,
            "current_step": "fetch_customer",
            "customer_info": customer_info,
            "messages": state["messages"] + [f"获取客户信息成功: {customer_id}"]
        }

    except ExternalAPIError as e:
        return {
            **state,
            "current_step": "fetch_customer_error",
            "customer_info": None,
            "messages": state["messages"] + [f"获取客户信息失败: {e}"]
        }

async def update_external_system_node(state: ExternalIntegrationState) -> ExternalIntegrationState:
    """更新外部系统节点"""
    processing_result = state.get("processing_result", {})
    customer_id = state["customer_id"]

    # 外部系统配置
    external_config = ExternalSystemConfig(
        name="workflow_system",
        base_url="https://api.workflow.example.com",
        auth_token="your_workflow_token"
    )

    try:
        async with ExternalSystemConnector(external_config) as connector:
            # 创建案例
            case_data = {
                "customer_id": customer_id,
                "request_type": processing_result.get("type"),
                "priority": processing_result.get("priority"),
                "description": processing_result.get("description")
            }

            case_result = await connector.call_api("cases", "POST", case_data)

            # 更新案例状态
            await connector.update_case_status(case_result["id"], "processing")

        return {
            **state,
            "current_step": "update_external",
            "external_case_id": case_result["id"],
            "external_status": "processing",
            "messages": state["messages"] + [f"外部系统更新成功: {case_result['id']}"]
        }

    except ExternalAPIError as e:
        return {
            **state,
            "current_step": "update_external_error",
            "external_case_id": None,
            "sync_errors": state.get("sync_errors", []) + [str(e)],
            "messages": state["messages"] + [f"外部系统更新失败: {e}"]
        }
```

---

## 📚 扩展资源

### 官方文档和资源
- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub仓库](https://github.com/langchain-ai/langgraph)
- [LangGraph API参考](https://langchain-ai.github.io/langgraph/reference/)

### 教程和示例
- [LangGraph教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [构建多Agent应用](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [工作流状态管理](https://langchain-ai.github.io/langgraph/tutorials/state_management/)

### 社区资源
- [LangChain Discord](https://discord.gg/langchain)
- [LangSmith文档](https://smith.langchain.com/)
- [示例库](https://github.com/langchain-ai/langgraph/tree/main/examples)

### 相关技术
- [State Machines](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Workflow Engines](https://en.wikipedia.org/wiki/Workflow_engine)
- [Graph Theory](https://en.wikipedia.org/wiki/Graph_theory)

### 推荐阅读
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building Microservices" by Sam Newman
- "Domain-Driven Design" by Eric Evans

---

*本教程将持续更新，涵盖LangGraph的最新功能和最佳实践。*

**创建时间**: 2026-02-06
**最后更新**: 2026-02-06
**版本**: v0.1