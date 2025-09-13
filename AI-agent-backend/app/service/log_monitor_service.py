# Copyright (c) 2025 左岚. All rights reserved.
"""
日志监控服务
提供实时日志监控和告警功能
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.core.logger import get_logger
from app.db.session import SessionLocal
from app.entity.system_log import SystemLog
from app.entity.audit_log import AuditLog
from app.service.audit_log_service import AuditLogService

logger = get_logger(__name__)


class LogMonitorService:
    """
    日志监控服务类
    提供实时监控、告警检测和统计分析功能
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditLogService(db)
        self.logger = get_logger(self.__class__.__name__)
    
    def get_real_time_stats(self, minutes: int = 5) -> Dict[str, Any]:
        """
        获取实时日志统计
        
        Args:
            minutes: 统计时间范围（分钟）
            
        Returns:
            实时统计数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=minutes)
            
            # 系统日志统计
            system_stats = self._get_system_log_stats(start_time, end_time)
            
            # 审计日志统计
            audit_stats = self._get_audit_log_stats(start_time, end_time)
            
            # 错误率统计
            error_rate = self._calculate_error_rate(start_time, end_time)
            
            # 活跃用户统计
            active_users = self._get_active_users(start_time, end_time)
            
            return {
                "time_range": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "minutes": minutes
                },
                "system_logs": system_stats,
                "audit_logs": audit_stats,
                "error_rate": error_rate,
                "active_users": active_users,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取实时统计失败: {str(e)}")
            return {}
    
    def _get_system_log_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """获取系统日志统计"""
        try:
            # 总数统计
            total_count = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time
                )
            ).scalar() or 0
            
            # 按级别统计
            level_stats = self.db.query(
                SystemLog.level,
                func.count(SystemLog.id).label('count')
            ).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time
                )
            ).group_by(SystemLog.level).all()
            
            level_counts = {level: count for level, count in level_stats}
            
            # 按模块统计
            module_stats = self.db.query(
                SystemLog.module,
                func.count(SystemLog.id).label('count')
            ).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time
                )
            ).group_by(SystemLog.module).order_by(desc('count')).limit(10).all()
            
            return {
                "total_count": total_count,
                "level_stats": level_counts,
                "top_modules": [{"module": module, "count": count} for module, count in module_stats]
            }
            
        except Exception as e:
            self.logger.error(f"获取系统日志统计失败: {str(e)}")
            return {}
    
    def _get_audit_log_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """获取审计日志统计"""
        try:
            # 总数统计
            total_count = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).scalar() or 0
            
            # 成功失败统计
            success_count = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.IS_SUCCESS == 1,
                    AuditLog.is_deleted == 0
                )
            ).scalar() or 0
            
            failed_count = total_count - success_count
            
            # 按操作类型统计
            operation_stats = self.db.query(
                AuditLog.OPERATION_TYPE,
                func.count(AuditLog.LOG_ID).label('count')
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).group_by(AuditLog.OPERATION_TYPE).order_by(desc('count')).limit(10).all()
            
            return {
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": round((success_count / total_count * 100), 2) if total_count > 0 else 0,
                "top_operations": [{"operation": op, "count": count} for op, count in operation_stats]
            }
            
        except Exception as e:
            self.logger.error(f"获取审计日志统计失败: {str(e)}")
            return {}
    
    def _calculate_error_rate(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """计算错误率"""
        try:
            # 系统日志错误率
            total_system_logs = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time
                )
            ).scalar() or 0
            
            error_system_logs = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time,
                    SystemLog.level.in_(['ERROR', 'CRITICAL'])
                )
            ).scalar() or 0
            
            # 审计日志错误率
            total_audit_logs = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).scalar() or 0
            
            failed_audit_logs = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.IS_SUCCESS == 0,
                    AuditLog.is_deleted == 0
                )
            ).scalar() or 0
            
            return {
                "system_error_rate": round((error_system_logs / total_system_logs * 100), 2) if total_system_logs > 0 else 0,
                "audit_error_rate": round((failed_audit_logs / total_audit_logs * 100), 2) if total_audit_logs > 0 else 0,
                "total_errors": error_system_logs + failed_audit_logs
            }
            
        except Exception as e:
            self.logger.error(f"计算错误率失败: {str(e)}")
            return {}
    
    def _get_active_users(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """获取活跃用户统计"""
        try:
            # 活跃用户数
            active_users_count = self.db.query(func.count(func.distinct(AuditLog.USER_ID))).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.USER_ID.isnot(None),
                    AuditLog.is_deleted == 0
                )
            ).scalar() or 0
            
            # 最活跃用户
            top_users = self.db.query(
                AuditLog.username,
                func.count(AuditLog.LOG_ID).label('operation_count')
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.username.isnot(None),
                    AuditLog.is_deleted == 0
                )
            ).group_by(AuditLog.username).order_by(desc('operation_count')).limit(5).all()
            
            return {
                "active_users_count": active_users_count,
                "top_users": [{"username": username, "operations": count} for username, count in top_users]
            }
            
        except Exception as e:
            self.logger.error(f"获取活跃用户统计失败: {str(e)}")
            return {}
    
    def check_alerts(self, check_hours: int = 1) -> List[Dict[str, Any]]:
        """
        检查告警条件
        
        Args:
            check_hours: 检查时间范围（小时）
            
        Returns:
            告警列表
        """
        try:
            alerts = []
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=check_hours)
            
            # 检查错误率告警
            error_alerts = self._check_error_rate_alerts(start_time, end_time)
            alerts.extend(error_alerts)
            
            # 检查安全告警
            security_alerts = self.audit_service.get_security_alerts(check_hours)
            alerts.extend(security_alerts)
            
            # 检查系统异常告警
            system_alerts = self._check_system_alerts(start_time, end_time)
            alerts.extend(system_alerts)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"检查告警失败: {str(e)}")
            return []
    
    def _check_error_rate_alerts(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """检查错误率告警"""
        alerts = []
        
        try:
            error_rate_data = self._calculate_error_rate(start_time, end_time)
            
            # 系统错误率告警阈值：10%
            if error_rate_data.get("system_error_rate", 0) > 10:
                alerts.append({
                    "type": "HIGH_ERROR_RATE",
                    "level": "HIGH",
                    "message": f"系统错误率过高: {error_rate_data['system_error_rate']}%",
                    "details": error_rate_data,
                    "time_range": f"{(end_time - start_time).total_seconds() / 3600:.1f}小时"
                })
            
            # 审计错误率告警阈值：15%
            if error_rate_data.get("audit_error_rate", 0) > 15:
                alerts.append({
                    "type": "HIGH_AUDIT_ERROR_RATE",
                    "level": "MEDIUM",
                    "message": f"操作失败率过高: {error_rate_data['audit_error_rate']}%",
                    "details": error_rate_data,
                    "time_range": f"{(end_time - start_time).total_seconds() / 3600:.1f}小时"
                })
            
        except Exception as e:
            self.logger.error(f"检查错误率告警失败: {str(e)}")
        
        return alerts
    
    def _check_system_alerts(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """检查系统异常告警"""
        alerts = []
        
        try:
            # 检查CRITICAL级别日志
            critical_count = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time,
                    SystemLog.level == 'CRITICAL'
                )
            ).scalar() or 0
            
            if critical_count > 0:
                alerts.append({
                    "type": "CRITICAL_ERRORS",
                    "level": "CRITICAL",
                    "message": f"发现{critical_count}条严重错误日志",
                    "count": critical_count,
                    "time_range": f"{(end_time - start_time).total_seconds() / 3600:.1f}小时"
                })
            
            # 检查频繁错误
            error_count = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time,
                    SystemLog.level == 'ERROR'
                )
            ).scalar() or 0
            
            # 错误数量阈值：每小时超过50条
            hours = (end_time - start_time).total_seconds() / 3600
            if error_count > 50 * hours:
                alerts.append({
                    "type": "FREQUENT_ERRORS",
                    "level": "HIGH",
                    "message": f"错误日志频繁，{hours:.1f}小时内发生{error_count}条错误",
                    "count": error_count,
                    "time_range": f"{hours:.1f}小时"
                })
            
        except Exception as e:
            self.logger.error(f"检查系统告警失败: {str(e)}")
        
        return alerts
    
    def get_log_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        获取日志趋势分析
        
        Args:
            days: 分析天数
            
        Returns:
            趋势分析数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # 按天统计系统日志
            daily_system_logs = self._get_daily_system_log_trends(start_time, end_time)
            
            # 按天统计审计日志
            daily_audit_logs = self._get_daily_audit_log_trends(start_time, end_time)
            
            # 错误趋势
            error_trends = self._get_error_trends(start_time, end_time)
            
            return {
                "time_range": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "days": days
                },
                "daily_system_logs": daily_system_logs,
                "daily_audit_logs": daily_audit_logs,
                "error_trends": error_trends
            }
            
        except Exception as e:
            self.logger.error(f"获取日志趋势失败: {str(e)}")
            return {}
    
    def _get_daily_system_log_trends(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """获取每日系统日志趋势"""
        try:
            # 按日期分组统计
            daily_stats = self.db.query(
                func.date(SystemLog.timestamp).label('date'),
                SystemLog.level,
                func.count(SystemLog.id).label('count')
            ).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time
                )
            ).group_by(func.date(SystemLog.timestamp), SystemLog.level).all()
            
            # 组织数据
            trends = {}
            for date, level, count in daily_stats:
                date_str = date.strftime('%Y-%m-%d')
                if date_str not in trends:
                    trends[date_str] = {"date": date_str, "total": 0}
                trends[date_str][level.lower()] = count
                trends[date_str]["total"] += count
            
            return list(trends.values())
            
        except Exception as e:
            self.logger.error(f"获取每日系统日志趋势失败: {str(e)}")
            return []
    
    def _get_daily_audit_log_trends(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """获取每日审计日志趋势"""
        try:
            # 按日期分组统计
            daily_stats = self.db.query(
                func.date(AuditLog.OPERATION_TIME).label('date'),
                func.count(AuditLog.LOG_ID).label('total'),
                func.sum(AuditLog.IS_SUCCESS).label('success')
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).group_by(func.date(AuditLog.OPERATION_TIME)).all()
            
            trends = []
            for date, total, success in daily_stats:
                failed = total - (success or 0)
                trends.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "total": total,
                    "success": success or 0,
                    "failed": failed,
                    "success_rate": round((success / total * 100), 2) if total > 0 else 0
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"获取每日审计日志趋势失败: {str(e)}")
            return []
    
    def _get_error_trends(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """获取错误趋势"""
        try:
            # 按日期统计错误
            error_stats = self.db.query(
                func.date(SystemLog.timestamp).label('date'),
                func.count(SystemLog.id).label('error_count')
            ).filter(
                and_(
                    SystemLog.timestamp >= start_time,
                    SystemLog.timestamp <= end_time,
                    SystemLog.level.in_(['ERROR', 'CRITICAL'])
                )
            ).group_by(func.date(SystemLog.timestamp)).all()
            
            trends = []
            for date, error_count in error_stats:
                trends.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "error_count": error_count
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"获取错误趋势失败: {str(e)}")
            return []


# 导出服务类
__all__ = ["LogMonitorService"]
