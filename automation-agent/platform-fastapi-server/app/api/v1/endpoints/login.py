"""
登录 API 端点
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import LoginRequest, LoginResponse, UserResponse
from app.services.login_service import login_service
from app.core.resp_model import RespModel
from app.schemas.user import UserResponse as UserModelResponse

router = APIRouter(tags=["登录"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        db_user, token = await login_service.authenticate(
            db, request.username, request.password
        )
        
        # 构建 UserResponse
        user_response = UserModelResponse(
            id=db_user.id,
            username=db_user.username,
            create_time=db_user.create_time.strftime('%Y-%m-%d %H:%M:%S') if db_user.create_time else ''
        )
        
        return LoginResponse(
            code=200,
            msg="登录成功",
            data=user_response,
            token=token
        )
    except Exception as e:
        from app.core.exceptions import UnauthorizedException
        if "不存在" in str(e) or "密码" in str(e):
            raise UnauthorizedException(str(e))
        raise Exception(f"登录失败: {str(e)}")
