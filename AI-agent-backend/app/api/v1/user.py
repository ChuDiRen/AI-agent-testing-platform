"""
用户管理API - 兼容vue-fastapi-admin格式
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.dto.base_dto import Success, Fail, PageRequest, PageResponse
from app.dto.user_dto import UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse
from app.entity.user import User
from app.service.user_service import UserService
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/list", summary="获取用户列表")
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    email: Optional[str] = Query(None, description="邮箱"),
    dept_id: Optional[int] = Query(None, description="部门ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    try:
        user_service = UserService(db)
        
        # 构建查询条件
        filters = {}
        if username:
            filters['username'] = username
        if email:
            filters['email'] = email
        if dept_id:
            filters['dept_id'] = dept_id
        
        # 获取用户列表
        users, total = await user_service.get_user_list(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        # 构建响应数据
        user_list = []
        for user in users:
            user_data = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email or "",
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                created_at=user.created_at,
                roles=[{"id": role.id, "name": role.name} for role in user.roles] if user.roles else [],
                dept={"id": user.dept.id, "name": user.dept.name} if user.dept else None
            )
            user_list.append(user_data.dict())
        
        response_data = UserListResponse(
            items=user_list,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
        
        return Success(data=response_data.dict())
        
    except Exception as e:
        return Fail(msg=f"获取用户列表失败: {str(e)}")


@router.get("/get", summary="获取用户详情")
async def get_user_detail(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_with_roles(user_id)
        
        if not user:
            return Fail(msg="用户不存在")
        
        user_data = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email or "",
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            created_at=user.created_at,
            roles=[{"id": role.id, "name": role.name} for role in user.roles] if user.roles else [],
            dept={"id": user.dept.id, "name": user.dept.name} if user.dept else None
        )
        
        return Success(data=user_data.dict())
        
    except Exception as e:
        return Fail(msg=f"获取用户详情失败: {str(e)}")


@router.post("/create", summary="创建用户")
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建用户"""
    try:
        user_service = UserService(db)
        
        # 检查用户名是否已存在
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            return Fail(msg="用户名已存在")
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = await user_service.get_user_by_email(user_data.email)
            if existing_email:
                return Fail(msg="邮箱已存在")
        
        # 创建用户
        password_hash = get_password_hash(user_data.password)
        new_user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            is_superuser=user_data.is_superuser,
            is_active=user_data.is_active,
            dept_id=user_data.dept_id,
            role_ids=user_data.role_ids
        )
        
        return Success(data={"id": new_user.id}, msg="创建成功")
        
    except Exception as e:
        return Fail(msg=f"创建用户失败: {str(e)}")


@router.post("/update", summary="更新用户")
async def update_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户"""
    try:
        user_service = UserService(db)
        
        # 检查用户是否存在
        user = await user_service.get_user_by_id(user_data.id)
        if not user:
            return Fail(msg="用户不存在")
        
        # 检查邮箱是否已被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_email = await user_service.get_user_by_email(user_data.email)
            if existing_email and existing_email.id != user_data.id:
                return Fail(msg="邮箱已被其他用户使用")
        
        # 更新用户
        await user_service.update_user(
            user_id=user_data.id,
            email=user_data.email,
            is_superuser=user_data.is_superuser,
            is_active=user_data.is_active,
            dept_id=user_data.dept_id,
            role_ids=user_data.role_ids
        )
        
        return Success(msg="更新成功")
        
    except Exception as e:
        return Fail(msg=f"更新用户失败: {str(e)}")


@router.delete("/delete", summary="删除用户")
async def delete_user(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户"""
    try:
        user_service = UserService(db)
        
        # 检查用户是否存在
        user = await user_service.get_user_by_id(user_id)
        if not user:
            return Fail(msg="用户不存在")
        
        # 不能删除自己
        if user_id == current_user.id:
            return Fail(msg="不能删除自己")
        
        # 不能删除超级用户
        if user.is_superuser:
            return Fail(msg="不能删除超级用户")
        
        # 删除用户
        await user_service.delete_user(user_id)
        
        return Success(msg="删除成功")
        
    except Exception as e:
        return Fail(msg=f"删除用户失败: {str(e)}")


@router.post("/reset_password", summary="重置密码")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重置用户密码"""
    try:
        user_service = UserService(db)
        
        # 检查用户是否存在
        user = await user_service.get_user_by_id(user_id)
        if not user:
            return Fail(msg="用户不存在")
        
        # 不能重置超级用户密码
        if user.is_superuser and not current_user.is_superuser:
            return Fail(msg="无权限重置超级用户密码")
        
        # 重置密码为123456
        new_password_hash = get_password_hash("123456")
        await user_service.update_password(user_id, new_password_hash)
        
        return Success(msg="密码已重置为123456")
        
    except Exception as e:
        return Fail(msg=f"重置密码失败: {str(e)}")
