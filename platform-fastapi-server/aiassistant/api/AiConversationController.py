import json
import logging
from datetime import datetime
from typing import AsyncGenerator

from core.AiStreamService import AiStreamService
from core.ConversationService import ConversationService
from core.PromptService import PromptService
from core.StreamTestCaseParser import StreamTestCaseParser
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import select, Session
from sse_starlette.sse import EventSourceResponse

from ..model.AiConversation import AiConversation
from ..model.AiMessage import AiMessage
from ..model.AiModel import AiModel
from ..schemas.ai_conversation_schema import AiConversationCreate, AiConversationResponse, AiConversationListResponse
from ..schemas.ai_message_schema import MessageStreamRequest, AiMessageResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/AiConversation", tags=["AI对话"])


@router.post("/create", response_model=AiConversationResponse, summary="创建AI对话会话")
async def create_conversation(req: AiConversationCreate, session: Session = Depends(get_session), current_user = Depends(None)):
    """创建新对话会话"""
    try:
        model = session.get(AiModel, req.model_id)
        if not model or not model.is_enabled:
            return respModel.error_resp("模型不存在或已禁用")
        conversation = AiConversation(
            user_id=current_user.id if current_user else 1,
            session_title=req.session_title or f"新对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model_id=req.model_id, test_type=req.test_type, project_id=req.project_id, status="active"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return AiConversationResponse.model_validate(conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return respModel.error_resp("创建对话失败")


@router.get("/list", response_model=AiConversationListResponse, summary="获取用户对话列表")
async def list_conversations(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), session: Session = Depends(get_session), current_user = Depends(None)):
    """获取用户的对话列表"""
    try:
        user_id = current_user.id if current_user else 1
        query = select(AiConversation).where(AiConversation.user_id == user_id).order_by(AiConversation.update_time.desc())
        total = session.exec(select(AiConversation).where(AiConversation.user_id == user_id)).all()
        conversations = session.exec(query.offset((page - 1) * page_size).limit(page_size)).all()
        items = [AiConversationResponse.model_validate(c) for c in conversations]
        return AiConversationListResponse(total=len(total), items=items)
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        return respModel.error_resp("获取对话列表失败")


@router.get("/{conversation_id}/messages", summary="获取对话的所有消息")
async def get_messages(conversation_id: int, session: Session = Depends(get_session)):
    """获取对话的所有消息"""
    try:
        messages = session.exec(select(AiMessage).where(AiMessage.conversation_id == conversation_id).order_by(AiMessage.create_time)).all()
        return {"data": [AiMessageResponse.model_validate(m) for m in messages]}
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        return respModel.error_resp("获取消息失败")


@router.post("/chat", summary="AI流式对话接口(SSE)")
async def chat_stream(req: MessageStreamRequest, session: Session = Depends(get_session), current_user = Depends(None)):
    """流式对话接口（核心）- 使用SSE推送实时生成的内容"""
    async def _event_generator() -> AsyncGenerator[str, None]:
        parser, full_response, test_cases = StreamTestCaseParser(), "", []
        try:
            user_message = AiMessage(conversation_id=req.conversation_id, role="user", content=req.user_message, message_type="text")
            session.add(user_message)
            session.commit()
            conversation = session.get(AiConversation, req.conversation_id)
            if not conversation:
                yield f"data: {json.dumps({'type': 'error', 'content': '对话不存在'})}\n\n"
                return
            model = session.get(AiModel, req.model_id)
            if not model or not model.is_enabled:
                yield f"data: {json.dumps({'type': 'error', 'content': '模型不可用'})}\n\n"
                return
            context = ConversationService.build_context(session, req.conversation_id) if req.include_context else []
            system_prompt = PromptService.build_system_message(req.test_type or "API", req.case_count)
            messages = [system_prompt] + context + [{"role": "user", "content": req.user_message}]
            async for chunk in AiStreamService.call_ai_stream(model.model_code, model.api_key, model.api_url, messages, temperature=0.7, max_tokens=req.max_tokens):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                test_case = parser.parse_chunk(chunk)
                if test_case:
                    test_cases.append(test_case)
                    yield f"data: {json.dumps({'type': 'testcase', 'data': test_case})}\n\n"
            final_case = parser.flush()
            if final_case:
                test_cases.append(final_case)
                yield f"data: {json.dumps({'type': 'testcase', 'data': final_case})}\n\n"
            ai_message = AiMessage(conversation_id=req.conversation_id, role="assistant", content=full_response, message_type="testcase", test_cases_json=json.dumps(test_cases, ensure_ascii=False))
            session.add(ai_message)
            conversation.message_count += 2
            conversation.test_case_count += len(test_cases)
            conversation.update_time = datetime.now()
            conversation.last_message_time = datetime.now()
            session.add(conversation)
            session.commit()
            yield f"data: {json.dumps({'type': 'done', 'message_id': ai_message.id, 'test_case_count': len(test_cases)})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        # ✅ 修复Session管理：移除手动关闭,由FastAPI依赖注入自动管理
    return EventSourceResponse(_event_generator(), media_type="text/event-stream")


@router.delete("/{conversation_id}", summary="删除对话会话")
async def delete_conversation(conversation_id: int, session: Session = Depends(get_session), current_user = Depends(None)):
    """删除对话"""
    try:
        conversation = session.get(AiConversation, conversation_id)
        if not conversation:
            return respModel.error_resp("对话不存在")
        if conversation.user_id != (current_user.id if current_user else 1):
            return respModel.error_resp("无权限删除此对话")
        conversation.status = "deleted"
        session.add(conversation)
        session.commit()
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return respModel.error_resp("删除对话失败")


@router.put("/{conversation_id}/title", summary="更新对话标题")
async def update_title(conversation_id: int, title: str = Query(..., max_length=200), session: Session = Depends(get_session), current_user = Depends(None)):
    """更新对话标题"""
    try:
        conversation = session.get(AiConversation, conversation_id)
        if not conversation:
            return respModel.error_resp("对话不存在")
        conversation.session_title = title
        conversation.update_time = datetime.now()
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return AiConversationResponse.model_validate(conversation)
    except Exception as e:
        logger.error(f"Error updating title: {str(e)}")
        return respModel.error_resp("更新标题失败")
