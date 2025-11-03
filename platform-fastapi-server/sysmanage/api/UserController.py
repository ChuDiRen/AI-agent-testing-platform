from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger

logger = get_logger(__name__)
from ..model.user import User
from ..model.user_role import UserRole
from ..schemas.user_schema import UserQuery, UserCreate, UserUpdate, UserRoleAssign, UserStatusUpdate
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime

module_name = "user" # 模块名称
module_model = User
module_route = APIRouter(prefix=f"/{module_name}", tags=["用户管理"])

@module_route.post("/queryByPage") # 分页查询用户
def queryByPage(query: UserQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 模糊查询用户名
        if query.username:
            statement = statement.where(module_model.username.like(f"%{query.username}%"))
        
        # 按部门过滤
        if query.dept_id:
            statement = statement.where(module_model.dept_id == query.dept_id)
        
        # 按状态过滤
        if query.status:
            statement = statement.where(module_model.status == query.status)
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(module_model)
        if query.username:
            count_statement = count_statement.where(module_model.username.like(f"%{query.username}%"))
        if query.dept_id:
            count_statement = count_statement.where(module_model.dept_id == query.dept_id)
        if query.status:
            count_statement = count_statement.where(module_model.status == query.status)
        total = len(session.exec(count_statement).all())
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询用户
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
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete") # 删除用户
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            # 删除用户的角色关联
            statement = select(UserRole).where(UserRole.user_id == id)
            user_roles = session.exec(statement).all()
            for ur in user_roles:
                session.delete(ur)
            
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.post("/assignRoles") # 为用户分配角色
def assignRoles(request: UserRoleAssign, session: Session = Depends(get_session)):
    try:
        # 检查用户是否存在
        user = session.get(User, request.id)
        if not user:
            return respModel.error_resp("用户不存在")
        
        # 删除用户原有的角色
        statement = select(UserRole).where(UserRole.user_id == request.id)
        old_user_roles = session.exec(statement).all()
        for ur in old_user_roles:
            session.delete(ur)
        
        # 添加新的角色
        for role_id in request.role_ids:
            user_role = UserRole(user_id=request.id, role_id=role_id)
            session.add(user_role)
        
        session.commit()
        return respModel.ok_resp_text(msg="分配角色成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/roles/{user_id}") # 获取用户的角色
def getRoles(user_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(UserRole).where(UserRole.user_id == user_id)
        user_roles = session.exec(statement).all()
        role_ids = [ur.role_id for ur in user_roles]
        return respModel.ok_resp_simple(lst=role_ids, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/updateStatus") # 更新用户状态（锁定/启用）
def updateStatus(request: UserStatusUpdate, session: Session = Depends(get_session)):
    try:
        user = session.get(User, request.id)
        if not user:
            return respModel.error_resp("用户不存在")
        
        user.status = request.status
        user.modify_time = datetime.now()
        session.add(user)
        session.commit()
        
        status_text = "启用" if request.status == "1" else "锁定"
        return respModel.ok_resp_text(msg=f"用户{status_text}成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
