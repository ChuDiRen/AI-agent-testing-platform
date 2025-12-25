"""用例编写智能体"""
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware, HumanInTheLoopMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


WriterProgressHook = Callable[[Dict[str, Any]], Awaitable[None]]


def _split_testcase_chunks(output: str) -> List[str]:
    """output -> chunks"""
    normalized = output.strip()
    if not normalized:
        return []
    return [s.strip() for s in normalized.split("\n\n") if s.strip()] or [normalized]


def create_writer_agent(model: BaseChatModel, summarization_model: BaseChatModel = None):
    """创建用例编写智能体 - 带上下文压缩"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_WRITER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')

    middleware = []
    if summarization_model:
        middleware.append(SummarizationMiddleware(
            model=summarization_model,
            max_tokens_before_summary=6000,
            messages_to_keep=15,
        ))

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="writer",
        state_schema=TestCaseState,
        middleware=middleware,
    )

    return agent


async def run_writer(
    agent, state: TestCaseState, enable_middleware: bool = True,
    enable_human_review: bool = False, progress_hook: Optional[WriterProgressHook] = None,
) -> Dict[str, Any]:
    """运行用例编写"""
    # 消息过滤中间件
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.WRITER,
            phase_name="generate"
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    user_message = f"""请基于以下信息编写测试用例:

## 原始需求
{state.requirement}

## 需求分析
{state.analysis}

## 测试点设计
{state.test_points}

请编写完整的{state.test_type}测试用例。"""

    if state.review and state.iteration > 0:
        user_message += f"\n\n## 上一轮评审意见\n{state.review}\n\n请根据评审意见优化测试用例。"

    response = await agent.ainvoke({"messages": state.messages + [HumanMessage(content=user_message)]})
    ai_output = response["messages"][-1].content if response.get("messages") else ""

    if enable_human_review:
        human_middleware = HumanInTheLoopMiddleware(interrupt_after=True)
        if not human_middleware.get_approval(state.__dict__, ai_output):
            return {}

    new_messages = state.messages + [HumanMessage(content=user_message), AIMessage(content=ai_output)]

    # 进度回调
    chunk_texts = _split_testcase_chunks(ai_output)
    if progress_hook and chunk_texts:
        await progress_hook({
            "writer_progress": 1.0,
            "writer_current_chunk": len(chunk_texts),
            "writer_total_chunks": len(chunk_texts),
            "testcases": ai_output.strip(),
        })

    updates = {
        "testcases": ai_output.strip(),
        "messages": new_messages,
        "current_phase": "generate",
        "generate_completed": True,
    }

    # 状态同步中间件
    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="testcases",
            phase_name="generate"
        )
        temp_state = {**state.__dict__, "messages": new_messages, "testcases": ai_output.strip()}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates
