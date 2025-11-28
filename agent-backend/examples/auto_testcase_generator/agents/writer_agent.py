"""用例编写智能体 - 编写可执行的测试用例"""
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from ..middleware.adapters import MessageFilterMiddleware, StateSyncMiddleware, HumanInTheLoopMiddleware
from ..middleware.config import TestCaseAgentFilterConfig
from ..models import TestCaseState


WriterProgressHook = Callable[[Dict[str, Any]], Awaitable[None]]


def _split_testcase_chunks(output: str) -> List[str]:
    """将输出按段落拆成多个 chunk"""
    normalized = output.strip()
    if not normalized:
        return []
    segments = [segment.strip() for segment in normalized.split("\n\n") if segment.strip()]
    return segments or [normalized]


def create_writer_agent(model: BaseChatModel):
    """创建用例编写智能体"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_WRITER_SYSTEM_MESSAGE_ORIGINAL.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        name="writer",
        state_schema=TestCaseState,
    )

    return agent


def _truncate_text(text: str, max_chars: int = 1500) -> str:
    """截断文本，保留关键信息"""
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... (已截断，完整内容见测试点)"


async def run_writer(
    agent,
    state: TestCaseState,
    enable_middleware: bool = True,
    enable_human_review: bool = False,
    progress_hook: Optional[WriterProgressHook] = None,
) -> Dict[str, Any]:
    """运行用例编写智能体 (支持 chunk 级别的进度回调)"""
    if enable_middleware:
        filter_middleware = MessageFilterMiddleware(
            filter_config=TestCaseAgentFilterConfig.WRITER,
            phase_name="generate",
        )
        filter_updates = filter_middleware(state.__dict__)
        for key, value in filter_updates.items():
            setattr(state, key, value)

    # 截断需求分析，避免上下文过长（测试点已包含关键信息）
    analysis_summary = _truncate_text(state.analysis, max_chars=1500)

    user_message = f"""请基于以下信息编写测试用例:

## 原始需求
{state.requirement}

## 需求分析摘要
{analysis_summary}

## 测试点设计
{state.test_points}

请编写完整的{state.test_type}测试用例代码。"""

    if state.review and state.iteration > 0:
        user_message += f"\n\n## 上一轮评审意见\n{state.review}\n\n请根据评审意见优化测试用例。"

    response = await agent.ainvoke({
        "messages": state.messages + [HumanMessage(content=user_message)]
    })

    ai_output = response["messages"][-1].content if response.get("messages") else ""

    if enable_human_review:
        human_middleware = HumanInTheLoopMiddleware(interrupt_after=True)
        approved = human_middleware.get_approval(state.__dict__, ai_output)
        if not approved:
            print("❌ 人工审核未通过,跳过此次生成")
            return {}

    new_messages = state.messages + [
        HumanMessage(content=user_message),
        AIMessage(content=ai_output),
    ]
    state.messages = new_messages

    chunk_texts = _split_testcase_chunks(ai_output)
    if not chunk_texts:
        chunk_texts = [ai_output.strip()]
    total_chunks = len(chunk_texts)
    assembled_chunks: List[str] = []

    for idx, chunk_text in enumerate(chunk_texts, start=1):
        assembled_chunks.append(chunk_text)
        chunk_payload = {
            "writer_chunks": list(assembled_chunks),
            "writer_total_chunks": total_chunks,
            "writer_current_chunk": idx,
            "writer_progress": idx / total_chunks if total_chunks else 0.0,
            "writer_last_chunk": chunk_text,
            "testcases": "\n\n".join(assembled_chunks).strip(),
        }
        if progress_hook:
            try:
                await progress_hook(chunk_payload)
            except Exception as exc:  # pragma: no cover
                print(f"⚠️ Writer progress hook 失败: {exc}")

    final_testcases = "\n\n".join(assembled_chunks).strip()
    updates: Dict[str, Any] = {
        "testcases": final_testcases,
        "writer_chunks": list(assembled_chunks),
        "writer_total_chunks": total_chunks,
        "writer_current_chunk": total_chunks,
        "writer_progress": 1.0 if total_chunks else 0.0,
        "writer_last_chunk": assembled_chunks[-1] if assembled_chunks else "",
        "messages": new_messages,
        "current_phase": "generate",
        "generate_completed": True,
    }

    if enable_middleware:
        sync_middleware = StateSyncMiddleware(
            save_to_field="testcases",
            phase_name="generate",
        )
        temp_state = {**state.__dict__, "messages": new_messages, "testcases": final_testcases}
        sync_updates = sync_middleware(temp_state)
        updates.update(sync_updates)

    return updates
