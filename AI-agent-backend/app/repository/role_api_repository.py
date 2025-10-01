"""
角色API关联Repository
实现角色API关联相关的数据访问操作
"""

from typing import List

from sqlalchemy.orm import Session

from app.entity.api_endpoint import ApiEndpoint
from app.entity.role_api import RoleApi
from app.repository.base import BaseRepository


class RoleApiRepository(BaseRepository[RoleApi]):
    """
    角色API关联Repository类
    提供角色API关联相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化角色API关联Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(db, RoleApi)

    def get_by_role_id(self, role_id: int) -> List[RoleApi]:
        """
        根据角色ID查询角色API关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色API关联列表
        """
        return self.db.query(RoleApi).filter(RoleApi.role_id == role_id).all()

    def get_by_api_id(self, api_id: int) -> List[RoleApi]:
        """
        根据API ID查询角色API关联
        
        Args:
            api_id: API ID
            
        Returns:
            角色API关联列表
        """
        return self.db.query(RoleApi).filter(RoleApi.api_id == api_id).all()

    def get_apis_by_role_id(self, role_id: int) -> List[ApiEndpoint]:
        """
        根据角色ID获取角色的所有API
        
        Args:
            role_id: 角色ID
            
        Returns:
            API列表
        """
        return self.db.query(ApiEndpoint).join(
            RoleApi, ApiEndpoint.id == RoleApi.api_id
        ).filter(RoleApi.role_id == role_id).all()

    def get_api_ids_by_role_id(self, role_id: int) -> List[int]:
        """
        根据角色ID获取API ID列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            API ID列表
        """
        result = self.db.query(RoleApi.api_id).filter(RoleApi.role_id == role_id).all()
        return [api_id[0] for api_id in result]

    def exists(self, role_id: int, api_id: int) -> bool:
        """
        检查角色API关联是否存在
        
        Args:
            role_id: 角色ID
            api_id: API ID
            
        Returns:
            True表示存在，False表示不存在
        """
        return self.db.query(RoleApi).filter(
            RoleApi.role_id == role_id,
            RoleApi.api_id == api_id
        ).first() is not None

    def delete_by_role_id(self, role_id: int) -> int:
        """
        删除角色的所有API关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(RoleApi).filter(RoleApi.role_id == role_id).count()
        self.db.query(RoleApi).filter(RoleApi.role_id == role_id).delete()
        return count

    def delete_by_api_id(self, api_id: int) -> int:
        """
        删除API的所有角色关联
        
        Args:
            api_id: API ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(RoleApi).filter(RoleApi.api_id == api_id).count()
        self.db.query(RoleApi).filter(RoleApi.api_id == api_id).delete()
        return count

    def delete_specific(self, role_id: int, api_id: int) -> bool:
        """
        删除特定的角色API关联
        
        Args:
            role_id: 角色ID
            api_id: API ID
            
        Returns:
            True表示删除成功，False表示记录不存在
        """
        result = self.db.query(RoleApi).filter(
            RoleApi.role_id == role_id,
            RoleApi.api_id == api_id
        ).delete()
        return result > 0

    def assign_apis_to_role(self, role_id: int, api_ids: List[int]) -> None:
        """
        为角色分配API权限（先清除原有权限，再分配新权限）
        
        Args:
            role_id: 角色ID
            api_ids: API ID列表
        """
        # 先删除角色的所有API权限
        self.delete_by_role_id(role_id)
        
        # 分配新的API权限
        for api_id in api_ids:
            role_api = RoleApi(role_id=role_id, api_id=api_id)
            self.db.add(role_api)

    def add_api_to_role(self, role_id: int, api_id: int) -> bool:
        """
        为角色添加API权限（如果不存在的话）
        
        Args:
            role_id: 角色ID
            api_id: API ID
            
        Returns:
            True表示添加成功，False表示已存在
        """
        if self.exists(role_id, api_id):
            return False
        
        role_api = RoleApi(role_id=role_id, api_id=api_id)
        self.db.add(role_api)
        return True

    def get_permissions_by_role_id(self, role_id: int) -> List[str]:
        """
        根据角色ID获取API权限标识列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限标识列表
        """
        permissions = self.db.query(ApiEndpoint.permission).join(
            RoleApi, ApiEndpoint.id == RoleApi.api_id
        ).filter(
            RoleApi.role_id == role_id,
            ApiEndpoint.permission.isnot(None)  # 只获取有权限标识的API
        ).all()
        
        # 提取权限标识字符串
        return [perm[0] for perm in permissions if perm[0]]
