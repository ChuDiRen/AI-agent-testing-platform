"""
Base模块API - 完全按照vue-fastapi-admin标准实现
提供登录、用户信息、菜单、API权限等基础功能
"""

from datetime import timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.entity.user import User
from app.dto.auth_dto import LoginRequest, UpdatePasswordRequest
from app.dto.base_dto import Success, Fail
from app.service.auth_service import AuthService
from app.service.user_service import RBACUserService
from app.utils.permissions import get_current_user

router = APIRouter()

@router.post("/access_token", summary="用户登录")
async def login_access_token(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录获取访问令牌

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(credentials.username, credentials.password)

        if not user:
            return Fail(msg="用户名或密码错误")

        if not user.is_active():
            return Fail(msg="用户已被禁用")

        # 更新最后登录时间
        user_service = RBACUserService(db)
        await user_service.update_last_login(user.id)

        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )

        # 按照vue-fastapi-admin的响应格式
        response_data = {
            "access_token": access_token,
            "token_type": "bearer"
        }

        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"登录失败: {str(e)}")


@router.get("/userinfo", summary="获取用户信息")
async def get_userinfo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        user_service = RBACUserService(db)
        user_info = await user_service.get_user_with_roles(current_user.id)

        # 获取部门信息
        dept_name = ""
        if user_info.dept_id:
            dept = await user_service.get_department_by_id(user_info.dept_id)
            if dept:
                dept_name = dept.dept_name

        # 构建角色列表
        roles = []
        if user_info.roles:
            for role in user_info.roles:
                roles.append({
                    "role_id": role.id,
                    "role_name": role.role_name
                })

        # 按照vue-fastapi-admin的响应格式
        user_data = {
            "user_id": user_info.id,
            "username": user_info.username,
            "nickname": user_info.username,  # 如果没有nickname字段，使用username
            "email": user_info.email or "",
            "mobile": user_info.mobile or "",
            "avatar": user_info.avatar if user_info.avatar and user_info.avatar != "default.jpg" else "https://avatars.githubusercontent.com/u/54677442?v=4",
            "dept_id": user_info.dept_id,
            "dept_name": dept_name,
            "roles": roles
        }

        return Success(data=user_data)

    except Exception as e:
        return Fail(msg=f"获取用户信息失败: {str(e)}")


@router.get("/usermenu", summary="获取用户菜单")
async def get_user_menu(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的菜单权限树

    完全按照vue-fastapi-admin的接口规范实现
    返回树形结构的菜单数据
    """
    try:
        user_service = RBACUserService(db)
        menus = await user_service.get_user_menus(current_user.id)

        # 构建菜单树结构
        def build_menu_tree(parent_id: int = 0) -> List[Dict[str, Any]]:
            """递归构建菜单树"""
            tree = []
            for menu in menus:
                if menu.parent_id == parent_id:
                    menu_dict = {
                        "menu_id": menu.id,
                        "parent_id": menu.parent_id,
                        "menu_name": menu.menu_name,
                        "path": menu.path or "",
                        "component": menu.component or "",
                        "icon": menu.icon or "",
                        "menu_type": menu.menu_type,
                        "order_num": menu.order_num or 0,
                        "children": build_menu_tree(menu.id)
                    }
                    tree.append(menu_dict)

            # 按order_num排序
            tree.sort(key=lambda x: x["order_num"])
            return tree

        menu_tree = build_menu_tree()

        return Success(data=menu_tree)

    except Exception as e:
        return Fail(msg=f"获取用户菜单失败: {str(e)}")


@router.get("/userapi", summary="获取用户API权限")
async def get_user_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的API权限列表

    完全按照vue-fastapi-admin的接口规范实现
    返回权限标识数组，如: ["user:view", "user:create"]
    """
    try:
        user_service = RBACUserService(db)
        apis = await user_service.get_user_apis(current_user.id)

        # 构建API权限列表
        api_permissions = []
        for api in apis:
            # 如果API有perms字段，使用perms；否则使用method+path格式
            if hasattr(api, 'perms') and api.perms:
                api_permissions.append(api.perms)
            else:
                # 兼容旧格式：method + path
                permission = f"{api.method.lower()}{api.path}"
                api_permissions.append(permission)

        return Success(data=api_permissions)

    except Exception as e:
        return Fail(msg=f"获取用户API权限失败: {str(e)}")


@router.post("/update_password", summary="修改密码")
async def update_user_password(
    request: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        # 验证旧密码
        if not verify_password(request.old_password, current_user.password):
            return Fail(msg="旧密码错误")

        # 更新密码
        user_service = RBACUserService(db)
        new_password_hash = get_password_hash(request.new_password)
        await user_service.update_password(current_user.id, new_password_hash)

        return Success(msg="密码修改成功")

    except Exception as e:
        return Fail(msg=f"修改密码失败: {str(e)}")
