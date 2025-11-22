"""
API用例步骤Controller
"""
import json
from datetime import datetime
from typing import List

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..schemas.api_info_case_schema import ApiInfoCaseStepCreate, ApiInfoCaseStepUpdate

module_name = "ApiInfoCaseStep"
module_model = ApiInfoCaseStep
module_route = APIRouter(prefix=f"/{module_name}", tags=["API用例步骤管理"])
logger = get_logger(__name__)


@module_route.get("/queryByCaseId", summary="根据用例ID查询步骤", dependencies=[Depends(check_permission("apitest:step:query"))])
def queryByCaseId(case_info_id: int = Query(...), session: Session = Depends(get_session)):
    """根据用例ID查询所有步骤"""
    try:
        statement = select(module_model).where(module_model.case_info_id == case_info_id).order_by(module_model.run_order)
        steps = session.exec(statement).all()
        return respModel.ok_resp_list(lst=steps, msg="查询成功")
    except Exception as e:
        logger.error(f"查询用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增用例步骤", dependencies=[Depends(check_permission("apitest:step:add"))])
def insert(step: ApiInfoCaseStepCreate, session: Session = Depends(get_session)):
    """新增用例步骤"""
    try:
        # 将字典转换为JSON字符串
        step_data_dict = step.model_dump()
        if step_data_dict.get('step_data'):
            step_data_dict['step_data'] = json.dumps(step_data_dict['step_data'], ensure_ascii=False)
        
        data = module_model(**step_data_dict, create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新用例步骤", dependencies=[Depends(check_permission("apitest:step:edit"))])
def update(step: ApiInfoCaseStepUpdate, session: Session = Depends(get_session)):
    """更新用例步骤"""
    try:
        statement = select(module_model).where(module_model.id == step.id)
        db_step = session.exec(statement).first()
        if db_step:
            update_data = step.model_dump(exclude_unset=True, exclude={'id'})
            # 处理step_data
            if 'step_data' in update_data and update_data['step_data']:
                update_data['step_data'] = json.dumps(update_data['step_data'], ensure_ascii=False)
            
            for key, value in update_data.items():
                setattr(db_step, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="步骤不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除用例步骤", dependencies=[Depends(check_permission("apitest:step:delete"))])
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用例步骤"""
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="步骤不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除用例步骤失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.post("/batchUpdateOrder", summary="批量更新步骤顺序", dependencies=[Depends(check_permission("apitest:step:edit"))])
def batchUpdateOrder(steps: List[dict], session: Session = Depends(get_session)):
    """批量更新步骤顺序"""
    try:
        for step_data in steps:
            step_id = step_data.get('id')
            run_order = step_data.get('run_order')
            if step_id and run_order is not None:
                statement = select(module_model).where(module_model.id == step_id)
                db_step = session.exec(statement).first()
                if db_step:
                    db_step.run_order = run_order
        session.commit()
        return respModel.ok_resp(msg="更新顺序成功")
    except Exception as e:
        session.rollback()
        logger.error(f"批量更新步骤顺序失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败: {e}")
