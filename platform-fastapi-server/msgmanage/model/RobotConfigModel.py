"""
机器人配置数据模型
支持微信、钉钉、飞书等多平台机器人配置
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class RobotConfig(SQLModel, table=True):
    """机器人配置表"""
    __tablename__ = "t_robot_config"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='机器人ID')
    robot_type: str = Field(max_length=50, description='机器人类型: wechat/dingtalk/feishu')
    robot_name: str = Field(max_length=255, description='机器人名称')
    webhook_url: str = Field(max_length=500, description='Webhook地址')
    secret_key: Optional[str] = Field(default=None, max_length=255, description='密钥（钉钉需要）')
    is_enabled: bool = Field(default=True, description='是否启用')
    description: Optional[str] = Field(default=None, max_length=500, description='描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    last_test_time: Optional[datetime] = Field(default=None, description='最后测试时间')
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_type": "dingtalk",
                "robot_name": "测试通知机器人",
                "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
                "secret_key": "SECxxx",
                "is_enabled": True,
                "description": "用于测试完成通知"
            }
        }
