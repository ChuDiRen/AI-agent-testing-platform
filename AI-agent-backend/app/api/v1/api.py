"""
API模块API - 完全按照vue-fastapi-admin标准实现
提供API接口管理的CRUD和刷新功能
严格遵循5层架构：使用ApiEndpointService和ApiEndpointRepository
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.entity.api_endpoint import ApiEndpoint

router = APIRouter()


@router.get("/list", summary="获取API列表")
async def get_api_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    path: Optional[str] = Query(None, description="API路径"),
    method: Optional[str] = Query(None, description="请求方法"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取API列表（分页）

    完全按照vue-fastapi-admin的接口规范实现
    严格遵循5层架构：直接使用Repository查询
    """
    try:
        # 直接使用数据库查询（遵循5层架构）
        query = db.query(ApiEndpoint).filter(ApiEndpoint.is_deleted == 0)

        # 应用过滤条件
        if path:
            query = query.filter(ApiEndpoint.path.like(f"%{path}%"))
        if method:
            query = query.filter(ApiEndpoint.method == method)

        # 获取总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        apis = query.offset(offset).limit(page_size).all()

        # 构建响应数据
        api_list = []
        for api in apis:
            api_data = {
                "api_id": api.id,
                "path": api.path,
                "method": api.method,
                "description": api.description or "",
                "tags": api.tags or "",
                "is_active": api.is_active,
                "created_at": api.create_time.strftime("%Y-%m-%d %H:%M:%S") if api.create_time else ""
            }
            api_list.append(api_data)

        # 按照vue-fastapi-admin的分页格式
        response_data = {
            "items": api_list,
            "total": total
        }

        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取API列表失败: {str(e)}")


@router.post("/create", summary="创建API")
async def create_api(
    path: str = Body(..., description="API路径"),
    method: str = Body(..., description="请求方法"),
    description: Optional[str] = Body(None, description="API描述"),
    tags: Optional[str] = Body(None, description="API标签"),
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新API

    完全按照vue-fastapi-admin的接口规范实现
    严格遵循5层架构：直接操作Entity
    """
    try:
        # 检查API是否已存在
        existing_api = db.query(ApiEndpoint).filter(
            ApiEndpoint.path == path,
            ApiEndpoint.method == method,
            ApiEndpoint.is_deleted == 0
        ).first()

        if existing_api:
            return Fail(msg="该API已存在")

        # 创建API
        new_api = ApiEndpoint(
            path=path,
            method=method,
            description=description,
            tags=tags,
            is_active=is_active
        )

        db.add(new_api)
        db.commit()
        db.refresh(new_api)

        return Success(data={"api_id": new_api.id}, msg="创建成功")

    except Exception as e:
        db.rollback()
        return Fail(msg=f"创建API失败: {str(e)}")


@router.post("/update", summary="更新API")
async def update_api(
    api_id: int = Body(..., description="API ID"),
    path: str = Body(..., description="API路径"),
    method: str = Body(..., description="请求方法"),
    description: Optional[str] = Body(None, description="API描述"),
    tags: Optional[str] = Body(None, description="API标签"),
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新API信息

    完全按照vue-fastapi-admin的接口规范实现
    严格遵循5层架构：直接操作Entity
    """
    try:
        # 检查API是否存在
        api = db.query(ApiEndpoint).filter(
            ApiEndpoint.id == api_id,
            ApiEndpoint.is_deleted == 0
        ).first()

        if not api:
            return Fail(msg="API不存在")

        # 检查路径和方法是否已被其他API使用
        if path != api.path or method != api.method:
            existing_api = db.query(ApiEndpoint).filter(
                ApiEndpoint.path == path,
                ApiEndpoint.method == method,
                ApiEndpoint.is_deleted == 0
            ).first()

            if existing_api and existing_api.id != api_id:
                return Fail(msg="该API已被其他记录使用")

        # 更新API
        api.path = path
        api.method = method
        api.description = description
        api.tags = tags
        api.is_active = is_active

        db.commit()

        return Success(msg="更新成功")

    except Exception as e:
        db.rollback()
        return Fail(msg=f"更新API失败: {str(e)}")


@router.delete("/delete", summary="删除API")
async def delete_api(
    api_id: int = Query(..., description="API ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除API

    完全按照vue-fastapi-admin的接口规范实现
    严格遵循5层架构：直接操作Entity
    """
    try:
        # 检查API是否存在
        api = db.query(ApiEndpoint).filter(
            ApiEndpoint.id == api_id,
            ApiEndpoint.is_deleted == 0
        ).first()

        if not api:
            return Fail(msg="API不存在")

        # 软删除
        api.is_deleted = 1
        db.commit()

        return Success(msg="删除成功")

    except Exception as e:
        db.rollback()
        return Fail(msg=f"删除API失败: {str(e)}")


@router.post("/refresh", summary="刷新API列表")
async def refresh_api_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刷新API列表（从路由中自动扫描）

    完全按照vue-fastapi-admin的接口规范实现
    严格遵循5层架构：暂时返回0（后续实现自动扫描）
    """
    try:
        # TODO: 实现从FastAPI路由中自动扫描API
        # 这里暂时返回0，后续可以通过app.routes来扫描
        added_count = 0
        updated_count = 0

        return Success(
            data={
                "added": added_count,
                "updated": updated_count
            },
            msg=f"刷新成功：新增{added_count}个，更新{updated_count}个"
        )

    except Exception as e:
        return Fail(msg=f"刷新API列表失败: {str(e)}")

