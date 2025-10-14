from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from sysmanage.model.user import User
from sysmanage.schemas.user_schema import UserQuery, UserCreate, UserUpdate
from core.database import get_session
from datetime import datetime

module_name = "user" # 模块名称
module_model = User
module_route = APIRouter(prefix=f"/{module_name}", tags=["用户管理"])

@module_route.post("/queryByPage") # 分页查询用户
def queryByPage(query: UserQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model).limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        total = len(session.exec(count_statement).all())
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询用户
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

@module_route.post("/insert") # 新增用户
def insert(user: UserCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**user.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update") # 更新用户
def update(user: UserUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == user.id)
        db_user = session.exec(statement).first()
        if db_user:
            update_data = user.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_user, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete") # 删除用户
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
