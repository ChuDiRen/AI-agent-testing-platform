"""
日志管理模块API
提供系统日志的查看、搜索、导出和清除功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv
from datetime import datetime

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.log_service import LogService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/", summary="获取系统日志列表")
@log_user_action(action="查看", resource_type="系统日志", description="查看日志列表")
async def get_log_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    level: Optional[str] = Query(None, description="日志级别"),
    module: Optional[str] = Query(None, description="模块"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    date_range: Optional[str] = Query(None, description="时间范围"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统日志列表（分页）"""
    try:
        log_service = LogService(db)

        # 构建查询条件
        filters = {}
        if level:
            filters['level'] = level
        if module:
            filters['module'] = module
        if keyword:
            filters['keyword'] = keyword
        if date_range:
            filters['date_range'] = date_range

        # 获取日志列表
        logs, total = await log_service.get_log_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据
        log_list = []
        for log in logs:
            log_data = {
                "id": log.id,
                "level": log.level,
                "module": log.module or "System",
                "message": log.message,
                "user": log.user_name if hasattr(log, 'user_name') else None,
                "ip_address": log.ip_address,
                "traceback": log.traceback,
                "extra_data": log.extra_data,
                "created_at": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else ""
            }
            log_list.append(log_data)

        response_data = {
            "items": log_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取日志列表失败: {str(e)}")


@router.get("/{log_id}", summary="获取单个日志详情")
@log_user_action(action="查看", resource_type="系统日志", description="查看日志详情")
async def get_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个日志的详细信息"""
    try:
        log_service = LogService(db)
        log = await log_service.get_log_by_id(log_id)

        if not log:
            return Fail(msg="日志不存在")

        log_data = {
            "id": log.id,
            "level": log.level,
            "module": log.module or "System",
            "message": log.message,
            "user": log.user_name if hasattr(log, 'user_name') else None,
            "ip_address": log.ip_address,
            "traceback": log.traceback,
            "extra_data": log.extra_data,
            "created_at": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else ""
        }

        return Success(data=log_data)

    except Exception as e:
        return Fail(msg=f"获取日志详情失败: {str(e)}")


@router.post("/search", summary="搜索系统日志")
@log_user_action(action="搜索", resource_type="系统日志", description="搜索系统日志")
async def search_logs(
    keyword: Optional[str] = Body(None, description="关键词"),
    level: Optional[str] = Body(None, description="日志级别"),
    module: Optional[str] = Body(None, description="模块"),
    date_range: Optional[List[str]] = Body(None, description="时间范围"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(50, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索系统日志"""
    try:
        log_service = LogService(db)

        # 构建搜索条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if level:
            filters['level'] = level
        if module:
            filters['module'] = module
        if date_range and len(date_range) == 2:
            filters['start_date'] = date_range[0]
            filters['end_date'] = date_range[1]

        # 执行搜索
        logs, total = await log_service.search_logs(
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        log_list = []
        for log in logs:
            log_data = {
                "id": log.id,
                "level": log.level,
                "module": log.module or "System",
                "message": log.message,
                "user": log.user_name if hasattr(log, 'user_name') else None,
                "ip_address": log.ip_address,
                "traceback": log.traceback,
                "extra_data": log.extra_data,
                "created_at": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else ""
            }
            log_list.append(log_data)

        response_data = {
            "items": log_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索日志失败: {str(e)}")


@router.get("/export", summary="导出系统日志")
@log_user_action(action="导出", resource_type="系统日志", description="导出系统日志")
async def export_logs(
    level: Optional[str] = Query(None, description="日志级别"),
    module: Optional[str] = Query(None, description="模块"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    date_range: Optional[str] = Query(None, description="时间范围"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出系统日志为CSV文件"""
    try:
        log_service = LogService(db)

        # 构建查询条件
        filters = {}
        if level:
            filters['level'] = level
        if module:
            filters['module'] = module
        if keyword:
            filters['keyword'] = keyword
        if date_range:
            filters['date_range'] = date_range

        # 获取所有符合条件的日志（限制数量防止内存溢出）
        logs = await log_service.get_all_logs(filters=filters, limit=10000)

        # 创建CSV内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            "ID", "时间", "级别", "模块", "消息", "用户", "IP地址", "堆栈跟踪", "额外数据"
        ])
        
        # 写入数据
        for log in logs:
            writer.writerow([
                log.id,
                log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else "",
                log.level,
                log.module or "System",
                log.message,
                log.user_name if hasattr(log, 'user_name') else "",
                log.ip_address or "",
                log.traceback or "",
                str(log.extra_data) if log.extra_data else ""
            ])

        # 转换为字节流
        csv_content = output.getvalue()
        output.close()

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8-sig')),  # 使用BOM以支持Excel正确显示中文
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=system_logs.csv"}
        )

    except Exception as e:
        return Fail(msg=f"导出日志失败: {str(e)}")


@router.delete("/clear", summary="清除系统日志")
@log_user_action(action="清除", resource_type="系统日志", description="清除系统日志")
async def clear_logs(
    keep_days: int = Body(0, description="保留天数，0表示清除所有"),
    level: Optional[str] = Body(None, description="只清除指定级别的日志"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清除系统日志"""
    try:
        log_service = LogService(db)

        # 执行清除操作
        cleared_count = await log_service.clear_logs(
            keep_days=keep_days,
            level=level,
            operator_id=current_user.id
        )

        return Success(
            data={"cleared_count": cleared_count},
            msg=f"日志清除成功，共清除 {cleared_count} 条记录"
        )

    except Exception as e:
        return Fail(msg=f"清除日志失败: {str(e)}")


@router.get("/statistics/overview", summary="获取日志统计概览")
@log_user_action(action="查看", resource_type="系统日志", description="查看日志统计")
async def get_log_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日志统计概览"""
    try:
        log_service = LogService(db)
        
        # 获取统计数据
        statistics = await log_service.get_log_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")


@router.get("/levels", summary="获取日志级别列表")
async def get_log_levels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取支持的日志级别列表"""
    levels = [
        {"label": "DEBUG", "value": "DEBUG"},
        {"label": "INFO", "value": "INFO"},
        {"label": "WARNING", "value": "WARNING"},
        {"label": "ERROR", "value": "ERROR"},
        {"label": "CRITICAL", "value": "CRITICAL"}
    ]
    
    return Success(data=levels)


@router.get("/modules", summary="获取日志模块列表")
async def get_log_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日志模块列表"""
    try:
        log_service = LogService(db)
        
        # 获取所有模块
        modules = await log_service.get_log_modules()
        
        return Success(data=modules)

    except Exception as e:
        return Fail(msg=f"获取模块列表失败: {str(e)}")


@router.post("/analyze", summary="日志分析")
@log_user_action(action="分析", resource_type="系统日志", description="分析系统日志")
async def analyze_logs(
    time_period: str = Body("1d", description="分析时间段: 1h, 6h, 1d, 7d, 30d"),
    analysis_type: str = Body("error", description="分析类型: error, performance, user_activity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分析系统日志"""
    try:
        log_service = LogService(db)
        
        # 执行日志分析
        analysis_result = await log_service.analyze_logs(
            time_period=time_period,
            analysis_type=analysis_type
        )
        
        return Success(data=analysis_result, msg="日志分析完成")

    except Exception as e:
        return Fail(msg=f"日志分析失败: {str(e)}")


@router.get("/recent", summary="获取最近日志")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=500, description="获取数量"),
    level: Optional[str] = Query(None, description="日志级别"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近的日志记录（用于实时监控）"""
    try:
        log_service = LogService(db)
        
        # 获取最近日志
        logs = await log_service.get_recent_logs(limit=limit, level=level)
        
        # 构建响应数据
        log_list = []
        for log in logs:
            log_data = {
                "id": log.id,
                "level": log.level,
                "module": log.module or "System",
                "message": log.message,
                "user": log.user_name if hasattr(log, 'user_name') else None,
                "ip_address": log.ip_address,
                "created_at": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else ""
            }
            log_list.append(log_data)
        
        return Success(data=log_list)

    except Exception as e:
        return Fail(msg=f"获取最近日志失败: {str(e)}")


@router.delete("/batch", summary="批量删除日志")
@log_user_action(action="批量删除", resource_type="系统日志", description="批量删除日志")
async def batch_delete_logs(
    log_ids: List[int] = Body(..., description="日志ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除指定的日志记录"""
    try:
        log_service = LogService(db)
        
        if not log_ids:
            return Fail(msg="请选择要删除的日志")

        # 执行批量删除
        success_count, error_messages = await log_service.batch_delete_logs(
            log_ids=log_ids,
            operator_id=current_user.id
        )

        if error_messages:
            return Success(
                data={"success_count": success_count, "errors": error_messages},
                msg=f"批量删除完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={"success_count": success_count},
                msg=f"批量删除完成，成功删除 {success_count} 条日志"
            )

    except Exception as e:
        return Fail(msg=f"批量删除失败: {str(e)}")


@router.post("/archive", summary="归档历史日志")
@log_user_action(action="归档", resource_type="系统日志", description="归档历史日志")
async def archive_logs(
    days_before: int = Body(30, description="归档多少天前的日志"),
    archive_path: Optional[str] = Body(None, description="归档路径"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """归档历史日志"""
    try:
        log_service = LogService(db)
        
        # 执行日志归档
        archived_count, archive_file = await log_service.archive_logs(
            days_before=days_before,
            archive_path=archive_path,
            operator_id=current_user.id
        )
        
        return Success(
            data={
                "archived_count": archived_count,
                "archive_file": archive_file
            },
            msg=f"日志归档成功，共归档 {archived_count} 条记录"
        )

    except Exception as e:
        return Fail(msg=f"归档日志失败: {str(e)}")
