"""
数据权限过滤工具
"""
from typing import Optional, List
from sqlmodel import Session, select, or_
from app.models.UserModel import User
from app.models.RoleModel import Role
from app.models.UserRoleModel import UserRole
from app.models.DeptModel import Dept


def get_user_data_scope(session: Session, user_id: int) -> tuple[str, List[int]]:
    """
    获取用户的数据权限范围
    
    Args:
        session: 数据库会话
        user_id: 用户ID
    
    Returns:
        tuple: (data_scope, dept_ids)
        - data_scope: 数据权限范围标识
          1=全部数据, 2=自定义, 3=本部门, 4=本部门及下级, 5=仅本人
        - dept_ids: 部门ID列表（用于自定义数据权限）
    """
    # 查询用户角色
    statement = select(UserRole).where(UserRole.user_id == user_id)
    user_roles = session.exec(statement).all()
    
    if not user_roles:
        # 没有角色，默认只能看自己的数据
        return "5", []
    
    role_ids = [ur.role_id for ur in user_roles]
    
    # 查询角色的数据权限
    statement = select(Role).where(Role.id.in_(role_ids))
    roles = session.exec(statement).all()
    
    # 找出最高的数据权限（数字越小权限越大）
    min_scope = "5"  # 默认最小权限
    for role in roles:
        if role.data_scope and role.data_scope < min_scope:
            min_scope = role.data_scope
    
    # 如果是全部数据权限，直接返回
    if min_scope == "1":
        return "1", []
    
    # 获取用户所属部门
    user = session.get(User, user_id)
    if not user or not user.dept_id:
        return "5", []
    
    dept_ids = []
    
    if min_scope == "3":
        # 本部门数据权限
        dept_ids = [user.dept_id]
    elif min_scope == "4":
        # 本部门及下级部门数据权限
        dept_ids = get_dept_and_children(session, user.dept_id)
    elif min_scope == "5":
        # 仅本人数据权限
        dept_ids = []
    
    return min_scope, dept_ids


def get_dept_and_children(session: Session, dept_id: int) -> List[int]:
    """
    获取部门及其所有下级部门ID列表
    
    Args:
        session: 数据库会话
        dept_id: 部门ID
    
    Returns:
        List[int]: 部门ID列表
    """
    dept_ids = [dept_id]
    
    # 递归查询子部门
    statement = select(Dept).where(Dept.parent_id == dept_id)
    children = session.exec(statement).all()
    
    for child in children:
        dept_ids.extend(get_dept_and_children(session, child.id))
    
    return dept_ids


def apply_data_scope_filter(statement, user_id: int, session: Session, 
                            model_class, user_id_field: str = 'creator_id',
                            dept_id_field: str = 'dept_id'):
    """
    应用数据权限过滤到查询语句
    
    Args:
        statement: SQLModel查询语句
        user_id: 当前用户ID
        session: 数据库会话
        model_class: 数据模型类
        user_id_field: 模型中的用户ID字段名（用于仅本人权限）
        dept_id_field: 模型中的部门ID字段名（用于部门权限）
    
    Returns:
        statement: 添加了数据权限过滤的查询语句
    """
    # 检查是否为超级管理员
    user = session.get(User, user_id)
    if user and user.username == 'admin':
        # 超级管理员不过滤数据
        return statement
    
    # 获取用户数据权限
    data_scope, dept_ids = get_user_data_scope(session, user_id)
    
    if data_scope == "1":
        # 全部数据权限，不过滤
        return statement
    elif data_scope == "5":
        # 仅本人数据权限
        user_field = getattr(model_class, user_id_field, None)
        if user_field is not None:
            statement = statement.where(user_field == user_id)
    elif data_scope in ["3", "4"] and dept_ids:
        # 部门数据权限
        dept_field = getattr(model_class, dept_id_field, None)
        if dept_field is not None:
            statement = statement.where(dept_field.in_(dept_ids))
    
    return statement
