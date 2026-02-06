#!/usr/bin/env python3
"""
LangGraph条件路由工作流示例
演示如何创建包含条件分支的复杂工作流

运行方式:
python conditional_workflow_example.py
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional
import operator
from datetime import datetime
import random

class ConditionalWorkflowState(TypedDict):
    """条件工作流状态"""
    current_step: str
    messages: Annotated[list[str], operator.add]
    user_query: str
    query_type: Optional[str]
    confidence: float
    requires_human: bool
    processing_result: Optional[dict]
    final_answer: Optional[str]
    step_count: int

def classify_query_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """查询分类节点"""
    query = state["user_query"].lower()

    # 简单的查询分类
    if any(word in query for word in ["搜索", "查找", "什么"]):
        query_type = "search"
        confidence = 0.9
    elif any(word in query for word in ["计算", "数学", "等于", "+", "-", "*", "/"]):
        query_type = "calculation"
        confidence = 0.85
    elif any(word in query for word in ["分析", "比较", "评估"]):
        query_type = "analysis"
        confidence = 0.8
    elif any(word in query for word in ["聊天", "对话", "你好"]):
        query_type = "chat"
        confidence = 0.95
    else:
        query_type = "general"
        confidence = 0.7

    print(f"🔍 查询分类: '{query}' -> {query_type} (置信度: {confidence:.2f})")

    return {
        **state,
        "current_step": "classify_query",
        "query_type": query_type,
        "confidence": confidence,
        "messages": state["messages"] + [f"查询类型: {query_type}"]
    }

def search_handler_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """搜索处理节点"""
    query = state["user_query"]

    # 模拟搜索结果
    search_results = [
        f"搜索结果1: 关于'{query}'的信息",
        f"搜索结果2: '{query}'相关资料",
        f"搜索结果3: '{query}'的最新动态"
    ]

    processing_result = {
        "type": "search",
        "query": query,
        "results": search_results,
        "result_count": len(search_results)
    }

    print(f"🔍 搜索完成，找到{len(search_results)}个结果")

    return {
        **state,
        "current_step": "search_handler",
        "processing_result": processing_result,
        "messages": state["messages"] + ["搜索处理完成"]
    }

def calculation_handler_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """计算处理节点"""
    query = state["user_query"]

    # 简单的计算模拟
    if "+" in query:
        result = "模拟计算: 1 + 1 = 2"
    elif "-" in query:
        result = "模拟计算: 10 - 5 = 5"
    elif "*" in query:
        result = "模拟计算: 3 * 4 = 12"
    else:
        result = "模拟计算: 无法解析表达式"

    processing_result = {
        "type": "calculation",
        "query": query,
        "result": result,
        "success": "无法解析" not in result
    }

    print(f"🧮 计算完成: {result}")

    return {
        **state,
        "current_step": "calculation_handler",
        "processing_result": processing_result,
        "messages": state["messages"] + ["计算处理完成"]
    }

def analysis_handler_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """分析处理节点"""
    query = state["user_query"]

    # 模拟分析结果
    analysis_result = {
        "type": "analysis",
        "query": query,
        "analysis": f"关于'{query}'的深入分析结果",
        "confidence": random.uniform(0.7, 0.9),
        "recommendations": ["建议1", "建议2", "建议3"]
    }

    print(f"📊 分析完成，置信度: {analysis_result['confidence']:.2f}")

    return {
        **state,
        "current_step": "analysis_handler",
        "processing_result": analysis_result,
        "messages": state["messages"] + ["分析处理完成"]
    }

def chat_handler_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """聊天处理节点"""
    query = state["user_query"]

    # 简单的聊天响应
    responses = {
        "你好": "你好！我是AI助手，很高兴为您服务！",
        "谢谢": "不客气！还有什么我可以帮助您的吗？",
        "再见": "再见！祝您有美好的一天！"
    }

    response = responses.get(query, f"我理解您说的是'{query}'，请问需要我为您做什么？")

    processing_result = {
        "type": "chat",
        "query": query,
        "response": response,
        "confidence": 0.95
    }

    print(f"💬 聊天响应: {response}")

    return {
        **state,
        "current_step": "chat_handler",
        "processing_result": processing_result,
        "messages": state["messages"] + ["聊天处理完成"]
    }

def general_handler_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """通用处理节点"""
    query = state["user_query"]

    processing_result = {
        "type": "general",
        "query": query,
        "response": f"我正在处理您的查询: '{query}'",
        "suggestions": ["请提供更具体的信息", "或者尝试重新表述您的问题"]
    }

    print(f"🔧 通用处理: '{query}'")

    return {
        **state,
        "current_step": "general_handler",
        "processing_result": processing_result,
        "messages": state["messages"] + ["通用处理完成"]
    }

def quality_check_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """质量检查节点"""
    confidence = state["confidence"]
    requires_human = confidence < 0.8

    print(f"🔍 质量检查: 置信度 {confidence:.2f} -> {'需要人工' if requires_human else '自动通过'}")

    return {
        **state,
        "current_step": "quality_check",
        "requires_human": requires_human,
        "messages": state["messages"] + ["质量检查完成"]
    }

def human_review_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """人工审查节点"""
    processing_result = state.get("processing_result", {})

    print("👨‍💼 需要人工干预:")
    print(f"  当前处理结果: {processing_result}")
    print("  请人工审查并提供反馈...")

    # 模拟人工输入
    human_feedback = "人工确认通过"
    adjusted_confidence = min(state["confidence"] + 0.1, 1.0)

    print(f"✅ 人工反馈: {human_feedback}")
    print(f"📈 调整后置信度: {adjusted_confidence:.2f}")

    return {
        **state,
        "current_step": "human_review",
        "confidence": adjusted_confidence,
        "requires_human": False,
        "human_feedback": human_feedback,
        "messages": state["messages"] + ["人工审查完成"]
    }

def generate_final_answer_node(state: ConditionalWorkflowState) -> ConditionalWorkflowState:
    """生成最终答案节点"""
    processing_result = state.get("processing_result", {})
    query_type = state.get("query_type", "general")

    # 基于处理结果生成最终答案
    if query_type == "search":
        results = processing_result.get("results", [])
        final_answer = f"🔍 搜索结果:\n" + "\n".join(f"• {result}" for result in results)
    elif query_type == "calculation":
        result = processing_result.get("result", "计算失败")
        final_answer = f"🧮 计算结果: {result}"
    elif query_type == "analysis":
        analysis = processing_result.get("analysis", "")
        recommendations = processing_result.get("recommendations", [])
        final_answer = f"📊 分析结果:\n{analysis}\n\n💡 建议:\n" + "\n".join(f"• {rec}" for rec in recommendations)
    elif query_type == "chat":
        response = processing_result.get("response", "无法生成响应")
        final_answer = f"💬 {response}"
    else:
        response = processing_result.get("response", "处理完成")
        final_answer = f"🔧 {response}"

    print(f"📝 最终答案生成完成")

    return {
        **state,
        "current_step": "generate_final_answer",
        "final_answer": final_answer,
        "messages": state["messages"] + ["最终答案生成完成"]
    }

def create_conditional_workflow():
    """创建条件工作流"""
    graph = StateGraph(ConditionalWorkflowState)

    # 添加节点
    graph.add_node("classify_query", classify_query_node)
    graph.add_node("search_handler", search_handler_node)
    graph.add_node("calculation_handler", calculation_handler_node)
    graph.add_node("analysis_handler", analysis_handler_node)
    graph.add_node("chat_handler", chat_handler_node)
    graph.add_node("general_handler", general_handler_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("generate_final_answer", generate_final_answer_node)

    # 设置入口点
    graph.set_entry_point("classify_query")

    # 条件路由
    def route_by_query_type(state: ConditionalWorkflowState) -> str:
        """根据查询类型路由"""
        query_type = state.get("query_type", "general")

        route_mapping = {
            "search": "search_handler",
            "calculation": "calculation_handler",
            "analysis": "analysis_handler",
            "chat": "chat_handler",
            "general": "general_handler"
        }

        return route_mapping.get(query_type, "general_handler")

    # 添加条件边
    graph.add_conditional_edges(
        "classify_query",
        route_by_query_type,
        {
            "search_handler": "search_handler",
            "calculation_handler": "calculation_handler",
            "analysis_handler": "analysis_handler",
            "chat_handler": "chat_handler",
            "general_handler": "general_handler"
        }
    )

    # 所有处理节点都连接到质量检查
    for node_name in ["search_handler", "calculation_handler", "analysis_handler", "chat_handler", "general_handler"]:
        graph.add_edge(node_name, "quality_check")

    # 质量检查后的条件路由
    def route_after_quality_check(state: ConditionalWorkflowState) -> str:
        """质量检查后的路由"""
        requires_human = state.get("requires_human", False)

        if requires_human:
            return "human_review"
        else:
            return "generate_final_answer"

    graph.add_conditional_edges(
        "quality_check",
        route_after_quality_check,
        {
            "human_review": "human_review",
            "generate_final_answer": "generate_final_answer"
        }
    )

    # 人工审查后生成最终答案
    graph.add_edge("human_review", "generate_final_answer")
    graph.add_edge("generate_final_answer", END)

    return graph.compile()

def test_queries():
    """测试不同的查询"""
    test_cases = [
        "搜索人工智能的最新发展",
        "计算 15 + 25",
        "分析区块链技术的优缺点",
        "你好",
        "今天天气怎么样？"
    ]

    return test_cases

def main():
    """主函数"""
    print("🎯 LangGraph条件路由工作流示例")
    print("=" * 60)

    # 创建工作流
    workflow = create_conditional_workflow()

    # 测试查询
    test_cases = test_queries()

    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试案例 {i}: '{query}'")
        print(f"{'='*60}")

        # 准备初始状态
        initial_state = {
            "current_step": "init",
            "messages": [],
            "user_query": query,
            "step_count": 0
        }

        try:
            # 执行工作流
            result = workflow.invoke(initial_state)

            # 显示结果
            print(f"\n📊 执行结果:")
            print(f"  🔍 查询类型: {result.get('query_type', 'N/A')}")
            print(f"  📈 置信度: {result.get('confidence', 0):.2f}")
            print(f"  👨‍💼 需要人工: {'是' if result.get('requires_human') else '否'}")
            print(f"\n💬 最终答案:")
            print(f"  {result.get('final_answer', 'N/A')}")

            # 显示消息历史
            print(f"\n📝 处理步骤:")
            for j, msg in enumerate(result['messages'], 1):
                print(f"  {j}. {msg}")

        except Exception as e:
            print(f"❌ 执行失败: {e}")

    print(f"\n{'='*60}")
    print("🎉 所有测试案例完成!")

if __name__ == "__main__":
    main()