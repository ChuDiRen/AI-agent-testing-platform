"""
可视化推荐智能体 - 基于数据特征智能推荐图表类型和配置
"""
import json
from typing import Dict, Any, List, Optional
from loguru import logger

from app.config.settings import settings
from app.core.model_client import get_deepseek_client


class VisualizationRecommendationEngine:
    """可视化推荐引擎"""
    
    def __init__(self):
        self.model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        self.system_message = self._build_system_message()
    
    def _build_system_message(self) -> str:
        """构建系统提示词"""
        return f"""
你是一个专业的数据可视化专家。你的任务是根据SQL查询结果和用户意图，智能推荐最适合的数据可视化方案。

## 你的专业技能：
1. **数据分析**: 深度分析数据特征、类型、分布和关系
2. **意图理解**: 准确理解用户的分析目标和可视化需求
3. **图表选择**: 基于数据特征选择最适合的图表类型
4. **配置优化**: 生成详细的图表配置和样式设置
5. **用户体验**: 优化可视化效果和交互体验

## 推荐标准：
1. **数据适配性**: 图表类型与数据特征高度匹配
2. **意图契合度**: 可视化方案符合用户分析目标
3. **视觉效果**: 图表美观、清晰、易于理解
4. **交互体验**: 提供良好的用户交互和探索体验
5. **性能考虑**: 考虑数据量对可视化性能的影响

## 支持的图表类型：
- **柱状图**: 适合分类数据对比
- **折线图**: 适合时间序列和趋势分析
- **饼图**: 适合占比和构成分析
- **散点图**: 适合相关性和分布分析
- **表格**: 适合详细数据展示
- **热力图**: 适合多维数据关系展示
- **面积图**: 适合累积和趋势展示

## 推荐流程：
1. 分析数据特征（类型、分布、关系）
2. 理解查询意图（对比、趋势、占比等）
3. 生成候选可视化方案
4. 评估和排序推荐方案
5. 生成详细的图表配置
6. 提供推荐理由和数据洞察

## 输出格式：
请以JSON格式返回推荐结果，包含：
- primary_recommendation: 主推荐方案
- alternative_recommendations: 备选方案（2-3个）
- data_insights: 数据洞察
- recommendation_reasoning: 推荐理由

## 图表配置要求：
- 为每种图表类型生成完整的配置参数
- 包含标题、坐标轴、颜色等设置
- 确保配置参数的正确性和完整性
- 提供清晰的配置说明

请始终保持专业、准确、用户友好的推荐标准。
"""

    async def recommend_visualization(self, sql: str, query_result: Dict[str, Any],
                                     user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        推荐可视化方案
        
        Args:
            sql: 原始SQL查询语句
            query_result: 查询结果数据
            user_context: 用户上下文信息
        
        Returns:
            包含推荐方案的详细信息
        """
        try:
            logger.info(f"开始可视化推荐，数据量: {len(query_result.get('data', []))}条")
            
            # 1. 分析数据特征
            data_characteristics = await self._analyze_data_characteristics(query_result)
            
            # 2. 分析查询意图
            query_intent = await self._analyze_query_intent(sql)
            
            # 3. 生成候选可视化方案
            candidate_charts = await self._generate_candidate_charts(
                data_characteristics, query_intent, user_context
            )
            
            # 4. 评估和排序推荐方案
            ranked_recommendations = await self._rank_recommendations(
                candidate_charts, data_characteristics, query_intent
            )
            
            # 5. 生成详细配置
            detailed_recommendations = await self._generate_detailed_configs(
                ranked_recommendations, query_result
            )
            
            # 6. 构建最终响应
            return {
                'success': True,
                'primary_recommendation': detailed_recommendations[0],
                'alternative_recommendations': detailed_recommendations[1:3],
                'data_insights': self._generate_data_insights(data_characteristics),
                'recommendation_reasoning': self._generate_reasoning(
                    data_characteristics, query_intent, ranked_recommendations[0]
                )
            }
            
        except Exception as e:
            logger.error(f"可视化推荐失败: {str(e)}")
            return await self._generate_fallback_recommendation(query_result, str(e))
    
    async def _analyze_data_characteristics(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据特征"""
        try:
            data = query_result.get('data', [])
            
            if not data:
                return {
                    'column_count': 0,
                    'row_count': 0,
                    'has_numeric': False,
                    'has_categorical': False,
                    'has_temporal': False,
                    'data_types': {},
                    'sample_data': []
                }
            
            columns = query_result.get('columns', [])
            
            # 分析列类型
            data_types = {}
            for col in columns:
                if len(data) > 0:
                    data_types[col] = self._determine_column_type(data[0][col])
            
            # 计算统计信息
            numeric_columns = [col for col, dtype in data_types.items() if dtype == 'numeric']
            categorical_columns = [col for col, dtype in data_types.items() if dtype == 'categorical']
            
            return {
                'column_count': len(columns),
                'row_count': len(data),
                'has_numeric': len(numeric_columns) > 0,
                'has_categorical': len(categorical_columns) > 0,
                'has_temporal': any(dtype == 'datetime' for dtype in data_types.values()),
                'data_types': data_types,
                'sample_data': data[:5] if len(data) > 5 else data
            }
            
        except Exception as e:
            logger.error(f"数据分析失败: {str(e)}")
            return {
                'column_count': 0,
                'row_count': 0,
                'has_numeric': False,
                'has_categorical': False,
                'has_temporal': False,
                'data_types': {},
                'sample_data': []
            }
    
    def _determine_column_type(self, value: Any) -> str:
        """确定列的数据类型"""
        if value is None:
            return 'unknown'
        
        value_type = type(value).__name__
        
        if value_type in ['int', 'float']:
            return 'numeric'
        elif value_type == 'str':
            return 'categorical'
        elif 'datetime' in value_type:
            return 'datetime'
        else:
            return 'unknown'
    
    async def _analyze_query_intent(self, sql: str) -> Dict[str, Any]:
        """分析查询意图"""
        sql_lower = sql.lower()
        
        intent_type = 'exploration'
        analysis_goal = '探索数据'
        
        if any(word in sql_lower for word in ['统计', '总和', '平均', '最大', '最小', 'count', 'sum', 'avg', 'max', 'min']):
            intent_type = 'statistics'
            analysis_goal = '数据分析'
        elif any(word in sql_lower for word in ['对比', '比较', '排名', '前', '最多', '最少', 'top', 'bottom']):
            intent_type = 'comparison'
            analysis_goal = '数据对比'
        elif any(word in sql_lower for word in ['趋势', '增长', '下降', '时间', '日期', '月', '年']):
            intent_type = 'trend'
            analysis_goal = '趋势分析'
        elif any(word in sql_lower for word in ['占比', '比例', '分布', '构成', '部分']):
            intent_type = 'proportion'
            analysis_goal = '占比分析'
        elif 'group' in sql_lower:
            intent_type = 'comparison'
            analysis_goal = '分组比较'
        
        return {
            'query_type': intent_type,
            'analysis_goal': analysis_goal,
            'description': f"基于SQL关键词推断的查询意图: {intent_type}"
        }
    
    async def _generate_candidate_charts(self, data_characteristics: Dict[str, Any],
                                      query_intent: Dict[str, Any],
                                      user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成候选可视化方案"""
        candidates = []
        
        has_numeric = data_characteristics.get('has_numeric', False)
        has_categorical = data_characteristics.get('has_categorical', False)
        query_type = query_intent.get('query_type', 'exploration')
        
        # 1. 表格（默认，适合详细数据展示）
        candidates.append({
            'type': 'table',
            'score': 60,
            'description': '表格展示适合查看详细数据',
            'suitability_score': self._calculate_suitability_score(
                data_characteristics, query_type, 'table'
            )
        })
        
        # 2. 柱状图（适合分类+数值）
        if has_categorical and has_numeric:
            candidates.append({
                'type': 'bar',
                'score': 85,
                'description': '柱状图适合展示分类数据的对比',
                'suitability_score': self._calculate_suitability_score(
                    data_characteristics, query_type, 'bar'
                )
            })
        
        # 3. 折线图（适合时间+数值）
        if has_numeric and data_characteristics.get('has_temporal', False):
            candidates.append({
                'type': 'line',
                'score': 80,
                'description': '折线图适合展示时间序列和趋势',
                'suitability_score': self._calculate_suitability_score(
                    data_characteristics, query_type, 'line'
                )
            })
        
        # 4. 饼图（适合分类占比）
        if has_categorical and query_type == 'proportion':
            candidates.append({
                'type': 'pie',
                'score': 75,
                'description': '饼图适合展示分类数据的占比和构成',
                'suitability_score': self._calculate_suitability_score(
                    data_characteristics, query_type, 'pie'
                )
            })
        
        # 5. 散点图（适合数值+数值）
        if has_numeric and len(data_characteristics.get('sample_data', [])) > 2:
            candidates.append({
                'type': 'scatter',
                'score': 70,
                'description': '散点图适合展示两个数值型字段的关系',
                'suitability_score': self._calculate_suitability_score(
                    data_characteristics, query_type, 'scatter'
                )
            })
        
        return candidates
    
    def _calculate_suitability_score(self, data_characteristics: Dict[str, Any],
                                  query_type: Dict[str, Any],
                                  chart_type: str) -> float:
        """计算适配度分数"""
        score = 50.0  # 基础分
        
        # 数据适配性（30分）
        if self._check_data_compatibility(data_characteristics, chart_type):
            score += 30
        
        # 意图契合度（30分）
        if self._check_chart_intent_match(query_type, chart_type):
            score += 30
        
        # 数据特征适配（20分）
        if self._check_feature_compatibility(data_characteristics, chart_type):
            score += 20
        
        return score
    
    def _check_data_compatibility(self, data_characteristics: Dict[str, Any], chart_type: str) -> bool:
        """检查数据兼容性"""
        if chart_type == 'table':
            return True
        
        has_numeric = data_characteristics.get('has_numeric', False)
        has_categorical = data_characteristics.get('has_categorical', False)
        
        if chart_type == 'bar':
            return has_categorical and has_numeric
        elif chart_type == 'line':
            return has_numeric and data_characteristics.get('has_temporal', False)
        elif chart_type == 'pie':
            return has_categorical
        elif chart_type == 'scatter':
            return has_numeric and len(data_characteristics.get('sample_data', [])) >= 2
        else:
            return False
    
    def _check_chart_intent_match(self, query_type: Dict[str, Any], chart_type: str) -> bool:
        """检查图表意图匹配"""
        intent = query_type.get('query_type', 'exploration')
        
        if chart_type == 'bar' and intent == 'comparison':
            return True
        elif chart_type == 'line' and intent == 'trend':
            return True
        elif chart_type == 'pie' and intent == 'proportion':
            return True
        elif chart_type == 'scatter' and intent in ['comparison', 'exploration']:
            return True
        else:
            return False
    
    def _check_feature_compatibility(self, data_characteristics: Dict[str, Any], chart_type: str) -> bool:
        """检查特征兼容性"""
        if chart_type == 'line' and data_characteristics.get('has_temporal', False):
            return True
        elif chart_type in ['bar', 'scatter'] and data_characteristics.get('has_numeric', False):
            return True
        else:
            return False
    
    async def _rank_recommendations(self, candidates: List[Dict[str, Any]],
                                   data_characteristics: Dict[str, Any],
                                   query_type: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估和排序推荐方案"""
        return sorted(candidates, key=lambda x: x['score'], reverse=True)
    
    async def _generate_detailed_configs(self, ranked_recommendations: List[Dict[str, Any]],
                                     query_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成详细的图表配置"""
        detailed_configs = []
        
        columns = query_result.get('columns', [])
        data = query_result.get('data', [])
        
        for i, recommendation in enumerate(ranked_recommendations):
            chart_type = recommendation['type']
            config = self._generate_chart_config(chart_type, columns, data)

            detailed_configs.append({
                **recommendation,
                'config': config,
                'rank': i + 1
            })

        return detailed_configs
    
    def _generate_chart_config(self, chart_type: str, columns: List[str], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成图表配置"""
        config = {
            'chart_type': chart_type,
            'title': self._generate_chart_title(chart_type, columns),
            'xAxis': self._generate_x_axis(chart_type, columns, data),
            'yAxis': self._generate_y_axis(chart_type, columns, data),
            'series': self._generate_series(chart_type, columns),
            'colorPalette': self._generate_color_palette(),
            'legend': self._generate_legend(chart_type, columns),
            'tooltip': self._generate_tooltip(chart_type),
            'grid': self._generate_grid(chart_type),
            'dataZoom': chart_type in ['line', 'scatter'],
            'animation': True
        }
        
        return config
    
    def _generate_chart_title(self, chart_type: str, columns: List[str]) -> str:
        """生成图表标题"""
        if chart_type == 'bar':
            return f"数据对比分析 - {columns[0] if columns else '数据列'}"
        elif chart_type == 'line':
            return f"趋势分析 - {columns[0] if columns else '数据列'} 随时间变化"
        elif chart_type == 'pie':
            return f"占比分析 - {columns[0] if columns else '数据列'} 构成"
        elif chart_type == 'scatter':
            return f"关系分析 - {columns[0]} vs {columns[1] if len(columns) > 1 else 'Y轴'}"
        elif chart_type == 'table':
            return "详细数据表格"
        else:
            return "数据可视化"
    
    def _generate_x_axis(self, chart_type: str, columns: List[str], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成X轴配置"""
        numeric_columns = [col for col in columns if self._is_numeric_column(col, data)]
        
        if chart_type == 'bar':
            return {
                'type': 'category',
                'data': numeric_columns if numeric_columns else columns[:1]
            }
        elif chart_type in ['line', 'scatter']:
            if len(numeric_columns) >= 1:
                return {
                    'type': 'value',
                    'data': numeric_columns[0] if len(numeric_columns) > 0 else 'category'
                }
            else:
                return {
                    'type': 'category',
                    'data': columns[:1]
                }
        else:
            return {
                'type': 'category',
                'data': columns[:1]
            }
    
    def _generate_y_axis(self, chart_type: str, columns: List[str], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成Y轴配置"""
        numeric_columns = [col for col in columns if self._is_numeric_column(col, data)]
        
        if chart_type in ['bar', 'line']:
            return {
                'type': 'value',
                'name': numeric_columns[0] if numeric_columns else columns[0]
            }
        elif chart_type == 'scatter' and len(numeric_columns) >= 2:
            return {
                'type': 'value',
                'name': numeric_columns[1] if len(numeric_columns) >= 2 else numeric_columns[0]
            }
        else:
            return None
    
    def _generate_series(self, chart_type: str, columns: List[str], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成系列配置"""
        if chart_type == 'bar':
            return [{
                'name': column,
                'type': 'bar'
            } for column in columns[:3]]  # 最多3个柱状图
        elif chart_type == 'line':
            return [{
                'name': column,
                'type': 'line'
            } for column in columns[:2]]  # 最多2条折线
        elif chart_type == 'pie':
            return [{
                'name': column,
                'type': 'pie'
            } for column in columns]
        elif chart_type == 'scatter':
            return [{
                'name': '散点图',
                'data': data,
                'type': 'scatter',
                'symbolSize': 8
            }]
        else:
            return [{
                'name': '数据',
                'type': chart_type
            }]
    
    def _is_numeric_column(self, column: str, data: List[Dict[str, Any]]) -> bool:
        """检查是否为数值列"""
        if not data:
            return False
        
        first_value = data[0].get(column)
        return isinstance(first_value, (int, float)) and not isinstance(first_value, bool)
    
    def _generate_color_palette(self) -> List[str]:
        """生成调色板"""
        return [
            '#f0f9ff',  # Blue
            '#bae6fd',  # Green
            '#7dd3fc',  # Yellow
            '#2563eb',  # Purple
            '#06306f',  # Orange
            '#0891b2',  # Pink
            '#075985',  # Indigo
            '#0c4a6e',  # Cyan
            '#ff6b35'   # Lime
        ]
    
    def _generate_legend(self, chart_type: str, columns: List[str]) -> List[Dict[str, Any]]:
        """生成图例配置"""
        return [{
            'data': column,
            'name': column
        } for column in columns[:5]]
    
    def _generate_tooltip(self, chart_type: str) -> Dict[str, Any]:
        """生成提示框配置"""
        return {
            'trigger': 'axis',
            'axisPointer': 'shadow',
            'formatter': '{b}'
        }
    
    def _generate_grid(self, chart_type: str) -> Dict[str, Any]:
        """生成网格配置"""
        return {
            'left': chart_type in ['bar', 'line'],
            'top': chart_type == 'bar'
        }
    
    def _generate_data_insights(self, data_characteristics: Dict[str, Any]) -> List[str]:
        """生成数据洞察"""
        insights = []
        
        column_count = data_characteristics.get('column_count', 0)
        row_count = data_characteristics.get('row_count', 0)
        has_numeric = data_characteristics.get('has_numeric', False)
        has_categorical = data_characteristics.get('has_categorical', False)
        
        if row_count > 100:
            insights.append(f"数据集包含{row_count}行记录，建议考虑分页或筛选")
        
        if column_count > 10:
            insights.append(f"数据集包含{column_count}个字段，建议选择关键字段进行可视化")
        
        if has_numeric and has_categorical:
            insights.append("数据集包含数值型和分类型数据，适合使用柱状图或折线图进行对比分析")
        
        if data_characteristics.get('has_temporal', False):
            insights.append("建议考虑时间维度分析，使用折线图展示趋势")
        
        return insights
    
    def _generate_reasoning(self, data_characteristics: Dict[str, Any],
                       query_type: Dict[str, Any],
                       top_recommendation: Dict[str, Any]) -> str:
        """生成推荐理由"""
        chart_type = top_recommendation.get('type', '')
        score = top_recommendation.get('score', 0)
        
        reasoning_parts = []
        
        # 基于评分和类型的理由
        reasoning_parts.append(f"{chart_type}图表的适配度评分为{score:.1f}")
        
        # 基于数据特征的理由
        if chart_type == 'bar' and data_characteristics.get('has_categorical', False):
            reasoning_parts.append("数据主要为数值型，适合使用柱状图对比分析")
        elif chart_type == 'line' and data_characteristics.get('has_temporal', False):
            reasoning_parts.append("数据为数值型，适合使用折线图展示趋势")
        elif chart_type == 'pie' and data_character_type == 'proportion':
            reasoning_parts.append("需要查看占比构成，饼图能清晰展示各部分比例")
        elif chart_type == 'scatter' and data_characteristics.get('has_numeric', False):
            reasoning_parts.append("包含两个数值型字段，适合分析它们之间的关系")
        else:
            reasoning_parts.append(f"提供了{chart_type}图表作为可视化选项")
        
        return "、".join(reasoning_parts)
    
    async def _generate_fallback_recommendation(self, query_result: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """生成备用推荐"""
        return {
            'success': False,
            'error': True,
            'message': f"可视化推荐失败: {error_message}",
            'primary_recommendation': {
                'type': 'table',
                'config': {
                    'chart_type': 'table',
                    'title': '详细数据表格',
                    'columns': query_result.get('columns', []),
                    'data': query_result.get('data', []),
                    'pagination': True,
                    'pageSize': 20
                }
            },
            'alternative_recommendations': [],
            'data_insights': ['无法生成数据洞察'],
            'recommendation_reasoning': '发生错误，使用表格展示作为备用方案'
        }


class VisualizationRecommenderAgent:
    """
    可视化推荐智能体实现
    
    功能:
    1. 分析数据特征
    2. 理解查询意图
    3. 推荐最适合的可视化方案
    4. 生成详细的图表配置
    """
    
    def __init__(self):
        self.engine = VisualizationRecommendationEngine()
        self.model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        self.system_message = f"""
你是Text2SQL系统中的可视化推荐专家。你的任务是根据SQL查询结果和用户意图，智能推荐最适合的数据可视化方案。

## 你的专业技能：
1. **数据分析**: 深度分析数据特征、类型、分布和关系
2. **意图理解**: 准确理解用户的分析目标和可视化需求
3. **图表选择**: 基于数据特征选择最适合的图表类型
4. **配置优化**: 生成详细的图表配置和样式设置
5. **用户体验**: 优化可视化效果和交互体验

## 推荐标准：
1. **数据适配性**: 图表类型与数据特征高度匹配
2. **意图契合度**: 可视化方案符合用户分析目标
3. **视觉效果**: 图表美观、清晰、易于理解
4. **交互体验**: 提供良好的用户交互和探索体验
5. **性能考虑**: 考虑数据量对可视化性能的影响

## 支持的图表类型：
- **柱状图**: 适合分类数据对比
- **折线图**: 适合时间序列和趋势分析
- **饼图**: 适合占比和构成分析
- **散点图**: 适合相关性和分布分析
- **表格**: 适合详细数据展示

## 输出格式：
请以JSON格式返回推荐结果。
"""
    
    async def recommend_visualization(self, sql: str, query_result: Dict[str, Any], 
                                     user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """推荐可视化方案"""
        try:
            logger.info(f"开始可视化推荐")
            
            # 使用推荐引擎
            result = await self.engine.recommend_visualization(sql, query_result, user_context)
            
            logger.info(f"可视化推荐完成: {result.get('primary_recommendation', {}).get('type', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"可视化推荐失败: {str(e)}")
            return await self.engine._generate_fallback_recommendation(query_result, str(e))
