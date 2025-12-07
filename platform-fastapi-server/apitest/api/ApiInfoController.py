from datetime import datetime

from core.SwaggerParser import SwaggerParser, fetch_swagger_from_url
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiInfoModel import ApiInfo
from ..schemas.api_info_schema import ApiInfoQuery, ApiInfoCreate, ApiInfoUpdate
from ..schemas.swagger_import_schema import SwaggerImportRequest, SwaggerImportResponse

module_name = "ApiInfo" # 模块名称
module_model = ApiInfo
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口信息管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询API接口信息", dependencies=[Depends(check_permission("apitest:api:query"))]) # 分页查询API接口信息
async def queryByPage(query: ApiInfoQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 添加筛选条件
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        if query.api_name:
            statement = statement.where(module_model.api_name.contains(query.api_name))
        if query.request_method:
            statement = statement.where(module_model.request_method == query.request_method)
            
        # 分页
        datas = session.exec(statement.limit(query.pageSize).offset(offset)).all()
        
        # 总数统计
        count_statement = select(module_model)
        if query.project_id:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.api_name:
            count_statement = count_statement.where(module_model.api_name.contains(query.api_name))
        if query.request_method:
            count_statement = count_statement.where(module_model.request_method == query.request_method)
        
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API接口信息") # 根据ID查询API接口信息
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API接口信息", dependencies=[Depends(check_permission("apitest:api:add"))]) # 新增API接口信息
async def insert(api_info: ApiInfoCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**api_info.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新API接口信息", dependencies=[Depends(check_permission("apitest:api:edit"))]) # 更新API接口信息
async def update(api_info: ApiInfoUpdate, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, api_info.id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        update_data = api_info.model_dump(exclude_unset=True, exclude={"id"})
        
        for key, value in update_data.items():
            setattr(obj, key, value)
        
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API接口信息", dependencies=[Depends(check_permission("apitest:api:delete"))]) # 删除API接口信息
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        session.delete(obj)
        session.commit()
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getByProject", summary="根据项目ID获取接口列表") # 根据项目ID获取接口列表
async def getByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.project_id == project_id)
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getMethods", summary="获取所有请求方法") # 获取所有请求方法
async def getMethods():
    try:
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        return respModel.ok_resp_simple(lst=methods, msg="获取成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/importSwagger", summary="导入Swagger/OpenAPI文档", dependencies=[Depends(check_permission("apitest:api:add"))]) # 导入Swagger
async def import_swagger(request: SwaggerImportRequest, session: Session = Depends(get_session)):
    """
    导入Swagger/OpenAPI文档
    支持OpenAPI 2.0和3.0规范
    """
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
        
        # 解析Swagger
        parser = SwaggerParser(swagger_data, source_url=source_url)
        detected_version = parser.version
        apis = parser.parse_apis()
        
        # 如果开启覆盖,先删除该项目的所有接口
        if request.override_existing:
            delete_count = session.exec(
                select(module_model).where(module_model.project_id == request.project_id)
            ).all()
            for item in delete_count:
                session.delete(item)
            session.flush()
        
        # 统计信息
        total_apis = len(apis)
        imported_apis = 0
        skipped_apis = 0
        failed_apis = 0
        details = []
        
        # 导入API
        for api in apis:
            try:
                api_name = api.get('api_name', '')
                request_method = api.get('request_method', '')
                
                # 如果没有开启覆盖,检查是否已存在
                if not request.override_existing:
                    existing = session.exec(
                        select(module_model).where(
                            module_model.project_id == request.project_id,
                            module_model.api_name == api_name,
                            module_model.request_method == request_method
                        )
                    ).first()
                    
                    if existing:
                        skipped_apis += 1
                        details.append(f"跳过已存在: {request_method} {api_name}")
                        continue
                
                # 创建新API
                new_api = module_model(
                    project_id=request.project_id,
                    create_time=datetime.now(),
                    **api
                )
                session.add(new_api)
                imported_apis += 1
                details.append(f"导入: {request_method} {api_name}")
                
            except Exception as e:
                failed_apis += 1
                details.append(f"失败: {api.get('api_name', 'unknown')} - {str(e)}")
                logger.error(f"导入API失败: {e}", exc_info=True)
        
        # 提交事务
        session.commit()
        
        # 返回结果
        result = SwaggerImportResponse(
            total_apis=total_apis,
            imported_apis=imported_apis,
            skipped_apis=skipped_apis,
            failed_apis=failed_apis,
            details=details[:100]  # 限制详情数量
        )
        
        msg = f"导入完成: 成功{imported_apis}个, 跳过{skipped_apis}个, 失败{failed_apis}个"
        return respModel.ok_resp(obj=result.model_dump(), msg=msg)
        
    except Exception as e:
        session.rollback()
        logger.error(f"导入Swagger失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败: {str(e)}")
