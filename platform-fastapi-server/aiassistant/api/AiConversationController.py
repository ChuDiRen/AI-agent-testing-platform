from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import json
import logging
from typing import AsyncGenerator

from ..model.AiConversation import AiConversation
from ..model.AiMessage import AiMessage
from ..model.AiModel import AiModel
from ..schemas.ai_conversation_schema import (
    AiConversationCreate, AiConversationResponse, AiConversationListResponse
)
from ..schemas.ai_message_schema import MessageStreamRequest, AiMessageResponse
from core.database import get_session
from core.AiStreamService import AiStreamService
from core.ConversationService import ConversationService
from core.PromptService import PromptService
from core.StreamTestCaseParser import StreamTestCaseParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/AiConversation", tags=["AI对话"])


@router.post("/create", response_model=AiConversationResponse)
async def create_conversation(
    req: AiConversationCreate,
    session: Session = Depends(get_session),
    current_user = Depends(None)  # 实际使用时需要权限依赖
):
    """创建新对话会话"""
    try:
        # 验证模型存在
        model = session.get(AiModel, req.model_id)
        if not model or not model.is_enabled:
            raise HTTPException(status_code=400, detail="模型不存在或已禁用")
        
        # 创建对话
        conversation = AiConversation(
            user_id=current_user.id if current_user else 1,
            session_title=req.session_title or f"新对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model_id=req.model_id,
            test_type=req.test_type,
            project_id=req.project_id,
            status="active"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        return AiConversationResponse.model_validate(conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="创建对话失败")


@router.get("/list", response_model=AiConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user = Depends(None)
):
    """获取用户的对话列表"""
    try:
        # 分页查询
        query = select(AiConversation).where(
            AiConversation.user_id == (current_user.id if current_user else 1)
        ).order_by(AiConversation.update_time.desc())
        
        total = session.exec(select(AiConversation).where(
            AiConversation.user_id == (current_user.id if current_user else 1)
        )).all()
        
        conversations = session.exec(
            query.offset((page - 1) * page_size).limit(page_size)
        ).all()
        
        items = [AiConversationResponse.model_validate(c) for c in conversations]
        return AiConversationListResponse(total=len(total), items=items)
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="获取对话列表失败")


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    session: Session = Depends(get_session)
):
    """获取对话的所有消息"""
    try:
        messages = session.exec(
            select(AiMessage).where(
                AiMessage.conversation_id == conversation_id
            ).order_by(AiMessage.create_time)
        ).all()
        
        return {"data": [AiMessageResponse.model_validate(m) for m in messages]}
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="获取消息失败")


@router.post("/chat")
async def chat_stream(
    req: MessageStreamRequest,
    session: Session = Depends(get_session),
    current_user = Depends(None)
):
    """
    流式对话接口（核心）- 使用SSE推送实时生成的内容
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        parser = StreamTestCaseParser()
        full_response = ""
        test_cases = []
        
        try:
            # 1. 保存用户消息
            user_message = AiMessage(
                conversation_id=req.conversation_id,
                role="user",
                content=req.user_message,
                message_type="text"
            )
            session.add(user_message)
            session.commit()
            
            # 2. 获取对话记录和上下文
            conversation = session.get(AiConversation, req.conversation_id)
            if not conversation:
                yield f"data: {json.dumps({'type': 'error', 'content': '对话不存在'})}\n\n"
                return
            
            # 3. 获取AI模型
            model = session.get(AiModel, req.model_id)
            if not model or not model.is_enabled:
                yield f"data: {json.dumps({'type': 'error', 'content': '模型不可用'})}\n\n"
                return
            
            # 4. 构建消息上下文
            context = ConversationService.build_context(session, req.conversation_id) if req.include_context else []
            
            # 5. 构建系统提示词
            system_prompt = PromptService.build_system_message(req.test_type or "API", req.case_count)
            
            # 6. 组织最终的消息列表
            messages = [system_prompt] + context + [
                {"role": "user", "content": req.user_message}
            ]
            
            # 7. 流式调用AI
            async for chunk in AiStreamService.call_ai_stream(
                model.model_code,
                model.api_key,
                model.api_url,
                messages,
                temperature=0.7,
                max_tokens=req.max_tokens
            ):
                full_response += chunk
                
                # 推送文本块
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                
                # 实时解析测试用例
                test_case = parser.parse_chunk(chunk)
                if test_case:
                    test_cases.append(test_case)
                    yield f"data: {json.dumps({'type': 'testcase', 'data': test_case})}\n\n"
            
            # 8. 刷新最后的缓冲区
            final_case = parser.flush()
            if final_case:
                test_cases.append(final_case)
                yield f"data: {json.dumps({'type': 'testcase', 'data': final_case})}\n\n"
            
            # 9. 保存AI响应
            ai_message = AiMessage(
                conversation_id=req.conversation_id,
                role="assistant",
                content=full_response,
                message_type="testcase",
                test_cases_json=json.dumps(test_cases, ensure_ascii=False)
            )
            session.add(ai_message)
            
            # 更新对话统计
            conversation.message_count += 2  # user + assistant
            conversation.test_case_count += len(test_cases)
            conversation.update_time = datetime.now()
            conversation.last_message_time = datetime.now()
            session.add(conversation)
            session.commit()
            
            # 10. 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'message_id': ai_message.id, 'test_case_count': len(test_cases)})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            session.close()
    
    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(None)
):
    """删除对话"""
    try:
        conversation = session.get(AiConversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 验证权限
        if conversation.user_id != (current_user.id if current_user else 1):
            raise HTTPException(status_code=403, detail="无权限删除此对话")
        
        conversation.status = "deleted"
        session.add(conversation)
        session.commit()
        
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="删除对话失败")


@router.put("/{conversation_id}/title")
async def update_title(
    conversation_id: int,
    title: str = Query(..., max_length=200),
    session: Session = Depends(get_session),
    current_user = Depends(None)
):
    """更新对话标题"""
    try:
        conversation = session.get(AiConversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        conversation.session_title = title
        conversation.update_time = datetime.now()
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        return AiConversationResponse.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating title: {str(e)}")
        raise HTTPException(status_code=500, detail="更新标题失败")
