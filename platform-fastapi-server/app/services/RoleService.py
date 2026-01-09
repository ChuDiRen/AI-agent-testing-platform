"""角色管理 Service 层"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlmodel import Session, select

from app.models.RoleModel import Role
from app.models.RoleMenuModel import RoleMenu
from app.schemas.RoleSchema import RoleQuery, RoleCreate, RoleUpdate, RoleMenuAssign


class RoleService:
    """角色管理服务类"""

    @staticmethod
    def query_by_page(session: Session, query: RoleQuery) -> Tuple[List[Role], int]:
        """分页查询角色"""
        offset = (query.page - 1) * query.pageSize
        statement = select(Role)
        
        if query.role_name:
            statement = statement.where(Role.role_name.like(f"%{query.role_name}%"))
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(Role)
        if query.role_name:
            count_statement = count_statement.where(Role.role_name.like(f"%{query.role_name}%"))
        total = len(session.exec(count_statement).all())
        
        return datas, total

    @staticmethod
    def query_by_id(session: Session, role_id: int) -> Optional[Role]:
        """根据ID查询角色"""
        return session.get(Role, role_id)

    @staticmethod
    def check_name_exists(session: Session, role_name: str) -> bool:
        """检查角色名是否已存在"""
        statement = select(Role).where(Role.role_name == role_name)
        return session.exec(statement).first() is not None

    @staticmethod
    def create(session: Session, request: RoleCreate) -> Role:
        """新增角色"""
        obj = Role(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def update(session: Session, request: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        obj = session.get(Role, request.id)
        if not obj:
            return None
        
        update_data = request.model_dump(exclude_unset=True, exclude={"id"})
        update_data["modify_time"] = datetime.now()
        
        for key, value in update_data.items():
            setattr(obj, key, value)
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def delete(session: Session, role_id: int) -> bool:
        """删除角色"""
        obj = session.get(Role, role_id)
        if not obj:
            return False
        
        # 删除角色关联的菜单权限
        statement = select(RoleMenu).where(RoleMenu.role_id == role_id)
        role_menus = session.exec(statement).all()
        for rm in role_menus:
            session.delete(rm)
        
        session.delete(obj)
        session.commit()
        return True

    @staticmethod
    def assign_menus(session: Session, request: RoleMenuAssign) -> bool:
        """为角色分配菜单权限"""
        role = session.get(Role, request.id)
        if not role:
            return False
        
        # 删除该角色原有的菜单权限
        statement = select(RoleMenu).where(RoleMenu.role_id == request.id)
        old_role_menus = session.exec(statement).all()
        for rm in old_role_menus:
            session.delete(rm)
        
        # 添加新的菜单权限
        for menu_id in request.menu_ids:
            role_menu = RoleMenu(role_id=request.id, menu_id=menu_id)
            session.add(role_menu)
        
        session.commit()
        return True

    @staticmethod
    def get_menus(session: Session, role_id: int) -> List[int]:
        """获取角色的菜单权限ID列表"""
        statement = select(RoleMenu).where(RoleMenu.role_id == role_id)
        role_menus = session.exec(statement).all()
        return [rm.menu_id for rm in role_menus]
