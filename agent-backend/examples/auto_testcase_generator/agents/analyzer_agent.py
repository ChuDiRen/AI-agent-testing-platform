"""需求分析智能体 - 提取需求关键信息"""
from pathlib import Path
from typing import Dict, Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


def create_analyzer_agent(model: BaseChatModel):
    """创建需求分析智能体 (集成 middlewareV1)

    职责:
    - 分析测试需求,提取关键信息
    - 识别接口信息、参数说明、业务规则等
    - 为后续测试点设计提供基础

    中间件:
    - MessageFilterMiddleware: 过滤消息 (只保留1条human消息)
    - StateSyncMiddleware: 保存输出到 state.analysis

    Args:
        model: 语言模型实例

    Returns:
        需求分析智能体
    """
    # 加载系统提示词
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_READER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')

    # 创建智能体 (集成中间件)
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="analyzer",
        state_schema=TestCaseState,
    )

    return agent


async def run_analyzer(agent, state: TestCaseState, enable_middleware: bool = True) -> Dict[str, Any]:
    """运行需求分析智能体

    Args:
        agent: 智能体实例
        state: 当前状态
        enable_middleware: 是否启用中间件

    Returns:
        更新后的状态字典
    """
    # 1️⃣ 消息过滤 (middlewareV1)
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.ANALYZER,
            phase_name="analyze"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    # 2️⃣ 构建输入消息
    user_message = f"请分析以下{state.test_type}测试需求：\n\n{state.requirement}"

    # 3️⃣ 调用智能体
    response = await agent.ainvoke({
        "messages": state.messages + [HumanMessage(content=user_message)]
    })

    # 4️⃣ 提取AI输出
    ai_output = response["messages"][-1].content if response.get("messages") else ""

    # 5️⃣ 更新消息历史
    new_messages = state.messages + [
        HumanMessage(content=user_message),
        AIMessage(content=ai_output)
    ]

    # 6️⃣ 状态同步 (middlewareV1)
    updates = {
        "analysis": ai_output,
        "messages": new_messages,
        "current_phase": "analyze",
        "analyze_completed": True,
    }

    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="analysis",
            phase_name="analyze"
        )
        # 临时状态用于中间件
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

