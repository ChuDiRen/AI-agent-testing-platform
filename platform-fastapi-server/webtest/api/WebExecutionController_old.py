"""
Web执行Controller - 独立的Web测试执行管理功能
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

from ..schemas.WebExecutionSchema import (
    WebExecutionRequest, WebExecutionStopRequest, WebExecutionStatus,
    WebExecutionQuery, WebExecutionResponse, WebExecutionResultResponse,
    WebExecutionDetail, WebReportInfo
)
from ..service.WebExecutionService import WebExecutionService

module_route = APIRouter(prefix="/api/web/execution", tags=["Web执行管理"])
logger = get_logger(__name__)


@module_route.post("/run", summary="执行Web测试")
async def execute_web_test(
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
        return respModel.error_resp(f"执行失败: {e}")


@module_route.post("/stop", summary="停止执行")
async def stop_web_test(
    request: WebExecutionStopRequest,
    session: Session = Depends(get_session)
):
    """停止执行"""
    try:
        success = WebExecutionService.stop_execution(session, request.execution_id, request.force_stop)
        if success:
            return respModel.ok_resp(msg="执行已停止")
        else:
            return respModel.error_resp("执行不存在或已结束")
    except Exception as e:
        logger.error(f"停止执行失败: {e}", exc_info=True)
        return respModel.error_resp(f"停止失败: {e}")


@module_route.get("/status/{execution_id}", summary="获取执行状态")
async def get_execution_status(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取执行状态"""
    try:
        status = WebExecutionService.get_execution_status(session, execution_id)
        if status:
            return respModel.ok_resp(obj=status)
        else:
            return respModel.error_resp("执行记录不存在")
    except Exception as e:
        logger.error(f"获取执行状态失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.get("/history", summary="获取执行历史")
async def get_execution_history(
    project_id: Optional[int] = Query(None, description="项目ID"),
    execution_name: Optional[str] = Query(None, description="执行名称"),
    status: Optional[str] = Query(None, description="执行状态"),
    execution_type: Optional[str] = Query(None, description="执行类型"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(default=1, description="页码"),
    pageSize: int = Query(default=10, description="每页数量"),
    session: Session = Depends(get_session)
):
    """获取执行历史"""
    try:
        query = WebExecutionQuery(
            page=page,
            pageSize=pageSize,
            project_id=project_id,
            execution_name=execution_name,
            status=status,
            execution_type=execution_type,
            start_date=start_date,
            end_date=end_date
        )
        
        executions, total = WebExecutionService.query_executions_by_page(session, query)
        execution_responses = [WebExecutionResponse.from_orm(execution) for execution in executions]
        
        return respModel.ok_resp_list(lst=execution_responses, total=total)
    except Exception as e:
        logger.error(f"获取执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.get("/detail/{id}", summary="获取执行详情")
async def get_execution_detail(
    id: int = Path(..., description="执行记录ID"),
    session: Session = Depends(get_session)
):
    """获取执行详情"""
    try:
        detail = WebExecutionService.get_execution_detail(session, id)
        if detail:
            return respModel.ok_resp(obj=detail)
        else:
            return respModel.error_resp("执行记录不存在")
    except Exception as e:
        logger.error(f"获取执行详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.get("/report/{execution_id}", summary="获取报告链接")
async def get_report_url(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取报告链接"""
    try:
        report_info = WebExecutionService.get_report_info(session, execution_id)
        if report_info:
            return respModel.ok_resp(obj=report_info)
        else:
            return respModel.error_resp("报告不存在或未生成")
    except Exception as e:
        logger.error(f"获取报告链接失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.get("/results/{execution_id}", summary="获取执行结果")
async def get_execution_results(
    execution_id: str = Path(..., description="执行ID"),
    page: int = Query(default=1, description="页码"),
    pageSize: int = Query(default=10, description="每页数量"),
    session: Session = Depends(get_session)
):
    """获取执行结果"""
    try:
        results, total = WebExecutionService.get_execution_results(session, execution_id, page, pageSize)
        result_responses = [WebExecutionResultResponse.from_orm(result) for result in results]
        
        return respModel.ok_resp_list(lst=result_responses, total=total)
    except Exception as e:
        logger.error(f"获取执行结果失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.get("/statistics/{project_id}", summary="获取执行统计")
async def get_execution_statistics(
    project_id: int = Path(..., description="项目ID"),
    days: int = Query(default=30, description="统计天数"),
    session: Session = Depends(get_session)
):
    """获取执行统计"""
    try:
        statistics = WebExecutionService.get_execution_statistics(session, project_id, days)
        return respModel.ok_resp(obj=statistics)
    except Exception as e:
        logger.error(f"获取执行统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败: {e}")


@module_route.post("/retry/{execution_id}", summary="重试失败的用例")
async def retry_failed_cases(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """重试失败的用例"""
    try:
        new_execution_id = WebExecutionService.retry_failed_cases(session, execution_id)
        if new_execution_id:
            return respModel.ok_resp(obj={
                "new_execution_id": new_execution_id,
                "message": "重试执行已启动"
            }, msg="重试成功")
        else:
            return respModel.error_resp("原执行记录不存在或没有失败的用例")
    except Exception as e:
        logger.error(f"重试失败用例失败: {e}", exc_info=True)
        return respModel.error_resp(f"重试失败: {e}")


@module_route.post("/report/{execution_id}/generate", summary="生成执行报告")
async def generate_execution_report(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """生成执行报告"""
    try:
        report_path = WebExecutionService.generate_execution_report(session, execution_id)
        if report_path:
            return respModel.ok_resp(obj={
                "report_path": report_path,
                "report_url": f"/reports/web/{execution_id}/index.html"
            }, msg="报告生成成功")
        else:
            return respModel.error_resp("报告生成失败")
    except Exception as e:
        logger.error(f"生成执行报告失败: {e}", exc_info=True)
        return respModel.error_resp(f"生成失败: {e}")


@module_route.post("/result/update", summary="更新执行结果")
async def update_execution_result(
    execution_id: str = Query(..., description="执行ID"),
    case_id: int = Query(..., description="用例ID"),
    status: str = Query(..., description="状态"),
    error_message: Optional[str] = Query(None, description="错误信息"),
    screenshot_path: Optional[str] = Query(None, description="截图路径"),
    execution_time: Optional[float] = Query(None, description="执行时间"),
    session: Session = Depends(get_session)
):
    """更新执行结果"""
    try:
        success = WebExecutionService.update_execution_result(
            session, execution_id, case_id, status, error_message, 
            screenshot_path, execution_time
        )
        
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("更新失败")
    except Exception as e:
        logger.error(f"更新执行结果失败: {e}", exc_info=True)
        return respModel.error_resp(f"更新失败: {e}")


@module_route.post("/complete/{execution_id}", summary="完成执行")
async def complete_execution(
    execution_id: str = Path(..., description="执行ID"),
    success: bool = Query(default=True, description="是否成功"),
    error_message: Optional[str] = Query(None, description="错误信息"),
    session: Session = Depends(get_session)
):
    """完成执行"""
    try:
        success_flag = WebExecutionService.complete_execution(
            session, execution_id, success, error_message
        )
        
        if success_flag:
            return respModel.ok_resp(msg="执行完成")
        else:
            return respModel.error_resp("执行不存在")
    except Exception as e:
        logger.error(f"完成执行失败: {e}", exc_info=True)
        return respModel.error_resp(f"完成失败: {e}")


# 后台任务执行函数
async def run_web_test_background(execution_id: str, execution_data: WebExecutionRequest):
    """后台执行Web测试"""
    try:
        logger.info(f"开始执行Web测试，执行ID: {execution_id}")
        
        # 模拟执行过程
        import asyncio
        import random
        
        # 模拟初始化浏览器
        await asyncio.sleep(1)
        
        # 逐个执行测试用例
        with next(get_session()) as session:
            for i, case_id in enumerate(execution_data.case_ids):
                try:
                    # 模拟用例执行时间
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                    # 模拟测试结果
                    status_weights = ['passed'] * 7 + ['failed'] * 2 + ['error'] * 1  # 70%通过率
                    status = random.choice(status_weights)
                    error_message = None
                    screenshot_path = None
                    execution_time = random.uniform(1.0, 5.0)
                    
                    if status in ['failed', 'error']:
                        error_message = f"模拟错误信息 - 用例{case_id}执行失败"
                        screenshot_path = f"screenshots/{execution_id}/case_{case_id}_{int(datetime.now().timestamp())}.png"
                    
                    # 更新执行结果
                    WebExecutionService.update_execution_result(
                        session, execution_id, case_id, status, error_message, 
                        screenshot_path, execution_time
                    )
                    
                    logger.info(f"用例 {case_id} 执行完成，状态: {status}")
                    
                except Exception as e:
                    logger.error(f"执行用例 {case_id} 失败: {e}")
                    WebExecutionService.update_execution_result(
                        session, execution_id, case_id, 'error', str(e)
                    )
            
            # 完成执行
            WebExecutionService.complete_execution(session, execution_id, True)
            
            # 自动生成报告
            try:
                WebExecutionService.generate_execution_report(session, execution_id)
                logger.info(f"执行报告生成成功，执行ID: {execution_id}")
            except Exception as e:
                logger.error(f"生成执行报告失败: {e}")
        
        logger.info(f"Web测试执行完成，执行ID: {execution_id}")
        
    except Exception as e:
        logger.error(f"Web测试执行失败，执行ID: {execution_id}, 错误: {e}", exc_info=True)
        
        # 更新执行状态为失败
        try:
            with next(get_session()) as session:
                WebExecutionService.complete_execution(session, execution_id, False, str(e))
        except Exception as inner_e:
            logger.error(f"更新执行失败状态失败: {inner_e}")
