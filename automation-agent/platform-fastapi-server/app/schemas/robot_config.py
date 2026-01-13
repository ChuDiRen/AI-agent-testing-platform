"""
机器人配置信息 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RobotConfigBase(BaseModel):
    """机器人配置基础 Schema"""
    robot_name: Optional[str] = Field(None, description='机器人名称')
    robot_type: Optional[str] = Field(None, description='机器人类型（钉钉、飞书、企业微信）')
    webhook_url: Optional[str] = Field(None, description='Webhook URL')
    message_template: Optional[str] = Field(None, description='消息模板内容')
    keywords: Optional[str] = Field(None, description='关键词及其对应的参数（JSON 格式）')


class RobotConfigCreate(RobotConfigBase):
    """创建机器人配置 Schema"""
    pass


class RobotConfigUpdate(BaseModel):
    """更新机器人配置 Schema"""
    robot_name: Optional[str] = None
    robot_type: Optional[str] = None
    webhook_url: Optional[str] = None
    message_template: Optional[str] = None
    keywords: Optional[str] = None


class RobotConfigResponse(RobotConfigBase):
    """机器人配置响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
