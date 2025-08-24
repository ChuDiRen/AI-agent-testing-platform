"""
权限缓存服务
管理用户权限和菜单权限的缓存机制
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import json

from app.core.logger import get_logger
from app.utils.redis_client import cache_client
from app.service.rbac_user_service import RBACUserService
from app.db.session import get_db

logger = get_logger(__name__)


class PermissionCacheService:
    """权限缓存服务类"""
    
    # 缓存键前缀
    USER_PERMISSIONS_PREFIX = "user_permissions:"
    USER_MENUS_PREFIX = "user_menus:"
    ROLE_PERMISSIONS_PREFIX = "role_permissions:"
    MENU_TREE_PREFIX = "menu_tree:"
    CACHE_CONFIG_PREFIX = "cache_config:"
    
    # 默认缓存时间（秒）
    DEFAULT_TTL = 3600  # 1小时
    MENU_TREE_TTL = 7200  # 2小时
    
    def __init__(self):
        # 不在初始化时创建Repository，而是在需要时通过数据库会话创建
        pass
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户权限列表（优先从缓存获取）"""
        cache_key = f"{self.USER_PERMISSIONS_PREFIX}{user_id}"
        
        # 尝试从缓存获取
        cached_permissions = cache_client.get(cache_key)
        if cached_permissions is not None:
            logger.debug(f"从缓存获取用户权限: user_id={user_id}")
            return cached_permissions if isinstance(cached_permissions, list) else []
        
        # 缓存未命中，从数据库查询
        permissions = await self._load_user_permissions_from_db(user_id)
        
        # 存入缓存
        ttl = await self._get_cache_ttl("user_permissions")
        cache_client.set(cache_key, permissions, ttl)
        logger.debug(f"用户权限已缓存: user_id={user_id}, permissions_count={len(permissions)}")
        
        return permissions
    
    async def get_user_menus(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户菜单树（优先从缓存获取）"""
        cache_key = f"{self.USER_MENUS_PREFIX}{user_id}"
        
        # 尝试从缓存获取
        cached_menus = cache_client.get(cache_key)
        if cached_menus is not None:
            logger.debug(f"从缓存获取用户菜单: user_id={user_id}")
            return cached_menus if isinstance(cached_menus, list) else []
        
        # 缓存未命中，从数据库查询
        menus = await self._load_user_menus_from_db(user_id)
        
        # 存入缓存
        ttl = await self._get_cache_ttl("user_menus")
        cache_client.set(cache_key, menus, ttl)
        logger.debug(f"用户菜单已缓存: user_id={user_id}, menus_count={len(menus)}")
        
        return menus
    
    async def get_role_permissions(self, role_id: int) -> List[str]:
        """获取角色权限列表（优先从缓存获取）"""
        cache_key = f"{self.ROLE_PERMISSIONS_PREFIX}{role_id}"
        
        # 尝试从缓存获取
        cached_permissions = cache_client.get(cache_key)
        if cached_permissions is not None:
            logger.debug(f"从缓存获取角色权限: role_id={role_id}")
            return cached_permissions if isinstance(cached_permissions, list) else []
        
        # 缓存未命中，从数据库查询
        permissions = await self._load_role_permissions_from_db(role_id)
        
        # 存入缓存
        ttl = await self._get_cache_ttl("role_permissions")
        cache_client.set(cache_key, permissions, ttl)
        logger.debug(f"角色权限已缓存: role_id={role_id}, permissions_count={len(permissions)}")
        
        return permissions
    
    async def get_menu_tree(self) -> List[Dict[str, Any]]:
        """获取完整菜单树（优先从缓存获取）"""
        cache_key = f"{self.MENU_TREE_PREFIX}all"
        
        # 尝试从缓存获取
        cached_tree = cache_client.get(cache_key)
        if cached_tree is not None:
            logger.debug("从缓存获取菜单树")
            return cached_tree if isinstance(cached_tree, list) else []
        
        # 缓存未命中，从数据库查询
        menu_tree = await self._load_menu_tree_from_db()
        
        # 存入缓存
        cache_client.set(cache_key, menu_tree, self.MENU_TREE_TTL)
        logger.debug(f"菜单树已缓存: menus_count={len(menu_tree)}")
        
        return menu_tree
    
    async def invalidate_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        user_permissions_key = f"{self.USER_PERMISSIONS_PREFIX}{user_id}"
        user_menus_key = f"{self.USER_MENUS_PREFIX}{user_id}"
        
        cache_client.delete(user_permissions_key)
        cache_client.delete(user_menus_key)
        
        logger.info(f"已清除用户缓存: user_id={user_id}")
    
    async def invalidate_role_cache(self, role_id: int):
        """清除角色相关缓存"""
        role_permissions_key = f"{self.ROLE_PERMISSIONS_PREFIX}{role_id}"
        cache_client.delete(role_permissions_key)
        
        # 清除所有使用该角色的用户缓存
        await self._invalidate_users_by_role(role_id)
        
        logger.info(f"已清除角色缓存: role_id={role_id}")
    
    async def invalidate_menu_cache(self):
        """清除菜单相关缓存"""
        # 清除菜单树缓存
        menu_tree_key = f"{self.MENU_TREE_PREFIX}all"
        cache_client.delete(menu_tree_key)
        
        # 清除所有用户菜单缓存
        cache_client.clear_pattern(f"{self.USER_MENUS_PREFIX}*")
        
        logger.info("已清除菜单缓存")
    
    async def refresh_all_cache(self):
        """刷新所有权限缓存"""
        # 清除所有权限相关缓存
        cache_client.clear_pattern(f"{self.USER_PERMISSIONS_PREFIX}*")
        cache_client.clear_pattern(f"{self.USER_MENUS_PREFIX}*")
        cache_client.clear_pattern(f"{self.ROLE_PERMISSIONS_PREFIX}*")
        cache_client.clear_pattern(f"{self.MENU_TREE_PREFIX}*")
        
        logger.info("已刷新所有权限缓存")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "cache_available": cache_client.is_available(),
            "cache_type": "redis" if cache_client.is_redis else "memory",
            "user_permissions_count": 0,
            "user_menus_count": 0,
            "role_permissions_count": 0,
            "menu_tree_cached": False
        }
        
        if cache_client.is_available():
            # 统计各类缓存数量（Redis模式下）
            if cache_client.is_redis:
                try:
                    # 这里简化统计，实际可以通过SCAN命令优化
                    stats["menu_tree_cached"] = cache_client.exists(f"{self.MENU_TREE_PREFIX}all")
                except Exception as e:
                    logger.error(f"获取缓存统计失败: {e}")
        
        return stats
    
    async def set_cache_config(self, cache_type: str, ttl: int, enabled: bool = True):
        """设置缓存配置"""
        # 简化实现，直接使用内存缓存配置
        config_key = f"{self.CACHE_CONFIG_PREFIX}{cache_type}"
        cache_client.set(config_key, {"ttl": ttl, "enabled": enabled}, 300)  # 5分钟缓存
        
        logger.info(f"缓存配置已更新: type={cache_type}, ttl={ttl}, enabled={enabled}")
    
    async def _load_user_permissions_from_db(self, user_id: int) -> List[str]:
        """从数据库加载用户权限"""
        try:
            db = next(get_db())
            try:
                user_service = RBACUserService(db)
                
                # 获取用户角色
                user_roles = user_service.get_user_roles(user_id)
                if not user_roles:
                    return []
                
                role_ids = [ur.role_id for ur in user_roles]
                permissions = set()
                
                # 获取每个角色的权限
                for role_id in role_ids:
                    role_permissions = await self._load_role_permissions_from_db(role_id)
                    permissions.update(role_permissions)
                
                return list(permissions)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"加载用户权限失败: {e}")
            return []
    
    async def _load_user_menus_from_db(self, user_id: int) -> List[Dict[str, Any]]:
        """从数据库加载用户菜单"""
        try:
            db = next(get_db())
            try:
                user_service = RBACUserService(db)
                
                # 获取用户角色
                user_roles = user_service.get_user_roles(user_id)
                if not user_roles:
                    return []
                
                role_ids = [ur.role_id for ur in user_roles]
                menu_ids = set()
                
                # 获取所有角色的菜单ID
                for role_id in role_ids:
                    role_menus = user_service.get_role_menus(role_id)
                    menu_ids.update([rm.menu_id for rm in role_menus])
                
                if not menu_ids:
                    return []
                
                # 获取菜单详情并构建树形结构
                menus = user_service.get_menus_by_ids(list(menu_ids))
                return self._build_menu_tree(menus)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"加载用户菜单失败: {e}")
            return []
    
    async def _load_role_permissions_from_db(self, role_id: int) -> List[str]:
        """从数据库加载角色权限"""
        try:
            db = next(get_db())
            try:
                user_service = RBACUserService(db)
                
                # 获取角色菜单
                role_menus = user_service.get_role_menus(role_id)
                if not role_menus:
                    return []
                
                menu_ids = [rm.menu_id for rm in role_menus]
                
                # 获取菜单权限
                menus = user_service.get_menus_by_ids(menu_ids)
                permissions = []
                
                for menu in menus:
                    if hasattr(menu, 'PERMISSION') and menu.PERMISSION:
                        permissions.append(menu.PERMISSION)
                
                return permissions
            finally:
                db.close()
        except Exception as e:
            logger.error(f"加载角色权限失败: {e}")
            return []
    
    async def _load_menu_tree_from_db(self) -> List[Dict[str, Any]]:
        """从数据库加载完整菜单树"""
        try:
            db = next(get_db())
            try:
                user_service = RBACUserService(db)
                menus = user_service.get_all_menus()
                return self._build_menu_tree(menus)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"加载菜单树失败: {e}")
            return []
    
    def _build_menu_tree(self, menus: List) -> List[Dict[str, Any]]:
        """构建菜单树形结构"""
        try:
            menu_dict = {}
            root_menus = []
            
            # 转换为字典格式
            for menu in menus:
                menu_data = {
                    "id": getattr(menu, 'MENU_ID', menu.id if hasattr(menu, 'id') else None),
                    "name": getattr(menu, 'MENU_NAME', menu.name if hasattr(menu, 'name') else ''),
                    "path": getattr(menu, 'PATH', menu.path if hasattr(menu, 'path') else ''),
                    "component": getattr(menu, 'COMPONENT', menu.component if hasattr(menu, 'component') else ''),
                    "icon": getattr(menu, 'ICON', menu.icon if hasattr(menu, 'icon') else ''),
                    "permission": getattr(menu, 'PERMISSION', menu.permission if hasattr(menu, 'permission') else ''),
                    "parent_id": getattr(menu, 'PARENT_ID', menu.parent_id if hasattr(menu, 'parent_id') else None),
                    "sort_order": getattr(menu, 'SORT_ORDER', menu.sort_order if hasattr(menu, 'sort_order') else 0),
                    "status": getattr(menu, 'STATUS', menu.status if hasattr(menu, 'status') else 1),
                    "children": []
                }
                menu_dict[menu_data["id"]] = menu_data
            
            # 构建树形结构
            for menu_data in menu_dict.values():
                if menu_data["parent_id"] is None:
                    root_menus.append(menu_data)
                else:
                    parent = menu_dict.get(menu_data["parent_id"])
                    if parent:
                        parent["children"].append(menu_data)
            
            # 按排序字段排序
            def sort_menus(menu_list):
                menu_list.sort(key=lambda x: x["sort_order"] or 0)
                for menu in menu_list:
                    if menu["children"]:
                        sort_menus(menu["children"])
            
            sort_menus(root_menus)
            return root_menus
        except Exception as e:
            logger.error(f"构建菜单树失败: {e}")
            return []
    
    async def _get_cache_ttl(self, cache_type: str) -> int:
        """获取缓存TTL配置"""
        config_key = f"{self.CACHE_CONFIG_PREFIX}{cache_type}"
        
        # 尝试从缓存获取配置
        cached_config = cache_client.get(config_key)
        if cached_config and isinstance(cached_config, dict):
            return cached_config.get("ttl", self.DEFAULT_TTL)
        
        return self.DEFAULT_TTL
    
    async def _invalidate_users_by_role(self, role_id: int):
        """清除使用指定角色的所有用户缓存"""
        try:
            db = next(get_db())
            try:
                user_service = RBACUserService(db)
                user_roles = user_service.get_users_by_role(role_id)
                for user_role in user_roles:
                    await self.invalidate_user_cache(user_role.user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"清除角色用户缓存失败: {e}")
