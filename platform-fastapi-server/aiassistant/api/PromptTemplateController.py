import logging

from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..schemas.prompt_template_schema import PromptTemplateQuery, PromptTemplateCreate, PromptTemplateUpdate
from ..services.PromptTemplateService import PromptTemplateService

logger = logging.getLogger(__name__)

module_name = "PromptTemplate"
module_route = APIRouter(prefix=f"/{module_name}", tags=["提示词模板管理"])


@module_route.post("/queryByPage", summary="分页查询提示词模板")
async def queryByPage(query: PromptTemplateQuery, session: Session = Depends(get_session)):
    datas, total, error = PromptTemplateService.query_by_page(session, query)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询提示词模板")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    data, error = PromptTemplateService.query_by_id(session, id)
    if error:
        return respModel.error_resp(error)
    if data:
        return respModel.ok_resp(obj=data)
    else:
        return respModel.ok_resp(msg="查询成功,但是没有数据")


@module_route.get("/queryByType", summary="按测试类型获取所有激活的模板")
async def queryByType(testType: str = Query(...), session: Session = Depends(get_session)):
    datas, error = PromptTemplateService.query_by_type(session, testType)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.get("/queryAll", summary="查询所有提示词模板")
async def queryAll(session: Session = Depends(get_session)):
    datas, error = PromptTemplateService.query_all(session)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.post("/insert", summary="新增提示词模板")
async def insert(template: PromptTemplateCreate, session: Session = Depends(get_session)):
    template_id, error = PromptTemplateService.insert(session, template)
    if error:
        return respModel.error_resp(msg=error)
    return respModel.ok_resp(msg="添加成功", dic_t={"id": template_id})


@module_route.put("/update", summary="更新提示词模板")
async def update(template: PromptTemplateUpdate, session: Session = Depends(get_session)):
    success, message = PromptTemplateService.update(session, template)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.delete("/delete", summary="删除提示词模板")
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = PromptTemplateService.delete(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.post("/toggleActive", summary="切换模板激活/停用状态")
async def toggleActive(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = PromptTemplateService.toggle_active(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.get("/queryByTestType", summary="按测试类型查询模板")
async def queryByTestType(test_type: str = Query(...), session: Session = Depends(get_session)):
    datas, error = PromptTemplateService.query_by_test_type(session, test_type)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=len(datas))
