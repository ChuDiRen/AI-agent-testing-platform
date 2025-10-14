from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session, select
from core.resp_model import respModel
from apitest.model.ApiTestHistoryModel import ApiTestHistory
from apitest.model.ApiInfoModel import ApiInfo
from apitest.schemas.api_test_schema import ApiTestHistoryQuery, ApiTestExecuteRequest, ApiTestResult
from core.database import get_session
from core.time_utils import TimeFormatter
from apitest.service.YamlGeneratorService import YamlGeneratorService
from apitest.service.FileManagerService import FileManagerService
from apitest.service.ApiEngineService import ApiEngineService
from apitest.service.TestResultService import TestResultService
from datetime import datetime

module_name = "ApiTest" # 模块名称
module_model = ApiTestHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口测试管理"])

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
        datas = session.exec(statement.limit(query.pageSize).offset(offset)).all()
        
        # 总数统计
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
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询测试历史
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel().ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

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
            create_time=datetime.now()
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
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

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
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

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
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

# 后台执行测试的函数
def execute_test_background(test_id: int, request: ApiTestExecuteRequest):
    """后台执行测试任务"""
    from core.database import SessionLocal
    
    db = SessionLocal()
    
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
        yaml_dir, report_dir, log_file = FileManagerService.create_test_workspace(test_id)
        
        # 4. 生成YAML测试用例
        yaml_content = YamlGeneratorService.generate_yaml(
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
        FileManagerService.write_yaml_file(yaml_dir, yaml_filename, yaml_content)
        
        # 6. 执行测试
        execution_result = ApiEngineService.execute_test(
            yaml_dir=yaml_dir,
            report_dir=report_dir,
            log_file=log_file,
            timeout=300
        )
        
        # 7. 解析测试结果
        allure_results = None
        if execution_result['success']:
            allure_results = ApiEngineService.parse_allure_results(report_dir)
        
        # 8. 提取响应数据
        response_data = None
        if allure_results:
            response_data = ApiEngineService.extract_response_data(allure_results)
        
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
            db.commit()
    finally:
        db.close()
