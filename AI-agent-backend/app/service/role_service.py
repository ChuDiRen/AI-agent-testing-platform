# Copyright (c) 2025 左岚. All rights reserved.
"""
角色Service
实现角色相关的业务逻辑
"""

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.role import Role
from app.repository.role_menu_repository import RoleMenuRepository
from app.repository.role_repository import RoleRepository
from app.repository.user_role_repository import UserRoleRepository

logger = get_logger(__name__)


class RoleService:
    """
    角色Service类
    提供角色相关的业务逻辑处理
    """

    def __init__(self, db: Session):
        """
        初始化角色Service
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.role_repository = RoleRepository(db)
        self.user_role_repository = UserRoleRepository(db)
        self.role_menu_repository = RoleMenuRepository(db)

    def create_role(self, role_name: str, remark: str = None) -> Role:
        """
        创建角色
        
        Args:
            role_name: 角色名称
            remark: 角色描述
            
        Returns:
            创建的角色对象
            
        Raises:
            ValueError: 角色名称已存在
        """
        # 检查角色名称是否已存在
        if self.role_repository.exists_by_name(role_name):
            raise ValueError(f"角色名称 '{role_name}' 已存在")
        
        # 创建角色
        role = Role(role_name=role_name, remark=remark)
        created_role = self.role_repository.create(role)
        
        logger.info(f"Created role: {role_name}")
        return created_role

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        根据ID获取角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色对象或None
        """
        return self.role_repository.get_by_id(role_id)

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """
        根据名称获取角色
        
        Args:
            role_name: 角色名称
            
        Returns:
            角色对象或None
        """
        return self.role_repository.get_by_name(role_name)

    def get_all_roles(self) -> List[Role]:
        """
        获取所有角色
        
        Returns:
            角色列表
        """
        return self.role_repository.get_all_active()

    def update_role(self, role_id: int, role_name: str = None, remark: str = None) -> Optional[Role]:
        """
        更新角色信息
        
        Args:
            role_id: 角色ID
            role_name: 新的角色名称
            remark: 新的角色描述
            
        Returns:
            更新后的角色对象或None
            
        Raises:
            ValueError: 角色名称已存在
        """
        role = self.role_repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role not found with id: {role_id}")
            return None
        
        # 如果要更新角色名称，检查是否已存在
        if role_name and role_name != role.role_name:
            if self.role_repository.exists_by_name(role_name, exclude_id=role_id):
                raise ValueError(f"角色名称 '{role_name}' 已存在")
        
        # 准备更新数据
        update_data = {}
        if role_name is not None:
            update_data['role_name'] = role_name
        if remark is not None:
            update_data['remark'] = remark

        # 更新角色信息
        updated_role = self.role_repository.update(role_id, update_data)

        logger.info(f"Updated role: {role_id}")
        return updated_role

    def delete_role(self, role_id: int) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            是否删除成功
            
        Raises:
            ValueError: 角色仍有用户关联
        """
        # 检查是否有用户关联此角色
        user_roles = self.user_role_repository.get_by_role_id(role_id)
        if user_roles:
            raise ValueError(f"角色仍有 {len(user_roles)} 个用户关联，无法删除")
        
        # 删除角色的菜单权限关联
        self.role_menu_repository.delete_by_role_id(role_id)
        
        # 删除角色
        success = self.role_repository.delete(role_id)
        
        if success:
            logger.info(f"Deleted role: {role_id}")
        
        return success

    def batch_delete_roles(self, role_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除角色

        Args:
            role_ids: 角色ID列表

        Returns:
            删除结果统计
        """
        success_count = 0
        failed_count = 0
        failed_roles = []

        for role_id in role_ids:
            try:
                # 检查角色是否存在
                role = self.role_repository.get_by_id(role_id)
                if not role:
                    failed_count += 1
                    failed_roles.append({"role_id": role_id, "reason": "角色不存在"})
                    continue

                # 检查是否有用户关联此角色
                user_roles = self.user_role_repository.get_by_role_id(role_id)
                if user_roles:
                    failed_count += 1
                    failed_roles.append({
                        "role_id": role_id,
                        "reason": f"角色仍有 {len(user_roles)} 个用户关联，无法删除"
                    })
                    continue

                # 删除角色的菜单权限关联
                self.role_menu_repository.delete_by_role_id(role_id)

                # 删除角色
                if self.role_repository.delete(role_id):
                    success_count += 1
                    logger.info(f"Batch deleted role: {role_id}")
                else:
                    failed_count += 1
                    failed_roles.append({"role_id": role_id, "reason": "删除失败"})

            except Exception as e:
                failed_count += 1
                failed_roles.append({"role_id": role_id, "reason": str(e)})
                logger.error(f"Error batch deleting role {role_id}: {str(e)}")

        result = {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_count": len(role_ids),
            "failed_roles": failed_roles
        }

        logger.info(f"Batch delete roles result: {result}")
        return result

    def search_roles(self, keyword: str) -> List[Role]:
        """
        搜索角色
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的角色列表
        """
        return self.role_repository.search_by_name(keyword)

    def get_roles_with_pagination(self, page: int = 1, size: int = 10, keyword: str = None) -> Dict[str, Any]:
        """
        分页获取角色

        Args:
            page: 页码（从1开始）
            size: 每页大小
            keyword: 关键词搜索

        Returns:
            包含角色列表和分页信息的字典
        """
        roles, total = self.role_repository.get_roles_with_pagination(page, size, keyword)

        return {
            "roles": [role.to_dict() for role in roles],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size  # 计算总页数
        }

    def assign_menus_to_role(self, role_id: int, menu_ids: List[int]) -> bool:
        """
        为角色分配菜单权限
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            
        Returns:
            是否分配成功
        """
        try:
            # 检查角色是否存在
            role = self.role_repository.get_by_id(role_id)
            if not role:
                logger.warning(f"Role not found with id: {role_id}")
                return False
            
            # 分配菜单权限
            self.role_menu_repository.assign_menus_to_role(role_id, menu_ids)
            self.db.commit()
            
            logger.info(f"Assigned {len(menu_ids)} menus to role: {role_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning menus to role {role_id}: {str(e)}")
            return False

    def get_role_permissions(self, role_id: int) -> List[str]:
        """
        获取角色的权限标识列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限标识列表
        """
        return self.role_menu_repository.get_permissions_by_role_id(role_id)

    def get_role_menu_ids(self, role_id: int) -> List[int]:
        """
        获取角色的菜单ID列表

        Args:
            role_id: 角色ID

        Returns:
            菜单ID列表
        """
        return self.role_menu_repository.get_menu_ids_by_role_id(role_id)

    def copy_role(self, source_role_id: int, new_role_name: str) -> Role:
        """
        复制角色（包括权限）

        Args:
            source_role_id: 源角色ID
            new_role_name: 新角色名称

        Returns:
            新创建的角色对象

        Raises:
            ValueError: 源角色不存在或新角色名称已存在
        """
        try:
            # 获取源角色
            source_role = self.role_repository.get_by_id(source_role_id)
            if not source_role:
                raise ValueError(f"源角色不存在: {source_role_id}")

            # 检查新角色名称是否已存在
            if self.role_repository.exists_by_name(new_role_name):
                raise ValueError(f"角色名称 '{new_role_name}' 已存在")

            # 创建新角色
            new_role = Role(
                role_name=new_role_name,
                remark=f"复制自: {source_role.role_name}"
            )
            created_role = self.role_repository.create(new_role)

            # 复制菜单权限
            source_menu_ids = self.get_role_menu_ids(source_role_id)
            if source_menu_ids:
                self.role_menu_repository.assign_menus_to_role(created_role.id, source_menu_ids)

            self.db.commit()

            logger.info(f"Copied role: {source_role_id} -> {created_role.id} with {len(source_menu_ids)} menus")
            return created_role

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error copying role {source_role_id}: {str(e)}")
            raise
