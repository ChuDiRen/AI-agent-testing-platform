# Copyright (c) 2025 左岚. All rights reserved.
"""
消息通知模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    """消息通知模型"""
    __tablename__ = "t_notification"

    notification_id = Column(Integer, primary_key=True, autoincrement=True, comment="通知ID")  # 主键ID
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="用户ID")  # 接收用户ID
    title = Column(String(200), nullable=False, comment="通知标题")  # 通知标题
    content = Column(Text, nullable=False, comment="通知内容")  # 通知内容
    type = Column(String(20), nullable=False, default="info", comment="通知类型")  # 通知类型: system/test/error/info
    is_read = Column(Boolean, default=False, comment="是否已读")  # 是否已读
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    read_time = Column(DateTime, nullable=True, comment="阅读时间")  # 阅读时间

    # 关联关系
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(notification_id={self.notification_id}, title='{self.title}', type='{self.type}', is_read={self.is_read})>"

