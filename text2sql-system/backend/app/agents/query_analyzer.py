"""
查询分析智能体 - 深度理解用户自然语言查询
"""
import json
import re
from typing import Dict, Any
from loguru import logger

from app.config.settings import settings
from app.core.model_client import get_deepseek_client


class QueryAnalyzerAgent:
    """
    查询分析智能体实现
    
    功能:
    1. 深度理解用户查询意图
    2. 识别查询相关的数据实体
    3. 映射到数据库结构
    4. 提供结构化分析结果
    """
    
    def __init__(self, db_schema: str):
        self.db_schema = db_schema
        self.model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        self.system_message = self._build_system_message()
    
    def _build_system_message(self) -> str:
        """构建系统提示词"""
        return f"""
你是一个专业的数据库查询分析专家。你的任务是深度分析用户的自然语言查询，理解其意图并识别相关的数据库实体。

## 核心职责：
1. **意图识别**: 准确理解用户想要执行的操作类型
2. **实体提取**: 识别查询中涉及的所有业务实体
3. **字段映射**: 将业务概念映射到具体的数据库字段
4. **关系分析**: 分析涉及的表之间的关联关系
5. **条件解析**: 解析查询中的筛选和排序条件

## 分析框架：

### 1. 查询意图分类
- **数据查询**: 获取特定数据记录
- **统计分析**: 计算总数、平均值、最大值等
- **排序展示**: 按某种规则排序显示数据
- **条件筛选**: 根据条件过滤数据
- **关联查询**: 跨表关联获取数据
- **时间分析**: 基于时间维度的数据分析

### 2. 实体识别模式
- **主体实体**: 查询的核心对象（如客户、订单、产品）
- **属性实体**: 实体的具体属性（如姓名、价格、日期）
- **关系实体**: 实体间的关联关系（如客户的订单、订单的商品）
- **条件实体**: 筛选和限制条件（如时间范围、数值区间）

### 3. 数据库映射规则
- **表名映射**: 业务实体到数据库表的映射
- **字段映射**: 属性描述到具体字段的映射
- **关系映射**: 业务关系到外键关联的映射
- **条件映射**: 自然语言条件到SQL条件的映射

## 数据库结构信息：
{self.db_schema}

## 分析输出格式：
请按照以下结构化格式输出分析结果：

```json
{{
  "query_intent": {{
    "type": "查询类型（query/statistics/sort/filter/join/time_analysis）",
    "description": "查询意图的详细描述",
    "complexity": "复杂度评级（simple/medium/complex）"
  }},
  "entities": {{
    "primary_entity": "主要查询实体",
    "secondary_entities": ["次要相关实体列表"],
    "attributes": ["涉及的属性字段列表"],
    "conditions": ["筛选条件列表"]
  }},
  "table_mapping": {{
    "primary_table": "主要数据表",
    "related_tables": ["相关表列表"],
    "join_conditions": ["表连接条件"],
    "required_fields": ["需要的字段列表"]
  }},
  "query_structure": {{
    "select_fields": ["需要选择的字段"],
    "where_conditions": ["WHERE条件"],
    "join_requirements": ["JOIN需求"],
    "group_by_fields": ["分组字段（如果需要）"],
    "order_by_fields": ["排序字段（如果需要）"],
    "limit_requirements": "限制条件（如果需要）"
  }},
  "analysis_confidence": "分析置信度（0-1）",
  "potential_issues": ["可能的问题或歧义"]
}}
```

## 特殊处理规则：

### 1. 时间表达处理
- "最近一个月" → 当前日期前30天
- "今年" → 当前年份
- "上季度" → 上一个季度的时间范围
- "去年同期" → 去年相同时间段

### 2. 数值表达处理
- "最高的" → ORDER BY DESC LIMIT
- "超过100" → WHERE field > 100
- "前10名" → ORDER BY DESC LIMIT 10
- "平均" → AVG()函数

### 3. 模糊表达处理
- "相关的" → 通过外键关联
- "类似的" → LIKE模糊匹配
- "大约" → 范围查询
- "经常" → 频次统计

### 4. 业务术语映射
- "客户" → Customer表
- "订单" → Invoice表
- "商品" → Track表
- "销售额" → Invoice.Total
- "购买记录" → InvoiceLine表

请始终使用专业、准确、详细的分析风格，为后续的SQL生成提供充分信息。
"""
    
    async def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        分析用户查询

        Args:
            user_query: 用户的自然语言查询

        Returns:
            结构化的分析结果
        """
        try:
            logger.info(f"开始分析查询: {user_query[:50]}...")
            
            # 构建分析提示
            analysis_prompt = f"""
请分析以下用户查询：

用户查询: "{user_query}"

请按照系统消息中定义的格式，提供详细的结构化分析结果。

要求：
- 准确理解用户查询的核心意图
- 识别所有相关的数据实体和字段
- 分析表之间的关联关系
- 确定查询的复杂度和类型
- 提供清晰的分析结果
"""
            
            # 调用AI模型进行分析
            response = await self.model_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": analysis_prompt}
                ],
                model=settings.model_name,
                temperature=0.1,  # 低温度确保分析的一致性
                max_tokens=2000
            )
            
            # 解析响应
            analysis_result = self._parse_analysis_response(response)
            
            logger.info(f"查询分析完成: {analysis_result.get('query_intent', {}).get('type', 'unknown')}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"查询分析失败: {str(e)}")
            return self._create_error_response(str(e))
    
    def _parse_analysis_response(self, response: dict) -> Dict[str, Any]:
        """解析AI响应内容"""
        try:
            # 提取消息内容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = content[json_start:json_end]
                analysis_result = json.loads(json_content)
                
                # 验证必要字段
                required_fields = ['query_intent', 'entities', 'table_mapping', 'query_structure', 'analysis_confidence']
                for field in required_fields:
                    if field not in analysis_result:
                        analysis_result[field] = self._create_default_field(field)
                
                return analysis_result
            else:
                # 如果没有找到JSON格式，返回文本分析
                return self._create_text_based_analysis(content)
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"JSON解析失败: {str(e)}")
            return self._create_text_based_analysis(response.get("choices", [{}])[0].get("message", {}).get("content", ""))
    
    def _create_default_field(self, field: str) -> Dict[str, Any]:
        """创建默认字段值"""
        defaults = {
            'query_intent': {'type': 'unknown', 'description': '无法确定查询意图', 'complexity': 'unknown'},
            'entities': {'primary_entity': '未确定', 'secondary_entities': [], 'attributes': [], 'conditions': []},
            'table_mapping': {'primary_table': 'Customer', 'related_tables': [], 'join_conditions': [], 'required_fields': ['*']},
            'query_structure': {'select_fields': ['*'], 'where_conditions': [], 'join_requirements': [], 'group_by_fields': [], 'order_by_fields': [], 'limit_requirements': ''},
            'analysis_confidence': 0.5,
            'potential_issues': ['解析失败，使用默认值']
        }
        return defaults.get(field, {})
    
    def _create_text_based_analysis(self, content: str) -> Dict[str, Any]:
        """基于文本内容创建分析结果"""
        # 简单的关键词提取
        query_lower = content.lower()
        
        # 推断查询意图
        if any(word in query_lower for word in ['最高', '最多', '最大', '最小', '总和', '平均']):
            intent_type = 'statistics'
            complexity = 'medium'
        elif any(word in query_lower for word in ['所有', '列表', '显示']):
            intent_type = 'query'
            complexity = 'simple'
        elif any(word in query_lower for word in ['分组', '分类', '类型', '分类统计']):
            intent_type = 'statistics'
            complexity = 'medium'
        else:
            intent_type = 'query'
            complexity = 'simple'
        
        return {
            'query_intent': {
                'type': intent_type,
                'description': f"基于文本内容推断的查询意图: {intent_type}",
                'complexity': complexity
            },
            'entities': {
                'primary_entity': '未确定（基于文本分析）',
                'secondary_entities': [],
                'attributes': [],
                'conditions': []
            },
            'table_mapping': {
                'primary_table': 'Customer',
                'related_tables': [],
                'join_conditions': [],
                'required_fields': ['*']
            },
            'query_structure': {
                'select_fields': ['*'],
                'where_conditions': [],
                'join_requirements': [],
                'group_by_fields': [],
                'order_by_fields': [],
                'limit_requirements': 'LIMIT 100'
            },
            'analysis_confidence': 0.3,
            'potential_issues': ['JSON解析失败，使用简单的文本分析'],
            'analysis_text': content
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            'error': True,
            'message': f"查询分析失败: {error_message}",
            'query_intent': {
                'type': 'error',
                'description': '分析过程中发生错误',
                'complexity': 'unknown'
            },
            'entities': {
                'primary_entity': '错误',
                'secondary_entities': [],
                'attributes': [],
                'conditions': []
            },
            'table_mapping': {
                'primary_table': 'Customer',
                'related_tables': [],
                'join_conditions': [],
                'required_fields': ['*']
            },
            'query_structure': {
                'select_fields': ['*'],
                'where_conditions': [],
                'join_requirements': [],
                'group_by_fields': [],
                'order_by_fields': [],
                'limit_requirements': 'LIMIT 10'
            },
            'analysis_confidence': 0.0,
            'potential_issues': [error_message]
        }
