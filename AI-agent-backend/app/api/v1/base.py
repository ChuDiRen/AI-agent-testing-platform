"""
基础模块API - 兼容vue-fastapi-admin格式
提供登录、用户信息、菜单、API权限等基础功能
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.entity.user import User
from app.entity.role import Role
from app.entity.menu import Menu
from app.entity.api_endpoint import ApiEndpoint
from app.dto.auth_dto import LoginRequest, LoginResponse, UserInfoResponse
from app.dto.base_dto import Success, Fail
from app.service.auth_service import AuthService
from app.service.user_service import UserService
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/access_token", summary="获取token")
async def login_access_token(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录获取访问令牌"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(credentials.username, credentials.password)
        
        if not user:
            return Fail(msg="用户名或密码错误")
        
        if not user.is_active:
            return Fail(msg="用户已被禁用")
        
        # 更新最后登录时间
        user_service = UserService(db)
        await user_service.update_last_login(user.id)
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        response_data = LoginResponse(
            access_token=access_token,
            username=user.username,
            token_type="bearer"
        )
        
        return Success(data=response_data.dict())
        
    except Exception as e:
        return Fail(msg=f"登录失败: {str(e)}")


@router.get("/userinfo", summary="查看用户信息")
async def get_userinfo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    try:
        user_service = UserService(db)
        user_info = await user_service.get_user_with_roles(current_user.id)
        
        # 构建用户信息响应
        user_data = UserInfoResponse(
            id=user_info.id,
            username=user_info.username,
            email=user_info.email or "",
            avatar="https://avatars.githubusercontent.com/u/54677442?v=4",  # 默认头像
            roles=[role.name for role in user_info.roles] if user_info.roles else [],
            is_superuser=user_info.is_superuser,
            is_active=user_info.is_active
        )
        
        return Success(data=user_data.dict())
        
    except Exception as e:
        return Fail(msg=f"获取用户信息失败: {str(e)}")


@router.get("/usermenu", summary="查看用户菜单")
async def get_user_menu(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户菜单权限"""
    try:
        user_service = UserService(db)
        menus = await user_service.get_user_menus(current_user.id)
        
        # 构建菜单树结构
        menu_tree = []
        parent_menus = [menu for menu in menus if menu.parent_id == 0]
        
        for parent_menu in parent_menus:
            parent_dict = {
                "id": parent_menu.id,
                "name": parent_menu.name,
                "path": parent_menu.path,
                "component": parent_menu.component,
                "icon": parent_menu.icon,
                "order": parent_menu.order_num,
                "is_hidden": not parent_menu.is_visible,
                "keepalive": parent_menu.keep_alive,
                "redirect": parent_menu.redirect,
                "children": []
            }
            
            # 查找子菜单
            child_menus = [menu for menu in menus if menu.parent_id == parent_menu.id]
            for child_menu in child_menus:
                child_dict = {
                    "id": child_menu.id,
                    "name": child_menu.name,
                    "path": child_menu.path,
                    "component": child_menu.component,
                    "icon": child_menu.icon,
                    "order": child_menu.order_num,
                    "is_hidden": not child_menu.is_visible,
                    "keepalive": child_menu.keep_alive
                }
                parent_dict["children"].append(child_dict)
            
            menu_tree.append(parent_dict)
        
        return Success(data=menu_tree)
        
    except Exception as e:
        return Fail(msg=f"获取用户菜单失败: {str(e)}")


@router.get("/userapi", summary="查看用户API")
async def get_user_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户API权限"""
    try:
        user_service = UserService(db)
        apis = await user_service.get_user_apis(current_user.id)
        
        # 构建API权限列表 (method + path格式)
        api_permissions = []
        for api in apis:
            permission = f"{api.method.lower()}{api.path}"
            api_permissions.append(permission)
        
        return Success(data=api_permissions)
        
    except Exception as e:
        return Fail(msg=f"获取用户API权限失败: {str(e)}")


@router.post("/update_password", summary="修改密码")
async def update_user_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    try:
        # 验证旧密码
        if not verify_password(old_password, current_user.password_hash):
            return Fail(msg="旧密码验证错误！")
        
        # 更新密码
        user_service = UserService(db)
        new_password_hash = get_password_hash(new_password)
        await user_service.update_password(current_user.id, new_password_hash)
        
        return Success(msg="修改成功")
        
    except Exception as e:
        return Fail(msg=f"修改密码失败: {str(e)}")
