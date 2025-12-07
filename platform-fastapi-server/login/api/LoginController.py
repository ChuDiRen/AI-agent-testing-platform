from core.JwtUtil import JwtUtils
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from sysmanage.model.user import User
from typing import Optional

from ..schemas.login_schema import LoginRequest

module_route = APIRouter(tags=["登录"])

@module_route.post("/login", summary="用户登录") # 用户登录，只返回access_token
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == request.username, User.password == request.password)
    user = session.exec(statement).first()
    if user:
        token = JwtUtils.create_token(user.id, user.username)
        return respModel.ok_resp(obj={"access_token": token}, msg="登录成功")
    else:
        return respModel.error_resp("登录失败，用户名或密码错误")


@module_route.get("/userinfo", summary="获取当前用户信息") # 通过token获取用户信息
async def get_userinfo(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)):
    """
    通过 token 获取当前登录用户的信息
    """
    if not authorization:
        return respModel.error_resp(msg="缺少认证信息", code=401)
    
    # 提取 token（去掉 Bearer 前缀）
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # 从 token 中获取用户ID
    user_id = JwtUtils.get_user_id_from_token(token)
    if not user_id:
        return respModel.error_resp(msg="Token无效或已过期", code=401)
    
    # 查询用户信息
    user = session.get(User, user_id)
    if not user:
        return respModel.error_resp(msg="用户不存在", code=404)
    
    # 返回用户信息（不包含密码）
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "mobile": user.mobile,
        "dept_id": user.dept_id,
        "status": user.status,
        "ssex": user.ssex,
        "avatar": user.avatar,
        "description": user.description,
        "create_time": user.create_time.isoformat() if user.create_time else None,
        "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
    }
    return respModel.ok_resp(obj=user_dict, msg="获取用户信息成功")


@module_route.post("/refreshToken", summary="刷新Token")
async def refresh_token(authorization: Optional[str] = Header(None)):
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
        return respModel.ok_resp(obj={"access_token": new_token}, msg="Token刷新成功")
    else:
        return respModel.error_resp(msg="Token刷新失败，请重新登录", code=401)
