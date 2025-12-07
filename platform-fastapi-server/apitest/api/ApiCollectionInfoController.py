import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

import yaml
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session, select

from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiHistoryModel import ApiHistory
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..model.ApiKeyWordModel import ApiKeyWord
from ..schemas.api_collection_schema import (
    ApiCollectionInfoQuery, ApiCollectionInfoCreate, ApiCollectionInfoUpdate,
    ApiCollectionDetailCreate, BatchAddCasesRequest, UpdateDdtDataRequest,
    ApiCollectionInfoExecuteRequest
)

logger = get_logger(__name__)

# ==================== 配置常量 ====================
# ✅ P2修复: 使用配置管理的路径,避免硬编码
from config.dev_settings import settings

BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

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
    """批量添加用例到计划"""
    try:
        added_count = 0
        for idx, case_id in enumerate(data.case_ids):
            # 检查是否已存在
            check_stmt = select(ApiCollectionDetail).where(
                ApiCollectionDetail.collection_info_id == data.plan_id,
                ApiCollectionDetail.case_info_id == case_id
            )
            existing = session.exec(check_stmt).first()
            if not existing:
                plan_case = ApiCollectionDetail(
                    collection_info_id=data.plan_id,
                    case_info_id=case_id,
                    run_order=idx + 1,
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

# ==================== 批量执行测试计划 ====================

@module_route.post("/executePlan", summary="批量执行测试计划", dependencies=[Depends(check_permission("apitest:collection:execute"))])
async def executePlan(request: ApiCollectionInfoExecuteRequest, session: Session = Depends(get_session)):
    """执行测试计划（所有用例合并到一个目录执行，生成一个包含所有用例的报告）"""
    from plugin.service.TaskScheduler import task_scheduler
    import yaml
    
    try:
        # 查询测试计划
        plan = session.get(ApiCollectionInfo, request.plan_id)
        if not plan:
            return respModel.error_resp("测试计划不存在")
        
        # 查询计划中的所有用例
        case_stmt = select(ApiCollectionDetail).where(ApiCollectionDetail.collection_info_id == request.plan_id).order_by(ApiCollectionDetail.run_order)
        plan_cases = session.exec(case_stmt).all()
        
        if not plan_cases:
            return respModel.error_resp("测试计划中没有用例")
        
        # 生成唯一的执行UUID（整个计划共享）
        execution_uuid = str(uuid.uuid4())
        
        # 构建所有用例的 YAML 文件列表
        all_yaml_cases = []
        combined_yaml_content = ""
        
        for idx, plan_case in enumerate(plan_cases):
            case_info = session.get(ApiInfoCase, plan_case.case_info_id)
            if not case_info:
                continue
            
            # 查询用例步骤
            step_stmt = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == plan_case.case_info_id).order_by(ApiInfoCaseStep.run_order)
            steps = session.exec(step_stmt).all()
            
            if not steps:
                continue
            
            # 构建单个用例
            yaml_data = {
                'desc': case_info.case_name,
                'steps': []
            }
            
            for step in steps:
                step_data_dict = json.loads(step.step_data) if step.step_data else {}
                keyword = session.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
                keyword_name = keyword.keyword_fun_name if keyword else "send_request"
                
                step_item = {
                    step.step_desc or f"步骤{step.run_order}": {
                        '关键字': keyword_name,
                        **step_data_dict
                    }
                }
                yaml_data['steps'].append(step_item)
            
            yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            all_yaml_cases.append({
                'index': idx + 1,
                'case_info': case_info,
                'yaml_data': yaml_data,
                'yaml_content': yaml_content
            })
            combined_yaml_content += f"# 用例 {idx + 1}: {case_info.case_name}\n{yaml_content}\n---\n"
        
        if not all_yaml_cases:
            return respModel.error_resp("没有有效的测试用例")
        
        # 将所有用例合并为一个列表，传递给执行器
        all_cases_list = [item['yaml_data'] for item in all_yaml_cases]
        combined_content = json.dumps(all_cases_list, ensure_ascii=False)
        
        # 执行整个计划（一次执行，一个报告包含所有用例）
        result = await task_scheduler.execute_test(
            session=session,
            plugin_code=plan.plugin_code or 'api_engine',
            test_case_id=request.plan_id,
            test_case_content=combined_content,
            config={}
        )
        
        # 获取执行结果
        is_success = result.get("success", False)
        report_path = result.get("temp_dir", "")
        error_msg = result.get("error") if not is_success else None
        
        # 统计结果
        total_cases = len(all_yaml_cases)
        success_count = total_cases if is_success else 0
        failed_count = 0 if is_success else total_cases
        
        # 创建一条测试历史记录（整个计划一条记录）
        test_history = ApiHistory(
            api_info_id=0,
            project_id=plan.project_id or 0,
            plan_id=request.plan_id,
            case_info_id=0,
            execution_uuid=execution_uuid,
            test_name=plan.plan_name,
            test_status="success" if is_success else "failed",
            yaml_content=combined_yaml_content,
            allure_report_path=report_path or "",
            error_message=error_msg,
            create_time=datetime.now(),
            finish_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(test_history)
        session.commit()
        
        return respModel.ok_resp(dic_t={
            "execution_uuid": execution_uuid,
            "status": "completed",
            "total_cases": total_cases,
            "success_count": success_count,
            "failed_count": failed_count,
            "report_path": report_path,
            "message": f"测试计划执行完成，共 {total_cases} 个用例"
        }, msg="测试计划执行完成")
        
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

