"""
机器人消息配置模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class RobotMsgConfig(Base):
    """机器人消息配置表"""
    __tablename__ = "t_robot_msg_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(Integer, comment='机器人ID')
    msg_type = Column(String(255), comment='消息类型')
    msg_content = Column(Text, comment='消息内容')
    msg_vars = Column(Text, comment='消息变量')
    is_enabled = Column(String(255), comment='是否启用')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
