from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger
from core.database import get_session
from core.time_utils import TimeFormatter
from ..model.ApiTestPlanModel import ApiTestPlan
from ..model.ApiPlanCaseModel import ApiPlanCase
from ..model.ApiCaseInfoModel import ApiCaseInfo
from ..model.ApiInfoStepModel import ApiInfoStep
from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiTestHistoryModel import ApiTestHistory
from ..schemas.api_test_plan_schema import (
    ApiTestPlanQuery, ApiTestPlanCreate, ApiTestPlanUpdate,
    ApiPlanCaseCreate, BatchAddCasesRequest, UpdateDdtDataRequest,
    ApiTestPlanExecuteRequest
)
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml
import json
import uuid

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
YAML_DIR = TEMP_DIR / "yaml_cases"
REPORT_DIR = TEMP_DIR / "allure_reports"
LOG_DIR = TEMP_DIR / "logs"

module_name = "ApiTestPlan"
module_model = ApiTestPlan
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试计划管理"])

# ==================== 测试计划CRUD ====================

@module_route.post("/queryByPage")
def queryByPage(query: ApiTestPlanQuery, session: Session = Depends(get_session)):
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
            case_count_stmt = select(ApiPlanCase).where(ApiPlanCase.plan_id == data.id)
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

@module_route.get("/queryById")
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试计划（含关联用例）"""
    try:
        plan = session.get(module_model, id)
        if not plan:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 查询关联的用例
        case_stmt = select(ApiPlanCase).where(ApiPlanCase.plan_id == id).order_by(ApiPlanCase.run_order)
        plan_cases = session.exec(case_stmt).all()
        
        cases = []
        for pc in plan_cases:
            # 查询用例信息
            case_info = session.get(ApiCaseInfo, pc.case_info_id)
            cases.append({
                "id": pc.id,
                "plan_id": pc.plan_id,
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

@module_route.post("/insert")
def insert(data: ApiTestPlanCreate, session: Session = Depends(get_session)):
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

@module_route.put("/update")
def update(data: ApiTestPlanUpdate, session: Session = Depends(get_session)):
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

@module_route.delete("/delete")
def delete(id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.post("/addCase")
def addCase(data: ApiPlanCaseCreate, session: Session = Depends(get_session)):
    """添加用例到计划"""
    try:
        # 检查是否已存在
        check_stmt = select(ApiPlanCase).where(
            ApiPlanCase.plan_id == data.plan_id,
            ApiPlanCase.case_info_id == data.case_info_id
        )
        existing = session.exec(check_stmt).first()
        if existing:
            return respModel.error_resp("该用例已添加到计划中")
        
        plan_case = ApiPlanCase(
            plan_id=data.plan_id,
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

@module_route.post("/batchAddCases")
def batchAddCases(data: BatchAddCasesRequest, session: Session = Depends(get_session)):
    """批量添加用例到计划"""
    try:
        added_count = 0
        for idx, case_id in enumerate(data.case_ids):
            # 检查是否已存在
            check_stmt = select(ApiPlanCase).where(
                ApiPlanCase.plan_id == data.plan_id,
                ApiPlanCase.case_info_id == case_id
            )
            existing = session.exec(check_stmt).first()
            if not existing:
                plan_case = ApiPlanCase(
                    plan_id=data.plan_id,
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

@module_route.delete("/removeCase")
def removeCase(plan_case_id: int = Query(...), session: Session = Depends(get_session)):
    """从计划中移除用例"""
    try:
        obj = session.get(ApiPlanCase, plan_case_id)
        if obj:
            session.delete(obj)
            session.commit()
            return respModel.ok_resp_text(msg="移除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/updateDdtData")
def updateDdtData(data: UpdateDdtDataRequest, session: Session = Depends(get_session)):
    """更新用例的数据驱动数据"""
    try:
        plan_case = session.get(ApiPlanCase, data.plan_case_id)
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

@module_route.post("/executePlan")
def executePlan(request: ApiTestPlanExecuteRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """执行测试计划（批量执行用例）"""
    try:
        # 查询测试计划
        plan = session.get(ApiTestPlan, request.plan_id)
        if not plan:
            return respModel.error_resp("测试计划不存在")
        
        # 查询计划中的所有用例
        case_stmt = select(ApiPlanCase).where(ApiPlanCase.plan_id == request.plan_id).order_by(ApiPlanCase.run_order)
        plan_cases = session.exec(case_stmt).all()
        
        if not plan_cases:
            return respModel.error_resp("测试计划中没有用例")
        
        # 生成唯一的执行UUID
        execution_uuid = str(uuid.uuid4())
        
        # 定义后台任务
        def _execute_plan_background():
            from core.database import SessionLocal
            db = SessionLocal()
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                workspace_name = f"plan_{request.plan_id}_{timestamp}_{execution_uuid[:8]}"
                yaml_dir = YAML_DIR / workspace_name
                report_dir = REPORT_DIR / workspace_name
                log_file = LOG_DIR / f"{workspace_name}.log"
                
                for directory in [TEMP_DIR, YAML_DIR, REPORT_DIR, LOG_DIR, yaml_dir, report_dir]:
                    directory.mkdir(exist_ok=True)
                
                # 遍历所有用例，生成YAML文件
                all_yaml_files = []
                for plan_case in plan_cases:
                    case_info = db.get(ApiCaseInfo, plan_case.case_info_id)
                    if not case_info:
                        continue
                    
                    # 查询用例步骤
                    step_stmt = select(ApiInfoStep).where(ApiInfoStep.case_info_id == plan_case.case_info_id).order_by(ApiInfoStep.run_order)
                    steps = db.exec(step_stmt).all()
                    
                    if not steps:
                        continue
                    
                    # 解析数据驱动数据
                    ddt_data_list = []
                    if plan_case.ddt_data:
                        try:
                            ddt_data_list = json.loads(plan_case.ddt_data)
                        except:
                            ddt_data_list = []
                    
                    # 如果没有数据驱动，生成一个默认用例
                    if not ddt_data_list:
                        ddt_data_list = [{}]
                    
                    # 为每组数据生成一个YAML文件
                    for idx, ddt_data in enumerate(ddt_data_list):
                        yaml_data = {
                            'desc': f"{case_info.case_name}_数据组{idx+1}" if len(ddt_data_list) > 1 else case_info.case_name,
                            'steps': []
                        }
                        
                        # 构建步骤
                        for step in steps:
                            step_data_dict = json.loads(step.step_data) if step.step_data else {}
                            keyword = db.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
                            keyword_name = keyword.keyword_fun_name if keyword else "unknown"
                            
                            step_item = {
                                step.step_desc or f"步骤{step.run_order}": {
                                    '关键字': keyword_name,
                                    **step_data_dict
                                }
                            }
                            yaml_data['steps'].append(step_item)
                        
                        # 添加数据驱动节点
                        if ddt_data:
                            yaml_data['ddts'] = [{
                                'desc': ddt_data.get('desc', f'数据组{idx+1}'),
                                **{k: v for k, v in ddt_data.items() if k != 'desc'}
                            }]
                        
                        # 生成YAML内容
                        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                        
                        # 写入文件
                        yaml_filename = f"{plan_case.run_order:03d}_{case_info.case_name}_data{idx+1}.yaml"
                        yaml_file_path = yaml_dir / yaml_filename
                        yaml_file_path.write_text(yaml_content, encoding='utf-8')
                        all_yaml_files.append(yaml_file_path)
                        
                        # 创建测试历史记录
                        test_history = ApiTestHistory(
                            api_info_id=0,
                            project_id=plan.project_id or 0,
                            plan_id=request.plan_id,
                            case_info_id=plan_case.case_info_id,
                            execution_uuid=execution_uuid,
                            test_name=f"{plan.plan_name}_{case_info.case_name}_数据组{idx+1}",
                            test_status="running",
                            yaml_content=yaml_content,
                            allure_report_path=str(report_dir),
                            create_time=datetime.now(),
                            modify_time=datetime.now()
                        )
                        db.add(test_history)
                
                db.commit()
                
                # 批量执行所有YAML文件
                command = ['huace-apirun', '--cases', str(yaml_dir), '--alluredir', str(report_dir)]
                exec_success = False
                exec_error = None
                exec_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                try:
                    start_time = datetime.now()
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
                    stdout, stderr = process.communicate(timeout=600)  # 10分钟超时
                    end_time = datetime.now()
                    exec_success = process.returncode == 0
                    
                    log_content = f"=== 批量执行命令 ===\n{' '.join(command)}\n\n=== 开始时间 ===\n{exec_start_time}\n\n=== 结束时间 ===\n{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n=== 执行时长 ===\n{(end_time - start_time).total_seconds()}秒\n\n=== 返回码 ===\n{process.returncode}\n\n=== YAML文件数 ===\n{len(all_yaml_files)}\n\n=== 标准输出 ===\n{stdout}\n\n=== 错误输出 ===\n{stderr}\n"
                    log_file.write_text(log_content, encoding='utf-8')
                except subprocess.TimeoutExpired:
                    exec_error = '测试执行超时（600秒）'
                    process.kill()
                except FileNotFoundError:
                    exec_error = 'huace-apirun命令不存在，请确认api-engine已正确安装'
                except Exception as e:
                    exec_error = f'执行失败: {str(e)}'
                
                # 更新所有测试历史记录
                update_stmt = select(ApiTestHistory).where(ApiTestHistory.execution_uuid == execution_uuid)
                test_histories = db.exec(update_stmt).all()
                for hist in test_histories:
                    hist.test_status = "success" if exec_success else "failed"
                    if exec_error:
                        hist.error_message = exec_error
                    hist.finish_time = datetime.now()
                    hist.modify_time = datetime.now()
                
                db.commit()
                logger.info(f"测试计划执行完成: {request.plan_id}, UUID: {execution_uuid}, 结果: {'成功' if exec_success else '失败'}")
                
            except Exception as e:
                logger.error(f"测试计划执行失败: {request.plan_id}, 错误: {e}", exc_info=True)
            finally:
                db.close()
        
        # 添加后台任务
        background_tasks.add_task(_execute_plan_background)
        
        return respModel.ok_resp(dic_t={
            "execution_uuid": execution_uuid,
            "status": "running",
            "total_cases": len(plan_cases),
            "message": "测试计划已开始执行"
        }, msg="测试计划已开始执行")
        
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

