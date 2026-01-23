"""
SQL生成智能体 - 基于分析结果生成精确的SQL语句
"""
import re
from typing import Dict, Any, List
from loguru import logger

from app.config.settings import settings
from app.core.model_client import get_deepseek_client


class SQLGeneratorAgent:
    """
    SQL生成智能体实现
    
    功能:
    1. 基于分析结果生成SQL语句
    2. SQL语法优化
    3. SQL验证和修复
    4. 安全性检查
    """
    
    def __init__(self, db_type: str):
        self.db_type = db_type
        self.model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        self.system_message = self._build_system_message()
    
    def _build_system_message(self) -> str:
        """构建系统提示词"""
        return f"""
你是一个专业的SQL开发专家。你的任务是将查询分析结果转换为高质量的SQL语句。

## 核心职责：
1. **SQL生成**: 基于分析结果生成准确的SQL语句
2. **性能优化**: 确保生成的SQL具有良好的执行性能
3. **安全保障**: 防止SQL注入和其他安全风险
4. **语法规范**: 遵循SQL标准和数据库特定语法
5. **错误预防**: 避免常见的SQL错误和陷阱

## SQL生成原则：

### 1. 准确性原则
- SQL语句必须准确反映用户查询意图
- 字段名、表名、条件逻辑完全正确
- 数据类型匹配和转换正确
- 结果集符合预期

### 2. 效率性原则
- 优化查询执行计划
- 合理使用索引
- 避免不必要的全表扫描
- 减少数据传输量

### 3. 安全性原则
- 防止SQL注入攻击
- 使用参数化查询（虽然实际执行时是动态SQL）
- 避免动态SQL拼接
- 限制查询权限范围

### 4. 可维护性原则
- 代码结构清晰
- 适当的注释说明
- 遵循命名规范
- 易于理解和修改

## 数据库信息：
- **数据库类型**: {self.db_type}
- **支持的特性**: SQLite, MySQL, PostgreSQL

## SQL生成模板：

### 1. 简单查询模板
```sql
-- 基础查询结构
SELECT [字段列表]
FROM [主表]
[WHERE 条件]
[ORDER BY 排序]
[LIMIT 限制];
```

### 2. 连接查询模板
```sql
-- 多表连接结构
SELECT [字段列表]
FROM [主表] [别名1]
[JOIN类型] JOIN [关联表] [别名2] ON [连接条件]
[WHERE 筛选条件]
[GROUP BY 分组字段]
[HAVING 聚合条件]
[ORDER BY 排序字段]
[LIMIT 结果数量];
```

### 3. 聚合查询模板
```sql
-- 统计分析结构
SELECT [分组字段], [聚合函数]
FROM [数据表]
[WHERE 筛选条件]
GROUP BY [分组字段]
[HAVING 聚合筛选]
[ORDER BY 排序规则]
[LIMIT 结果数量];
```

## 数据库特性：

### SQLite特定语法
- 日期函数: date(), datetime(), strftime()
- 字符串函数: substr(), length(), trim()
- 数学函数: round(), abs(), random()
- 限制语法: LIMIT offset, count

### MySQL特定语法
- 日期函数: DATE_FORMAT(), YEAR(), MONTH()
- 字符串函数: CONCAT(), SUBSTRING(), CHAR_LENGTH()
- 限制语法: LIMIT count OFFSET offset

### PostgreSQL特定语法
- 日期函数: EXTRACT(), DATE_TRUNC(), AGE()
- 字符串函数: POSITION(), SPLIT_PART(), REGEXP_REPLACE()
- 窗口函数: ROW_NUMBER(), RANK(), DENSE_RANK()

## 生成要求：

### 1. 输出格式
- **只生成一条SQL语句**
- 使用标准SQL语法
- 包含必要的注释
- 格式化良好，易于阅读

### 2. 质量标准
- 语法完全正确
- 逻辑完全准确
- 性能充分优化
- 安全完全保障

### 3. 错误处理
- 识别并避免常见错误
- 提供错误预警
- 建议优化方案
- 确保SQL可执行性

## 特殊语法处理：

### 1. 复杂查询优化
- 使用EXISTS替代IN（大数据集）
- 使用UNION ALL替代UNION（无需去重）
- 避免SELECT *，明确指定字段
- 合理使用子查询和临时表

### 2. 性能优化建议
- 在WHERE条件字段上使用索引
- 在JOIN连接字段上使用索引
- 在ORDER BY排序字段上使用索引
- 避免在索引字段上使用函数

### 3. 数据库兼容性
- 生成符合{self.db_type}数据库的特定语法
- 避免使用不兼容的函数或特性
- 考虑不同数据库的SQL方言差异

## 安全注意事项：

### 1. SQL注入防护
- 验证SQL语句的安全性
- 避免危险的SQL操作（DROP、DELETE、UPDATE、INSERT）
- 限制查询为只读操作（SELECT）
- 避免注释注入（--、/* */）

### 2. 查询限制
- 确保所有查询都有LIMIT限制
- 避免返回过大的结果集
- 考虑性能和资源消耗

## 常见错误模式：

### 1. 语法错误
- 缺少必要的SQL关键字（SELECT、FROM、WHERE）
- 括号不匹配
- 引号不匹配
- 表名或字段名拼写错误

### 2. 逻辑错误
- 连接条件错误
- 聚合函数使用不当
- GROUP BY与SELECT字段不匹配
- HAVING条件错误

### 3. 性能错误
- 缺少必要的索引提示
- 不必要的全表扫描
- 过多的JOIN操作
- 低效的子查询

## 优化策略：

### 1. 索引优化
- 在WHERE条件字段上使用索引
- 在JOIN连接字段上使用索引
- 在ORDER BY排序字段上使用索引
- 避免在索引字段上使用函数

### 2. 查询优化
- 使用EXISTS替代IN（大数据集）
- 使用UNION ALL替代UNION（无需去重）
- 避免SELECT *，明确指定字段
- 合理使用子查询和临时表

### 3. 性能监控
- 预估查询执行时间
- 监控资源使用情况
- 识别性能瓶颈
- 提供优化建议

请根据提供的查询分析结果，生成高质量的SQL语句。
"""
    
    async def generate_sql(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成SQL语句

        Args:
            analysis_result: 查询分析结果

        Returns:
            SQL生成结果
        """
        try:
            logger.info(f"开始生成SQL，查询类型: {analysis_result.get('query_intent', {}).get('type', 'unknown')}")
            
            # 构建SQL生成提示
            generation_prompt = f"""
基于以下查询分析结果，生成精确的SQL语句：

查询分析结果:
```json
{{
  "query_intent": {analysis_result.get('query_intent', {})},
  "entities": {analysis_result.get('entities', {})},
  "table_mapping": {analysis_result.get('table_mapping', {})},
  "query_structure": {analysis_result.get('query_structure', {})}
}}
```

请生成符合以下要求的SQL语句：
1. 语法完全正确
2. 逻辑完全准确
3. 性能充分优化
4. 格式清晰易读
5. 包含适当注释
6. 确保与{self.db_type}数据库兼容
7. 自动添加LIMIT限制（如果未指定）
8. 只输出一条完整的SQL语句，不要包含其他解释文字

数据库类型: {self.db_type}

请直接输出SQL语句，使用markdown代码块格式。
"""
            
            # 调用AI模型生成SQL
            response = await self.model_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": generation_prompt}
                ],
                model=settings.model_name,
                temperature=0.1,  # 低温度确保SQL的准确性
                max_tokens=1000
            )
            
            # 提取和清理SQL语句
            sql_content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            cleaned_sql = self._clean_sql_output(sql_content)
            
            # 验证SQL语法
            validation_result = self._validate_sql_syntax(cleaned_sql)
            
            logger.info(f"SQL生成完成: {len(cleaned_sql)}字符")
            
            return {
                'sql': cleaned_sql,
                'validation': validation_result,
                'optimization_notes': self._get_optimization_notes(cleaned_sql)
            }
            
        except Exception as e:
            logger.error(f"SQL生成失败: {str(e)}")
            return self._create_error_response(str(e), analysis_result)
    
    def _clean_sql_output(self, sql_content: str) -> str:
        """清理SQL输出内容"""
        # 移除markdown代码块标记
        cleaned = re.sub(r'```sql\s*', '', sql_content, flags=re.IGNORECASE)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 移除注释后的多余空行
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip() and not line.strip().startswith('--'):
                cleaned_lines.append(line)
            elif line.strip().startswith('--'):
                cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # 确保SQL以分号结尾
        if cleaned.strip() and not cleaned.rstrip().endswith(';'):
            cleaned = cleaned.rstrip() + ';'
        
        return cleaned.strip()
    
    def _validate_sql_syntax(self, sql: str) -> Dict[str, Any]:
        """验证SQL语法"""
        errors = []
        warnings = []
        sql_upper = sql.upper()
        
        # 检查必要的SQL关键字
        if not re.search(r'\bSELECT\b', sql_upper, re.IGNORECASE):
            errors.append("缺少SELECT关键字")
        
        if not re.search(r'\bFROM\b', sql_upper, re.IGNORECASE):
            errors.append("缺少FROM关键字")
        
        # 检查括号匹配
        if sql.count('(') != sql.count(')'):
            errors.append("括号不匹配")
        
        # 检查引号匹配
        single_quotes = sql.count("'")
        if single_quotes % 2 != 0:
            errors.append("单引号不匹配")
        
        double_quotes = sql.count('"')
        if double_quotes % 2 != 0:
            errors.append("双引号不匹配")
        
        # 检查表名和字段名有效性
        table_validation = self._validate_table_references(sql)
        errors.extend(table_validation)
        
        # 检查是否使用SELECT *
        if re.search(r'SELECT\s+\*', sql_upper, re.IGNORECASE):
            warnings.append("建议明确指定字段名而不是使用SELECT *")
        
        # 检查是否有WHERE条件
        if not re.search(r'\bWHERE\b', sql_upper, re.IGNORECASE):
            if re.search(r'\b(Invoice|InvoiceLine|Track)\b', sql_upper, re.IGNORECASE):
                warnings.append("大表查询建议添加WHERE条件以提升性能")
        
        # 检查是否有LIMIT
        if not re.search(r'\bLIMIT\b', sql_upper, re.IGNORECASE):
            if re.search(r'\b(Invoice|InvoiceLine|Track)\b', sql_upper, re.IGNORECASE):
                warnings.append("建议添加LIMIT限制结果数量")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_table_references(self, sql: str) -> List[str]:
        """验证表引用的有效性"""
        errors = []
        
        # 定义有效的表名
        valid_tables = {
            'Customer', 'Invoice', 'InvoiceLine', 'Track',
            'Album', 'Artist', 'Genre', 'MediaType',
            'Playlist', 'PlaylistTrack', 'Employee'
        }
        
        # 提取SQL中的表名
        table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables_in_sql = set(re.findall(table_pattern, sql, re.IGNORECASE))
        
        for table in tables_in_sql:
            if table not in valid_tables:
                errors.append(f"无效的表名: {table}")
        
        return errors
    
    def _get_optimization_notes(self, sql: str) -> List[str]:
        """获取SQL优化建议"""
        notes = []
        sql_upper = sql.upper()
        
        # 检查索引使用提示
        if re.search(r'WHERE.*CustomerId', sql_upper):
            notes.append("CustomerId字段有索引，查询性能良好")
        
        # 检查JOIN优化
        if re.search(r'INNER JOIN', sql_upper):
            notes.append("使用INNER JOIN，性能优于LEFT JOIN")
        
        # 检查聚合优化
        if re.search(r'GROUP BY', sql_upper):
            notes.append("聚合查询已优化，建议在分组字段上建立索引")
        
        # 检查排序优化
        if re.search(r'ORDER BY', sql_upper):
            if re.search(r'LIMIT', sql_upper):
                notes.append("ORDER BY配合LIMIT使用，性能良好")
            else:
                notes.append("ORDER BY查询可能较慢，建议添加LIMIT")
        
        return notes
    
    def _create_error_response(self, error_message: str, 
                           analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误响应"""
        # 生成基础的备用SQL
        fallback_sql = self._generate_fallback_sql(analysis_result)
        
        return {
            'sql': fallback_sql,
            'error': True,
            'message': f"SQL生成失败: {error_message}",
            'validation': {
                'valid': False,
                'errors': [error_message],
                'warnings': []
            },
            'optimization_notes': []
        }
    
    def _generate_fallback_sql(self, analysis_result: Dict[str, Any]) -> str:
        """生成备用SQL语句"""
        try:
            # 从分析结果中提取基本信息
            table_mapping = analysis_result.get('table_mapping', {})
            primary_table = table_mapping.get('primary_table', 'Customer')
            
            # 生成最基础的查询
            if primary_table:
                fallback_sql = f"SELECT * FROM {primary_table} LIMIT 10;"
            else:
                fallback_sql = "SELECT * FROM Customer LIMIT 10;"
            
            return fallback_sql
            
        except Exception:
            return "SELECT * FROM Customer LIMIT 10;"
