from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger
from core.database import get_session
from core.dependencies import check_permission
from core.time_utils import TimeFormatter
from ..model.ApiHistoryModel import ApiHistory
from ..model.ApiInfoModel import ApiInfo
from ..schemas.api_history_schema import ApiTestHistoryQuery, ApiTestExecuteRequest, ApiTestResult
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml
import json

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
YAML_DIR = TEMP_DIR / "yaml_cases"
REPORT_DIR = TEMP_DIR / "allure_reports"
LOG_DIR = TEMP_DIR / "logs"

module_name = "ApiTest"
module_model = ApiHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口测试管理"])

# ==================== 路由处理函数 ====================
@module_route.post("/queryByPage", dependencies=[Depends(check_permission("apitest:history:query"))])
def queryByPage(query: ApiTestHistoryQuery, session: Session = Depends(get_session)):
    """分页查询测试历史"""
    try:
        statement = select(module_model)
        if query.api_info_id:
            statement = statement.where(module_model.api_info_id == query.api_info_id)
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.test_status:
            statement = statement.where(module_model.test_status == query.test_status)
        if query.start_date:
            statement = statement.where(module_model.create_time >= query.start_date)
        if query.end_date:
            statement = statement.where(module_model.create_time <= query.end_date)

        offset = (query.page - 1) * query.pageSize
        datas = session.exec(statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)).all()
        total = len(session.exec(statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById")
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试历史"""
    try:
        data = session.get(module_model, id)
        return respModel.ok_resp(obj=data) if data else respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/execute")
def execute_test(request: ApiTestExecuteRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """执行接口测试"""
    try:
        # 创建测试历史记录
        test_name = request.test_name or f"接口测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_history = module_model(
            api_info_id=request.api_info_id,
            project_id=0,
            test_name=test_name,
            test_status="running",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(test_history)
        session.commit()
        session.refresh(test_history)

        # 定义后台任务（内联函数）
        def _execute_background():
            from core.database import SessionLocal
            db = SessionLocal()
            test_hist = None
            try:
                # 1. 获取测试历史记录
                test_hist = db.get(ApiHistory, test_history.id)
                if not test_hist:
                    logger.warning(f"测试记录不存在: {test_history.id}")
                    return

                # 2. 获取接口信息
                api_info = db.get(ApiInfo, request.api_info_id)
                if not api_info:
                    test_hist.test_status = "failed"
                    test_hist.error_message = "接口信息不存在"
                    db.commit()
                    return

                # 3. 创建工作空间
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                workspace_name = f"test_{test_history.id}_{timestamp}"
                yaml_dir = YAML_DIR / workspace_name
                report_dir = REPORT_DIR / workspace_name
                log_file = LOG_DIR / f"{workspace_name}.log"
                for directory in [TEMP_DIR, YAML_DIR, REPORT_DIR, LOG_DIR, yaml_dir, report_dir]:
                    directory.mkdir(exist_ok=True)

                # 4. 生成YAML测试用例
                def _parse_json(field_value: Optional[str]) -> Optional[Dict]:
                    if not field_value:
                        return None
                    try:
                        return json.loads(field_value) if isinstance(field_value, str) else field_value
                    except (json.JSONDecodeError, TypeError):
                        return None

                def _build_request_step(api: ApiInfo) -> Dict[str, Any]:
                    step_data = {'关键字': 'send_request', 'method': api.request_method or 'GET', 'url': api.request_url or ''}
                    optional_fields = {'params': _parse_json(api.request_params), 'headers': _parse_json(api.request_headers)}
                    step_data.update({k: v for k, v in optional_fields.items() if v})
                    if api.request_method in ['POST', 'PUT', 'PATCH']:
                        body_data = _parse_json(api.request_form_datas) or _parse_json(api.request_www_form_datas)
                        if body_data:
                            step_data['data'] = body_data
                        json_data = _parse_json(api.requests_json_data)
                        if json_data:
                            step_data['json'] = json_data
                        files = _parse_json(api.request_files)
                        if files:
                            step_data['files'] = files
                    return {api.api_name or '发送请求': step_data}

                def _build_extract_step(extract_cfg: Dict[str, Any]) -> Dict[str, Any]:
                    var_name = extract_cfg.get('var_name', '')
                    step_name = extract_cfg.get('description') or f"提取_{var_name}"
                    return {step_name: {'关键字': 'ex_jsonData', 'EXVALUE': extract_cfg.get('extract_path', ''), 'VARNAME': var_name, 'INDEX': str(extract_cfg.get('index', 0))}}

                def _build_assertion_step(assert_cfg: Dict[str, Any]) -> Dict[str, Any]:
                    step_name = assert_cfg.get('description') or '断言验证'
                    assert_type = assert_cfg.get('type', 'assert_text_comparators')
                    builders = {
                        'assert_text_comparators': lambda: {'关键字': 'assert_text_comparators', 'VALUE': assert_cfg.get('actual_value', ''), 'EXPECTED': assert_cfg.get('expected_value', ''), 'OP_STR': assert_cfg.get('operator', '==')},
                        'assert_json_path': lambda: {'关键字': 'ex_jsonData', 'EXVALUE': assert_cfg.get('extract_path', ''), 'VARNAME': f"temp_{assert_cfg.get('description', 'value')}", 'INDEX': '0'}
                    }
                    return {step_name: builders.get(assert_type, builders['assert_text_comparators'])()}

                # 生成YAML内容
                test_case = {'desc': request.test_name or f'{api_info.api_name}_测试', 'steps': []}
                test_case['steps'].append(_build_request_step(api_info))
                test_case['steps'].extend([_build_extract_step(e) for e in (request.variable_extracts or [])])
                test_case['steps'].extend([_build_assertion_step(a) for a in (request.assertions or [])])
                if request.pre_script:
                    test_case['pre_script'] = request.pre_script
                if request.post_script:
                    test_case['post_script'] = request.post_script
                if request.context_vars:
                    test_case['ddts'] = [{'desc': f'{request.test_name}_数据', **request.context_vars}]
                yaml_content = yaml.dump(test_case, allow_unicode=True, default_flow_style=False, sort_keys=False)

                # 5. 写入YAML文件
                yaml_filename = f"{api_info.api_name or 'test'}_{test_history.id}.yaml"
                (yaml_dir / yaml_filename).write_text(yaml_content, encoding='utf-8')

                # 6. 执行测试
                command = ['huace-apirun', '--cases', str(yaml_dir), '--alluredir', str(report_dir)]
                exec_success = False
                exec_error = None
                exec_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    start_time = datetime.now()
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
                    stdout, stderr = process.communicate(timeout=300)
                    end_time = datetime.now()
                    exec_success = process.returncode == 0

                    # 写入日志
                    log_content = f"=== 执行命令 ===\n{' '.join(command)}\n\n=== 开始时间 ===\n{exec_start_time}\n\n=== 结束时间 ===\n{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n=== 执行时长 ===\n{(end_time - start_time).total_seconds()}秒\n\n=== 返回码 ===\n{process.returncode}\n\n=== 标准输出 ===\n{stdout}\n\n=== 错误输出 ===\n{stderr}\n"
                    log_file.write_text(log_content, encoding='utf-8')
                except subprocess.TimeoutExpired:
                    exec_error = '测试执行超时（300秒）'
                    process.kill()
                except FileNotFoundError:
                    exec_error = 'huace-apirun命令不存在，请确认api-engine已正确安装'
                except Exception as e:
                    exec_error = f'执行失败: {str(e)}'

                # 7. 解析测试结果
                response_data = None
                if exec_success:
                    try:
                        result_files = list(report_dir.glob("*-result.json"))
                        if result_files:
                            all_results = [json.loads(f.read_text(encoding='utf-8')) for f in result_files]
                            if all_results:
                                first_result = all_results[0]
                                response_data = {
                                    'status': first_result.get('status'),
                                    'status_code': None,
                                    'response_time': first_result.get('stop', 0) - first_result.get('start', 0),
                                    'response_body': None,
                                    'response_headers': None,
                                    'error_message': first_result.get('statusDetails', {}).get('message') if first_result.get('status') in ['failed', 'broken'] else None
                                }
                    except Exception as e:
                        logger.error(f"解析Allure结果失败: {e}", exc_info=True)

                # 8. 更新测试历史记录
                test_hist.test_status = "success" if exec_success else "failed"
                test_hist.request_url = api_info.request_url
                test_hist.request_method = api_info.request_method
                test_hist.request_headers = api_info.request_headers
                test_hist.request_params = api_info.request_params
                test_hist.request_body = api_info.requests_json_data or api_info.request_form_datas
                test_hist.response_time = int(response_data.get('response_time', 0)) if response_data else None
                test_hist.status_code = response_data.get('status_code') if response_data else None
                test_hist.response_headers = response_data.get('response_headers') if response_data else None
                test_hist.response_body = response_data.get('response_body') if response_data else None
                test_hist.error_message = exec_error or (response_data.get('error_message') if response_data else None)
                test_hist.allure_report_path = str(report_dir)
                test_hist.yaml_content = yaml_content
                test_hist.finish_time = datetime.now()
                test_hist.modify_time = datetime.now()
                db.commit()

                logger.info(f"测试任务执行完成: {test_history.id}, 结果: {test_hist.test_status}")

            except Exception as e:
                logger.error(f"测试任务执行失败: {test_history.id}, 错误: {e}", exc_info=True)
                if test_hist:
                    test_hist.test_status = "failed"
                    test_hist.error_message = str(e)
                    test_hist.finish_time = datetime.now()
                    test_hist.modify_time = datetime.now()
                    db.commit()
            finally:
                db.close()

        # 添加后台任务
        background_tasks.add_task(_execute_background)
        return respModel.ok_resp(dic_t={"test_id": test_history.id, "status": "running"}, msg="测试已开始执行")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/status")
def get_test_status(test_id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.delete("/delete", dependencies=[Depends(check_permission("apitest:history:delete"))])
def delete(id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.get("/queryByPlanId")
def queryByPlanId(plan_id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.get("/queryByExecutionUuid")
def queryByExecutionUuid(execution_uuid: str = Query(...), session: Session = Depends(get_session)):
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
