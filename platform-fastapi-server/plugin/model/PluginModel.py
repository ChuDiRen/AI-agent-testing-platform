"""
插件数据模型
支持执行引擎插件化架构（命令行调用方式）
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


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
    plugin_content: Optional[str] = Field(default=None, description="插件ZIP包内容(Base64编码)，上传时存入，安装时解压并 pip install -e")
    
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
                "capabilities": {"console_scripts": {"webrun": "webrun.cli:run"}},
                "dependencies": ["selenium>=4.0.0", "allure-pytest"]
            }
        }
