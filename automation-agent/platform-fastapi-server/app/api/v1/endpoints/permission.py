"""
权限查询 API 端点
提供用户信息、菜单、API权限等查询接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.permission import permission
from app.core.security import verify_token
from app.models.user import User
from app.schemas.permission import (
    UserInfoResponse,
    UserMenusResponse,
    UserApisResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
)
from app.core.resp_model import RespModel
from app.core.exceptions import BadRequestException

router = APIRouter(tags=["权限"])


@router.get("/userinfo", response_model=RespModel)
async def get_user_info(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取当前登录用户信息
    
    返回用户基本信息和角色列表
    """
    # 从 token 中获取用户 ID
    user_id = token.get("user_id") if isinstance(token, dict) else token.get("sub")
    
    # 查询用户信息
    from app.crud.user import user_crud
    db_user = await user_crud.get(db, user_id)
    
    if not db_user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("用户不存在")
    
    # 查询用户角色
    roles = await permission.get_user_roles(db, user_id)
    
    # 构建响应
    user_info = UserInfoResponse(
        id=db_user.id,
        username=db_user.username,
        alias=db_user.alias,
        email=db_user.email,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        dept_id=db_user.dept_id,
        roles=[{"id": role.id, "name": role.name, "desc": role.desc} for role in roles]
    )
    
    return RespModel(code=200, msg="获取成功", data=user_info)


@router.get("/usermenu", response_model=RespModel)
async def get_user_menus(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取当前用户的菜单树

    超级管理员返回所有菜单，普通用户返回角色关联的菜单
    """
    # 从 token 中获取用户 ID
    user_id = token.get("user_id") if isinstance(token, dict) else token.get("sub")

    # 查询用户菜单
    menus = await permission.get_user_menus(db, user_id, include_hidden=False)

    # 将Menu对象转换为字典（包含所有必要字段）
    menu_list = [
        {
            "id": menu.id,
            "name": menu.name,
            "menu_type": menu.menu_type,
            "icon": menu.icon,
            "path": menu.path,
            "component": menu.component,
            "order": menu.order,
            "parent_id": menu.parent_id,
            "is_hidden": menu.is_hidden,
            "keepalive": menu.keepalive,
            "redirect": menu.redirect,
            "children": menu.children if hasattr(menu, 'children') else []
        }
        for menu in menus
    ]

    return RespModel(code=200, msg="获取成功", data=menu_list)


@router.get("/userapi", response_model=RespModel)
async def get_user_apis(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取当前用户的API权限列表
    
    返回格式：["get/api/v1/user/list", "post/api/v1/user/create", ...]
    """
    # 从 token 中获取用户 ID
    user_id = token.get("user_id") if isinstance(token, dict) else token.get("sub")
    
    # 查询用户API权限
    api_permissions = await permission.get_user_api_permissions(db, user_id)
    
    return RespModel(code=200, msg="获取成功", data=list(api_permissions))


@router.post("/check", response_model=RespModel)
async def check_permission(
    request: PermissionCheckRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    检查用户是否有权限访问指定API
    
    用于前端按钮级权限控制
    """
    # 从 token 中获取用户 ID
    user_id = token.get("user_id") if isinstance(token, dict) else token.get("sub")
    
    # 检查API权限
    has_perm = await permission.check_api_permission(
        db, user_id, request.api_path, request.method
    )
    
    return RespModel(
        code=200,
        msg="检查成功",
        data={"has_permission": has_perm}
    )


@router.post("/change-password", response_model=RespModel)
async def change_password(
    *,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token),
    old_password: str,
    new_password: str
):
    """
    修改用户密码
    
    需要验证旧密码
    """
    from app.crud.user import user_crud
    
    # 从 token 中获取用户 ID
    user_id = token.get("user_id") if isinstance(token, dict) else token.get("sub")
    
    # 查询用户
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise BadRequestException("用户不存在")
    
    # 验证旧密码
    if not db_user.check_password(old_password):
        raise BadRequestException("旧密码错误")
    
    # 检查新密码是否与旧密码相同
    if old_password == new_password:
        raise BadRequestException("新密码不能与旧密码相同")
    
    # 更新密码
    db_user.set_password(new_password)
    await db.commit()
    
    return RespModel(code=200, msg="密码修改成功")
