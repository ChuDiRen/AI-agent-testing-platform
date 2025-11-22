"""
机器人消息模板配置Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ==================== 消息模板查询相关 ====================
class RobotMsgConfigQuery(BaseModel):
    """消息模板查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    robot_id: Optional[int] = Field(default=None, description="机器人ID")
    msg_type: Optional[str] = Field(default=None, description="消息类型")
    template_name: Optional[str] = Field(default=None, description="模板名称")
    is_enabled: Optional[bool] = Field(default=None, description="是否启用")


# ==================== 消息模板创建/更新相关 ====================
class RobotMsgConfigCreate(BaseModel):
    """消息模板创建请求"""
    robot_id: int = Field(description="关联的机器人ID")
    msg_type: str = Field(max_length=50, description="消息类型: text/markdown/card")
    template_name: str = Field(max_length=255, description="模板名称")
    template_content: str = Field(description="模板内容（支持变量替换）")
    variables: Optional[str] = Field(default=None, description="模板变量说明（JSON格式）")
    is_enabled: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")


class RobotMsgConfigUpdate(BaseModel):
    """消息模板更新请求"""
    id: int = Field(description="模板ID")
    robot_id: Optional[int] = Field(default=None, description="机器人ID")
    msg_type: Optional[str] = Field(default=None, description="消息类型")
    template_name: Optional[str] = Field(default=None, description="模板名称")
    template_content: Optional[str] = Field(default=None, description="模板内容")
    variables: Optional[str] = Field(default=None, description="模板变量说明")
    is_enabled: Optional[bool] = Field(default=None, description="是否启用")
    description: Optional[str] = Field(default=None, description="描述")


# ==================== 消息模板响应相关 ====================
class RobotMsgConfigResponse(BaseModel):
    """消息模板响应"""
    id: int
    robot_id: int
    msg_type: str
    template_name: str
    template_content: str
    variables: Optional[str]
    is_enabled: bool
    description: Optional[str]
    create_time: Optional[str]
    update_time: Optional[str]
    # 扩展字段（关联查询）
    robot_name: Optional[str] = None
    robot_type: Optional[str] = None


# ==================== 消息发送相关 ====================
class MessageSendRequest(BaseModel):
    """消息发送请求"""
    template_id: int = Field(description="消息模板ID")
    variables: Optional[Dict[str, Any]] = Field(default=None, description="变量替换数据")


class MessageSendResponse(BaseModel):
    """消息发送响应"""
    success: bool = Field(description="发送是否成功")
    message: str = Field(description="发送结果消息")
    robot_name: str = Field(description="机器人名称")
    sent_at: str = Field(description="发送时间")
