"""仪表板相关API"""
from fastapi import APIRouter, Depends
from typing import Dict, List, Any
from datetime import datetime, timedelta
import calendar

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取仪表板统计数据"""
    
    # 模拟数据 - 实际项目中应该从数据库查询
    stats = {
        "totalCases": 1248,
        "webCases": 456,
        "apiCases": 523,
        "appCases": 269
    }
    
    return {
        "code": 200,
        "message": "获取统计数据成功",
        "data": stats
    }


@router.get("/dashboard/trend")
async def get_trend_data(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取趋势图表数据"""
    
    # 生成最近12个月的时间线
    now = datetime.now()
    timeline = []
    web_data = []
    api_data = []
    app_data = []
    
    for i in range(11, -1, -1):
        # 计算月份
        target_date = now - timedelta(days=30 * i)
        month_name = calendar.month_abbr[target_date.month]
        timeline.append(f"{target_date.year}-{month_name}")
        
        # 模拟数据 - 实际项目中应该从数据库查询
        base_web = 30 + i * 5
        base_api = 40 + i * 6
        base_app = 20 + i * 3
        
        web_data.append(base_web + (i % 3) * 10)
        api_data.append(base_api + (i % 4) * 8)
        app_data.append(base_app + (i % 2) * 5)
    
    trend_data = {
        "timeline": timeline,
        "web": web_data,
        "api": api_data,
        "app": app_data
    }
    
    return {
        "code": 200,
        "message": "获取趋势数据成功",
        "data": trend_data
    }


@router.get("/dashboard/activities")
async def get_recent_activities(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取最近活动"""
    
    # 模拟数据 - 实际项目中应该从数据库查询
    activities = [
        {
            "id": 1,
            "user": "张三",
            "action": "创建了新的API测试用例",
            "target": "用户登录接口测试",
            "time": "2分钟前",
            "type": "create"
        },
        {
            "id": 2,
            "user": "李四",
            "action": "执行了WEB自动化测试",
            "target": "商品购买流程测试",
            "time": "5分钟前",
            "type": "execute"
        },
        {
            "id": 3,
            "user": "王五",
            "action": "更新了APP测试用例",
            "target": "用户注册流程测试",
            "time": "10分钟前",
            "type": "update"
        },
        {
            "id": 4,
            "user": "赵六",
            "action": "生成了测试报告",
            "target": "2024年第一季度测试报告",
            "time": "15分钟前",
            "type": "report"
        }
    ]
    
    return {
        "code": 200,
        "message": "获取活动数据成功",
        "data": activities
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取仪表板汇总信息"""
    
    # 模拟数据 - 实际项目中应该从数据库查询
    summary = {
        "todayExecutions": 45,
        "todaySuccess": 42,
        "todayFailed": 3,
        "successRate": 93.3,
        "avgExecutionTime": "2.5分钟",
        "activeUsers": 12,
        "totalProjects": 8,
        "pendingTasks": 23
    }
    
    return {
        "code": 200,
        "message": "获取汇总信息成功",
        "data": summary
    }
