# LangGraph示例代码

这个目录包含了LangGraph学习教程的配套示例代码，演示了各种工作流模式和应用场景。

## 📁 文件列表

### 1. 基础示例
- **`basic_workflow_example.py`** - 基础线性工作流示例
- **`conditional_workflow_example.py`** - 条件路由工作流示例
- **`multi_agent_workflow_example.py`** - 多Agent协作工作流示例

## 🚀 快速开始

### 环境要求
```bash
# 安装LangGraph
pip install langgraph

# 或使用conda
conda install -c conda-forge langgraph
```

### 运行示例
```bash
# 运行基础工作流示例
python basic_workflow_example.py

# 运行条件路由示例
python conditional_workflow_example.py

# 运行多Agent协作示例
python multi_agent_workflow_example.py
```

## 📖 示例说明

### 1. 基础工作流 (basic_workflow_example.py)

**功能**: 演示最简单的线性工作流
- 输入处理 → 验证 → 响应
- 状态管理和基本节点操作
- 流式执行演示

**学习重点**:
- StateGraph的基本概念
- 节点定义和连接
- 状态更新机制

**输出示例**:
```
🎯 LangGraph基础工作流示例
==================================================
📥 初始状态: {'current_step': 'init', 'messages': [], 'user_input': 'Hello LangGraph!', 'step_count': 0}

🚀 开始处理用户输入: Hello LangGraph!
📝 处理输入: 'Hello LangGraph!' -> 'HELLO LANGGRAPH!'
✅ 验证结果: 有效
💬 响应: ✅ 处理成功: HELLO LANGGRAPH!
```

### 2. 条件路由工作流 (conditional_workflow_example.py)

**功能**: 演示基于条件的动态路由
- 查询分类 (搜索/计算/分析/聊天/通用)
- 质量检查和人工干预
- 不同处理路径

**学习重点**:
- 条件边 (conditional edges)
- 动态路由逻辑
- 质量控制机制

**测试案例**:
```
🧪 测试案例 1: '搜索人工智能的最新发展'
🔍 查询分类: '搜索人工智能的最新发展' -> search (置信度: 0.90)
🔍 搜索完成，找到3个结果
🔍 质量检查: 置信度 0.90 -> 自动通过
📝 最终答案生成完成

💬 最终答案:
  🔍 搜索结果:
  • 搜索结果1: 关于'搜索人工智能的最新发展'的信息
  • 搜索结果2: '搜索人工智能的最新发展'相关资料
  • 搜索结果3: '搜索人工智能的最新发展'的最新动态
```

### 3. 多Agent协作工作流 (multi_agent_workflow_example.py)

**功能**: 演示多个Agent协作完成复杂任务
- 研究员Agent (Researcher)
- 分析师Agent (Analyst)
- 写作Agent (Writer)
- 审稿Agent (Reviewer)
- 协调员 (Coordinator)

**学习重点**:
- Agent设计和协作
- 复杂状态管理
- 质量控制流程
- 错误处理和恢复

**处理流程**:
```
🎯 [协调员] 开始协调任务: 人工智能在医疗领域的应用分析
📋 [协调员] Agent分配完成

🔍 [研究阶段] 开始执行
✅ [研究阶段] 完成

📊 [分析阶段] 开始执行
✅ [分析阶段] 完成

✍️ [写作阶段] 开始执行
✅ [写作阶段] 完成

🔍 [审稿阶段] 开始执行
✅ [审稿阶段] 完成，评分: 0.89, 需要修订: 是
🔄 [修订阶段] 第1次修订
📈 [修订阶段] 质量提升到: 0.99

🎉 [最终阶段] 工作流完成
```

## 🔧 代码结构

### 状态类定义
```python
class BasicWorkflowState(TypedDict):
    current_step: str
    messages: Annotated[list[str], operator.add]
    user_input: str
    step_count: int
```

### 节点定义模式
```python
def node_function(state: StateType) -> StateType:
    """节点函数"""
    # 处理逻辑
    result = process_data(state)

    return {
        **state,
        "current_step": "processed",
        "result": result,
        "messages": state["messages"] + ["处理完成"]
    }
```

### 工作流构建模式
```python
def create_workflow():
    """创建工作流"""
    graph = StateGraph(StateType)

    # 添加节点
    graph.add_node("node1", node1_function)
    graph.add_node("node2", node2_function)

    # 设置入口点
    graph.set_entry_point("node1")

    # 添加边
    graph.add_edge("node1", "node2")
    graph.add_edge("node2", END)

    return graph.compile()
```

## 🎯 学习建议

### 初学者
1. 从 `basic_workflow_example.py` 开始
2. 理解状态管理和节点概念
3. 练习修改现有示例

### 进阶者
1. 研究 `conditional_workflow_example.py` 的路由逻辑
2. 学习错误处理和质量控制
3. 尝试添加新的条件分支

### 高级用户
1. 深入理解 `multi_agent_workflow_example.py`
2. 学习Agent设计和协作模式
3. 扩展到实际业务场景

## 🔧 自定义和扩展

### 修改状态结构
```python
class CustomState(TypedDict):
    current_step: str
    messages: Annotated[List[str], operator.add]
    # 添加自定义字段
    custom_field: str
    business_data: Dict[str, Any]
```

### 添加新节点
```python
def custom_node(state: CustomState) -> CustomState:
    """自定义节点"""
    # 实现业务逻辑
    result = process_custom_logic(state)

    return {
        **state,
        "current_step": "custom_processed",
        "result": result,
        "messages": state["messages"] + ["自定义处理完成"]
    }
```

### 创建新工作流
```python
def create_custom_workflow():
    """创建自定义工作流"""
    graph = StateGraph(CustomState)

    # 添加节点和边
    graph.add_node("custom", custom_node)
    graph.set_entry_point("custom")
    graph.add_edge("custom", END)

    return graph.compile()
```

## 🚨 注意事项

### 性能考虑
- 避免在节点中执行耗时操作
- 使用流式执行观察中间状态
- 合理管理状态大小

### 错误处理
- 总是验证输入状态
- 提供有意义的错误消息
- 实现重试机制

### 状态管理
- 保持状态结构简洁
- 避免存储大对象
- 及时清理不需要的数据

## 📚 相关资源

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [状态图理论](https://en.wikipedia.org/wiki/Finite-state_machine)
- [工作流引擎](https://en.wikipedia.org/wiki/Workflow_engine)

## 🤝 贡献

欢迎提交改进建议和新的示例代码！

### 添加新示例
1. 创建新的Python文件
2. 遵循现有的代码结构
3. 添加详细的注释和文档
4. 测试运行并确保功能正常

### 改进现有示例
1. 优化性能和可读性
2. 添加边界情况处理
3. 完善错误处理
4. 更新文档说明

---

**最后更新**: 2026-02-06
**维护者**: Claude Code Assistant