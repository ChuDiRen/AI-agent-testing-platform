"""用户相关路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import StringIO

from app.core.database import get_db
from app.schemas.user import UserResponse, UserCreate, UserUpdate, PasswordChange, ProfileUpdate
from app.schemas.common import APIResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.user_service import UserService
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.export import export_to_csv, export_to_json

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[UserResponse]:
    """获取当前用户信息"""
    return APIResponse(
        data=UserResponse.model_validate(current_user)
    )


@router.put("/me", response_model=APIResponse[UserResponse])
async def update_current_user_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[UserResponse]:
    """更新当前用户的个人资料"""
    user_service = UserService(db)

    # 构建更新数据
    update_data = UserUpdate(**profile_data.model_dump(exclude_unset=True))

    # 更新用户信息
    user = await user_service.update_user(current_user.user_id, update_data)

    return APIResponse(
        message="个人资料更新成功",
        data=UserResponse.model_validate(user)
    )


@router.put("/me/password", response_model=APIResponse[None])
async def change_current_user_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """修改当前用户密码"""
    from app.core.security import verify_password, get_password_hash
    from fastapi import HTTPException, status

    # 验证原密码
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    # 更新密码
    user_service = UserService(db)
    new_password_hash = get_password_hash(password_data.new_password)
    update_data = UserUpdate(password=new_password_hash)
    await user_service.update_user(current_user.user_id, update_data)

    return APIResponse(
        message="密码修改成功,请重新登录"
    )


@router.get("/", response_model=APIResponse[PaginatedResponse[UserResponse]])
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PaginatedResponse[UserResponse]]:
    """获取用户列表（分页、搜索、过滤）"""
    user_service = UserService(db)
    
    pagination = PaginationParams(page=page, page_size=page_size)
    users, total = await user_service.get_users_paginated(
        pagination=pagination,
        keyword=keyword,
        is_active=is_active
    )
    
    paginated_data = PaginatedResponse.create(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size
    )
    
    return APIResponse(data=paginated_data)


@router.post("/", response_model=APIResponse[UserResponse])
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[UserResponse]:
    """创建新用户"""
    from fastapi import HTTPException, status
    user_service = UserService(db)

    # 检查用户名是否已存在
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = await user_service.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

    # 创建用户
    new_user = await user_service.create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        mobile=user_data.mobile,
        dept_id=user_data.dept_id,
        ssex=user_data.ssex or '2',
        description=None
    )

    return APIResponse(
        success=True,
        message="创建用户成功",
        data=UserResponse.model_validate(new_user)
    )


@router.get("/export/csv")
async def export_users_csv(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """导出用户数据为CSV"""
    user_service = UserService(db)
    users = await user_service.get_all_users(skip=0, limit=1000)
    
    # 转换为字典列表
    user_dicts = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": str(user.created_at)
        }
        for user in users
    ]
    
    headers = ["id", "username", "email", "full_name", "is_active", "created_at"]
    csv_content = export_to_csv(user_dicts, headers)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )


@router.get("/export/json")
async def export_users_json(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """导出用户数据为JSON"""
    user_service = UserService(db)
    users = await user_service.get_all_users(skip=0, limit=1000)
    
    user_dicts = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": str(user.created_at)
        }
        for user in users
    ]
    
    json_content = export_to_json(user_dicts)
    
    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=users.json"}
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[UserResponse]:
    """获取用户详情"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    return APIResponse(
        data=UserResponse.model_validate(user)
    )


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[UserResponse]:
    """更新用户信息"""
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_data)
    
    return APIResponse(
        message="用户更新成功",
        data=UserResponse.model_validate(user)
    )


@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除用户"""
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    
    return APIResponse(
        message="用户删除成功"
    )

