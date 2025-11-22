"""
WebSocket连接管理器
用于管理测试执行的实时WebSocket连接
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接: {execution_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = []
        self.active_connections[execution_id].append(websocket)
        logger.info(f"WebSocket connected for execution_id: {execution_id}")
    
    def disconnect(self, execution_id: str, websocket: WebSocket):
        """断开WebSocket连接"""
        if execution_id in self.active_connections:
            if websocket in self.active_connections[execution_id]:
                self.active_connections[execution_id].remove(websocket)
            # 如果该execution_id没有连接了，删除key
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
        logger.info(f"WebSocket disconnected for execution_id: {execution_id}")
    
    async def send_progress(self, execution_id: str, data: dict):
        """
        向指定execution_id的所有连接发送进度消息
        
        Args:
            execution_id: 执行ID
            data: 进度数据字典
        """
        if execution_id in self.active_connections:
            # 发送给该execution_id的所有连接
            disconnected = []
            for websocket in self.active_connections[execution_id]:
                try:
                    await websocket.send_json(data)
                except Exception as e:
                    logger.error(f"Failed to send message to websocket: {e}")
                    disconnected.append(websocket)
            
            # 清理断开的连接
            for ws in disconnected:
                self.disconnect(execution_id, ws)
    
    async def broadcast(self, data: dict):
        """
        广播消息给所有连接
        
        Args:
            data: 广播数据字典
        """
        for execution_id in list(self.active_connections.keys()):
            await self.send_progress(execution_id, data)
    
    def get_connection_count(self, execution_id: str = None) -> int:
        """
        获取连接数量
        
        Args:
            execution_id: 如果指定，返回该execution_id的连接数；否则返回总连接数
        
        Returns:
            连接数量
        """
        if execution_id:
            return len(self.active_connections.get(execution_id, []))
        else:
            return sum(len(conns) for conns in self.active_connections.values())


# 全局WebSocket管理器实例
manager = ConnectionManager()
