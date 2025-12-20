"""
环境管理Controller
提供环境的CRUD、切换、复制等功能
"""
from apitest.schemas.api_environment_schema import (
    ApiEnvironmentQuery,
    ApiEnvironmentCreate,
    ApiEnvironmentUpdate,
    ApiEnvironmentCopy
)
from apitest.service.api_environment_service import ApiEnvironmentService
from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

module_name = "ApiEnvironment"
module_route = APIRouter(prefix=f"/{module_name}", tags=["环境管理"])


@module_route.post("/queryByPage", summary="分页查询环境列表",
                   dependencies=[Depends(check_permission("apitest:environment:query"))])
async def query_by_page(query: ApiEnvironmentQuery, session: Session = Depends(get_session)):
    """分页查询环境列表"""
    service = ApiEnvironmentService(session)
    datas, total = service.query_by_page(
        page=query.page,
        page_size=query.pageSize,
        project_id=query.project_id,
        env_name=query.env_name,
        env_code=query.env_code,
        is_enabled=query.is_enabled
    )
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询环境",
                  dependencies=[Depends(check_permission("apitest:environment:query"))])
async def query_by_id(id: int = Query(..., description="环境ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询环境详情"""
    service = ApiEnvironmentService(session)
    data = service.get_by_id(id)
    if not data:
        return respModel.error_resp(msg="环境不存在")
    return respModel.ok_resp(obj=data)


@module_route.get("/queryByProject", summary="查询项目下所有环境",
                  dependencies=[Depends(check_permission("apitest:environment:query"))])
async def query_by_project(project_id: int = Query(..., description="项目ID"),
                           session: Session = Depends(get_session)):
    """查询项目下所有启用的环境"""
    service = ApiEnvironmentService(session)
    datas = service.query_by_project(project_id)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.get("/getDefaultEnv", summary="获取项目默认环境",
                  dependencies=[Depends(check_permission("apitest:environment:query"))])
async def get_default_env(project_id: int = Query(..., description="项目ID"),
                          session: Session = Depends(get_session)):
    """获取项目的默认环境"""
    service = ApiEnvironmentService(session)
    data = service.get_default_env(project_id)
    return respModel.ok_resp(obj=data)


@module_route.post("/insert", summary="新增环境",
                   dependencies=[Depends(check_permission("apitest:environment:add"))])
async def insert(env: ApiEnvironmentCreate, session: Session = Depends(get_session)):
    """新增环境配置"""
    service = ApiEnvironmentService(session)
    data = service.create(**env.model_dump())
    if not data:
        return respModel.error_resp(msg=f"环境代码 '{env.env_code}' 已存在")
    return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})


@module_route.put("/update", summary="更新环境",
                  dependencies=[Depends(check_permission("apitest:environment:edit"))])
async def update(env: ApiEnvironmentUpdate, session: Session = Depends(get_session)):
    """更新环境配置"""
    service = ApiEnvironmentService(session)
    update_data = env.model_dump(exclude_unset=True, exclude={"id"})
    updated = service.update(env.id, update_data)
    if not updated:
        return respModel.error_resp(msg="环境不存在")
    return respModel.ok_resp(msg="更新成功")


@module_route.delete("/delete", summary="删除环境",
                     dependencies=[Depends(check_permission("apitest:environment:delete"))])
async def delete(id: int = Query(..., description="环境ID"),
                 session: Session = Depends(get_session)):
    """删除环境配置"""
    service = ApiEnvironmentService(session)
    if not service.delete(id):
        return respModel.error_resp(msg="环境不存在")
    return respModel.ok_resp(msg="删除成功")


@module_route.put("/setDefault", summary="设置默认环境",
                  dependencies=[Depends(check_permission("apitest:environment:edit"))])
async def set_default(id: int = Query(..., description="环境ID"),
                      session: Session = Depends(get_session)):
    """设置为默认环境"""
    service = ApiEnvironmentService(session)
    if not service.set_default(id):
        return respModel.error_resp(msg="环境不存在")
    return respModel.ok_resp(msg="设置成功")


@module_route.put("/toggleEnabled", summary="切换启用状态",
                  dependencies=[Depends(check_permission("apitest:environment:edit"))])
async def toggle_enabled(id: int = Query(..., description="环境ID"),
                         session: Session = Depends(get_session)):
    """切换环境启用/禁用状态"""
    service = ApiEnvironmentService(session)
    data = service.toggle_enabled(id)
    if not data:
        return respModel.error_resp(msg="环境不存在")
    status = "启用" if data.is_enabled == 1 else "禁用"
    return respModel.ok_resp(msg=f"已{status}")


@module_route.post("/copy", summary="复制环境",
                   dependencies=[Depends(check_permission("apitest:environment:add"))])
async def copy_env(copy_data: ApiEnvironmentCopy, session: Session = Depends(get_session)):
    """复制环境配置"""
    service = ApiEnvironmentService(session)
    new_env = service.copy_environment(
        env_id=copy_data.source_id,
        new_env_name=copy_data.new_env_name,
        new_env_code=copy_data.new_env_code
    )
    if not new_env:
        return respModel.error_resp(msg="源环境不存在或环境代码已存在")
    return respModel.ok_resp(msg="复制成功", dic_t={"id": new_env.id})


@module_route.post("/initDefaultEnvs", summary="初始化默认环境",
                   dependencies=[Depends(check_permission("apitest:environment:add"))])
async def init_default_envs(project_id: int = Query(..., description="项目ID"),
                            session: Session = Depends(get_session)):
    """为项目初始化默认的开发/测试/生产环境"""
    # 检查是否已有环境
    existing = session.exec(
        select(module_model).where(module_model.project_id == project_id)
    ).first()
    
    if existing:
        return respModel.error_resp(msg="项目已存在环境配置")
    
    default_envs = [
        {"env_name": "开发环境", "env_code": "dev", "is_default": 1, "sort_order": 1},
        {"env_name": "测试环境", "env_code": "test", "is_default": 0, "sort_order": 2},
        {"env_name": "生产环境", "env_code": "prod", "is_default": 0, "sort_order": 3},
    ]
    
    created_ids = []
    for env_data in default_envs:
        env = module_model(
            project_id=project_id,
            **env_data,
            is_enabled=1,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(env)
        session.commit()
        session.refresh(env)
        created_ids.append(env.id)
    
    return respModel.ok_resp(msg="初始化成功", dic_t={"ids": created_ids})


async def _clear_default_env(session: Session, project_id: int, exclude_id: int = None):
    """清除项目的默认环境设置"""
    statement = select(module_model).where(
        and_(
            module_model.project_id == project_id,
            module_model.is_default == 1
        )
    )
    if exclude_id:
        statement = statement.where(module_model.id != exclude_id)
    
    envs = session.exec(statement).all()
    for env in envs:
        env.is_default = 0
        env.update_time = datetime.now()
        session.add(env)
    session.commit()
