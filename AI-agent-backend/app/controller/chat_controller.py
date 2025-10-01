"""
AI聊天Controller
处理AI聊天相关的HTTP请求
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import json
import asyncio

from app.service.ai_model_service import AIModelService
from app.service.chat_session_service import ChatSessionService
from app.dto.base import Success, Fail
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["AI聊天"])


# 请求模型
class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色: system, user, assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    large_model_id: int = Field(..., description="AI模型ID")
    messages: List[ChatMessage] = Field(..., description="聊天消息列表")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="最大令牌数")
    stream: bool = Field(False, description="是否流式响应")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatSessionCreateRequest(BaseModel):
    """创建聊天会话请求"""
    title: Optional[str] = Field(None, description="会话标题")
    large_model_id: int = Field(..., description="AI模型ID")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


class ChatSessionUpdateRequest(BaseModel):
    """更新聊天会话请求"""
    title: Optional[str] = Field(None, description="会话标题")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


@router.post("/sessions", summary="创建聊天会话")
async def create_chat_session(
    request: ChatSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新的聊天会话"""
    try:
        chat_service = ChatSessionService(db)
        session = await chat_service.create_session(
            user_id=current_user.user_id,
            large_model_id=request.large_model_id,
            title=request.title,
            system_prompt=request.system_prompt
        )
        
        return Success(data=session, msg="会话创建成功")
        
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        return Fail(msg=f"创建会话失败: {str(e)}")


@router.get("/sessions", summary="获取用户聊天会话列表")
async def get_chat_sessions(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户的聊天会话列表"""
    try:
        chat_service = ChatSessionService(db)
        sessions = await chat_service.get_user_sessions(
            user_id=current_user.user_id,
            page=page,
            page_size=page_size
        )
        
        return Success(data=sessions, msg="获取会话列表成功")
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        return Fail(msg=f"获取会话列表失败: {str(e)}")


@router.get("/sessions/{session_id}", summary="获取聊天会话详情")
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取聊天会话详情"""
    try:
        chat_service = ChatSessionService(db)
        session = await chat_service.get_session_detail(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not session:
            return Fail(code=404, msg="会话不存在")
        
        return Success(data=session, msg="获取会话详情成功")
        
    except Exception as e:
        logger.error(f"Error getting chat session {session_id}: {str(e)}")
        return Fail(msg=f"获取会话详情失败: {str(e)}")


@router.put("/sessions/{session_id}", summary="更新聊天会话")
async def update_chat_session(
    session_id: str,
    request: ChatSessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新聊天会话"""
    try:
        chat_service = ChatSessionService(db)
        session = await chat_service.update_session(
            session_id=session_id,
            user_id=current_user.user_id,
            title=request.title,
            system_prompt=request.system_prompt
        )
        
        if not session:
            return Fail(code=404, msg="会话不存在")
        
        return Success(data=session, msg="会话更新成功")
        
    except Exception as e:
        logger.error(f"Error updating chat session {session_id}: {str(e)}")
        return Fail(msg=f"更新会话失败: {str(e)}")


@router.delete("/sessions/{session_id}", summary="删除聊天会话")
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除聊天会话"""
    try:
        chat_service = ChatSessionService(db)
        success = await chat_service.delete_session(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not success:
            return Fail(code=404, msg="会话不存在")
        
        return Success(msg="会话删除成功")
        
    except Exception as e:
        logger.error(f"Error deleting chat session {session_id}: {str(e)}")
        return Fail(msg=f"删除会话失败: {str(e)}")


@router.post("/", summary="发送聊天消息")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """发送聊天消息"""
    try:
        ai_model_service = AIModelService(db)
        chat_service = ChatSessionService(db)
        
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 如果有会话ID，保存消息到会话
        if request.session_id:
            await chat_service.add_message_to_session(
                session_id=request.session_id,
                user_id=current_user.user_id,
                role="user",
                content=request.messages[-1].content  # 最后一条用户消息
            )
        
        if request.stream:
            # 流式响应
            async def generate():
                try:
                    response_content = ""
                    async for chunk in await ai_model_service.chat_with_model(
                        model_id=request.large_model_id,
                        messages=messages,
                        user_id=current_user.user_id,
                        stream=True,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                    ):
                        response_content += chunk
                        yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n"
                    
                    # 保存AI响应到会话
                    if request.session_id:
                        await chat_service.add_message_to_session(
                            session_id=request.session_id,
                            user_id=current_user.user_id,
                            role="assistant",
                            content=response_content
                        )
                    
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in streaming chat: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # 完整响应
            response = await ai_model_service.chat_with_model(
                model_id=request.large_model_id,
                messages=messages,
                user_id=current_user.user_id,
                stream=False,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # 保存AI响应到会话
            if request.session_id:
                await chat_service.add_message_to_session(
                    session_id=request.session_id,
                    user_id=current_user.user_id,
                    role="assistant",
                    content=response.content
                )
            
            return Success(data={
                "content": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time": response.response_time,
                "metadata": response.metadata
            }, msg="聊天成功")
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return Fail(msg=f"聊天失败: {str(e)}")


@router.get("/sessions/{session_id}/messages", summary="获取会话消息历史")
async def get_session_messages(
    session_id: str,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取会话的消息历史"""
    try:
        chat_service = ChatSessionService(db)
        messages = await chat_service.get_session_messages(
            session_id=session_id,
            user_id=current_user.user_id,
            page=page,
            page_size=page_size
        )
        
        return Success(data=messages, msg="获取消息历史成功")
        
    except Exception as e:
        logger.error(f"Error getting session messages: {str(e)}")
        return Fail(msg=f"获取消息历史失败: {str(e)}")


@router.delete("/sessions/{session_id}/messages", summary="清空会话消息")
async def clear_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """清空会话的所有消息"""
    try:
        chat_service = ChatSessionService(db)
        success = await chat_service.clear_session_messages(
            session_id=session_id,
            user_id=current_user.user_id
        )
        
        if not success:
            return Fail(code=404, msg="会话不存在")
        
        return Success(msg="消息清空成功")
        
    except Exception as e:
        logger.error(f"Error clearing session messages: {str(e)}")
        return Fail(msg=f"清空消息失败: {str(e)}")
