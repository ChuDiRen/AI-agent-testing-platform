from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from ..model.ApiInfoModel import ApiInfo
from ..schemas.api_info_schema import ApiInfoQuery, ApiInfoCreate, ApiInfoUpdate
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)

module_name = "ApiInfo" # 模块名称
module_model = ApiInfo
module_route = APIRouter(prefix=f"/{module_name}", tags=["API接口信息管理"])

@module_route.post("/queryByPage") # 分页查询API接口信息
def queryByPage(query: ApiInfoQuery, session: Session = Depends(get_session)):
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

@module_route.get("/queryById") # 根据ID查询API接口信息
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.post("/insert") # 新增API接口信息
def insert(api_info: ApiInfoCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**api_info.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update") # 更新API接口信息
def update(api_info: ApiInfoUpdate, session: Session = Depends(get_session)):
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

@module_route.delete("/delete") # 删除API接口信息
def delete(id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.get("/getByProject") # 根据项目ID获取接口列表
def getByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.project_id == project_id)
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getMethods") # 获取所有请求方法
def getMethods():
    try:
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        return respModel.ok_resp_simple(lst=methods, msg="获取成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
