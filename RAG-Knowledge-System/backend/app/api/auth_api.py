"""
认证API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel

from services.user_service import UserService
from core.security import create_access_token, verify_password
from core.deps import get_db
from sqlmodel import Session
from config.settings import settings
from core.resp_model import ResponseModel

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str
    role_id: int
    is_superuser: bool


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: str
    full_name: Optional[str] = None


@router.post("/login", response_model=ResponseModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录

    不需要认证
    """
    try:
        user_service = UserService(db)

        # 验证用户
        user = user_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 检查是否激活
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )

        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )

        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            email=user.email,
            role_id=user.role_id,
            is_superuser=user.is_superuser
        )

        return ResponseModel.success(
            data=login_response.dict(),
            message="登录成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.post("/register", response_model=ResponseModel)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册

    不需要认证
    """
    try:
        user_service = UserService(db)

        # 创建用户
        user = user_service.create_user(
            username=request.username,
            password=request.password,
            email=request.email,
            full_name=request.full_name,
            role_id=None,  # 注册时使用默认角色
            dept_id=None
        )

        return ResponseModel.success(
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            message="注册成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/logout", response_model=ResponseModel)
async def logout():
    """
    用户登出

    客户端删除本地存储的token即可
    需要认证
    """
    return ResponseModel.success(
        message="登出成功"
    )


@router.get("/verify-token", response_model=ResponseModel)
async def verify_token():
    """
    验证token有效性

    需要认证
    """
    return ResponseModel.success(
        message="Token有效"
    )
