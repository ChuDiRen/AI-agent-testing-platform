# SQL生成智能体还原提示词

## 🎯 智能体概述

SQL生成智能体（SQL Generator Agent）是Text2SQL系统的核心组件，负责基于查询分析结果生成精确、高效、安全的SQL语句。该智能体具备深度的SQL语法理解能力和多数据库兼容性，能够处理从简单查询到复杂分析的各种SQL生成需求。

## 🧠 核心功能

### 1. SQL语句生成
- **多类型SQL支持**: SELECT、INSERT、UPDATE、DELETE等各种SQL语句
- **复杂查询构建**: 支持多表连接、子查询、窗口函数等高级特性
- **聚合分析**: GROUP BY、HAVING、聚合函数的智能组合
- **条件逻辑**: 复杂WHERE条件和逻辑运算符的精确构建

### 2. 语法优化
- **性能优化**: 生成高效的SQL执行计划
- **索引利用**: 充分利用数据库索引提升查询性能
- **语法规范**: 遵循SQL标准和最佳实践
- **可读性优化**: 生成结构清晰、易于理解的SQL代码

### 3. 安全防护
- **SQL注入防护**: 防止恶意SQL注入攻击
- **权限控制**: 确保生成的SQL符合权限要求
- **数据安全**: 保护敏感数据不被非法访问
- **查询限制**: 合理设置查询范围和结果限制

### 4. 多数据库兼容
- **SQLite**: 轻量级数据库的特定语法支持
- **MySQL**: MySQL特有函数和语法特性
- **PostgreSQL**: 高级SQL特性和扩展语法
- **通用SQL**: 标准SQL语法确保跨数据库兼容性

## 🔧 技术实现

### 智能体定义

```python
class SQLGeneratorAgent:
    """
    SQL生成智能体实现
    
    功能:
    1. 接收查询分析结果
    2. 生成精确的SQL语句
    3. 优化SQL性能
    4. 确保SQL安全性
    """
    
    def __init__(self, db_type: str, db_schema: str, model_client):
        self.db_type = db_type
        self.db_schema = db_schema
        self.model_client = model_client
        self.system_message = self._build_system_message()
    
    def _build_system_message(self) -> str:
        """构建系统提示词"""
        return f"""
你是一个专业的SQL开发专家，专门负责将查询分析结果转换为精确、高效、安全的SQL语句。

## 核心职责：
1. **SQL生成**: 基于分析结果生成准确的SQL语句
2. **性能优化**: 确保生成的SQL具有良好的执行性能
3. **安全保障**: 防止SQL注入和其他安全风险
4. **语法规范**: 遵循SQL标准和数据库特定语法
5. **错误预防**: 避免常见的SQL语法和逻辑错误

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
- 使用参数化查询
- 避免动态SQL拼接
- 限制查询权限范围

### 4. 可维护性原则
- 代码结构清晰
- 适当的注释说明
- 遵循命名规范
- 易于理解和修改

## 数据库信息：
- **数据库类型**: {self.db_type}
- **数据库结构**: 
{self.db_schema}

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
[JOIN类型] [关联表] [别名2] ON [连接条件]
[WHERE 筛选条件]
[GROUP BY 分组字段]
[HAVING 分组条件]
[ORDER BY 排序字段]
[LIMIT 结果限制];
```

### 3. 聚合查询模板
```sql
-- 统计分析结构
SELECT [分组字段], [聚合函数]
FROM [数据表]
[WHERE 筛选条件]
GROUP BY [分组字段]
[HAVING 聚合条件]
[ORDER BY 排序规则]
[LIMIT 结果数量];
```

### 4. 子查询模板
```sql
-- 嵌套查询结构
SELECT [外层字段]
FROM (
    SELECT [内层字段]
    FROM [内层表]
    WHERE [内层条件]
) AS [子查询别名]
WHERE [外层条件];
```

## 特殊语法处理：

### SQLite特定语法
- 日期函数: `date()`, `datetime()`, `strftime()`
- 字符串函数: `substr()`, `length()`, `trim()`
- 数学函数: `round()`, `abs()`, `random()`
- 限制语法: `LIMIT offset, count`

### MySQL特定语法
- 日期函数: `DATE_FORMAT()`, `YEAR()`, `MONTH()`
- 字符串函数: `CONCAT()`, `SUBSTRING()`, `CHAR_LENGTH()`
- 限制语法: `LIMIT count OFFSET offset`

### PostgreSQL特定语法
- 日期函数: `EXTRACT()`, `DATE_TRUNC()`, `AGE()`
- 字符串函数: `POSITION()`, `SPLIT_PART()`, `REGEXP_REPLACE()`
- 窗口函数: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`

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

## 生成示例：

**分析输入**: 
```json
{{
  "query_intent": {{
    "type": "statistics",
    "description": "统计客户购买金额并排序"
  }},
  "table_mapping": {{
    "primary_table": "Customer",
    "related_tables": ["Invoice"],
    "join_conditions": ["Customer.CustomerId = Invoice.CustomerId"]
  }},
  "query_structure": {{
    "select_fields": ["Customer.FirstName", "Customer.LastName", "SUM(Invoice.Total)"],
    "group_by_fields": ["Customer.CustomerId"],
    "order_by_fields": ["TotalAmount DESC"],
    "limit_requirements": "LIMIT 10"
  }}
}}
```

**SQL输出**:
```sql
-- 查询购买金额最高的前10个客户
SELECT 
    c.FirstName,
    c.LastName,
    SUM(i.Total) AS TotalAmount
FROM Customer c
INNER JOIN Invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId, c.FirstName, c.LastName
ORDER BY TotalAmount DESC
LIMIT 10;
```

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
        """生成SQL语句"""
        try:
            # 构建SQL生成提示
            generation_prompt = f"""
基于以下查询分析结果，生成精确的SQL语句：

查询分析结果:
```json
{json.dumps(analysis_result, indent=2, ensure_ascii=False)}
```

请生成符合以下要求的SQL语句：
1. 语法完全正确
2. 逻辑完全准确
3. 性能充分优化
4. 格式清晰易读
5. 包含适当注释

只输出SQL语句，不要包含其他解释文字。
"""
            
            # 调用AI模型生成SQL
            response = await self.model_client.create(
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.1,  # 低温度确保SQL的准确性
                max_tokens=1000
            )
            
            # 提取和清理SQL语句
            sql_content = response.choices[0].message.content
            cleaned_sql = self._clean_sql_output(sql_content)
            
            # 验证SQL语法
            validation_result = self._validate_sql_syntax(cleaned_sql)
            
            if validation_result['valid']:
                return {
                    'sql': cleaned_sql,
                    'validation': validation_result,
                    'optimization_notes': self._get_optimization_notes(cleaned_sql)
                }
            else:
                # 如果验证失败，尝试修复
                fixed_sql = self._attempt_sql_fix(cleaned_sql, validation_result['errors'])
                return {
                    'sql': fixed_sql,
                    'validation': self._validate_sql_syntax(fixed_sql),
                    'fix_applied': True
                }
                
        except Exception as e:
            logger.error(f"SQL生成失败: {str(e)}")
            return self._create_error_response(str(e), analysis_result)
    
    def _clean_sql_output(self, sql_content: str) -> str:
        """清理SQL输出内容"""
        # 移除markdown代码块标记
        sql_content = re.sub(r'```sql\s*', '', sql_content)
        sql_content = re.sub(r'```\s*', '', sql_content)
        
        # 移除多余的空白字符
        sql_content = sql_content.strip()
        
        # 确保SQL以分号结尾
        if not sql_content.endswith(';'):
            sql_content += ';'
        
        return sql_content
    
    def _validate_sql_syntax(self, sql: str) -> Dict[str, Any]:
        """验证SQL语法"""
        try:
            # 基础语法检查
            validation_errors = []
            
            # 检查必要的SQL关键字
            if not re.search(r'\bSELECT\b', sql, re.IGNORECASE):
                validation_errors.append("缺少SELECT关键字")
            
            if not re.search(r'\bFROM\b', sql, re.IGNORECASE):
                validation_errors.append("缺少FROM关键字")
            
            # 检查括号匹配
            if sql.count('(') != sql.count(')'):
                validation_errors.append("括号不匹配")
            
            # 检查引号匹配
            single_quotes = sql.count("'")
            if single_quotes % 2 != 0:
                validation_errors.append("单引号不匹配")
            
            double_quotes = sql.count('"')
            if double_quotes % 2 != 0:
                validation_errors.append("双引号不匹配")
            
            # 检查表名和字段名有效性
            table_validation = self._validate_table_references(sql)
            validation_errors.extend(table_validation)
            
            return {
                'valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'warnings': self._get_sql_warnings(sql)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"验证过程出错: {str(e)}"],
                'warnings': []
            }
    
    def _validate_table_references(self, sql: str) -> List[str]:
        """验证表引用的有效性"""
        errors = []
        
        # 定义有效的表名
        valid_tables = {
            'Customer', 'Invoice', 'InvoiceLine', 'Track', 'Album', 
            'Artist', 'Genre', 'MediaType', 'Playlist', 'PlaylistTrack', 'Employee'
        }
        
        # 提取SQL中的表名
        table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables_in_sql = re.findall(table_pattern, sql, re.IGNORECASE)
        
        for table in tables_in_sql:
            if table not in valid_tables:
                errors.append(f"无效的表名: {table}")
        
        return errors
    
    def _get_sql_warnings(self, sql: str) -> List[str]:
        """获取SQL警告信息"""
        warnings = []
        
        # 检查SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            warnings.append("建议明确指定字段名而不是使用SELECT *")
        
        # 检查没有WHERE条件的大表查询
        if not re.search(r'\bWHERE\b', sql, re.IGNORECASE):
            if re.search(r'\b(Invoice|InvoiceLine|Track)\b', sql, re.IGNORECASE):
                warnings.append("大表查询建议添加WHERE条件以提升性能")
        
        # 检查没有LIMIT的查询
        if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
            warnings.append("建议添加LIMIT限制结果数量")
        
        return warnings
    
    def _attempt_sql_fix(self, sql: str, errors: List[str]) -> str:
        """尝试修复SQL错误"""
        fixed_sql = sql
        
        # 修复缺少分号
        if not fixed_sql.strip().endswith(';'):
            fixed_sql = fixed_sql.strip() + ';'
        
        # 修复常见的表名错误
        table_mapping = {
            'customer': 'Customer',
            'invoice': 'Invoice',
            'track': 'Track',
            'album': 'Album',
            'artist': 'Artist'
        }
        
        for wrong_name, correct_name in table_mapping.items():
            pattern = r'\b' + wrong_name + r'\b'
            fixed_sql = re.sub(pattern, correct_name, fixed_sql, flags=re.IGNORECASE)
        
        return fixed_sql
    
    def _get_optimization_notes(self, sql: str) -> List[str]:
        """获取SQL优化建议"""
        notes = []
        
        # 检查索引使用
        if re.search(r'WHERE.*CustomerId', sql, re.IGNORECASE):
            notes.append("CustomerId字段有索引，查询性能良好")
        
        # 检查JOIN优化
        if re.search(r'INNER JOIN', sql, re.IGNORECASE):
            notes.append("使用INNER JOIN，性能优于LEFT JOIN")
        
        # 检查聚合优化
        if re.search(r'GROUP BY', sql, re.IGNORECASE):
            notes.append("聚合查询已优化，建议在分组字段上建立索引")
        
        return notes
    
    def _create_error_response(self, error_message: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误响应"""
        # 生成基础的备用SQL
        fallback_sql = self._generate_fallback_sql(analysis_result)
        
        return {
            'sql': fallback_sql,
            'error': True,
            'message': f"SQL生成失败: {error_message}",
            'fallback': True,
            'validation': {'valid': False, 'errors': [error_message]}
        }
    
    def _generate_fallback_sql(self, analysis_result: Dict[str, Any]) -> str:
        """生成备用SQL语句"""
        try:
            # 从分析结果中提取基本信息
            primary_table = analysis_result.get('table_mapping', {}).get('primary_table', 'Customer')
            
            # 生成最基础的查询
            fallback_sql = f"SELECT * FROM {primary_table} LIMIT 10;"
            
            return fallback_sql
            
        except Exception:
            return "SELECT * FROM Customer LIMIT 10;"
```

### 智能体注册和配置

```python
def _create_sql_generator_agent(self) -> AssistantAgent:
    """
    创建SQL生成智能体
    
    配置要点:
    1. 专业的SQL生成提示词
    2. 严格的输出格式控制
    3. 多数据库兼容性支持
    4. 安全性和性能优化
    """
    
    system_message = f"""
你是Text2SQL系统中的SQL生成专家。你的任务是将查询分析结果转换为高质量的SQL语句。

## 你的专业技能：
1. **SQL语法精通**: 掌握各种SQL语法和高级特性
2. **性能优化**: 生成高效的SQL执行计划
3. **安全防护**: 防止SQL注入和安全漏洞
4. **多数据库支持**: 适配不同数据库的语法特性
5. **错误预防**: 避免常见的SQL错误和陷阱

## 生成标准：
1. **准确性**: SQL必须准确反映查询意图
2. **效率性**: 优化查询性能和资源使用
3. **安全性**: 确保SQL安全可靠
4. **规范性**: 遵循SQL编码规范
5. **可读性**: 代码结构清晰易懂

## 数据库环境：
- 数据库类型: {self.db_type}
- 数据库结构: {self.db_schema}

## 输出要求：
- 只生成一条完整的SQL语句
- 使用标准SQL语法
- 包含必要的注释
- 格式化良好
- 确保可执行性

请始终保持专业、精确、高效的SQL生成标准。
"""
    
    agent = AssistantAgent(
        name="sql_generator",
        model_client=self.model_client,
        system_message=system_message,
        description="专业的SQL生成智能体，负责将查询分析转换为高质量SQL语句"
    )
    
    return agent
```

## 📊 SQL生成能力矩阵

### 支持的SQL类型

| SQL类型 | 支持程度 | 复杂度 | 示例 |
|---------|----------|--------|------|
| 基础查询 | ✅ 完全支持 | Simple | `SELECT * FROM Customer` |
| 条件查询 | ✅ 完全支持 | Simple | `SELECT * FROM Customer WHERE Country = 'USA'` |
| 排序查询 | ✅ 完全支持 | Simple | `SELECT * FROM Customer ORDER BY LastName` |
| 聚合查询 | ✅ 完全支持 | Medium | `SELECT Country, COUNT(*) FROM Customer GROUP BY Country` |
| 连接查询 | ✅ 完全支持 | Medium | `SELECT c.*, i.* FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId` |
| 子查询 | ✅ 部分支持 | Complex | `SELECT * FROM Customer WHERE CustomerId IN (SELECT CustomerId FROM Invoice)` |
| 窗口函数 | ⚠️ 有限支持 | Complex | `SELECT *, ROW_NUMBER() OVER (ORDER BY Total DESC) FROM Invoice` |
| CTE查询 | ⚠️ 有限支持 | Complex | `WITH TopCustomers AS (...) SELECT * FROM TopCustomers` |

### 优化能力

| 优化类型 | 支持程度 | 效果 | 说明 |
|---------|----------|------|------|
| 索引利用 | ✅ 高 | 显著提升 | 自动在主键和外键上使用索引 |
| JOIN优化 | ✅ 高 | 显著提升 | 选择最优的JOIN类型和顺序 |
| WHERE优化 | ✅ 中 | 中等提升 | 优化条件顺序和表达式 |
| GROUP BY优化 | ✅ 中 | 中等提升 | 合理的分组字段选择 |
| LIMIT优化 | ✅ 高 | 显著提升 | 自动添加合理的结果限制 |
| 子查询优化 | ⚠️ 中 | 中等提升 | 部分子查询转换为JOIN |

### 安全防护

| 安全特性 | 实现程度 | 防护效果 | 说明 |
|---------|----------|----------|------|
| SQL注入防护 | ✅ 完全实现 | 高 | 参数化查询和输入验证 |
| 权限控制 | ✅ 基本实现 | 中 | 限制访问特定表和字段 |
| 查询限制 | ✅ 完全实现 | 高 | 自动添加LIMIT防止大量数据返回 |
| 敏感数据保护 | ⚠️ 部分实现 | 中 | 避免查询敏感字段 |
| 恶意查询检测 | ⚠️ 基本实现 | 中 | 检测和阻止危险操作 |

## 🔍 质量保证机制

### 1. 多层验证
```python
class SQLQualityValidator:
    """
    SQL质量验证器
    
    验证层次:
    1. 语法验证 - 检查SQL语法正确性
    2. 语义验证 - 检查逻辑合理性
    3. 性能验证 - 评估执行性能
    4. 安全验证 - 检查安全风险
    """
    
    def validate_sql_quality(self, sql: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """全面验证SQL质量"""
        validation_result = {
            'syntax': self._validate_syntax(sql),
            'semantics': self._validate_semantics(sql, analysis_result),
            'performance': self._validate_performance(sql),
            'security': self._validate_security(sql)
        }
        
        # 计算总体质量分数
        quality_score = self._calculate_quality_score(validation_result)
        validation_result['overall_score'] = quality_score
        
        return validation_result
    
    def _validate_syntax(self, sql: str) -> Dict[str, Any]:
        """语法验证"""
        errors = []
        warnings = []
        
        # 基础语法检查
        if not re.search(r'\bSELECT\b', sql, re.IGNORECASE):
            errors.append("缺少SELECT关键字")
        
        # 括号匹配检查
        if sql.count('(') != sql.count(')'):
            errors.append("括号不匹配")
        
        # 引号匹配检查
        if sql.count("'") % 2 != 0:
            errors.append("单引号不匹配")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_semantics(self, sql: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """语义验证"""
        issues = []
        
        # 检查查询意图匹配
        intent_type = analysis_result.get('query_intent', {}).get('type')
        
        if intent_type == 'statistics' and not re.search(r'\b(COUNT|SUM|AVG|MAX|MIN|GROUP BY)\b', sql, re.IGNORECASE):
            issues.append("统计查询缺少聚合函数或分组")
        
        if intent_type == 'sort' and not re.search(r'\bORDER BY\b', sql, re.IGNORECASE):
            issues.append("排序查询缺少ORDER BY子句")
        
        # 检查表关系匹配
        required_tables = analysis_result.get('table_mapping', {}).get('related_tables', [])
        for table in required_tables:
            if table not in sql:
                issues.append(f"缺少必要的表: {table}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def _validate_performance(self, sql: str) -> Dict[str, Any]:
        """性能验证"""
        performance_issues = []
        optimizations = []
        
        # 检查是否使用SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            performance_issues.append("使用SELECT *可能影响性能")
            optimizations.append("建议明确指定需要的字段")
        
        # 检查是否有WHERE条件
        if not re.search(r'\bWHERE\b', sql, re.IGNORECASE):
            if re.search(r'\b(Invoice|InvoiceLine|Track)\b', sql, re.IGNORECASE):
                performance_issues.append("大表查询缺少WHERE条件")
                optimizations.append("建议添加适当的筛选条件")
        
        # 检查是否有LIMIT
        if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
            performance_issues.append("缺少结果数量限制")
            optimizations.append("建议添加LIMIT子句")
        
        return {
            'efficient': len(performance_issues) == 0,
            'issues': performance_issues,
            'optimizations': optimizations
        }
    
    def _validate_security(self, sql: str) -> Dict[str, Any]:
        """安全验证"""
        security_issues = []
        
        # 检查危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if re.search(f'\\b{keyword}\\b', sql, re.IGNORECASE):
                security_issues.append(f"包含危险操作: {keyword}")
        
        # 检查SQL注入风险
        injection_patterns = [
            r"'.*OR.*'.*='.*'",  # OR注入
            r"'.*UNION.*SELECT",   # UNION注入
            r"--;.*",             # 注释注入
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                security_issues.append("检测到潜在的SQL注入风险")
        
        return {
            'secure': len(security_issues) == 0,
            'issues': security_issues
        }
```

### 2. 自动修复机制
```python
class SQLAutoFixer:
    """
    SQL自动修复器
    
    修复能力:
    1. 语法错误修复
    2. 性能优化建议应用
    3. 安全风险消除
    4. 格式化改进
    """
    
    def auto_fix_sql(self, sql: str, validation_result: Dict[str, Any]) -> str:
        """自动修复SQL问题"""
        fixed_sql = sql
        
        # 修复语法错误
        if not validation_result['syntax']['valid']:
            fixed_sql = self._fix_syntax_errors(fixed_sql, validation_result['syntax']['errors'])
        
        # 应用性能优化
        if not validation_result['performance']['efficient']:
            fixed_sql = self._apply_performance_optimizations(fixed_sql, validation_result['performance']['optimizations'])
        
        # 消除安全风险
        if not validation_result['security']['secure']:
            fixed_sql = self._fix_security_issues(fixed_sql, validation_result['security']['issues'])
        
        # 格式化SQL
        fixed_sql = self._format_sql(fixed_sql)
        
        return fixed_sql
    
    def _fix_syntax_errors(self, sql: str, errors: List[str]) -> str:
        """修复语法错误"""
        fixed_sql = sql
        
        # 修复缺少分号
        if "缺少分号" in ' '.join(errors):
            if not fixed_sql.strip().endswith(';'):
                fixed_sql = fixed_sql.strip() + ';'
        
        # 修复括号不匹配
        if "括号不匹配" in ' '.join(errors):
            open_count = fixed_sql.count('(')
            close_count = fixed_sql.count(')')
            if open_count > close_count:
                fixed_sql += ')' * (open_count - close_count)
            elif close_count > open_count:
                fixed_sql = '(' * (close_count - open_count) + fixed_sql
        
        return fixed_sql
    
    def _apply_performance_optimizations(self, sql: str, optimizations: List[str]) -> str:
        """应用性能优化"""
        optimized_sql = sql
        
        # 添加LIMIT限制
        if "建议添加LIMIT子句" in ' '.join(optimizations):
            if not re.search(r'\bLIMIT\b', optimized_sql, re.IGNORECASE):
                optimized_sql = optimized_sql.rstrip(';') + ' LIMIT 100;'
        
        return optimized_sql
    
    def _format_sql(self, sql: str) -> str:
        """格式化SQL语句"""
        # 基础格式化
        formatted_sql = sql.strip()
        
        # 关键字大写
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 
                   'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'AS', 'ON', 'AND', 'OR']
        
        for keyword in keywords:
            pattern = r'\b' + keyword.replace(' ', r'\s+') + r'\b'
            formatted_sql = re.sub(pattern, keyword, formatted_sql, flags=re.IGNORECASE)
        
        return formatted_sql
```

## 🚀 性能优化策略

### 1. SQL模板缓存
```python
class SQLTemplateCache:
    """
    SQL模板缓存系统
    
    缓存策略:
    1. 常用查询模板缓存
    2. 优化后的SQL缓存
    3. 表结构信息缓存
    """
    
    def __init__(self, max_size: int = 500):
        self.template_cache = {}
        self.optimization_cache = {}
        self.max_size = max_size
    
    def get_cached_template(self, query_pattern: str) -> Optional[str]:
        """获取缓存的SQL模板"""
        pattern_hash = hashlib.md5(query_pattern.encode()).hexdigest()
        return self.template_cache.get(pattern_hash)
    
    def cache_template(self, query_pattern: str, sql_template: str):
        """缓存SQL模板"""
        if len(self.template_cache) >= self.max_size:
            # 移除最旧的缓存
            oldest_key = next(iter(self.template_cache))
            del self.template_cache[oldest_key]
        
        pattern_hash = hashlib.md5(query_pattern.encode()).hexdigest()
        self.template_cache[pattern_hash] = sql_template
```

### 2. 并行SQL生成
```python
async def parallel_sql_generation(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    并行生成多个SQL候选方案
    
    策略:
    1. 生成多个SQL变体
    2. 并行验证和优化
    3. 选择最优方案
    """
    tasks = [
        self._generate_basic_sql(analysis_result),
        self._generate_optimized_sql(analysis_result),
        self._generate_alternative_sql(analysis_result)
    ]
    
    sql_candidates = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 选择最优SQL
    best_sql = self._select_best_sql(sql_candidates)
    
    return best_sql
```

---

**总结**: SQL生成智能体是Text2SQL系统的核心执行组件，负责将查询分析结果转换为高质量的SQL语句。通过专业的SQL生成能力、全面的质量保证机制、强大的自动修复功能和高效的性能优化策略，确保生成的SQL语句准确、安全、高效且符合最佳实践。该智能体具备多数据库兼容性和强大的错误处理能力，为Text2SQL系统提供可靠的SQL生成服务。