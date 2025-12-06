from core.JwtUtil import JwtUtils
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from sysmanage.model.user import User
from typing import Optional

from ..schemas.login_schema import LoginRequest

module_route = APIRouter(tags=["登录"])

@module_route.post("/login", summary="用户登录") # 用户登录
def login(request: LoginRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == request.username, User.password == request.password)
    user = session.exec(statement).first()
    if user:
        token = JwtUtils.create_token(request.username, request.password)
        return respModel.ok_resp(obj=user, msg="登录成功", dic_t={"token": token})
    else:
        return respModel.error_resp("登录失败，用户名或密码错误")


@module_route.post("/refreshToken", summary="刷新Token")
def refresh_token(authorization: Optional[str] = Header(None)):
    """
    刷新 token：使用旧的 token 获取新的 token
    即使 token 已过期，只要签名有效就可以刷新
    """
    if not authorization:
        return respModel.error_resp(msg="缺少认证信息", code=401)
    
    # 提取 token（去掉 Bearer 前缀）
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # 刷新 token
    new_token = JwtUtils.refresh_token(token)
    if new_token:
        return respModel.ok_resp(obj={"token": new_token}, msg="Token刷新成功")
    else:
        return respModel.error_resp(msg="Token刷新失败，请重新登录", code=401)
