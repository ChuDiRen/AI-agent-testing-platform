from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from apitest.model.ApiDbBaseModel import ApiDbBase
from schemas.api_database_schema import ApiDbBaseQuery, ApiDbBaseCreate, ApiDbBaseUpdate
from core.database import get_session
from datetime import datetime

module_name = "ApiDbBase" # 模块名称
module_model = ApiDbBase
module_route = APIRouter(prefix=f"/{module_name}", tags=["API数据库配置管理"])

@module_route.post("/queryByPage") # 分页查询API数据库配置
def queryByPage(query: ApiDbBaseQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        # 添加项目筛选条件
        if query.project_id and query.project_id > 0:
            statement = statement.where(module_model.project_id == query.project_id)
        # 添加连接名模糊搜索条件
        if query.connect_name:
            statement = statement.where(module_model.name.like(f'%{query.connect_name}%'))
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        if query.project_id and query.project_id > 0:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.connect_name:
            count_statement = count_statement.where(module_model.name.like(f'%{query.connect_name}%'))
        total = len(session.exec(count_statement).all())
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询API数据库配置
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

@module_route.post("/insert") # 新增API数据库配置
def insert(db_config: ApiDbBaseCreate, session: Session = Depends(get_session)):
    try:
        # 检查引用名称是否重复
        statement = select(module_model).where(module_model.ref_name == db_config.ref_name)
        existing = session.exec(statement).first()
        if existing:
            return respModel.error_resp(msg="数据库已存在重复的数据库引用名，请重新输入")
        data = module_model(**db_config.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update") # 更新API数据库配置
def update(db_config: ApiDbBaseUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == db_config.id)
        db_data = session.exec(statement).first()
        if db_data:
            update_data = db_config.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_data, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="数据库配置不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete") # 删除API数据库配置
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="数据库配置不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")