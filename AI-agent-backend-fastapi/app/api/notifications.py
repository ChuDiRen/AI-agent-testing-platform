# Copyright (c) 2025 左岚. All rights reserved.
"""
消息通知API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListParams,
    NotificationStats
)
from app.schemas.common import APIResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=APIResponse[NotificationResponse])
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建通知(管理员功能)"""
    service = NotificationService(db)
    notification = await service.create_notification(notification_data)
    return APIResponse(success=True, message="创建通知成功", data=notification)


@router.get("/", response_model=APIResponse[PaginatedResponse[NotificationResponse]])
async def get_notifications(
    filter_type: str = "all",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的通知列表"""
    service = NotificationService(db)
    
    # 获取通知列表
    notifications = await service.get_user_notifications(
        current_user.user_id,
        filter_type,
        skip,
        limit
    )
    
    # 获取总数
    from app.repositories.notification_repository import NotificationRepository
    repository = NotificationRepository(db)
    total = await repository.get_count_by_user_id(current_user.user_id, filter_type)
    
    # 计算总页数
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return APIResponse(
        success=True,
        data=PaginatedResponse(
            items=notifications,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            pages=pages
        )
    )


@router.get("/stats", response_model=APIResponse[NotificationStats])
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的通知统计"""
    service = NotificationService(db)
    stats = await service.get_notification_stats(current_user.user_id)
    return APIResponse(success=True, data=stats)


@router.get("/{notification_id}", response_model=APIResponse[NotificationResponse])
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取通知详情"""
    service = NotificationService(db)
    notification = await service.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    # 验证通知是否属于当前用户
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此通知"
        )
    
    return APIResponse(success=True, data=notification)


@router.put("/{notification_id}/read", response_model=APIResponse[NotificationResponse])
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记通知为已读"""
    service = NotificationService(db)
    
    # 先获取通知验证权限
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此通知"
        )
    
    # 标记为已读
    updated_notification = await service.mark_as_read(notification_id)
    return APIResponse(success=True, message="标记已读成功", data=updated_notification)


@router.put("/read-all", response_model=APIResponse[dict])
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记所有通知为已读"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.user_id)
    return APIResponse(
        success=True,
        message=f"已标记{count}条通知为已读",
        data={"count": count}
    )


@router.delete("/{notification_id}", response_model=APIResponse[None])
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除通知"""
    service = NotificationService(db)
    
    # 先获取通知验证权限
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此通知"
        )
    
    # 删除通知
    success = await service.delete_notification(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除通知失败"
        )
    
    return APIResponse(success=True, message="删除通知成功")


@router.delete("/", response_model=APIResponse[dict])
async def delete_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除所有通知"""
    service = NotificationService(db)
    count = await service.delete_all_notifications(current_user.user_id)
    return APIResponse(
        success=True,
        message=f"已删除{count}条通知",
        data={"count": count}
    )

