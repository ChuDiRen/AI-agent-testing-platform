from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from ..model.ApiInfoGroupModel import ApiInfoGroup
from ..schemas.api_group_schema import ApiGroupQuery, ApiGroupCreate, ApiGroupUpdate
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from core.logger import get_logger

module_name = "ApiGroup"
module_model = ApiInfoGroup
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口分组管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage")
def queryByPage(query: ApiGroupQuery, session: Session = Depends(get_session)):
    """分页查询接口分组"""
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.group_name:
            statement = statement.where(module_model.group_name.like(f"%{query.group_name}%"))
        statement = statement.order_by(module_model.order_num)
        datas = session.exec(statement).all()

        count_statement = select(module_model)
        if query.project_id:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.group_name:
            count_statement = count_statement.where(module_model.group_name.like(f"%{query.group_name}%"))
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询API分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/tree")
def getTree(project_id: int = Query(...), session: Session = Depends(get_session)):
    """获取分组树"""
    try:
        statement = select(module_model).where(module_model.project_id == project_id)
        groups = session.exec(statement).all()

        # 构建分组树（内联实现）
        def _build_tree(group_list, parent_id=0):
            tree = []
            for group in group_list:
                if group.parent_id == parent_id:
                    node = {
                        "id": group.id,
                        "project_id": group.project_id,
                        "group_name": group.group_name,
                        "group_desc": group.group_desc,
                        "parent_id": group.parent_id,
                        "order_num": group.order_num,
                        "create_time": TimeFormatter.format_datetime(group.create_time),
                        "modify_time": TimeFormatter.format_datetime(group.modify_time),
                        "children": _build_tree(group_list, group.id)
                    }
                    tree.append(node)
            return sorted(tree, key=lambda x: x["order_num"])

        tree = _build_tree(groups)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"获取分组树失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById")
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询分组"""
    try:
        obj = session.get(module_model, id)
        return respModel.ok_resp(obj=obj) if obj else respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"根据ID查询分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert")
def insert(request: ApiGroupCreate, session: Session = Depends(get_session)):
    """新增分组"""
    try:
        obj = module_model(**request.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"新增分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update")
def update(request: ApiGroupUpdate, session: Session = Depends(get_session)):
    """更新分组"""
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
        logger.error(f"更新分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete")
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除分组"""
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        statement = select(module_model).where(module_model.parent_id == id)
        children = session.exec(statement).all()
        if children:
            return respModel.error_resp("存在子分组，无法删除")
        session.delete(obj)
        session.commit()
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"删除分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getByProject")
def getByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    """根据项目获取所有分组（平铺）"""
    try:
        statement = select(module_model).where(module_model.project_id == project_id).order_by(module_model.order_num)
        groups = session.exec(statement).all()
        return respModel.ok_resp_list(lst=groups, total=len(groups))
    except Exception as e:
        logger.error(f"根据项目获取分组失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
