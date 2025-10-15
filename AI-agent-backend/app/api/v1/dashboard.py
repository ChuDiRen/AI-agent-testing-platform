"""
Dashboard数据统计模块API
提供系统概览和统计数据
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.dashboard_service import DashboardService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.post("/get-statistics-data", summary="获取统计数据")
@log_user_action(action="查看", resource_type="Dashboard", description="获取Dashboard统计数据")
async def get_statistics_data(
    time_range: str = Body("7d", description="时间范围: 1d, 7d, 30d, 90d"),
    metrics: Optional[List[str]] = Body(None, description="指定指标列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Dashboard统计数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取统计数据
        statistics = await dashboard_service.get_comprehensive_statistics(
            time_range=time_range,
            metrics=metrics,
            user_id=current_user.id
        )

        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")


@router.post("/get-system-info", summary="获取系统信息")
@log_user_action(action="查看", resource_type="Dashboard", description="获取系统信息")
async def get_system_info(
    include_performance: bool = Body(True, description="包含性能信息"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统运行信息"""
    try:
        dashboard_service = DashboardService(db)

        # 获取系统信息
        system_info = await dashboard_service.get_system_info(
            include_performance=include_performance
        )

        return Success(data=system_info)

    except Exception as e:
        return Fail(msg=f"获取系统信息失败: {str(e)}")


@router.get("/overview", summary="获取系统概览")
@log_user_action(action="查看", resource_type="Dashboard", description="查看系统概览")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Dashboard概览数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取概览数据
        overview = await dashboard_service.get_dashboard_overview()

        return Success(data=overview)

    except Exception as e:
        return Fail(msg=f"获取概览数据失败: {str(e)}")


@router.get("/agents/statistics", summary="获取AI代理统计")
async def get_agent_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI代理相关统计数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取代理统计
        agent_stats = await dashboard_service.get_agent_statistics()

        return Success(data=agent_stats)

    except Exception as e:
        return Fail(msg=f"获取代理统计失败: {str(e)}")


@router.get("/test-cases/statistics", summary="获取测试用例统计")
async def get_test_case_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试用例相关统计数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取测试用例统计
        test_case_stats = await dashboard_service.get_test_case_statistics()

        return Success(data=test_case_stats)

    except Exception as e:
        return Fail(msg=f"获取测试用例统计失败: {str(e)}")


@router.get("/models/statistics", summary="获取AI模型统计")
async def get_model_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI模型相关统计数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取模型统计
        model_stats = await dashboard_service.get_model_statistics()

        return Success(data=model_stats)

    except Exception as e:
        return Fail(msg=f"获取模型统计失败: {str(e)}")


@router.get("/reports/statistics", summary="获取测试报告统计")
async def get_report_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试报告相关统计数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取报告统计
        report_stats = await dashboard_service.get_report_statistics()

        return Success(data=report_stats)

    except Exception as e:
        return Fail(msg=f"获取报告统计失败: {str(e)}")


@router.get("/activity/trends", summary="获取活动趋势")
async def get_activity_trends(
    time_range: str = Query("7d", description="时间范围"),
    metric_type: str = Query("all", description="指标类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统活动趋势数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取活动趋势
        trends = await dashboard_service.get_activity_trends(
            time_range=time_range,
            metric_type=metric_type
        )

        return Success(data=trends)

    except Exception as e:
        return Fail(msg=f"获取活动趋势失败: {str(e)}")


@router.get("/performance/metrics", summary="获取性能指标")
async def get_performance_metrics(
    time_range: str = Query("1d", description="时间范围"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统性能指标"""
    try:
        dashboard_service = DashboardService(db)

        # 获取性能指标
        performance = await dashboard_service.get_performance_metrics(
            time_range=time_range
        )

        return Success(data=performance)

    except Exception as e:
        return Fail(msg=f"获取性能指标失败: {str(e)}")


@router.get("/alerts", summary="获取系统告警")
async def get_system_alerts(
    severity: Optional[str] = Query(None, description="告警级别"),
    limit: int = Query(10, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统告警信息"""
    try:
        dashboard_service = DashboardService(db)

        # 获取告警信息
        alerts = await dashboard_service.get_system_alerts(
            severity=severity,
            limit=limit
        )

        return Success(data=alerts)

    except Exception as e:
        return Fail(msg=f"获取系统告警失败: {str(e)}")


@router.get("/recent-activities", summary="获取最近活动")
async def get_recent_activities(
    limit: int = Query(20, description="返回数量"),
    activity_type: Optional[str] = Query(None, description="活动类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近系统活动"""
    try:
        dashboard_service = DashboardService(db)

        # 获取最近活动
        activities = await dashboard_service.get_recent_activities(
            limit=limit,
            activity_type=activity_type,
            user_id=current_user.id
        )

        return Success(data=activities)

    except Exception as e:
        return Fail(msg=f"获取最近活动失败: {str(e)}")


@router.post("/custom-chart", summary="自定义图表数据")
@log_user_action(action="自定义图表", resource_type="Dashboard", description="获取自定义图表数据")
async def get_custom_chart_data(
    chart_type: str = Body(..., description="图表类型"),
    data_source: str = Body(..., description="数据源"),
    time_range: str = Body("7d", description="时间范围"),
    filters: Dict[str, Any] = Body(default={}, description="筛选条件"),
    group_by: Optional[str] = Body(None, description="分组字段"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取自定义图表数据"""
    try:
        dashboard_service = DashboardService(db)

        # 获取自定义图表数据
        chart_data = await dashboard_service.get_custom_chart_data(
            chart_type=chart_type,
            data_source=data_source,
            time_range=time_range,
            filters=filters,
            group_by=group_by
        )

        return Success(data=chart_data)

    except Exception as e:
        return Fail(msg=f"获取自定义图表数据失败: {str(e)}")


@router.get("/health-check", summary="系统健康检查")
async def system_health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """系统健康状态检查"""
    try:
        dashboard_service = DashboardService(db)

        # 执行健康检查
        health_status = await dashboard_service.perform_health_check()

        return Success(data=health_status)

    except Exception as e:
        return Fail(msg=f"健康检查失败: {str(e)}")


@router.get("/usage/summary", summary="使用情况汇总")
async def get_usage_summary(
    period: str = Query("monthly", description="汇总周期: daily, weekly, monthly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统使用情况汇总"""
    try:
        dashboard_service = DashboardService(db)

        # 获取使用情况汇总
        usage_summary = await dashboard_service.get_usage_summary(period=period)

        return Success(data=usage_summary)

    except Exception as e:
        return Fail(msg=f"获取使用情况汇总失败: {str(e)}")


@router.post("/export-report", summary="导出Dashboard报告")
@log_user_action(action="导出报告", resource_type="Dashboard", description="导出Dashboard报告")
async def export_dashboard_report(
    report_type: str = Body("overview", description="报告类型"),
    time_range: str = Body("30d", description="时间范围"),
    format: str = Body("pdf", description="导出格式"),
    include_charts: bool = Body(True, description="包含图表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出Dashboard报告"""
    try:
        dashboard_service = DashboardService(db)

        # 生成并导出报告
        report_data = await dashboard_service.generate_dashboard_report(
            report_type=report_type,
            time_range=time_range,
            format=format,
            include_charts=include_charts,
            user_id=current_user.id
        )

        return Success(data=report_data, msg="报告导出成功")

    except Exception as e:
        return Fail(msg=f"导出报告失败: {str(e)}")


@router.get("/real-time/metrics", summary="实时指标数据")
async def get_realtime_metrics(
    metrics: Optional[str] = Query(None, description="指标名称，多个用逗号分隔"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取实时指标数据（用于实时刷新）"""
    try:
        dashboard_service = DashboardService(db)

        # 解析指标列表
        metric_list = metrics.split(',') if metrics else None

        # 获取实时指标
        realtime_data = await dashboard_service.get_realtime_metrics(
            metrics=metric_list
        )

        return Success(data=realtime_data)

    except Exception as e:
        return Fail(msg=f"获取实时指标失败: {str(e)}")


@router.post("/notifications/mark-read", summary="标记通知为已读")
@log_user_action(action="标记通知", resource_type="Dashboard", description="标记通知为已读")
async def mark_notifications_read(
    notification_ids: List[int] = Body(..., description="通知ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记指定通知为已读"""
    try:
        dashboard_service = DashboardService(db)

        # 标记通知为已读
        success_count = await dashboard_service.mark_notifications_read(
            notification_ids=notification_ids,
            user_id=current_user.id
        )

        return Success(
            data={"success_count": success_count},
            msg=f"成功标记 {success_count} 个通知为已读"
        )

    except Exception as e:
        return Fail(msg=f"标记通知失败: {str(e)}")


@router.get("/notifications", summary="获取用户通知")
async def get_user_notifications(
    unread_only: bool = Query(False, description="只获取未读通知"),
    limit: int = Query(20, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户通知列表"""
    try:
        dashboard_service = DashboardService(db)

        # 获取通知列表
        notifications = await dashboard_service.get_user_notifications(
            user_id=current_user.id,
            unread_only=unread_only,
            limit=limit
        )

        return Success(data=notifications)

    except Exception as e:
        return Fail(msg=f"获取通知失败: {str(e)}")


@router.get("/widgets/config", summary="获取仪表板组件配置")
async def get_dashboard_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的仪表板组件配置"""
    try:
        dashboard_service = DashboardService(db)

        # 获取组件配置
        widgets_config = await dashboard_service.get_user_dashboard_config(
            user_id=current_user.id
        )

        return Success(data=widgets_config)

    except Exception as e:
        return Fail(msg=f"获取组件配置失败: {str(e)}")


@router.post("/widgets/config", summary="保存仪表板组件配置")
@log_user_action(action="保存配置", resource_type="Dashboard", description="保存仪表板组件配置")
async def save_dashboard_widgets(
    widgets_config: Dict[str, Any] = Body(..., description="组件配置"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存用户的仪表板组件配置"""
    try:
        dashboard_service = DashboardService(db)

        # 保存组件配置
        await dashboard_service.save_user_dashboard_config(
            user_id=current_user.id,
            widgets_config=widgets_config
        )

        return Success(msg="仪表板配置保存成功")

    except Exception as e:
        return Fail(msg=f"保存配置失败: {str(e)}")


@router.get("/comparison", summary="数据对比分析")
async def get_comparison_data(
    metric: str = Query(..., description="对比指标"),
    period1: str = Query(..., description="时间段1"),
    period2: str = Query(..., description="时间段2"),
    dimension: Optional[str] = Query(None, description="对比维度"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取数据对比分析"""
    try:
        dashboard_service = DashboardService(db)

        # 获取对比数据
        comparison_data = await dashboard_service.get_comparison_analysis(
            metric=metric,
            period1=period1,
            period2=period2,
            dimension=dimension
        )

        return Success(data=comparison_data)

    except Exception as e:
        return Fail(msg=f"获取对比数据失败: {str(e)}")
