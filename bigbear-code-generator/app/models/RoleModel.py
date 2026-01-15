from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True): # 角色模型
    __tablename__ = "t_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(max_length=100, unique=True, index=True) # 角色名称
    role_key: Optional[str] = Field(default=None, max_length=100) # 角色标识
    role_sort: Optional[int] = Field(default=0) # 角色排序
    data_scope: Optional[str] = Field(default="1", max_length=10) # 数据权限范围:1=全部数据,2=自定义,3=本部门,4=本部门及下级,5=仅本人
    status: Optional[str] = Field(default="1", max_length=1) # 状态:1=正常,0=停用
    del_flag: Optional[str] = Field(default="0", max_length=1) # 删除标记:0=正常,1=已删除
    remark: Optional[str] = Field(default=None, max_length=500) # 角色描述
    create_by: Optional[str] = Field(default=None, max_length=64) # 创建者
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    update_by: Optional[str] = Field(default=None, max_length=64) # 更新者
    update_time: Optional[datetime] = Field(default_factory=datetime.now) # 更新时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间（向后兼容）



