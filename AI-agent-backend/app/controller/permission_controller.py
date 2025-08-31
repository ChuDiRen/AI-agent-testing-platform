"""
权限管理控制器
提供权限配置、批量授权、权限查询等API接口
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import BaseResponse
from app.entity.user import User
from app.middleware.auth import (
    get_current_user_with_audit,
    rbac_auth
)
from app.service.audit_log_service import AuditLogService
from app.service.data_permission_service import DataPermissionService
from app.service.menu_service import MenuService
from app.service.user_service import RBACUserService
from app.service.role_service import RoleService

logger = get_logger(__name__)
router = APIRouter(prefix="/permissions", tags=["权限管理"])


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


@router.post("/get-user-permissions", summary="获取用户权限列表")
async def get_user_permissions(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user_with_audit),
    db: Session = Depends(get_db)
):
    """获取指定用户的权限列表"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID不能为空"
            )

        # 检查权限
        if current_user.id != user_id:
            # 需要管理员权限才能查看其他用户权限
            user_service = permission_controller._get_user_service(db)
            if not user_service.has_permission(current_user.id, "user:permission:view"):
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


@router.post("/get-user-menus", summary="获取用户菜单树")
async def get_user_menus(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user_with_audit),
    db: Session = Depends(get_db)
):
    """获取指定用户的菜单树"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID不能为空"
            )

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


@router.post("/get-role-permissions", summary="获取角色权限列表")
async def get_role_permissions(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("role:permission:view", "ROLE")),
    db: Session = Depends(get_db)
):
    """获取指定角色的权限列表"""
    try:
        role_id = request.get("role_id")
        if not role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色ID不能为空"
            )

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


@router.post("/get-permission-menu-tree", summary="获取权限管理菜单树")
async def get_permission_menu_tree(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("menu:view", "MENU")),
    db: Session = Depends(get_db)
):
    """获取权限管理相关的菜单树结构"""
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


@router.post("/batch-assign-user-roles", summary="批量分配用户角色")
async def batch_assign_user_roles(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("user:role:assign", "USER")),
    db: Session = Depends(get_db)
):
    """批量分配用户角色"""
    try:
        user_id = request.get("user_id")
        role_ids = request.get("role_ids", [])

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID不能为空"
            )

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


@router.post("/batch-assign-role-menus", summary="批量分配角色菜单权限")
async def batch_assign_role_menus(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("role:menu:assign", "ROLE")),
    db: Session = Depends(get_db)
):
    """批量分配角色菜单权限"""
    try:
        role_id = request.get("role_id")
        menu_ids = request.get("menu_ids", [])

        if not role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色ID不能为空"
            )

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


@router.post("/create-data-permission-rule", summary="创建数据权限规则")
async def create_data_permission_rule(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("data:permission:create", "DATA_PERMISSION")),
    db: Session = Depends(get_db)
):
    """创建数据权限规则"""
    try:
        rule = await permission_controller.data_permission_service.create_data_permission_rule(
            resource_type=request.get("resource_type"),
            permission_type=request.get("permission_type"),
            user_ids=request.get("user_ids"),
            role_ids=request.get("role_ids"),
            dept_ids=request.get("dept_ids"),
            rule_expression=request.get("rule_expression"),
            priority=request.get("priority", 1),
            description=request.get("description")
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


@router.post("/get-cache-statistics", summary="获取权限缓存统计")
async def get_cache_statistics(
    request: Dict[str, Any],
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


@router.post("/refresh-permission-cache", summary="刷新权限缓存")
async def refresh_permission_cache(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("cache:refresh", "CACHE")),
    db: Session = Depends(get_db)
):
    """刷新权限缓存"""
    try:
        cache_type = request.get("cache_type")
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


@router.post("/set-cache-config", summary="设置缓存配置")
async def set_cache_config(
    request: Dict[str, Any],
    current_user: User = Depends(rbac_auth.require_permission_with_audit("cache:config:update", "CACHE")),
    db: Session = Depends(get_db)
):
    """设置缓存配置"""
    try:
        await permission_controller.permission_cache_service.set_cache_config(
            cache_type=request.get("cache_type"),
            ttl=request.get("ttl"),
            enabled=request.get("enabled", True)
        )

        return BaseResponse(
            code=200,
            message="设置缓存配置成功",
            data=request
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