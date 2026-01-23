"""
SQL执行智能体 - 安全执行SQL并处理结果
"""
import re
import time
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from app.config.settings import settings
from app.core.db_access import get_db_access
from app.models.schemas import ExecutionResult, ResponseMessage


class SQLExecutionHandler:
    """SQL执行处理器"""
    
    def __init__(self, max_rows: int = 1000, timeout: int = 30):
        self.max_rows = max_rows
        self.timeout = timeout
        self.execution_stats = ExecutionStats()
        self.security_validator = SQLSecurityValidator()
    
    async def execute_sql(self, sql: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行SQL语句并返回结果
        
        Args:
            sql: 要执行的SQL语句
            context: 执行上下文信息
        
        Returns:
            包含执行结果、统计信息和元数据的字典
        """
        execution_id = self._generate_execution_id()
        start_time = time.time()
        
        try:
            # 1. 安全验证
            security_result = await self._validate_sql_security(sql)
            if not security_result['safe']:
                return self._create_security_error_response(security_result, execution_id)
            
            # 2. SQL预处理
            processed_sql = await self._preprocess_sql(sql)
            
            # 3. 执行SQL
            execution_result = await self._execute_sql_with_monitoring(processed_sql, execution_id)
            
            # 4. 处理结果
            formatted_result = await self._process_execution_result(execution_result, execution_id)
            
            # 5. 记录统计信息
            execution_time = time.time() - start_time
            await self._record_execution_stats(execution_id, sql, execution_time, formatted_result)
            
            return {
                'success': True,
                'execution_id': execution_id,
                'data': formatted_result['data'],
                'metadata': formatted_result['metadata'],
                'execution_time': execution_time,
                'row_count': formatted_result['row_count'],
                'columns': formatted_result['columns']
            }
            
        except Exception as e:
            # 错误处理
            execution_time = time.time() - start_time
            error_response = await self._handle_execution_error(e, sql, execution_id, execution_time)
            return error_response
    
    async def _validate_sql_security(self, sql: str) -> Dict[str, Any]:
        """验证SQL安全性"""
        dangerous_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        sql_upper = sql.upper()
        
        for operation in dangerous_operations:
            if f'\\b{operation}\\b' in sql_upper:
                return {
                    'safe': False,
                    'reason': f'包含危险操作: {operation}',
                    'risk_level': 'HIGH'
                }
        
        # 检查SQL注入风险
        injection_patterns = [
            r"'.*OR.*'.*='.*'",  # OR注入
            r"'.*UNION.*SELECT",   # UNION注入
            r"--.*",             # 注释注入
            r"'.*DROP.*TABLE",    # DROP注入
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': '检测到潜在的SQL注入风险',
                    'risk_level': 'HIGH'
                }
        
        # 检查查询复杂度
        complexity_score = self._calculate_query_complexity(sql)
        if complexity_score > 10:
            return {
                'safe': False,
                'reason': '查询过于复杂，可能影响系统性能',
                'risk_level': 'MEDIUM'
            }
        
        # 检查结果集大小限制
        if 'LIMIT' not in sql_upper:
            return {
                'safe': True,
                'warning': '查询未包含LIMIT，将自动添加结果限制',
                'auto_limit': True
            }
        
        return {
            'safe': True,
            'risk_level': 'LOW'
        }
    
    async def _preprocess_sql(self, sql: str) -> str:
        """SQL预处理"""
        processed_sql = sql.strip()
        
        # 移除注释
        processed_sql = re.sub(r'--.*$', '', processed_sql, flags=re.MULTILINE)
        processed_sql = re.sub(r'/\*.*?\*/', '', processed_sql, flags=re.DOTALL)
        
        # 标准化空白字符
        processed_sql = re.sub(r'\s+', ' ', processed_sql)
        
        # 确保以分号结尾
        if not processed_sql.endswith(';'):
            processed_sql += ';'
        
        # 自动添加LIMIT（如果需要）
        if 'LIMIT' not in processed_sql.upper():
            processed_sql = processed_sql.rstrip(';') + f' LIMIT {self.max_rows};'
        
        return processed_sql
    
    async def _execute_sql_with_monitoring(self, sql: str, execution_id: str) -> Dict[str, Any]:
        """带监控的SQL执行"""
        start_time = time.time()
        
        try:
            # 设置超时
            async with asyncio.timeout(self.timeout):
                # 获取数据库访问实例
                db_access = get_db_access(settings.database_url, settings.database_type)
                
                # 执行查询
                result_df = db_access.run_sql(sql)
                
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'data': result_df,
                    'execution_time': execution_time,
                    'row_count': len(result_df) if result_df is not None else 0
                }
                
        except asyncio.TimeoutError:
            raise SQLExecutionTimeout(f"查询超时 (>{self.timeout}秒)")
        except Exception as e:
            execution_time = time.time() - start_time
            raise SQLExecutionError(f"SQL执行失败: {str(e)}", execution_time)
    
    async def _process_execution_result(self, execution_result: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """处理执行结果"""
        try:
            result_df = execution_result.get('data')
            
            if result_df is None or result_df.empty:
                return {
                    'data': [],
                    'metadata': {
                        'columns': [],
                        'data_types': {},
                        'total_rows': 0,
                        'execution_id': execution_id
                    },
                    'row_count': 0,
                    'columns': []
                }
            
            # 转换为JSON格式
            data_records = self._convert_dataframe_to_records(result_df)
            
            # 生成元数据
            metadata = {
                'columns': list(result_df.columns),
                'data_types': self._get_column_types(result_df),
                'total_rows': len(result_df),
                'execution_id': execution_id,
                'sample_data': data_records[:5] if len(data_records) > 5 else data_records
            }
            
            return {
                'data': data_records,
                'metadata': metadata,
                'row_count': len(result_df),
                'columns': list(result_df.columns)
            }
            
        except Exception as e:
            logger.error(f"结果处理失败: {str(e)}")
            raise ResultProcessingError(f"结果处理失败: {str(e)}")
    
    def _convert_dataframe_to_records(self, df) -> List[Dict[str, Any]]:
        """将DataFrame转换为记录列表"""
        try:
            df_processed = df.copy()
            
            # 处理日期时间类型
            for col in df_processed.columns:
                if df_processed[col].dtype == 'datetime64[ns]':
                    df_processed[col] = df_processed[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif df_processed[col].dtype == 'object':
                    df_processed[col] = df_processed[col].astype(str)
            
            # 处理NaN值
            df_processed = df_processed.fillna('')
            
            # 转换为记录
            records = df_processed.to_dict('records')
            
            return records
            
        except Exception as e:
            logger.error(f"DataFrame转换失败: {str(e)}")
            return [{'error': f'数据转换失败: {str(e)}'}]
    
    def _get_column_types(self, df) -> Dict[str, str]:
        """获取列的数据类型"""
        type_mapping = {
            'int64': 'integer',
            'float64': 'float',
            'object': 'string',
            'bool': 'boolean',
            'datetime64[ns]': 'datetime'
        }
        
        column_types = {}
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            column_types[col] = type_mapping.get(dtype_str, 'unknown')
        
        return column_types
    
    def _calculate_query_complexity(self, sql: str) -> int:
        """计算查询复杂度分数"""
        complexity_score = 0
        sql_upper = sql.upper()
        
        # 基础查询 +1
        complexity_score += 1
        
        # JOIN操作 +2 each
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))
        if join_count > 0:
            complexity_score += join_count * 2
        
        # GROUP BY +2
        if 'GROUP BY' in sql_upper:
            complexity_score += 2
        
        # ORDER BY +1
        if 'ORDER BY' in sql_upper:
            complexity_score += 1
        
        # 子查询 +3 each
        subquery_count = sql.count('(SELECT')
        if subquery_count > 0:
            complexity_score += subquery_count * 3
        
        return complexity_score
    
    def _generate_execution_id(self) -> str:
        """生成执行ID"""
        import uuid
        return f"exec_{uuid.uuid4().hex[:8]}"
    
    async def _record_execution_stats(self, execution_id: str, sql: str, 
                                     execution_time: float, result: Dict[str, Any]):
        """记录执行统计信息"""
        try:
            stats = {
                'execution_id': execution_id,
                'sql_hash': hashlib.md5(sql.encode()).hexdigest(),
                'execution_time': execution_time,
                'row_count': result.get('row_count', 0),
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
            self.execution_stats.record(stats)
            
        except Exception as e:
            logger.error(f"统计信息记录失败: {str(e)}")
    
    async def _handle_execution_error(self, error: Exception, sql: str, 
                                   execution_id: str, execution_time: float) -> Dict[str, Any]:
        """处理执行错误"""
        try:
            # 分类错误类型
            error_type = self._classify_error(error)
            
            # 生成错误建议
            suggestions = self._generate_error_suggestions(error, sql)
            
            # 记录错误统计
            await self._record_error_stats(execution_id, sql, error, execution_time)
            
            return {
                'success': False,
                'execution_id': execution_id,
                'error': {
                    'type': error_type,
                    'message': str(error),
                    'suggestions': suggestions
                },
                'execution_time': execution_time,
                'data': [],
                'metadata': {
                    'columns': [],
                    'total_rows': 0,
                    'error': True,
                    'execution_id': execution_id
                },
                'row_count': 0,
                'columns': []
            }
            
        except Exception as e:
            logger.error(f"错误处理失败: {str(e)}")
            return {
                'success': False,
                'execution_id': execution_id,
                'error': {
                    'type': 'UNKNOWN_ERROR',
                    'message': '执行过程中发生未知错误'
                },
                'execution_time': execution_time,
                'data': [],
                'row_count': 0,
                'columns': []
            }
    
    def _classify_error(self, error: Exception) -> str:
        """分类错误类型"""
        error_message = str(error).lower()
        
        if 'syntax' in error_message or 'parse' in error_message:
            return 'SYNTAX_ERROR'
        elif 'table' in error_message and 'not found' in error_message:
            return 'TABLE_NOT_FOUND'
        elif 'column' in error_message and 'not found' in error_message:
            return 'COLUMN_NOT_FOUND'
        elif 'timeout' in error_message:
            return 'TIMEOUT_ERROR'
        elif 'permission' in error_message or 'access' in error_message:
            return 'PERMISSION_ERROR'
        elif 'connection' in error_message:
            return 'CONNECTION_ERROR'
        else:
            return 'EXECUTION_ERROR'
    
    def _generate_error_suggestions(self, error: Exception, sql: str) -> list:
        """生成错误建议"""
        error_type = self._classify_error(error)
        suggestions = []
        
        if error_type == 'SYNTAX_ERROR':
            suggestions = [
                '请检查SQL语法是否正确',
                '确认所有括号、引号是否匹配',
                '检查关键字拼写是否正确'
            ]
        elif error_type == 'TABLE_NOT_FOUND':
            suggestions = [
                '请确认表名是否正确',
                '检查表是否存在于当前数据库中',
                '确认表名的大小写是否正确'
            ]
        elif error_type == 'COLUMN_NOT_FOUND':
            suggestions = [
                '请确认字段名是否正确',
                '检查字段是否存在于指定表中',
                '确认字段名的大小写是否正确'
            ]
        elif error_type == 'TIMEOUT_ERROR':
            suggestions = [
                '查询执行时间过长，请优化SQL语句',
                '考虑添加WHERE条件限制数据范围',
                '检查是否需要添加索引'
            ]
        elif error_type == 'PERMISSION_ERROR':
            suggestions = [
                '当前用户没有执行此操作的权限',
                '请联系管理员获取相应权限',
                '确认操作是否被系统策略允许'
            ]
        elif error_type == 'CONNECTION_ERROR':
            suggestions = [
                '请检查数据库连接是否正常',
                '确认数据库服务是否运行',
                '如问题持续存在，请联系技术支持'
            ]
        else:
            suggestions = [
                '请检查SQL语句是否正确',
                '确认数据库连接是否正常',
                '如问题持续存在，请联系技术支持'
            ]
        
        return suggestions
    
    async def _record_error_stats(self, execution_id: str, sql: str, 
                             error: Exception, execution_time: float):
        """记录错误统计"""
        try:
            error_stats = {
                'execution_id': execution_id,
                'sql_hash': hashlib.md5(sql.encode()).hexdigest(),
                'error_type': self._classify_error(error),
                'error_message': str(error),
                'execution_time': execution_time,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
            self.execution_stats.record_error(error_stats)
            
        except Exception as e:
            logger.error(f"错误统计记录失败: {str(e)}")
    
    def _create_security_error_response(self, security_result: Dict[str, Any], 
                                      execution_id: str) -> Dict[str, Any]:
        """创建安全错误响应"""
        return {
            'success': False,
            'execution_id': execution_id,
            'error': {
                'type': 'SECURITY_ERROR',
                'message': f"安全检查失败: {security_result.get('reason', '')}",
                'suggestions': [
                    '请检查SQL语句是否包含危险操作',
                    '确认查询意图是否正确',
                    '如有疑问请联系系统管理员'
                ]
            },
            'execution_time': 0,
            'data': [],
            'metadata': {
                'columns': [],
                'total_rows': 0,
                'security_blocked': True,
                'execution_id': execution_id
            },
            'row_count': 0,
            'columns': []
        }


class SQLSecurityValidator:
    """SQL安全验证器"""
    
    def __init__(self):
        self.dangerous_operations = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE'
        ]
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证SQL安全性"""
        sql_upper = sql.upper()
        
        for operation in self.dangerous_operations:
            if f'\\b{operation}\\b' in sql_upper:
                return {
                    'safe': False,
                    'reason': f'包含危险操作: {operation}',
                    'risk_level': 'HIGH'
                }
        
        return {
            'safe': True,
            'risk_level': 'LOW'
        }


class ExecutionStats:
    """执行统计信息管理"""
    
    def __init__(self):
        self.stats_history = []
        self.error_history = []
        self.max_history = 1000
    
    def record(self, stats: Dict[str, Any]):
        """记录执行统计"""
        self.stats_history.append(stats)
        if len(self.stats_history) > self.max_history:
            self.stats_history.pop(0)
    
    def record_error(self, error_stats: Dict[str, Any]):
        """记录错误统计"""
        self.error_history.append(error_stats)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.stats_history:
            return {
                'message': '暂无执行统计数据'
            }
        
        execution_times = [stat.get('execution_time', 0) for stat in self.stats_history]
        row_counts = [stat.get('row_count', 0) for stat in self.stats_history]
        
        return {
            'total_executions': len(self.stats_history),
            'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'max_execution_time': max(execution_times) if execution_times else 0,
            'min_execution_time': min(execution_times) if execution_times else 0,
            'avg_row_count': sum(row_counts) / len(row_counts) if row_counts else 0,
            'total_rows_processed': sum(row_counts) if row_counts else 0,
            'error_rate': len(self.error_history) / (len(self.stats_history) + len(self.error_history)) if (self.stats_history or self.error_history) else 0
        }


class SQLExecutionError(Exception):
    """SQL执行错误"""
    def __init__(self, message: str, execution_time: float = 0):
        super().__init__(message)
        self.execution_time = execution_time


class SQLExecutionTimeout(SQLExecutionError):
    """SQL执行超时错误"""
    pass


class ResultProcessingError(Exception):
    """结果处理错误"""
    pass


# 全局执行处理器实例
_sql_executor: Optional[SQLExecutionHandler] = None


def get_sql_executor(max_rows: int = 1000, timeout: int = 30) -> SQLExecutionHandler:
    """获取SQL执行处理器实例（单例模式）"""
    global _sql_executor
    
    if _sql_executor is None:
        _sql_executor = SQLExecutionHandler(max_rows, timeout)
    
    return _sql_executor
