from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class WebKeyword(SQLModel, table=True):
    """Web关键字表"""
    __tablename__ = "t_web_keyword"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='关键字ID')
    name: str = Field(max_length=100, description='关键字名称')
    display_name: str = Field(max_length=100, description='显示名称')
    description: Optional[str] = Field(default=None, max_length=500, description='关键字描述')
    category: str = Field(default='action', max_length=50, description='分类：action/assertion/util')
    params: Optional[str] = Field(default=None, description='参数定义JSON')
    return_type: Optional[str] = Field(default=None, max_length=100, description='返回类型')
    code_template: str = Field(description='代码模板')
    python_code: Optional[str] = Field(default=None, description='Python实现代码')
    is_builtin: bool = Field(default=False, description='是否内置关键字')
    is_active: bool = Field(default=True, description='是否启用')
    usage_count: int = Field(default=0, description='使用次数')
    author: Optional[str] = Field(default=None, max_length=100, description='作者')
    version: str = Field(default='1.0', max_length=20, description='版本号')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_by: Optional[int] = Field(default=None, description='更新人ID')
