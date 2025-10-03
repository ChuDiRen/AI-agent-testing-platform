"""认证相关路由"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.schemas.common import APIResponse
from app.schemas.user import UserLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[UserResponse]:
    """用户注册"""
    auth_service = AuthService(db)
    user = await auth_service.register(user_data)
    
    return APIResponse(
        message="注册成功",
        data=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=APIResponse[Token])
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    """用户登录"""
    auth_service = AuthService(db)
    token = await auth_service.login(login_data)
    
    return APIResponse(
        message="登录成功",
        data=token
    )

