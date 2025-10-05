"""
Copyright (c) 2025 左岚. All rights reserved.
测试数据管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.test_data import TestData
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取测试数据列表"""
    query = db.query(TestData)

    # 搜索过滤
    if keyword:
        query = query.filter(TestData.name.like(f"%{keyword}%"))
    if data_type:
        query = query.filter(TestData.data_type == data_type)

    # 分页
    total = query.count()
    items = query.order_by(TestData.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return APIResponse.success(
        data=TestDataListResponse(
            total=total,
            items=[TestDataResponse.from_orm(item) for item in items],
        )
    )


@router.get("/{data_id}", response_model=APIResponse[TestDataResponse])
async def get_test_data(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取测试数据详情"""
    test_data = db.query(TestData).filter(TestData.id == data_id).first()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    return APIResponse.success(data=TestDataResponse.from_orm(test_data))


@router.post("", response_model=APIResponse[TestDataResponse])
async def create_test_data(
    data: TestDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建测试数据"""
    # 检查名称是否重复
    existing = db.query(TestData).filter(TestData.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="数据名称已存在")

    # 创建测试数据
    test_data = TestData(**data.dict())
    db.add(test_data)
    db.commit()
    db.refresh(test_data)

    return APIResponse.success(data=TestDataResponse.from_orm(test_data), message="创建成功")


@router.put("/{data_id}", response_model=APIResponse[TestDataResponse])
async def update_test_data(
    data_id: int,
    data: TestDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新测试数据"""
    test_data = db.query(TestData).filter(TestData.id == data_id).first()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    # 如果更新名称，检查是否重复
    if data.name and data.name != test_data.name:
        existing = db.query(TestData).filter(TestData.name == data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="数据名称已存在")

    # 更新字段
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test_data, field, value)

    db.commit()
    db.refresh(test_data)

    return APIResponse.success(data=TestDataResponse.from_orm(test_data), message="更新成功")


@router.delete("/{data_id}", response_model=APIResponse)
async def delete_test_data(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除测试数据"""
    test_data = db.query(TestData).filter(TestData.id == data_id).first()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")

    db.delete(test_data)
    db.commit()

    return APIResponse.success(message="删除成功")

