# Copyright (c) 2025 左岚. All rights reserved.
"""
审计日志Service
提供审计日志的业务逻辑处理
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.audit_log import AuditLog
from app.repository.audit_log_repository import AuditLogRepository
from app.service.base import BaseService

logger = get_logger(__name__)


class AuditLogService(BaseService):
    """
    审计日志Service
    提供审计日志的业务逻辑处理
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self.audit_log_repo = AuditLogRepository(db)
        self.logger = get_logger(self.__class__.__name__)
    
    def _create_entity_from_data(self, data: Dict[str, Any]) -> AuditLog:
        """
        从数据字典创建审计日志实体
        
        Args:
            data: 数据字典
            
        Returns:
            审计日志实体
        """
        return AuditLog(**data)

    def create_audit_log(
        self, user_id: Optional[int], username: Optional[str], operation_type: str,
        resource_type: str, resource_id: Optional[str] = None, resource_name: Optional[str] = None,
        operation_desc: str = "", request_method: Optional[str] = None,
        request_url: Optional[str] = None, request_params: Optional[Dict] = None,
        response_status: Optional[int] = None, response_message: Optional[str] = None,
        ip_address: Optional[str] = None, user_agent: Optional[str] = None,
        execution_time: Optional[int] = None, is_success: bool = True,
        error_message: Optional[str] = None, before_data: Optional[Dict] = None,
        after_data: Optional[Dict] = None
    ) -> Optional[AuditLog]:
        """
        创建审计日志
        
        Args:
            user_id: 操作用户ID
            username: 操作用户名
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            operation_desc: 操作描述
            request_method: 请求方法
            request_url: 请求URL
            request_params: 请求参数
            response_status: 响应状态码
            response_message: 响应消息
            ip_address: IP地址
            user_agent: 用户代理
            execution_time: 执行时间
            is_success: 是否成功
            error_message: 错误信息
            before_data: 操作前数据
            after_data: 操作后数据
            
        Returns:
            创建的审计日志对象
        """
        try:
            # 序列化复杂数据
            request_params_json = json.dumps(request_params, ensure_ascii=False) if request_params else None
            before_data_json = json.dumps(before_data, ensure_ascii=False) if before_data else None
            after_data_json = json.dumps(after_data, ensure_ascii=False) if after_data else None
            
            audit_log = self.audit_log_repo.create_audit_log(
                user_id=user_id,
                username=username,
                operation_type=operation_type,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                operation_desc=operation_desc,
                request_method=request_method,
                request_url=request_url,
                request_params=request_params_json,
                response_status=response_status,
                response_message=response_message,
                ip_address=ip_address,
                user_agent=user_agent,
                execution_time=execution_time,
                is_success=1 if is_success else 0,
                error_message=error_message,
                before_data=before_data_json,
                after_data=after_data_json
            )
            
            self.logger.debug(f"Created audit log: {operation_type} - {resource_type} by {username}")
            return audit_log
            
        except Exception as e:
            self.logger.error(f"Create audit log error: {str(e)}")
            return None

    def get_user_audit_logs(
        self, user_id: int, page: int = 1, size: int = 20
    ) -> tuple[List[Dict], int]:
        """
        获取用户审计日志
        
        Args:
            user_id: 用户ID
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            logs, total = self.audit_log_repo.get_audit_logs_by_user(user_id, page, size)
            
            log_dicts = []
            for log in logs:
                log_dict = log.to_dict()
                # 解析JSON字段
                if log_dict.get('request_params'):
                    try:
                        log_dict['request_params'] = json.loads(log_dict['request_params'])
                    except:
                        pass
                
                if log_dict.get('before_data'):
                    try:
                        log_dict['before_data'] = json.loads(log_dict['before_data'])
                    except:
                        pass
                
                if log_dict.get('after_data'):
                    try:
                        log_dict['after_data'] = json.loads(log_dict['after_data'])
                    except:
                        pass
                
                log_dicts.append(log_dict)
            
            return log_dicts, total
            
        except Exception as e:
            self.logger.error(f"Get user audit logs error: {str(e)}")
            return [], 0

    def search_audit_logs(
        self, filters: Dict[str, Any], page: int = 1, size: int = 20
    ) -> tuple[List[Dict], int]:
        """
        搜索审计日志
        
        Args:
            filters: 搜索条件
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            # 处理时间范围
            if filters.get('start_date') and filters.get('end_date'):
                try:
                    start_time = datetime.fromisoformat(filters['start_date'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(filters['end_date'].replace('Z', '+00:00'))
                    filters['start_time'] = start_time
                    filters['end_time'] = end_time
                except:
                    pass
            
            logs, total = self.audit_log_repo.search_audit_logs(filters, page, size)
            
            log_dicts = []
            for log in logs:
                log_dict = log.to_dict()
                # 解析JSON字段
                if log_dict.get('request_params'):
                    try:
                        log_dict['request_params'] = json.loads(log_dict['request_params'])
                    except:
                        pass
                
                if log_dict.get('before_data'):
                    try:
                        log_dict['before_data'] = json.loads(log_dict['before_data'])
                    except:
                        pass
                
                if log_dict.get('after_data'):
                    try:
                        log_dict['after_data'] = json.loads(log_dict['after_data'])
                    except:
                        pass
                
                log_dicts.append(log_dict)
            
            return log_dicts, total
            
        except Exception as e:
            self.logger.error(f"Search audit logs error: {str(e)}")
            return [], 0

    def get_operation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            return self.audit_log_repo.get_operation_statistics(days)
            
        except Exception as e:
            self.logger.error(f"Get operation statistics error: {str(e)}")
            return {}

    def get_security_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取安全告警信息
        
        Args:
            hours: 检查小时数
            
        Returns:
            安全告警列表
        """
        try:
            alerts = []
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # 查询失败的登录尝试
            failed_logins, _ = self.audit_log_repo.search_audit_logs({
                'operation_type': 'LOGIN',
                'is_success': 0,
                'start_time': start_time,
                'end_time': end_time
            }, page=1, size=100)
            
            if failed_logins:
                # 按IP地址分组统计失败次数
                ip_failures = {}
                for log in failed_logins:
                    ip = log.IP_ADDRESS
                    if ip:
                        ip_failures[ip] = ip_failures.get(ip, 0) + 1
                
                # 检查是否有异常IP
                for ip, count in ip_failures.items():
                    if count >= 5:  # 5次以上失败登录
                        alerts.append({
                            'type': 'SUSPICIOUS_LOGIN',
                            'level': 'HIGH' if count >= 10 else 'MEDIUM',
                            'message': f'IP {ip} 在过去{hours}小时内有{count}次失败登录尝试',
                            'ip_address': ip,
                            'count': count,
                            'time_range': f'{hours}小时'
                        })
            
            # 查询权限异常访问
            permission_denied, _ = self.audit_log_repo.search_audit_logs({
                'operation_type': 'ACCESS',
                'is_success': 0,
                'start_time': start_time,
                'end_time': end_time
            }, page=1, size=100)
            
            if permission_denied:
                # 按用户分组统计权限拒绝次数
                user_denials = {}
                for log in permission_denied:
                    username = log.username
                    if username:
                        user_denials[username] = user_denials.get(username, 0) + 1
                
                # 检查是否有异常用户
                for username, count in user_denials.items():
                    if count >= 10:  # 10次以上权限拒绝
                        alerts.append({
                            'type': 'PERMISSION_ABUSE',
                            'level': 'MEDIUM',
                            'message': f'用户 {username} 在过去{hours}小时内有{count}次权限拒绝',
                            'username': username,
                            'count': count,
                            'time_range': f'{hours}小时'
                        })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Get security alerts error: {str(e)}")
            return []

    def export_audit_logs(
        self, filters: Dict[str, Any], format: str = 'json'
    ) -> Optional[str]:
        """
        导出审计日志
        
        Args:
            filters: 过滤条件
            format: 导出格式 (json/csv)
            
        Returns:
            导出的数据字符串
        """
        try:
            # 获取所有匹配的日志（不分页）
            logs, _ = self.audit_log_repo.search_audit_logs(filters, page=1, size=10000)
            
            if format.lower() == 'json':
                log_dicts = [log.to_dict() for log in logs]
                return json.dumps(log_dicts, ensure_ascii=False, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                if logs:
                    fieldnames = logs[0].to_dict().keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for log in logs:
                        writer.writerow(log.to_dict())
                
                return output.getvalue()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Export audit logs error: {str(e)}")
            return None

    def cleanup_old_logs(self, days: int = 90) -> int:
        """
        清理旧的审计日志
        
        Args:
            days: 保留天数
            
        Returns:
            清理的记录数
        """
        try:
            return self.audit_log_repo.cleanup_old_logs(days)
            
        except Exception as e:
            self.logger.error(f"Cleanup old logs error: {str(e)}")
            return 0

    def log_user_operation(
        self, user_id: int, username: str, operation_type: str,
        resource_type: str, resource_id: str, resource_name: str,
        operation_desc: str, before_data: Optional[Dict] = None,
        after_data: Optional[Dict] = None, ip_address: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        记录用户操作日志（简化接口）
        
        Args:
            user_id: 用户ID
            username: 用户名
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            operation_desc: 操作描述
            before_data: 操作前数据
            after_data: 操作后数据
            ip_address: IP地址
            
        Returns:
            创建的审计日志对象
        """
        return self.create_audit_log(
            user_id=user_id,
            username=username,
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            operation_desc=operation_desc,
            response_status=200,
            is_success=True,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )

    def log_system_operation(
        self, operation_type: str, resource_type: str, operation_desc: str,
        is_success: bool = True, error_message: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        记录系统操作日志
        
        Args:
            operation_type: 操作类型
            resource_type: 资源类型
            operation_desc: 操作描述
            is_success: 是否成功
            error_message: 错误信息
            
        Returns:
            创建的审计日志对象
        """
        return self.create_audit_log(
            user_id=None,
            username="SYSTEM",
            operation_type=operation_type,
            resource_type=resource_type,
            operation_desc=operation_desc,
            response_status=200 if is_success else 500,
            is_success=is_success,
            error_message=error_message
        )

    async def log_user_access(
        self, user_id: int, username: str, ip_address: str,
        user_agent: str, endpoint: str, method: str
    ) -> Optional[AuditLog]:
        """
        记录用户访问日志

        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: IP地址
            user_agent: 用户代理
            endpoint: 访问端点
            method: 请求方法

        Returns:
            创建的审计日志对象
        """
        return self.create_audit_log(
            user_id=user_id,
            username=username,
            operation_type="ACCESS",
            resource_type="ENDPOINT",
            resource_id=endpoint,
            resource_name=endpoint,
            operation_desc=f"用户访问 {method} {endpoint}",
            request_method=method,
            request_url=endpoint,
            response_status=200,
            is_success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

    async def log_permission_check(
        self, user_id: int, username: str, permission: str,
        resource_type: str, result: str, ip_address: str, endpoint: str
    ) -> Optional[AuditLog]:
        """
        记录权限检查日志

        Args:
            user_id: 用户ID
            username: 用户名
            permission: 权限标识
            resource_type: 资源类型
            result: 检查结果 (GRANTED/DENIED)
            ip_address: IP地址
            endpoint: 访问端点

        Returns:
            创建的审计日志对象
        """
        is_success = result == "GRANTED"
        return self.create_audit_log(
            user_id=user_id,
            username=username,
            operation_type="PERMISSION_CHECK",
            resource_type=resource_type,
            resource_id=permission,
            resource_name=permission,
            operation_desc=f"权限检查: {permission} - {result}",
            request_url=endpoint,
            response_status=200 if is_success else 403,
            is_success=is_success,
            ip_address=ip_address,
            error_message=None if is_success else f"权限 {permission} 被拒绝"
        )