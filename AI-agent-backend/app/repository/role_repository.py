"""
角色Repository
实现角色相关的数据访问操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.entity.role import Role
from app.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """
    角色Repository类
    提供角色相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化角色Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(db, Role)

    def get_by_name(self, role_name: str) -> Optional[Role]:
        """
        根据角色名称查询角色
        
        Args:
            role_name: 角色名称
            
        Returns:
            角色对象或None
        """
        return self.db.query(Role).filter(Role.role_name == role_name).first()

    def get_all_active(self) -> List[Role]:
        """
        获取所有有效角色
        
        Returns:
            角色列表
        """
        return self.db.query(Role).all()

    def exists_by_name(self, role_name: str, exclude_id: int = None) -> bool:
        """
        检查角色名称是否已存在
        
        Args:
            role_name: 角色名称
            exclude_id: 排除的角色ID（用于更新时检查）
            
        Returns:
            True表示存在，False表示不存在
        """
        query = self.db.query(Role).filter(Role.role_name == role_name)
        if exclude_id:
            query = query.filter(Role.id != exclude_id)  # 修复：使用正确的属性名
        return query.first() is not None

    def search_by_name(self, keyword: str) -> List[Role]:
        """
        根据关键词搜索角色

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的角色列表
        """
        return self.db.query(Role).filter(
            Role.role_name.like(f"%{keyword}%"),
            Role.is_deleted == 0
        ).all()

    def get_roles_with_pagination(self, page: int = 1, size: int = 10, keyword: str = None) -> tuple[List[Role], int]:
        """
        分页查询角色

        Args:
            page: 页码（从1开始）
            size: 每页大小
            keyword: 关键词搜索

        Returns:
            (角色列表, 总数量)
        """
        offset = (page - 1) * size

        # 构建基础查询条件
        query = self.db.query(Role).filter(Role.is_deleted == 0)

        # 如果有关键词，添加搜索条件
        if keyword:
            query = query.filter(Role.role_name.like(f"%{keyword}%"))

        # 查询总数
        total = query.count()

        # 查询当前页数据
        roles = query.offset(offset).limit(size).all()

        return roles, total
