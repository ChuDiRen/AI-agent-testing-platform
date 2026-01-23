"""
Text2SQL智能体协作流程控制器
"""
import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from app.config.settings import settings
from app.agents.query_analyzer import QueryAnalyzerAgent
from app.agents.sql_generator import SQLGeneratorAgent
from app.agents.sql_explainer import SQLExplainerAgent
from app.agents.sql_executor import get_sql_executor
from app.agents.visualization_recommender import VisualizationRecommenderAgent


class Text2SQLGraphFlow:
    """
    Text2SQL智能体协作流程控制器
    
    协作机制:
    1. 顺序执行: 智能体按照预定顺序依次执行
    2. 流式输出: 每个智能体的结果实时流式传输
    3. 上下文传递: 前一个智能体的输出作为后一个的输入
    4. 错误处理: 任一环节出错时的恢复机制
    5. 状态管理: 维护整个流程的执行状态
    """
    
    def __init__(self, db_type: str, db_schema: str):
        self.db_type = db_type
        self.db_schema = db_schema
        
        # 创建所有智能体
        self.agents = self._create_agents()
        
    def _create_agents(self) -> Dict[str, Any]:
        """创建所有智能体"""
        from app.core.model_client import get_deepseek_client
        
        model_client = get_deepseek_client(
            settings.deepseek_api_key,
            settings.deepseek_base_url
        )
        
        return {
            'query_analyzer': QueryAnalyzerAgent(self.db_schema, model_client),
            'sql_generator': SQLGeneratorAgent(self.db_type, model_client),
            'sql_explainer': SQLExplainerAgent(model_client),
            'sql_executor': get_sql_executor(),
            'visualization_recommender': VisualizationRecommenderAgent(model_client)
        }
    
    async def process_query(self, user_query: str, stream_callback):
        """处理用户查询的完整流程
        
        Args:
            user_query: 用户的自然语言查询
            stream_callback: 流式回调函数，用于发送实时消息
        
        Returns:
            完整的查询结果
        """
        try:
            logger.info(f"开始处理用户查询: {user_query[:50]}...")
            
            # 1. 查询分析
            await stream_callback({
                "source": "system",
                "content": "正在分析用户查询...",
                "is_final": False
            })
            
            analysis_result = await self._run_agent(
                "query_analyzer",
                user_query,
                stream_callback
            )
            
            if analysis_result.get('error', False):
                # 如果分析失败，提前结束
                await stream_callback({
                    "source": "system",
                    "content": f"查询分析失败: {analysis_result.get('message', '未知错误')}",
                    "is_final": True,
                    "error": True
                })
                return analysis_result
            
            # 2. SQL生成
            await stream_callback({
                "source": "system",
                "content": "正在生成SQL语句...",
                "is_final": False
            })
            
            sql_generation_result = await self._run_agent(
                "sql_generator",
                analysis_result,
                stream_callback
            )
            
            if sql_generation_result.get('error', False):
                # 如果SQL生成失败，提前结束
                await stream_callback({
                    "source": "system",
                    "content": f"SQL生成失败: {sql_generation_result.get('message', '未知错误')}",
                    "is_final": True,
                    "error": True
                })
                return sql_generation_result
            
            # 3. SQL解释
            await stream_callback({
                "source": "system",
                "content": "正在解释SQL语句...",
                "is_final": False
            })
            
            explanation_result = await self._run_agent(
                "sql_explainer",
                sql_generation_result.get('sql', ''),
                stream_callback
            )
            
            # 4. SQL执行
            await stream_callback({
                "source": "system",
                "content": "正在执行SQL查询...",
                "is_final": False
            })
            
            execution_result = await self._run_agent(
                "sql_executor",
                sql_generation_result.get('sql', ''),
                stream_callback
            )
            
            if not execution_result.get('success', False):
                # 如果SQL执行失败，仍然可以继续可视化推荐
                await stream_callback({
                    "source": "system",
                    "content": f"SQL执行失败: {execution_result.get('error', {}).get('message', '未知错误')}",
                    "is_final": True,
                    "error": True
                })
                return execution_result
            
            # 5. 可视化推荐
            await stream_callback({
                "source": "system",
                "content": "正在生成可视化推荐...",
                "is_final": False
            })
            
            visualization_result = await self.run_agent(
                "visualization_recommender",
                sql_generation_result.get('sql', ''),
                execution_result,
                stream_callback
            )
            
            # 6. 构建最终响应
            final_response = self._build_final_response(
                sql_generation_result,
                explanation_result,
                execution_result,
                visualization_result
            )
            
            # 发送最终结果
            await stream_callback({
                "source": "system",
                "content": "Text2SQL查询处理完成！",
                "is_final": True,
                "result": final_response
            })
            
            logger.info(f"查询处理完成")
            return final_response
            
        except Exception as e:
            logger.error(f"查询处理过程中发生错误: {str(e)}")
            await stream_callback({
                "source": "system",
                "content": f"处理过程中发生错误: {str(e)}",
                "is_final": True,
                "error": True
            })
            raise
    
    async def _run_agent(self, agent_name: str, input_data: Any, stream_callback):
        """运行单个智能体"""
        try:
            agent = self.agents.get(agent_name)
            if hasattr(agent, 'process'):
                result = await agent.process(input_data, stream_callback)
            else:
                logger.warning(f"智能体 {agent_name}没有process方法，直接返回输入数据")
                result = input_data
            return result
        except Exception as e:
            logger.error(f"智能体{agent_name}执行失败: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def _build_final_response(self, sql_result: Dict[str, Any], 
                         explanation_result: Dict[str, Any],
                         execution_result: Dict[str, Any],
                         visualization_result: Dict[str, Any]) -> Dict[str, Any]:
        """构建最终响应"""
        return {
            'sql': sql_result.get('sql', ''),
            'explanation': explanation_result.get('explanation', {}).get('overview', ''),
            'results': execution_result.get('data', []),
            'row_count': execution_result.get('row_count', 0),
            'columns': execution_result.get('columns', []),
            'visualization_type': visualization_result.get('primary_recommendation', {}).get('type', ''),
            'visualization_config': visualization_result.get('primary_recommendation', {}).get('config', {}),
            'metadata': {
                'query_execution_time': execution_result.get('execution_time', 0),
                'database_type': self.db_type,
                'timestamp': execution_result.get('metadata', {}).get('timestamp', '')
            }
        }


# 全局流程实例（延迟初始化）
_graph_flow_instance: Optional[Text2SQLGraphFlow] = None


def get_graph_flow(db_type: str, db_schema: str) -> Text2SQLGraphFlow:
    """
    获取GraphFlow实例（单例模式）
    
    Args:
        db_type: 数据库类型
        db_schema: 数据库schema信息
    
    Returns:
        Text2SQLGraphFlow实例
    """
    global _graph_flow_instance
    
    if _graph_flow_instance is None:
        _graph_flow_instance = Text2SQLGraphFlow(db_type, db_schema)
    
    return _graph_flow_instance
