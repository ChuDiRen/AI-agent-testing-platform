"""
插件数据模型
支持执行引擎插件化架构（命令行调用方式）
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from enum import Enum


class InstallStatus(str, Enum):
    """安装状态枚举"""
    NOT_INSTALLED = "not_installed"  # 未安装（仅上传）
    INSTALLING = "installing"        # 安装中
    INSTALLED = "installed"          # 已安装
    INSTALL_FAILED = "install_failed"  # 安装失败
    UPGRADING = "upgrading"          # 升级中


class HealthStatus(str, Enum):
    """健康状态枚举"""
    UNKNOWN = "unknown"              # 未知（未检查）
    HEALTHY = "healthy"              # 健康
    UNHEALTHY = "unhealthy"          # 不健康（命令不可用）
    DEGRADED = "degraded"            # 降级（部分功能不可用）
    NOT_INSTALLED = "not_installed"  # 未安装


class Plugin(SQLModel, table=True):
    """
    插件数据模型
    
    支持三种插件类型：
    - executor: 执行引擎插件（web-engine, api-engine等）- 通过命令行调用
    - tool: 工具类插件（报告生成器、通知服务等）
    - extension: 扩展插件（自定义关键字、自定义断言等）
    """
    __tablename__ = "t_plugin"
    
    # 基本信息
    id: Optional[int] = Field(default=None, primary_key=True, description="主键ID")
    plugin_name: str = Field(max_length=100, unique=True, index=True, description="插件名称")
    plugin_code: str = Field(max_length=50, unique=True, index=True, description="插件代码标识")
    plugin_type: str = Field(max_length=20, description="插件类型: executor/tool/extension")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    
    # 命令行配置
    command: str = Field(max_length=500, description="执行命令（从 setup.py 的 console_scripts 提取，如: webrun）")
    
    # 插件包内容（Base64编码的ZIP包）
    plugin_content: Optional[str] = Field(default=None, description="插件ZIP包内容(Base64编码)，上传时存入，安装时解压并 pip install")
    
    # 安装与版本管理
    content_hash: Optional[str] = Field(default=None, max_length=64, description="插件包SHA256哈希值，用于校验和去重")
    install_status: str = Field(default="not_installed", max_length=20, description="安装状态: not_installed/installing/installed/install_failed/upgrading")
    install_path: Optional[str] = Field(default=None, max_length=500, description="安装目录路径（venv所在目录）")
    venv_path: Optional[str] = Field(default=None, max_length=500, description="虚拟环境路径（独立venv）")
    install_time: Optional[datetime] = Field(default=None, description="安装时间")
    install_log: Optional[str] = Field(default=None, description="安装日志（成功/失败信息）")
    
    # 健康检查
    health_status: str = Field(default="unknown", max_length=20, description="健康状态: unknown/healthy/unhealthy/degraded/not_installed")
    health_message: Optional[str] = Field(default=None, max_length=500, description="健康检查消息")
    last_health_check: Optional[datetime] = Field(default=None, description="上次健康检查时间")
    
    # 禁用原因
    disable_reason: Optional[str] = Field(default=None, max_length=200, description="禁用原因（is_enabled=0时记录）")
    
    # 描述信息
    description: Optional[str] = Field(default=None, description="插件描述")
    author: Optional[str] = Field(default=None, max_length=100, description="作者")
    
    # 状态
    is_enabled: int = Field(default=1, description="是否启用: 0禁用 1启用")
    
    # 扩展信息（JSON格式）
    capabilities: Optional[str] = Field(
        default=None, 
        sa_column=Column(JSON),
        description="插件能力描述（测试类型、特性等）"
    )
    config_schema: Optional[str] = Field(
        default=None,
        sa_column=Column(JSON),
        description="配置参数的JSON Schema"
    )
    dependencies: Optional[str] = Field(
        default=None,
        sa_column=Column(JSON),
        description="依赖包列表"
    )
    keywords: Optional[str] = Field(
        default=None,
        sa_column=Column(JSON),
        description="插件支持的关键字列表（从 keywords.yaml 解析）"
    )
    
    # 时间戳
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    modify_time: datetime = Field(default_factory=datetime.now, description="修改时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plugin_name": "web-engine",
                "plugin_code": "web_engine",
                "plugin_type": "executor",
                "version": "1.0.0",
                "command": "webrun",
                "description": "Web自动化测试执行引擎",
                "is_enabled": 1,
                "install_status": "installed",
                "health_status": "healthy",
                "capabilities": {"console_scripts": {"webrun": "webrun.cli:run"}},
                "dependencies": ["selenium>=4.0.0", "allure-pytest"]
            }
        }
