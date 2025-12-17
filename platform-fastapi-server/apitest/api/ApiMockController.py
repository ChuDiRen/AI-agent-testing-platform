"""
Mock服务Controller
提供Mock规则的CRUD、智能生成、Mock服务等功能
"""
import json
import time
import re
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, and_
from typing import Optional

from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel
from core.logger import get_logger

from apitest.model.ApiMockModel import ApiMock, ApiMockLog
from apitest.model.ApiInfoModel import ApiInfo
from apitest.schemas.api_mock_schema import (
    ApiMockQuery,
    ApiMockCreate,
    ApiMockUpdate,
    ApiMockLogQuery,
    ApiMockGenerate,
    ApiMockFromApi
)

logger = get_logger(__name__)

module_name = "ApiMock"
module_model = ApiMock
module_route = APIRouter(prefix=f"/{module_name}", tags=["Mock服务管理"])


@module_route.post("/queryByPage", summary="分页查询Mock规则",
                   dependencies=[Depends(check_permission("apitest:mock:query"))])
async def query_by_page(query: ApiMockQuery, session: Session = Depends(get_session)):
    """分页查询Mock规则"""
    offset = (query.page - 1) * query.pageSize
    statement = select(module_model)
    
    if query.project_id:
        statement = statement.where(module_model.project_id == query.project_id)
    if query.api_id:
        statement = statement.where(module_model.api_id == query.api_id)
    if query.mock_name:
        statement = statement.where(module_model.mock_name.contains(query.mock_name))
    if query.mock_method:
        statement = statement.where(module_model.mock_method == query.mock_method)
    if query.is_enabled is not None:
        statement = statement.where(module_model.is_enabled == query.is_enabled)
    
    statement = statement.order_by(module_model.priority.desc(), module_model.id.desc())
    
    count_statement = select(module_model)
    if query.project_id:
        count_statement = count_statement.where(module_model.project_id == query.project_id)
    total = len(session.exec(count_statement).all())
    
    datas = session.exec(statement.limit(query.pageSize).offset(offset)).all()
    
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询Mock规则",
                  dependencies=[Depends(check_permission("apitest:mock:query"))])
async def query_by_id(id: int = Query(..., description="Mock ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询Mock规则详情"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="Mock规则不存在")
    return respModel.ok_resp(obj=data)


@module_route.get("/queryByApi", summary="查询接口的Mock规则",
                  dependencies=[Depends(check_permission("apitest:mock:query"))])
async def query_by_api(api_id: int = Query(..., description="接口ID"),
                       session: Session = Depends(get_session)):
    """查询接口关联的Mock规则"""
    statement = select(module_model).where(
        module_model.api_id == api_id
    ).order_by(module_model.priority.desc())
    
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.post("/insert", summary="新增Mock规则",
                   dependencies=[Depends(check_permission("apitest:mock:add"))])
async def insert(mock: ApiMockCreate, session: Session = Depends(get_session)):
    """新增Mock规则"""
    # 检查路径是否重复
    existing = session.exec(
        select(module_model).where(
            and_(
                module_model.project_id == mock.project_id,
                module_model.mock_path == mock.mock_path,
                module_model.mock_method == mock.mock_method
            )
        )
    ).first()
    
    if existing:
        return respModel.error_resp(msg=f"Mock路径 '{mock.mock_method} {mock.mock_path}' 已存在")
    
    data = module_model(
        **mock.model_dump(),
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    session.add(data)
    session.commit()
    session.refresh(data)
    
    return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})


@module_route.put("/update", summary="更新Mock规则",
                  dependencies=[Depends(check_permission("apitest:mock:edit"))])
async def update(mock: ApiMockUpdate, session: Session = Depends(get_session)):
    """更新Mock规则"""
    data = session.get(module_model, mock.id)
    if not data:
        return respModel.error_resp(msg="Mock规则不存在")
    
    # 检查路径是否重复
    if mock.mock_path or mock.mock_method:
        path = mock.mock_path or data.mock_path
        method = mock.mock_method or data.mock_method
        existing = session.exec(
            select(module_model).where(
                and_(
                    module_model.project_id == data.project_id,
                    module_model.mock_path == path,
                    module_model.mock_method == method,
                    module_model.id != mock.id
                )
            )
        ).first()
        if existing:
            return respModel.error_resp(msg=f"Mock路径 '{method} {path}' 已存在")
    
    update_data = mock.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(data, key, value)
    data.update_time = datetime.now()
    
    session.add(data)
    session.commit()
    
    return respModel.ok_resp(msg="更新成功")


@module_route.delete("/delete", summary="删除Mock规则",
                     dependencies=[Depends(check_permission("apitest:mock:delete"))])
async def delete(id: int = Query(..., description="Mock ID"),
                 session: Session = Depends(get_session)):
    """删除Mock规则"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="Mock规则不存在")
    
    session.delete(data)
    session.commit()
    
    return respModel.ok_resp(msg="删除成功")


@module_route.put("/toggleEnabled", summary="切换启用状态",
                  dependencies=[Depends(check_permission("apitest:mock:edit"))])
async def toggle_enabled(id: int = Query(..., description="Mock ID"),
                         session: Session = Depends(get_session)):
    """切换Mock规则启用状态"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="Mock规则不存在")
    
    data.is_enabled = 0 if data.is_enabled == 1 else 1
    data.update_time = datetime.now()
    session.add(data)
    session.commit()
    
    status = "启用" if data.is_enabled == 1 else "禁用"
    return respModel.ok_resp(msg=f"已{status}")


@module_route.post("/generateFromApi", summary="从接口生成Mock",
                   dependencies=[Depends(check_permission("apitest:mock:add"))])
async def generate_from_api(params: ApiMockFromApi, session: Session = Depends(get_session)):
    """从接口定义自动生成Mock规则"""
    api = session.get(ApiInfo, params.api_id)
    if not api:
        return respModel.error_resp(msg="接口不存在")
    
    mock_name = params.mock_name or f"{api.api_name} - Mock"
    mock_path = api.request_url or f"/mock/api/{api.id}"
    
    # 生成默认响应
    response_body = params.response_template
    if not response_body:
        response_body = json.dumps({
            "code": 200,
            "msg": "success",
            "data": generate_mock_data(api)
        }, ensure_ascii=False, indent=2)
    
    mock = module_model(
        project_id=api.project_id,
        api_id=api.id,
        mock_name=mock_name,
        mock_path=mock_path,
        mock_method=api.request_method or "GET",
        response_status=200,
        response_body=response_body,
        response_body_type="json",
        is_enabled=1,
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    session.add(mock)
    session.commit()
    session.refresh(mock)
    
    return respModel.ok_resp(msg="生成成功", dic_t={"id": mock.id})


@module_route.post("/queryLogs", summary="查询Mock日志",
                   dependencies=[Depends(check_permission("apitest:mock:query"))])
async def query_logs(query: ApiMockLogQuery, session: Session = Depends(get_session)):
    """查询Mock请求日志"""
    offset = (query.page - 1) * query.pageSize
    statement = select(ApiMockLog)
    
    if query.mock_id:
        statement = statement.where(ApiMockLog.mock_id == query.mock_id)
    if query.project_id:
        statement = statement.where(ApiMockLog.project_id == query.project_id)
    if query.request_method:
        statement = statement.where(ApiMockLog.request_method == query.request_method)
    if query.start_time:
        statement = statement.where(ApiMockLog.create_time >= query.start_time)
    if query.end_time:
        statement = statement.where(ApiMockLog.create_time <= query.end_time)
    
    statement = statement.order_by(ApiMockLog.create_time.desc())
    
    total = len(session.exec(statement).all())
    datas = session.exec(statement.limit(query.pageSize).offset(offset)).all()
    
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.delete("/clearLogs", summary="清空Mock日志",
                     dependencies=[Depends(check_permission("apitest:mock:delete"))])
async def clear_logs(project_id: int = Query(..., description="项目ID"),
                     days: int = Query(7, description="保留天数"),
                     session: Session = Depends(get_session)):
    """清空Mock日志"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    statement = select(ApiMockLog).where(
        and_(
            ApiMockLog.project_id == project_id,
            ApiMockLog.create_time < cutoff_date
        )
    )
    logs = session.exec(statement).all()
    deleted_count = len(logs)
    
    for log in logs:
        session.delete(log)
    session.commit()
    
    return respModel.ok_resp(msg=f"已清空 {deleted_count} 条日志")


@module_route.get("/getMockUrl", summary="获取Mock URL",
                  dependencies=[Depends(check_permission("apitest:mock:query"))])
async def get_mock_url(id: int = Query(..., description="Mock ID"),
                       session: Session = Depends(get_session)):
    """获取Mock的完整URL"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="Mock规则不存在")
    
    # 构建Mock URL
    mock_url = f"/mock/{data.project_id}{data.mock_path}"
    
    return respModel.ok_resp(dic_t={
        "mock_url": mock_url,
        "method": data.mock_method,
        "full_url": f"http://localhost:5000{mock_url}"
    })


def generate_mock_data(api: ApiInfo) -> dict:
    """根据接口定义生成Mock数据"""
    # 简单的Mock数据生成
    return {
        "id": 1,
        "name": "mock_data",
        "created_at": datetime.now().isoformat()
    }


# Mock服务路由 - 处理实际的Mock请求
mock_service_route = APIRouter(prefix="/mock", tags=["Mock服务"])


@mock_service_route.api_route("/{project_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_mock_request(
    request: Request,
    project_id: int,
    path: str,
    session: Session = Depends(get_session)
):
    """处理Mock请求"""
    start_time = time.time()
    method = request.method
    full_path = f"/{path}"
    
    # 查找匹配的Mock规则
    statement = select(ApiMock).where(
        and_(
            ApiMock.project_id == project_id,
            ApiMock.mock_method == method,
            ApiMock.is_enabled == 1
        )
    ).order_by(ApiMock.priority.desc())
    
    mocks = session.exec(statement).all()
    
    matched_mock = None
    for mock in mocks:
        if match_path(mock.mock_path, full_path):
            matched_mock = mock
            break
    
    if not matched_mock:
        return JSONResponse(
            status_code=404,
            content={"code": 404, "msg": f"No mock found for {method} {full_path}"}
        )
    
    # 延迟响应
    if matched_mock.delay_ms > 0:
        time.sleep(matched_mock.delay_ms / 1000)
    
    # 构建响应
    response_headers = {}
    if matched_mock.response_headers:
        try:
            response_headers = json.loads(matched_mock.response_headers)
        except:
            pass
    
    # 设置Content-Type
    content_type_map = {
        "json": "application/json",
        "xml": "application/xml",
        "text": "text/plain",
        "html": "text/html"
    }
    content_type = content_type_map.get(matched_mock.response_body_type, "application/json")
    response_headers["Content-Type"] = content_type
    
    # 记录日志
    response_time = int((time.time() - start_time) * 1000)
    try:
        request_body = await request.body()
        log = ApiMockLog(
            mock_id=matched_mock.id,
            project_id=project_id,
            request_method=method,
            request_path=full_path,
            request_headers=json.dumps(dict(request.headers)),
            request_body=request_body.decode() if request_body else None,
            response_status=matched_mock.response_status,
            response_body=matched_mock.response_body,
            response_time=response_time,
            client_ip=request.client.host if request.client else None,
            create_time=datetime.now()
        )
        session.add(log)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to log mock request: {e}")
    
    return Response(
        content=matched_mock.response_body or "",
        status_code=matched_mock.response_status,
        headers=response_headers
    )


def match_path(pattern: str, path: str) -> bool:
    """匹配路径，支持通配符"""
    # 简单匹配
    if pattern == path:
        return True
    
    # 支持 * 通配符
    if "*" in pattern:
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", path))
    
    # 支持路径参数 {id}
    if "{" in pattern:
        regex_pattern = re.sub(r"\{[^}]+\}", r"[^/]+", pattern)
        return bool(re.match(f"^{regex_pattern}$", path))
    
    return False
