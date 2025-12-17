"""
LangGraph Server 兼容API

实现与 @langchain/langgraph-sdk 兼容的API端点
参考: https://docs.langchain.com/langgraph-platform/streaming

端点:
- GET /info - 服务信息
- GET /assistants - 获取助手列表
- POST /threads - 创建线程
- GET /threads - 获取线程列表
- GET /threads/{thread_id}/state - 获取线程状态
- POST /threads/{thread_id}/runs/stream - 流式运行
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from core.database import get_session
from ..services.LangGraphServerService import LangGraphServerService

logger = logging.getLogger(__name__)

# 创建独立的路由器，不带前缀，用于LangGraph SDK兼容
langgraph_server_router = APIRouter(tags=["LangGraph Server API"])


@langgraph_server_router.get("/info")
async def get_info():
    """获取服务信息"""
    return LangGraphServerService.get_info()


@langgraph_server_router.get("/assistants")
async def list_assistants():
    """获取助手列表"""
    return LangGraphServerService.list_assistants()


@langgraph_server_router.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """获取指定助手信息"""
    return LangGraphServerService.get_assistant(assistant_id)


@langgraph_server_router.post("/threads")
async def create_thread(request: Request, session: Session = Depends(get_session)):
    """创建新线程"""
    try:
        body = {}
        try:
            body = await request.json()
        except:
            pass
        
        return LangGraphServerService.create_thread(session, body.get("metadata"))
    except Exception as e:
        logger.error(f"Failed to create thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@langgraph_server_router.get("/threads")
async def list_threads(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """获取线程列表"""
    return LangGraphServerService.list_threads(session, limit, offset)


@langgraph_server_router.get("/threads/{thread_id}")
async def get_thread(thread_id: str, session: Session = Depends(get_session)):
    """获取线程详情"""
    result = LangGraphServerService.get_thread(session, thread_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return result


@langgraph_server_router.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str, session: Session = Depends(get_session)):
    """获取线程状态"""
    result = LangGraphServerService.get_thread_state(session, thread_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return result


@langgraph_server_router.post("/threads/{thread_id}/runs/stream")
async def stream_run(thread_id: str, request: Request, session: Session = Depends(get_session)):
    """流式运行智能体"""
    try:
        body = await request.json()
    except:
        body = {}
    
    input_data = body.get("input", {})
    stream_mode = body.get("stream_mode", "updates")
    
    return StreamingResponse(
        LangGraphServerService.stream_run(session, thread_id, input_data, stream_mode),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@langgraph_server_router.post("/runs/stream")
async def stream_run_stateless(request: Request, session: Session = Depends(get_session)):
    """无状态流式运行（自动创建线程）"""
    try:
        body = await request.json()
    except:
        body = {}
    
    input_data = body.get("input", {})
    stream_mode = body.get("stream_mode", "updates")
    
    return StreamingResponse(
        LangGraphServerService.stream_run_stateless(session, input_data, stream_mode),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
