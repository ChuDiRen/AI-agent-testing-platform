# Copyright (c) 2025 左岚. All rights reserved.
"""
消息通知Repository
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationRepository:
    """消息通知数据访问层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification_data: NotificationCreate) -> Notification:
        """创建通知"""
        notification = Notification(**notification_data.model_dump())
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """根据ID获取通知"""
        result = await self.db.execute(
            select(Notification).where(Notification.notification_id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: int,
        filter_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Notification]:
        """获取用户的通知列表"""
        query = select(Notification).where(Notification.user_id == user_id)

        # 应用过滤条件
        if filter_type == "unread":
            query = query.where(Notification.is_read == False)
        elif filter_type == "read":
            query = query.where(Notification.is_read == True)
        elif filter_type and filter_type != "all":
            # 按类型过滤: system/test/error/info
            query = query.where(Notification.type == filter_type)

        # 按创建时间倒序排列
        query = query.order_by(Notification.create_time.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_count_by_user_id(
        self,
        user_id: int,
        filter_type: Optional[str] = None
    ) -> int:
        """获取用户通知数量"""
        query = select(func.count(Notification.notification_id)).where(
            Notification.user_id == user_id
        )

        # 应用过滤条件
        if filter_type == "unread":
            query = query.where(Notification.is_read == False)
        elif filter_type == "read":
            query = query.where(Notification.is_read == True)
        elif filter_type and filter_type != "all":
            query = query.where(Notification.type == filter_type)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_unread_count(self, user_id: int) -> int:
        """获取用户未读通知数量"""
        result = await self.db.execute(
            select(func.count(Notification.notification_id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        return result.scalar() or 0

    async def update(
        self,
        notification_id: int,
        notification_data: NotificationUpdate
    ) -> Optional[Notification]:
        """更新通知"""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        update_data = notification_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(notification, key, value)

        # 如果标记为已读,设置阅读时间
        if update_data.get("is_read") and not notification.read_time:
            notification.read_time = datetime.now()

        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """标记通知为已读"""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.is_read = True
        notification.read_time = datetime.now()

        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: int) -> int:
        """标记用户所有通知为已读"""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()

        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_time = datetime.now()
            count += 1

        await self.db.commit()
        return count

    async def delete(self, notification_id: int) -> bool:
        """删除通知"""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return False

        await self.db.delete(notification)
        await self.db.commit()
        return True

    async def delete_all(self, user_id: int) -> int:
        """删除用户所有通知"""
        result = await self.db.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        notifications = result.scalars().all()

        count = 0
        for notification in notifications:
            await self.db.delete(notification)
            count += 1

        await self.db.commit()
        return count

