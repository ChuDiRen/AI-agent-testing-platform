from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel): # 登录请求
    username: str
    password: str

