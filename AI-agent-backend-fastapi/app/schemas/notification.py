# Copyright (c) 2025 左岚. All rights reserved.
"""
消息通知Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    """通知基础Schema"""
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(default="info", description="通知类型: system/test/error/info")


class NotificationCreate(NotificationBase):
    """创建通知Schema"""
    user_id: int = Field(..., description="接收用户ID")


class NotificationUpdate(BaseModel):
    """更新通知Schema"""
    is_read: Optional[bool] = Field(None, description="是否已读")


class NotificationResponse(NotificationBase):
    """通知响应Schema"""
    notification_id: int = Field(..., description="通知ID")
    user_id: int = Field(..., description="用户ID")
    is_read: bool = Field(..., description="是否已读")
    create_time: datetime = Field(..., description="创建时间")
    read_time: Optional[datetime] = Field(None, description="阅读时间")

    class Config:
        from_attributes = True


class NotificationListParams(BaseModel):
    """通知列表查询参数"""
    filter_type: Optional[str] = Field(None, description="过滤类型: all/unread/read/system/test/error/info")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数")


class NotificationStats(BaseModel):
    """通知统计Schema"""
    total: int = Field(..., description="总数")
    unread: int = Field(..., description="未读数")
    read: int = Field(..., description="已读数")

