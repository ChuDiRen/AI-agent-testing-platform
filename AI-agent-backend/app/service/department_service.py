# Copyright (c) 2025 左岚. All rights reserved.
"""
部门Service
实现部门相关的业务逻辑
"""

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.department import Department
from app.repository.department_repository import DepartmentRepository

logger = get_logger(__name__)


class DepartmentService:
    """
    部门Service类
    提供部门相关的业务逻辑处理
    """

    def __init__(self, db: Session):
        """
        初始化部门Service

        Args:
            db: 数据库会话
        """
        self.db = db
        self.department_repository = DepartmentRepository(db)

    def create_department(self, parent_id: int, dept_name: str, order_num: float = None) -> Department:
        """
        创建部门

        Args:
            parent_id: 上级部门ID，0表示顶级部门
            dept_name: 部门名称
            order_num: 排序号

        Returns:
            创建的部门对象

        Raises:
            ValueError: 部门名称已存在
        """
        # 检查部门名称是否已存在
        if self.department_repository.exists_by_name(dept_name):
            raise ValueError(f"部门名称 '{dept_name}' 已存在")

        # 创建部门
        department = Department(parent_id=parent_id, dept_name=dept_name, order_num=order_num)
        created_department = self.department_repository.create(department)

        logger.info(f"Created department: {dept_name}")
        return created_department

    def get_department_by_id(self, dept_id: int) -> Optional[Department]:
        """
        根据ID获取部门

        Args:
            dept_id: 部门ID

        Returns:
            部门对象或None
        """
        return self.department_repository.get_by_id(dept_id)

    def get_departments_by_ids(self, dept_ids: List[int]) -> List[Department]:
        """批量根据ID获取部门列表  # 注释"""
        return self.department_repository.get_by_ids(dept_ids)


    def get_department_by_name(self, dept_name: str) -> Optional[Department]:
        """
        根据名称获取部门

        Args:
            dept_name: 部门名称

        Returns:
            部门对象或None
        """
        return self.department_repository.get_by_name(dept_name)

    def get_department_tree(self, keyword: str = None) -> List[Dict[str, Any]]:
        """
        获取部门树结构

        Args:
            keyword: 搜索关键词，用于过滤部门名称

        Returns:
            部门树列表
        """
        all_departments = self.department_repository.get_department_tree()

        # 如果有关键词，先过滤部门
        if keyword:
            filtered_departments = []
            for dept in all_departments:
                if keyword.lower() in dept.dept_name.lower():
                    filtered_departments.append(dept)
            all_departments = filtered_departments

        # 构建部门树
        dept_dict = {}
        for dept in all_departments:
            dept_dict[dept.id] = {
                "id": dept.id,  # 前端期望id
                "name": dept.dept_name,  # 前端期望name
                "desc": "",  # 前端期望desc
                "order": dept.order_num,  # 前端期望order
                "parent_id": dept.parent_id,
                "children": []
            }

        # 构建父子关系
        tree = []
        for dept_data in dept_dict.values():
            if dept_data["parent_id"] == 0:
                tree.append(dept_data)
            else:
                parent = dept_dict.get(dept_data["parent_id"])
                if parent:
                    parent["children"].append(dept_data)

        return tree

    def get_top_level_departments(self) -> List[Department]:
        """
        获取顶级部门

        Returns:
            顶级部门列表
        """
        return self.department_repository.get_top_level_departments()

    def get_children_departments(self, parent_id: int) -> List[Department]:
        """
        获取子部门

        Args:
            parent_id: 父级部门ID

        Returns:
            子部门列表
        """
        return self.department_repository.get_by_parent_id(parent_id)

    def update_department(self, dept_id: int, dept_name: str = None, order_num: float = None) -> Optional[Department]:
        """
        更新部门信息

        Args:
            dept_id: 部门ID
            dept_name: 新的部门名称
            order_num: 新的排序号

        Returns:
            更新后的部门对象或None

        Raises:
            ValueError: 部门名称已存在
        """
        department = self.department_repository.get_by_id(dept_id)
        if not department:
            logger.warning(f"Department not found with id: {dept_id}")
            return None

        # 如果要更新部门名称，检查是否已存在
        if dept_name and dept_name != department.dept_name:
            if self.department_repository.exists_by_name(dept_name, exclude_id=dept_id):
                raise ValueError(f"部门名称 '{dept_name}' 已存在")

        # 更新部门信息
        department.update_info(dept_name=dept_name, order_num=order_num)
        updated_department = self.department_repository.update(department)

        logger.info(f"Updated department: {dept_id}")
        return updated_department

    def delete_department(self, dept_id: int) -> bool:
        """
        删除部门

        Args:
            dept_id: 部门ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 部门仍有子部门或用户
        """
        # 检查是否可以删除
        if not self.department_repository.can_delete(dept_id):
            if self.department_repository.has_children(dept_id):
                raise ValueError("部门仍有子部门，无法删除")
            if self.department_repository.has_users(dept_id):
                raise ValueError("部门仍有用户，无法删除")

        # 删除部门
        success = self.department_repository.delete(dept_id)

        if success:
            logger.info(f"Deleted department: {dept_id}")

        return success

    def search_departments(self, keyword: str) -> List[Department]:
        """
        搜索部门

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的部门列表
        """
        return self.department_repository.search_by_name(keyword)

    def get_all_departments(self) -> List[Department]:
        """
        获取所有部门

        Returns:
            部门列表
        """
        return self.department_repository.get_all()

    def has_children(self, dept_id: int) -> bool:
        """
        检查部门是否有子部门

        Args:
            dept_id: 部门ID

        Returns:
            True表示有子部门，False表示没有
        """
        return self.department_repository.has_children(dept_id)

    def has_users(self, dept_id: int) -> bool:
        """
        检查部门是否有用户

        Args:
            dept_id: 部门ID

        Returns:
            True表示有用户，False表示没有
        """
        return self.department_repository.has_users(dept_id)

    def can_delete(self, dept_id: int) -> bool:
        """
        检查部门是否可以删除

        Args:
            dept_id: 部门ID

        Returns:
            True表示可以删除，False表示不可以
        """
        return self.department_repository.can_delete(dept_id)

    async def get_department_user_count(self, dept_id: int) -> int:
        """
        获取部门下的用户数量

        Args:
            dept_id: 部门ID

        Returns:
            用户数量
        """
        from app.entity.user import User
        count = self.db.query(User).filter(
            User.dept_id == dept_id,
            User.is_deleted == 0
        ).count()
        return count
