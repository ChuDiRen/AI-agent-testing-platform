from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session, select
from core.resp_model import respModel
from apitest.model.ApiTestHistoryModel import ApiTestHistory
from apitest.model.ApiInfoModel import ApiInfo
from apitest.schemas.api_test_schema import ApiTestHistoryQuery, ApiTestExecuteRequest, ApiTestResult
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml
import json
import shutil

# ==================== 文件管理相关配置和函数 ====================

# 基础路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
YAML_DIR = TEMP_DIR / "yaml_cases"
REPORT_DIR = TEMP_DIR / "allure_reports"
LOG_DIR = TEMP_DIR / "logs"

def init_directories():
    """初始化必要的目录"""
    TEMP_DIR.mkdir(exist_ok=True)
    YAML_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

def create_test_workspace(test_id: int) -> tuple:
    """
    创建测试工作空间
    
    Args:
        test_id: 测试ID
        
    Returns:
        (yaml_dir, report_dir, log_file)元组
    """
    init_directories()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    workspace_name = f"test_{test_id}_{timestamp}"
    
    # 创建YAML用例目录
    yaml_dir = YAML_DIR / workspace_name
    yaml_dir.mkdir(exist_ok=True)
    
    # 创建报告目录
    report_dir = REPORT_DIR / workspace_name
    report_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = LOG_DIR / f"{workspace_name}.log"
    
    return yaml_dir, report_dir, log_file

def write_yaml_file(yaml_dir: Path, filename: str, content: str) -> Path:
    """
    写入YAML文件
    
    Args:
        yaml_dir: YAML目录
        filename: 文件名
        content: YAML内容
        
    Returns:
        文件路径
    """
    file_path = yaml_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path

# ==================== YAML生成相关函数 ====================

def generate_yaml(
    api_info: ApiInfo,
    test_name: str,
    context_vars: Optional[Dict[str, Any]] = None,
    pre_script: Optional[List[str]] = None,
    post_script: Optional[List[str]] = None,
    variable_extracts: Optional[List[Dict]] = None,
    assertions: Optional[List[Dict]] = None
) -> str:
    """
    生成YAML测试用例
    
    Args:
        api_info: 接口信息对象
        test_name: 测试用例名称
        context_vars: 上下文变量字典
        pre_script: 前置脚本列表
        post_script: 后置脚本列表
        variable_extracts: 变量提取配置列表
        assertions: 断言配置列表
        
    Returns:
        YAML格式的测试用例字符串
    """
    # 构建测试用例结构
    test_case = {
        'desc': test_name or f'{api_info.api_name}_测试',
        'steps': []
    }
    
    # 构建主请求步骤
    request_step = build_request_step(api_info, context_vars)
    test_case['steps'].append(request_step)
    
    # 添加变量提取步骤
    if variable_extracts:
        for extract in variable_extracts:
            extract_step = build_extract_step(extract)
            test_case['steps'].append(extract_step)
    
    # 添加断言步骤
    if assertions:
        for assertion in assertions:
            assert_step = build_assertion_step(assertion)
            test_case['steps'].append(assert_step)
    
    # 添加前置脚本
    if pre_script and len(pre_script) > 0:
        test_case['pre_script'] = pre_script
    
    # 添加后置脚本
    if post_script and len(post_script) > 0:
        test_case['post_script'] = post_script
    
    # 添加数据驱动（如果需要）
    if context_vars:
        test_case['ddts'] = [{
            'desc': f'{test_name}_数据',
            **context_vars
        }]
    
    # 转换为YAML格式
    yaml_content = yaml.dump(test_case, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return yaml_content

def build_request_step(api_info: ApiInfo, context_vars: Optional[Dict[str, Any]] = None) -> Dict:
    """构建请求步骤"""
    step_name = api_info.api_name or '发送请求'
    step_data = {
        '关键字': 'send_request',
        'method': api_info.request_method or 'GET',
        'url': api_info.request_url or ''
    }
    
    # 添加URL参数
    if api_info.request_params:
        try:
            params = json.loads(api_info.request_params) if isinstance(api_info.request_params, str) else api_info.request_params
            step_data['params'] = params
        except:
            pass
    
    # 添加请求头
    if api_info.request_headers:
        try:
            headers = json.loads(api_info.request_headers) if isinstance(api_info.request_headers, str) else api_info.request_headers
            step_data['headers'] = headers
        except:
            pass
    
    # 根据请求方法添加请求体
    if api_info.request_method in ['POST', 'PUT', 'PATCH']:
        # form-data
        if api_info.request_form_datas:
            try:
                form_data = json.loads(api_info.request_form_datas) if isinstance(api_info.request_form_datas, str) else api_info.request_form_datas
                step_data['data'] = form_data
            except:
                pass
        
        # x-www-form-urlencoded
        elif api_info.request_www_form_datas:
            try:
                www_form_data = json.loads(api_info.request_www_form_datas) if isinstance(api_info.request_www_form_datas, str) else api_info.request_www_form_datas
                step_data['data'] = www_form_data
            except:
                pass
        
        # json数据
        elif api_info.requests_json_data:
            try:
                json_data = json.loads(api_info.requests_json_data) if isinstance(api_info.requests_json_data, str) else api_info.requests_json_data
                step_data['json'] = json_data
            except:
                pass
        
        # 文件上传
        if api_info.request_files:
            try:
                files = json.loads(api_info.request_files) if isinstance(api_info.request_files, str) else api_info.request_files
                step_data['files'] = files
            except:
                pass
    
    return {step_name: step_data}

def build_extract_step(extract_config: Dict) -> Dict:
    """构建变量提取步骤"""
    step_name = extract_config.get('description') or f"提取_{extract_config.get('var_name')}"
    step_data = {
        '关键字': 'ex_jsonData',
        'EXVALUE': extract_config.get('extract_path', ''),
        'VARNAME': extract_config.get('var_name', ''),
        'INDEX': str(extract_config.get('index', 0))
    }
    return {step_name: step_data}

def build_assertion_step(assertion_config: Dict) -> Dict:
    """构建断言步骤"""
    step_name = assertion_config.get('description') or '断言验证'
    
    # 根据断言类型构建不同的步骤
    assert_type = assertion_config.get('type', 'assert_text_comparators')
    
    if assert_type == 'assert_text_comparators':
        # 文本比较断言
        step_data = {
            '关键字': 'assert_text_comparators',
            'VALUE': assertion_config.get('actual_value', ''),
            'EXPECTED': assertion_config.get('expected_value', ''),
            'OP_STR': assertion_config.get('operator', '==')
        }
    elif assert_type == 'assert_json_path':
        # JSONPath断言
        step_data = {
            '关键字': 'ex_jsonData',
            'EXVALUE': assertion_config.get('extract_path', ''),
            'VARNAME': f"temp_{assertion_config.get('description', 'value')}",
            'INDEX': '0'
        }
    else:
        # 默认文本比较
        step_data = {
            '关键字': 'assert_text_comparators',
            'VALUE': assertion_config.get('actual_value', ''),
            'EXPECTED': assertion_config.get('expected_value', ''),
            'OP_STR': '=='
        }
    
    return {step_name: step_data}

# ==================== API测试引擎执行相关函数 ====================

def execute_api_test(
    yaml_dir: Path,
    report_dir: Path,
    log_file: Path,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    执行API测试
    
    Args:
        yaml_dir: YAML用例目录
        report_dir: Allure报告目录
        log_file: 日志文件
        timeout: 超时时间（秒）
        
    Returns:
        执行结果字典
    """
    # 构建命令
    command = [
        'huace-apirun',
        '--cases', str(yaml_dir),
        '--alluredir', str(report_dir)
    ]
    
    # 执行结果
    result = {
        'success': False,
        'return_code': -1,
        'stdout': '',
        'stderr': '',
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': None,
        'duration': 0,
        'error_message': None
    }
    
    try:
        # 执行命令
        start_time = datetime.now()
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 等待执行完成
        stdout, stderr = process.communicate(timeout=timeout)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 更新结果
        result['return_code'] = process.returncode
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
        result['duration'] = duration
        result['success'] = process.returncode == 0
        
        # 写入日志文件
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== 执行命令 ===\n")
            f.write(' '.join(command) + '\n\n')
            f.write(f"=== 开始时间 ===\n{result['start_time']}\n\n")
            f.write(f"=== 结束时间 ===\n{result['end_time']}\n\n")
            f.write(f"=== 执行时长 ===\n{duration}秒\n\n")
            f.write(f"=== 返回码 ===\n{process.returncode}\n\n")
            f.write(f"=== 标准输出 ===\n{stdout}\n\n")
            f.write(f"=== 错误输出 ===\n{stderr}\n")
        
    except subprocess.TimeoutExpired:
        result['error_message'] = f'测试执行超时（{timeout}秒）'
        if process:
            process.kill()
    except FileNotFoundError:
        result['error_message'] = 'huace-apirun命令不存在，请确认api-engine已正确安装'
    except Exception as e:
        result['error_message'] = f'执行失败: {str(e)}'
    
    return result

def parse_allure_results(report_dir: Path) -> Optional[Dict[str, Any]]:
    """
    解析Allure测试结果
    
    Args:
        report_dir: Allure报告目录
        
    Returns:
        解析后的测试结果，如果失败返回None
    """
    try:
        # 查找result.json或其他allure结果文件
        result_files = list(report_dir.glob("*-result.json"))
        
        if not result_files:
            return None
        
        # 解析所有结果文件
        all_results = []
        for result_file in result_files:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_results.append(data)
        
        # 汇总统计信息
        total = len(all_results)
        passed = sum(1 for r in all_results if r.get('status') == 'passed')
        failed = sum(1 for r in all_results if r.get('status') == 'failed')
        broken = sum(1 for r in all_results if r.get('status') == 'broken')
        skipped = sum(1 for r in all_results if r.get('status') == 'skipped')
        
        summary = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'broken': broken,
            'skipped': skipped,
            'pass_rate': round(passed / total * 100, 2) if total > 0 else 0,
            'results': all_results
        }
        
        return summary
        
    except Exception as e:
        print(f"解析Allure结果失败: {e}")
        return None

def extract_response_data(allure_results: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    从Allure结果中提取响应数据
    
    Args:
        allure_results: Allure解析结果
        
    Returns:
        提取的响应数据，包含状态码、响应时间、响应体等
    """
    if not allure_results or 'results' not in allure_results:
        return None
    
    results = allure_results['results']
    if not results:
        return None
    
    # 取第一个结果（通常一个YAML只有一个测试用例）
    first_result = results[0]
    
    # 提取响应数据
    response_data = {
        'status': first_result.get('status'),
        'status_code': None,
        'response_time': first_result.get('stop', 0) - first_result.get('start', 0),
        'response_body': None,
        'response_headers': None,
        'error_message': None
    }
    
    # 尝试从attachments中提取响应信息
    attachments = first_result.get('attachments', [])
    for attachment in attachments:
        if 'response' in attachment.get('name', '').lower():
            # 这里需要根据实际的attachment结构来解析
            # 暂时保留占位逻辑
            pass
    
    # 如果失败，提取错误信息
    if first_result.get('status') in ['failed', 'broken']:
        status_details = first_result.get('statusDetails', {})
        response_data['error_message'] = status_details.get('message', '未知错误')
    
    return response_data

# ==================== 路由定义 ====================

module_name = "ApiTest" # 模块名称
module_model = ApiTestHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口测试管理"])

# ==================== 路由处理函数 ====================

@module_route.post("/queryByPage") # 分页查询测试历史
def queryByPage(query: ApiTestHistoryQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 添加筛选条件
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
            
        # 按创建时间倒序
        statement = statement.order_by(module_model.create_time.desc())
        
        # 分页
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(module_model)
        if query.api_info_id:
            count_statement = count_statement.where(module_model.api_info_id == query.api_info_id)
        if query.project_id:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.test_status:
            count_statement = count_statement.where(module_model.test_status == query.test_status)
        if query.start_date:
            count_statement = count_statement.where(module_model.create_time >= query.start_date)
        if query.end_date:
            count_statement = count_statement.where(module_model.create_time <= query.end_date)
        total = len(session.exec(count_statement).all())
        
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel().error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询测试历史
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel().ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel().error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/execute") # 执行接口测试
def execute_test(request: ApiTestExecuteRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    try:
        # 创建测试历史记录
        test_name = request.test_name or f"接口测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_history = ApiTestHistory(
            api_info_id=request.api_info_id,
            project_id=0,  # 需要从api_info中获取project_id
            test_name=test_name,
            test_status="running",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        session.add(test_history)
        session.commit()
        session.refresh(test_history)
        
        # 添加后台任务执行测试
        background_tasks.add_task(execute_test_background, test_history.id, request)
        
        return respModel().ok_resp(
            dic_t={"test_id": test_history.id, "status": "running"}, 
            msg="测试已开始执行"
        )
    except Exception as e:
        session.rollback()
        print(e)
        return respModel().error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/status") # 查询测试状态
def get_test_status(test_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        test_history = session.get(module_model, test_id)
        if not test_history:
            return respModel().error_resp("测试记录不存在")
        
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
        
        return respModel().ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel().error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete") # 删除测试历史
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel().error_resp("数据不存在")
        
        session.delete(obj)
        session.commit()
        return respModel().ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel().error_resp(f"服务器错误,请联系管理员:{e}")

# ==================== 后台任务函数 ====================

def execute_test_background(test_id: int, request: ApiTestExecuteRequest):
    """后台执行测试任务"""
    from core.database import SessionLocal
    
    db = SessionLocal()
    test_history = None
    
    try:
        # 1. 获取测试历史记录
        test_history = db.get(ApiTestHistory, test_id)
        if not test_history:
            print(f"测试记录不存在: {test_id}")
            return
        
        # 2. 获取接口信息
        api_info = db.get(ApiInfo, request.api_info_id)
        if not api_info:
            test_history.test_status = "failed"
            test_history.error_message = "接口信息不存在"
            db.commit()
            return
        
        # 3. 创建测试工作空间
        yaml_dir, report_dir, log_file = create_test_workspace(test_id)
        
        # 4. 生成YAML测试用例
        yaml_content = generate_yaml(
            api_info=api_info,
            test_name=request.test_name,
            context_vars=request.context_vars,
            pre_script=request.pre_script,
            post_script=request.post_script,
            variable_extracts=request.variable_extracts,
            assertions=request.assertions
        )
        
        # 5. 写入YAML文件
        yaml_filename = f"{api_info.api_name or 'test'}_{test_id}.yaml"
        write_yaml_file(yaml_dir, yaml_filename, yaml_content)
        
        # 6. 执行测试
        execution_result = execute_api_test(
            yaml_dir=yaml_dir,
            report_dir=report_dir,
            log_file=log_file,
            timeout=300
        )
        
        # 7. 解析测试结果
        allure_results = None
        if execution_result['success']:
            allure_results = parse_allure_results(report_dir)
        
        # 8. 提取响应数据
        response_data = None
        if allure_results:
            response_data = extract_response_data(allure_results)
        
        # 9. 更新测试历史记录
        test_history.test_status = "success" if execution_result['success'] else "failed"
        test_history.request_url = api_info.request_url
        test_history.request_method = api_info.request_method
        test_history.request_headers = api_info.request_headers
        test_history.request_params = api_info.request_params
        test_history.request_body = api_info.requests_json_data or api_info.request_form_datas
        test_history.response_time = int(response_data.get('response_time', 0)) if response_data else None
        test_history.status_code = response_data.get('status_code') if response_data else None
        test_history.response_headers = response_data.get('response_headers') if response_data else None
        test_history.response_body = response_data.get('response_body') if response_data else None
        test_history.error_message = execution_result.get('error_message') or (response_data.get('error_message') if response_data else None)
        test_history.allure_report_path = str(report_dir)
        test_history.yaml_content = yaml_content
        test_history.finish_time = datetime.now()
        test_history.modify_time = datetime.now()
        
        db.commit()
        
        print(f"测试任务执行完成: {test_id}, 结果: {test_history.test_status}")
        
    except Exception as e:
        print(f"测试任务执行失败: {test_id}, 错误: {e}")
        if test_history:
            test_history.test_status = "failed"
            test_history.error_message = str(e)
            test_history.finish_time = datetime.now()
            test_history.modify_time = datetime.now()
            db.commit()
    finally:
        db.close()
