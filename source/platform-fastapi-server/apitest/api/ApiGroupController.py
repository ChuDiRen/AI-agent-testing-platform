from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from apitest.model.ApiInfoGroupModel import ApiInfoGroup
from apitest.schemas.api_group_schema import ApiGroupQuery, ApiGroupCreate, ApiGroupUpdate
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from typing import List, Dict

module_name = "ApiGroup" # 模块名称
module_model = ApiInfoGroup
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口分组管理"])

def build_tree(groups: List[ApiInfoGroup], parent_id: int = 0) -> List[Dict]: # 构建分组树
    tree = []
    for group in groups:
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
                "children": build_tree(groups, group.id)
            }
            tree.append(node)
    return sorted(tree, key=lambda x: x["order_num"])

@module_route.get("/tree") # 获取分组树
def getTree(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.project_id == project_id)
        groups = session.exec(statement).all()
        tree = build_tree(groups)
        return respModel().ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询分组
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if obj:
            return respModel().ok_resp(obj=obj)
        else:
            return respModel().error_resp("数据不存在")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert") # 新增分组
def insert(request: ApiGroupCreate, session: Session = Depends(get_session)):
    try:
        obj = module_model(**request.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel().ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update") # 更新分组
def update(request: ApiGroupUpdate, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, request.id)
        if not obj:
            return respModel().error_resp("数据不存在")
        
        update_data = request.model_dump(exclude_unset=True, exclude={"id"})
        update_data["modify_time"] = datetime.now()
        
        for key, value in update_data.items():
            setattr(obj, key, value)
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel().ok_resp(obj=obj, msg="更新成功")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete") # 删除分组
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel().error_resp("数据不存在")
        
        # 检查是否有子分组
        statement = select(module_model).where(module_model.parent_id == id)
        children = session.exec(statement).all()
        if children:
            return respModel().error_resp("存在子分组，无法删除")
        
        # 检查是否有关联的接口
        from apitest.model.ApiInfoModel import ApiInfo
        # 这里暂时不检查接口关联，后续可以添加group_id字段到ApiInfo表
        
        session.delete(obj)
        session.commit()
        return respModel().ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getByProject") # 根据项目获取所有分组（平铺）
def getByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.project_id == project_id).order_by(module_model.order_num)
        groups = session.exec(statement).all()
        return respModel().ok_resp_list(lst=groups, total=len(groups))
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
