"""
认证 API 端点
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.user_crud import user as user_crud
from app.schemas.user_schema import (
    LoginRequest, RegisterRequest, TokenResponse,
    UserCreate, UserUpdate, UserResponse
)
from app.core.security import AuthService
from app.core.resp_model import RespModel
from app.core.config import settings


router = APIRouter(prefix="/Auth", tags=["认证授权"])


@router.post("/login", response_model=RespModel)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查找用户
    db_user = await user_crud.get_by_username(db, username=request.username)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )

    # 验证密码
    if not AuthService.verify_password(request.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 更新最后登录时间
    await user_crud.update_last_login(db, user_id=db_user.id)

    # 生成 Token
    access_token = AuthService.create_access_token({
        "user_id": db_user.id,
        "username": db_user.username,
        "is_superuser": db_user.is_superuser
    })

    refresh_token = AuthService.create_refresh_token({
        "user_id": db_user.id
    })

    return RespModel.ok_resp(data=TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user_info={
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active,
            "is_superuser": db_user.is_superuser,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
            "last_login_at": db_user.last_login_at
        }
    ))


@router.post("/register", response_model=RespModel)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = await user_crud.get_by_username(db, username=request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if request.email:
        existing_email = await user_crud.get_by_email(db, email=request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    # 创建用户
    user_in = UserCreate(
        username=request.username,
        password=request.password,
        email=request.email,
        full_name=request.full_name or request.username
    )

    db_user = await user_crud.create(db, obj_in=user_in)

    return RespModel.ok_resp(data=UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        created_at=db_user.created_at
    ), msg="注册成功")


@router.post("/refresh", response_model=RespModel)
async def refresh_token(
    refresh_token: str = Header(..., description="Refresh Token"),
    db: AsyncSession = Depends(get_db)
):
    """刷新访问 Token"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 不能为空"
        )

    # 解码 refresh token
    payload = AuthService.decode_refresh_token(refresh_token)

    # 查找用户
    db_user = await user_crud.get(db, id=payload["user_id"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    # 生成新的 access token
    access_token = AuthService.create_access_token({
        "user_id": db_user.id,
        "username": db_user.username,
        "is_superuser": db_user.is_superuser
    })

    return RespModel.ok_resp(data=TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user_info=UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            last_login_at=db_user.last_login_at
        )
    ))


@router.get("/user/info", response_model=RespModel)
async def get_user_info(
    current_user_id: int = Header(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供用户 ID"
        )

    db_user = await user_crud.get(db, id=current_user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return RespModel.ok_resp(data=UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        last_login_at=db_user.last_login_at
    ))


@router.get("/users", response_model=RespModel)
async def list_users(
    skip: int = 0,
    limit: int = 10,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    if is_active is not None:
        users = await user_crud.get_active_users(db, skip=skip, limit=limit)
    else:
        users = await user_crud.get_multi(db, skip=skip, limit=limit)

    total = await user_crud.count_total_users(db)

    return RespModel.ok_resp_list(data=users, total=total)


@router.get("/stats", response_model=RespModel)
async def get_user_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计"""
    total_users = await user_crud.count_total_users(db)
    active_users = await user_crud.count_active_users(db)

    return RespModel.ok_resp(data={
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    })
