# Copyright (c) 2025 左岚. All rights reserved.
"""
部门Repository
实现部门相关的数据访问操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.entity.department import Department
from app.repository.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """
    部门Repository类
    提供部门相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化部门Repository

        Args:
            db: 数据库会话
        """
        super().__init__(db, Department)

    def get_by_name(self, dept_name: str) -> Optional[Department]:
        """
        根据部门名称查询部门

        Args:
            dept_name: 部门名称

        Returns:
            部门对象或None
        """
        return self.db.query(Department).filter(Department.dept_name == dept_name).first()

    def get_by_ids(self, dept_ids: List[int]) -> List[Department]:
        """根据ID列表批量查询部门  # 注释"""
        if not dept_ids:
            return []
        return self.db.query(Department).filter(Department.id.in_(dept_ids)).all()


    def get_by_parent_id(self, parent_id: int) -> List[Department]:
        """
        根据父级ID查询子部门

        Args:
            parent_id: 父级部门ID

        Returns:
            子部门列表
        """
        return self.db.query(Department).filter(
            Department.parent_id == parent_id
        ).order_by(Department.order_num).all()

    def get_top_level_departments(self) -> List[Department]:
        """
        获取顶级部门（父级ID为0）

        Returns:
            顶级部门列表
        """
        return self.get_by_parent_id(0)

    def get_department_tree(self) -> List[Department]:
        """
        获取完整的部门树结构

        Returns:
            部门树列表
        """
        # 获取所有部门，按ORDER_NUM排序
        all_departments = self.db.query(Department).order_by(Department.order_num).all()

        # 构建部门树（这里返回所有部门，前端可以根据PARENT_ID构建树形结构）
        return all_departments

    def exists_by_name(self, dept_name: str, exclude_id: int = None) -> bool:
        """
        检查部门名称是否已存在

        Args:
            dept_name: 部门名称
            exclude_id: 排除的部门ID（用于更新时检查）

        Returns:
            True表示存在，False表示不存在
        """
        query = self.db.query(Department).filter(Department.dept_name == dept_name)
        if exclude_id:
            query = query.filter(Department.id != exclude_id)  # 修复：使用正确的属性名
        return query.first() is not None

    def search_by_name(self, keyword: str) -> List[Department]:
        """
        根据关键词搜索部门

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的部门列表
        """
        return self.db.query(Department).filter(
            Department.dept_name.like(f"%{keyword}%")
        ).order_by(Department.order_num).all()

    def has_children(self, dept_id: int) -> bool:
        """
        检查部门是否有子部门

        Args:
            dept_id: 部门ID

        Returns:
            True表示有子部门，False表示没有
        """
        return self.db.query(Department).filter(
            Department.parent_id == dept_id
        ).first() is not None

    def has_users(self, dept_id: int) -> bool:
        """
        检查部门是否有用户

        Args:
            dept_id: 部门ID

        Returns:
            True表示有用户，False表示没有
        """
        from app.entity.user import User

        return self.db.query(User).filter(
            User.dept_id == dept_id
        ).first() is not None

    def can_delete(self, dept_id: int) -> bool:
        """
        检查部门是否可以删除（没有子部门且没有用户）

        Args:
            dept_id: 部门ID

        Returns:
            True表示可以删除，False表示不可以
        """
        return not self.has_children(dept_id) and not self.has_users(dept_id)
