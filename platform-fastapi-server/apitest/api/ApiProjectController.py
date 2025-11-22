from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from ..model.ApiProjectModel import ApiProject
from ..schemas.api_project_schema import ApiProjectQuery, ApiProjectCreate, ApiProjectUpdate
from core.database import get_session
from core.dependencies import check_permission
from core.time_utils import TimeFormatter
from datetime import datetime
from core.logger import get_logger



module_name = "ApiProject" # 模块名称
module_model = ApiProject
module_route = APIRouter(prefix=f"/{module_name}", tags=["API项目管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", dependencies=[Depends(check_permission("apitest:project:query"))]) # 分页查询API项目
def queryByPage(query: ApiProjectQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", dependencies=[Depends(check_permission("apitest:project:query"))]) # 根据ID查询API项目
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", dependencies=[Depends(check_permission("apitest:project:add"))]) # 新增API项目
def insert(project: ApiProjectCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**project.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", dependencies=[Depends(check_permission("apitest:project:edit"))]) # 更新API项目
def update(project: ApiProjectUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == project.id)
        db_project = session.exec(statement).first()
        if db_project:
            update_data = project.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_project, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", dependencies=[Depends(check_permission("apitest:project:delete"))]) # 删除API项目
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.get("/queryAll", dependencies=[Depends(check_permission("apitest:project:query"))]) # 查询所有API项目
def queryAll(session: Session = Depends(get_session)):
    statement = select(module_model)
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")
