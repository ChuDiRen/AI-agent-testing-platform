from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Dept(SQLModel, table=True): # 部门模型
    __tablename__ = "t_dept"
    dept_id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0, index=True) # 上级部门ID，0表示顶级部门
    dept_name: str = Field(max_length=100) # 部门名称
    order_num: int = Field(default=0) # 排序
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间

