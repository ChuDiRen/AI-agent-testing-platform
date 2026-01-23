"""
FastAPI 服务器 - API路由、认证授权、WebSocket支持

职责：
- 提供RESTful API接口
- 实现WebSocket支持（实时进度）
- 认证和授权
- API文档（Swagger/OpenAPI）
- 文件上传接口
- 测试结果查询接口
- 任务管理接口
"""
from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime
import json
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from core.task_manager import get_task_manager, TaskStatus
from core.data_persistence import get_persistence_manager, PersistedTask, PersistedSession
from core.logging_config import get_logger
# from agents.orchestrator.orchestrator import OrchestratorAgent  # TODO: 需要实现 OrchestratorAgent

logger = get_logger(__name__)

# 数据模型
class TaskCreateRequest(BaseModel):
    """任务创建请求模型"""
    task_type: str = Field(..., description="任务类型")
    task_name: str = Field(..., description="任务名称")
    api_spec: Dict[str, Any] = Field(..., description="API规范")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="测试要求")
    framework: str = Field(default="playwright", description="测试框架")
    execute_tests: bool = Field(default=False, description="是否执行测试")


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    task_type: str
    task_name: str
    status: str
    progress: float = 0.0
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionCreateRequest(BaseModel):
    """会话创建请求模型"""
    session_name: Optional[str] = Field(None, description="会话名称")
    user_id: Optional[str] = Field(None, description="用户ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="会话元数据")


class SessionResponse(BaseModel):
    """会话响应模型"""
    session_id: str
    session_name: Optional[str] = None
    user_id: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    task_count: int = 0


class APIUploadRequest(BaseModel):
    """API文档上传请求模型"""
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型: openapi, graphql, postman")
    description: Optional[str] = Field(None, description="文件描述")


class TestExecutionRequest(BaseModel):
    """测试执行请求模型"""
    test_files: List[Dict[str, Any]] = Field(..., description="测试文件")
    framework: str = Field(..., description="测试框架")
    execution_options: Dict[str, Any] = Field(default_factory=dict, description="执行选项")


# 认证依赖
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """验证JWT令牌（简化实现）"""
    # 在实际应用中，这里应该验证JWT令牌
    # 为了演示，我们接受任何Bearer token
    if credentials.credentials:
        return "user_123"  # 返回用户ID
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket连接已建立: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket连接已断开: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"广播WebSocket消息失败: {e}")
                disconnected.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected:
            self.disconnect(client_id)


# 全局变量
manager = ConnectionManager()
# orchestrator = OrchestratorAgent()  # TODO: 需要实现 OrchestratorAgent
orchestrator = None  # 临时设置为 None，待实现后启用


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("API服务器启动中...")
    
    # 初始化任务管理器
    task_manager = get_task_manager()
    persistence_manager = get_persistence_manager()
    
    # 初始化持久化系统
    await persistence_manager.initialize()
    
    yield
    
    # 关闭时清理
    logger.info("API服务器关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="API Automation Agent Platform",
    description="智能API测试自动化平台",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "API Automation Agent Platform",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查任务管理器
        task_manager = get_task_manager()
        task_stats = await task_manager.get_task_statistics()
        
        # 检查持久化系统
        persistence_manager = get_persistence_manager()
        persistence_stats = await persistence_manager.get_persistence_statistics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "task_manager": "ok",
                "persistence": "ok",
                "orchestrator": "ok"
            },
            "statistics": {
                "tasks": task_stats,
                "persistence": persistence_stats
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


# 任务管理API
@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    current_user: str = Depends(verify_token)
):
    """创建新任务"""
    try:
        task_manager = get_task_manager()
        
        # 创建任务
        task_id = await task_manager.create_task(
            task_type=request.task_type,
            task_name=request.task_name,
            task_func=lambda: None,  # 实际任务函数由orchestrator处理
            timeout=300
        )
        
        # 准备orchestrator输入数据
        input_data = {
            "task_id": task_id,
            "workflow_type": "complete" if request.execute_tests else "planning_only",
            "api_spec": request.api_spec,
            "requirements": {
                "framework": request.framework,
                **request.requirements
            },
            "execute_tests": request.execute_tests
        }
        
        # 异步执行工作流
        asyncio.create_task(execute_workflow_async(task_id, input_data))
        
        # 返回任务信息
        task = await task_manager.get_task(task_id)
        return TaskResponse(
            task_id=task.task_id,
            task_type=task.task_type,
            task_name=task.task_name,
            status=task.status.value,
            progress=task.progress,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            metadata=task.metadata
        )
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/api/v1/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: str = Depends(verify_token)
):
    """列出任务"""
    try:
        task_manager = get_task_manager()
        tasks = await task_manager.list_tasks(status=status, limit=limit)
        
        return [
            TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_name=task.task_name,
                status=task.status.value,
                progress=task.progress,
                result=task.result,
                error_message=task.error_message,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
                metadata=task.metadata
            )
            for task in tasks
        ]
        
    except Exception as e:
        logger.error(f"列出任务失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: str = Depends(verify_token)
):
    """获取任务详情"""
    try:
        task_manager = get_task_manager()
        task = await task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            task_id=task.task_id,
            task_type=task.task_type,
            task_name=task.task_name,
            status=task.status.value,
            progress=task.progress,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get task")


@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: str = Depends(verify_token)
):
    """删除任务"""
    try:
        task_manager = get_task_manager()
        success = await task_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task deleted successfully", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to delete task")


# 会话管理API
@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    current_user: str = Depends(verify_token)
):
    """创建新会话"""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        session = PersistedSession(
            session_id=session_id,
            user_id=request.user_id or current_user,
            session_name=request.session_name,
            metadata=request.metadata
        )
        
        persistence_manager = get_persistence_manager()
        success = await persistence_manager.save_session(session)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return SessionResponse(
            session_id=session.session_id,
            session_name=session.session_name,
            user_id=session.user_id,
            status=session.status,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            metadata=session.metadata,
            task_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建会话失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.get("/api/v1/sessions", response_model=List[SessionResponse])
async def list_sessions(
    user_id: Optional[str] = None,
    limit: int = 100,
    current_user: str = Depends(verify_token)
):
    """列出会话"""
    try:
        persistence_manager = get_persistence_manager()
        sessions = await persistence_manager.list_sessions(user_id=user_id, limit=limit)
        
        return [
            SessionResponse(
                session_id=session.session_id,
                session_name=session.session_name,
                user_id=session.user_id,
                status=session.status,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                metadata=session.metadata,
                task_count=len(session.task_ids)
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"列出会话失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to list sessions")


@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: str = Depends(verify_token)
):
    """获取会话详情"""
    try:
        persistence_manager = get_persistence_manager()
        session = await persistence_manager.load_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=session.session_id,
            session_name=session.session_name,
            user_id=session.user_id,
            status=session.status,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            metadata=session.metadata,
            task_count=len(session.task_ids)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get session")


# 文件上传API
@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
    """上传API文档文件"""
    try:
        # 保存文件到临时目录
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 验证文件类型
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.json', '.yaml', '.yml']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "file_size": len(content),
            "file_path": tmp_file_path,
            "upload_time": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to upload file")


# 测试执行API
@app.post("/api/v1/execute")
async def execute_tests(
    request: TestExecutionRequest,
    current_user: str = Depends(verify_token)
):
    """执行测试"""
    try:
        # 创建任务
        task_manager = get_task_manager()
        task_id = await task_manager.create_task(
            task_type="test_execution",
            task_name="手动测试执行",
            task_func=lambda: None,
            timeout=600
        )
        
        # 准备执行数据
        input_data = {
            "task_id": task_id,
            "workflow_type": "execution_only",
            "requirements": {
                "framework": request.framework
            },
            "test_files": request.test_files,
            "execution_options": request.execution_options
        }
        
        # 异步执行
        asyncio.create_task(execute_workflow_async(task_id, input_data))
        
        return {
            "message": "Test execution started",
            "task_id": task_id,
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to execute tests")


# WebSocket端点
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点用于实时进度更新"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 接收客户端消息（如果需要）
            data = await websocket.receive_text()
            # 处理客户端消息...
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)


# 工作流执行异步函数
async def execute_workflow_async(task_id: str, input_data: Dict[str, Any]):
    """异步执行工作流"""
    try:
        task_manager = get_task_manager()
        
        # 更新任务状态
        await task_manager.update_task_progress(task_id, 5.0, "Starting workflow execution")
        
        # 执行工作流
        result = await orchestrator.execute_workflow(input_data)
        
        # 更新任务完成状态
        if result["status"] == "success":
            await task_manager.update_task_progress(task_id, 100.0, "Workflow completed successfully")
            
            # 通过WebSocket发送完成通知
            await manager.send_personal_message({
                "type": "task_completed",
                "task_id": task_id,
                "result": result
            }, task_id)
        else:
            await task_manager.update_task_progress(task_id, 0.0, f"Workflow failed: {result.get('error', 'Unknown error')}")
            
            # 通过WebSocket发送失败通知
            await manager.send_personal_message({
                "type": "task_failed",
                "task_id": task_id,
                "error": result.get("error", "Unknown error")
            }, task_id)
            
    except Exception as e:
        logger.error(f"工作流执行失败: {e}", exc_info=e)
        
        # 更新任务失败状态
        await task_manager.update_task_progress(task_id, 0.0, f"Execution failed: {str(e)}")
        
        # 通过WebSocket发送失败通知
        await manager.send_personal_message({
            "type": "task_failed",
            "task_id": task_id,
            "error": str(e)
        }, task_id)


# 统计API
@app.get("/api/v1/statistics")
async def get_statistics(current_user: str = Depends(verify_token)):
    """获取系统统计信息"""
    try:
        task_manager = get_task_manager()
        persistence_manager = get_persistence_manager()
        
        # 获取任务统计
        task_stats = await task_manager.get_task_statistics()
        
        # 获取持久化统计
        persistence_stats = await persistence_manager.get_persistence_statistics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "tasks": task_stats,
                "persistence": persistence_stats
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# 知识图谱API
@app.get("/api/v1/knowledge-graphs")
async def list_knowledge_graphs(
    limit: int = 100,
    current_user: str = Depends(verify_token)
):
    """列出知识图谱"""
    try:
        persistence_manager = get_persistence_manager()
        graphs = await persistence_manager.list_knowledge_graphs(limit=limit)
        
        return [
            {
                "graph_id": graph.graph_id,
                "name": graph.name,
                "description": graph.description,
                "version": graph.version,
                "created_at": graph.created_at.isoformat(),
                "updated_at": graph.updated_at.isoformat(),
                "entity_count": len(json.loads(graph.entities)) if graph.entities else 0,
                "relationship_count": len(json.loads(graph.relationships)) if graph.relationships else 0
            }
            for graph in graphs
        ]
        
    except Exception as e:
        logger.error(f"列出知识图谱失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to list knowledge graphs")


@app.get("/api/v1/knowledge-graphs/{graph_id}")
async def get_knowledge_graph(
    graph_id: str,
    current_user: str = Depends(verify_token)
):
    """获取知识图谱详情"""
    try:
        persistence_manager = get_persistence_manager()
        graph = await persistence_manager.load_knowledge_graph(graph_id)
        
        if not graph:
            raise HTTPException(status_code=404, detail="Knowledge graph not found")
        
        return {
            "graph_id": graph.graph_id,
            "name": graph.name,
            "description": graph.description,
            "entities": json.loads(graph.entities) if graph.entities else [],
            "relationships": json.loads(graph.relationships) if graph.relationships else [],
            "metadata": graph.metadata,
            "version": graph.version,
            "created_at": graph.created_at.isoformat(),
            "updated_at": graph.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识图谱失败: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get knowledge graph")


# 启动服务器
def start_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """启动API服务器"""
    logger.info(f"启动API服务器: {host}:{port}")
    
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info" if not debug else "debug",
        reload=debug
    )
    
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="API Automation Agent Platform Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    start_server(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
