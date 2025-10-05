# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.testcase_service import TestCaseService
from app.schemas.testcase import (
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    TestCaseExecute
)
from app.schemas.common import APIResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.post("/", response_model=APIResponse[TestCaseResponse])
async def create_testcase(
    testcase_data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestCaseResponse]:
    """创建测试用例"""
    service = TestCaseService(db)
    testcase = await service.create_testcase(testcase_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="测试用例创建成功",
        data=TestCaseResponse.model_validate(testcase)
    )


@router.get("/", response_model=APIResponse[PaginatedResponse[TestCaseResponse]])
async def get_testcases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PaginatedResponse[TestCaseResponse]]:
    """获取测试用例列表"""
    service = TestCaseService(db)
    pagination = PaginationParams(page=page, page_size=page_size)
    
    testcases, total = await service.get_testcases_paginated(
        pagination=pagination,
        test_type=test_type,
        keyword=keyword,
        status=status,
        priority=priority
    )
    
    paginated_data = PaginatedResponse.create(
        items=[TestCaseResponse.model_validate(tc) for tc in testcases],
        total=total,
        page=page,
        page_size=page_size
    )
    
    return APIResponse(
        success=True,
        data=paginated_data
    )


@router.get("/statistics", response_model=APIResponse[dict])
async def get_statistics(
    test_type: Optional[str] = Query(None, description="测试类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """获取统计信息"""
    service = TestCaseService(db)
    stats = await service.get_statistics(test_type=test_type)
    
    return APIResponse(
        success=True,
        data=stats
    )


@router.get("/{testcase_id}", response_model=APIResponse[TestCaseResponse])
async def get_testcase(
    testcase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestCaseResponse]:
    """获取测试用例详情"""
    service = TestCaseService(db)
    testcase = await service.get_testcase(testcase_id)
    
    if not testcase:
        return APIResponse(
            success=False,
            message="测试用例不存在"
        )
    
    return APIResponse(
        success=True,
        data=TestCaseResponse.model_validate(testcase)
    )


@router.put("/{testcase_id}", response_model=APIResponse[TestCaseResponse])
async def update_testcase(
    testcase_id: int,
    testcase_data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestCaseResponse]:
    """更新测试用例"""
    service = TestCaseService(db)
    
    try:
        testcase = await service.update_testcase(testcase_id, testcase_data)
        return APIResponse(
            success=True,
            message="测试用例更新成功",
            data=TestCaseResponse.model_validate(testcase)
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.delete("/{testcase_id}", response_model=APIResponse[None])
async def delete_testcase(
    testcase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除测试用例"""
    service = TestCaseService(db)
    success = await service.delete_testcase(testcase_id)
    
    if not success:
        return APIResponse(
            success=False,
            message="测试用例不存在"
        )
    
    return APIResponse(
        success=True,
        message="测试用例删除成功"
    )


@router.post("/{testcase_id}/execute", response_model=APIResponse[dict])
async def execute_testcase(
    testcase_id: int,
    execute_data: TestCaseExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """执行测试用例"""
    from app.services.test_executor import TestExecutorFactory

    service = TestCaseService(db)
    testcase = await service.get_testcase(testcase_id)

    if not testcase:
        return APIResponse(
            success=False,
            message="测试用例不存在"
        )

    # 使用测试执行引擎执行
    try:
        executor = TestExecutorFactory.get_executor(testcase.test_type)
        result = await executor.execute(testcase, execute_data.config)

        result["testcase_id"] = testcase_id
        result["testcase_name"] = testcase.name

        return APIResponse(
            success=True,
            message="测试用例执行完成",
            data=result
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.post("/batch-execute", response_model=APIResponse[dict])
async def batch_execute_testcases(
    testcase_ids: list[int],
    execute_data: TestCaseExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """
    批量执行测试用例
    
    Args:
        testcase_ids: 测试用例ID列表
        execute_data: 执行配置
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        执行结果汇总
    """
    from app.services.test_executor import TestExecutorFactory
    import asyncio
    
    if not testcase_ids:
        return APIResponse(
            success=False,
            message="请选择要执行的测试用例"
        )
    
    service = TestCaseService(db)
    results = []
    passed_count = 0
    failed_count = 0
    error_count = 0
    total_duration = 0.0
    
    # 并发执行测试用例
    async def execute_single(testcase_id: int):
        try:
            testcase = await service.get_testcase(testcase_id)
            if not testcase:
                return {
                    "testcase_id": testcase_id,
                    "testcase_name": f"用例{testcase_id}",
                    "status": "error",
                    "error_message": "测试用例不存在",
                    "duration": 0
                }
            
            executor = TestExecutorFactory.get_executor(testcase.test_type)
            result = await executor.execute(testcase, execute_data.config)
            
            result["testcase_id"] = testcase_id
            result["testcase_name"] = testcase.name
            
            return result
        except Exception as e:
            return {
                "testcase_id": testcase_id,
                "testcase_name": f"用例{testcase_id}",
                "status": "error",
                "error_message": str(e),
                "duration": 0
            }
    
    # 并发执行所有用例（最多10个并发）
    semaphore = asyncio.Semaphore(10)
    
    async def execute_with_semaphore(testcase_id: int):
        async with semaphore:
            return await execute_single(testcase_id)
    
    tasks = [execute_with_semaphore(tc_id) for tc_id in testcase_ids]
    results = await asyncio.gather(*tasks)
    
    # 统计结果
    for result in results:
        total_duration += result.get("duration", 0)
        status = result.get("status", "error")
        
        if status == "passed":
            passed_count += 1
        elif status == "failed":
            failed_count += 1
        else:
            error_count += 1
    
    return APIResponse(
        success=True,
        message=f"批量执行完成: 通过{passed_count}个, 失败{failed_count}个, 错误{error_count}个",
        data={
            "total": len(testcase_ids),
            "passed": passed_count,
            "failed": failed_count,
            "error": error_count,
            "total_duration": round(total_duration, 2),
            "results": results
        }
    )

