"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from loguru import logger
from typing import List
from app.core.graph_flow import get_graph_flow
from app.core.stream_handler import get_stream_collector
from app.config.settings import settings

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接已建立. 当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket连接已断开. 当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            import json
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for connection in self.active_connections:
            try:
                import json
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/text2sql/websocket")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点 - Text2SQL查询处理"""
    await manager.connect(websocket)

    try:
        # 接收客户端消息
        data = await websocket.receive_json()

        if "query" not in data:
            await manager.send_personal_message(
                {"error": "缺少query字段", "is_final": True},
                websocket
            )
            return

        query = data["query"]
        logger.info(f"收到查询: {query[:100]}...")

        # 执行查询流程
        try:
            result = await stream_handler.process_query_stream(query, websocket)

            # 发送最终结果
            await manager.send_personal_message(
                {
                    "source": "system",
                    "content": "Text2SQL查询处理完成！",
                    "is_final": True,
                    "result": result
                },
                websocket
            )

        except Exception as e:
            logger.error(f"查询处理失败: {e}", exc_info=True)
            await manager.send_personal_message(
                {
                    "source": "system",
                    "content": f"查询处理失败: {str(e)}",
                    "is_final": True,
                    "error": str(e)
                },
                websocket
            )

    except WebSocketDisconnect:
        logger.info("WebSocket客户端主动断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}", exc_info=True)
        await manager.send_personal_message(
            {
                "source": "system",
                "content": f"连接错误: {str(e)}",
                "is_final": True,
                "error": str(e)
            },
            websocket
        )
    finally:
        manager.disconnect(websocket)
