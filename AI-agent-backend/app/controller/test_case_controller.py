# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例Controller
处理测试用例相关的HTTP请求
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.service.test_case_service import TestCaseService
from app.dto.test_case_dto import (
    TestCaseCreateRequest, TestCaseUpdateRequest, TestCaseSearchRequest,
    TestCaseResponse, TestCaseListResponse, TestCaseStatisticsResponse,
    TestCaseExecutionRequest, TestCaseBatchOperationRequest, TestCaseBatchOperationResponse,
    TestCaseGenerationHistoryRequest, TestCaseGenerationHistoryResponse
)
from app.dto.base import Success, Fail
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/test-cases", tags=["测试用例管理"])


@router.post("/", response_model=TestCaseResponse, summary="创建测试用例")
def create_test_case(
    request: TestCaseCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新的测试用例"""
    try:
        test_case_service = TestCaseService(db)
        test_case = test_case_service.create_test_case(request, current_user.get("user_id"))
        
        return Success(data=test_case, msg="测试用例创建成功")
        
    except Exception as e:
        logger.error(f"Error creating test case: {str(e)}")
        return Fail(msg=f"创建测试用例失败: {str(e)}")


@router.get("/{test_case_id}", response_model=TestCaseResponse, summary="获取测试用例详情")
def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """根据ID获取测试用例详情"""
    try:
        test_case_service = TestCaseService(db)
        test_case = test_case_service.get_test_case_by_id(test_case_id)
        
        if not test_case:
            return Fail(code=404, msg="测试用例不存在")
        
        return Success(data=test_case)
        
    except Exception as e:
        logger.error(f"Error getting test case {test_case_id}: {str(e)}")
        return Fail(msg=f"获取测试用例失败: {str(e)}")


@router.put("/{test_case_id}", response_model=TestCaseResponse, summary="更新测试用例")
def update_test_case(
    test_case_id: int,
    request: TestCaseUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新测试用例信息"""
    try:
        test_case_service = TestCaseService(db)
        test_case = test_case_service.update_test_case(test_case_id, request)
        
        if not test_case:
            return Fail(code=404, msg="测试用例不存在")
        
        return Success(data=test_case, msg="测试用例更新成功")
        
    except Exception as e:
        logger.error(f"Error updating test case {test_case_id}: {str(e)}")
        return Fail(msg=f"更新测试用例失败: {str(e)}")


@router.delete("/{test_case_id}", summary="删除测试用例")
def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除测试用例"""
    try:
        test_case_service = TestCaseService(db)
        success = test_case_service.delete_test_case(test_case_id)
        
        if success:
            return Success(msg="测试用例删除成功")
        else:
            return Fail(msg="删除测试用例失败")
        
    except Exception as e:
        logger.error(f"Error deleting test case {test_case_id}: {str(e)}")
        return Fail(msg=f"删除测试用例失败: {str(e)}")


@router.post("/search", response_model=TestCaseListResponse, summary="搜索测试用例")
def search_test_cases(
    request: TestCaseSearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """搜索测试用例列表"""
    try:
        test_case_service = TestCaseService(db)
        result = test_case_service.search_test_cases(request)
        
        return Success(data=result)
        
    except Exception as e:
        logger.error(f"Error searching test cases: {str(e)}")
        return Fail(msg=f"搜索测试用例失败: {str(e)}")


@router.get("/", response_model=TestCaseListResponse, summary="获取测试用例列表")
def list_test_cases(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例列表"""
    try:
        request = TestCaseSearchRequest(page=page, page_size=page_size)
        test_case_service = TestCaseService(db)
        result = test_case_service.search_test_cases(request)
        
        return Success(data=result)
        
    except Exception as e:
        logger.error(f"Error listing test cases: {str(e)}")
        return Fail(msg=f"获取测试用例列表失败: {str(e)}")


@router.get("/statistics/overview", response_model=TestCaseStatisticsResponse, summary="获取测试用例统计")
def get_test_case_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例统计信息"""
    try:
        test_case_service = TestCaseService(db)
        statistics = test_case_service.get_test_case_statistics()
        
        return Success(data=statistics)
        
    except Exception as e:
        logger.error(f"Error getting test case statistics: {str(e)}")
        return Fail(msg=f"获取统计信息失败: {str(e)}")


@router.post("/{test_case_id}/execute", response_model=TestCaseResponse, summary="执行测试用例")
def execute_test_case(
    test_case_id: int,
    request: TestCaseExecutionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """执行测试用例"""
    try:
        test_case_service = TestCaseService(db)
        executor_id = request.executor_id or current_user.get("user_id")
        test_case = test_case_service.execute_test_case(test_case_id, executor_id)
        
        return Success(data=test_case, msg="测试用例开始执行")
        
    except Exception as e:
        logger.error(f"Error executing test case {test_case_id}: {str(e)}")
        return Fail(msg=f"执行测试用例失败: {str(e)}")


@router.post("/{test_case_id}/complete", response_model=TestCaseResponse, summary="完成测试用例执行")
def complete_test_case(
    test_case_id: int,
    passed: bool,
    actual_result: str = None,
    execution_time: float = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """完成测试用例执行并设置结果"""
    try:
        test_case_service = TestCaseService(db)
        test_case = test_case_service.complete_test_case(
            test_case_id, passed, actual_result, execution_time
        )
        
        result_text = "通过" if passed else "失败"
        return Success(data=test_case, msg=f"测试用例执行完成: {result_text}")
        
    except Exception as e:
        logger.error(f"Error completing test case {test_case_id}: {str(e)}")
        return Fail(msg=f"完成测试用例失败: {str(e)}")


@router.post("/batch", response_model=TestCaseBatchOperationResponse, summary="批量操作测试用例")
def batch_operation_test_cases(
    request: TestCaseBatchOperationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量操作测试用例"""
    try:
        test_case_service = TestCaseService(db)
        result = test_case_service.batch_operation(request)

        return Success(data=result, msg=f"批量操作完成: {result.success_count}/{result.total} 成功")

    except Exception as e:
        logger.error(f"Error in batch operation: {str(e)}")
        return Fail(msg=f"批量操作失败: {str(e)}")


@router.get("/history/generation", response_model=TestCaseGenerationHistoryResponse, summary="获取测试用例生成历史")
def get_generation_history(
    page: int = 1,
    page_size: int = 10,
    user_id: int = None,
    status: str = None,
    test_type: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例生成历史记录"""
    try:
        # 构建请求对象
        request = TestCaseGenerationHistoryRequest(
            page=page,
            page_size=page_size,
            user_id=user_id,
            status=status,
            test_type=test_type
        )

        test_case_service = TestCaseService(db)
        result = test_case_service.get_generation_history(request, current_user.id)

        return Success(data=result, msg="获取生成历史成功")

    except Exception as e:
        logger.error(f"Error getting generation history: {str(e)}")
        return Fail(msg=f"获取生成历史失败: {str(e)}")
