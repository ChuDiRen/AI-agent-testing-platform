from pydantic import BaseModel


class LoginRequest(BaseModel): # 登录请求
    username: str
    password: str

