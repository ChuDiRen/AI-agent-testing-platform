# API路由还原提示词

## 服务概述

智能客服API路由系统基于FastAPI框架，提供RESTful API接口和WebSocket连接，支持流式聊天、会话管理、文件上传等核心功能，为前端提供完整的客服服务接口。

## 技术栈要求

```json
{
  "framework": "FastAPI 0.104+",
  "language": "Python 3.9+",
  "async_support": "asyncio",
  "streaming": "Server-Sent Events (SSE)",
  "file_handling": "multipart/form-data",
  "validation": "Pydantic v2",
  "cors": "fastapi.middleware.cors",
  "logging": "Python logging"
}
```

## 核心架构设计

### 1. 主路由配置

```python
# 文件路径: c_app/api/__init__.py
from fastapi import APIRouter
from .v1 import api_router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")
```

```python
# 文件路径: c_app/api/v1/__init__.py
from fastapi import APIRouter
from .customer import router as customer_router

api_router = APIRouter()
api_router.include_router(customer_router, prefix="/chat", tags=["智能客服"])
```

### 2. 客服API路由实现

```python
# 文件路径: c_app/api/v1/customer/customer.py
import os
import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer
from pydantic import ValidationError

from ....schemas.customer import (
    ChatRequest, 
    ChatResponse, 
    ChatMessage,
    SessionRequest,
    SessionResponse,
    MemoryAddRequest,
    MemoryRetrieveRequest
)
from ....services.chat_service_v4 import ChatService
from ....services.session_service import SessionService
from ....services.memory_service import MemoryServiceFactory
from ....config import settings

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 安全认证（可选）
security = HTTPBearer(auto_error=False)

# 服务实例
chat_service = ChatService()
session_service = SessionService()
memory_factory = MemoryServiceFactory()

# 文件上传配置
UPLOAD_DIR = "./uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    token: Optional[str] = Depends(security)
) -> StreamingResponse:
    """
    流式聊天接口
    
    支持文本和多模态消息的流式处理，返回Server-Sent Events格式的响应流。
    """
    try:
        # 验证请求参数
        if not request.user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        if not request.session_id:
            raise HTTPException(status_code=400, detail="会话ID不能为空")
        
        if not request.message or not request.message.content:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 验证消息格式
        if isinstance(request.message.content, list):
            for content_item in request.message.content:
                if not isinstance(content_item, dict) or "type" not in content_item:
                    raise HTTPException(status_code=400, detail="多模态消息格式错误")
        
        logger.info(f"开始处理流式聊天请求 - 用户: {request.user_id}, 会话: {request.session_id}")
        
        # 创建流式响应生成器
        async def generate_stream():
            try:
                # 调用聊天服务的流式处理
                async for chunk in chat_service.chat_stream(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    message=request.message,
                    stream=True
                ):
                    # 格式化为SSE格式
                    if chunk.strip():
                        # 转义特殊字符
                        escaped_chunk = chunk.replace('\n', '\\n').replace('\r', '\\r')
                        yield f"data: {escaped_chunk}\n\n"
                    
                    # 添加小延迟以避免过快的流式输出
                    await asyncio.sleep(0.01)
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"流式聊天处理错误: {str(e)}", exc_info=True)
                error_msg = f"处理聊天请求时发生错误: {str(e)}"
                yield f"data: {{\"error\": \"{error_msg}\"}}\n\n"
                yield "data: [DONE]\n\n"
        
        # 返回流式响应
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"请求参数验证错误: {str(e)}")
        raise HTTPException(status_code=422, detail=f"请求参数格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"流式聊天接口错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/session/create", response_model=SessionResponse)
async def create_session(
    request: SessionRequest,
    token: Optional[str] = Depends(security)
) -> SessionResponse:
    """
    创建新的聊天会话
    
    为指定用户创建一个新的聊天会话，返回会话ID和基本信息。
    """
    try:
        if not request.user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        logger.info(f"创建新会话 - 用户: {request.user_id}")
        
        # 生成新的会话ID
        session_id = f"session_{request.user_id}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # 创建会话
        session_data = await session_service.create_session(
            session_id=session_id,
            user_id=request.user_id,
            metadata={
                "created_at": datetime.now().isoformat(),
                "title": request.title or "新对话",
                "description": request.description or ""
            }
        )
        
        if not session_data:
            raise HTTPException(status_code=500, detail="创建会话失败")
        
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            title=request.title or "新对话",
            created_at=datetime.now().isoformat(),
            message_count=0,
            last_activity=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建会话错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建会话失败")


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    token: Optional[str] = Depends(security)
) -> SessionResponse:
    """
    获取指定会话信息
    
    根据会话ID获取会话的详细信息，包括消息数量和最后活动时间。
    """
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="会话ID不能为空")
        
        logger.info(f"获取会话信息 - 会话ID: {session_id}")
        
        # 获取会话数据
        session_data = await session_service.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取消息数量
        message_count = await session_service.get_message_count(session_id)
        
        # 获取最后活动时间
        last_activity = await session_service.get_last_activity(session_id)
        
        return SessionResponse(
            session_id=session_id,
            user_id=session_data.get("user_id", ""),
            title=session_data.get("metadata", {}).get("title", "对话"),
            created_at=session_data.get("created_at", ""),
            message_count=message_count,
            last_activity=last_activity or session_data.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取会话信息失败")


@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    token: Optional[str] = Depends(security)
) -> List[SessionResponse]:
    """
    获取用户的所有会话列表
    
    分页获取指定用户的所有聊天会话，按最后活动时间倒序排列。
    """
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        if limit <= 0 or limit > 100:
            raise HTTPException(status_code=400, detail="限制数量必须在1-100之间")
        
        if offset < 0:
            raise HTTPException(status_code=400, detail="偏移量不能为负数")
        
        logger.info(f"获取用户会话列表 - 用户: {user_id}, 限制: {limit}, 偏移: {offset}")
        
        # 获取用户会话列表
        sessions_data = await session_service.get_user_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        sessions = []
        for session_data in sessions_data:
            try:
                # 获取每个会话的详细信息
                message_count = await session_service.get_message_count(session_data["session_id"])
                last_activity = await session_service.get_last_activity(session_data["session_id"])
                
                session_response = SessionResponse(
                    session_id=session_data["session_id"],
                    user_id=session_data["user_id"],
                    title=session_data.get("metadata", {}).get("title", "对话"),
                    created_at=session_data["created_at"],
                    message_count=message_count,
                    last_activity=last_activity or session_data["created_at"]
                )
                sessions.append(session_response)
                
            except Exception as e:
                logger.warning(f"处理会话数据错误: {str(e)}")
                continue
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取会话列表失败")


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    token: Optional[str] = Depends(security)
) -> JSONResponse:
    """
    上传图片文件
    
    支持多种图片格式的上传，返回图片的访问URL和基本信息。
    """
    try:
        # 验证参数
        if not user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="会话ID不能为空")
        
        if not file:
            raise HTTPException(status_code=400, detail="请选择要上传的文件")
        
        # 验证文件类型
        file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ""
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"文件大小超过限制 ({MAX_FILE_SIZE // (1024*1024)}MB)"
            )
        
        # 重置文件指针
        await file.seek(0)
        
        logger.info(f"上传图片 - 用户: {user_id}, 会话: {session_id}, 文件: {file.filename}")
        
        # 生成唯一文件名
        timestamp = int(datetime.now().timestamp())
        unique_filename = f"{user_id}_{session_id}_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # 生成访问URL
        file_url = f"/static/uploads/{unique_filename}"
        
        # 获取文件信息
        file_info = {
            "filename": file.filename,
            "size": len(file_content),
            "content_type": file.content_type,
            "upload_time": datetime.now().isoformat(),
            "file_path": file_path,
            "file_url": file_url
        }
        
        logger.info(f"图片上传成功 - 文件: {unique_filename}, 大小: {len(file_content)} bytes")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "图片上传成功",
                "data": {
                    "file_url": file_url,
                    "filename": unique_filename,
                    "original_filename": file.filename,
                    "size": len(file_content),
                    "content_type": file.content_type,
                    "upload_time": datetime.now().isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片上传错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="图片上传失败")


@router.post("/memory/add")
async def add_memory(
    request: MemoryAddRequest,
    token: Optional[str] = Depends(security)
) -> JSONResponse:
    """
    添加用户记忆
    
    向用户的私有知识库添加新的记忆内容。
    """
    try:
        if not request.user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        if not request.content:
            raise HTTPException(status_code=400, detail="记忆内容不能为空")
        
        logger.info(f"添加用户记忆 - 用户: {request.user_id}")
        
        # 获取私有记忆服务
        private_memory = memory_factory.get_private_memory_service(request.user_id)
        
        # 添加记忆
        memory_id = await private_memory.add_memory(
            content=request.content,
            metadata=request.metadata or {}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "记忆添加成功",
                "data": {
                    "memory_id": memory_id,
                    "user_id": request.user_id,
                    "created_at": datetime.now().isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加记忆错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="添加记忆失败")


@router.post("/memory/retrieve")
async def retrieve_memories(
    request: MemoryRetrieveRequest,
    token: Optional[str] = Depends(security)
) -> JSONResponse:
    """
    检索相关记忆
    
    根据查询内容检索用户的相关记忆。
    """
    try:
        if not request.user_id:
            raise HTTPException(status_code=400, detail="用户ID不能为空")
        
        if not request.query:
            raise HTTPException(status_code=400, detail="查询内容不能为空")
        
        logger.info(f"检索用户记忆 - 用户: {request.user_id}, 查询: {request.query}")
        
        # 获取记忆服务
        private_memory = memory_factory.get_private_memory_service(request.user_id)
        chat_memory = memory_factory.get_chat_memory_service(request.user_id)
        public_memory = memory_factory.get_public_memory_service()
        
        # 并行检索各类记忆
        private_results, chat_results, public_results = await asyncio.gather(
            private_memory.retrieve_memories(request.query, limit=request.limit or 3),
            chat_memory.retrieve_memories(request.query, limit=request.limit or 3),
            public_memory.retrieve_memories(request.query, limit=request.limit or 3),
            return_exceptions=True
        )
        
        # 处理结果
        all_memories = []
        
        # 添加私有记忆结果
        if not isinstance(private_results, Exception):
            for memory in private_results:
                all_memories.append({
                    "id": memory.id,
                    "content": memory.content,
                    "type": "private",
                    "relevance_score": memory.metadata.get("relevance_score", 0),
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                })
        
        # 添加聊天记忆结果
        if not isinstance(chat_results, Exception):
            for memory in chat_results:
                all_memories.append({
                    "id": memory.id,
                    "content": memory.content,
                    "type": "chat",
                    "relevance_score": memory.metadata.get("relevance_score", 0),
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                })
        
        # 添加公共记忆结果
        if not isinstance(public_results, Exception):
            for memory in public_results:
                all_memories.append({
                    "id": memory.id,
                    "content": memory.content,
                    "type": "public",
                    "title": memory.metadata.get("title", ""),
                    "category": memory.metadata.get("category", ""),
                    "relevance_score": memory.metadata.get("relevance_score", 0),
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                })
        
        # 按相关性排序
        all_memories.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # 限制返回数量
        final_limit = request.limit or 10
        all_memories = all_memories[:final_limit]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "记忆检索成功",
                "data": {
                    "query": request.query,
                    "total_count": len(all_memories),
                    "memories": all_memories
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检索记忆错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="检索记忆失败")


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    健康检查接口
    
    检查服务的运行状态和各个组件的健康状况。
    """
    try:
        # 检查各个服务的状态
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "chat_service": "healthy",
                "session_service": "healthy",
                "memory_service": "healthy"
            }
        }
        
        # 简单的服务可用性检查
        try:
            # 测试会话服务
            test_sessions = await session_service.get_user_sessions("health_check", limit=1)
            health_status["services"]["session_service"] = "healthy"
        except Exception:
            health_status["services"]["session_service"] = "unhealthy"
            health_status["status"] = "degraded"
        
        try:
            # 测试记忆服务
            test_memory = memory_factory.get_public_memory_service()
            await test_memory.retrieve_memories("test", limit=1)
            health_status["services"]["memory_service"] = "healthy"
        except Exception:
            health_status["services"]["memory_service"] = "unhealthy"
            health_status["status"] = "degraded"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"健康检查错误: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


@router.get("/stats")
async def get_stats(
    token: Optional[str] = Depends(security)
) -> JSONResponse:
    """
    获取服务统计信息
    
    返回系统的使用统计和性能指标。
    """
    try:
        # 获取统计信息
        stats = {
            "timestamp": datetime.now().isoformat(),
            "uptime": "运行中",
            "version": "1.0.0",
            "statistics": {
                "total_sessions": 0,
                "active_sessions": 0,
                "total_messages": 0,
                "total_uploads": 0
            }
        }
        
        try:
            # 获取会话统计
            session_stats = await session_service.get_statistics()
            stats["statistics"].update(session_stats)
        except Exception as e:
            logger.warning(f"获取会话统计失败: {str(e)}")
        
        try:
            # 获取上传文件统计
            upload_count = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
            stats["statistics"]["total_uploads"] = upload_count
        except Exception as e:
            logger.warning(f"获取上传统计失败: {str(e)}")
        
        return JSONResponse(
            status_code=200,
            content=stats
        )
        
    except Exception as e:
        logger.error(f"获取统计信息错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取统计信息失败")
```

### 3. 错误处理中间件

```python
# 文件路径: c_app/api/middleware/error_handler.py
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # HTTP异常直接返回
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": e.status_code,
                        "message": e.detail,
                        "type": "HTTPException"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except ValidationError as e:
            # 参数验证错误
            logger.error(f"参数验证错误: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": {
                        "code": 422,
                        "message": "请求参数格式错误",
                        "type": "ValidationError",
                        "details": str(e)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            # 其他未处理的异常
            logger.error(f"未处理的异常: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": 500,
                        "message": "服务器内部错误",
                        "type": "InternalServerError"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
```

### 4. CORS配置

```python
# 文件路径: c_app/api/middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    """配置CORS中间件"""
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js 开发服务器
            "http://127.0.0.1:3000",
            "http://localhost:8080",  # 其他可能的前端端口
            "https://your-domain.com",  # 生产环境域名
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "*",
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        expose_headers=[
            "Content-Length",
            "Content-Type",
            "Cache-Control",
            "Connection"
        ]
    )
```

### 5. 静态文件服务

```python
# 文件路径: c_app/api/static.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

def setup_static_files(app: FastAPI):
    """配置静态文件服务"""
    
    # 上传文件目录
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 挂载静态文件目录
    app.mount("/static/uploads", StaticFiles(directory=upload_dir), name="uploads")
    
    @app.get("/download/{filename}")
    async def download_file(filename: str):
        """文件下载接口"""
        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
```

### 6. 主应用配置

```python
# 文件路径: c_app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api import api_router
from .api.middleware.cors import setup_cors
from .api.middleware.error_handler import ErrorHandlerMiddleware
from .api.static import setup_static_files
from .config import settings
from .utils.init_memory_db import init_memory_database

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('customer_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("智能客服系统启动中...")
    
    # 初始化数据库
    try:
        init_memory_database()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
    
    yield
    
    # 关闭时执行
    logger.info("智能客服系统关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="智能客服系统 API",
    description="基于AutoGen的智能客服系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(ErrorHandlerMiddleware)
setup_cors(app)

# 配置静态文件
setup_static_files(app)

# 注册路由
app.include_router(api_router, prefix="/api")

# 根路径
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "智能客服系统 API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "health": "/api/v1/chat/health"
        }
    )

# 健康检查
@app.get("/health")
async def health():
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "智能客服系统"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "c_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### 7. 启动脚本

```python
# 文件路径: run_server.py
import uvicorn
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 开发环境配置
    uvicorn.run(
        "c_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["c_app"],
        log_level="info",
        access_log=True
    )
```

### 8. 生产环境配置

```dockerfile
# 文件路径: Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "c_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# 文件路径: docker-compose.yml
version: '3.8'

services:
  customer-service-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_MODEL=deepseek-chat
      - MEMORY_DB_PATH=/app/data/customer_service.db
      - MAX_FILE_SIZE=10485760
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## API接口文档

### 接口列表

| 接口路径 | 方法 | 功能描述 |
|---------|------|----------|
| `/api/v1/chat/stream` | POST | 流式聊天接口 |
| `/api/v1/chat/session/create` | POST | 创建新会话 |
| `/api/v1/chat/session/{session_id}` | GET | 获取会话信息 |
| `/api/v1/chat/sessions/{user_id}` | GET | 获取用户会话列表 |
| `/api/v1/chat/upload-image` | POST | 上传图片文件 |
| `/api/v1/chat/memory/add` | POST | 添加用户记忆 |
| `/api/v1/chat/memory/retrieve` | POST | 检索相关记忆 |
| `/api/v1/chat/health` | GET | 健康检查 |
| `/api/v1/chat/stats` | GET | 获取统计信息 |

### 请求/响应示例

#### 流式聊天
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session456",
    "message": {
      "role": "user",
      "content": "我想了解退货政策"
    }
  }'
```

#### 上传图片
```bash
curl -X POST "http://localhost:8000/api/v1/chat/upload-image" \
  -F "file=@image.jpg" \
  -F "user_id=user123" \
  -F "session_id=session456"
```

## 关键特性说明

1. **流式响应**: 支持Server-Sent Events的实时流式聊天
2. **多模态支持**: 文本和图片的混合消息处理
3. **会话管理**: 完整的会话创建、查询和管理功能
4. **文件上传**: 安全的图片文件上传和存储
5. **记忆集成**: 与记忆服务的深度集成
6. **错误处理**: 全局异常处理和标准化错误响应
7. **CORS支持**: 跨域请求支持
8. **健康检查**: 服务状态监控
9. **静态文件**: 上传文件的访问服务
10. **生产就绪**: Docker化部署支持

---

此提示词包含了完整的API路由实现，可以直接用于还原智能客服系统的后端API服务。