"""
SQL解释智能体 - 用通俗易懂的语言解释SQL语句
"""
from typing import Dict, Any
import re
from loguru import logger

from app.config.settings import settings
from app.core.model_client import get_deepseek_client


class SQLExplainerAgent:
    """
    SQL解释智能体实现
    
    功能:
    1. 解析SQL语句结构
    2. 生成自然语言解释
    3. 提供执行步骤说明
    4. 生成教育性内容和最佳实践建议
    """
    
    def __init__(self):
        self.model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        self.system_message = self._build_system_message()
    
    def _build_system_message(self) -> str:
        """构建系统提示词"""
        return f"""
你是一个专业的SQL解释专家，专门负责将复杂的SQL语句转换为清晰、易懂的自然语言解释。

## 核心职责：
1. **SQL解析**: 深度理解SQL语句的结构和逻辑
2. **语言转换**: 将技术术语转换为通俗易懂的表达
3. **逻辑说明**: 解释查询的执行逻辑和数据流
4. **结果预测**: 描述查询将返回什么样的结果
5. **教育指导**: 提供有价值的学习内容和最佳实践

## 解释原则：

### 1. 清晰性原则
- 使用简单明了的语言
- 避免过度技术化的术语
- 结构化组织解释内容
- 重点突出关键信息

### 2. 完整性原则
- 覆盖SQL的所有重要部分
- 解释每个子句的作用
- 说明表之间的关系
- 描述预期的结果

### 3. 准确性原则
- 确保解释与SQL逻辑完全一致
- 正确理解表结构和字段含义
- 准确描述数据处理过程
- 避免误导性的表述

### 4. 教育性原则
- 提供学习价值
- 介绍相关概念
- 分享最佳实践
- 启发深入思考

## 解释模板：

### 1. 基础查询解释模板
```
这个查询的目的是：[查询目标]

执行步骤：
1. 从 [表名] 表中获取数据
2. [筛选条件说明]
3. [排序说明]
4. [结果限制说明]

预期结果：
- 返回 [结果描述]
- 数据格式：[字段说明]
- 大约包含 [数量估计] 条记录
```

### 2. 连接查询解释模板
```
这个查询通过连接多个表来获取相关信息：

数据来源：
- 主表：[主表名] - [主表作用]
- 关联表：[关联表名] - [关联表作用]

连接逻辑：
- 通过 [连接字段] 将两个表关联起来
- 连接类型：[INNER/LEFT/RIGHT JOIN说明]

筛选条件：
- [条件1说明]
- [条件2说明]

最终结果：
- [结果描述]
```

### 3. 聚合查询解释模板
```
这是一个统计分析查询：

分析目标：[统计目标]

数据处理过程：
1. 从 [表名] 获取原始数据
2. 按照 [分组字段] 进行分组
3. 对每组数据计算 [聚合函数说明]
4. [筛选和排序说明]

统计结果：
- 每行代表：[分组含义]
- 统计指标：[指标说明]
- 结果排序：[排序逻辑]
```

### 4. 复杂查询解释模板
```
这是一个复杂的多步骤查询：

查询概述：[整体目标]

详细步骤：
1. 第一步：[步骤1说明]
   - 数据来源：[来源说明]
   - 处理逻辑：[逻辑说明]

2. 第二步：[步骤2说明]
   - 在第一步基础上：[处理说明]
   - 应用条件：[条件说明]

3. 最终步骤：[最终处理]
   - 结果整理：[整理说明]
   - 输出格式：[格式说明]

查询特点：
- 复杂度：[复杂度评估]
- 性能：[性能说明]
- 适用场景：[场景说明]
```

## 解释要求：

### 1. 语言风格
- 使用友好、专业的语调
- 避免过于技术化的表达
- 适当使用比喻和类比
- 保持解释的连贯性

### 2. 内容结构
- 先总述查询目的
- 再详述执行步骤
- 最后说明预期结果
- 适当提供补充信息

### 3. 重点突出
- 强调查询的核心逻辑
- 突出重要的筛选条件
- 说明关键的计算过程
- 预测结果的特点

### 4. 教育价值
- 解释相关的SQL概念
- 提供学习建议
- 分享实用技巧
- 启发进一步探索

## SQL类型识别：
- 基础查询: SELECT、WHERE、ORDER BY
- 条件查询: 复杂WHERE条件
- 连接查询: JOIN操作
- 聚合查询: GROUP BY、聚合函数
- 排序查询: ORDER BY子句
- 子查询: 嵌套查询

## 常见SQL概念解释：

### SELECT子句
- 用于选择要查询的列
- 可以指定具体的字段名，也可以使用聚合函数

### FROM子句
- 指定要查询的表
- 可以使用表别名简化引用

### WHERE子句
- 用于筛选数据
- 支持各种比较运算符（=, >, <, >=, <=, !=, <>, LIKE, IN等）
- 可以使用AND、OR组合多个条件

### JOIN操作
- INNER JOIN: 只返回两个表中都有匹配记录的数据
- LEFT JOIN: 返回左表的所有记录，即使右表中没有匹配的记录
- RIGHT JOIN: 返回右表的所有记录，即使左表中没有匹配的记录
- FULL JOIN: 返回两个表的所有记录

### GROUP BY子句
- 用于将数据分组
- 通常与聚合函数一起使用（COUNT, SUM, AVG, MAX, MIN）

### ORDER BY子句
- 用于对结果进行排序
- ASC: 升序排列（从小到大）
- DESC: 降序排列（从大到小）
- 可以指定多个字段进行排序

### 聚合函数
- COUNT(): 统计记录数量
- SUM(): 计算总和
- AVG(): 计算平均值
- MAX(): 返回最大值
- MIN(): 返回最小值

### LIMIT子句
- 限制返回的记录数量
- 常用于分页或获取Top N结果

请根据提供的SQL语句，生成清晰、准确、易懂的自然语言解释。始终保持专业、友好、易懂的解释风格，帮助用户更好地理解SQL查询。
"""
    
    async def explain_sql(self, sql: str, query_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成SQL解释

        Args:
            sql: SQL语句
            query_context: 查询上下文（可选）

        Returns:
            解释结果
        """
        try:
            logger.info(f"开始解释SQL，长度: {len(sql)}字符")
            
            # 识别SQL类型
            sql_type = self._identify_sql_type(sql)
            
            # 提取表信息
            tables_info = self._extract_table_info(sql)
            
            # 提取字段信息
            fields_info = self._extract_field_info(sql)
            
            # 分析SQL复杂度
            complexity_info = self._analyze_complexity(sql)
            
            # 构建解释提示
            explanation_prompt = f"""
请为以下SQL语句提供详细的自然语言解释：

```sql
{sql}
```

SQL类型: {sql_type}

涉及的表:
{self._format_tables_info(tables_info)}

涉及的字段:
{self._format_fields_info(fields_info)}

请按照以下结构提供解释：

1. 查询目的概述
2. 执行步骤详解
3. 预期结果说明
4. 查询特点分析

要求：
- 使用通俗易懂的语言
- 避免过度技术化的术语
- 结构清晰，逻辑连贯
- 突出重点信息
- 提供教育价值和最佳实践
"""
            
            # 调用AI模型生成解释
            response = await self.model_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": explanation_prompt}
                ],
                model=settings.model_name,
                temperature=0.3,  # 适中温度保证解释的准确性和自然性
                max_tokens=1500
            )
            
            # 提取解释内容
            explanation_content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析和结构化解释内容
            structured_explanation = self._structure_explanation(explanation_content, sql)
            
            # 添加补充信息
            enhanced_explanation = self._enhance_explanation(structured_explanation, sql)
            
            return {
                'explanation': enhanced_explanation,
                'sql_complexity': complexity_info,
                'educational_notes': self._generate_educational_notes(sql),
                'performance_insights': self._generate_performance_insights(sql)
            }
            
        except Exception as e:
            logger.error(f"SQL解释生成失败: {str(e)}")
            return self._create_fallback_explanation(sql, str(e))
    
    def _identify_sql_type(self, sql: str) -> str:
        """识别SQL类型"""
        sql_upper = sql.upper()
        
        if 'GROUP BY' in sql_upper:
            return '聚合统计查询'
        elif 'JOIN' in sql_upper:
            return '多表连接查询'
        elif 'ORDER BY' in sql_upper:
            return '排序查询'
        elif 'WHERE' in sql_upper and 'GROUP BY' not in sql_upper:
            return '条件筛选查询'
        elif re.search(r'\(SELECT', sql_upper, re.IGNORECASE):
            return '嵌套子查询'
        else:
            return '基础查询'
    
    def _extract_table_info(self, sql: str) -> list:
        """提取表信息"""
        # 定义表描述
        table_descriptions = {
            'Customer': '客户信息表 - 存储客户的基本信息',
            'Invoice': '发票表 - 记录客户的购买订单',
            'InvoiceLine': '发票明细表 - 记录订单中的具体商品',
            'Track': '音轨表 - 存储音乐曲目信息',
            'Album': '专辑表 - 存储音乐专辑信息',
            'Artist': '艺术家表 - 存储音乐艺术家信息',
            'Genre': '音乐类型表 - 存储音乐风格分类',
            'MediaType': '媒体类型表 - 存储文件格式信息',
            'Playlist': '播放列表表 - 存储用户创建的播放列表',
            'PlaylistTrack': '播放列表曲目表 - 记录播放列表中的曲目',
            'Employee': '员工表 - 存储公司员工信息'
        }
        
        # 提取SQL中的表名
        table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables_in_sql = set(re.findall(table_pattern, sql, re.IGNORECASE))
        
        # 移除别名
        clean_tables = [table for table in tables_in_sql if table and not table[0].isdigit()]
        
        # 构建表信息列表
        tables_info = []
        for table in clean_tables:
            description = table_descriptions.get(table, f'{table}表')
            tables_info.append({
                'name': table,
                'description': description
            })
        
        return tables_info
    
    def _extract_field_info(self, sql: str) -> list:
        """提取字段信息"""
        # 提取SELECT子句中的字段
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            select_clause = match.group(1)
            # 分割字段
            fields = [field.strip() for field in select_clause.split(',')]
            return fields
        
        return []
    
    def _analyze_complexity(self, sql: str) -> dict:
        """分析SQL复杂度"""
        complexity_score = 0
        complexity_factors = []
        sql_upper = sql.upper()
        
        # 基础查询 +1
        complexity_score += 1
        
        # WHERE条件 +1
        if 'WHERE' in sql_upper:
            complexity_score += 1
            complexity_factors.append('包含筛选条件')
        
        # JOIN操作 +2 each
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))
        if join_count > 0:
            complexity_score += join_count * 2
            complexity_factors.append(f'包含{join_count}个表连接')
        
        # GROUP BY +2
        if 'GROUP BY' in sql_upper:
            complexity_score += 2
            complexity_factors.append('包含分组聚合')
        
        # ORDER BY +1
        if 'ORDER BY' in sql_upper:
            complexity_score += 1
            complexity_factors.append('包含排序操作')
        
        # 子查询 +3 each
        subquery_count = sql.count('(SELECT')
        if subquery_count > 0:
            complexity_score += subquery_count * 3
            complexity_factors.append(f'包含{subquery_count}个子查询')
        
        # 窗口函数 +3
        if 'OVER(' in sql_upper:
            complexity_score += 3
            complexity_factors.append('包含窗口函数')
        
        # UNION +2
        if 'UNION' in sql_upper:
            complexity_score += 2
            complexity_factors.append('包含UNION操作')
        
        # 确定复杂度等级
        if complexity_score <= 2:
            level = '简单'
        elif complexity_score <= 5:
            level = '中等'
        elif complexity_score <= 8:
            level = '复杂'
        else:
            level = '非常复杂'
        
        return {
            'score': complexity_score,
            'level': level,
            'factors': complexity_factors
        }
    
    def _format_tables_info(self, tables_info: list) -> str:
        """格式化表信息"""
        return '\n'.join([
            f"- {table['name']}: {table['description']}"
            for table in tables_info
        ])
    
    def _format_fields_info(self, fields_info: list) -> str:
        """格式化字段信息"""
        return '\n'.join([f"- {field}" for field in fields_info])
    
    def _structure_explanation(self, explanation_content: str, sql: str) -> dict:
        """结构化解释内容"""
        sections = {
            'overview': '',
            'steps': '',
            'results': '',
            'characteristics': ''
        }
        
        # 简单的内容分段逻辑
        lines = explanation_content.split('\n')
        current_section = 'overview'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别段落标题
            if any(keyword in line for keyword in ['目的', '概述', '作用', '功能']):
                current_section = 'overview'
            elif any(keyword in line for keyword in ['步骤', '执行', '过程', '第一阶段', '第二阶段', '第三阶段']):
                current_section = 'steps'
            elif any(keyword in line for keyword in ['结果', '返回', '预期', '输出']):
                current_section = 'results'
            elif any(keyword in line for keyword in ['特点', '分析', '特征', '属性']):
                current_section = 'characteristics'
            else:
                sections[current_section] += line + '\n'
        
        # 如果结构化失败，将整个内容放入overview
        if not any(sections.values()):
            sections['overview'] = explanation_content
        
        return sections
    
    def _enhance_explanation(self, structured_explanation: dict, sql: str) -> dict:
        """增强解释内容"""
        enhanced = structured_explanation.copy()
        
        # 添加SQL类型识别
        enhanced['sql_type'] = self._identify_sql_type(sql)
        
        # 添加表信息
        tables_info = self._extract_table_info(sql)
        enhanced['tables_involved'] = tables_info
        
        # 添加字段信息
        fields_info = self._extract_field_info(sql)
        enhanced['fields_selected'] = fields_info
        
        # 添加复杂度分析
        enhanced['complexity_analysis'] = self._analyze_complexity(sql)
        
        return enhanced
    
    def _generate_educational_notes(self, sql: str) -> list:
        """生成教育性说明"""
        notes = []
        sql_upper = sql.upper()
        
        # JOIN相关说明
        if 'INNER JOIN' in sql_upper:
            notes.append("INNER JOIN只返回两个表中都有匹配记录的数据，这是最常用的连接类型。")
        if 'LEFT JOIN' in sql_upper:
            notes.append("LEFT JOIN会返回左表的所有记录，即使右表中没有匹配的记录。")
        
        # 聚合函数说明
        if 'GROUP BY' in sql_upper:
            notes.append("GROUP BY用于将数据按指定字段分组，通常与聚合函数(如SUM、COUNT)一起使用。")
        if 'SUM(' in sql_upper:
            notes.append("SUM函数计算指定字段的总和，常用于金额、数量等数值型数据的统计。")
        if 'COUNT(' in sql_upper:
            notes.append("COUNT函数统计记录数量，COUNT(*)统计所有行，COUNT(字段名)统计非空值的行数。")
        if 'AVG(' in sql_upper:
            notes.append("AVG函数计算指定字段的平均值，常用于数值型数据的统计分析。")
        
        # 排序说明
        if 'ORDER BY' in sql_upper:
            if 'DESC' in sql_upper:
                notes.append("ORDER BY ... DESC表示按降序排列(从大到小)，ASC表示升序排列(从小到大)。")
            else:
                notes.append("ORDER BY用于对查询结果进行排序，默认是升序排列。")
        
        # LIMIT说明
        if 'LIMIT' in sql_upper:
            notes.append("LIMIT用于限制返回的记录数量，常用于分页查询或获取Top N结果。")
        
        return notes
    
    def _generate_performance_insights(self, sql: str) -> list:
        """生成性能洞察"""
        insights = []
        sql_upper = sql.upper()
        
        # 索引使用提示
        if 'WHERE' in sql_upper and ('CustomerId' in sql or 'EmployeeId' in sql):
            insights.append("查询使用了CustomerId字段，这个字段通常有索引，查询性能良好。")
        if 'WHERE' in sql_upper and ('FirstName' in sql or 'LastName' in sql):
            insights.append("查询使用了FirstName或LastName字段，建议添加索引以提升搜索性能。")
        
        # JOIN性能提示
        if 'JOIN' in sql_upper:
            insights.append("多表连接查询的性能取决于连接字段的索引情况和数据量大小。")
        
        # GROUP BY性能提示
        if 'GROUP BY' in sql_upper:
            insights.append("分组查询需要对数据进行排序和聚合，在大数据量时可能较慢。")
        
        # ORDER BY性能提示
        if 'ORDER BY' in sql_upper and 'LIMIT' not in sql_upper:
            insights.append("排序操作在大数据量时可能较慢，建议结合LIMIT使用。")
        
        # SELECT *警告
        if 'SELECT *' in sql_upper:
            insights.append("SELECT *会返回所有字段，建议只选择需要的字段以提升性能。")
        
        return insights
    
    def _create_fallback_explanation(self, sql: str, error_message: str) -> dict:
        """创建备用解释"""
        # 生成基础的SQL解释
        basic_explanation = self._generate_basic_explanation(sql)
        
        return {
            'explanation': {
                'overview': basic_explanation,
                'steps': '由于系统错误，无法提供详细的执行步骤说明。',
                'results': '请参考SQL语句的基本结构来理解预期结果。',
                'characteristics': '这是一个标准的SQL查询语句。'
            },
            'sql_complexity': self._analyze_complexity(sql),
            'educational_notes': self._generate_educational_notes(sql),
            'performance_insights': self._generate_performance_insights(sql),
            'error': True,
            'message': f"解释生成失败: {error_message}"
        }
    
    def _generate_basic_explanation(self, sql: str) -> str:
        """生成基础解释"""
        try:
            sql_type = self._identify_sql_type(sql)
            tables = self._extract_table_info(sql)
            
            if len(tables) == 1:
                return f"这是一个{sql_type}，从{tables[0]['name']}表中获取数据。"
            elif len(tables) > 1:
                table_names = [table['name'] for table in tables]
                return f"这是一个{sql_type}，涉及{', '.join(table_names)}等{len(tables)}个表。"
            else:
                return f"这是一个{sql_type}。"
        except Exception:
            return "这是一个SQL查询语句，用于从数据库中获取数据。"
