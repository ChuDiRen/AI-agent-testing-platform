"""
API用例步骤Controller
"""
import json
from datetime import datetime
from typing import List

from apitest.service.api_info_case_step_service import InfoCaseStepService
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..schemas.api_info_case_schema import ApiInfoCaseStepCreate, ApiInfoCaseStepUpdate

module_name = "ApiInfoCaseStep"
module_model = ApiInfoCaseStep
module_route = APIRouter(prefix=f"/{module_name}", tags=["API用例步骤管理"])
logger = get_logger(__name__)


@module_route.get("/queryByCaseId", summary="根据用例ID查询步骤", dependencies=[Depends(check_permission("apitest:step:query"))])
async def queryByCaseId(case_info_id: int = Query(...), session: Session = Depends(get_session)):
    """根据用例ID查询所有步骤"""
    try:
        service = InfoCaseStepService(session)
        steps = service.query_by_case_id(case_info_id)
        return respModel.ok_resp_list(lst=steps, msg="查询成功")
    except Exception as e:
        logger.error(f"查询用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增用例步骤", dependencies=[Depends(check_permission("apitest:step:add"))])
async def insert(step: ApiInfoCaseStepCreate, session: Session = Depends(get_session)):
    """新增用例步骤"""
    try:
        service = InfoCaseStepService(session)
        step_data_dict = step.model_dump()
        if step_data_dict.get('step_data'):
            step_data_dict['step_data'] = json.dumps(step_data_dict['step_data'], ensure_ascii=False)
        data = service.create(**step_data_dict)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        logger.error(f"新增用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新用例步骤", dependencies=[Depends(check_permission("apitest:step:edit"))])
async def update(step: ApiInfoCaseStepUpdate, session: Session = Depends(get_session)):
    """更新用例步骤"""
    try:
        service = InfoCaseStepService(session)
        update_data = step.model_dump(exclude_unset=True, exclude={'id'})
        if 'step_data' in update_data and update_data['step_data']:
            update_data['step_data'] = json.dumps(update_data['step_data'], ensure_ascii=False)
        
        if service.update(step.id, update_data):
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="步骤不存在")
    except Exception as e:
        logger.error(f"更新用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除用例步骤", dependencies=[Depends(check_permission("apitest:step:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用例步骤"""
    try:
        service = InfoCaseStepService(session)
        if service.delete(id):
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="步骤不存在")
    except Exception as e:
        logger.error(f"删除用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.post("/batchUpdateOrder", summary="批量更新步骤顺序", dependencies=[Depends(check_permission("apitest:step:edit"))])
async def batchUpdateOrder(steps: List[dict], session: Session = Depends(get_session)):
    """批量更新步骤顺序"""
    try:
        service = InfoCaseStepService(session)
        order_updates = [{"id": s.get('id'), "run_order": s.get('run_order')} for s in steps]
        service.batch_update_order(order_updates)
        return respModel.ok_resp(msg="更新顺序成功")
    except Exception as e:
        logger.error(f"批量更新步骤顺序失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败: {e}")
