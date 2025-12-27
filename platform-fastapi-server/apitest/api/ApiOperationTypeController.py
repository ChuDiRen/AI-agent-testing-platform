from datetime import datetime

from apitest.service.ApiOperationTypeService import OperationTypeService
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..model.ApiOperationTypeModel import OperationType
from ..schemas.ApiOperationTypeSchema import OperationTypeQuery, OperationTypeCreate, OperationTypeUpdate

module_name = "OperationType" # 模块名称
module_model = OperationType
module_route = APIRouter(prefix=f"/{module_name}", tags=["操作类型管理"])
logger = get_logger(__name__)

@module_route.get("/queryAll", summary="查询所有操作类型")
async def queryAll(session: Session = Depends(get_session)):
    service = OperationTypeService(session)
    datas = service.query_all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")

@module_route.post("/queryByPage", summary="分页查询操作类型", dependencies=[Depends(check_permission("apitest:operationtype:query"))])
async def queryByPage(query: OperationTypeQuery, session: Session = Depends(get_session)):
    try:
        service = OperationTypeService(session)
        datas = service.query_all()
        if query.operation_type_name:
            datas = [d for d in datas if query.operation_type_name in d.operation_type_name]
        total = len(datas)
        offset = (query.page - 1) * query.pageSize
        datas = datas[offset:offset + query.pageSize]
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询操作类型", dependencies=[Depends(check_permission("apitest:operationtype:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = OperationTypeService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增操作类型", dependencies=[Depends(check_permission("apitest:operationtype:add"))])
async def insert(op_type: OperationTypeCreate, session: Session = Depends(get_session)):
    try:
        service = OperationTypeService(session)
        data = service.create(**op_type.model_dump())
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except ValueError as e:
        return respModel.error_resp(msg=str(e))
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新操作类型", dependencies=[Depends(check_permission("apitest:operationtype:edit"))])
async def update(op_type: OperationTypeUpdate, session: Session = Depends(get_session)):
    try:
        service = OperationTypeService(session)
        update_data = op_type.model_dump(exclude_unset=True, exclude={'id'})
        if service.update(op_type.id, update_data):
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="操作类型不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除操作类型", dependencies=[Depends(check_permission("apitest:operationtype:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = OperationTypeService(session)
        if service.delete(id):
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="操作类型不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
