from datetime import datetime
from typing import Optional

from sqlalchemy import Text
from sqlmodel import SQLModel, Field


class TestCase(SQLModel, table=True):
    """测试用例表 - 支持JSON和YAML两种格式"""

    __tablename__ = "test_case"

    id: Optional[int] = Field(default=None, primary_key=True)
    case_name: str = Field(max_length=200, index=True)  # 测试用例名称
    project_id: int = Field(index=True)  # 所属项目ID
    module_name: Optional[str] = Field(default=None, max_length=100)  # 模块名称
    test_type: str = Field(max_length=20, index=True)  # 测试类型（API/Web/App）
    priority: str = Field(max_length=10, default="P1")  # 优先级（P0/P1/P2/P3）
    precondition: Optional[str] = Field(default=None, sa_type=Text)  # 前置条件
    test_steps: Optional[str] = Field(default=None, sa_type=Text)  # 测试步骤（JSON格式数组）
    expected_result: Optional[str] = Field(default=None, sa_type=Text)  # 预期结果
    test_data: Optional[str] = Field(default=None, sa_type=Text)  # 测试数据
    case_format: str = Field(max_length=20, default="JSON")  # 格式类型（JSON/YAML）
    yaml_content: Optional[str] = Field(default=None, sa_type=Text)  # YAML格式内容
    created_by: Optional[int] = Field(default=None)  # 创建人ID
    create_time: datetime = Field(default_factory=datetime.now)  # 创建时间
    modify_time: datetime = Field(default_factory=datetime.now)  # 修改时间
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_name": "用户登录成功测试",
                "project_id": 1,
                "module_name": "用户认证",
                "test_type": "API",
                "priority": "P0",
                "precondition": "用户已注册且未登录",
                "test_steps": '["输入正确的用户名和密码", "点击登录按钮"]',
                "expected_result": "返回200成功，返回用户信息",
                "case_format": "JSON"
            }
        }
