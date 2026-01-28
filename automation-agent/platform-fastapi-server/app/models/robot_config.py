"""
机器人配置信息模型
"""
from sqlalchemy import Column, String, Boolean, Text, Index, JSON
from app.db.base import Base


class RobotConfig(Base):
    """机器人配置信息表"""
    __tablename__ = "t_robot_config"
    
    robot_name = Column(String(100), nullable=False, comment='机器人名称')
    robot_type = Column(String(20), nullable=False, index=True, comment='机器人类型(dingtalk/feishu/wechat)')
    webhook_url = Column(String(500), nullable=False, comment='Webhook URL')
    message_template = Column(Text, nullable=True, comment='消息模板内容')
    keywords = Column(JSON, nullable=True, comment='关键词及其对应的参数(JSON格式)')
    is_enabled = Column(Boolean, nullable=False, default=True, index=True, comment='是否启用')
    
    __table_args__ = (
        Index('idx_robot_type_enabled', 'robot_type', 'is_enabled'),
        {'comment': '机器人配置表'}
    )
