from pydantic import BaseModel
from typing import Optional

# 分页查询Schema
class TestCaseQuery(BaseModel):
    page: int = 1 # 页码
    pageSize: int = 20 # 每页条数
    project_id: Optional[int] = None # 项目ID
    test_type: Optional[str] = None # 测试类型
    priority: Optional[str] = None # 优先级


# 创建Schema
class TestCaseCreate(BaseModel):
    case_name: str # 用例名称
    project_id: Optional[int] = None # 项目ID
    module_name: Optional[str] = None # 模块名称
    test_type: str = "API" # 测试类型
    priority: str = "P1" # 优先级
    precondition: Optional[str] = None # 前置条件
    test_steps: Optional[str] = None # 测试步骤（JSON字符串）
    expected_result: Optional[str] = None # 预期结果
    test_data: Optional[str] = None # 测试数据（JSON字符串）
    case_format: str = "json" # 用例格式
    yaml_content: Optional[str] = None # YAML内容


# 更新Schema
class TestCaseUpdate(BaseModel):
    id: int # ID
    case_name: Optional[str] = None # 用例名称
    project_id: Optional[int] = None # 项目ID
    module_name: Optional[str] = None # 模块名称
    test_type: Optional[str] = None # 测试类型
    priority: Optional[str] = None # 优先级
    precondition: Optional[str] = None # 前置条件
    test_steps: Optional[str] = None # 测试步骤（JSON字符串）
    expected_result: Optional[str] = None # 预期结果
    test_data: Optional[str] = None # 测试数据（JSON字符串）
    case_format: Optional[str] = None # 用例格式
    yaml_content: Optional[str] = None # YAML内容


# 批量插入请求Schema
class BatchInsertRequest(BaseModel):
    project_id: int # 项目ID
    test_cases: list[TestCaseCreate] # 测试用例列表
