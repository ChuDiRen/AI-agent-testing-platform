from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from apitest.model.ApiTestHistoryModel import ApiTestHistory
from apitest.schemas.api_test_history_schema import ApiTestHistoryQuery, ApiTestHistoryCreate, ExecuteTestRequest
from core.database import get_session
from core.resp_model import respModel
from datetime import datetime
import json
import requests
import traceback

module_name = "ApiTestHistory"  # 模块名称
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试历史管理"])  # 路由对象
module_model = ApiTestHistory  # 模型对象

@module_route.post("/queryByPage")  # 分页查询测试历史
def queryByPage(query: ApiTestHistoryQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        
        # 条件筛选
        if query.api_info_id:
            statement = statement.where(module_model.api_info_id == query.api_info_id)
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.test_status:
            statement = statement.where(module_model.test_status == query.test_status)
        
        # 按创建时间倒序
        statement = statement.order_by(module_model.create_time.desc())
        
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(module_model)
        if query.api_info_id:
            count_statement = count_statement.where(module_model.api_info_id == query.api_info_id)
        if query.project_id:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.test_status:
            count_statement = count_statement.where(module_model.test_status == query.test_status)
        
        total = len(session.exec(count_statement).all())
        
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(traceback.format_exc())
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/executeTest")  # 执行API测试
def executeTest(request_data: ExecuteTestRequest, session: Session = Depends(get_session)):
    try:
        # 准备请求参数
        url = request_data.request_url
        method = request_data.request_method.upper()
        headers = {}
        
        # 解析Headers
        if request_data.request_headers:
            try:
                headers = json.loads(request_data.request_headers)
            except:
                headers = {}
        
        # 准备请求数据
        request_body = None
        if request_data.request_body:
            try:
                request_body = json.loads(request_data.request_body)
            except:
                request_body = request_data.request_body
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 执行请求
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=request_body, timeout=30)
            elif method == 'POST':
                if isinstance(request_body, dict):
                    response = requests.post(url, headers=headers, json=request_body, timeout=30)
                else:
                    response = requests.post(url, headers=headers, data=request_body, timeout=30)
            elif method == 'PUT':
                if isinstance(request_body, dict):
                    response = requests.put(url, headers=headers, json=request_body, timeout=30)
                else:
                    response = requests.put(url, headers=headers, data=request_body, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            elif method == 'PATCH':
                if isinstance(request_body, dict):
                    response = requests.patch(url, headers=headers, json=request_body, timeout=30)
                else:
                    response = requests.patch(url, headers=headers, data=request_body, timeout=30)
            else:
                return respModel.error_resp(f"不支持的请求方法: {method}")
            
            # 计算响应时间
            end_time = datetime.now()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            # 解析响应
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # 判断测试状态
            test_status = 'success' if response.status_code < 400 else 'failed'
            
            # 保存测试历史
            if request_data.api_info_id:
                history = ApiTestHistory(
                    api_info_id=request_data.api_info_id,
                    project_id=request_data.project_id or 0,
                    test_name=f"{method} {url}",
                    test_status=test_status,
                    request_data=json.dumps({
                        'url': url,
                        'method': method,
                        'headers': headers,
                        'body': request_body
                    }, ensure_ascii=False),
                    response_data=json.dumps(response_data, ensure_ascii=False) if isinstance(response_data, dict) else response_data,
                    response_time=response_time,
                    status_code=response.status_code,
                    create_time=start_time,
                    finish_time=end_time
                )
                session.add(history)
                session.commit()
            
            # 返回结果
            return respModel().ok_resp(data={
                'status': test_status,
                'status_code': response.status_code,
                'response_time': response_time,
                'response_data': response_data,
                'response_headers': dict(response.headers)
            })
            
        except requests.RequestException as e:
            # 请求失败
            end_time = datetime.now()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            error_message = str(e)
            
            # 保存失败记录
            if request_data.api_info_id:
                history = ApiTestHistory(
                    api_info_id=request_data.api_info_id,
                    project_id=request_data.project_id or 0,
                    test_name=f"{method} {url}",
                    test_status='failed',
                    request_data=json.dumps({
                        'url': url,
                        'method': method,
                        'headers': headers,
                        'body': request_body
                    }, ensure_ascii=False),
                    response_time=response_time,
                    error_message=error_message,
                    create_time=start_time,
                    finish_time=end_time
                )
                session.add(history)
                session.commit()
            
            return respModel.error_resp(f"请求失败: {error_message}")
    
    except Exception as e:
        print(traceback.format_exc())
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById")  # 根据ID查询测试历史
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        data = session.get(module_model, id)
        if data:
            return respModel().ok_resp(data=data)
        else:
            return respModel.error_resp("未找到数据")
    except Exception as e:
        print(traceback.format_exc())
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete")  # 删除测试历史
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        data = session.get(module_model, id)
        if data:
            session.delete(data)
            session.commit()
            return respModel().ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("未找到数据")
    except Exception as e:
        print(traceback.format_exc())
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

