from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class OperationType(SQLModel, table=True): # 操作类型表
    __tablename__ = "t_api_operationtype"
    id: Optional[int] = Field(default=None, primary_key=True, description='操作类型ID')
    operation_type_name: str = Field(max_length=255, description='操作类型名称')
    ex_fun_name: str = Field(max_length=255, description='操作类型方法名')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')