"""测试点设计智能体"""
from pathlib import Path
from typing import Dict, Any

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


def create_test_point_designer_agent(model: BaseChatModel, summarization_model: BaseChatModel = None):
    """创建测试点设计智能体 - 带上下文压缩"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_TEST_POINT_DESIGNER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    middleware = []
    if summarization_model:
        middleware.append(SummarizationMiddleware(
            model=summarization_model,
            max_tokens_before_summary=4000,
            messages_to_keep=10,
        ))

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="test_point_designer",
        state_schema=TestCaseState,
        middleware=middleware,
    )
    
    return agent


async def run_test_point_designer(agent, state: TestCaseState, enable_middleware: bool = True) -> Dict[str, Any]:
    """运行测试点设计"""
    # 消息过滤中间件
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.TEST_POINT_DESIGNER,
            phase_name="design"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    user_message = f"""请基于以下信息设计测试点:

## 原始需求
{state.requirement}

## 需求分析结果
{state.analysis if state.analysis else "（分析中...）"}

请设计全面的测试点,覆盖正常、异常、边界场景。"""

    response = await agent.ainvoke({"messages": state.messages + [HumanMessage(content=user_message)]})
    ai_output = response["messages"][-1].content if response.get("messages") else ""
    new_messages = state.messages + [HumanMessage(content=user_message), AIMessage(content=ai_output)]

    updates = {
        "test_points": ai_output,
        "messages": new_messages,
        "current_phase": "design",
        "design_completed": True,
    }

    # 状态同步中间件
    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="test_points",
            phase_name="design"
        )
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

