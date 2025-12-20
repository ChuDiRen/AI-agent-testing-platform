"""
API测试统计图表Controller
实现需求文档中的统计功能：
- CHT-001 执行次数统计
- CHT-002 用例数量统计
- CHT-003 通过率统计
- CHT-004 执行趋势图
- CHT-005 耗时趋势图
- CHT-006 失败TOP5
"""
from datetime import datetime, timedelta

from apitest.service.api_statistics_service import StatisticsService
from core.database import get_session
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

module_name = "ApiStatistics"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试统计"])
logger = get_logger(__name__)


@module_route.get("/overview", summary="获取系统总览统计")
async def getOverview(session: Session = Depends(get_session)):
    """
    获取系统总览统计数据
    - 项目数量
    - 接口数量
    - 用例数量
    - 测试计划数量
    - 执行总次数
    - 成功率
    """
    try:
        service = StatisticsService(session)
        result = service.get_overview()
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/executionCount", summary="查询测试计划执行次数")
async def getExecutionCount(
    plan_id: int = Query(None, description="测试计划ID，不传则查询所有"),
    session: Session = Depends(get_session)
):
    """CHT-001 查询测试计划的执行次数"""
    try:
        service = StatisticsService(session)
        result = service.get_execution_count(plan_id)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询执行次数失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/caseCount", summary="查询用例数量统计")
async def getCaseCount(
    plan_id: int = Query(None, description="测试计划ID"),
    project_id: int = Query(None, description="项目ID"),
    session: Session = Depends(get_session)
):
    """CHT-002 查询最近一次执行的用例数量"""
    try:
        service = StatisticsService(session)
        result = service.get_case_count(plan_id, project_id)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询用例数量失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/passRate", summary="查询测试通过率")
async def getPassRate(
    plan_id: int = Query(None, description="测试计划ID"),
    days: int = Query(7, description="统计天数"),
    session: Session = Depends(get_session)
):
    """CHT-003 计算测试计划的通过率百分比"""
    try:
        service = StatisticsService(session)
        result = service.get_pass_rate(plan_id, days)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询通过率失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/executionTrend", summary="查询执行趋势图数据")
async def getExecutionTrend(
    plan_id: int = Query(None, description="测试计划ID"),
    limit: int = Query(5, description="查询最近N次执行"),
    session: Session = Depends(get_session)
):
    """CHT-004 查询最近5次执行结果趋势（passed/failed/broken/skipped）"""
    try:
        service = StatisticsService(session)
        result = service.get_execution_trend(plan_id, limit)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询执行趋势失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/timeTrend", summary="查询耗时趋势图数据")
async def getTimeTrend(
    plan_id: int = Query(None, description="测试计划ID"),
    limit: int = Query(10, description="查询最近N次执行"),
    session: Session = Depends(get_session)
):
    """CHT-005 查询最近10次执行耗时"""
    try:
        service = StatisticsService(session)
        result = service.get_time_trend(plan_id, limit)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询耗时趋势失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/failedTop5", summary="查询失败TOP5用例")
async def getFailedTop5(
    plan_id: int = Query(None, description="测试计划ID"),
    days: int = Query(30, description="统计天数"),
    session: Session = Depends(get_session)
):
    """CHT-006 查询失败次数最多的5个用例"""
    try:
        service = StatisticsService(session)
        result = service.get_failed_top5(plan_id, days)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询失败TOP5失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.get("/dailyStats", summary="查询每日统计数据")
async def getDailyStats(
    days: int = Query(7, description="统计天数"),
    session: Session = Depends(get_session)
):
    """查询最近N天的每日执行统计"""
    try:
        service = StatisticsService(session)
        result = service.get_daily_stats(days)
        return respModel.ok_resp(obj=result, msg="查询成功")
    except Exception as e:
        logger.error(f"查询每日统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")
