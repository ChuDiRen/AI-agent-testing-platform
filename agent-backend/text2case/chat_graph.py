"""
Text-to-TestCase 图工作流

基于 LangGraph 官方的 langgraph_supervisor 构建
参考 text2sql 架构，使用 Supervisor + ReAct Agents 模式
"""
import sys
import os
from typing import Optional

# 确保 text2case 包可以被导入
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from text2case.config import get_model, LLMConfig
from text2case.agents.supervisor_agent import build_supervisor_with_config


def create_text2case_graph(
    model_config: Optional[LLMConfig] = None,
    max_retries: int = 2,
    enable_review: bool = True,
    enable_export: bool = False,
    checkpointer=None,
    store=None,
    use_persistent_memory: bool = False
):
    """创建 Text-to-TestCase 图工作流
    
    Args:
        model_config: LLM 配置
        max_retries: 最大重试次数
        enable_review: 是否启用评审（默认启用）
        enable_export: 是否启用导出（默认不启用，按需调用）
        checkpointer: 短期记忆（可选，优先使用）
        store: 长期记忆（可选，优先使用）
        use_persistent_memory: 是否使用持久化记忆（当 checkpointer/store 未提供时）
        
    Returns:
        编译好的图
    """
    model = get_model(model_config)
    
    supervisor = build_supervisor_with_config(
        model=model,
        max_retries=max_retries,
        enable_review=enable_review,
        enable_export=enable_export
    )
    
    # 如果未提供 checkpointer/store 且启用持久化记忆，则使用 MemoryManager
    if use_persistent_memory and checkpointer is None:
        from memory import get_memory_manager
        memory = get_memory_manager()
        checkpointer = memory.checkpointer
        store = memory.store
    
    return supervisor.compile(checkpointer=checkpointer, store=store)


def graph(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图（不含 checkpointer/store，由 LangGraph API 注入）
    """
    max_retries = 2
    enable_review = True
    enable_export = False
    
    if config and "configurable" in config:
        max_retries = config["configurable"].get("max_retries", 2)
        enable_review = config["configurable"].get("enable_review", True)
        enable_export = config["configurable"].get("enable_export", False)
    
    return create_text2case_graph(
        max_retries=max_retries,
        enable_review=enable_review,
        enable_export=enable_export
    )


# ============== LangGraph API 工厂函数 ==============

def get_app(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用
    
    重要：返回未编译的 StateGraph，让 LangGraph API 服务器负责编译并注入 
    checkpointer 和 store（通过 langgraph.json 配置）。
    
    Args:
        config: RunnableConfig
        
    Returns:
        未编译的 StateGraph（checkpointer/store 由 LangGraph API 在编译时注入）
    """
    max_retries = 2
    enable_review = True
    enable_export = True  # 默认启用导出
    
    if config and "configurable" in config:
        max_retries = config["configurable"].get("max_retries", 2)
        enable_review = config["configurable"].get("enable_review", True)
        enable_export = config["configurable"].get("enable_export", True)
    
    model = get_model()
    
    # 返回未编译的 StateGraph，由 LangGraph API 服务器编译并注入 checkpointer/store
    return build_supervisor_with_config(
        model=model,
        max_retries=max_retries,
        enable_review=enable_review,
        enable_export=enable_export
    )


def get_app_simple(config: dict = None):
    """
    简化版图工厂函数 - 不带记忆
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图（不带 checkpointer）
    """
    return graph(config)


# ============== 便捷运行函数 ==============

async def run_text2case(
    requirement: str,
    test_type: str = "API",
    thread_id: str = "default",
    user_id: str = "default",
    enable_review: bool = True,
    enable_export: bool = False
) -> dict:
    """便捷运行函数（带持久化记忆）
    
    Args:
        requirement: 需求描述
        test_type: 测试类型 (API/Web/App)
        thread_id: 会话 ID
        user_id: 用户 ID
        enable_review: 是否启用评审
        enable_export: 是否启用导出
        
    Returns:
        生成结果
    """
    from langchain_core.messages import HumanMessage
    
    # 使用持久化记忆创建图
    app = create_text2case_graph(
        max_retries=2,
        enable_review=enable_review,
        enable_export=enable_export,
        use_persistent_memory=True
    )
    
    # 构建输入
    user_message = f"""请为以下{test_type}需求生成测试用例：

{requirement}

请按照完整流程执行：
1. 分析需求
2. 生成测试用例
{"3. 评审测试用例" if enable_review else ""}
{"4. 导出文件" if enable_export else ""}
"""
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    result = await app.ainvoke(
        {"messages": [HumanMessage(content=user_message)]},
        config
    )
    
    # 提取最终结果
    final_message = result.get("messages", [])[-1] if result.get("messages") else None
    
    return {
        "success": True,
        "content": final_message.content if final_message else "",
        "messages": result.get("messages", []),
    }


# ============== 同步运行函数 ==============

def run_text2case_sync(
    requirement: str,
    test_type: str = "API",
    thread_id: str = "default",
    user_id: str = "default",
    enable_review: bool = False,
    enable_export: bool = False,
    use_memory: bool = True
) -> dict:
    """同步运行函数
    
    Args:
        requirement: 需求描述
        test_type: 测试类型
        thread_id: 会话 ID
        user_id: 用户 ID
        enable_review: 是否启用评审
        enable_export: 是否启用导出
        use_memory: 是否使用持久化记忆
        
    Returns:
        生成结果
    """
    from langchain_core.messages import HumanMessage
    
    app = create_text2case_graph(
        max_retries=2,
        enable_review=enable_review,
        enable_export=enable_export,
        use_persistent_memory=use_memory
    )
    
    user_message = f"""请为以下{test_type}需求生成测试用例：

{requirement}
"""
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    result = app.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config
    )
    
    final_message = result.get("messages", [])[-1] if result.get("messages") else None
    
    return {
        "success": True,
        "content": final_message.content if final_message else "",
    }
