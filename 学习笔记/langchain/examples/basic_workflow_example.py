#!/usr/bin/env python3
"""
LangGraph基础工作流示例
演示如何创建一个简单的线性工作流

运行方式:
python basic_workflow_example.py
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from datetime import datetime

class BasicWorkflowState(TypedDict):
    """基础工作流状态"""
    current_step: str
    messages: Annotated[list[str], operator.add]
    user_input: str
    step_count: int
    timestamp: str

def start_node(state: BasicWorkflowState) -> BasicWorkflowState:
    """开始节点"""
    print(f"🚀 开始处理用户输入: {state['user_input']}")

    return {
        **state,
        "current_step": "start",
        "messages": state["messages"] + ["工作流开始"],
        "timestamp": datetime.now().isoformat()
    }

def process_input_node(state: BasicWorkflowState) -> BasicWorkflowState:
    """处理输入节点"""
    user_input = state["user_input"]

    # 简单的文本处理
    processed_text = user_input.upper()

    print(f"📝 处理输入: '{user_input}' -> '{processed_text}'")

    return {
        **state,
        "current_step": "process_input",
        "processed_text": processed_text,
        "messages": state["messages"] + ["输入处理完成"]
    }

def validate_node(state: BasicWorkflowState) -> BasicWorkflowState:
    """验证节点"""
    processed_text = state.get("processed_text", "")

    # 简单验证
    is_valid = len(processed_text) > 0

    print(f"✅ 验证结果: {'有效' if is_valid else '无效'}")

    return {
        **state,
        "current_step": "validate",
        "is_valid": is_valid,
        "messages": state["messages"] + ["验证完成"]
    }

def respond_node(state: BasicWorkflowState) -> BasicWorkflowState:
    """响应节点"""
    is_valid = state.get("is_valid", False)
    processed_text = state.get("processed_text", "")

    if is_valid:
        response = f"✅ 处理成功: {processed_text}"
    else:
        response = "❌ 处理失败: 输入无效"

    print(f"💬 响应: {response}")

    return {
        **state,
        "current_step": "respond",
        "response": response,
        "messages": state["messages"] + [response]
    }

def create_basic_workflow():
    """创建基础工作流"""
    # 创建状态图
    graph = StateGraph(BasicWorkflowState)

    # 添加节点
    graph.add_node("start", start_node)
    graph.add_node("process_input", process_input_node)
    graph.add_node("validate", validate_node)
    graph.add_node("respond", respond_node)

    # 设置入口点
    graph.set_entry_point("start")

    # 添加边
    graph.add_edge("start", "process_input")
    graph.add_edge("process_input", "validate")
    graph.add_edge("validate", "respond")
    graph.add_edge("respond", END)

    return graph.compile()

def main():
    """主函数"""
    print("🎯 LangGraph基础工作流示例")
    print("=" * 50)

    # 创建工作流
    workflow = create_basic_workflow()

    # 准备初始状态
    initial_state = {
        "current_step": "init",
        "messages": [],
        "user_input": "Hello LangGraph!",
        "step_count": 0
    }

    print(f"📥 初始状态: {initial_state}")
    print()

    # 执行工作流
    try:
        result = workflow.invoke(initial_state)

        print()
        print("=" * 50)
        print("🎉 工作流执行完成!")
        print(f"📊 最终步骤: {result['current_step']}")
        print(f"💬 最终响应: {result.get('response', 'N/A')}")
        print(f"📝 消息历史: {result['messages']}")

        # 流式执行示例
        print("\n" + "=" * 50)
        print("🌊 流式执行示例:")

        for step in workflow.stream(initial_state):
            node_name = list(step.keys())[0]
            node_state = step[node_name]
            print(f"  📍 {node_name}: {node_state.get('current_step', 'N/A')}")

    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    main()