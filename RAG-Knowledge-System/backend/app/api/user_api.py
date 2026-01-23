"""
用户管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.user_service import UserService
from db.session import get_db
from core.deps import get_current_user
from models.user import User
from core.resp_model import ResponseModel

router = APIRouter(prefix="/users", tags=["用户管理"])


class UserCreateRequest(BaseModel):
    """用户创建请求"""
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """重置密码请求"""
    new_password: str


@router.post("", response_model=ResponseModel)
async def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建用户（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        user_service = UserService(db)
        user = user_service.create_user(
            username=request.username,
            password=request.password,
            email=request.email,
            full_name=request.full_name,
            role_id=request.role_id,
            dept_id=request.dept_id
        )

        return ResponseModel.success(
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role_id": user.role_id
            },
            message="用户创建成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息

    需要认证
    """
    return ResponseModel.success(
        data=current_user.dict(exclude={"hashed_password"}),
        message="获取用户信息成功"
    )


@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户信息

    需要认证
    """
    try:
        # 检查权限
        if user_id != current_user.id and not current_user.is_superuser:
            return ResponseModel.error(message="无权访问此用户信息")

        user_service = UserService(db)
        user = user_service.get_user(user_id)

        if not user:
            return ResponseModel.error(message="用户不存在")

        return ResponseModel.success(
            data=user.dict(exclude={"hashed_password"}),
            message="获取用户信息成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息

    需要认证
    """
    try:
        # 检查权限
        if user_id != current_user.id and not current_user.is_superuser:
            return ResponseModel.error(message="无权修改此用户信息")

        user_service = UserService(db)
        user = user_service.update_user(
            user_id=user_id,
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            role_id=request.role_id if current_user.is_superuser else None,
            dept_id=request.dept_id if current_user.is_superuser else None,
            is_active=request.is_active if current_user.is_superuser else None,
            password=request.password
        )

        return ResponseModel.success(
            data=user.dict(exclude={"hashed_password"}),
            message="用户更新成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.get("", response_model=ResponseModel)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = None,
    dept_id: Optional[int] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户列表（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        user_service = UserService(db)
        result = user_service.list_users(
            skip=skip,
            limit=limit,
            keyword=keyword,
            dept_id=dept_id,
            role_id=role_id,
            is_active=is_active
        )

        return ResponseModel.success(
            data=result,
            message="获取用户列表成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.post("/{user_id}/password/change", response_model=ResponseModel)
async def change_password(
    user_id: int,
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    修改密码

    需要认证
    """
    try:
        # 检查权限
        if user_id != current_user.id:
            return ResponseModel.error(message="只能修改自己的密码")

        user_service = UserService(db)
        user_service.change_password(
            user_id=user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )

        return ResponseModel.success(
            message="密码修改成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")


@router.post("/{user_id}/password/reset", response_model=ResponseModel)
async def reset_password(
    user_id: int,
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    重置密码（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        user_service = UserService(db)
        user_service.reset_password(
            user_id=user_id,
            new_password=request.new_password
        )

        return ResponseModel.success(
            message="密码重置成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置密码失败: {str(e)}")


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        user_service = UserService(db)
        success = user_service.delete_user(user_id)

        if success:
            return ResponseModel.success(
                message="用户删除成功"
            )
        else:
            return ResponseModel.error(
                message="用户不存在"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")
