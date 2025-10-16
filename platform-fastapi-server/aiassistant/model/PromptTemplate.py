from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class PromptTemplate(SQLModel, table=True):
    """提示词模板表 - 支持API/Web/App/通用四种测试类型"""
    
    __tablename__ = "prompt_template"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)  # 模板名称
    template_type: str = Field(max_length=20, index=True)  # 模板类型（system/user/assistant）
    test_type: str = Field(max_length=20, index=True)  # 测试类型（API/Web/App/通用）
    content: str = Field(sa_column_kwargs={"type_": "TEXT"})  # 模板内容（支持变量如{test_type}、{case_count}）
    variables: Optional[str] = Field(default=None, max_length=500)  # 支持的变量列表（JSON格式）
    is_active: bool = Field(default=True)  # 是否激活
    created_by: Optional[int] = Field(default=None)  # 创建人ID
    create_time: datetime = Field(default_factory=datetime.now)  # 创建时间
    modify_time: datetime = Field(default_factory=datetime.now)  # 修改时间
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "API测试用例生成提示词",
                "template_type": "system",
                "test_type": "API",
                "content": "你是一位专业的测试工程师，擅长编写{test_type}测试用例。请根据用户需求生成{case_count}个测试用例，格式为JSON。",
                "variables": '["test_type", "case_count"]',
                "is_active": True
            }
        }

