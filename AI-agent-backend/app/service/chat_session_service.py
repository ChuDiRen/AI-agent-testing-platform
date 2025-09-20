# Copyright (c) 2025 左岚. All rights reserved.
"""
聊天会话Service
处理聊天会话和消息管理的业务逻辑
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.entity.chat_session import ChatSession, ChatMessage
from app.repository.chat_session_repository import ChatSessionRepository
from app.repository.chat_message_repository import ChatMessageRepository
from app.core.logger import get_logger
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class ChatSessionService:
    """聊天会话服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = ChatSessionRepository(db)
        self.message_repo = ChatMessageRepository(db)
    
    async def create_session(self, user_id: int, large_model_id: int,
                           title: Optional[str] = None,
                           system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """创建聊天会话"""
        try:
            session_id = str(uuid.uuid4())

            # 如果没有提供标题，生成默认标题
            if not title:
                session_count = self.session_repo.count_user_sessions(user_id)
                title = f"聊天会话 {session_count + 1}"

            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                large_model_id=large_model_id,
                title=title,
                system_prompt=system_prompt
            )
            
            created_session = self.session_repo.create(session)
            
            logger.info(f"Created chat session {session_id} for user {user_id}")
            
            return {
                "session_id": created_session.session_id,
                "title": created_session.title,
                "large_model_id": created_session.large_model_id,
                "system_prompt": created_session.system_prompt,
                "created_at": created_session.created_at.isoformat(),
                "message_count": 0
            }
            
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise BusinessException(f"创建聊天会话失败: {str(e)}")
    
    async def get_user_sessions(self, user_id: int, page: int = 1, 
                              page_size: int = 20) -> Dict[str, Any]:
        """获取用户的聊天会话列表"""
        try:
            sessions, total = self.session_repo.get_user_sessions(
                user_id=user_id,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            session_list = []
            for session in sessions:
                # 获取最后一条消息
                last_message = self.message_repo.get_last_message(session.session_id)
                message_count = self.message_repo.count_session_messages(session.session_id)
                
                session_list.append({
                    "session_id": session.session_id,
                    "title": session.title,
                    "large_model_id": session.large_model_id,
                    "system_prompt": session.system_prompt,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": message_count,
                    "last_message": {
                        "content": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
                        "role": last_message.role if last_message else None,
                        "created_at": last_message.created_at.isoformat() if last_message else None
                    } if last_message else None
                })
            
            return {
                "sessions": session_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            raise BusinessException(f"获取会话列表失败: {str(e)}")
    
    async def get_session_detail(self, session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """获取聊天会话详情"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                return None
            
            message_count = self.message_repo.count_session_messages(session_id)
            
            return {
                "session_id": session.session_id,
                "title": session.title,
                "large_model_id": session.large_model_id,
                "system_prompt": session.system_prompt,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": message_count
            }
            
        except Exception as e:
            logger.error(f"Error getting session detail: {str(e)}")
            raise BusinessException(f"获取会话详情失败: {str(e)}")
    
    async def update_session(self, session_id: str, user_id: int,
                           title: Optional[str] = None,
                           system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """更新聊天会话"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                return None
            
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if system_prompt is not None:
                update_data["system_prompt"] = system_prompt
            
            if update_data:
                updated_session = self.session_repo.update(session.id, update_data)
                
                return {
                    "session_id": updated_session.session_id,
                    "title": updated_session.title,
                    "model_id": updated_session.model_id,
                    "system_prompt": updated_session.system_prompt,
                    "created_at": updated_session.created_at.isoformat(),
                    "updated_at": updated_session.updated_at.isoformat()
                }
            
            return await self.get_session_detail(session_id, user_id)
            
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise BusinessException(f"更新会话失败: {str(e)}")
    
    async def delete_session(self, session_id: str, user_id: int) -> bool:
        """删除聊天会话"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                return False
            
            # 先删除所有消息
            self.message_repo.delete_session_messages(session_id)
            
            # 再删除会话
            self.session_repo.delete(session.id)
            
            logger.info(f"Deleted chat session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            raise BusinessException(f"删除会话失败: {str(e)}")
    
    async def add_message_to_session(self, session_id: str, user_id: int,
                                   role: str, content: str,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """向会话添加消息"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                raise BusinessException("会话不存在或无权限")
            
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            
            created_message = self.message_repo.create(message)
            
            # 更新会话的更新时间
            self.session_repo.update(session.id, {"updated_at": datetime.now()})
            
            return {
                "id": created_message.id,
                "session_id": created_message.session_id,
                "role": created_message.role,
                "content": created_message.content,
                "metadata": created_message.message_metadata,
                "created_at": created_message.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding message to session: {str(e)}")
            raise BusinessException(f"添加消息失败: {str(e)}")
    
    async def get_session_messages(self, session_id: str, user_id: int,
                                 page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """获取会话消息历史"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                raise BusinessException("会话不存在或无权限")
            
            messages, total = self.message_repo.get_session_messages(
                session_id=session_id,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            message_list = []
            for message in messages:
                message_list.append({
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "metadata": message.message_metadata,
                    "created_at": message.created_at.isoformat()
                })
            
            return {
                "messages": message_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"Error getting session messages: {str(e)}")
            raise BusinessException(f"获取消息历史失败: {str(e)}")
    
    async def clear_session_messages(self, session_id: str, user_id: int) -> bool:
        """清空会话消息"""
        try:
            session = self.session_repo.get_by_session_id(session_id)
            
            if not session or session.user_id != user_id:
                return False
            
            self.message_repo.delete_session_messages(session_id)
            
            logger.info(f"Cleared messages for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session messages: {str(e)}")
            raise BusinessException(f"清空消息失败: {str(e)}")
