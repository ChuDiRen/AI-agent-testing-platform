"""
聊天功能模块API
提供AI对话的会话管理和消息功能
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.chat_session_service import ChatSessionService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/sessions", summary="获取聊天会话列表")
@log_user_action(action="查看", resource_type="聊天管理", description="查看会话列表")
async def get_chat_session_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的聊天会话列表"""
    try:
        chat_service = ChatSessionService(db)

        # 获取会话列表
        sessions, total = await chat_service.get_user_sessions(
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        session_list = []
        for session in sessions:
            session_data = {
                "id": session.id,
                "title": session.title,
                "agent_id": session.agent_id,
                "agent_name": session.agent_name if hasattr(session, 'agent_name') else "",
                "last_message": session.last_message or "",
                "message_count": session.message_count or 0,
                "created_at": session.create_time.strftime("%Y-%m-%d %H:%M:%S") if session.create_time else "",
                "updated_at": session.update_time.strftime("%Y-%m-%d %H:%M:%S") if session.update_time else ""
            }
            session_list.append(session_data)

        response_data = {
            "items": session_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取会话列表失败: {str(e)}")


@router.post("/sessions", summary="创建聊天会话")
@log_user_action(action="创建", resource_type="聊天管理", description="创建聊天会话")
async def create_chat_session(
    agent_id: int = Body(..., description="AI代理ID"),
    title: Optional[str] = Body(None, description="会话标题"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    try:
        chat_service = ChatSessionService(db)

        # 创建会话
        new_session = await chat_service.create_session(
            user_id=current_user.id,
            agent_id=agent_id,
            title=title
        )

        session_data = {
            "id": new_session.id,
            "title": new_session.title,
            "agent_id": new_session.agent_id,
            "created_at": new_session.create_time.strftime("%Y-%m-%d %H:%M:%S") if new_session.create_time else ""
        }

        return Success(data=session_data, msg="会话创建成功")

    except Exception as e:
        return Fail(msg=f"创建会话失败: {str(e)}")


@router.get("/sessions/{session_id}", summary="获取会话详情")
@log_user_action(action="查看", resource_type="聊天管理", description="查看会话详情")
async def get_chat_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天会话详情"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权访问此会话")

        session_data = {
            "id": session.id,
            "title": session.title,
            "agent_id": session.agent_id,
            "agent_name": session.agent_name if hasattr(session, 'agent_name') else "",
            "message_count": session.message_count or 0,
            "created_at": session.create_time.strftime("%Y-%m-%d %H:%M:%S") if session.create_time else "",
            "updated_at": session.update_time.strftime("%Y-%m-%d %H:%M:%S") if session.update_time else ""
        }

        return Success(data=session_data)

    except Exception as e:
        return Fail(msg=f"获取会话详情失败: {str(e)}")


@router.delete("/sessions/{session_id}", summary="删除聊天会话")
@log_user_action(action="删除", resource_type="聊天管理", description="删除聊天会话")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权删除此会话")

        # 删除会话
        await chat_service.delete_session(session_id)

        return Success(msg="会话删除成功")

    except Exception as e:
        return Fail(msg=f"删除会话失败: {str(e)}")


@router.get("/sessions/{session_id}/messages", summary="获取会话消息")
@log_user_action(action="查看", resource_type="聊天管理", description="查看会话消息")
async def get_chat_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天会话的消息列表"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权访问此会话")

        # 获取消息列表
        messages, total = await chat_service.get_session_messages(
            session_id=session_id,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        message_list = []
        for message in messages:
            message_data = {
                "id": message.id,
                "session_id": message.session_id,
                "role": message.role,  # user 或 assistant
                "content": message.content,
                "metadata": message.metadata or {},
                "created_at": message.create_time.strftime("%Y-%m-%d %H:%M:%S") if message.create_time else ""
            }
            message_list.append(message_data)

        response_data = {
            "items": message_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取消息列表失败: {str(e)}")


@router.post("/sessions/{session_id}/messages", summary="发送消息")
@log_user_action(action="发送消息", resource_type="聊天管理", description="发送聊天消息")
async def send_chat_message(
    session_id: int,
    content: str = Body(..., description="消息内容"),
    agent_id: Optional[int] = Body(None, description="AI代理ID"),
    metadata: Optional[Dict[str, Any]] = Body(default={}, description="消息元数据"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """向聊天会话发送消息并获取AI回复"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权访问此会话")

        # 发送消息并获取AI回复
        user_message, ai_message = await chat_service.send_message(
            session_id=session_id,
            user_id=current_user.id,
            content=content,
            agent_id=agent_id or session.agent_id,
            metadata=metadata
        )

        # 构建响应数据
        response_data = {
            "user_message": {
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.content,
                "created_at": user_message.create_time.strftime("%Y-%m-%d %H:%M:%S") if user_message.create_time else ""
            },
            "ai_message": {
                "id": ai_message.id,
                "role": ai_message.role,
                "content": ai_message.content,
                "created_at": ai_message.create_time.strftime("%Y-%m-%d %H:%M:%S") if ai_message.create_time else ""
            } if ai_message else None
        }

        return Success(data=response_data, msg="消息发送成功")

    except Exception as e:
        return Fail(msg=f"发送消息失败: {str(e)}")


@router.put("/sessions/{session_id}", summary="更新会话信息")
@log_user_action(action="更新", resource_type="聊天管理", description="更新会话信息")
async def update_chat_session(
    session_id: int,
    title: Optional[str] = Body(None, description="会话标题"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新聊天会话信息"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权修改此会话")

        # 更新会话
        await chat_service.update_session(
            session_id=session_id,
            title=title
        )

        return Success(msg="会话更新成功")

    except Exception as e:
        return Fail(msg=f"更新会话失败: {str(e)}")


@router.post("/clear", summary="清除聊天历史")
@log_user_action(action="清除历史", resource_type="聊天管理", description="清除聊天历史")
async def clear_chat_history(
    session_id: Optional[int] = Body(None, description="会话ID，不提供则清除所有会话"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清除聊天历史记录"""
    try:
        chat_service = ChatSessionService(db)

        if session_id:
            # 清除指定会话
            session = await chat_service.get_session_by_id(session_id)
            if not session:
                return Fail(msg="会话不存在")
            
            if session.user_id != current_user.id:
                return Fail(msg="无权操作此会话")

            cleared_count = await chat_service.clear_session_messages(session_id)
            message = f"会话消息清除成功，共清除 {cleared_count} 条消息"
        else:
            # 清除用户所有会话
            cleared_count = await chat_service.clear_user_chat_history(current_user.id)
            message = f"聊天历史清除成功，共清除 {cleared_count} 条消息"

        return Success(data={"cleared_count": cleared_count}, msg=message)

    except Exception as e:
        return Fail(msg=f"清除聊天历史失败: {str(e)}")


@router.delete("/sessions/{session_id}/messages/{message_id}", summary="删除消息")
@log_user_action(action="删除消息", resource_type="聊天管理", description="删除聊天消息")
async def delete_chat_message(
    session_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除指定的聊天消息"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权操作此会话")

        # 删除消息
        success = await chat_service.delete_message(message_id, session_id)
        
        if success:
            return Success(msg="消息删除成功")
        else:
            return Fail(msg="消息不存在或已被删除")

    except Exception as e:
        return Fail(msg=f"删除消息失败: {str(e)}")


@router.post("/sessions/{session_id}/regenerate", summary="重新生成回复")
@log_user_action(action="重新生成", resource_type="聊天管理", description="重新生成AI回复")
async def regenerate_response(
    session_id: int,
    message_id: int = Body(..., description="要重新生成回复的消息ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新生成AI回复"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权操作此会话")

        # 重新生成回复
        new_message = await chat_service.regenerate_response(
            session_id=session_id,
            message_id=message_id,
            agent_id=session.agent_id
        )

        response_data = {
            "id": new_message.id,
            "role": new_message.role,
            "content": new_message.content,
            "created_at": new_message.create_time.strftime("%Y-%m-%d %H:%M:%S") if new_message.create_time else ""
        }

        return Success(data=response_data, msg="回复重新生成成功")

    except Exception as e:
        return Fail(msg=f"重新生成回复失败: {str(e)}")


@router.get("/sessions/{session_id}/export", summary="导出会话记录")
@log_user_action(action="导出", resource_type="聊天管理", description="导出会话记录")
async def export_chat_session(
    session_id: int,
    format: str = Query("json", description="导出格式: json, txt, md"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出聊天会话记录"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权访问此会话")

        # 导出会话
        export_data = await chat_service.export_session(session_id, format)

        return Success(data=export_data, msg="会话导出成功")

    except Exception as e:
        return Fail(msg=f"导出会话失败: {str(e)}")


@router.get("/statistics", summary="获取聊天统计")
@log_user_action(action="查看统计", resource_type="聊天管理", description="查看聊天统计")
async def get_chat_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的聊天统计信息"""
    try:
        chat_service = ChatSessionService(db)
        
        # 获取统计数据
        statistics = await chat_service.get_user_chat_statistics(current_user.id)
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取聊天统计失败: {str(e)}")


@router.post("/sessions/{session_id}/share", summary="分享会话")
@log_user_action(action="分享", resource_type="聊天管理", description="分享聊天会话")
async def share_chat_session(
    session_id: int,
    share_type: str = Body("public", description="分享类型: public, private"),
    expires_at: Optional[str] = Body(None, description="过期时间"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分享聊天会话"""
    try:
        chat_service = ChatSessionService(db)

        # 验证会话归属
        session = await chat_service.get_session_by_id(session_id)
        if not session:
            return Fail(msg="会话不存在")
        
        if session.user_id != current_user.id:
            return Fail(msg="无权分享此会话")

        # 创建分享链接
        share_link = await chat_service.create_share_link(
            session_id=session_id,
            share_type=share_type,
            expires_at=expires_at
        )

        return Success(data={"share_link": share_link}, msg="会话分享链接创建成功")

    except Exception as e:
        return Fail(msg=f"分享会话失败: {str(e)}")


@router.get("/agents", summary="获取可用的聊天代理")
async def get_chat_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取可用于聊天的AI代理列表"""
    try:
        chat_service = ChatSessionService(db)
        
        # 获取聊天代理
        agents = await chat_service.get_available_chat_agents()
        
        return Success(data=agents)

    except Exception as e:
        return Fail(msg=f"获取聊天代理失败: {str(e)}")


@router.post("/sessions/search", summary="搜索会话")
@log_user_action(action="搜索", resource_type="聊天管理", description="搜索聊天会话")
async def search_chat_sessions(
    keyword: str = Body(..., description="搜索关键词"),
    agent_id: Optional[int] = Body(None, description="代理ID"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(20, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索聊天会话"""
    try:
        chat_service = ChatSessionService(db)

        # 搜索会话
        sessions, total = await chat_service.search_user_sessions(
            user_id=current_user.id,
            keyword=keyword,
            agent_id=agent_id,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        session_list = []
        for session in sessions:
            session_data = {
                "id": session.id,
                "title": session.title,
                "agent_id": session.agent_id,
                "agent_name": session.agent_name if hasattr(session, 'agent_name') else "",
                "last_message": session.last_message or "",
                "message_count": session.message_count or 0,
                "created_at": session.create_time.strftime("%Y-%m-%d %H:%M:%S") if session.create_time else "",
                "updated_at": session.update_time.strftime("%Y-%m-%d %H:%M:%S") if session.update_time else ""
            }
            session_list.append(session_data)

        response_data = {
            "items": session_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索会话失败: {str(e)}")
