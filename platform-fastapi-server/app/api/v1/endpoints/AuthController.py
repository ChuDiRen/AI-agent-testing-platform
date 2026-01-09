from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select

from app.security.JwtUtil import JwtUtils
from app.database.database import get_session
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from app.models.UserModel import User
from app.schemas.LoginSchema import LoginRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["登录认证"])


@router.post("/login", summary="用户登录")
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """用户登录，只返回access_token"""
    statement = select(User).where(User.username == request.username, User.password == request.password)
    user = session.exec(statement).first()
    if user:
        token = JwtUtils.create_token(user.id, user.username)
        return respModel.ok_resp(obj={"access_token": token}, msg="登录成功")
    else:
        return respModel.error_resp("登录失败，用户名或密码错误")


@router.get("/userinfo", summary="获取当前用户信息")
async def get_userinfo(authorization: Optional[str] = Header(default=None), session: Session = Depends(get_session)):
    """通过 token 获取当前登录用户的信息"""
    logger.info(f"userinfo 接口被调用, authorization={authorization}")
    if not authorization:
        logger.warning("缺少 authorization header")
        return respModel.error_resp("请先登录")
    
    try:
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        user_id = JwtUtils.get_user_id_from_token(token)
        if not user_id:
            return respModel.error_resp("登录已过期，请重新登录")
        
        user = session.get(User, user_id)
        if not user:
            return respModel.error_resp("用户不存在")
        
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
    except Exception as e:
        return respModel.error_resp("Token无效，请重新登录")


@router.post("/refreshToken", summary="刷新Token")
async def refresh_token(authorization: Optional[str] = Header(default=None)):
    """刷新 token：使用旧的 token 获取新的 token"""
    if not authorization:
        return respModel.error_resp("缺少认证信息")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    new_token = JwtUtils.refresh_token(token)
    if new_token:
        return respModel.ok_resp(obj={"access_token": new_token}, msg="Token刷新成功")
    else:
        return respModel.error_resp("Token刷新失败，请重新登录")
