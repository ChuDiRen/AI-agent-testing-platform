"""
机器人配置Schema
"""
from typing import Optional

from pydantic import BaseModel, Field


# ==================== 机器人配置查询相关 ====================
class RobotConfigQuery(BaseModel):
    """机器人配置查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    robot_type: Optional[str] = Field(default=None, description="机器人类型")
    robot_name: Optional[str] = Field(default=None, description="机器人名称")
    is_enabled: Optional[bool] = Field(default=None, description="是否启用")


# ==================== 机器人配置创建/更新相关 ====================
class RobotConfigCreate(BaseModel):
    """机器人配置创建请求"""
    robot_type: str = Field(description="机器人类型: wechat/dingtalk/feishu")
    robot_name: str = Field(max_length=255, description="机器人名称")
    webhook_url: str = Field(max_length=500, description="Webhook地址")
    secret_key: Optional[str] = Field(default=None, max_length=255, description="密钥（钉钉需要）")
    is_enabled: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")


class RobotConfigUpdate(BaseModel):
    """机器人配置更新请求"""
    id: int = Field(description="机器人ID")
    robot_type: Optional[str] = Field(default=None, description="机器人类型")
    robot_name: Optional[str] = Field(default=None, max_length=255, description="机器人名称")
    webhook_url: Optional[str] = Field(default=None, max_length=500, description="Webhook地址")
    secret_key: Optional[str] = Field(default=None, max_length=255, description="密钥")
    is_enabled: Optional[bool] = Field(default=None, description="是否启用")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")


# ==================== 机器人配置响应相关 ====================
class RobotConfigResponse(BaseModel):
    """机器人配置响应"""
    id: int
    robot_type: str
    robot_name: str
    webhook_url: str
    secret_key: Optional[str]
    is_enabled: bool
    description: Optional[str]
    create_time: Optional[str]
    update_time: Optional[str]
    last_test_time: Optional[str]


# ==================== 机器人测试相关 ====================
class RobotTestRequest(BaseModel):
    """机器人连接测试请求"""
    robot_id: int = Field(description="机器人ID")
    test_message: Optional[str] = Field(default="这是一条测试消息", description="测试消息内容")


class RobotTestResponse(BaseModel):
    """机器人连接测试响应"""
    success: bool = Field(description="测试是否成功")
    message: str = Field(description="测试结果消息")
    response_time: Optional[int] = Field(default=None, description="响应时间(ms)")
