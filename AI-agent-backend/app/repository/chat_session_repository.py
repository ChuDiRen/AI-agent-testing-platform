# Copyright (c) 2025 左岚. All rights reserved.
"""
聊天会话Repository
处理聊天会话的数据访问
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.entity.chat_session import ChatSession
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class ChatSessionRepository(BaseRepository[ChatSession]):
    """聊天会话Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, ChatSession)

    def get_by_session_id(self, session_id: str) -> Optional[ChatSession]:
        """根据会话ID获取会话"""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting chat session by session_id {session_id}: {str(e)}")
            raise

    def get_user_sessions(self, user_id: int, skip: int = 0, 
                         limit: int = 20) -> Tuple[List[ChatSession], int]:
        """获取用户的聊天会话列表"""
        try:
            query = self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            )
            
            total = query.count()
            
            sessions = query.order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
            
            return sessions, total
            
        except Exception as e:
            logger.error(f"Error getting user sessions for user {user_id}: {str(e)}")
            raise

    def count_user_sessions(self, user_id: int) -> int:
        """统计用户的会话数量"""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
        except Exception as e:
            logger.error(f"Error counting user sessions for user {user_id}: {str(e)}")
            raise

    def get_sessions_by_model(self, model_id: int, skip: int = 0, 
                             limit: int = 20) -> Tuple[List[ChatSession], int]:
        """获取使用特定模型的会话列表"""
        try:
            query = self.db.query(ChatSession).filter(
                ChatSession.large_model_id == model_id
            )
            
            total = query.count()
            
            sessions = query.order_by(desc(ChatSession.created_at)).offset(skip).limit(limit).all()
            
            return sessions, total
            
        except Exception as e:
            logger.error(f"Error getting sessions by model {model_id}: {str(e)}")
            raise

    def search_sessions(self, user_id: int, keyword: Optional[str] = None,
                       model_id: Optional[int] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       skip: int = 0, limit: int = 20) -> Tuple[List[ChatSession], int]:
        """搜索聊天会话"""
        try:
            query = self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            )
            
            # 关键词搜索
            if keyword:
                query = query.filter(
                    ChatSession.title.contains(keyword)
                )
            
            # 模型筛选
            if model_id:
                query = query.filter(ChatSession.large_model_id == model_id)
            
            # 时间范围筛选
            if start_date:
                query = query.filter(ChatSession.created_at >= start_date)
            if end_date:
                query = query.filter(ChatSession.created_at <= end_date)
            
            total = query.count()
            
            sessions = query.order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
            
            return sessions, total
            
        except Exception as e:
            logger.error(f"Error searching sessions: {str(e)}")
            raise

    def get_recent_sessions(self, user_id: int, limit: int = 10) -> List[ChatSession]:
        """获取用户最近的会话"""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(ChatSession.updated_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent sessions for user {user_id}: {str(e)}")
            raise

    def delete_user_sessions(self, user_id: int) -> int:
        """删除用户的所有会话"""
        try:
            deleted_count = self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Deleted {deleted_count} sessions for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting user sessions for user {user_id}: {str(e)}")
            self.db.rollback()
            raise

    def get_session_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取会话统计信息"""
        try:
            query = self.db.query(ChatSession)
            
            if user_id:
                query = query.filter(ChatSession.user_id == user_id)
            
            total_sessions = query.count()
            
            # 今日新增会话
            today = datetime.now().date()
            today_sessions = query.filter(
                ChatSession.created_at >= today
            ).count()
            
            # 本周新增会话
            week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = week_ago.replace(day=week_ago.day - 7)
            week_sessions = query.filter(
                ChatSession.created_at >= week_ago
            ).count()
            
            # 按模型统计
            model_stats = self.db.query(
                ChatSession.large_model_id,
                self.db.func.count(ChatSession.id).label('count')
            ).group_by(ChatSession.large_model_id).all()
            
            return {
                "total_sessions": total_sessions,
                "today_sessions": today_sessions,
                "week_sessions": week_sessions,
                "model_stats": [{"model_id": stat[0], "count": stat[1]} for stat in model_stats]
            }
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {str(e)}")
            raise
