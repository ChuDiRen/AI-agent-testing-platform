# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告控制器
处理测试报告相关的HTTP请求
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.entity.user import User
from app.service.test_report_service import TestReportService
from app.dto.test_report_dto import (
    TestReportCreateRequest, TestReportUpdateRequest, TestReportSearchRequest,
    TestReportResponse, TestReportListResponse, TestReportStatisticsResponse
)
from app.utils.exceptions import BusinessException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test-reports", tags=["测试报告"])


@router.get("/", response_model=TestReportListResponse)
async def get_test_reports(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    report_type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取测试报告列表
    
    Args:
        page: 页码
        page_size: 每页大小
        keyword: 关键词搜索
        report_type: 报告类型筛选
        status: 状态筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        测试报告列表响应
    """
    try:
        logger.info(f"User {current_user.id} getting test reports list")
        
        # 构建搜索请求
        search_request = TestReportSearchRequest(
            page=page,
            page_size=page_size,
            keyword=keyword,
            report_type=report_type,
            status=status
        )
        
        # 调用服务层
        service = TestReportService(db)
        result = service.get_report_list(search_request)
        
        logger.info(f"Retrieved {len(result.reports)} test reports for user {current_user.id}")
        return result
        
    except BusinessException as e:
        logger.error(f"Business error getting test reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting test reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取测试报告列表失败"
        )


@router.get("/statistics", response_model=TestReportStatisticsResponse)
async def get_test_report_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取测试报告统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        测试报告统计响应
    """
    try:
        logger.info(f"User {current_user.id} getting test report statistics")
        
        # 调用服务层
        service = TestReportService(db)
        result = service.get_statistics()
        
        logger.info(f"Retrieved test report statistics for user {current_user.id}")
        return result
        
    except BusinessException as e:
        logger.error(f"Business error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )


@router.post("/", response_model=TestReportResponse)
async def create_test_report(
    request: TestReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建测试报告
    
    Args:
        request: 创建请求
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的测试报告响应
    """
    try:
        logger.info(f"User {current_user.id} creating test report: {request.name}")
        
        # 调用服务层
        service = TestReportService(db)
        result = service.create_report(request, current_user.id)
        
        logger.info(f"Created test report {result.id} for user {current_user.id}")
        return result
        
    except BusinessException as e:
        logger.error(f"Business error creating test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建测试报告失败"
        )


@router.get("/{report_id}", response_model=TestReportResponse)
async def get_test_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个测试报告详情
    
    Args:
        report_id: 报告ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        测试报告详情响应
    """
    try:
        logger.info(f"User {current_user.id} getting test report {report_id}")
        
        # 调用服务层
        service = TestReportService(db)
        # 这里需要在service中添加get_report_by_id方法
        # result = service.get_report_by_id(report_id)
        
        # 临时返回空响应，避免编译错误
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="功能开发中"
        )
        
    except BusinessException as e:
        logger.error(f"Business error getting test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取测试报告失败"
        )


@router.put("/{report_id}", response_model=TestReportResponse)
async def update_test_report(
    report_id: int,
    request: TestReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新测试报告
    
    Args:
        report_id: 报告ID
        request: 更新请求
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的测试报告响应
    """
    try:
        logger.info(f"User {current_user.id} updating test report {report_id}")
        
        # 调用服务层
        service = TestReportService(db)
        # 这里需要在service中添加update_report方法
        # result = service.update_report(report_id, request)
        
        # 临时返回空响应，避免编译错误
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="功能开发中"
        )
        
    except BusinessException as e:
        logger.error(f"Business error updating test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新测试报告失败"
        )


@router.delete("/{report_id}")
async def delete_test_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除测试报告
    
    Args:
        report_id: 报告ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    try:
        logger.info(f"User {current_user.id} deleting test report {report_id}")
        
        # 调用服务层
        service = TestReportService(db)
        # 这里需要在service中添加delete_report方法
        # service.delete_report(report_id)
        
        # 临时返回空响应，避免编译错误
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="功能开发中"
        )
        
    except BusinessException as e:
        logger.error(f"Business error deleting test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting test report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除测试报告失败"
        )
