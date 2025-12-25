"""用例评审智能体"""
from pathlib import Path
from typing import Dict, Any

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


def create_reviewer_agent(model: BaseChatModel, summarization_model: BaseChatModel = None):
    """创建用例评审智能体 - 带上下文压缩"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    middleware = []
    if summarization_model:
        middleware.append(SummarizationMiddleware(
            model=summarization_model,
            max_tokens_before_summary=8000,
            messages_to_keep=10,
        ))

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="reviewer",
        state_schema=TestCaseState,
        middleware=middleware,
    )
    
    return agent


async def run_reviewer(agent, state: TestCaseState, enable_middleware: bool = True) -> Dict[str, Any]:
    """运行用例评审"""
    # 消息过滤中间件
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.REVIEWER,
            phase_name="review"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    user_message = f"""请评审以下测试用例:

## 原始需求
{state.requirement}

## 需求分析
{state.analysis}

## 测试点设计
{state.test_points}

## 生成的测试用例
{state.testcases}

请评审测试用例的质量,检查是否覆盖所有测试点,并提供改进建议。"""

    response = await agent.ainvoke({"messages": state.messages + [HumanMessage(content=user_message)]})
    ai_output = response["messages"][-1].content if response.get("messages") else ""
    new_messages = state.messages + [HumanMessage(content=user_message), AIMessage(content=ai_output)]

    updates = {
        "review": ai_output,
        "messages": new_messages,
        "current_phase": "review",
        "review_completed": True,
        "iteration": state.iteration + 1,
    }

    # 状态同步中间件
    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="review",
            phase_name="review"
        )
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

