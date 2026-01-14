"""用户管理 Service 层"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from sqlmodel import Session, select

from app.models.UserModel import User
from app.models.UserRoleModel import UserRole
from app.models.RoleModel import Role
from app.schemas.UserSchema import (
    UserQuery, UserCreate, UserUpdate, UserRoleAssign, 
    UserStatusUpdate, BatchUserStatusUpdate, BatchUserDelete
)
from app.utils.data_scope import apply_data_scope_filter


class UserService:
    """用户管理服务类"""

    @staticmethod
    def query_by_page(session: Session, query: UserQuery, current_user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """分页查询用户（包含角色信息，应用数据权限过滤）"""
        offset = (query.page - 1) * query.pageSize
        statement = select(User)
        
        if query.username:
            statement = statement.where(User.username.like(f"%{query.username}%"))
        if query.dept_id:
            statement = statement.where(User.dept_id == query.dept_id)
        if query.status:
            statement = statement.where(User.status == query.status)
        
        # 应用数据权限过滤
        if current_user_id:
            statement = apply_data_scope_filter(
                statement=statement,
                user_id=current_user_id,
                session=session,
                model_class=User,
                user_id_field='id',
                dept_id_field='dept_id'
            )
        
        statement = statement.limit(query.pageSize).offset(offset)
        users = session.exec(statement).all()
        
        # 为每个用户添加角色信息
        user_data_list = []
        for user in users:
            user_dict = user.model_dump()
            # 获取用户角色
            role_ids = UserService.get_roles(session, user.id)
            if role_ids:
                # 获取角色名称
                role_statement = select(Role).where(Role.id.in_(role_ids))
                roles = session.exec(role_statement).all()
                user_dict['roles'] = [role.role_name for role in roles]
            else:
                user_dict['roles'] = []
            user_data_list.append(user_dict)
        
        # 统计总数
        count_statement = select(User)
        if query.username:
            count_statement = count_statement.where(User.username.like(f"%{query.username}%"))
        if query.dept_id:
            count_statement = count_statement.where(User.dept_id == query.dept_id)
        if query.status:
            count_statement = count_statement.where(User.status == query.status)
        
        # 应用数据权限过滤
        if current_user_id:
            count_statement = apply_data_scope_filter(
                statement=count_statement,
                user_id=current_user_id,
                session=session,
                model_class=User,
                user_id_field='id',
                dept_id_field='dept_id'
            )
        
        total = len(session.exec(count_statement).all())
        
        return user_data_list, total

    @staticmethod
    def query_by_id(session: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户（包含角色信息）"""
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        if not user:
            return None
        
        user_dict = user.model_dump()
        # 获取用户角色
        role_ids = UserService.get_roles(session, user.id)
        if role_ids:
            # 获取角色名称
            role_statement = select(Role).where(Role.id.in_(role_ids))
            roles = session.exec(role_statement).all()
            user_dict['roles'] = [role.role_name for role in roles]
        else:
            user_dict['roles'] = []
        
        return user_dict

    @staticmethod
    def create(session: Session, user: UserCreate) -> User:
        """新增用户"""
        # 排除 role_ids 字段，因为 User 模型中没有这个字段
        user_data = user.model_dump(exclude={'role_ids'})
        data = User(**user_data, create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        
        # 如果指定了角色，为用户分配角色
        if user.role_ids and len(user.role_ids) > 0:
            for role_id in user.role_ids:
                user_role = UserRole(user_id=data.id, role_id=role_id)
                session.add(user_role)
            session.commit()
        
        return data

    @staticmethod
    def update(session: Session, user: UserUpdate) -> Optional[User]:
        """更新用户"""
        statement = select(User).where(User.id == user.id)
        db_user = session.exec(statement).first()
        if not db_user:
            return None
        
        # 排除 role_ids 和 id 字段
        update_data = user.model_dump(exclude_unset=True, exclude={'id', 'role_ids'})
        for key, value in update_data.items():
            setattr(db_user, key, value)
        session.commit()
        
        # 如果指定了角色，为用户分配角色
        if user.role_ids is not None:  # 允许空数组，表示清除所有角色
            # 删除用户原有的角色
            old_role_statement = select(UserRole).where(UserRole.user_id == user.id)
            old_user_roles = session.exec(old_role_statement).all()
            for ur in old_user_roles:
                session.delete(ur)
            
            # 添加新的角色
            for role_id in user.role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                session.add(user_role)
            
            session.commit()
        
        return db_user

    @staticmethod
    def delete(session: Session, user_id: int) -> bool:
        """删除用户"""
        statement = select(User).where(User.id == user_id)
        data = session.exec(statement).first()
        if not data:
            return False
        
        # 删除用户的角色关联
        statement = select(UserRole).where(UserRole.user_id == user_id)
        user_roles = session.exec(statement).all()
        for ur in user_roles:
            session.delete(ur)
        
        session.delete(data)
        session.commit()
        return True

    @staticmethod
    def assign_roles(session: Session, request: UserRoleAssign) -> Tuple[bool, str]:
        """为用户分配角色，返回 (成功状态, 消息)"""
        user = session.get(User, request.id)
        if not user:
            return False, "用户不存在"
        
        # 检查是否是超级管理员（用户名为 admin）
        if user.username == 'admin':
            return False, "超级管理员角色不允许修改"
        
        # 删除用户原有的角色
        statement = select(UserRole).where(UserRole.user_id == request.id)
        old_user_roles = session.exec(statement).all()
        for ur in old_user_roles:
            session.delete(ur)
        
        # 添加新的角色
        for role_id in request.role_ids:
            user_role = UserRole(user_id=request.id, role_id=role_id)
            session.add(user_role)
        
        session.commit()
        return True, "角色分配成功"

    @staticmethod
    def get_roles(session: Session, user_id: int) -> List[int]:
        """获取用户的角色ID列表"""
        statement = select(UserRole).where(UserRole.user_id == user_id)
        user_roles = session.exec(statement).all()
        return [ur.role_id for ur in user_roles]

    @staticmethod
    def update_status(session: Session, request: UserStatusUpdate) -> Optional[str]:
        """更新用户状态，返回状态文本或None（用户不存在）"""
        user = session.get(User, request.id)
        if not user:
            return None
        
        user.status = request.status
        user.modify_time = datetime.now()
        session.add(user)
        session.commit()
        
        return "启用" if request.status == "1" else "锁定"

    @staticmethod
    def batch_update_status(session: Session, request: BatchUserStatusUpdate) -> int:
        """批量更新用户状态"""
        count = 0
        for user_id in request.user_ids:
            user = session.get(User, user_id)
            if user:
                user.status = request.status
                user.modify_time = datetime.now()
                session.add(user)
                count += 1
        session.commit()
        return count

    @staticmethod
    def batch_delete(session: Session, request: BatchUserDelete) -> int:
        """批量删除用户"""
        count = 0
        for user_id in request.user_ids:
            # 删除用户的角色关联
            statement = select(UserRole).where(UserRole.user_id == user_id)
            user_roles = session.exec(statement).all()
            for ur in user_roles:
                session.delete(ur)
            
            # 删除用户
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                count += 1
        
        session.commit()
        return count
