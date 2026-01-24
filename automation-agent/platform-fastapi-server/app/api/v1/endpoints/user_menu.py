"""
用户菜单和权限API端点
参考vue-fastapi-admin的实现
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any

from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.api import Api
from app.core.resp_model import RespModel, ResponseModel
from app.core.deps import get_current_user_model

router = APIRouter(prefix="/user", tags=["用户菜单"])


@router.get("/userinfo", response_model=ResponseModel)
async def get_user_info(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.role_objects))
            .where(User.id == current_user.id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        user_info = {
            "id": user.id,
            "username": user.username,
            "alias": user.alias,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            "avatar": "https://avatars.githubusercontent.com/u/54677442?v=4",
            "roles": [{"id": role.id, "name": role.name, "desc": role.desc} for role in user.role_objects]
        }

        return RespModel.ok_resp_simple(data=user_info, msg="获取用户信息成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/usermenu", response_model=ResponseModel)
async def get_user_menu(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的菜单权限 - 参考vue-fastapi-admin实现"""
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.role_objects).selectinload(Role.menu_objects))
            .where(User.id == current_user.id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        menus: List[Menu] = []

        if user.is_superuser:  # 超级管理员获取所有菜单
            result = await db.execute(select(Menu).order_by(Menu.order.asc()))
            menus = list(result.scalars().all())
        else:  # 普通用户按角色获取菜单
            for role in user.role_objects:
                for menu in role.menu_objects:
                    if menu not in menus:
                        menus.append(menu)

        # 构建菜单树结构 - 与vue-fastapi-admin保持一致
        parent_menus = [m for m in menus if m.parent_id == 0]
        menu_tree = []

        for parent_menu in sorted(parent_menus, key=lambda x: x.order):
            parent_dict = {
                "id": parent_menu.id,
                "name": parent_menu.name,
                "path": parent_menu.path,
                "component": parent_menu.component,
                "icon": parent_menu.icon,
                "order": parent_menu.order,
                "parent_id": parent_menu.parent_id,
                "is_hidden": parent_menu.is_hidden,
                "keepalive": parent_menu.keepalive,
                "redirect": parent_menu.redirect,
                "menu_type": parent_menu.menu_type,
                "children": []
            }

            child_menus = [m for m in menus if m.parent_id == parent_menu.id]
            for child_menu in sorted(child_menus, key=lambda x: x.order):
                parent_dict["children"].append({
                    "id": child_menu.id,
                    "name": child_menu.name,
                    "path": child_menu.path,
                    "component": child_menu.component,
                    "icon": child_menu.icon,
                    "order": child_menu.order,
                    "parent_id": child_menu.parent_id,
                    "is_hidden": child_menu.is_hidden,
                    "keepalive": child_menu.keepalive,
                    "redirect": child_menu.redirect,
                    "menu_type": child_menu.menu_type
                })

            menu_tree.append(parent_dict)

        return RespModel.ok_resp_simple_list(lst=menu_tree, msg="获取用户菜单成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/userapi", response_model=ResponseModel)
async def get_user_api(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的API权限 - 参考vue-fastapi-admin实现"""
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.role_objects).selectinload(Role.api_objects))
            .where(User.id == current_user.id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        apis: List[str] = []

        if user.is_superuser:  # 超级管理员获取所有API
            result = await db.execute(select(Api))
            apis = [f"{api.method.lower()}{api.path}" for api in result.scalars().all()]
        else:  # 普通用户按角色获取API
            for role in user.role_objects:
                for api in role.api_objects:
                    api_str = f"{api.method.lower()}{api.path}"
                    if api_str not in apis:
                        apis.append(api_str)

        return RespModel.ok_resp_simple_list(lst=apis, msg="获取用户API权限成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
