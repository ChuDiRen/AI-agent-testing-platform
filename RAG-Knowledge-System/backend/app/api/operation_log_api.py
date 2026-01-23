"""
操作日志API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from services.operation_log_service import OperationLogService
from models.operation_log import OperationType
from db.session import get_db
from core.deps import get_current_user
from models.user import User
from core.resp_model import ResponseModel

router = APIRouter(prefix="/logs", tags=["操作日志"])


@router.get("/my-logs", response_model=ResponseModel)
async def get_my_logs(
    operation_type: Optional[OperationType] = None,
    module: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的操作日志

    需要认证
    """
    try:
        log_service = OperationLogService(db)
        logs = log_service.get_user_logs(
            user_id=current_user.id,
            operation_type=operation_type,
            module=module,
            skip=skip,
            limit=limit
        )

        return ResponseModel.success(
            data={
                "items": [log.dict() for log in logs],
                "count": len(logs)
            },
            message="获取操作日志成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")


@router.get("", response_model=ResponseModel)
async def get_logs(
    operation_type: Optional[OperationType] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取操作日志（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        log_service = OperationLogService(db)

        # 转换日期字符串
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        logs = log_service.get_logs(
            operation_type=operation_type,
            module=module,
            status=status,
            start_date=start_dt,
            end_date=end_dt,
            skip=skip,
            limit=limit
        )

        return ResponseModel.success(
            data={
                "items": [log.dict() for log in logs],
                "count": len(logs)
            },
            message="获取操作日志成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取操作日志失败: {str(e)}")


@router.get("/stats", response_model=ResponseModel)
async def get_log_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取操作统计（管理员）

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        log_service = OperationLogService(db)

        # 转换日期字符串
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        stats = log_service.get_operation_stats(start_dt, end_dt)

        return ResponseModel.success(
            data=stats,
            message="获取统计成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/count", response_model=ResponseModel)
async def count_logs(
    operation_type: Optional[OperationType] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    统计日志数量

    需要认证
    """
    try:
        # 检查权限
        if not current_user.is_superuser:
            return ResponseModel.error(message="需要管理员权限")

        log_service = OperationLogService(db)

        # 转换日期字符串
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        count = log_service.count_logs(
            operation_type=operation_type,
            module=module,
            status=status,
            start_date=start_dt,
            end_date=end_dt
        )

        return ResponseModel.success(
            data={"count": count},
            message="统计成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")
