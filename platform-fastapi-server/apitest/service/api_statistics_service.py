"""
API统计Service
提供测试统计、图表数据、趋势分析等功能
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_, func

from apitest.model.ApiHistoryModel import ApiHistory
from apitest.model.ApiInfoCaseModel import ApiInfoCase
from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiProjectModel import ApiProject
from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo


class StatisticsService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_overview(self) -> Dict[str, Any]:
        """获取系统总览统计"""
        # 项目数量
        project_count = len(self.session.exec(select(ApiProject)).all())
        
        # 接口数量
        api_count = len(self.session.exec(select(ApiInfo)).all())
        
        # 用例数量
        case_count = len(self.session.exec(select(ApiInfoCase)).all())
        
        # 测试计划数量
        plan_count = len(self.session.exec(select(ApiCollectionInfo)).all())
        
        # 执行总次数
        history_all = self.session.exec(select(ApiHistory)).all()
        total_tests = len(history_all)
        
        # 计算成功率
        success_count = len([h for h in history_all if h.test_status in ['success', 'passed', 'completed']])
        success_rate = round(success_count / total_tests * 100, 1) if total_tests > 0 else 0
        
        # 计算平均执行时间
        response_times = [h.response_time for h in history_all if h.response_time]
        avg_time = round(sum(response_times) / len(response_times), 0) if response_times else 0
        
        return {
            "projectCount": project_count,
            "apiCount": api_count,
            "testcaseCount": case_count,
            "planCount": plan_count,
            "totalTests": total_tests,
            "successRate": success_rate,
            "avgTime": avg_time
        }
    
    def get_execution_count(self, plan_id: Optional[int] = None) -> Dict[str, int]:
        """查询测试计划执行次数"""
        statement = select(ApiHistory)
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        histories = self.session.exec(statement).all()
        
        return {
            "total_count": len(histories),
            "success_count": len([h for h in histories if h.test_status in ['success', 'passed', 'completed']]),
            "failed_count": len([h for h in histories if h.test_status in ['failed', 'error']]),
            "running_count": len([h for h in histories if h.test_status == 'running'])
        }
    
    def get_case_count(self, plan_id: Optional[int] = None, project_id: Optional[int] = None) -> Dict[str, Any]:
        """查询用例数量统计"""
        statement = select(ApiInfoCase)
        if project_id:
            statement = statement.where(ApiInfoCase.project_id == project_id)
        
        cases = self.session.exec(statement).all()
        
        # 如果指定了计划ID，查询最近一次执行结果
        last_execution = None
        if plan_id:
            history_stmt = select(ApiHistory).where(
                ApiHistory.plan_id == plan_id
            ).order_by(ApiHistory.create_time.desc()).limit(1)
            last_execution = self.session.exec(history_stmt).first()
        
        return {
            "total_cases": len(cases),
            "last_execution": {
                "test_name": last_execution.test_name if last_execution else None,
                "test_status": last_execution.test_status if last_execution else None,
                "create_time": last_execution.create_time.isoformat() if last_execution and last_execution.create_time else None
            } if last_execution else None
        }
    
    def get_pass_rate(self, plan_id: Optional[int] = None, days: int = 7) -> Dict[str, Any]:
        """计算测试通过率"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        histories = self.session.exec(statement).all()
        
        total = len(histories)
        passed = len([h for h in histories if h.test_status in ['success', 'passed', 'completed']])
        failed = len([h for h in histories if h.test_status in ['failed', 'error']])
        
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "period_days": days
        }
    
    def get_execution_trend(self, plan_id: Optional[int] = None, limit: int = 5) -> Dict[str, Any]:
        """查询执行趋势图数据"""
        statement = select(ApiHistory)
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        statement = statement.order_by(ApiHistory.create_time.desc()).limit(limit)
        
        histories = self.session.exec(statement).all()
        
        trend_data = []
        for history in reversed(histories):
            trend_data.append({
                "execution_id": history.id,
                "test_name": history.test_name,
                "status": history.test_status,
                "create_time": history.create_time.strftime("%m-%d %H:%M") if history.create_time else None,
                "response_time": history.response_time
            })
        
        return {
            "trend": trend_data,
            "total": len(trend_data)
        }
    
    def get_time_trend(self, plan_id: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
        """查询耗时趋势图数据"""
        statement = select(ApiHistory).where(
            ApiHistory.response_time != None
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        statement = statement.order_by(ApiHistory.create_time.desc()).limit(limit)
        
        histories = self.session.exec(statement).all()
        
        trend_data = []
        for history in reversed(histories):
            trend_data.append({
                "execution_id": history.id,
                "test_name": history.test_name,
                "response_time": history.response_time,
                "create_time": history.create_time.strftime("%m-%d %H:%M") if history.create_time else None
            })
        
        times = [h.response_time for h in histories if h.response_time]
        avg_time = round(sum(times) / len(times), 2) if times else 0
        max_time = max(times) if times else 0
        min_time = min(times) if times else 0
        
        return {
            "trend": trend_data,
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time
        }
    
    def get_failed_top5(self, plan_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """查询失败TOP5用例"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date,
            ApiHistory.test_status.in_(['failed', 'error'])
        )
        if plan_id:
            statement = statement.where(ApiHistory.plan_id == plan_id)
        
        failed_histories = self.session.exec(statement).all()
        
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
        
        top5 = sorted(failure_count.values(), key=lambda x: x["count"], reverse=True)[:5]
        
        return {
            "top5": top5,
            "period_days": days,
            "total_failures": len(failed_histories)
        }
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Any]:
        """查询每日统计数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        statement = select(ApiHistory).where(
            ApiHistory.create_time >= start_date
        ).order_by(ApiHistory.create_time)
        
        histories = self.session.exec(statement).all()
        
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
        
        result = sorted(daily_stats.values(), key=lambda x: x["date"])
        
        return {
            "daily_stats": result,
            "period_days": days
        }
