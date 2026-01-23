"""
WebSocket 服务 - 实时执行监控
"""
import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, status
from app.core.logger import setup_logger

logger = setup_logger(name="websocket_service")


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储活跃的 WebSocket 连接 {execution_id: [ws1, ws2, ...]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # 存储 WebSocket -> execution_id 映射
        self.connection_to_execution: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, execution_id: int):
        """建立新的 WebSocket 连接"""
        await websocket.accept()
        logger.info(
            f"WebSocket connected: execution_id={execution_id}",
            extra={"execution_id": execution_id}
        )

        # 添加到活跃连接
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()

        self.active_connections[execution_id].add(websocket)
        self.connection_to_execution[websocket] = execution_id

        # 发送欢迎消息
        await self.send_personal_message(
            websocket,
            {
                "type": "connected",
                "execution_id": execution_id,
                "message": "WebSocket 连接已建立"
            }
        )

    async def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        execution_id = self.connection_to_execution.get(websocket)

        if execution_id:
            logger.info(
                f"WebSocket disconnected: execution_id={execution_id}",
                extra={"execution_id": execution_id}
            )

            # 从活跃连接中移除
            if execution_id in self.active_connections:
                self.active_connections[execution_id].discard(websocket)
                if not self.active_connections[execution_id]:
                    del self.active_connections[execution_id]

            del self.connection_to_execution[websocket]

    async def send_personal_message(self, websocket: WebSocket, message: Dict):
        """向特定 WebSocket 发送消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(
                f"Failed to send message to WebSocket: {e}",
                extra={"execution_id": self.connection_to_execution.get(websocket)},
                exc_info=True
            )

    async def broadcast_to_execution(self, execution_id: int, message: Dict):
        """向特定 execution 的所有 WebSocket 广播消息"""
        if execution_id not in self.active_connections:
            return

        # 需要移除的连接列表（已断开的）
        disconnected = set()

        for websocket in self.active_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # 移除断开的连接
        for ws in disconnected:
            await self.disconnect(ws)

    async def broadcast_system_message(self, message: Dict):
        """向所有连接广播系统消息"""
        for websocket in list(self.connection_to_execution.keys()):
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(websocket)

    def get_connection_count(self, execution_id: int) -> int:
        """获取特定 execution 的连接数"""
        return len(self.active_connections.get(execution_id, set()))


# 全局 WebSocket 管理器实例
ws_manager = WebSocketManager()
