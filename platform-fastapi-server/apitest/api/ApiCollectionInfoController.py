import json
from datetime import datetime

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..schemas.api_collection_schema import (
    ApiCollectionInfoQuery, ApiCollectionInfoCreate, ApiCollectionInfoUpdate,
    ApiCollectionDetailCreate, BatchAddCasesRequest, UpdateDdtDataRequest
)

logger = get_logger(__name__)

module_name = "ApiCollectionInfo"
module_model = ApiCollectionInfo
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试计划管理"])

# ==================== 测试计划CRUD ====================

@module_route.post("/queryByPage", summary="分页查询测试计划", dependencies=[Depends(check_permission("apitest:collection:query"))])
async def queryByPage(query: ApiCollectionInfoQuery, session: Session = Depends(get_session)):
    """分页查询测试计划"""
    try:
        statement = select(module_model)
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.plan_name:
            statement = statement.where(module_model.plan_name.like(f"%{query.plan_name}%"))

        offset = (query.page - 1) * query.pageSize
        datas = session.exec(statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)).all()
        total = len(session.exec(statement).all())
        
        result_list = []
        for data in datas:
            # 统计用例数量
            case_count_stmt = select(ApiCollectionDetail).where(ApiCollectionDetail.collection_info_id == data.id)
            case_count = len(session.exec(case_count_stmt).all())
            
            item = {
                "id": data.id,
                "project_id": data.project_id,
                "plan_name": data.plan_name,
                "plan_desc": data.plan_desc,
                "case_count": case_count,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "modify_time": TimeFormatter.format_datetime(data.modify_time)
            }
            result_list.append(item)
        
        return respModel.ok_resp_list(lst=result_list, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询测试计划", dependencies=[Depends(check_permission("apitest:collection:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试计划（含关联用例）"""
    try:
        plan = session.get(module_model, id)
        if not plan:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 查询关联的用例
        case_stmt = select(ApiCollectionDetail).where(ApiCollectionDetail.collection_info_id == id).order_by(ApiCollectionDetail.run_order)
        plan_cases = session.exec(case_stmt).all()
        
        cases = []
        for pc in plan_cases:
            # 查询用例信息
            case_info = session.get(ApiInfoCase, pc.case_info_id)
            cases.append({
                "id": pc.id,
                "plan_id": pc.collection_info_id,
                "case_info_id": pc.case_info_id,
                "case_name": case_info.case_name if case_info else "",
                "case_desc": case_info.case_desc if case_info else "",
                "run_order": pc.run_order,
                "ddt_data": pc.ddt_data,
                "create_time": TimeFormatter.format_datetime(pc.create_time)
            })
        
        result = {
            "id": plan.id,
            "project_id": plan.project_id,
            "plan_name": plan.plan_name,
            "plan_desc": plan.plan_desc,
            "create_time": TimeFormatter.format_datetime(plan.create_time),
            "modify_time": TimeFormatter.format_datetime(plan.modify_time),
            "cases": cases
        }
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增测试计划", dependencies=[Depends(check_permission("apitest:collection:add"))])
async def insert(data: ApiCollectionInfoCreate, session: Session = Depends(get_session)):
    """新增测试计划"""
    try:
        plan = module_model(
            project_id=data.project_id,
            plan_name=data.plan_name,
            plan_desc=data.plan_desc,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(plan)
        session.commit()
        return respModel.ok_resp_text(msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def update(data: ApiCollectionInfoUpdate, session: Session = Depends(get_session)):
    """更新测试计划"""
    try:
        plan = session.get(module_model, data.id)
        if not plan:
            return respModel.error_resp("测试计划不存在")
        
        if data.project_id is not None:
            plan.project_id = data.project_id
        if data.plan_name is not None:
            plan.plan_name = data.plan_name
        if data.plan_desc is not None:
            plan.plan_desc = data.plan_desc
        plan.modify_time = datetime.now()
        
        session.commit()
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除测试计划", dependencies=[Depends(check_permission("apitest:collection:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除测试计划"""
    try:
        obj = session.get(module_model, id)
        if obj:
            session.delete(obj)
            session.commit()
            return respModel.ok_resp_text(msg="删除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# ==================== 用例关联管理 ====================

@module_route.post("/addCase", summary="添加用例到测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def addCase(data: ApiCollectionDetailCreate, session: Session = Depends(get_session)):
    """添加用例到计划"""
    try:
        # 检查是否已存在
        check_stmt = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == data.plan_id,
            ApiCollectionDetail.case_info_id == data.case_info_id
        )
        existing = session.exec(check_stmt).first()
        if existing:
            return respModel.error_resp("该用例已添加到计划中")
        
        plan_case = ApiCollectionDetail(
            collection_info_id=data.plan_id,
            case_info_id=data.case_info_id,
            run_order=data.run_order,
            ddt_data=json.dumps(data.ddt_data, ensure_ascii=False) if data.ddt_data else None,
            create_time=datetime.now()
        )
        session.add(plan_case)
        session.commit()
        return respModel.ok_resp_text(msg="添加成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/batchAddCases", summary="批量添加用例到测试计划", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def batchAddCases(data: BatchAddCasesRequest, session: Session = Depends(get_session)):
    """批量添加用例到计划，自动提取数据驱动配置"""
    try:
        # 不需要参数化的字段
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_ddt_from_case(case_id: int) -> str:
            """从用例步骤中提取数据驱动配置"""
            variables = {}
            
            def extract_all_fields(data_dict):
                if isinstance(data_dict, dict):
                    for key, value in data_dict.items():
                        if key in skip_fields:
                            continue
                        if isinstance(value, dict):
                            extract_all_fields(value)
                        elif isinstance(value, list):
                            for item in value:
                                extract_all_fields(item)
                        elif isinstance(value, (str, int, float, bool)):
                            variables[key] = value if isinstance(value, str) else str(value)
                elif isinstance(data_dict, list):
                    for item in data_dict:
                        extract_all_fields(item)
            
            # 获取用例步骤
            steps = session.exec(
                select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_id)
            ).all()
            
            for step in steps:
                if step.step_data:
                    try:
                        step_dict = json.loads(step.step_data)
                        extract_all_fields(step_dict)
                    except:
                        pass
            
            # 获取用例名称
            case_info = session.get(ApiInfoCase, case_id)
            case_name = case_info.case_name if case_info else f"用例{case_id}"
            
            if variables:
                template = [{"desc": f"{case_name}_数据1", **variables}]
                return json.dumps(template, ensure_ascii=False)
            return None
        
        added_count = 0
        for idx, case_id in enumerate(data.case_ids):
            # 检查是否已存在
            check_stmt = select(ApiCollectionDetail).where(
                ApiCollectionDetail.collection_info_id == data.plan_id,
                ApiCollectionDetail.case_info_id == case_id
            )
            existing = session.exec(check_stmt).first()
            if not existing:
                # 自动提取数据驱动配置
                ddt_data = extract_ddt_from_case(case_id)
                plan_case = ApiCollectionDetail(
                    collection_info_id=data.plan_id,
                    case_info_id=case_id,
                    run_order=idx + 1,
                    ddt_data=ddt_data,
                    create_time=datetime.now()
                )
                session.add(plan_case)
                added_count += 1
        
        session.commit()
        return respModel.ok_resp_text(msg=f"成功添加{added_count}个用例")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/removeCase", summary="从测试计划移除用例", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def removeCase(plan_case_id: int = Query(...), session: Session = Depends(get_session)):
    """从计划中移除用例"""
    try:
        obj = session.get(ApiCollectionDetail, plan_case_id)
        if obj:
            session.delete(obj)
            session.commit()
            return respModel.ok_resp_text(msg="移除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/updateDdtData", summary="更新测试计划的数据驱动信息", dependencies=[Depends(check_permission("apitest:collection:edit"))])
async def updateDdtData(data: UpdateDdtDataRequest, session: Session = Depends(get_session)):
    """更新用例的数据驱动数据"""
    try:
        plan_case = session.get(ApiCollectionDetail, data.plan_case_id)
        if not plan_case:
            return respModel.error_resp("关联数据不存在")
        
        plan_case.ddt_data = json.dumps(data.ddt_data, ensure_ascii=False) if data.ddt_data else None
        session.commit()
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# ==================== 批量执行测试计划（已废弃，请使用 /ApiInfoCase/executeCase 接口） ====================
# 注意：executePlan 接口已合并到 /ApiInfoCase/executeCase 接口
# 前端调用 executeCase 时传入 plan_id 即可实现批量执行

