"""测试点设计智能体 - 设计全面的测试点"""
from pathlib import Path
from typing import Dict, Any
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from ..middleware.config import TestCaseAgentFilterConfig
from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware, DynamicPromptMiddleware
from ..models import TestCaseState


def create_test_point_designer_agent(model: BaseChatModel):
    """创建测试点设计智能体
    
    职责:
    - 基于需求分析结果设计测试点
    - 覆盖正常、异常、边界场景
    - 为每个测试点定义验证要点
    
    Args:
        model: 语言模型实例
        
    Returns:
        测试点设计智能体
    """
    # 加载系统提示词
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_TEST_POINT_DESIGNER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="test_point_designer",
        state_schema=TestCaseState,
    )
    
    return agent


async def run_test_point_designer(agent, state: TestCaseState, enable_middleware: bool = True) -> Dict[str, Any]:
    """运行测试点设计智能体

    Args:
        agent: 智能体实例
        state: 当前状态
        enable_middleware: 是否启用中间件

    Returns:
        更新后的状态字典
    """
    # 1️⃣ 消息过滤 (middlewareV1 - 保留2条human, 1条ai)
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.TEST_POINT_DESIGNER,
            phase_name="design"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    # 2️⃣ 动态提示词注入 (middlewareV1 - 自动注入 analysis)
    user_message = f"""请基于以下信息设计测试点:

## 原始需求
{state.requirement}

## 需求分析结果
{state.analysis}

请设计全面的测试点,覆盖正常、异常、边界场景。"""

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
        "test_points": ai_output,
        "messages": new_messages,
        "current_phase": "design",
        "design_completed": True,
    }

    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="test_points",
            phase_name="design"
        )
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

