"""
Text-to-TestCase 图工作流

基于 LangGraph 的测试用例生成工作流
将 TestCaseSupervisor 封装为 LangGraph 兼容的图
"""

from typing import Annotated, Any, Dict, List, Literal, Optional
from dataclasses import dataclass, field

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from .config import Config
from .models import TestCaseState
from .supervisor import TestCaseSupervisor


# ============== LangGraph 状态定义 ==============

@dataclass
class Text2TestCaseGraphState:
    """LangGraph 兼容的状态定义
    
    使用 messages 作为主要通信通道，同时保留 TestCaseState 的核心字段
    """
    # LangGraph 标准消息列表
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    
    # 测试用例生成核心字段
    requirement: str = ""
    test_type: Literal["API", "Web", "App"] = "API"
    
    # 阶段输出
    analysis: str = ""
    test_points: str = ""
    testcases: str = ""
    review: str = ""
    
    # 质量评分
    quality_score: float = 0.0
    quality_dimensions: Dict[str, float] = field(default_factory=dict)
    
    # 输出文件
    xmind_path: str = ""
    excel_path: str = ""
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    # 迭代控制
    iteration: int = 0
    max_iterations: int = 3
    
    # 阶段完成标记
    analyze_completed: bool = False
    design_completed: bool = False
    generate_completed: bool = False
    review_completed: bool = False
    
    # 当前阶段
    current_phase: str = "init"
    target_phase: str = "end"


# ============== 模型工厂 ==============

def get_model(model_str: str, api_key: str = None):
    """获取 LLM 模型实例"""
    config = Config()
    key = api_key or config.api_key
    
    if model_str.startswith("siliconflow:"):
        model_name = model_str.replace("siliconflow:", "")
        return ChatOpenAI(
            model=model_name,
            api_key=key,
            base_url="https://api.siliconflow.cn/v1",
            temperature=0.0,
            max_tokens=4096,
            streaming=True,
        )
    
    return init_chat_model(model_str, temperature=0.0)


# ============== 图节点函数 ==============

async def process_input(state: Text2TestCaseGraphState) -> Dict[str, Any]:
    """处理用户输入，提取需求"""
    messages = state.messages
    
    # 从最后一条人类消息中提取需求
    requirement = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            requirement = msg.content
            break
    
    if not requirement:
        return {
            "messages": [AIMessage(content="请提供需要生成测试用例的需求描述。")],
            "current_phase": "init"
        }
    
    return {
        "requirement": requirement,
        "current_phase": "processing"
    }


async def run_supervisor(state: Text2TestCaseGraphState) -> Dict[str, Any]:
    """运行 TestCaseSupervisor 生成测试用例"""
    config = Config()
    
    # 创建模型
    reader_model = get_model(config.reader_model)
    writer_model = get_model(config.writer_model)
    reviewer_model = get_model(config.reviewer_model)
    
    # 创建 Supervisor
    supervisor = TestCaseSupervisor(
        reader_model=reader_model,
        writer_model=writer_model,
        reviewer_model=reviewer_model,
        enable_middleware=True,
        enable_human_review=False,
        enable_persistence=True,
        enable_data_export=True,
    )
    
    # 创建内部状态
    internal_state = TestCaseState(
        requirement=state.requirement,
        test_type=state.test_type,
        max_iterations=state.max_iterations,
    )
    
    # 定义进度回调
    progress_messages = []
    
    async def progress_hook(chunk_updates: Dict[str, Any]):
        """进度回调 - 收集中间状态"""
        if "testcases" in chunk_updates:
            progress_messages.append(f"正在生成测试用例...")
    
    # 运行 Supervisor
    try:
        result_state = await supervisor.run(internal_state, writer_status_hook=progress_hook)
        
        # 构建响应消息
        response_parts = []
        
        if result_state.analysis:
            response_parts.append(f"## 需求分析\n{result_state.analysis[:500]}...")
        
        if result_state.test_points:
            response_parts.append(f"## 测试点设计\n{result_state.test_points[:500]}...")
        
        if result_state.testcases:
            response_parts.append(f"## 测试用例\n{result_state.testcases}")
        
        if result_state.review:
            response_parts.append(f"## 评审结果\n质量评分: {result_state.quality_score:.1f}分\n{result_state.review[:300]}...")
        
        if result_state.xmind_path or result_state.excel_path:
            response_parts.append(f"## 输出文件\n- XMind: {result_state.xmind_path or '未生成'}\n- Excel: {result_state.excel_path or '未生成'}")
        
        response = "\n\n".join(response_parts) if response_parts else "测试用例生成完成"
        
        return {
            "messages": [AIMessage(content=response)],
            "analysis": result_state.analysis,
            "test_points": result_state.test_points,
            "testcases": result_state.testcases,
            "review": result_state.review,
            "quality_score": result_state.quality_score,
            "quality_dimensions": result_state.quality_dimensions,
            "xmind_path": result_state.xmind_path,
            "excel_path": result_state.excel_path,
            "statistics": result_state.statistics,
            "iteration": result_state.iteration,
            "analyze_completed": result_state.analyze_completed,
            "design_completed": result_state.design_completed,
            "generate_completed": result_state.generate_completed,
            "review_completed": result_state.review_completed,
            "current_phase": "completed"
        }
        
    except Exception as e:
        error_msg = f"测试用例生成失败: {str(e)}"
        return {
            "messages": [AIMessage(content=error_msg)],
            "current_phase": "error"
        }


def should_process(state: Text2TestCaseGraphState) -> Literal["process", "end"]:
    """决定是否需要处理"""
    if state.requirement and state.current_phase == "processing":
        return "process"
    return "end"


# ============== 图构建 ==============

def build_text2testcase_graph():
    """构建 Text2TestCase 图"""
    
    # 创建图
    graph = StateGraph(Text2TestCaseGraphState)
    
    # 添加节点
    graph.add_node("input", process_input)
    graph.add_node("supervisor", run_supervisor)
    
    # 添加边
    graph.add_edge(START, "input")
    graph.add_conditional_edges(
        "input",
        should_process,
        {
            "process": "supervisor",
            "end": END
        }
    )
    graph.add_edge("supervisor", END)
    
    return graph


# ============== LangGraph API 工厂函数 ==============

def get_app(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用 (无 checkpointer)
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图（checkpointer 由 LangGraph API 注入）
    """
    graph = build_text2testcase_graph()
    return graph.compile()


def get_stream_app(config: dict = None):
    """
    流式图工厂函数 - 供 LangGraph API 使用
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图，支持流式输出
    """
    graph = build_text2testcase_graph()
    return graph.compile()


def get_app_with_memory():
    """
    带内存检查点的图 - 用于独立运行
    
    Returns:
        编译好的图（带 MemorySaver）
    """
    graph = build_text2testcase_graph()
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# ============== 便捷运行函数 ==============

async def run_text2testcase(
    requirement: str,
    test_type: Literal["API", "Web", "App"] = "API",
    thread_id: str = "default"
) -> Dict[str, Any]:
    """便捷运行函数
    
    Args:
        requirement: 需求描述
        test_type: 测试类型
        thread_id: 会话ID
        
    Returns:
        生成结果
    """
    app = get_app_with_memory()
    
    initial_state = {
        "messages": [HumanMessage(content=requirement)],
        "test_type": test_type,
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await app.ainvoke(initial_state, config)
    
    return {
        "testcases": result.get("testcases", ""),
        "analysis": result.get("analysis", ""),
        "test_points": result.get("test_points", ""),
        "review": result.get("review", ""),
        "quality_score": result.get("quality_score", 0.0),
        "xmind_path": result.get("xmind_path", ""),
        "excel_path": result.get("excel_path", ""),
    }
