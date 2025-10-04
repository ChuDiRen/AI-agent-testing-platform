# Copyright (c) 2025 左岚. All rights reserved.
"""
消息通知Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationStats
)


class NotificationService:
    """消息通知业务逻辑层"""

    def __init__(self, db: AsyncSession):
        self.repository = NotificationRepository(db)

    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> NotificationResponse:
        """创建通知"""
        notification = await self.repository.create(notification_data)
        return NotificationResponse.model_validate(notification)

    async def get_notification(self, notification_id: int) -> Optional[NotificationResponse]:
        """获取通知详情"""
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def get_user_notifications(
        self,
        user_id: int,
        filter_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[NotificationResponse]:
        """获取用户通知列表"""
        notifications = await self.repository.get_by_user_id(
            user_id, filter_type, skip, limit
        )
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def get_notification_stats(self, user_id: int) -> NotificationStats:
        """获取用户通知统计"""
        total = await self.repository.get_count_by_user_id(user_id)
        unread = await self.repository.get_unread_count(user_id)
        read = total - unread

        return NotificationStats(
            total=total,
            unread=unread,
            read=read
        )

    async def mark_as_read(self, notification_id: int) -> Optional[NotificationResponse]:
        """标记通知为已读"""
        notification = await self.repository.mark_as_read(notification_id)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def mark_all_as_read(self, user_id: int) -> int:
        """标记用户所有通知为已读"""
        return await self.repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: int) -> bool:
        """删除通知"""
        return await self.repository.delete(notification_id)

    async def delete_all_notifications(self, user_id: int) -> int:
        """删除用户所有通知"""
        return await self.repository.delete_all(user_id)

    async def send_system_notification(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> NotificationResponse:
        """发送系统通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            content=content,
            type="system"
        )
        return await self.create_notification(notification_data)

    async def send_test_notification(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> NotificationResponse:
        """发送测试通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            content=content,
            type="test"
        )
        return await self.create_notification(notification_data)

    async def send_error_notification(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> NotificationResponse:
        """发送错误通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            content=content,
            type="error"
        )
        return await self.create_notification(notification_data)

