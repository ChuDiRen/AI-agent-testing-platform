"""
User模块API - 完全按照vue-fastapi-admin标准实现
提供用户管理的CRUD功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.user_service import RBACUserService
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/list", summary="获取用户列表")
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    dept_id: Optional[int] = Query(None, description="部门ID"),
    status: Optional[str] = Query(None, description="状态：0禁用 1启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)

        # 构建查询条件
        filters = {}
        if username:
            filters['username'] = username
        if dept_id:
            filters['dept_id'] = dept_id
        if status:
            filters['status'] = status

        # 获取用户列表
        users, total = await user_service.get_user_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据
        user_list = []
        for user in users:
            # 获取部门信息
            dept_obj = None
            if user.dept_id:
                dept = await user_service.get_department_by_id(user.dept_id)
                if dept:
                    dept_obj = {
                        "id": dept.id,
                        "name": dept.dept_name
                    }

            # 获取用户角色
            roles = []
            user_roles = user.get_roles()
            for role in user_roles:
                roles.append({
                    "id": role.id,
                    "name": role.role_name
                })

            user_data = {
                "id": user.id,  # 前端期望id而不是user_id
                "username": user.username,
                "nickname": user.username,  # 如果没有nickname字段，使用username
                "email": user.email or "",
                "mobile": user.mobile or "",
                "dept": dept_obj,  # 前端期望dept对象
                "roles": roles,  # 前端期望roles数组
                "is_superuser": user.is_superuser if hasattr(user, 'is_superuser') else False,
                "is_active": user.status == '1' if user.status else True,  # 前端期望is_active布尔值
                "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user, 'last_login') and user.last_login else None,
                "created_at": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else ""
            }
            user_list.append(user_data)

        # 按照vue-fastapi-admin的分页格式,直接返回数组
        return Success(data=user_list)

    except Exception as e:
        return Fail(msg=f"获取用户列表失败: {str(e)}")


@router.get("/get", summary="获取单个用户")
async def get_user_detail(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个用户的详细信息

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)
        user = await user_service.get_user_with_roles(user_id)

        if not user:
            return Fail(msg="用户不存在")

        # 获取角色ID列表
        role_ids = []
        user_roles = user.get_roles()
        role_ids = [role.id for role in user_roles]

        # 按照vue-fastapi-admin的响应格式
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "nickname": user.username,  # 如果没有nickname字段，使用username
            "email": user.email or "",
            "mobile": user.mobile or "",
            "dept_id": user.dept_id,
            "status": int(user.status) if user.status else 1,
            "role_ids": role_ids
        }

        return Success(data=user_data)

    except Exception as e:
        return Fail(msg=f"获取用户详情失败: {str(e)}")


@router.post("/create", summary="创建用户")
async def create_user(
    username: str = Body(..., description="用户名"),
    password: str = Body(..., description="密码"),
    nickname: Optional[str] = Body(None, description="昵称"),
    email: Optional[str] = Body(None, description="邮箱"),
    mobile: Optional[str] = Body(None, description="手机号"),
    dept_id: Optional[int] = Body(None, description="部门ID"),
    is_active: bool = Body(True, description="是否启用"),
    is_superuser: bool = Body(False, description="是否为超级用户"),
    role_ids: List[int] = Body(default=[], description="角色ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新用户

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)

        # 检查用户名是否已存在
        existing_user = await user_service.get_user_by_username(username)
        if existing_user:
            return Fail(msg="用户名已存在")

        # 检查邮箱是否已存在
        if email:
            existing_email = await user_service.get_user_by_email(email)
            if existing_email:
                return Fail(msg="邮箱已存在")

        # 创建用户
        new_user = user_service.create_user(
            username=username,
            password=password,
            email=email,
            mobile=mobile,
            dept_id=dept_id,
            ssex='2',  # 默认保密
            avatar=None,
            description=None
        )

        # 设置用户状态和超级用户标识
        new_user.status = '1' if is_active else '0'
        if hasattr(new_user, 'is_superuser'):
            new_user.is_superuser = is_superuser
        user_service.db.commit()

        # 分配角色
        if role_ids:
            await user_service.assign_roles_to_user(new_user.id, role_ids)

        return Success(data={"id": new_user.id}, msg="创建成功")

    except ValueError as e:
        return Fail(msg=str(e))
    except Exception as e:
        return Fail(msg=f"创建用户失败: {str(e)}")


@router.post("/update", summary="更新用户")
async def update_user(
    id: int = Body(..., description="用户ID"),  # 前端传id而不是user_id
    nickname: Optional[str] = Body(None, description="昵称"),
    email: Optional[str] = Body(None, description="邮箱"),
    mobile: Optional[str] = Body(None, description="手机号"),
    dept_id: Optional[int] = Body(None, description="部门ID"),
    is_active: bool = Body(True, description="是否启用"),
    is_superuser: Optional[bool] = Body(None, description="是否为超级用户"),
    role_ids: List[int] = Body(default=[], description="角色ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)

        # 检查用户是否存在
        user = await user_service.get_user_by_id(id)
        if not user:
            return Fail(msg="用户不存在")

        # 检查邮箱是否已被其他用户使用
        if email and email != user.email:
            existing_email = await user_service.get_user_by_email(email)
            if existing_email and existing_email.id != id:
                return Fail(msg="邮箱已被其他用户使用")

        # 更新用户基本信息
        if email is not None:
            user.email = email
        if mobile is not None:
            user.mobile = mobile
        if dept_id is not None:
            user.dept_id = dept_id
        user.status = '1' if is_active else '0'
        if is_superuser is not None and hasattr(user, 'is_superuser'):
            user.is_superuser = is_superuser

        user_service.db.commit()

        # 更新角色
        if role_ids is not None:
            await user_service.assign_roles_to_user(id, role_ids)

        return Success(msg="更新成功")

    except Exception as e:
        user_service.db.rollback()
        return Fail(msg=f"更新用户失败: {str(e)}")


@router.delete("/delete", summary="删除用户")
async def delete_user(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)

        # 检查用户是否存在
        user = await user_service.get_user_by_id(user_id)
        if not user:
            return Fail(msg="用户不存在")

        # 不能删除自己
        if user_id == current_user.id:
            return Fail(msg="不能删除自己")

        # 删除用户（软删除）
        await user_service.delete_user(user_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除用户失败: {str(e)}")


@router.post("/reset_password", summary="重置用户密码")
async def reset_user_password(
    request: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重置用户密码

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)

        user_id = request.get('user_id')
        new_password = request.get('new_password')

        if not user_id or not new_password:
            return Fail(msg="缺少必需参数")

        # 检查用户是否存在
        user = await user_service.get_user_by_id(user_id)
        if not user:
            return Fail(msg="用户不存在")

        # 重置密码
        new_password_hash = get_password_hash(new_password)
        await user_service.update_password(user_id, new_password_hash)

        return Success(msg="密码重置成功")

    except Exception as e:
        return Fail(msg=f"重置密码失败: {str(e)}")

