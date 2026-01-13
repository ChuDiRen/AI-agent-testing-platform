"""
机器人配置信息模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class RobotConfig(Base):
    """机器人配置信息表"""
    __tablename__ = "t_robot_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_name = Column(String(255), default=None, comment='机器人名称')
    robot_type = Column(String(255), default=None, comment='机器人类型（钉钉、飞书、企业微信）')
    webhook_url = Column(String(255), default=None, comment='Webhook URL')
    message_template = Column(Text, default=None, comment='消息模板内容')
    keywords = Column(Text, default=None, comment='关键词及其对应的参数（JSON 格式）')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
