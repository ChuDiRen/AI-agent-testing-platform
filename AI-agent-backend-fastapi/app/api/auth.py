"""认证相关路由"""
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.common import APIResponse
from app.schemas.user import UserLogin
from app.services.auth_service import AuthService
from app.core.security import decode_refresh_token, create_access_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


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


@router.post("/refresh", response_model=APIResponse[Token])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    """刷新访问令牌"""
    # 解码刷新令牌
    payload = decode_refresh_token(refresh_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证用户是否存在
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )

    # 生成新的刷新令牌
    from app.core.security import create_refresh_token
    new_refresh_token = create_refresh_token(data={"sub": username})

    return APIResponse(
        message="令牌刷新成功",
        data=Token(
            access_token=access_token,
            refresh_token=new_refresh_token,  # 返回新的refresh_token
            token_type="bearer"
        )
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> APIResponse:
    """用户登出 - 将 token 加入黑名单"""
    from app.core.token_blacklist import token_blacklist
    
    token = credentials.credentials
    
    # 将 token 加入黑名单
    success = token_blacklist.add_to_blacklist(
        token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    if not success:
        # 即使加入黑名单失败,也返回成功(可能是 Redis 不可用)
        return APIResponse(
            message="登出成功(Token黑名单服务不可用,请注意安全)"
        )
    
    return APIResponse(message="登出成功")

