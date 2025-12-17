"""
接口目录Controller
提供目录的CRUD、树形结构查询、拖拽排序等功能
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, and_
from typing import List, Optional

from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel

from apitest.model.ApiFolderModel import ApiFolder
from apitest.model.ApiInfoModel import ApiInfo
from apitest.schemas.api_folder_schema import (
    ApiFolderQuery,
    ApiFolderCreate,
    ApiFolderUpdate,
    ApiFolderMove,
    ApiMoveToFolder,
    ApiFolderBatchSort
)

module_name = "ApiFolder"
module_model = ApiFolder
module_route = APIRouter(prefix=f"/{module_name}", tags=["接口目录管理"])


@module_route.post("/queryTree", summary="查询目录树",
                   dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_tree(query: ApiFolderQuery, session: Session = Depends(get_session)):
    """查询项目的目录树结构（包含接口）"""
    # 查询所有目录
    folder_statement = select(module_model).where(
        module_model.project_id == query.project_id
    ).order_by(module_model.sort_order, module_model.id)
    folders = session.exec(folder_statement).all()
    
    # 查询所有接口
    api_statement = select(ApiInfo).where(
        ApiInfo.project_id == query.project_id
    ).order_by(ApiInfo.id)
    apis = session.exec(api_statement).all()
    
    # 构建树形结构
    tree = build_folder_tree(folders, apis)
    
    return respModel.ok_resp_list(lst=tree, total=len(tree))


@module_route.get("/queryList", summary="查询目录列表",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_list(project_id: int = Query(..., description="项目ID"),
                     parent_id: Optional[int] = Query(None, description="父目录ID"),
                     session: Session = Depends(get_session)):
    """查询指定目录下的子目录列表"""
    statement = select(module_model).where(
        module_model.project_id == project_id
    )
    if parent_id is not None:
        statement = statement.where(module_model.parent_id == parent_id)
    
    statement = statement.order_by(module_model.sort_order, module_model.id)
    folders = session.exec(statement).all()
    
    return respModel.ok_resp_list(lst=folders, total=len(folders))


@module_route.get("/queryById", summary="根据ID查询目录",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_by_id(id: int = Query(..., description="目录ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询目录详情"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="目录不存在")
    return respModel.ok_resp(obj=data)


@module_route.post("/insert", summary="新增目录",
                   dependencies=[Depends(check_permission("apitest:folder:add"))])
async def insert(folder: ApiFolderCreate, session: Session = Depends(get_session)):
    """新增目录"""
    # 检查父目录是否存在
    if folder.parent_id > 0:
        parent = session.get(module_model, folder.parent_id)
        if not parent:
            return respModel.error_resp(msg="父目录不存在")
        if parent.project_id != folder.project_id:
            return respModel.error_resp(msg="父目录不属于该项目")
    
    # 获取同级目录的最大排序号
    statement = select(module_model).where(
        and_(
            module_model.project_id == folder.project_id,
            module_model.parent_id == folder.parent_id
        )
    ).order_by(module_model.sort_order.desc())
    last_folder = session.exec(statement).first()
    
    if folder.sort_order == 0 and last_folder:
        folder.sort_order = last_folder.sort_order + 1
    
    data = module_model(
        **folder.model_dump(),
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    session.add(data)
    session.commit()
    session.refresh(data)
    
    return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})


@module_route.put("/update", summary="更新目录",
                  dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def update(folder: ApiFolderUpdate, session: Session = Depends(get_session)):
    """更新目录"""
    data = session.get(module_model, folder.id)
    if not data:
        return respModel.error_resp(msg="目录不存在")
    
    # 更新字段
    update_data = folder.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(data, key, value)
    data.update_time = datetime.now()
    
    session.add(data)
    session.commit()
    
    return respModel.ok_resp(msg="更新成功")


@module_route.delete("/delete", summary="删除目录",
                     dependencies=[Depends(check_permission("apitest:folder:delete"))])
async def delete(id: int = Query(..., description="目录ID"),
                 move_to_parent: bool = Query(True, description="是否将子项移动到父目录"),
                 session: Session = Depends(get_session)):
    """删除目录"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="目录不存在")
    
    # 查询子目录
    child_folders = session.exec(
        select(module_model).where(module_model.parent_id == id)
    ).all()
    
    # 查询目录下的接口
    child_apis = session.exec(
        select(ApiInfo).where(ApiInfo.folder_id == id)
    ).all()
    
    if move_to_parent:
        # 将子目录移动到父目录
        for child in child_folders:
            child.parent_id = data.parent_id
            child.update_time = datetime.now()
            session.add(child)
        
        # 将接口移动到父目录
        for api in child_apis:
            api.folder_id = data.parent_id
            session.add(api)
    else:
        # 递归删除子目录
        for child in child_folders:
            await delete_folder_recursive(session, child.id)
        
        # 将接口移动到根目录
        for api in child_apis:
            api.folder_id = 0
            session.add(api)
    
    session.delete(data)
    session.commit()
    
    return respModel.ok_resp(msg="删除成功")


@module_route.put("/move", summary="移动目录",
                  dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def move(move_data: ApiFolderMove, session: Session = Depends(get_session)):
    """移动目录到新的父目录"""
    data = session.get(module_model, move_data.id)
    if not data:
        return respModel.error_resp(msg="目录不存在")
    
    # 检查目标父目录
    if move_data.target_parent_id > 0:
        target_parent = session.get(module_model, move_data.target_parent_id)
        if not target_parent:
            return respModel.error_resp(msg="目标父目录不存在")
        if target_parent.project_id != data.project_id:
            return respModel.error_resp(msg="不能移动到其他项目")
        
        # 检查是否移动到自己的子目录
        if is_descendant(session, move_data.target_parent_id, move_data.id):
            return respModel.error_resp(msg="不能移动到自己的子目录")
    
    data.parent_id = move_data.target_parent_id
    data.sort_order = move_data.target_sort_order
    data.update_time = datetime.now()
    
    session.add(data)
    session.commit()
    
    return respModel.ok_resp(msg="移动成功")


@module_route.post("/moveApis", summary="移动接口到目录",
                   dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def move_apis(move_data: ApiMoveToFolder, session: Session = Depends(get_session)):
    """批量移动接口到指定目录"""
    # 检查目标目录
    if move_data.folder_id > 0:
        folder = session.get(module_model, move_data.folder_id)
        if not folder:
            return respModel.error_resp(msg="目标目录不存在")
    
    # 更新接口的目录ID
    for api_id in move_data.api_ids:
        api = session.get(ApiInfo, api_id)
        if api:
            api.folder_id = move_data.folder_id
            session.add(api)
    
    session.commit()
    
    return respModel.ok_resp(msg=f"已移动 {len(move_data.api_ids)} 个接口")


@module_route.post("/batchSort", summary="批量排序",
                   dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def batch_sort(sort_data: ApiFolderBatchSort, session: Session = Depends(get_session)):
    """批量更新排序"""
    for item in sort_data.items:
        folder = session.get(module_model, item.get("id"))
        if folder:
            folder.sort_order = item.get("sort_order", 0)
            if "parent_id" in item:
                folder.parent_id = item["parent_id"]
            folder.update_time = datetime.now()
            session.add(folder)
    
    session.commit()
    
    return respModel.ok_resp(msg="排序更新成功")


@module_route.get("/getPath", summary="获取目录路径",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def get_path(id: int = Query(..., description="目录ID"),
                   session: Session = Depends(get_session)):
    """获取目录的完整路径（面包屑）"""
    path = []
    current_id = id
    
    while current_id > 0:
        folder = session.get(module_model, current_id)
        if not folder:
            break
        path.insert(0, {
            "id": folder.id,
            "folder_name": folder.folder_name
        })
        current_id = folder.parent_id
    
    return respModel.ok_resp_list(lst=path, total=len(path))


def build_folder_tree(folders: List[ApiFolder], apis: List[ApiInfo]) -> List[dict]:
    """构建目录树结构"""
    # 创建目录映射
    folder_map = {}
    for folder in folders:
        folder_map[folder.id] = {
            "id": folder.id,
            "project_id": folder.project_id,
            "parent_id": folder.parent_id,
            "folder_name": folder.folder_name,
            "folder_desc": folder.folder_desc,
            "folder_icon": folder.folder_icon,
            "sort_order": folder.sort_order,
            "is_expanded": folder.is_expanded,
            "node_type": "folder",
            "children": [],
            "api_count": 0
        }
    
    # 将接口添加到对应目录
    api_by_folder = {}
    for api in apis:
        folder_id = api.folder_id if hasattr(api, 'folder_id') and api.folder_id else 0
        if folder_id not in api_by_folder:
            api_by_folder[folder_id] = []
        api_by_folder[folder_id].append({
            "id": api.id,
            "api_name": api.api_name,
            "request_method": api.request_method,
            "request_url": api.request_url,
            "node_type": "api",
            "folder_id": folder_id
        })
    
    # 构建树
    tree = []
    for folder_id, folder_node in folder_map.items():
        parent_id = folder_node["parent_id"]
        
        # 添加该目录下的接口
        if folder_id in api_by_folder:
            folder_node["children"].extend(api_by_folder[folder_id])
            folder_node["api_count"] = len(api_by_folder[folder_id])
        
        if parent_id == 0:
            tree.append(folder_node)
        elif parent_id in folder_map:
            folder_map[parent_id]["children"].append(folder_node)
    
    # 添加根目录下的接口（folder_id = 0）
    if 0 in api_by_folder:
        for api_node in api_by_folder[0]:
            tree.append(api_node)
    
    # 排序
    def sort_children(nodes):
        nodes.sort(key=lambda x: (x.get("node_type") != "folder", x.get("sort_order", 0), x.get("id", 0)))
        for node in nodes:
            if node.get("children"):
                sort_children(node["children"])
    
    sort_children(tree)
    
    return tree


def is_descendant(session: Session, folder_id: int, ancestor_id: int) -> bool:
    """检查folder_id是否是ancestor_id的后代"""
    current_id = folder_id
    while current_id > 0:
        if current_id == ancestor_id:
            return True
        folder = session.get(ApiFolder, current_id)
        if not folder:
            break
        current_id = folder.parent_id
    return False


async def delete_folder_recursive(session: Session, folder_id: int):
    """递归删除目录及其子目录"""
    # 查询子目录
    child_folders = session.exec(
        select(ApiFolder).where(ApiFolder.parent_id == folder_id)
    ).all()
    
    for child in child_folders:
        await delete_folder_recursive(session, child.id)
    
    # 将接口移动到根目录
    child_apis = session.exec(
        select(ApiInfo).where(ApiInfo.folder_id == folder_id)
    ).all()
    for api in child_apis:
        api.folder_id = 0
        session.add(api)
    
    # 删除当前目录
    folder = session.get(ApiFolder, folder_id)
    if folder:
        session.delete(folder)
