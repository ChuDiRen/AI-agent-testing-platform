from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger

logger = get_logger(__name__)
from ..model.dept import Dept
from ..schemas.dept_schema import DeptQuery, DeptCreate, DeptUpdate, DeptTree
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from typing import List, Dict

module_name = "dept"
module_model = Dept
module_route = APIRouter(prefix=f"/{module_name}", tags=["部门管理"])

def build_tree(depts: List[Dept], parent_id: int = 0) -> List[Dict]: # 构建部门树
    tree = []
    for dept in depts:
        if dept.parent_id == parent_id:
            node = {
                "id": dept.id,
                "parent_id": dept.parent_id,
                "dept_name": dept.dept_name,
                "order_num": dept.order_num,
                "create_time": TimeFormatter.format_datetime(dept.create_time),
                "modify_time": TimeFormatter.format_datetime(dept.modify_time),
                "children": build_tree(depts, dept.id)
            }
            tree.append(node)
    return sorted(tree, key=lambda x: x["order_num"])

@module_route.get("/tree") # 获取部门树
def getTree(session: Session = Depends(get_session)):
    try:
        statement = select(module_model)
        depts = session.exec(statement).all()
        tree = build_tree(depts)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询部门
def queryById(id: int, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if obj:
            return respModel.ok_resp(obj=obj)
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert") # 新增部门
def insert(request: DeptCreate, session: Session = Depends(get_session)):
    try:
        obj = module_model(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update") # 更新部门
def update(request: DeptUpdate, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, request.id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        update_data = request.model_dump(exclude_unset=True, exclude={"id"})
        update_data["modify_time"] = datetime.now()
        
        for key, value in update_data.items():
            setattr(obj, key, value)
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete") # 删除部门
def delete(id: int, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        # 检查是否有子部门
        statement = select(module_model).where(module_model.parent_id == id)
        children = session.exec(statement).all()
        if children:
            return respModel.error_resp("存在子部门，无法删除")
        
        # 检查是否有关联用户
        from ..model.user import User
        statement = select(User).where(User.dept_id == id)
        users = session.exec(statement).all()
        if users:
            return respModel.error_resp("该部门下有用户，无法删除")
        
        session.delete(obj)
        session.commit()
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

