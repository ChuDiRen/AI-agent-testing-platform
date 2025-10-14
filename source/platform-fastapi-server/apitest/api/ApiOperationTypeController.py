from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from apitest.model.ApiOperationTypeModel import OperationType
from apitest.schemas.operation_type_schema import OperationTypeQuery, OperationTypeCreate, OperationTypeUpdate
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime

module_name = "OperationType" # 模块名称
module_model = OperationType
module_route = APIRouter(prefix=f"/{module_name}", tags=["操作类型管理"])

@module_route.get("/queryAll") # 查询所有操作类型
def queryAll(session: Session = Depends(get_session)):
    statement = select(module_model)
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")

@module_route.post("/queryByPage") # 分页查询操作类型
def queryByPage(query: OperationTypeQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        # 添加操作类型名称模糊搜索条件
        if query.operation_type_name:
            statement = statement.where(module_model.operation_type_name.like(f'%{query.operation_type_name}%'))
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        if query.operation_type_name:
            count_statement = count_statement.where(module_model.operation_type_name.like(f'%{query.operation_type_name}%'))
        total = len(session.exec(count_statement).all())
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询操作类型
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

@module_route.post("/insert") # 新增操作类型
def insert(op_type: OperationTypeCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**op_type.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update") # 更新操作类型
def update(op_type: OperationTypeUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == op_type.id)
        db_data = session.exec(statement).first()
        if db_data:
            update_data = op_type.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_data, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="操作类型不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete") # 删除操作类型
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="操作类型不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
