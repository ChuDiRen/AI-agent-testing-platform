"""
权限管理控制器
提供权限配置、批量授权、权限查询等API接口
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.middleware.auth import (
    get_current_user_with_audit,
    rbac_auth
)
from app.service.permission_cache_service import PermissionCacheService
from app.service.audit_log_service import AuditLogService
from app.service.data_permission_service import DataPermissionService
from app.service.rbac_user_service import RBACUserService
from app.service.role_service import RoleService
from app.service.menu_service import MenuService
from app.dto.base import BaseResponse
from app.entity.user import User

logger = get_logger(__name__)
router = APIRouter(prefix="/permission", tags=["权限管理"])


class PermissionController:
    """权限管理控制器类"""
    
    def __init__(self):
        # 所有服务需要数据库会话，延迟初始化
        self.permission_cache_service = None
        self.audit_service = None
        self.data_permission_service = None
        self.user_service = None
        self.role_service = None
        self.menu_service = None
    
    def _get_user_service(self, db: Session):
        """获取用户服务实例"""
        if not self.user_service:
            self.user_service = RBACUserService(db)
        return self.user_service
    
    def _get_role_service(self, db: Session):
        """获取角色服务实例"""
        if not self.role_service:
            self.role_service = RoleService(db)
        return self.role_service
    
    def _get_menu_service(self, db: Session):
        """获取菜单服务实例"""
        if not self.menu_service:
            self.menu_service = MenuService(db)
        return self.menu_service
    
    def _get_audit_service(self, db: Session):
        """获取审计日志服务实例"""
        if not self.audit_service:
            self.audit_service = AuditLogService(db)
        return self.audit_service
    
    def _get_data_permission_service(self, db: Session):
        """获取数据权限服务实例"""
        if not self.data_permission_service:
            self.data_permission_service = DataPermissionService(db)
        return self.data_permission_service


# 创建控制器实例
permission_controller = PermissionController()


@router.get("/user/{user_id}/permissions", summary="获取用户权限列表")
async def get_user_permissions(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_with_audit),
    db: Session = Depends(get_db)
):
    """获取指定用户的权限列表"""
    try:
        # 检查权限
        if current_user.user_id != user_id:
            # 需要管理员权限才能查看其他用户权限
            user_service = permission_controller._get_user_service(db)
            if not user_service.has_permission(current_user.user_id, "user:permission:view"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足，无法查看其他用户权限"
                )
        
        # 获取用户权限
        permissions = await permission_controller.permission_cache_service.get_user_permissions(user_id)
        
        return BaseResponse(
            code=200,
            message="获取用户权限成功",
            data={"user_id": user_id, "permissions": permissions}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户权限失败"
        )


@router.get("/user/{user_id}/menus", summary="获取用户菜单树")
async def get_user_menus(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_with_audit),
    db: Session = Depends(get_db)
):
    """获取指定用户的菜单树"""
    try:
        # 检查权限
        if current_user.user_id != user_id:
            user_service = permission_controller._get_user_service(db)
            if not user_service.has_permission(current_user.user_id, "user:menu:view"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足，无法查看其他用户菜单"
                )
        
        # 获取用户菜单
        menus = await permission_controller.permission_cache_service.get_user_menus(user_id)
        
        return BaseResponse(
            code=200,
            message="获取用户菜单成功",
            data={"user_id": user_id, "menus": menus}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户菜单失败"
        )


@router.get("/role/{role_id}/permissions", summary="获取角色权限列表")
async def get_role_permissions(
    role_id: int,
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("role:permission:view", "ROLE")),
    db: Session = Depends(get_db)
):
    """获取指定角色的权限列表"""
    try:
        # 获取角色权限
        permissions = await permission_controller.permission_cache_service.get_role_permissions(role_id)
        
        return BaseResponse(
            code=200,
            message="获取角色权限成功",
            data={"role_id": role_id, "permissions": permissions}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取角色权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色权限失败"
        )


@router.get("/menus/tree", summary="获取完整菜单树")
async def get_menu_tree(
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("menu:view", "MENU")),
    db: Session = Depends(get_db)
):
    """获取完整菜单树结构"""
    try:
        # 获取菜单树
        menu_tree = await permission_controller.permission_cache_service.get_menu_tree()
        
        return BaseResponse(
            code=200,
            message="获取菜单树成功",
            data={"menu_tree": menu_tree}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取菜单树失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单树失败"
        )


@router.post("/user/{user_id}/roles/batch", summary="批量分配用户角色")
async def batch_assign_user_roles(
    user_id: int,
    role_ids: List[int],
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("user:role:assign", "USER")),
    db: Session = Depends(get_db)
):
    """批量分配用户角色"""
    try:
        user_service = permission_controller._get_user_service(db)
        
        # 清除现有角色
        user_service.clear_user_roles(user_id)
        
        # 分配新角色
        for role_id in role_ids:
            user_service.assign_role_to_user(user_id, role_id)
        
        # 清除用户权限缓存
        await permission_controller.permission_cache_service.invalidate_user_cache(user_id)
        
        return BaseResponse(
            code=200,
            message="批量分配用户角色成功",
            data={"user_id": user_id, "role_ids": role_ids}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量分配用户角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量分配用户角色失败"
        )


@router.post("/role/{role_id}/menus/batch", summary="批量分配角色菜单权限")
async def batch_assign_role_menus(
    role_id: int,
    menu_ids: List[int],
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("role:menu:assign", "ROLE")),
    db: Session = Depends(get_db)
):
    """批量分配角色菜单权限"""
    try:
        role_service = permission_controller._get_role_service(db)
        
        # 清除现有菜单权限
        role_service.clear_role_menus(role_id)
        
        # 分配新菜单权限
        for menu_id in menu_ids:
            role_service.assign_menu_to_role(role_id, menu_id)
        
        # 清除角色权限缓存
        await permission_controller.permission_cache_service.invalidate_role_cache(role_id)
        
        return BaseResponse(
            code=200,
            message="批量分配角色菜单权限成功",
            data={"role_id": role_id, "menu_ids": menu_ids}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量分配角色菜单权限失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量分配角色菜单权限失败"
        )


@router.post("/data-permission/rules", summary="创建数据权限规则")
async def create_data_permission_rule(
    rule_data: Dict[str, Any],
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("data:permission:create", "DATA_PERMISSION")),
    db: Session = Depends(get_db)
):
    """创建数据权限规则"""
    try:
        rule = await permission_controller.data_permission_service.create_data_permission_rule(
            resource_type=rule_data.get("resource_type"),
            permission_type=rule_data.get("permission_type"),
            user_ids=rule_data.get("user_ids"),
            role_ids=rule_data.get("role_ids"),
            dept_ids=rule_data.get("dept_ids"),
            rule_expression=rule_data.get("rule_expression"),
            priority=rule_data.get("priority", 1),
            description=rule_data.get("description")
        )
        
        return BaseResponse(
            code=200,
            message="创建数据权限规则成功",
            data={"rule_id": rule.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建数据权限规则失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建数据权限规则失败"
        )


@router.get("/cache/stats", summary="获取权限缓存统计")
async def get_cache_stats(
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("cache:stats:view", "CACHE")),
    db: Session = Depends(get_db)
):
    """获取权限缓存统计信息"""
    try:
        stats = await permission_controller.permission_cache_service.get_cache_stats()
        
        return BaseResponse(
            code=200,
            message="获取缓存统计成功",
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取缓存统计失败"
        )


@router.post("/cache/refresh", summary="刷新权限缓存")
async def refresh_permission_cache(
    request: Request,
    cache_type: Optional[str] = Query(None, description="缓存类型：user_permissions, user_menus, role_permissions, menu_tree, all"),
    current_user: User = Depends(rbac_auth.require_permission_with_audit("cache:refresh", "CACHE")),
    db: Session = Depends(get_db)
):
    """刷新权限缓存"""
    try:
        if cache_type == "all" or cache_type is None:
            await permission_controller.permission_cache_service.refresh_all_cache()
            message = "刷新所有权限缓存成功"
        elif cache_type == "menu_tree":
            await permission_controller.permission_cache_service.invalidate_menu_cache()
            message = "刷新菜单缓存成功"
        else:
            # 其他类型的缓存刷新可以根据需要扩展
            await permission_controller.permission_cache_service.refresh_all_cache()
            message = f"刷新{cache_type}缓存成功"
        
        return BaseResponse(
            code=200,
            message=message,
            data={"cache_type": cache_type or "all"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新权限缓存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新权限缓存失败"
        )


@router.post("/cache/config", summary="设置缓存配置")
async def set_cache_config(
    config_data: Dict[str, Any],
    request: Request,
    current_user: User = Depends(rbac_auth.require_permission_with_audit("cache:config:update", "CACHE")),
    db: Session = Depends(get_db)
):
    """设置缓存配置"""
    try:
        await permission_controller.permission_cache_service.set_cache_config(
            cache_type=config_data.get("cache_type"),
            ttl=config_data.get("ttl"),
            enabled=config_data.get("enabled", True)
        )
        
        return BaseResponse(
            code=200,
            message="设置缓存配置成功",
            data=config_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置缓存配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="设置缓存配置失败"
        )


# 导出路由
__all__ = ["router"]