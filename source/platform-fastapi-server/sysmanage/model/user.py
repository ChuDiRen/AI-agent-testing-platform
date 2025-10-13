from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True): # 用户模型
    __tablename__ = "t_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=255, index=True, unique=True)
    password: str = Field(max_length=255)
    create_time: Optional[datetime] = None
