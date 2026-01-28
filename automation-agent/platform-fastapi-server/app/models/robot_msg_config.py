"""
机器人消息配置模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class RobotMsgConfig(Base):
    """机器人消息配置表"""
    __tablename__ = "t_robot_msg_config"
    
    robot_id = Column(Integer, ForeignKey('t_robot_config.id', ondelete='CASCADE'), nullable=False, index=True, comment='机器人ID')
    msg_type = Column(String(50), nullable=False, comment='消息类型(text/markdown/card等)')
    msg_content = Column(Text, nullable=False, comment='消息内容')
    msg_vars = Column(JSON, nullable=True, comment='消息变量(JSON格式)')
    is_enabled = Column(Boolean, nullable=False, default=True, index=True, comment='是否启用')
    
    # 关系
    robot = relationship("RobotConfig", backref="msg_configs")
    
    __table_args__ = (
        Index('idx_msg_robot_enabled', 'robot_id', 'is_enabled'),
        Index('idx_msg_type', 'msg_type'),
        {'comment': '机器人消息配置表'}
    )
