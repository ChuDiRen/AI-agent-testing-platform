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

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func

from ..model.ApiProjectModel import ApiProject
from ..model.ApiInfoModel import ApiInfo
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiHistoryModel import ApiHistory

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
        # 项目数量
        project_count = len(session.exec(select(ApiProject)).all())
        
        # 接口数量
        api_count = len(session.exec(select(ApiInfo)).all())
        
        # 用例数量
        case_count = len(session.exec(select(ApiInfoCase)).all())
        
        # 测试计划数量
        plan_count = len(session.exec(select(ApiCollectionInfo)).all())
        
        # 执行总次数
        history_all = session.exec(select(ApiHistory)).all()
        total_tests = len(history_all)
        
        # 计算成功率
        success_count = len([h for h in history_all if h.test_status in ['success', 'passed', 'completed']])
        success_rate = round(success_count / total_tests * 100, 1) if total_tests > 0 else 0
        
        # 计算平均执行时间
        response_times = [h.response_time for h in history_all if h.response_time]
        avg_time = round(sum(response_times) / len(response_times), 0) if response_times else 0
        
        result = {
            "projectCount": project_count,
            "apiCount": api_count,
            "testcaseCount": case_count,
            "planCount": plan_count,
            "totalTests": total_tests,
            "successRate": success_rate,
            "avgTime": avg_time
        }
        
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
        statement = select(ApiHistory)
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        histories = session.exec(statement).all()
        
        result = {
            "total_count": len(histories),
            "success_count": len([h for h in histories if h.test_status in ['success', 'passed', 'completed']]),
            "failed_count": len([h for h in histories if h.test_status in ['failed', 'error']]),
            "running_count": len([h for h in histories if h.test_status == 'running'])
        }
        
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
        # 查询用例
        statement = select(ApiInfoCase)
        if project_id:
            statement = statement.where(ApiInfoCase.project_id == project_id)
        
        cases = session.exec(statement).all()
        
        # 如果指定了计划ID，查询最近一次执行结果
        last_execution = None
        if plan_id:
            history_stmt = select(ApiHistory).where(
                ApiHistory.plan_id == plan_id
            ).order_by(ApiHistory.create_time.desc()).limit(1)
            last_execution = session.exec(history_stmt).first()
        
        result = {
            "total_cases": len(cases),
            "last_execution": {
                "test_name": last_execution.test_name if last_execution else None,
                "test_status": last_execution.test_status if last_execution else None,
                "create_time": last_execution.create_time.isoformat() if last_execution and last_execution.create_time else None
            } if last_execution else None
        }
        
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
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        histories = session.exec(statement).all()
        
        total = len(histories)
        passed = len([h for h in histories if h.test_status in ['success', 'passed', 'completed']])
        failed = len([h for h in histories if h.test_status in ['failed', 'error']])
        
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0
        
        result = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "period_days": days
        }
        
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
        statement = select(ApiHistory)
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        statement = statement.order_by(ApiHistory.create_time.desc()).limit(limit)
        
        histories = session.exec(statement).all()
        
        # 按执行UUID分组统计
        trend_data = []
        for history in reversed(histories):  # 按时间正序
            trend_data.append({
                "execution_id": history.id,
                "test_name": history.test_name,
                "status": history.test_status,
                "create_time": history.create_time.strftime("%m-%d %H:%M") if history.create_time else None,
                "response_time": history.response_time
            })
        
        return respModel.ok_resp(obj={
            "trend": trend_data,
            "total": len(trend_data)
        }, msg="查询成功")
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
        statement = select(ApiHistory).where(
            ApiHistory.response_time != None
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        statement = statement.order_by(ApiHistory.create_time.desc()).limit(limit)
        
        histories = session.exec(statement).all()
        
        trend_data = []
        for history in reversed(histories):
            trend_data.append({
                "execution_id": history.id,
                "test_name": history.test_name,
                "response_time": history.response_time,
                "create_time": history.create_time.strftime("%m-%d %H:%M") if history.create_time else None
            })
        
        # 计算平均耗时
        times = [h.response_time for h in histories if h.response_time]
        avg_time = round(sum(times) / len(times), 2) if times else 0
        max_time = max(times) if times else 0
        min_time = min(times) if times else 0
        
        return respModel.ok_resp(obj={
            "trend": trend_data,
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time
        }, msg="查询成功")
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
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询失败的历史记录
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date,
            ApiHistory.test_status.in_(['failed', 'error'])
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        failed_histories = session.exec(statement).all()
        
        # 按用例ID统计失败次数
        failure_count = {}
        for history in failed_histories:
            case_id = history.case_info_id or history.api_info_id
            if case_id:
                if case_id not in failure_count:
                    failure_count[case_id] = {
                        "case_id": case_id,
                        "test_name": history.test_name,
                        "count": 0,
                        "last_error": history.error_message
                    }
                failure_count[case_id]["count"] += 1
        
        # 排序取TOP5
        top5 = sorted(failure_count.values(), key=lambda x: x["count"], reverse=True)[:5]
        
        return respModel.ok_resp(obj={
            "top5": top5,
            "period_days": days,
            "total_failures": len(failed_histories)
        }, msg="查询成功")
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
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date
        ).order_by(ApiHistory.create_time)
        
        histories = session.exec(statement).all()
        
        # 按日期分组统计
        daily_stats = {}
        for history in histories:
            if history.create_time:
                date_key = history.create_time.strftime("%Y-%m-%d")
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        "date": date_key,
                        "total": 0,
                        "passed": 0,
                        "failed": 0
                    }
                daily_stats[date_key]["total"] += 1
                if history.test_status in ['success', 'passed', 'completed']:
                    daily_stats[date_key]["passed"] += 1
                elif history.test_status in ['failed', 'error']:
                    daily_stats[date_key]["failed"] += 1
        
        # 转换为列表并排序
        result = sorted(daily_stats.values(), key=lambda x: x["date"])
        
        return respModel.ok_resp(obj={
            "daily_stats": result,
            "period_days": days
        }, msg="查询成功")
    except Exception as e:
        logger.error(f"查询每日统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")
