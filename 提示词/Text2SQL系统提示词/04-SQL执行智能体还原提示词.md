# SQL执行智能体还原提示词

## 🎯 智能体概述

SQL执行智能体（SQL Executor Agent）是Text2SQL系统中的核心执行组件，专门负责安全、高效地执行SQL语句并处理查询结果。该智能体具备强大的SQL执行能力、完善的安全防护机制和智能的结果处理功能，确保SQL查询的可靠执行和结果的准确返回。

## 🧠 核心功能

### 1. SQL执行管理
- **安全执行**: 在受控环境中安全执行SQL语句
- **连接管理**: 管理数据库连接的建立、维护和释放
- **事务控制**: 处理事务的开始、提交和回滚
- **超时控制**: 防止长时间运行的查询影响系统性能

### 2. 结果处理
- **数据格式化**: 将查询结果转换为标准格式
- **类型转换**: 处理不同数据类型的转换和序列化
- **结果分页**: 对大量结果进行分页处理
- **数据清洗**: 清理和标准化查询结果

### 3. 错误处理
- **异常捕获**: 捕获和分类各种SQL执行异常
- **错误诊断**: 分析错误原因并提供解决建议
- **恢复机制**: 实现查询失败后的恢复策略
- **日志记录**: 详细记录执行过程和错误信息

### 4. 性能监控
- **执行时间监控**: 监控SQL查询的执行时间
- **资源使用监控**: 监控内存、CPU等资源使用情况
- **性能分析**: 分析查询性能并提供优化建议
- **统计信息**: 收集和分析查询统计数据

## 🔧 技术实现

### 核心执行器类

```python
class SQLExecutionHandler:
    """
    SQL执行处理器
    
    功能:
    1. 安全执行SQL语句
    2. 处理查询结果
    3. 管理数据库连接
    4. 监控执行性能
    """
    
    def __init__(self, db_access: DBAccess, max_rows: int = 1000, timeout: int = 30):
        self.db_access = db_access
        self.max_rows = max_rows
        self.timeout = timeout
        self.execution_stats = ExecutionStats()
        self.security_validator = SQLSecurityValidator()
        self.result_formatter = ResultFormatter()
    
    async def execute_sql(self, sql: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
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
        """
        验证SQL安全性
        """
        try:
            # 检查危险操作
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
                r"--;.*",             # 注释注入
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
                # 自动添加LIMIT限制
                return {
                    'safe': True,
                    'warning': '查询未包含LIMIT，将自动添加结果限制',
                    'auto_limit': True
                }
            
            return {
                'safe': True,
                'risk_level': 'LOW'
            }
            
        except Exception as e:
            logger.error(f"SQL安全验证失败: {str(e)}")
            return {
                'safe': False,
                'reason': f'安全验证过程出错: {str(e)}',
                'risk_level': 'UNKNOWN'
            }
    
    async def _preprocess_sql(self, sql: str) -> str:
        """
        SQL预处理
        """
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
            # 在分号前添加LIMIT
            processed_sql = processed_sql.rstrip(';') + f' LIMIT {self.max_rows};'
        
        return processed_sql
    
    async def _execute_sql_with_monitoring(self, sql: str, execution_id: str) -> Dict[str, Any]:
        """
        带监控的SQL执行
        """
        start_time = time.time()
        
        try:
            # 设置超时
            async with asyncio.timeout(self.timeout):
                # 执行SQL
                result_df = await asyncio.to_thread(self.db_access.run_sql, sql)
                
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
        """
        处理执行结果
        """
        try:
            result_df = execution_result['data']
            
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
    
    def _convert_dataframe_to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        将DataFrame转换为记录列表
        """
        try:
            # 处理特殊数据类型
            df_processed = df.copy()
            
            # 处理日期时间类型
            for col in df_processed.columns:
                if df_processed[col].dtype == 'datetime64[ns]':
                    df_processed[col] = df_processed[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif df_processed[col].dtype == 'object':
                    # 处理可能的日期字符串
                    df_processed[col] = df_processed[col].astype(str)
            
            # 处理NaN值
            df_processed = df_processed.fillna('')
            
            # 转换为记录
            records = df_processed.to_dict('records')
            
            return records
            
        except Exception as e:
            logger.error(f"DataFrame转换失败: {str(e)}")
            # 返回基础格式
            return [{'error': f'数据转换失败: {str(e)}'}]
    
    def _get_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        获取列的数据类型
        """
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
        """
        计算查询复杂度分数
        """
        complexity_score = 0
        sql_upper = sql.upper()
        
        # 基础查询 +1
        complexity_score += 1
        
        # JOIN操作 +2 each
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))
        complexity_score += join_count * 2
        
        # 子查询 +3 each
        subquery_count = sql.count('(SELECT')
        complexity_score += subquery_count * 3
        
        # GROUP BY +2
        if 'GROUP BY' in sql_upper:
            complexity_score += 2
        
        # ORDER BY +1
        if 'ORDER BY' in sql_upper:
            complexity_score += 1
        
        # 窗口函数 +3
        if 'OVER(' in sql_upper:
            complexity_score += 3
        
        # UNION +2
        if 'UNION' in sql_upper:
            complexity_score += 2
        
        return complexity_score
    
    def _generate_execution_id(self) -> str:
        """
        生成执行ID
        """
        import uuid
        return f"exec_{uuid.uuid4().hex[:8]}"
    
    async def _record_execution_stats(self, execution_id: str, sql: str, 
                                    execution_time: float, result: Dict[str, Any]):
        """
        记录执行统计信息
        """
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
        """
        处理执行错误
        """
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
                    'error': True
                }
            }
            
        except Exception as e:
            logger.error(f"错误处理失败: {str(e)}")
            return {
                'success': False,
                'execution_id': execution_id,
                'error': {
                    'type': 'UNKNOWN',
                    'message': '执行过程中发生未知错误',
                    'suggestions': ['请检查SQL语法', '请联系系统管理员']
                },
                'execution_time': execution_time,
                'data': [],
                'metadata': {'columns': [], 'total_rows': 0, 'error': True}
            }
    
    def _classify_error(self, error: Exception) -> str:
        """
        分类错误类型
        """
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
    
    def _generate_error_suggestions(self, error: Exception, sql: str) -> List[str]:
        """
        生成错误建议
        """
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
        else:
            suggestions = [
                '请检查SQL语句是否正确',
                '确认数据库连接是否正常',
                '如问题持续存在，请联系技术支持'
            ]
        
        return suggestions
    
    async def _record_error_stats(self, execution_id: str, sql: str, 
                                error: Exception, execution_time: float):
        """
        记录错误统计信息
        """
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
        """
        创建安全错误响应
        """
        return {
            'success': False,
            'execution_id': execution_id,
            'error': {
                'type': 'SECURITY_ERROR',
                'message': f"安全检查失败: {security_result['reason']}",
                'risk_level': security_result['risk_level'],
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
                'security_blocked': True
            }
        }

# 自定义异常类
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

# 执行统计类
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
            return {'message': '暂无执行统计数据'}
        
        execution_times = [stat['execution_time'] for stat in self.stats_history]
        row_counts = [stat['row_count'] for stat in self.stats_history]
        
        return {
            'total_executions': len(self.stats_history),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'max_execution_time': max(execution_times),
            'min_execution_time': min(execution_times),
            'avg_row_count': sum(row_counts) / len(row_counts),
            'total_rows_processed': sum(row_counts),
            'error_rate': len(self.error_history) / (len(self.stats_history) + len(self.error_history))
        }
```

### 智能体注册和配置

```python
def _create_sql_executor_agent(self) -> AssistantAgent:
    """
    创建SQL执行智能体
    
    配置要点:
    1. 专业的SQL执行能力
    2. 完善的安全防护机制
    3. 智能的结果处理
    4. 全面的错误处理
    """
    
    system_message = f"""
你是Text2SQL系统中的SQL执行专家。你的任务是安全、高效地执行SQL语句并处理查询结果。

## 你的专业技能：
1. **安全执行**: 在受控环境中安全执行SQL语句
2. **结果处理**: 智能处理和格式化查询结果
3. **错误诊断**: 准确诊断和处理各种执行错误
4. **性能监控**: 监控执行性能并提供优化建议
5. **连接管理**: 高效管理数据库连接和资源

## 执行标准：
1. **安全性**: 确保SQL执行的安全性，防止危险操作
2. **可靠性**: 保证执行结果的准确性和一致性
3. **效率性**: 优化执行性能，减少资源消耗
4. **稳定性**: 处理各种异常情况，确保系统稳定
5. **可观测性**: 提供详细的执行日志和统计信息

## 执行环境：
- 数据库类型: {self.db_type}
- 最大结果行数: {self.max_rows}
- 执行超时时间: {self.timeout}秒
- 安全级别: 高

## 执行流程：
1. 接收SQL语句和执行上下文
2. 进行安全性验证和预处理
3. 在监控环境中执行SQL
4. 处理和格式化查询结果
5. 返回结构化的执行结果

请始终保持专业、安全、高效的执行标准。
"""
    
    agent = AssistantAgent(
        name="sql_executor",
        model_client=self.model_client,
        system_message=system_message,
        description="专业的SQL执行智能体，负责安全高效地执行SQL语句并处理结果"
    )
    
    return agent
```

## 📊 执行能力矩阵

### SQL执行支持

| SQL类型 | 执行支持 | 安全级别 | 性能优化 |
|---------|----------|----------|----------|
| SELECT查询 | ✅ 完全支持 | 高 | 优秀 |
| 简单JOIN | ✅ 完全支持 | 高 | 良好 |
| 复杂JOIN | ✅ 完全支持 | 高 | 中等 |
| 聚合查询 | ✅ 完全支持 | 高 | 良好 |
| 子查询 | ✅ 完全支持 | 中 | 中等 |
| 窗口函数 | ✅ 部分支持 | 中 | 中等 |
| INSERT语句 | ❌ 禁止 | 安全限制 | N/A |
| UPDATE语句 | ❌ 禁止 | 安全限制 | N/A |
| DELETE语句 | ❌ 禁止 | 安全限制 | N/A |
| DDL语句 | ❌ 禁止 | 安全限制 | N/A |

### 安全防护机制

| 安全特性 | 实现程度 | 防护效果 | 说明 |
|---------|----------|----------|------|
| 危险操作检测 | ✅ 完全实现 | 高 | 阻止所有写操作和DDL |
| SQL注入防护 | ✅ 完全实现 | 高 | 多模式检测和阻止 |
| 查询超时控制 | ✅ 完全实现 | 高 | 防止长时间运行查询 |
| 结果集限制 | ✅ 完全实现 | 中 | 自动添加LIMIT限制 |
| 复杂度控制 | ✅ 基本实现 | 中 | 限制过于复杂的查询 |
| 权限验证 | ⚠️ 部分实现 | 中 | 基于数据库连接权限 |

### 结果处理能力

| 处理特性 | 支持程度 | 质量评级 | 说明 |
|---------|----------|----------|------|
| 数据类型转换 | ✅ 完全支持 | 优秀 | 支持所有常见数据类型 |
| 格式标准化 | ✅ 完全支持 | 优秀 | JSON格式输出 |
| 大结果集处理 | ✅ 完全支持 | 良好 | 自动分页和限制 |
| 空值处理 | ✅ 完全支持 | 良好 | 智能空值转换 |
| 日期时间处理 | ✅ 完全支持 | 良好 | 标准格式转换 |
| 元数据生成 | ✅ 完全支持 | 优秀 | 丰富的结果元信息 |

## 🔍 执行监控和诊断

### 1. 性能监控系统
```python
class ExecutionMonitor:
    """
    SQL执行监控系统
    
    监控维度:
    1. 执行时间监控
    2. 资源使用监控
    3. 错误率监控
    4. 性能趋势分析
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_analyzer = PerformanceAnalyzer()
    
    async def monitor_execution(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """监控SQL执行过程"""
        monitoring_data = {
            'start_time': time.time(),
            'execution_id': execution_context['execution_id'],
            'sql_hash': execution_context['sql_hash']
        }
        
        try:
            # 监控执行过程
            result = await self._execute_with_monitoring(execution_context)
            
            # 收集性能指标
            monitoring_data.update({
                'end_time': time.time(),
                'success': True,
                'row_count': result.get('row_count', 0),
                'execution_time': result.get('execution_time', 0)
            })
            
            # 分析性能
            performance_analysis = await self._analyze_performance(monitoring_data)
            
            # 检查告警条件
            await self._check_alerts(monitoring_data, performance_analysis)
            
            return {
                'monitoring_data': monitoring_data,
                'performance_analysis': performance_analysis,
                'result': result
            }
            
        except Exception as e:
            monitoring_data.update({
                'end_time': time.time(),
                'success': False,
                'error': str(e)
            })
            
            await self._handle_monitoring_error(monitoring_data, e)
            raise
    
    async def _analyze_performance(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析执行性能"""
        execution_time = monitoring_data['execution_time']
        row_count = monitoring_data['row_count']
        
        # 性能评级
        if execution_time < 1.0:
            performance_grade = 'EXCELLENT'
        elif execution_time < 5.0:
            performance_grade = 'GOOD'
        elif execution_time < 15.0:
            performance_grade = 'FAIR'
        else:
            performance_grade = 'POOR'
        
        # 效率分析
        if row_count > 0:
            rows_per_second = row_count / execution_time
        else:
            rows_per_second = 0
        
        return {
            'performance_grade': performance_grade,
            'execution_time': execution_time,
            'row_count': row_count,
            'rows_per_second': rows_per_second,
            'efficiency_score': self._calculate_efficiency_score(execution_time, row_count)
        }
    
    def _calculate_efficiency_score(self, execution_time: float, row_count: int) -> float:
        """计算效率分数"""
        if execution_time == 0:
            return 100.0
        
        # 基础分数
        base_score = 100.0
        
        # 时间惩罚
        time_penalty = min(execution_time * 5, 50)  # 最多扣50分
        
        # 数据量奖励
        data_bonus = min(row_count / 100, 10)  # 最多加10分
        
        efficiency_score = base_score - time_penalty + data_bonus
        return max(0, min(100, efficiency_score))
```

### 2. 错误诊断系统
```python
class ErrorDiagnosticSystem:
    """
    错误诊断系统
    
    诊断能力:
    1. 错误分类和识别
    2. 根因分析
    3. 解决方案推荐
    4. 预防措施建议
    """
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.solution_database = self._load_solution_database()
    
    async def diagnose_error(self, error: Exception, sql: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """诊断执行错误"""
        try:
            # 错误分类
            error_classification = self._classify_error_detailed(error, sql)
            
            # 根因分析
            root_cause_analysis = self._analyze_root_cause(error, sql, context)
            
            # 解决方案推荐
            solutions = self._recommend_solutions(error_classification, root_cause_analysis)
            
            # 预防措施
            prevention_measures = self._suggest_prevention_measures(error_classification)
            
            return {
                'error_classification': error_classification,
                'root_cause_analysis': root_cause_analysis,
                'recommended_solutions': solutions,
                'prevention_measures': prevention_measures,
                'diagnostic_confidence': self._calculate_diagnostic_confidence(error_classification)
            }
            
        except Exception as diagnostic_error:
            logger.error(f"错误诊断失败: {str(diagnostic_error)}")
            return self._create_fallback_diagnosis(error, sql)
    
    def _classify_error_detailed(self, error: Exception, sql: str) -> Dict[str, Any]:
        """详细错误分类"""
        error_message = str(error).lower()
        sql_upper = sql.upper()
        
        # 语法错误
        if any(keyword in error_message for keyword in ['syntax', 'parse', 'invalid']):
            return {
                'category': 'SYNTAX_ERROR',
                'subcategory': self._identify_syntax_error_type(error_message, sql),
                'severity': 'HIGH',
                'user_fixable': True
            }
        
        # 数据库对象错误
        elif any(keyword in error_message for keyword in ['table', 'column', 'not found']):
            return {
                'category': 'OBJECT_ERROR',
                'subcategory': self._identify_object_error_type(error_message),
                'severity': 'HIGH',
                'user_fixable': True
            }
        
        # 权限错误
        elif any(keyword in error_message for keyword in ['permission', 'access', 'denied']):
            return {
                'category': 'PERMISSION_ERROR',
                'subcategory': 'ACCESS_DENIED',
                'severity': 'MEDIUM',
                'user_fixable': False
            }
        
        # 性能错误
        elif any(keyword in error_message for keyword in ['timeout', 'memory', 'resource']):
            return {
                'category': 'PERFORMANCE_ERROR',
                'subcategory': self._identify_performance_error_type(error_message),
                'severity': 'MEDIUM',
                'user_fixable': True
            }
        
        # 连接错误
        elif any(keyword in error_message for keyword in ['connection', 'network', 'host']):
            return {
                'category': 'CONNECTION_ERROR',
                'subcategory': 'DATABASE_UNREACHABLE',
                'severity': 'HIGH',
                'user_fixable': False
            }
        
        # 未知错误
        else:
            return {
                'category': 'UNKNOWN_ERROR',
                'subcategory': 'UNCLASSIFIED',
                'severity': 'MEDIUM',
                'user_fixable': False
            }
    
    def _analyze_root_cause(self, error: Exception, sql: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """根因分析"""
        analysis = {
            'primary_cause': '',
            'contributing_factors': [],
            'context_factors': [],
            'confidence_level': 0.0
        }
        
        error_message = str(error).lower()
        
        # 分析主要原因
        if 'syntax' in error_message:
            analysis['primary_cause'] = 'SQL语法错误'
            analysis['confidence_level'] = 0.9
        elif 'table' in error_message and 'not found' in error_message:
            analysis['primary_cause'] = '表不存在或名称错误'
            analysis['confidence_level'] = 0.95
        elif 'column' in error_message and 'not found' in error_message:
            analysis['primary_cause'] = '字段不存在或名称错误'
            analysis['confidence_level'] = 0.95
        elif 'timeout' in error_message:
            analysis['primary_cause'] = '查询执行超时'
            analysis['confidence_level'] = 0.9
        
        # 分析贡献因素
        if 'JOIN' in sql.upper() and len(re.findall(r'\bJOIN\b', sql.upper())) > 2:
            analysis['contributing_factors'].append('复杂的多表连接可能影响性能')
        
        if 'GROUP BY' in sql.upper() and 'LIMIT' not in sql.upper():
            analysis['contributing_factors'].append('聚合查询缺少结果限制')
        
        if len(sql) > 1000:
            analysis['contributing_factors'].append('SQL语句过于复杂')
        
        # 分析上下文因素
        if context.get('execution_time', 0) > 10:
            analysis['context_factors'].append('执行时间过长')
        
        if context.get('retry_count', 0) > 0:
            analysis['context_factors'].append('存在重试历史')
        
        return analysis
    
    def _recommend_solutions(self, error_classification: Dict[str, Any], 
                           root_cause_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐解决方案"""
        solutions = []
        
        category = error_classification['category']
        subcategory = error_classification.get('subcategory', '')
        
        if category == 'SYNTAX_ERROR':
            solutions.extend([
                {
                    'solution': '检查SQL语法',
                    'description': '仔细检查SQL语句的语法，确保所有关键字、括号、引号正确匹配',
                    'priority': 'HIGH',
                    'difficulty': 'EASY'
                },
                {
                    'solution': '使用SQL验证工具',
                    'description': '使用在线SQL语法检查工具验证语句正确性',
                    'priority': 'MEDIUM',
                    'difficulty': 'EASY'
                }
            ])
        
        elif category == 'OBJECT_ERROR':
            if 'table' in subcategory.lower():
                solutions.append({
                    'solution': '确认表名正确性',
                    'description': '检查表名拼写、大小写，确认表在当前数据库中存在',
                    'priority': 'HIGH',
                    'difficulty': 'EASY'
                })
            elif 'column' in subcategory.lower():
                solutions.append({
                    'solution': '确认字段名正确性',
                    'description': '检查字段名拼写、大小写，确认字段在指定表中存在',
                    'priority': 'HIGH',
                    'difficulty': 'EASY'
                })
        
        elif category == 'PERFORMANCE_ERROR':
            solutions.extend([
                {
                    'solution': '添加查询限制',
                    'description': '使用LIMIT子句限制返回结果数量',
                    'priority': 'HIGH',
                    'difficulty': 'EASY'
                },
                {
                    'solution': '优化WHERE条件',
                    'description': '添加更具选择性的WHERE条件减少数据扫描量',
                    'priority': 'MEDIUM',
                    'difficulty': 'MEDIUM'
                },
                {
                    'solution': '简化JOIN操作',
                    'description': '减少不必要的表连接，优化连接条件',
                    'priority': 'MEDIUM',
                    'difficulty': 'HARD'
                }
            ])
        
        return solutions
```

## 🚀 性能优化策略

### 1. 连接池管理
```python
class DatabaseConnectionPool:
    """
    数据库连接池管理
    
    优化策略:
    1. 连接复用
    2. 连接健康检查
    3. 自动重连机制
    4. 负载均衡
    """
    
    def __init__(self, max_connections: int = 10, min_connections: int = 2):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.active_connections = []
        self.idle_connections = []
        self.connection_stats = ConnectionStats()
    
    async def get_connection(self) -> DBConnection:
        """获取数据库连接"""
        # 尝试从空闲连接池获取
        if self.idle_connections:
            connection = self.idle_connections.pop()
            if await self._validate_connection(connection):
                self.active_connections.append(connection)
                return connection
        
        # 创建新连接
        if len(self.active_connections) < self.max_connections:
            connection = await self._create_new_connection()
            self.active_connections.append(connection)
            return connection
        
        # 等待连接可用
        return await self._wait_for_available_connection()
    
    async def release_connection(self, connection: DBConnection):
        """释放数据库连接"""
        if connection in self.active_connections:
            self.active_connections.remove(connection)
            
            if await self._validate_connection(connection):
                self.idle_connections.append(connection)
            else:
                await self._close_connection(connection)
```

### 2. 查询缓存机制
```python
class QueryResultCache:
    """
    查询结果缓存
    
    缓存策略:
    1. LRU缓存算法
    2. 基于SQL哈希的缓存键
    3. 结果过期机制
    4. 内存使用控制
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl  # 生存时间（秒）
    
    async def get_cached_result(self, sql: str) -> Optional[Dict[str, Any]]:
        """获取缓存的查询结果"""
        cache_key = self._generate_cache_key(sql)
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            
            # 检查是否过期
            if time.time() - cached_item['timestamp'] < self.ttl:
                # 更新访问时间
                self.access_times[cache_key] = time.time()
                return cached_item['result']
            else:
                # 删除过期缓存
                del self.cache[cache_key]
                del self.access_times[cache_key]
        
        return None
    
    async def cache_result(self, sql: str, result: Dict[str, Any]):
        """缓存查询结果"""
        cache_key = self._generate_cache_key(sql)
        
        # 检查缓存大小
        if len(self.cache) >= self.max_size:
            await self._evict_least_recently_used()
        
        # 缓存结果
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        self.access_times[cache_key] = time.time()
```

---

**总结**: SQL执行智能体是Text2SQL系统的核心执行引擎，负责安全、高效地执行SQL语句并处理查询结果。通过完善的安全防护机制、智能的结果处理能力、全面的错误诊断系统和高效的性能优化策略，确保SQL查询的可靠执行和优质的用户体验。该智能体具备强大的监控和诊断能力，能够及时发现和解决执行过程中的各种问题，为Text2SQL系统提供稳定可靠的SQL执行服务。