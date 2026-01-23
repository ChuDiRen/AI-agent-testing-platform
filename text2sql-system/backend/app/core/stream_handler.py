"""
流式响应处理器 - 集成智能体流程与WebSocket
"""
import json
from typing import Dict, Any, Callable, Optional
from loguru import logger

from app.config.settings import settings
from app.core.graph_flow import get_graph_flow


class StreamResponseCollector:
    """
    流式响应收集器
    
    功能:
    1. 集成GraphFlow流程
    2. 实时收集智能体输出
    3. 格式化为WebSocket消息
    4. 处理用户输入
    """
    
    def __init__(self):
        self.graph_flow = None  # 延迟初始化
        self.is_processing = False
    
    async def initialize(self, db_type: str, db_schema: str):
        """初始化流式响应处理器"""
        try:
            self.graph_flow = get_graph_flow(db_type, db_schema)
            self.is_processing = False
            logger.info(f"流式响应处理器初始化成功，数据库类型: {db_type}")
            return True
        except Exception as e:
            logger.error(f"流式响应处理器初始化失败: {str(e)}")
            return False
    
    async def process_query_stream(self, user_query: str, 
                                websocket, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        处理查询流
        
        Args:
            user_query: 用户查询
            websocket: WebSocket连接对象
            callback: 可选的回调函数
        
        Returns:
            处理结果
        """
        if self.graph_flow is None:
            await self.send_error(
                websocket,
                "GraphFlow未初始化，请先调用initialize方法"
            )
            return {
                'error': True,
                'message': 'GraphFlow未初始化'
            }
        
        if self.is_processing:
            await self.send_error(
                websocket,
                "已有查询正在处理中，请等待当前查询完成"
            )
            return {
                'error': True,
                'message': '系统繁忙'
            }
        
        self.is_processing = True
        
        try:
            # 创建流式回调
            async def stream_callback(data: Dict[str, Any]):
                """内部流式回调"""
                await self.send_message(websocket, data)
            
            # 启动GraphFlow流程
            result = await self.graph_flow.process_query(
                user_query,
                stream_callback
            )
            
            self.is_processing = False
            
            # 发送处理完成消息
            await self.send_message(websocket, {
                "source": "system",
                "content": "查询处理完成",
                "is_final": True,
                "result": result
            })
            
            logger.info(f"查询流处理完成: {user_query[:50]}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询流处理失败: {str(e)}")
            await self.send_error(
                websocket,
                f"处理过程中发生错误: {str(e)}"
            )
            self.is_processing = False
            
            return {
                'error': True,
                'message': f"处理失败: {str(e)}",
                'data': []
            }
    
    async def send_message(self, websocket, message: Dict[str, Any]):
        """发送WebSocket消息"""
        try:
            await websocket.send_json(message)
            logger.debug(f"发送消息: {message.get('source', 'system')[:20]}: {message.get('content', '')[:50]}")
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
    
    async def send_error(self, websocket, error_message: str):
        """发送错误消息"""
        await self.send_message(websocket, {
            'source': 'system',
            'content': error_message,
            'is_final': True,
            'error': True
        })


# 全局流式响应处理器实例（单例模式）
_stream_collector: Optional[StreamResponseCollector] = None


def get_stream_collector() -> StreamResponseCollector:
    """获取流式响应处理器实例（单例模式）"""
    global _stream_collector
    
    if _stream_collector is None:
        _stream_collector = StreamResponseCollector()
    
    return _stream_collector
