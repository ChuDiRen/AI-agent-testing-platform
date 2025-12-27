"""用户管理 Service 层"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlmodel import Session, select

from ..model.UserModel import User
from ..model.UserRoleModel import UserRole
from ..schemas.UserSchema import UserQuery, UserCreate, UserUpdate, UserRoleAssign, UserStatusUpdate


class UserService:
    """用户管理服务类"""

    @staticmethod
    def query_by_page(session: Session, query: UserQuery) -> Tuple[List[User], int]:
        """分页查询用户"""
        offset = (query.page - 1) * query.pageSize
        statement = select(User)
        
        if query.username:
            statement = statement.where(User.username.like(f"%{query.username}%"))
        if query.dept_id:
            statement = statement.where(User.dept_id == query.dept_id)
        if query.status:
            statement = statement.where(User.status == query.status)
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(User)
        if query.username:
            count_statement = count_statement.where(User.username.like(f"%{query.username}%"))
        if query.dept_id:
            count_statement = count_statement.where(User.dept_id == query.dept_id)
        if query.status:
            count_statement = count_statement.where(User.status == query.status)
        total = len(session.exec(count_statement).all())
        
        return datas, total

    @staticmethod
    def query_by_id(session: Session, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()

    @staticmethod
    def create(session: Session, user: UserCreate) -> User:
        """新增用户"""
        data = User(**user.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, user: UserUpdate) -> Optional[User]:
        """更新用户"""
        statement = select(User).where(User.id == user.id)
        db_user = session.exec(statement).first()
        if not db_user:
            return None
        
        update_data = user.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_user, key, value)
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
    def assign_roles(session: Session, request: UserRoleAssign) -> bool:
        """为用户分配角色"""
        user = session.get(User, request.id)
        if not user:
            return False
        
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
        return True

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
