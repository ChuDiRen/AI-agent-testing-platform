from core.JwtUtil import JwtUtils
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sysmanage.model.user import User

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
