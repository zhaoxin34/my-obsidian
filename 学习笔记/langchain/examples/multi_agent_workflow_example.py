#!/usr/bin/env python3
"""
LangGraph多Agent协作工作流示例
演示如何创建多Agent协作的复杂工作流

运行方式:
python multi_agent_workflow_example.py
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional, List, Dict, Any
import operator
from datetime import datetime
import random

class MultiAgentState(TypedDict):
    """多Agent工作流状态"""
    current_step: str
    messages: Annotated[List[str], operator.add]

    # 任务信息
    task_id: str
    task_description: str
    task_type: str
    priority: str

    # Agent结果
    research_results: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    writing_results: Optional[Dict[str, Any]]
    review_results: Optional[Dict[str, Any]]

    # 协作控制
    active_agent: Optional[str]
    agent_assignments: Dict[str, str]
    agent_status: Dict[str, str]
    collaboration_decisions: List[str]

    # 质量控制
    quality_score: Optional[float]
    requires_revision: bool
    revision_count: int
    max_revisions: int

class ResearcherAgent:
    """研究员Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities = ["数据收集", "信息分析", "趋势识别"]

    def research_topic(self, topic: str, task_type: str) -> Dict[str, Any]:
        """执行研究任务"""
        print(f"🔍 [{self.agent_id}] 开始研究: {topic}")

        # 模拟研究过程
        research_sources = [
            f"{topic} - 学术论文分析",
            f"{topic} - 行业报告总结",
            f"{topic} - 最新动态追踪",
            f"{topic} - 专家观点收集"
        ]

        key_findings = [
            f"{topic}的核心趋势1",
            f"{topic}的重要发展2",
            f"{topic}的未来展望3"
        ]

        confidence = random.uniform(0.75, 0.95)

        print(f"✅ [{self.agent_id}] 研究完成，置信度: {confidence:.2f}")

        return {
            "agent_id": self.agent_id,
            "topic": topic,
            "task_type": task_type,
            "sources": research_sources,
            "findings": key_findings,
            "confidence": confidence,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

class AnalystAgent:
    """分析师Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities = ["数据分析", "模式识别", "预测建模"]

    def analyze_data(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析任务"""
        print(f"📊 [{self.agent_id}] 开始分析数据")

        findings = research_data.get("findings", [])
        confidence = research_data.get("confidence", 0.5)

        # 基于研究发现进行分析
        analysis_result = {
            "agent_id": self.agent_id,
            "input_confidence": confidence,
            "insights": [
                f"基于研究发现的关键洞察1",
                f"数据模式和趋势分析2",
                f"预测性分析和建议3"
            ],
            "risk_assessment": {
                "low_risk": 3,
                "medium_risk": 2,
                "high_risk": 1
            },
            "recommendations": [
                "建议1: 基于数据分析的策略调整",
                "建议2: 风险控制措施",
                "建议3: 未来发展方向"
            ],
            "confidence": min(confidence + 0.05, 1.0),  # 分析提高置信度
            "status": "completed"
        }

        print(f"✅ [{self.agent_id}] 分析完成，新的置信度: {analysis_result['confidence']:.2f}")

        return analysis_result

class WriterAgent:
    """写作Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities = ["内容创作", "结构化写作", "语言优化"]

    def write_content(self, analysis_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """执行写作任务"""
        print(f"✍️ [{self.agent_id}] 开始撰写内容")

        insights = analysis_data.get("insights", [])
        recommendations = analysis_data.get("recommendations", [])

        # 生成结构化内容
        content = f"""
# {topic} - 分析报告

## 执行摘要
本报告基于深入研究和数据分析，为{topic}提供了全面的洞察和建议。

## 主要发现
{chr(10).join(f"- {insight}" for insight in insights)}

## 风险评估
- 低风险因素: {analysis_data['risk_assessment']['low_risk']}项
- 中等风险因素: {analysis_data['risk_assessment']['medium_risk']}项
- 高风险因素: {analysis_data['risk_assessment']['high_risk']}项

## 建议和策略
{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))}

## 结论
基于全面的研究和分析，我们认为{topic}具有重要的发展潜力，建议采用渐进式策略实施。
        """.strip()

        writing_result = {
            "agent_id": self.agent_id,
            "topic": topic,
            "content": content,
            "word_count": len(content.split()),
            "sections": ["执行摘要", "主要发现", "风险评估", "建议和策略", "结论"],
            "quality_score": random.uniform(0.8, 0.95),
            "status": "completed"
        }

        print(f"✅ [{self.agent_id}] 写作完成，字数: {writing_result['word_count']}")

        return writing_result

class ReviewerAgent:
    """审稿Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities = ["内容审核", "质量评估", "改进建议"]

    def review_content(self, writing_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行审稿任务"""
        print(f"🔍 [{self.agent_id}] 开始审稿")

        content = writing_data.get("content", "")
        quality_score = writing_data.get("quality_score", 0.5)

        # 评估内容质量
        evaluation_criteria = {
            "准确性": random.uniform(0.8, 0.95),
            "完整性": random.uniform(0.75, 0.9),
            "逻辑性": random.uniform(0.8, 0.95),
            "可读性": random.uniform(0.85, 0.95)
        }

        overall_score = sum(evaluation_criteria.values()) / len(evaluation_criteria)

        # 决定是否需要修订
        requires_revision = overall_score < 0.85

        review_result = {
            "agent_id": self.agent_id,
            "content_length": len(content),
            "word_count": len(content.split()),
            "evaluation_criteria": evaluation_criteria,
            "overall_score": overall_score,
            "requires_revision": requires_revision,
            "feedback": {
                "strengths": ["内容结构清晰", "逻辑严密", "建议具体"],
                "improvements": ["可增加更多数据支撑", "某些表述可以优化"]
            },
            "status": "completed"
        }

        print(f"✅ [{self.agent_id}] 审稿完成，评分: {overall_score:.2f}, 需要修订: {'是' if requires_revision else '否'}")

        return review_result

# Agent实例
researcher = ResearcherAgent("researcher_001")
analyst = AnalystAgent("analyst_001")
writer = WriterAgent("writer_001")
reviewer = ReviewerAgent("reviewer_001")

def coordinator_node(state: MultiAgentState) -> MultiAgentState:
    """协调员节点"""
    task_description = state["task_description"]
    task_type = state["task_type"]

    print(f"🎯 [协调员] 开始协调任务: {task_description}")

    # 任务分析和Agent分配
    agent_assignments = {
        "researcher_001": "研究阶段",
        "analyst_001": "分析阶段",
        "writer_001": "写作阶段",
        "reviewer_001": "审稿阶段"
    }

    collaboration_decisions = [
        "分配研究员进行资料收集",
        "指派分析师处理数据",
        "安排写作员生成内容",
        "指定审稿员质量控制"
    ]

    print(f"📋 [协调员] Agent分配完成")

    return {
        **state,
        "current_step": "coordinator",
        "active_agent": "coordinator",
        "agent_assignments": agent_assignments,
        "agent_status": {agent: "pending" for agent in agent_assignments},
        "collaboration_decisions": collaboration_decisions,
        "messages": state["messages"] + ["协调员完成任务分配"]
    }

def research_node(state: MultiAgentState) -> MultiAgentState:
    """研究节点"""
    topic = state["task_description"]
    task_type = state["task_type"]

    print(f"🔍 [研究阶段] 开始执行")

    # 执行研究
    research_results = researcher.research_topic(topic, task_type)

    # 更新Agent状态
    agent_status = state["agent_status"].copy()
    agent_status["researcher_001"] = "completed"

    print(f"✅ [研究阶段] 完成")

    return {
        **state,
        "current_step": "research",
        "active_agent": "researcher_001",
        "research_results": research_results,
        "agent_status": agent_status,
        "messages": state["messages"] + ["研究阶段完成"]
    }

def analysis_node(state: MultiAgentState) -> MultiAgentState:
    """分析节点"""
    research_data = state.get("research_results")

    if not research_data:
        print("❌ [分析阶段] 缺少研究数据")
        return {
            **state,
            "current_step": "analysis_error",
            "messages": state["messages"] + ["分析阶段失败: 缺少研究数据"]
        }

    print(f"📊 [分析阶段] 开始执行")

    # 执行分析
    analysis_results = analyst.analyze_data(research_data)

    # 更新Agent状态
    agent_status = state["agent_status"].copy()
    agent_status["analyst_001"] = "completed"

    print(f"✅ [分析阶段] 完成")

    return {
        **state,
        "current_step": "analysis",
        "active_agent": "analyst_001",
        "analysis_results": analysis_results,
        "agent_status": agent_status,
        "messages": state["messages"] + ["分析阶段完成"]
    }

def writing_node(state: MultiAgentState) -> MultiAgentState:
    """写作节点"""
    analysis_data = state.get("analysis_results")
    topic = state["task_description"]

    if not analysis_data:
        print("❌ [写作阶段] 缺少分析数据")
        return {
            **state,
            "current_step": "writing_error",
            "messages": state["messages"] + ["写作阶段失败: 缺少分析数据"]
        }

    print(f"✍️ [写作阶段] 开始执行")

    # 执行写作
    writing_results = writer.write_content(analysis_data, topic)

    # 更新Agent状态
    agent_status = state["agent_status"].copy()
    agent_status["writer_001"] = "completed"

    print(f"✅ [写作阶段] 完成")

    return {
        **state,
        "current_step": "writing",
        "active_agent": "writer_001",
        "writing_results": writing_results,
        "agent_status": agent_status,
        "messages": state["messages"] + ["写作阶段完成"]
    }

def review_node(state: MultiAgentState) -> MultiAgentState:
    """审稿节点"""
    writing_data = state.get("writing_results")

    if not writing_data:
        print("❌ [审稿阶段] 缺少写作内容")
        return {
            **state,
            "current_step": "review_error",
            "messages": state["messages"] + ["审稿阶段失败: 缺少写作内容"]
        }

    print(f"🔍 [审稿阶段] 开始执行")

    # 执行审稿
    review_results = reviewer.review_content(writing_data)

    # 更新Agent状态
    agent_status = state["agent_status"].copy()
    agent_status["reviewer_001"] = "completed"

    print(f"✅ [审稿阶段] 完成")

    return {
        **state,
        "current_step": "review",
        "active_agent": "reviewer_001",
        "review_results": review_results,
        "quality_score": review_results["overall_score"],
        "requires_revision": review_results["requires_revision"],
        "agent_status": agent_status,
        "messages": state["messages"] + ["审稿阶段完成"]
    }

def revision_node(state: MultiAgentState) -> MultiAgentState:
    """修订节点"""
    revision_count = state["revision_count"] + 1
    max_revisions = state["max_revisions"]

    print(f"🔄 [修订阶段] 第{revision_count}次修订")

    # 模拟修订过程
    improved_quality = min(state.get("quality_score", 0.5) + 0.1, 1.0)
    requires_revision = improved_quality < 0.85 and revision_count < max_revisions

    print(f"📈 [修订阶段] 质量提升到: {improved_quality:.2f}")

    return {
        **state,
        "current_step": "revision",
        "revision_count": revision_count,
        "quality_score": improved_quality,
        "requires_revision": requires_revision,
        "messages": state["messages"] + [f"第{revision_count}次修订完成"]
    }

def finalize_node(state: MultiAgentState) -> MultiAgentState:
    """最终完成节点"""
    writing_data = state.get("writing_results", {})
    review_data = state.get("review_results", {})

    print(f"🎉 [最终阶段] 工作流完成")

    final_content = writing_data.get("content", "内容生成失败")
    final_score = state.get("quality_score", 0.0)

    print(f"📝 最终内容长度: {len(final_content)} 字符")
    print(f"📊 最终质量评分: {final_score:.2f}")

    return {
        **state,
        "current_step": "finalize",
        "final_content": final_content,
        "final_quality_score": final_score,
        "messages": state["messages"] + ["工作流最终完成"]
    }

def create_multi_agent_workflow():
    """创建多Agent工作流"""
    graph = StateGraph(MultiAgentState)

    # 添加节点
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("research", research_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("writing", writing_node)
    graph.add_node("review", review_node)
    graph.add_node("revision", revision_node)
    graph.add_node("finalize", finalize_node)

    # 设置入口点
    graph.set_entry_point("coordinator")

    # 添加边
    graph.add_edge("coordinator", "research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "writing")
    graph.add_edge("writing", "review")

    # 条件边：审稿后决定是否修订
    def route_after_review(state: MultiAgentState) -> str:
        requires_revision = state.get("requires_revision", False)
        revision_count = state.get("revision_count", 0)
        max_revisions = state.get("max_revisions", 3)

        if requires_revision and revision_count < max_revisions:
            return "revision"
        else:
            return "finalize"

    graph.add_conditional_edges(
        "review",
        route_after_review,
        {
            "revision": "revision",
            "finalize": "finalize"
        }
    )

    # 修订后回到审稿
    graph.add_edge("revision", "review")
    graph.add_edge("finalize", END)

    return graph.compile()

def main():
    """主函数"""
    print("🎯 LangGraph多Agent协作工作流示例")
    print("=" * 70)

    # 创建工作流
    workflow = create_multi_agent_workflow()

    # 测试任务
    test_tasks = [
        {
            "task_id": "task_001",
            "task_description": "人工智能在医疗领域的应用分析",
            "task_type": "research_report",
            "priority": "high"
        },
        {
            "task_id": "task_002",
            "task_description": "区块链技术发展趋势研究",
            "task_type": "trend_analysis",
            "priority": "medium"
        }
    ]

    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*70}")
        print(f"🧪 测试任务 {i}: {task['task_description']}")
        print(f"{'='*70}")

        # 准备初始状态
        initial_state = {
            "current_step": "init",
            "messages": [],
            **task,
            "active_agent": None,
            "agent_assignments": {},
            "agent_status": {},
            "collaboration_decisions": [],
            "revision_count": 0,
            "max_revisions": 3
        }

        try:
            print(f"\n📋 任务信息:")
            print(f"  ID: {task['task_id']}")
            print(f"  类型: {task['task_type']}")
            print(f"  优先级: {task['priority']}")

            # 执行工作流
            result = workflow.invoke(initial_state)

            # 显示结果
            print(f"\n📊 执行结果:")
            print(f"  最终步骤: {result['current_step']}")
            print(f"  质量评分: {result.get('final_quality_score', 0):.2f}")
            print(f"  修订次数: {result.get('revision_count', 0)}")

            # 显示Agent状态
            print(f"\n🤖 Agent状态:")
            for agent, status in result.get('agent_status', {}).items():
                print(f"  {agent}: {status}")

            # 显示最终内容摘要
            final_content = result.get('final_content', '')
            if final_content and len(final_content) > 100:
                print(f"\n📝 内容摘要:")
                print(f"  {final_content[:200]}...")
            else:
                print(f"\n📝 最终内容: {final_content}")

        except Exception as e:
            print(f"❌ 执行失败: {e}")

    print(f"\n{'='*70}")
    print("🎉 多Agent协作示例完成!")

if __name__ == "__main__":
    main()