import logging
from typing import List

from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session

from ..schemas.test_case_schema import TestCaseQuery, TestCaseCreate, TestCaseUpdate, BatchInsertRequest
from ..service.TestCaseService import TestCaseService

logger = logging.getLogger(__name__)

module_name = "TestCase"
module_route = APIRouter(prefix=f"/{module_name}", tags=["测试用例管理"])


@module_route.post("/queryByPage", summary="分页查询测试用例")
async def queryByPage(query: TestCaseQuery, session: Session = Depends(get_session)):
    datas, total, error = TestCaseService.query_by_page(session, query)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询测试用例")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    data, error = TestCaseService.query_by_id(session, id)
    if error:
        return respModel.error_resp(error)
    if data:
        return respModel.ok_resp(obj=data)
    else:
        return respModel.ok_resp(msg="查询成功,但是没有数据")


@module_route.post("/insert", summary="新增测试用例")
async def insert(case: TestCaseCreate, session: Session = Depends(get_session)):
    case_id, error = TestCaseService.insert(session, case)
    if error:
        return respModel.error_resp(msg=error)
    return respModel.ok_resp(msg="添加成功", dic_t={"id": case_id})


@module_route.post("/batchInsert", summary="批量插入测试用例")
async def batchInsert(req: BatchInsertRequest, session: Session = Depends(get_session)):
    count, error = TestCaseService.batch_insert(session, req)
    if error:
        return respModel.error_resp(msg=error)
    return respModel.ok_resp(msg=f"成功创建{count}个测试用例", dic_t={"count": count})


@module_route.put("/update", summary="更新测试用例")
async def update(case: TestCaseUpdate, session: Session = Depends(get_session)):
    success, message = TestCaseService.update(session, case)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.delete("/delete", summary="删除测试用例")
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = TestCaseService.delete(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.get("/exportYaml", summary="导出单个测试用例为YAML")
async def exportYaml(id: int = Query(...), session: Session = Depends(get_session)):
    yaml_content, filename, error = TestCaseService.export_yaml(session, id)
    if error:
        return respModel.error_resp(msg=error)
    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@module_route.post("/exportBatchYaml", summary="批量导出测试用例为YAML")
async def exportBatchYaml(case_ids: List[int], session: Session = Depends(get_session)):
    yaml_content, error = TestCaseService.export_batch_yaml(session, case_ids)
    if error:
        return respModel.error_resp(msg=error)
    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={"Content-Disposition": f"attachment; filename=test_cases_batch.yaml"}
    )
