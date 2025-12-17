"""
插件 Schema 定义
用于 API 请求和响应的数据验证
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

from pydantic import BaseModel, Field, field_validator


class PluginBase(BaseModel):
    """插件基础 Schema"""
    plugin_name: str = Field(..., max_length=100, description="插件名称")
    plugin_code: str = Field(..., max_length=50, description="插件代码标识")
    plugin_type: str = Field(..., max_length=20, description="插件类型: executor/tool/extension")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    command: str = Field(..., max_length=500, description="执行命令")
    description: Optional[str] = Field(None, description="插件描述")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    is_enabled: int = Field(default=1, description="是否启用: 0禁用 1启用")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="插件能力描述")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="配置参数Schema")
    dependencies: Optional[List[str]] = Field(None, description="依赖包列表")


class PluginCreate(PluginBase):
    """创建插件请求 Schema"""
    pass


class PluginUpdate(BaseModel):
    """更新插件请求 Schema"""
    plugin_name: Optional[str] = Field(None, max_length=100)
    plugin_type: Optional[str] = Field(None, max_length=20)
    version: Optional[str] = Field(None, max_length=20)
    command: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    is_enabled: Optional[int] = None
    capabilities: Optional[Dict[str, Any]] = None
    config_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None


class PluginQuery(BaseModel):
    """查询插件请求 Schema"""
    plugin_name: Optional[str] = Field(None, description="插件名称（模糊查询）")
    plugin_code: Optional[str] = Field(None, description="插件代码")
    plugin_type: Optional[str] = Field(None, description="插件类型")
    is_enabled: Optional[int] = Field(None, description="是否启用")
    install_status: Optional[str] = Field(None, description="安装状态")
    health_status: Optional[str] = Field(None, description="健康状态")
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页数量")


class PluginResponse(PluginBase):
    """插件响应 Schema"""
    id: int
    create_time: datetime
    modify_time: datetime
    plugin_content: Optional[bool] = Field(None, description="是否有内嵌插件内容")
    
    # 安装与版本管理
    content_hash: Optional[str] = Field(None, description="插件包SHA256哈希值")
    install_status: str = Field(default="not_installed", description="安装状态")
    install_path: Optional[str] = Field(None, description="安装目录路径")
    install_time: Optional[datetime] = Field(None, description="安装时间")
    
    # 健康检查
    health_status: str = Field(default="unknown", description="健康状态")
    health_message: Optional[str] = Field(None, description="健康检查消息")
    last_health_check: Optional[datetime] = Field(None, description="上次健康检查时间")
    
    # 禁用原因
    disable_reason: Optional[str] = Field(None, description="禁用原因")
    
    @field_validator("capabilities", "config_schema", "dependencies", mode="before")
    @classmethod
    def parse_json_fields(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except json.JSONDecodeError:
                return None
        return v
    
    @field_validator("plugin_content", mode="before")
    @classmethod
    def convert_plugin_content(cls, v):
        """将 plugin_content 转换为布尔值（是否存在内容）"""
        return bool(v) if v else False
    
    class Config:
        from_attributes = True


class PluginHealthCheck(BaseModel):
    """插件健康检查响应"""
    plugin_code: str
    status: str  # healthy/unhealthy/degraded/not_installed/unknown
    version: Optional[str] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    install_status: Optional[str] = None
    command_path: Optional[str] = None
    dependencies_check: Optional[Dict[str, Any]] = None  # 依赖检查结果


class PluginRegisterRequest(BaseModel):
    """插件自注册请求"""
    plugin: Dict[str, Any] = Field(..., description="插件元信息")
    requirements: Optional[Dict[str, Any]] = Field(None, description="运行环境要求")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="插件能力")
    api: Dict[str, str] = Field(..., description="API端点配置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plugin": {
                    "name": "web-engine",
                    "code": "web_engine",
                    "type": "executor",
                    "version": "1.0.0",
                    "description": "Web自动化测试执行引擎",
                    "author": "Platform Team"
                },
                "requirements": {
                    "python": ">=3.8",
                    "dependencies": ["selenium>=4.0.0", "allure-pytest"]
                },
                "capabilities": {
                    "test_types": ["web_ui"],
                    "features": ["keyword_driven", "data_driven"]
                },
                "api": {
                    "endpoint": "http://localhost:8001",
                    "health_check": "/health",
                    "execute": "/execute"
                }
            }
        }
