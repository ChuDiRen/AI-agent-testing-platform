"""
接口历史Controller - 已重构为使用Service层
"""
import json
from datetime import datetime

import yaml
from apitest.service.api_history_service import HistoryService
from config.dev_settings import settings
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiHistoryModel import ApiHistory
from ..schemas.api_history_schema import ApiTestHistoryQuery, ApiTestExecuteRequest

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiHistory"
module_model = ApiHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试历史管理"])

# ==================== 路由处理函数 ====================

@module_route.post("/queryByPage", summary="分页查询API测试历史", dependencies=[Depends(check_permission("apitest:history:query"))])
async def queryByPage(query: ApiTestHistoryQuery, session: Session = Depends(get_session)):
    """分页查询测试历史"""
    try:
        service = HistoryService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            project_id=query.project_id,
            api_id=query.api_info_id,
            case_id=query.plan_id,
            execution_status=query.test_status,
            start_time=query.start_date,
            end_time=query.end_date
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/queryById", summary="根据ID查询测试历史")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试历史"""
    try:
        service = HistoryService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.error_resp("测试历史不存在")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/create", summary="创建测试历史记录", dependencies=[Depends(check_permission("apitest:history:add"))])
async def create(history_data: dict, session: Session = Depends(get_session)):
    """创建测试历史记录"""
    try:
        service = HistoryService(session)
        data = service.create(**history_data)
        return respModel.ok_resp(msg="创建成功", dic_t={"id": data.id})
    except Exception as e:
        return respModel.error_resp(msg=f"创建失败: {e}")

@module_route.put("/update", summary="更新测试历史记录", dependencies=[Depends(check_permission("apitest:history:edit"))])
async def update(history_id: int, update_data: dict, session: Session = Depends(get_session)):
    """更新测试历史记录"""
    try:
        service = HistoryService(session)
        updated = service.update(history_id, update_data)
        if not updated:
            return respModel.error_resp("测试历史不存在")
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        return respModel.error_resp(msg=f"更新失败: {e}")

@module_route.delete("/delete", summary="删除测试历史记录", dependencies=[Depends(check_permission("apitest:history:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除测试历史记录"""
    try:
        service = HistoryService(session)
        if not service.delete(id):
            return respModel.error_resp("测试历史不存在")
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        return respModel.error_resp(msg=f"删除失败: {e}")

@module_route.get("/getByProject", summary="根据项目ID获取测试历史")
async def getByProject(project_id: int = Query(...), limit: int = Query(100), session: Session = Depends(get_session)):
    """根据项目ID获取测试历史"""
    try:
        service = HistoryService(session)
        datas = service.query_by_project(project_id, limit)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/getByApi", summary="根据接口ID获取测试历史")
async def getByApi(api_id: int = Query(...), limit: int = Query(50), session: Session = Depends(get_session)):
    """根据接口ID获取测试历史"""
    try:
        service = HistoryService(session)
        datas = service.query_by_api(api_id, limit)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/getByCase", summary="根据用例ID获取测试历史")
async def getByCase(case_id: int = Query(...), limit: int = Query(50), session: Session = Depends(get_session)):
    """根据用例ID获取测试历史"""
    try:
        service = HistoryService(session)
        datas = service.query_by_case(case_id, limit)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        return respModel.error_resp(f"查询失败: {e}")

@module_route.delete("/batchDelete", summary="批量删除测试历史", dependencies=[Depends(check_permission("apitest:history:delete"))])
async def batch_delete(history_ids: list[int], session: Session = Depends(get_session)):
    """批量删除测试历史"""
    try:
        service = HistoryService(session)
        deleted_count = service.batch_delete(history_ids)
        return respModel.ok_resp(msg=f"成功删除 {deleted_count} 条记录")
    except Exception as e:
        return respModel.error_resp(msg=f"批量删除失败: {e}")

@module_route.delete("/clean", summary="清理旧的历史记录", dependencies=[Depends(check_permission("apitest:history:delete"))])
async def clean_old_records(project_id: int = Query(...), days: int = Query(30), session: Session = Depends(get_session)):
    """清理旧的历史记录"""
    try:
        service = HistoryService(session)
        deleted_count = service.clean_old_records(project_id, days)
        return respModel.ok_resp(msg=f"成功清理 {deleted_count} 条旧记录")
    except Exception as e:
        return respModel.error_resp(msg=f"清理失败: {e}")

@module_route.get("/getStatistics", summary="获取测试历史统计信息")
async def getStatistics(project_id: int = Query(...), days: int = Query(7), session: Session = Depends(get_session)):
    """获取测试历史统计信息"""
    try:
        service = HistoryService(session)
        stats = service.get_statistics(project_id, days)
        return respModel.ok_resp(obj=stats)
    except Exception as e:
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/execute", summary="执行API接口测试")
async def execute_test(request: ApiTestExecuteRequest, session: Session = Depends(get_session)):
    """
    执行接口测试（基于 ApiInfo 模型）
    
    注意：此接口用于接口级别的快速测试，会自动生成 YAML 并通过统一的 TaskScheduler 执行。
    如需执行用例级别测试，请使用 /ApiInfoCase/executeCase 接口。
    """
    try:
        # 1. 获取接口信息
        api_info = session.get(ApiInfo, request.api_info_id)
        if not api_info:
            return respModel.error_resp("接口信息不存在")
        
        # 2. 创建测试历史记录
        test_name = request.test_name or f"接口测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_history = module_model(
            api_info_id=request.api_info_id,
            project_id=api_info.project_id or 0,
            test_name=test_name,
            test_status="running",
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(test_history)
        session.commit()
        session.refresh(test_history)
        
        # 3. 生成 YAML 测试用例
        def _parse_json(field_value):
            if not field_value:
                return None
            try:
                return json.loads(field_value) if isinstance(field_value, str) else field_value
            except (json.JSONDecodeError, TypeError):
                return None
        
        # 构建请求步骤
        step_data = {'关键字': 'send_request', 'method': api_info.request_method or 'GET', 'url': api_info.request_url or ''}
        if _parse_json(api_info.request_params):
            step_data['params'] = _parse_json(api_info.request_params)
        if _parse_json(api_info.request_headers):
            step_data['headers'] = _parse_json(api_info.request_headers)
        if api_info.request_method in ['POST', 'PUT', 'PATCH']:
            body_data = _parse_json(api_info.request_form_datas) or _parse_json(api_info.request_www_form_datas)
            if body_data:
                step_data['data'] = body_data
            json_data = _parse_json(api_info.requests_json_data)
            if json_data:
                step_data['json'] = json_data
        
        test_case = {'desc': test_name, 'steps': [{api_info.api_name or '发送请求': step_data}]}
        
        # 添加变量提取步骤
        for extract in (request.variable_extracts or []):
            var_name = extract.get('var_name', '')
            step_name = extract.get('description') or f"提取_{var_name}"
            test_case['steps'].append({step_name: {
                '关键字': 'ex_jsonData',
                'EXVALUE': extract.get('extract_path', ''),
                'VARNAME': var_name,
                'INDEX': str(extract.get('index', 0))
            }})
        
        # 添加断言步骤
        for assertion in (request.assertions or []):
            step_name = assertion.get('description') or '断言验证'
            test_case['steps'].append({step_name: {
                '关键字': 'assert_text_comparators',
                'VALUE': assertion.get('actual_value', ''),
                'EXPECTED': assertion.get('expected_value', ''),
                'OP_STR': assertion.get('operator', '==')
            }})
        
        # 添加数据驱动
        if request.context_vars:
            test_case['ddts'] = [{'desc': f'{test_name}_数据', **request.context_vars}]
        
        yaml_content = yaml.dump(test_case, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # 4. 创建工作空间并写入 YAML 文件
        workspace = get_temp_subdir("executor") / f"api_{test_history.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        workspace.mkdir(parents=True, exist_ok=True)
        yaml_filename = f"{api_info.api_name or 'test'}_{test_history.id}.yaml"
        (workspace / yaml_filename).write_text(yaml_content, encoding='utf-8')
        
        # 更新历史记录的 YAML 内容
        test_history.yaml_content = yaml_content
        test_history.allure_report_path = str(workspace)
        test_history.request_url = api_info.request_url
        test_history.request_method = api_info.request_method
        test_history.request_headers = api_info.request_headers
        test_history.request_params = api_info.request_params
        test_history.request_body = api_info.requests_json_data or api_info.request_form_datas
        session.commit()
        
        # 5. 提交后台执行任务
        def _run_api_test(test_id: int, workspace_path: str):
            from core.database import engine
            from sqlmodel import Session as DBSession
            
            db = DBSession(engine)
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        task_scheduler.execute_test(
                            session=db,
                            plugin_code="api_engine",
                            test_case_id=test_id,
                            test_case_content=workspace_path,
                            config={"is_directory": True}
                        )
                    )
                finally:
                    loop.close()
                
                # 更新结果
                collector = ResultCollector(db)
                collector.update_single_case_result(test_id, result)
                logger.info(f"接口测试完成: test_id={test_id}, success={result.get('success')}")
                
            except Exception as e:
                logger.error(f"接口测试失败: test_id={test_id}, 错误: {e}", exc_info=True)
                try:
                    collector = ResultCollector(db)
                    collector.mark_failed(test_id, str(e))
                except:
                    pass
            finally:
                db.close()
        
        # 使用线程池执行
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(_run_api_test, test_history.id, str(workspace))
        
        return respModel.ok_resp(dic_t={"test_id": test_history.id, "status": "running"}, msg="测试已开始执行")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/status", summary="查询API测试状态")
async def get_test_status(test_id: int = Query(...), session: Session = Depends(get_session)):
    """查询测试状态"""
    try:
        test_history = session.get(module_model, test_id)
        if not test_history:
            return respModel.error_resp("测试记录不存在")

        result = {
            "test_id": test_history.id,
            "status": test_history.test_status,
            "response_time": test_history.response_time,
            "status_code": test_history.status_code,
            "error_message": test_history.error_message,
            "allure_report_path": test_history.allure_report_path,
            "create_time": TimeFormatter.format_datetime(test_history.create_time),
            "finish_time": TimeFormatter.format_datetime(test_history.finish_time)
        }
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API测试历史", dependencies=[Depends(check_permission("apitest:history:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除测试历史"""
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

@module_route.get("/queryByPlanId", summary="根据测试计划ID查询历史记录")
async def queryByPlanId(plan_id: int = Query(...), session: Session = Depends(get_session)):
    """根据测试计划ID查询历史记录"""
    try:
        statement = select(module_model).where(module_model.plan_id == plan_id).order_by(module_model.create_time.desc())
        datas = session.exec(statement).all()
        
        result_list = []
        for data in datas:
            item = {
                "id": data.id,
                "plan_id": data.plan_id,
                "case_info_id": data.case_info_id,
                "execution_uuid": data.execution_uuid,
                "test_name": data.test_name,
                "test_status": data.test_status,
                "response_time": data.response_time,
                "status_code": data.status_code,
                "error_message": data.error_message,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "finish_time": TimeFormatter.format_datetime(data.finish_time)
            }
            result_list.append(item)
        
        return respModel.ok_resp(obj=result_list, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryByExecutionUuid", summary="根据批量执行UUID查询历史记录")
async def queryByExecutionUuid(execution_uuid: str = Query(...), session: Session = Depends(get_session)):
    """根据批量执行UUID查询历史记录"""
    try:
        statement = select(module_model).where(module_model.execution_uuid == execution_uuid).order_by(module_model.create_time)
        datas = session.exec(statement).all()
        
        result_list = []
        for data in datas:
            item = {
                "id": data.id,
                "plan_id": data.plan_id,
                "case_info_id": data.case_info_id,
                "execution_uuid": data.execution_uuid,
                "test_name": data.test_name,
                "test_status": data.test_status,
                "response_time": data.response_time,
                "status_code": data.status_code,
                "error_message": data.error_message,
                "allure_report_path": data.allure_report_path,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "finish_time": TimeFormatter.format_datetime(data.finish_time)
            }
            result_list.append(item)
        
        return respModel.ok_resp(obj=result_list, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
