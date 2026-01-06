"""
Web测试执行Controller - 按照ApiTest标准实现
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, BackgroundTasks
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..service.WebExecutionService import WebExecutionService
from ..schemas.WebExecutionSchema import (
    WebExecutionRequest, WebExecutionStopRequest, WebExecutionStatus,
    WebExecutionQuery, WebExecutionResponse, WebExecutionResultResponse,
    WebExecutionDetail, WebReportInfo
)

module_name = "WebExecution"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web执行管理"])
logger = get_logger(__name__)


@module_route.post("/run", summary="执行Web测试", dependencies=[Depends(check_permission("webtest:execution:run"))])
async def run(
    execution_data: WebExecutionRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """执行Web测试"""
    try:
        # 启动执行
        execution_id = WebExecutionService.start_execution(session, execution_data)
        
        # 添加后台任务来实际执行测试
        background_tasks.add_task(run_web_test_background, execution_id, execution_data)
        
        return respModel.ok_resp(obj={
            "execution_id": execution_id,
            "status": "running",
            "message": "测试执行已启动"
        }, msg="执行成功")
    except Exception as e:
        logger.error(f"执行Web测试失败: {e}", exc_info=True)
        return respModel.error_resp(f"执行失败:{e}")


@module_route.post("/stop", summary="停止执行", dependencies=[Depends(check_permission("webtest:execution:stop"))])
async def stop(
    stop_data: WebExecutionStopRequest,
    session: Session = Depends(get_session)
):
    """停止执行"""
    try:
        success = WebExecutionService.stop_execution(session, stop_data.execution_id)
        if success:
            return respModel.ok_resp(msg="停止成功")
        else:
            return respModel.error_resp("执行不存在或已停止")
    except Exception as e:
        logger.error(f"停止执行失败: {e}", exc_info=True)
        return respModel.error_resp(f"停止失败:{e}")


@module_route.get("/status/{execution_id}", summary="获取执行状态", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def getStatus(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取执行状态"""
    try:
        status = WebExecutionService.get_execution_status(session, execution_id)
        if status:
            return respModel.ok_resp(obj=status)
        else:
            return respModel.error_resp("执行不存在")
    except Exception as e:
        logger.error(f"获取执行状态失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败:{e}")


@module_route.post("/queryByPage", summary="分页查询执行记录", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def queryByPage(
    query: WebExecutionQuery,
    session: Session = Depends(get_session)
):
    """分页查询执行记录"""
    try:
        executions, total = WebExecutionService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=executions, total=total)
    except Exception as e:
        logger.error(f"分页查询执行记录失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/queryById", summary="查询执行详情", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def queryById(
    execution_id: str = Query(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """查询执行详情"""
    try:
        execution = WebExecutionService.query_by_id(session, execution_id)
        if execution:
            return respModel.ok_resp(obj=execution)
        else:
            return respModel.error_resp("执行不存在")
    except Exception as e:
        logger.error(f"查询执行详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/getResults/{execution_id}", summary="获取执行结果", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def getResults(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取执行结果"""
    try:
        results = WebExecutionService.get_execution_results(session, execution_id)
        if results:
            return respModel.ok_resp(obj=results)
        else:
            return respModel.error_resp("执行结果不存在")
    except Exception as e:
        logger.error(f"获取执行结果失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败:{e}")


@module_route.get("/getReport/{execution_id}", summary="获取报告信息", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def getReport(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取报告信息"""
    try:
        report_info = WebExecutionService.get_report_info(session, execution_id)
        if report_info:
            return respModel.ok_resp(obj=report_info)
        else:
            return respModel.error_resp("报告信息不存在")
    except Exception as e:
        logger.error(f"获取报告信息失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败:{e}")


@module_route.delete("/delete", summary="删除执行记录", dependencies=[Depends(check_permission("webtest:execution:delete"))])
async def delete(
    execution_id: str = Query(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """删除执行记录"""
    try:
        success = WebExecutionService.delete_execution(session, execution_id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("执行记录不存在")
    except Exception as e:
        logger.error(f"删除执行记录失败: {e}", exc_info=True)
        return respModel.error_resp(f"删除失败:{e}")


@module_route.delete("/batchDelete", summary="批量删除执行记录", dependencies=[Depends(check_permission("webtest:execution:delete"))])
async def batchDelete(
    execution_ids: List[str],
    session: Session = Depends(get_session)
):
    """批量删除执行记录"""
    try:
        deleted_count = WebExecutionService.batch_delete_executions(session, execution_ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}条记录")
        else:
            return respModel.error_resp("没有找到要删除的记录")
    except Exception as e:
        logger.error(f"批量删除执行记录失败: {e}", exc_info=True)
        return respModel.error_resp(f"批量删除失败:{e}")


@module_route.get("/getStatistics", summary="获取执行统计", dependencies=[Depends(check_permission("webtest:execution:query"))])
async def getStatistics(
    project_id: int = Query(None, description="项目ID"),
    days: int = Query(default=7, description="统计天数"),
    session: Session = Depends(get_session)
):
    """获取执行统计信息"""
    try:
        stats = WebExecutionService.get_statistics(session, project_id, days)
        return respModel.ok_resp(obj=stats)
    except Exception as e:
        logger.error(f"获取执行统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败:{e}")


# 后台任务函数
async def run_web_test_background(execution_id: str, execution_data: WebExecutionRequest):
    """后台执行Web测试任务"""
    try:
        from core.database import get_session
        
        with get_session() as session:
            # 更新状态为运行中
            WebExecutionService.update_execution_status(session, execution_id, "running")
            
            # 模拟执行过程
            import asyncio
            await asyncio.sleep(2)  # 模拟执行时间
            
            # 更新状态为完成
            WebExecutionService.update_execution_status(session, execution_id, "completed")
            
            logger.info(f"后台任务执行完成: {execution_id}")
    except Exception as e:
        logger.error(f"后台任务执行失败: {e}", exc_info=True)
        
        # 更新状态为失败
        try:
            from core.database import get_session
            with get_session() as session:
                WebExecutionService.update_execution_status(session, execution_id, "failed")
        except:
            pass
