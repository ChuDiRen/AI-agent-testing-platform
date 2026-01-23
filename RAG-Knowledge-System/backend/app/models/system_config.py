"""
系统配置模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class SystemConfig(SQLModel, table=True):
    """系统配置表"""

    __tablename__ = "sys_config"

    id: Optional[int] = Field(default=None, primary_key=True, description="配置ID")
    config_key: str = Field(max_length=100, unique=True, index=True, description="配置键")
    config_value: Optional[str] = Field(default=None, max_length=2000, description="配置值")
    config_type: str = Field(default="string", max_length=20, description="配置类型：string/number/boolean/json")
    category: str = Field(default="system", max_length=50, description="配置分类")
    description: Optional[str] = Field(default=None, max_length=200, description="配置描述")
    is_public: bool = Field(default=False, description="是否公开（前端可见）")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
