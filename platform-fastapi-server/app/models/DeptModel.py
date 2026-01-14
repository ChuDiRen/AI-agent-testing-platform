from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Dept(SQLModel, table=True): # 部门模型
    __tablename__ = "t_dept"
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0, index=True) # 上级部门ID，0表示顶级部门
    dept_name: str = Field(max_length=100) # 部门名称
    leader: Optional[str] = Field(default=None, max_length=50) # 负责人
    phone: Optional[str] = Field(default=None, max_length=20) # 联系电话
    email: Optional[str] = Field(default=None, max_length=100) # 邮箱
    status: str = Field(default="0", max_length=1) # 部门状态（0正常 1停用）
    order_num: int = Field(default=0) # 排序
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间


