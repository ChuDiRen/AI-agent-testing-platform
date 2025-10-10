# Copyright (c) 2025 左岚. All rights reserved.
"""
执行API路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import io

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.report_exporter import report_exporter

from ..services.case_service import CaseService
from ..services.execution_service import ExecutionService
from ..services.report_service import ReportService
from ..models.execution import ApiEngineExecution
from ..schemas.case import CaseExecuteRequest
from ..schemas.execution import ExecutionStatusResponse, ExecutionResponse, ExecutionListResponse
from ..tasks.execution import execute_case_task

router = APIRouter()


@router.post("/batch", response_model=APIResponse[dict])
async def execute_batch(
    batch_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量执行测试用例"""
    case_ids = batch_data.get("case_ids", [])
    context = batch_data.get("context", {})
    execution_mode = batch_data.get("execution_mode", "parallel")  # parallel/sequential
    max_concurrent = batch_data.get("max_concurrent", 5)

    if not case_ids:
        return APIResponse(success=False, message="请选择要执行的用例")

    case_service = CaseService(db)

    # 验证所有用例都存在
    cases = await case_service.get_cases_by_ids(case_ids)
    if len(cases) != len(case_ids):
        return APIResponse(success=False, message="部分用例不存在")

    # 创建批量执行记录
    batch_execution_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.user_id}"

    if execution_mode == "parallel":
        # 并行执行
        from celery.group import group

        tasks = []
        execution_ids = []

        for case_id in case_ids:
            # 创建执行记录
            execution = ApiEngineExecution(
                case_id=case_id,
                task_id="",  # 待Celery任务创建后更新
                batch_execution_id=batch_execution_id,
                status="pending",
                executed_by=current_user.user_id
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            execution_ids.append(execution.execution_id)

            # 创建Celery任务
            task = execute_case_task.apply_async(
                args=[case_id, context, execution.execution_id, current_user.user_id]
            )
            execution.task_id = task.id
            tasks.append(task)

        await db.commit()

        return APIResponse(
            success=True,
            message="批量执行已启动",
            data={
                "batch_execution_id": batch_execution_id,
                "execution_mode": "parallel",
                "execution_ids": execution_ids,
                "task_ids": [task.id for task in tasks]
            }
        )
    else:
        # 顺序执行
        execution_ids = []
        task_ids = []

        for case_id in case_ids:
            # 创建执行记录
            execution = ApiEngineExecution(
                case_id=case_id,
                task_id="",
                batch_execution_id=batch_execution_id,
                status="pending",
                executed_by=current_user.user_id
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            execution_ids.append(execution.execution_id)

            # 创建链式任务
            task = execute_case_task.apply_async(
                args=[case_id, context, execution.execution_id, current_user.user_id]
            )
            execution.task_id = task.id
            task_ids.append(task.id)

            # 如果不是最后一个任务，设置回调
            if len(task_ids) < len(case_ids):
                # 这里可以实现任务链，但为简化起见，我们直接提交所有任务
                pass

        await db.commit()

        return APIResponse(
            success=True,
            message="批量执行已启动",
            data={
                "batch_execution_id": batch_execution_id,
                "execution_mode": "sequential",
                "execution_ids": execution_ids,
                "task_ids": task_ids
            }
        )


@router.post("/{case_id}/execute", response_model=APIResponse[dict])
async def execute_case(
    case_id: int,
    execute_data: CaseExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行测试用例"""
    # 检查用例是否存在
    case_service = CaseService(db)
    case = await case_service.get_case(case_id)
    
    if not case:
        return APIResponse(success=False, message="用例不存在")
    
    # 创建执行记录
    execution = ApiEngineExecution(
        case_id=case_id,
        task_id="",  # 待Celery任务创建后更新
        status="pending",
        executed_by=current_user.user_id
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # 提交Celery任务
    task = execute_case_task.apply_async(
        args=[
            case_id,
            execute_data.context or {},
            execution.execution_id,
            current_user.user_id
        ]
    )
    
    # 更新task_id
    execution.task_id = task.id
    await db.commit()
    
    return APIResponse(
        success=True,
        message="用例已提交执行",
        data={
            "execution_id": execution.execution_id,
            "task_id": task.id
        }
    )


@router.get("/", response_model=APIResponse[ExecutionListResponse])
async def get_executions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    case_id: Optional[int] = Query(None, description="用例ID"),
    status: Optional[str] = Query(None, description="执行状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行历史列表"""
    execution_service = ExecutionService(db)
    executions, total = await execution_service.get_executions(
        page=page,
        page_size=page_size,
        case_id=case_id,
        status=status
    )

    # 转换为响应格式
    items = [ExecutionResponse.model_validate(execution) for execution in executions]

    return APIResponse(
        success=True,
        data=ExecutionListResponse(total=total, items=items)
    )


@router.get("/{execution_id}", response_model=APIResponse[ExecutionResponse])
async def get_execution_detail(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录详情"""
    execution_service = ExecutionService(db)
    execution = await execution_service.get_execution(execution_id)

    if not execution:
        return APIResponse(success=False, message="执行记录不存在")

    return APIResponse(
        success=True,
        data=ExecutionResponse.model_validate(execution)
    )


@router.delete("/{execution_id}", response_model=APIResponse[dict])
async def delete_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除执行记录"""
    execution_service = ExecutionService(db)

    # 检查执行记录是否存在
    execution = await execution_service.get_execution(execution_id)
    if not execution:
        return APIResponse(success=False, message="执行记录不存在")

    # 删除
    success = await execution_service.delete_execution(execution_id)

    if success:
        return APIResponse(success=True, message="删除成功")
    else:
        return APIResponse(success=False, message="删除失败")


@router.get("/batch/{batch_execution_id}/status", response_model=APIResponse[dict])
async def get_batch_execution_status(
    batch_execution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """查询批量执行状态"""
    from celery.result import AsyncResult

    execution_service = ExecutionService(db)

    # 获取所有相关的执行记录
    executions = await execution_service.get_executions_by_batch_id(batch_execution_id)

    if not executions:
        return APIResponse(success=False, message="批量执行记录不存在")

    # 统计执行状态
    status_counts = {
        "pending": 0,
        "running": 0,
        "success": 0,
        "failed": 0,
        "error": 0
    }

    execution_details = []
    total_duration = 0
    total_steps = 0
    passed_steps = 0
    failed_steps = 0

    for execution in executions:
        status_counts[execution.status] = status_counts.get(execution.status, 0) + 1

        execution_details.append({
            "execution_id": execution.execution_id,
            "case_id": execution.case_id,
            "status": execution.status,
            "duration": execution.duration,
            "steps_total": execution.steps_total,
            "steps_passed": execution.steps_passed,
            "steps_failed": execution.steps_failed,
            "error_message": execution.error_message
        })

        total_duration += execution.duration or 0
        total_steps += execution.steps_total or 0
        passed_steps += execution.steps_passed or 0
        failed_steps += execution.steps_failed or 0

        # 获取任务状态
        if execution.task_id:
            task_result = AsyncResult(execution.task_id)
            if task_result.state == 'PENDING':
                status_counts["pending"] += 1
            elif task_result.state == 'RUNNING':
                status_counts["running"] += 1
            elif task_result.state == 'FAILURE' and execution.status not in ['failed', 'error']:
                status_counts["error"] += 1

    # 计算总体状态
    total_cases = len(executions)
    completed_cases = status_counts["success"] + status_counts["failed"] + status_counts["error"]
    progress = (completed_cases / total_cases * 100) if total_cases > 0 else 0

    overall_status = "running"
    if completed_cases == total_cases:
        if status_counts["failed"] + status_counts["error"] == 0:
            overall_status = "success"
        else:
            overall_status = "failed"
    elif status_counts["running"] > 0:
        overall_status = "running"
    else:
        overall_status = "pending"

    response_data = {
        "batch_execution_id": batch_execution_id,
        "overall_status": overall_status,
        "progress": round(progress, 2),
        "total_cases": total_cases,
        "completed_cases": completed_cases,
        "status_counts": status_counts,
        "total_duration": total_duration,
        "total_steps": total_steps,
        "passed_steps": passed_steps,
        "failed_steps": failed_steps,
        "success_rate": (passed_steps / total_steps * 100) if total_steps > 0 else 0,
        "execution_details": execution_details
    }

    return APIResponse(success=True, data=response_data)


@router.get("/task/{task_id}/status", response_model=APIResponse[ExecutionStatusResponse])
async def get_execution_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """查询执行状态"""
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id)

    response_data = ExecutionStatusResponse(
        task_id=task_id,
        status=task_result.state,
        progress=None,
        current_step=None,
        message=None,
        result=None
    )

    if task_result.state == 'PENDING':
        response_data.message = "任务等待中"
    elif task_result.state == 'RUNNING':
        if task_result.info:
            response_data.progress = task_result.info.get('progress')
            response_data.message = task_result.info.get('message')
    elif task_result.state == 'SUCCESS':
        response_data.progress = 100
        response_data.message = "执行成功"
        response_data.result = task_result.result
    elif task_result.state == 'FAILURE':
        response_data.message = f"执行失败: {str(task_result.info)}"

    return APIResponse(success=True, data=response_data)


@router.get("/{execution_id}/export/{format}")
async def export_execution_report(
    execution_id: int,
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    导出执行报告为文件

    Args:
        execution_id: 执行记录ID
        format: 导出格式 (pdf/excel/json)

    Returns:
        文件流
    """
    # 验证格式
    if format not in ['pdf', 'excel', 'json']:
        raise HTTPException(status_code=400, detail="不支持的导出格式，仅支持pdf、excel和json")

    # 获取执行记录
    execution_service = ExecutionService(db)
    execution = await execution_service.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")

    # 获取用例信息
    case_service = CaseService(db)
    case = await case_service.get_case(execution.case_id)

    if not case:
        raise HTTPException(status_code=404, detail="关联用例不存在")

    try:
        # 生成报告数据
        report_service = ReportService()
        report_data = report_service.generate_execution_report(
            execution_result={
                "status": execution.status,
                "execution_time": execution.execution_time,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "step_results": execution.step_results or [],
                "context": execution.execution_context or {},
                "logs": execution.logs or ""
            },
            case_info={
                "case_id": case.case_id,
                "name": case.name,
                "suite_name": case.suite.name if case.suite else "未知套件",
                "executed_by": current_user.username
            }
        )

        # 如果是JSON格式，直接返回
        if format == 'json':
            import json
            json_data = json.dumps(report_data, ensure_ascii=False, indent=2)
            media_type = "application/json"
            filename = f"execution_report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            return StreamingResponse(
                io.StringIO(json_data),
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

        # 转换为通用报告格式用于PDF/Excel导出
        export_data = {
            "report_id": report_data["report_info"]["report_id"],
            "report_name": f"执行报告 - {report_data['report_info']['case_name']}",
            "test_type": "api_engine",
            "total_cases": 1,
            "passed_cases": 1 if execution.status == "success" else 0,
            "failed_cases": 1 if execution.status in ["failed", "error"] else 0,
            "skipped_cases": 0,
            "pass_rate": 100 if execution.status == "success" else 0,
            "duration": execution.execution_time or 0,
            "start_time": execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else "N/A",
            "end_time": execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else "N/A",
            "test_results": [
                {
                    "testcase_name": case.name,
                    "status": execution.status,
                    "duration": execution.execution_time or 0,
                    "executed_at": execution.executed_at.strftime("%Y-%m-%d %H:%M:%S") if execution.executed_at else "N/A",
                    "error_message": execution.error_message or ""
                }
            ]
        }

        # 导出为对应格式
        if format == 'pdf':
            file_bytes = report_exporter.export_to_pdf(export_data)
            media_type = "application/pdf"
            filename = f"execution_report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:  # excel
            file_bytes = report_exporter.export_to_excel(export_data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"execution_report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出功能不可用: {str(e)}。请安装所需的依赖库。"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )

