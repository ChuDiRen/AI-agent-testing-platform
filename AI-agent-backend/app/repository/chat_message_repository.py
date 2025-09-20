# Copyright (c) 2025 左岚. All rights reserved.
"""
聊天消息Repository
处理聊天消息的数据访问
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from app.entity.chat_session import ChatMessage
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """聊天消息Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, ChatMessage)

    def get_session_messages(self, session_id: str, skip: int = 0, 
                           limit: int = 50) -> Tuple[List[ChatMessage], int]:
        """获取会话的消息列表"""
        try:
            query = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            )
            
            total = query.count()
            
            messages = query.order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
            
            return messages, total
            
        except Exception as e:
            logger.error(f"Error getting session messages for session {session_id}: {str(e)}")
            raise

    def get_last_message(self, session_id: str) -> Optional[ChatMessage]:
        """获取会话的最后一条消息"""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(desc(ChatMessage.created_at)).first()
            
        except Exception as e:
            logger.error(f"Error getting last message for session {session_id}: {str(e)}")
            raise

    def count_session_messages(self, session_id: str) -> int:
        """统计会话的消息数量"""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).count()
        except Exception as e:
            logger.error(f"Error counting session messages for session {session_id}: {str(e)}")
            raise

    def get_messages_by_role(self, session_id: str, role: str) -> List[ChatMessage]:
        """获取会话中特定角色的消息"""
        try:
            return self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.session_id == session_id,
                    ChatMessage.role == role
                )
            ).order_by(ChatMessage.created_at).all()
            
        except Exception as e:
            logger.error(f"Error getting messages by role {role} for session {session_id}: {str(e)}")
            raise

    def delete_session_messages(self, session_id: str) -> int:
        """删除会话的所有消息"""
        try:
            deleted_count = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Deleted {deleted_count} messages for session {session_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting session messages for session {session_id}: {str(e)}")
            self.db.rollback()
            raise

    def search_messages(self, session_id: str, keyword: str,
                       role: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       skip: int = 0, limit: int = 50) -> Tuple[List[ChatMessage], int]:
        """搜索会话中的消息"""
        try:
            query = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.session_id == session_id,
                    ChatMessage.content.contains(keyword)
                )
            )
            
            # 角色筛选
            if role:
                query = query.filter(ChatMessage.role == role)
            
            # 时间范围筛选
            if start_date:
                query = query.filter(ChatMessage.created_at >= start_date)
            if end_date:
                query = query.filter(ChatMessage.created_at <= end_date)
            
            total = query.count()
            
            messages = query.order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
            
            return messages, total
            
        except Exception as e:
            logger.error(f"Error searching messages in session {session_id}: {str(e)}")
            raise

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """获取会话的最近消息"""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting recent messages for session {session_id}: {str(e)}")
            raise

    def get_message_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取消息统计信息"""
        try:
            query = self.db.query(ChatMessage)
            
            if session_id:
                query = query.filter(ChatMessage.session_id == session_id)
            
            total_messages = query.count()
            
            # 按角色统计
            role_stats = self.db.query(
                ChatMessage.role,
                func.count(ChatMessage.id).label('count'),
                func.sum(ChatMessage.tokens).label('total_tokens'),
                func.sum(ChatMessage.cost).label('total_cost')
            ).group_by(ChatMessage.role)
            
            if session_id:
                role_stats = role_stats.filter(ChatMessage.session_id == session_id)
            
            role_stats = role_stats.all()
            
            # 今日消息数
            today = datetime.now().date()
            today_messages = query.filter(
                ChatMessage.created_at >= today
            ).count()
            
            # 总令牌数和费用
            token_cost_stats = query.with_entities(
                func.sum(ChatMessage.tokens).label('total_tokens'),
                func.sum(ChatMessage.cost).label('total_cost')
            ).first()
            
            return {
                "total_messages": total_messages,
                "today_messages": today_messages,
                "total_tokens": token_cost_stats.total_tokens or 0,
                "total_cost": token_cost_stats.total_cost or 0,
                "role_stats": [
                    {
                        "role": stat.role,
                        "count": stat.count,
                        "total_tokens": stat.total_tokens or 0,
                        "total_cost": stat.total_cost or 0
                    }
                    for stat in role_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting message statistics: {str(e)}")
            raise

    def get_conversation_context(self, session_id: str, limit: int = 20) -> List[ChatMessage]:
        """获取对话上下文（最近的消息）"""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(desc(ChatMessage.created_at)).limit(limit).all()[::-1]  # 反转顺序，最早的在前
            
        except Exception as e:
            logger.error(f"Error getting conversation context for session {session_id}: {str(e)}")
            raise

    def delete_old_messages(self, days: int = 30) -> int:
        """删除指定天数之前的消息"""
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            deleted_count = self.db.query(ChatMessage).filter(
                ChatMessage.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Deleted {deleted_count} old messages (older than {days} days)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old messages: {str(e)}")
            self.db.rollback()
            raise
