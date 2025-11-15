"""用例编写智能体 - 编写可执行的测试用例"""
from pathlib import Path
from typing import Dict, Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware, HumanInTheLoopMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


def create_writer_agent(model: BaseChatModel):
    """创建用例编写智能体
    
    职责:
    - 基于测试点设计编写具体测试用例
    - 生成可执行的测试代码
    - 确保用例覆盖所有测试点
    
    Args:
        model: 语言模型实例
        
    Returns:
        用例编写智能体
    """
    # 加载系统提示词
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_WRITER_SYSTEM_MESSAGE_ORIGINAL.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    # 创建智能体
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="writer",
        state_schema=TestCaseState,
    )
    
    return agent


async def run_writer(agent, state: TestCaseState, enable_middleware: bool = True,
                    enable_human_review: bool = False) -> Dict[str, Any]:
    """运行用例编写智能体

    Args:
        agent: 智能体实例
        state: 当前状态
        enable_middleware: 是否启用中间件
        enable_human_review: 是否启用人工审核

    Returns:
        更新后的状态字典
    """
    # 1️⃣ 消息过滤 (middlewareV1 - 保留2条human, 2条ai)
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.WRITER,
            phase_name="generate"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    # 2️⃣ 构建输入消息 (包含需求、分析、测试点)
    user_message = f"""请基于以下信息编写测试用例:

## 原始需求
{state.requirement}

## 需求分析
{state.analysis}

## 测试点设计
{state.test_points}

请编写完整的{state.test_type}测试用例代码。"""

    # 如果有评审意见,添加到消息中
    if state.review and state.iteration > 0:
        user_message += f"\n\n## 上一轮评审意见\n{state.review}\n\n请根据评审意见优化测试用例。"

    # 3️⃣ 调用智能体
    response = await agent.ainvoke({
        "messages": state.messages + [HumanMessage(content=user_message)]
    })

    # 4️⃣ 提取AI输出
    ai_output = response["messages"][-1].content if response.get("messages") else ""

    # 5️⃣ 人工审核 (可选)
    if enable_human_review:
        human_middleware = HumanInTheLoopMiddleware(interrupt_after=True)
        approved = human_middleware.get_approval(state.__dict__, ai_output)
        if not approved:
            print("❌ 人工审核未通过,跳过此次生成")
            return {}

    # 6️⃣ 更新消息历史
    new_messages = state.messages + [
        HumanMessage(content=user_message),
        AIMessage(content=ai_output)
    ]

    # 7️⃣ 状态同步 (middlewareV1)
    updates = {
        "testcases": ai_output,
        "messages": new_messages,
        "current_phase": "generate",
        "generate_completed": True,
    }

    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="testcases",
            phase_name="generate"
        )
        temp_state = {**state.__dict__, "messages": new_messages}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates

