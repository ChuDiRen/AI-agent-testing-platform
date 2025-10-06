"""
Copyright (c) 2025 左岚. All rights reserved.
测试数据管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.test_data import TestData
from app.models.user import User
from app.schemas.test_data import (
    TestDataCreate,
    TestDataUpdate,
    TestDataResponse,
    TestDataListResponse,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/test-data", tags=["测试数据管理"])


@router.get("", response_model=APIResponse[TestDataListResponse])
async def list_test_data(
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    data_type: Optional[str] = Query(None, description="数据类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取测试数据列表"""
    query = select(TestData)

    # 搜索过滤
    if keyword:
        query = query.where(TestData.name.like(f"%{keyword}%"))
    if data_type:
        query = query.where(TestData.data_type == data_type)

    # 获取总数
    count_query = select(func.count()).select_from(TestData)
    if keyword:
        count_query = count_query.where(TestData.name.like(f"%{keyword}%"))
    if data_type:
        count_query = count_query.where(TestData.data_type == data_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    query = query.order_by(TestData.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return APIResponse(
        data=TestDataListResponse(
            total=total,
            items=[TestDataResponse.model_validate(item) for item in items],
        )
    )


@router.get("/{data_id}", response_model=APIResponse[TestDataResponse])
async def get_test_data(
    data_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取测试数据详情"""
    query = select(TestData).where(TestData.id == data_id)
    result = await db.execute(query)
    test_data = result.scalar_one_or_none()

    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    return APIResponse(data=TestDataResponse.model_validate(test_data))


@router.post("", response_model=APIResponse[TestDataResponse])
async def create_test_data(
    data: TestDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建测试数据"""
    # 检查名称是否重复
    query = select(TestData).where(TestData.name == data.name)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="数据名称已存在")

    # 创建测试数据
    test_data = TestData(**data.model_dump())
    db.add(test_data)
    await db.commit()
    await db.refresh(test_data)

    return APIResponse(
        message="创建成功",
        data=TestDataResponse.model_validate(test_data)
    )


@router.put("/{data_id}", response_model=APIResponse[TestDataResponse])
async def update_test_data(
    data_id: int,
    data: TestDataUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新测试数据"""
    query = select(TestData).where(TestData.id == data_id)
    result = await db.execute(query)
    test_data = result.scalar_one_or_none()

    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    # 如果更新名称，检查是否重复
    if data.name and data.name != test_data.name:
        check_query = select(TestData).where(TestData.name == data.name)
        check_result = await db.execute(check_query)
        existing = check_result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="数据名称已存在")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test_data, field, value)

    await db.commit()
    await db.refresh(test_data)

    return APIResponse(
        message="更新成功",
        data=TestDataResponse.model_validate(test_data)
    )


@router.delete("/{data_id}", response_model=APIResponse)
async def delete_test_data(
    data_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除测试数据"""
    query = select(TestData).where(TestData.id == data_id)
    result = await db.execute(query)
    test_data = result.scalar_one_or_none()

    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    await db.delete(test_data)
    await db.commit()

    return APIResponse(message="删除成功")

