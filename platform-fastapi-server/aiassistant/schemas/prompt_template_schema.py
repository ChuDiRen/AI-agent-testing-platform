from pydantic import BaseModel
from typing import Optional

# 分页查询Schema
class PromptTemplateQuery(BaseModel):
    page: int = 1 # 页码
    pageSize: int = 20 # 每页条数
    test_type: Optional[str] = None # 测试类型
    template_type: Optional[str] = None # 模板类型
    is_active: Optional[bool] = None # 是否激活


# 创建Schema
class PromptTemplateCreate(BaseModel):
    name: str # 模板名称
    template_type: str # 模板类型（system/user/assistant）
    test_type: Optional[str] = None # 测试类型（API/Web/App/通用）
    content: str # 模板内容
    variables: Optional[str] = None # 变量（JSON字符串）
    is_active: bool = True # 是否激活
    created_by: Optional[int] = None # 创建人ID


# 更新Schema
class PromptTemplateUpdate(BaseModel):
    id: int # ID
    name: Optional[str] = None # 模板名称
    template_type: Optional[str] = None # 模板类型
    test_type: Optional[str] = None # 测试类型
    content: Optional[str] = None # 模板内容
    variables: Optional[str] = None # 变量
    is_active: Optional[bool] = None # 是否激活
