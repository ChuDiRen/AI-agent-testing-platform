"""用例评审智能体 - 评审测试用例质量"""
from pathlib import Path
from typing import Dict, Any
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from ..middleware.config import TestCaseAgentFilterConfig
from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware
from ..models import TestCaseState


def create_reviewer_agent(model: BaseChatModel):
    """创建用例评审智能体
    
    职责:
    - 评审测试用例的完整性和正确性
    - 检查是否覆盖所有测试点
    - 提供改进建议
    
    Args:
        model: 语言模型实例
        
    Returns:
        用例评审智能体
    """
    # 加载系统提示词
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="reviewer",
        state_schema=TestCaseState,
    )
    
    return agent


async def run_reviewer(agent, state: TestCaseState, enable_middleware: bool = True) -> Dict[str, Any]:
    """运行用例评审智能体

    Args:
        agent: 智能体实例
        state: 当前状态
        enable_middleware: 是否启用中间件

    Returns:
        更新后的状态字典
    """
    # 1️⃣ 消息过滤 (middlewareV1 - 保留3条human, 3条ai)
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.REVIEWER,
            phase_name="review"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    # 2️⃣ 构建输入消息 (包含完整上下文)
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
        "review": ai_output,
        "messages": new_messages,
        "current_phase": "review",
        "review_completed": True,
        "iteration": state.iteration + 1,
    }

    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="review",
            phase_name="review"
        )
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

