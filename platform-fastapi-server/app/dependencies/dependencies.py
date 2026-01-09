"""依赖注入函数"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.security.JwtUtil import JwtUtils

security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    l_token: Optional[str] = Cookie(None, alias="l-token")
) -> dict: # JWT认证依赖
    token = None
    
    # 1. 尝试从 Authorization Header 获取
    if credentials:
        token = credentials.credentials
    
    # 2. 尝试从 Cookie 获取
    if not token and l_token:
        token = l_token
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = JwtUtils.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户权限信息
    user_id = int(payload.get("sub", 0))
    if user_id > 0:
        from app.database.database import engine
        from sqlmodel import Session, select
        from app.models.UserRoleModel import UserRole
        from app.models.RoleMenuModel import RoleMenu
        from app.models.MenuModel import Menu
        
        with Session(engine) as session:
            # 获取用户角色
            user_roles = session.exec(select(UserRole).where(UserRole.user_id == user_id)).all()
            role_ids = [ur.role_id for ur in user_roles]
            
            # 获取角色菜单权限
            permissions = []
            if role_ids:
                role_menus = session.exec(select(RoleMenu).where(RoleMenu.role_id.in_(role_ids))).all()
                menu_ids = [rm.menu_id for rm in role_menus]
                if menu_ids:
                    menus = session.exec(select(Menu).where(Menu.id.in_(menu_ids))).all()
                    permissions = [menu.perms for menu in menus if menu.perms]
            
            payload["permissions"] = permissions
            payload["id"] = user_id
    
    return payload

def check_permission(permission: str): # 权限检查依赖
    """
    权限检查依赖生成器
    :param permission: 需要的权限标识，如 'user:add'
    :return: 依赖函数
    """
    def _check_permission(user: dict = Depends(get_current_user)):
        # 超级管理员直接放行
        if user.get("username") == "admin":
            return True
            
        # 获取用户权限列表
        permissions = user.get("permissions", [])
        
        # 检查权限
        if permission not in permissions:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {permission}"
            )
        return True
    return _check_permission

