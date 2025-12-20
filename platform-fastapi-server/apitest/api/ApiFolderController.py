"""
接口目录Controller
提供目录的CRUD、树形结构查询、拖拽排序等功能
"""
from typing import Optional
from apitest.schemas.api_folder_schema import (
    ApiFolderQuery,
    ApiFolderCreate,
    ApiFolderUpdate,
    ApiFolderMove,
    ApiMoveToFolder,
    ApiFolderBatchSort
)
from apitest.service.api_folder_service import ApiFolderService
from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

module_name = "ApiFolder"
module_route = APIRouter(prefix=f"/{module_name}", tags=["接口目录管理"])


@module_route.post("/queryTree", summary="查询目录树",
                   dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_tree(query: ApiFolderQuery, session: Session = Depends(get_session)):
    """查询项目的目录树结构（包含接口）"""
    service = ApiFolderService(session)
    tree = service.query_tree(project_id=query.project_id)
    return respModel.ok_resp_list(lst=tree, total=len(tree))


@module_route.get("/queryList", summary="查询目录列表",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_list(project_id: int = Query(..., description="项目ID"),
                     parent_id: Optional[int] = Query(None, description="父目录ID"),
                     session: Session = Depends(get_session)):
    """查询指定目录下的子目录列表"""
    service = ApiFolderService(session)
    folders = service.query_list(project_id=project_id, parent_id=parent_id)
    return respModel.ok_resp_list(lst=folders, total=len(folders))


@module_route.get("/queryById", summary="根据ID查询目录",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def query_by_id(id: int = Query(..., description="目录ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询目录详情"""
    service = ApiFolderService(session)
    data = service.get_by_id(id)
    if not data:
        return respModel.error_resp(msg="目录不存在")
    return respModel.ok_resp(obj=data)


@module_route.post("/insert", summary="新增目录",
                   dependencies=[Depends(check_permission("apitest:folder:add"))])
async def insert(folder: ApiFolderCreate, session: Session = Depends(get_session)):
    """新增目录"""
    service = ApiFolderService(session)
    data = service.create(**folder.model_dump())
    if not data:
        return respModel.error_resp(msg="父目录不存在或不属于该项目")
    return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})


@module_route.put("/update", summary="更新目录",
                  dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def update(folder: ApiFolderUpdate, session: Session = Depends(get_session)):
    """更新目录"""
    service = ApiFolderService(session)
    update_data = folder.model_dump(exclude_unset=True, exclude={"id"})
    updated = service.update(folder.id, update_data)
    if not updated:
        return respModel.error_resp(msg="目录不存在")
    return respModel.ok_resp(msg="更新成功")


@module_route.delete("/delete", summary="删除目录",
                     dependencies=[Depends(check_permission("apitest:folder:delete"))])
async def delete(id: int = Query(..., description="目录ID"),
                 move_to_parent: bool = Query(True, description="是否将子项移动到父目录"),
                 session: Session = Depends(get_session)):
    """删除目录"""
    service = ApiFolderService(session)
    if not service.delete(id, move_to_parent=move_to_parent):
        return respModel.error_resp(msg="目录不存在")
    return respModel.ok_resp(msg="删除成功")


@module_route.put("/move", summary="移动目录",
                  dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def move(move_data: ApiFolderMove, session: Session = Depends(get_session)):
    """移动目录到新的父目录"""
    service = ApiFolderService(session)
    moved = service.move(
        folder_id=move_data.id,
        target_parent_id=move_data.target_parent_id,
        target_sort_order=move_data.target_sort_order
    )
    if not moved:
        return respModel.error_resp(msg="目录不存在或不能移动到指定位置")
    return respModel.ok_resp(msg="移动成功")


@module_route.post("/moveApis", summary="移动接口到目录",
                   dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def move_apis(move_data: ApiMoveToFolder, session: Session = Depends(get_session)):
    """批量移动接口到指定目录"""
    service = ApiFolderService(session)
    moved_count = service.move_apis(folder_id=move_data.folder_id, api_ids=move_data.api_ids)
    if moved_count == 0:
        return respModel.error_resp(msg="目标目录不存在")
    return respModel.ok_resp(msg=f"已移动 {moved_count} 个接口")


@module_route.post("/batchSort", summary="批量排序",
                   dependencies=[Depends(check_permission("apitest:folder:edit"))])
async def batch_sort(sort_data: ApiFolderBatchSort, session: Session = Depends(get_session)):
    """批量更新排序"""
    service = ApiFolderService(session)
    service.batch_sort(sort_data.items)
    return respModel.ok_resp(msg="排序更新成功")


@module_route.get("/getPath", summary="获取目录路径",
                  dependencies=[Depends(check_permission("apitest:folder:query"))])
async def get_path(id: int = Query(..., description="目录ID"),
                   session: Session = Depends(get_session)):
    """获取目录的完整路径（面包屑）"""
    service = ApiFolderService(session)
    path = service.get_path(folder_id=id)
    return respModel.ok_resp_list(lst=path, total=len(path))


