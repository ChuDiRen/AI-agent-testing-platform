"""
接口信息Controller - 已重构为使用Service层
"""
from datetime import datetime

from apitest.service.ApiInfoService import InfoService
from core.SwaggerParser import SwaggerParser, fetch_swagger_from_url
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..model.ApiInfoModel import ApiInfo
from ..schemas.ApiInfoSchema import ApiInfoQuery, ApiInfoCreate, ApiInfoUpdate, ApiDebugRequest
from ..schemas.SwaggerImportSchema import SwaggerImportRequest, SwaggerImportResponse

module_name = "ApiInfo"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口信息管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询API接口信息", dependencies=[Depends(check_permission("apitest:api:query"))])
async def queryByPage(query: ApiInfoQuery, session: Session = Depends(get_session)):
    try:
        datas, total = InfoService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API接口信息")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        data = InfoService.query_by_id(session, id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API接口信息", dependencies=[Depends(check_permission("apitest:api:add"))])
async def insert(api_info: ApiInfoCreate, session: Session = Depends(get_session)):
    try:
        data = InfoService.create(session, api_info)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新API接口信息", dependencies=[Depends(check_permission("apitest:api:edit"))])
async def update(api_info: ApiInfoUpdate, session: Session = Depends(get_session)):
    try:
        updated = InfoService.update(session, api_info)
        if not updated:
            return respModel.error_resp("数据不存在")
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API接口信息", dependencies=[Depends(check_permission("apitest:api:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        if not InfoService.delete(session, id):
            return respModel.error_resp("数据不存在")
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/batchDelete", summary="批量删除API接口信息", dependencies=[Depends(check_permission("apitest:api:delete"))])
async def batchDelete(request: dict, session: Session = Depends(get_session)):
    try:
        ids = request.get("ids", [])
        if not ids:
            return respModel.error_resp("请提供要删除的ID列表")
        
        success_count = 0
        error_count = 0
        
        for id in ids:
            if InfoService.delete(session, id):
                success_count += 1
            else:
                error_count += 1
        
        if error_count == 0:
            return respModel.ok_resp_text(msg=f"批量删除成功，共删除{success_count}条数据")
        else:
            return respModel.ok_resp_text(msg=f"批量删除完成，成功{success_count}条，失败{error_count}条")
    except Exception as e:
        logger.error(f"批量删除失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getByProject", summary="根据项目ID获取接口列表")
async def getByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        datas = InfoService.query_by_project(session, project_id)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getMethods", summary="获取所有请求方法")
async def getMethods():
    try:
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        return respModel.ok_resp_simple(lst=methods, msg="获取成功")
    except Exception as e:
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/search", summary="搜索接口")
async def search(keyword: str = Query(...), project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        datas = InfoService.search(session, keyword, project_id)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getStatistics", summary="获取接口统计信息")
async def getStatistics(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        stats = InfoService.get_statistics(session, project_id)
        return respModel.ok_resp(obj=stats)
    except Exception as e:
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/importSwagger", summary="导入Swagger/OpenAPI文档", dependencies=[Depends(check_permission("apitest:api:add"))])
async def import_swagger(request: SwaggerImportRequest, session: Session = Depends(get_session)):
    try:
        # 获取Swagger数据
        source_url = None
        if request.swagger_url:
            swagger_data = await fetch_swagger_from_url(request.swagger_url)
            source_url = request.swagger_url
        elif request.swagger_json:
            swagger_data = request.swagger_json
        else:
            return respModel.error_resp("请提供swagger_url或swagger_json")

        # 解析Swagger文档
        parser = SwaggerParser(swagger_data, source_url)
        apis = parser.parse_apis()

        # 导入统计
        total_apis = len(apis)
        imported_apis = 0
        skipped_apis = 0
        failed_apis = 0
        details = []

        # 逐个导入接口
        for api in apis:
            try:
                # 检查是否已存在（根据URL和方法判断）
                existing = InfoService.find_by_url_method(
                    session,
                    project_id=request.project_id,
                    url=api.get('url', ''),
                    method=api.get('method', '')
                )

                if existing and not request.overwrite:
                    skipped_apis += 1
                    details.append({
                        "api_name": api.get('name', ''),
                        "status": "skipped",
                        "reason": "已存在"
                    })
                    continue

                # 创建或更新接口
                api_create_data = {
                    'project_id': request.project_id,
                    'api_name': api.get('name', ''),
                    'request_method': api.get('method', 'GET'),
                    'request_url': api.get('url', ''),
                }
                
                # 添加解析的参数数据
                api_create_data.update({
                    'request_params': api.get('request_params'),
                    'request_headers': api.get('request_headers'),
                    'request_form_datas': api.get('request_form_datas'),
                    'requests_json_data': api.get('requests_json_data'),
                    'request_www_form_datas': api.get('request_www_form_datas'),
                })

                if existing:
                    # 更新接口
                    api_create_data['id'] = existing.id
                    api_update = ApiInfoUpdate(**api_create_data)
                    if InfoService.update(session, api_update):
                        imported_apis += 1
                        details.append({
                            "api_name": api.get('name', ''),
                            "status": "updated",
                            "reason": "更新成功"
                        })
                    else:
                        failed_apis += 1
                        details.append({
                            "api_name": api.get('name', ''),
                            "status": "failed",
                            "reason": "更新失败"
                        })
                else:
                    # 新增接口
                    api_create = ApiInfoCreate(**api_create_data)
                    data = InfoService.create(session, api_create)
                    if data:
                        imported_apis += 1
                        details.append({
                            "api_name": api.get('name', ''),
                            "status": "imported",
                            "reason": "导入成功"
                        })
                    else:
                        failed_apis += 1
                        details.append({
                            "api_name": api.get('name', ''),
                            "status": "failed",
                            "reason": "导入失败"
                        })

            except Exception as e:
                failed_apis += 1
                details.append({
                    "api_name": api.get('name', ''),
                    "status": "failed",
                    "reason": str(e)
                })
                logger.error(f"导入API失败 {api.get('name', '')}: {e}")

        # 返回结果
        result = SwaggerImportResponse(
            total_apis=total_apis,
            imported_apis=imported_apis,
            skipped_apis=skipped_apis,
            failed_apis=failed_apis,
            details=details[:100]  # 限制返回前100条详情
        )
        
        logger.info(f"Swagger导入完成 - 总计:{total_apis}, 成功:{imported_apis}, 跳过:{skipped_apis}, 失败:{failed_apis}")
        return respModel.ok_resp(obj=result)

    except Exception as e:
        session.rollback()
        logger.error(f"导入Swagger失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败: {str(e)}")

@module_route.post("/debug", summary="接口调试", dependencies=[Depends(check_permission("apitest:api:debug"))])
async def debug(request: ApiDebugRequest):
    """
    接口调试功能
    支持多种请求方式：GET、POST、PUT、DELETE、PATCH、HEAD、OPTIONS
    支持多种请求体格式：form-data、x-www-form-urlencoded、JSON、文件上传
    支持变量定义和引用
    """
    import httpx
    import time

    try:
        # 1. 处理调试变量替换
        def replace_vars(text, vars_list):
            if not text or not vars_list:
                return text
            for var in vars_list:
                key = var.get('key', '')
                value = var.get('value', '')
                if key:
                    # 支持 {{var}} 和 ${var} 两种格式
                    text = text.replace(f'{{{{{key}}}}}', str(value))
                    text = text.replace(f'${{{key}}}', str(value))
            return text
        
        # 2. 构建请求URL
        url = request.request_url
        if request.debug_vars:
            url = replace_vars(url, request.debug_vars)
        
        # 3. 处理URL参数
        params = {}
        if request.request_params:
            for param in request.request_params:
                key = param.get('key', '')
                value = param.get('value', '')
                if key:
                    if request.debug_vars:
                        value = replace_vars(str(value), request.debug_vars)
                    params[key] = value
        
        # 4. 处理请求头
        headers = {}
        if request.request_headers:
            for header in request.request_headers:
                key = header.get('key', '')
                value = header.get('value', '')
                if key:
                    if request.debug_vars:
                        value = replace_vars(str(value), request.debug_vars)
                    headers[key] = value
        
        # 5. 处理请求体
        data = None
        json_data = None
        files = None
        actual_body = None
        
        if request.request_method.upper() in ['POST', 'PUT', 'PATCH']:
            # JSON请求体
            if request.requests_json_data:
                import json
                json_str = request.requests_json_data
                if request.debug_vars:
                    json_str = replace_vars(json_str, request.debug_vars)
                try:
                    json_data = json.loads(json_str)
                    actual_body = json_str
                except json.JSONDecodeError:
                    return respModel.error_resp("JSON格式错误")
            
            # form-data
            elif request.request_form_datas:
                data = {}
                for item in request.request_form_datas:
                    key = item.get('key', '')
                    value = item.get('value', '')
                    if key:
                        if request.debug_vars:
                            value = replace_vars(str(value), request.debug_vars)
                        data[key] = value
                actual_body = str(data)
            
            # x-www-form-urlencoded
            elif request.request_www_form_datas:
                data = {}
                for item in request.request_www_form_datas:
                    key = item.get('key', '')
                    value = item.get('value', '')
                    if key:
                        if request.debug_vars:
                            value = replace_vars(str(value), request.debug_vars)
                        data[key] = value
                actual_body = str(data)
        
        # 6. 发送请求
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=request.timeout, verify=False) as client:
            response = await client.request(
                method=request.request_method.upper(),
                url=url,
                params=params if params else None,
                headers=headers if headers else None,
                data=data,
                json=json_data
            )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 7. 处理响应
        try:
            response_body = response.text
        except:
            response_body = str(response.content)
        
        result = {
            "success": True,
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "response_headers": dict(response.headers),
            "response_body": response_body,
            "request_url": str(response.url),
            "request_method": request.request_method.upper(),
            "request_headers": headers,
            "request_body": actual_body
        }
        
        return respModel.ok_resp(obj=result, msg="请求成功")
        
    except httpx.TimeoutException:
        return respModel.ok_resp(obj={
            "success": False,
            "error_message": f"请求超时（{request.timeout}秒）",
            "request_url": request.request_url,
            "request_method": request.request_method.upper()
        }, msg="请求超时")
    except httpx.ConnectError as e:
        return respModel.ok_resp(obj={
            "success": False,
            "error_message": f"连接失败: {str(e)}",
            "request_url": request.request_url,
            "request_method": request.request_method.upper()
        }, msg="连接失败")
    except Exception as e:
        logger.error(f"接口调试失败: {e}", exc_info=True)
        return respModel.ok_resp(obj={
            "success": False,
            "error_message": str(e),
            "request_url": request.request_url,
            "request_method": request.request_method.upper()
        }, msg=f"请求失败: {str(e)}")

@module_route.post("/debugAndDownload", summary="发送请求并下载响应", dependencies=[Depends(check_permission("apitest:api:debug"))])
async def debugAndDownload(request: ApiDebugRequest):
    """
    发送请求并下载响应文件
    用于下载文件类型的响应
    """
    import httpx
    import time
    import base64
    
    try:
        # 构建请求（复用debug逻辑）
        url = request.request_url
        
        # 处理URL参数
        params = {}
        if request.request_params:
            for param in request.request_params:
                key = param.get('key', '')
                value = param.get('value', '')
                if key:
                    params[key] = value
        
        # 处理请求头
        headers = {}
        if request.request_headers:
            for header in request.request_headers:
                key = header.get('key', '')
                value = header.get('value', '')
                if key:
                    headers[key] = value
        
        # 发送请求
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=request.timeout, verify=False) as client:
            response = await client.request(
                method=request.request_method.upper(),
                url=url,
                params=params if params else None,
                headers=headers if headers else None
            )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # 获取文件名
        content_disposition = response.headers.get('content-disposition', '')
        filename = 'download'
        if 'filename=' in content_disposition:
            import re
            match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
            if match:
                filename = match.group(1).strip('"\'')
        
        # 返回文件内容（base64编码）
        result = {
            "success": True,
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "response_headers": dict(response.headers),
            "filename": filename,
            "content_type": response.headers.get('content-type', ''),
            "file_content": base64.b64encode(response.content).decode('utf-8'),
            "file_size": len(response.content)
        }
        
        return respModel.ok_resp(obj=result, msg="下载成功")
        
    except Exception as e:
        logger.error(f"下载失败: {e}", exc_info=True)
        return respModel.error_resp(f"下载失败: {str(e)}")
