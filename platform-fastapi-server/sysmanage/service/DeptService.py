"""部门管理 Service 层"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select

from core.time_utils import TimeFormatter
from ..model.DeptModel import Dept
from ..model.UserModel import User
from ..schemas.DeptSchema import DeptCreate, DeptUpdate


class DeptService:
    """部门管理服务类"""

    @staticmethod
    def _build_tree(dept_list: List[Dept], parent_id: int = 0) -> List[Dict[str, Any]]:
        """构建部门树"""
        tree = []
        for dept in dept_list:
            if dept.parent_id == parent_id:
                node = {
                    "id": dept.id,
                    "parent_id": dept.parent_id,
                    "dept_name": dept.dept_name,
                    "order_num": dept.order_num,
                    "create_time": TimeFormatter.format_datetime(dept.create_time),
                    "modify_time": TimeFormatter.format_datetime(dept.modify_time),
                    "children": DeptService._build_tree(dept_list, dept.id)
                }
                tree.append(node)
        return sorted(tree, key=lambda x: x["order_num"])

    @staticmethod
    def get_tree(session: Session) -> List[Dict[str, Any]]:
        """获取部门树"""
        statement = select(Dept)
        depts = session.exec(statement).all()
        return DeptService._build_tree(depts)

    @staticmethod
    def query_by_id(session: Session, dept_id: int) -> Optional[Dept]:
        """根据ID查询部门"""
        return session.get(Dept, dept_id)

    @staticmethod
    def create(session: Session, request: DeptCreate) -> Dept:
        """新增部门"""
        obj = Dept(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def update(session: Session, request: DeptUpdate) -> Optional[Dept]:
        """更新部门"""
        obj = session.get(Dept, request.id)
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
    def delete(session: Session, dept_id: int) -> Optional[str]:
        """删除部门，返回错误信息或None（成功）"""
        obj = session.get(Dept, dept_id)
        if not obj:
            return "数据不存在"
        
        statement = select(Dept).where(Dept.parent_id == dept_id)
        children = session.exec(statement).all()
        if children:
            return "存在子部门，无法删除"
        
        statement = select(User).where(User.dept_id == dept_id)
        users = session.exec(statement).all()
        if users:
            return "该部门下有用户，无法删除"
        
        session.delete(obj)
        session.commit()
        return None
