import json
import subprocess
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

from ..model.ApiHistoryModel import ApiHistory
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..schemas.api_info_case_schema import (
    ApiInfoCaseQuery, ApiInfoCaseCreate, ApiInfoCaseUpdate,
    YamlGenerateRequest,
    ApiInfoCaseExecuteRequest
)
from config.dev_settings import settings
from plugin.model.PluginModel import Plugin
from plugin.service.TaskScheduler import task_scheduler

logger = get_logger(__name__)

# ==================== 配置常量 ====================
# ✅ P2修复: 使用配置管理的路径,避免硬编码
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiInfoCase"
module_model = ApiInfoCase
module_route = APIRouter(prefix=f"/{module_name}", tags=["API用例管理"])

# ==================== 路由处理函数 ====================

@module_route.post("/queryByPage", summary="分页查询API用例", dependencies=[Depends(check_permission("apitest:case:query"))])
async def queryByPage(query: ApiInfoCaseQuery, session: Session = Depends(get_session)):
    """分页查询用例"""
    try:
        statement = select(module_model)
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.case_name:
            statement = statement.where(module_model.case_name.like(f"%{query.case_name}%"))

        offset = (query.page - 1) * query.pageSize
        datas = session.exec(statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)).all()
        total = len(session.exec(statement).all())
        
        # 转换时间格式
        result_list = []
        for data in datas:
            item = {
                "id": data.id,
                "project_id": data.project_id,
                "case_name": data.case_name,
                "case_desc": data.case_desc,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "modify_time": TimeFormatter.format_datetime(data.modify_time)
            }
            result_list.append(item)
        
        return respModel.ok_resp_list(lst=result_list, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API用例（含步骤）", dependencies=[Depends(check_permission("apitest:case:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询用例（含步骤）"""
    try:
        # 查询用例基本信息
        case_info = session.get(module_model, id)
        if not case_info:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 查询用例步骤
        statement = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == id).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        # 解析step_data为对象
        def parse_step_data(step_data_str):
            if not step_data_str:
                return {}
            try:
                return json.loads(step_data_str)
            except:
                return {}
        
        # 构建响应
        result = {
            "id": case_info.id,
            "project_id": case_info.project_id,
            "case_name": case_info.case_name,
            "case_desc": case_info.case_desc,
            "create_time": TimeFormatter.format_datetime(case_info.create_time),
            "modify_time": TimeFormatter.format_datetime(case_info.modify_time),
            "steps": [
                {
                    "id": step.id,
                    "case_info_id": step.case_info_id,
                    "run_order": step.run_order,
                    "step_desc": step.step_desc,
                    "operation_type_id": step.operation_type_id,
                    "keyword_id": step.keyword_id,
                    "step_data": parse_step_data(step.step_data),
                    "create_time": TimeFormatter.format_datetime(step.create_time)
                } for step in steps
            ]
        }
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API用例（含步骤）", dependencies=[Depends(check_permission("apitest:case:add"))])
async def insert(data: ApiInfoCaseCreate, session: Session = Depends(get_session)):
    """新增用例（含步骤）"""
    try:
        # 创建用例基本信息
        case_info = module_model(
            project_id=data.project_id,
            case_name=data.case_name,
            case_desc=data.case_desc,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(case_info)
        session.flush()  # 获取case_info.id
        
        # 创建步骤
        if data.steps:
            for step_data in data.steps:
                step = ApiInfoCaseStep(
                    case_info_id=case_info.id,
                    run_order=step_data.run_order,
                    step_desc=step_data.step_desc,
                    operation_type_id=step_data.operation_type_id,
                    keyword_id=step_data.keyword_id,
                    step_data=json.dumps(step_data.step_data, ensure_ascii=False) if step_data.step_data else None,
                    create_time=datetime.now()
                )
                session.add(step)
        
        session.commit()
        return respModel.ok_resp_text(msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新API用例（含步骤）", dependencies=[Depends(check_permission("apitest:case:edit"))])
async def update(data: ApiInfoCaseUpdate, session: Session = Depends(get_session)):
    """更新用例（含步骤）"""
    try:
        # 更新用例基本信息
        case_info = session.get(module_model, data.id)
        if not case_info:
            return respModel.error_resp("用例不存在")
        
        if data.project_id is not None:
            case_info.project_id = data.project_id
        if data.case_name is not None:
            case_info.case_name = data.case_name
        if data.case_desc is not None:
            case_info.case_desc = data.case_desc
        case_info.modify_time = datetime.now()
        
        # 更新步骤：先删除旧步骤，再创建新步骤
        if data.steps is not None:
            # 删除旧步骤
            old_steps = session.exec(select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == data.id)).all()
            for old_step in old_steps:
                session.delete(old_step)
            
            # 创建新步骤
            for step_data in data.steps:
                step = ApiInfoCaseStep(
                    case_info_id=data.id,
                    run_order=step_data.run_order,
                    step_desc=step_data.step_desc,
                    operation_type_id=step_data.operation_type_id,
                    keyword_id=step_data.keyword_id,
                    step_data=json.dumps(step_data.step_data, ensure_ascii=False) if step_data.step_data else None,
                    create_time=datetime.now()
                )
                session.add(step)
        
        session.commit()
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API用例", dependencies=[Depends(check_permission("apitest:case:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用例（含关联步骤）"""
    try:
        obj = session.get(module_model, id)
        if obj:
            # 先删除关联的步骤
            steps = session.exec(select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == id)).all()
            for step in steps:
                session.delete(step)
            # 再删除用例
            session.delete(obj)
            session.commit()
            return respModel.ok_resp_text(msg="删除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getSteps", summary="获取用例步骤", dependencies=[Depends(check_permission("apitest:case:query"))])
async def getSteps(case_id: int = Query(...), session: Session = Depends(get_session)):
    """获取用例的所有步骤"""
    try:
        statement = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_id).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        def parse_step_data(step_data_str):
            if not step_data_str:
                return {}
            try:
                return json.loads(step_data_str)
            except:
                return {}
        
        result = [
            {
                "id": step.id,
                "case_info_id": step.case_info_id,
                "run_order": step.run_order,
                "step_desc": step.step_desc,
                "operation_type_id": step.operation_type_id,
                "keyword_id": step.keyword_id,
                "step_data": parse_step_data(step.step_data),
                "create_time": TimeFormatter.format_datetime(step.create_time)
            } for step in steps
        ]
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/generateYaml", summary="生成用例YAML文件", dependencies=[Depends(check_permission("apitest:case:generate"))])
async def generateYaml(request: YamlGenerateRequest, session: Session = Depends(get_session)):
    """生成用例YAML文件"""
    try:
        # 查询用例信息
        case_info = session.get(ApiInfoCase, request.case_id)
        if not case_info:
            return respModel.error_resp("用例不存在")
        
        # 查询用例步骤
        statement = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == request.case_id).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        if not steps:
            return respModel.error_resp("用例没有步骤")
        
        # 构建YAML内容
        yaml_data = {
            'desc': case_info.case_name,
            'steps': []
        }
        
        # 转换步骤为YAML格式
        for step in steps:
            # 解析步骤数据
            step_data_dict = json.loads(step.step_data) if step.step_data else {}
            
            # 获取关键字信息
            keyword = session.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
            keyword_name = keyword.keyword_fun_name if keyword else "unknown"
            
            # 构建步骤
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': keyword_name,
                    **step_data_dict
                }
            }
            yaml_data['steps'].append(step_item)
        
        # 添加上下文变量
        if request.context_vars:
            yaml_data['ddts'] = [{
                'desc': f'{case_info.case_name}_数据',
                **request.context_vars
            }]
        
        # 生成YAML内容
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # 保存到文件
        YAML_DIR.mkdir(parents=True, exist_ok=True)
        yaml_filename = f"{case_info.case_name}_{request.case_id}.yaml"
        yaml_file_path = YAML_DIR / yaml_filename
        yaml_file_path.write_text(yaml_content, encoding='utf-8')
        
        return respModel.ok_resp(dic_t={
            "yaml_content": yaml_content,
            "file_path": str(yaml_file_path)
        }, msg="YAML生成成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/executeCase", summary="执行用例测试（异步）", dependencies=[Depends(check_permission("apitest:case:execute"))])
async def executeCase(
    request: ApiInfoCaseExecuteRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    异步执行用例测试
    支持两种模式：
    - 单用例执行：提供 case_id
    - 批量执行计划：提供 plan_id（执行计划中所有用例，生成一份报告）
    接口立即返回 test_id，前端通过 /executionStatus 接口轮询结果
    """
    import uuid
    
    try:
        # 参数校验
        if not request.case_id and not request.plan_id:
            return respModel.error_resp("请提供 case_id 或 plan_id")
        
        # 选择执行器插件
        plugin_code = request.executor_code or "api_engine"
        plugin = session.exec(
            select(Plugin).where(Plugin.plugin_code == plugin_code)
        ).first()
        if not plugin:
            return respModel.error_resp(f"执行器插件不存在: {plugin_code}")
        if plugin.is_enabled != 1:
            return respModel.error_resp(f"执行器插件未启用: {plugin_code}")
        if plugin.plugin_type != "executor":
            return respModel.error_resp(f"插件类型错误: {plugin.plugin_type}")
        
        # ==================== 批量执行计划模式 ====================
        if request.plan_id:
            plan = session.get(ApiCollectionInfo, request.plan_id)
            if not plan:
                return respModel.error_resp("测试计划不存在")
            
            # 查询计划中的所有用例
            case_stmt = select(ApiCollectionDetail).where(
                ApiCollectionDetail.collection_info_id == request.plan_id
            ).order_by(ApiCollectionDetail.run_order)
            plan_cases = session.exec(case_stmt).all()
            
            if not plan_cases:
                return respModel.error_resp("测试计划中没有用例")
            
            # 生成唯一的执行UUID
            execution_uuid = str(uuid.uuid4())
            
            # 构建所有用例的 YAML 数据
            all_yaml_cases = []
            combined_yaml_content = ""
            
            for idx, plan_case in enumerate(plan_cases):
                case_info = session.get(ApiInfoCase, plan_case.case_info_id)
                if not case_info:
                    continue
                
                # 查询用例步骤
                step_stmt = select(ApiInfoCaseStep).where(
                    ApiInfoCaseStep.case_info_id == plan_case.case_info_id
                ).order_by(ApiInfoCaseStep.run_order)
                steps = session.exec(step_stmt).all()
                
                if not steps:
                    continue
                
                # 构建单个用例
                yaml_data = {'desc': case_info.case_name, 'steps': []}
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
                
                yaml_content_single = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                all_yaml_cases.append(yaml_data)
                combined_yaml_content += f"# 用例 {idx + 1}: {case_info.case_name}\n{yaml_content_single}\n---\n"
            
            if not all_yaml_cases:
                return respModel.error_resp("没有有效的测试用例")
            
            # 创建测试历史记录
            test_name = request.test_name or f"{plan.plan_name}_测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            test_history = ApiHistory(
                api_info_id=0,
                case_info_id=0,
                project_id=plan.project_id or 0,
                plan_id=request.plan_id,
                execution_uuid=execution_uuid,
                test_name=test_name,
                test_status="running",
                yaml_content=combined_yaml_content,
                create_time=datetime.now(),
                modify_time=datetime.now()
            )
            session.add(test_history)
            session.commit()
            session.refresh(test_history)
            
            # 创建工作空间
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            workspace_name = f"plan_{test_history.id}_{timestamp}"
            yaml_dir = YAML_DIR / workspace_name
            report_dir = REPORT_DIR / workspace_name
            for directory in [TEMP_DIR, YAML_DIR, REPORT_DIR, LOG_DIR, yaml_dir, report_dir]:
                directory.mkdir(exist_ok=True)
            
            # 保存 YAML 文件
            yaml_filename = f"{plan.plan_name}_{test_history.id}.yaml"
            (yaml_dir / yaml_filename).write_text(combined_yaml_content, encoding='utf-8')
            test_history.allure_report_path = str(report_dir)
            session.commit()
            
            # 将所有用例合并为一个列表传递给执行器
            combined_content = json.dumps(all_yaml_cases, ensure_ascii=False)
            test_id = test_history.id
            total_cases = len(all_yaml_cases)
            
            def _execute_plan_in_background():
                import asyncio
                from core.database import engine
                from sqlmodel import Session as DBSession
                db = DBSession(engine)
                try:
                    hist = db.get(ApiHistory, test_id)
                    if not hist:
                        logger.warning(f"测试记录不存在: {test_id}")
                        return
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(
                            task_scheduler.execute_test(
                                session=db,
                                plugin_code=plugin_code,
                                test_case_id=test_id,
                                test_case_content=combined_content,
                                config={}
                            )
                        )
                    finally:
                        loop.close()
                    
                    logger.info(f"计划执行结果: success={result.get('success')}, temp_dir={result.get('temp_dir')}")
                    if result.get("success"):
                        hist.test_status = result.get("status", "completed")
                        if result.get("result"):
                            hist.response_data = json.dumps(result.get("result"), ensure_ascii=False)
                        temp_dir = result.get("temp_dir")
                        if temp_dir:
                            hist.allure_report_path = temp_dir
                    else:
                        hist.test_status = "failed"
                        hist.error_message = result.get("error")
                    
                    hist.finish_time = datetime.now()
                    hist.modify_time = datetime.now()
                    db.commit()
                    logger.info(f"计划测试完成: {test_id}, 状态: {hist.test_status}")
                    
                except Exception as e:
                    logger.error(f"计划执行失败: {test_id}, 错误: {e}", exc_info=True)
                    try:
                        hist = db.get(ApiHistory, test_id)
                        if hist:
                            hist.test_status = "failed"
                            hist.error_message = str(e)
                            hist.finish_time = datetime.now()
                            db.commit()
                    except:
                        pass
                finally:
                    db.close()
            
            background_tasks.add_task(_execute_plan_in_background)
            
            return respModel.ok_resp(
                dic_t={
                    "test_id": test_id,
                    "execution_uuid": execution_uuid,
                    "status": "running",
                    "total_cases": total_cases,
                    "plan_id": request.plan_id
                },
                msg="测试计划已提交，请通过 executionStatus 接口查询结果"
            )
        
        # ==================== 单用例执行模式 ====================
        case_info = session.get(ApiInfoCase, request.case_id)
        if not case_info:
            return respModel.error_resp("用例不存在")

        # 创建测试历史记录
        test_name = request.test_name or f"{case_info.case_name}_测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_history = ApiHistory(
            api_info_id=0,
            case_info_id=request.case_id,
            project_id=case_info.project_id or 0,
            test_name=test_name,
            test_status="running",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(test_history)
        session.commit()
        session.refresh(test_history)

        # 创建工作空间
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        workspace_name = f"case_{test_history.id}_{timestamp}"
        yaml_dir = YAML_DIR / workspace_name
        report_dir = REPORT_DIR / workspace_name
        for directory in [TEMP_DIR, YAML_DIR, REPORT_DIR, LOG_DIR, yaml_dir, report_dir]:
            directory.mkdir(exist_ok=True)

        # 生成 YAML 内容
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == request.case_id
        ).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()

        yaml_data = {'desc': case_info.case_name, 'steps': []}
        for step in steps:
            step_data_dict = json.loads(step.step_data) if step.step_data else {}
            keyword = session.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
            keyword_name = keyword.keyword_fun_name if keyword else "unknown"
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': keyword_name,
                    **step_data_dict
                }
            }
            yaml_data['steps'].append(step_item)

        if request.context_vars:
            yaml_data['ddts'] = [{'desc': f'{case_info.case_name}_数据', **request.context_vars}]

        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        yaml_filename = f"{case_info.case_name}_{test_history.id}.yaml"
        (yaml_dir / yaml_filename).write_text(yaml_content, encoding='utf-8')

        # 保存 yaml_content 到历史记录
        test_history.yaml_content = yaml_content
        test_history.allure_report_path = str(report_dir)
        session.commit()

        # 定义后台任务
        test_id = test_history.id
        def _execute_in_background():
            import asyncio
            from core.database import engine
            from sqlmodel import Session as DBSession
            db = DBSession(engine)
            try:
                hist = db.get(ApiHistory, test_id)
                if not hist:
                    logger.warning(f"测试记录不存在: {test_id}")
                    return

                # 执行测试
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        task_scheduler.execute_test(
                            session=db,
                            plugin_code=plugin_code,
                            test_case_id=test_id,
                            test_case_content=yaml_content,
                            config=None
                        )
                    )
                finally:
                    loop.close()

                # 更新状态
                logger.info(f"执行结果: success={result.get('success')}, temp_dir={result.get('temp_dir')}")
                if result.get("success"):
                    hist.test_status = result.get("status", "completed")
                    # 保存执行结果数据
                    if result.get("result"):
                        hist.response_data = json.dumps(result.get("result"), ensure_ascii=False)
                    # 更新报告路径（temp_dir 是执行目录，报告在其中）
                    temp_dir = result.get("temp_dir")
                    if temp_dir:
                        hist.allure_report_path = temp_dir
                        logger.info(f"报告路径已更新: {temp_dir}")
                else:
                    hist.test_status = "failed"
                    hist.error_message = result.get("error")

                hist.finish_time = datetime.now()
                hist.modify_time = datetime.now()
                db.commit()
                logger.info(f"用例测试完成: {test_id}, 状态: {hist.test_status}")

            except Exception as e:
                logger.error(f"后台执行失败: {test_id}, 错误: {e}", exc_info=True)
                try:
                    hist = db.get(ApiHistory, test_id)
                    if hist:
                        hist.test_status = "failed"
                        hist.error_message = str(e)
                        hist.finish_time = datetime.now()
                        db.commit()
                except:
                    pass
            finally:
                db.close()

        # 添加后台任务
        background_tasks.add_task(_execute_in_background)

        return respModel.ok_resp(
            dic_t={"test_id": test_id, "status": "running"},
            msg="用例测试已提交，请通过 executionStatus 接口查询结果"
        )
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {str(e)}")


@module_route.get("/executionStatus", summary="查询用例执行状态", dependencies=[Depends(check_permission("apitest:case:query"))])
async def executionStatus(test_id: int = Query(..., description="测试ID"), session: Session = Depends(get_session)):
    """
    查询用例执行状态
    前端轮询此接口获取执行结果
    """
    try:
        history = session.get(ApiHistory, test_id)
        if not history:
            return respModel.error_resp("测试记录不存在")

        result = {
            "test_id": history.id,
            "status": history.test_status,
            "test_name": history.test_name,
            "error_message": history.error_message,
            "yaml_content": history.yaml_content,
            "response_data": history.response_data,
            "create_time": TimeFormatter.datetime_to_str(history.create_time) if history.create_time else None,
            "finish_time": TimeFormatter.datetime_to_str(history.finish_time) if history.finish_time else None,
        }

        # 判断是否完成
        is_finished = history.test_status in ["completed", "passed", "failed", "error"]
        
        return respModel.ok_resp(
            dic_t={"data": result, "finished": is_finished},
            msg="查询成功"
        )
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {str(e)}")
