# Copyright (c) 2025 左岚. All rights reserved.
"""AI助手API路由"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.ai_service import AIService
from app.schemas.ai_chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse, ChatSessionDetail,
    ChatMessageResponse, ChatRequest, ChatResponse, AIModelResponse,
    TestCaseGenerateRequest, TestCaseGenerateResponse, AIModelCreate, AIModelUpdate
)
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI聊天 - 支持流式和非流式"""
    service = AIService(db)

    try:
        if request.stream:
            # 流式响应
            async def event_generator():
                """SSE事件生成器"""
                try:
                    async for chunk in await service.chat_stream(request, current_user.user_id):
                        # SSE格式: data: {json}\n\n
                        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                    # 发送结束标记
                    yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # 禁用nginx缓冲
                }
            )
        else:
            # 非流式响应
            response = await service.chat(request, current_user.user_id)
            return APIResponse(
                success=True,
                data=response
            )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"聊天失败: {str(e)}"
        )


@router.post("/sessions", response_model=APIResponse[ChatSessionResponse])
async def create_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[ChatSessionResponse]:
    """创建聊天会话"""
    service = AIService(db)
    session = await service.create_session(session_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="会话创建成功",
        data=ChatSessionResponse.model_validate(session)
    )


@router.get("/sessions", response_model=APIResponse[List[ChatSessionResponse]])
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[ChatSessionResponse]]:
    """获取用户的所有会话"""
    service = AIService(db)
    sessions = await service.get_user_sessions(current_user.user_id)
    
    return APIResponse(
        success=True,
        data=[ChatSessionResponse.model_validate(s) for s in sessions]
    )


@router.get("/sessions/{session_id}", response_model=APIResponse[ChatSessionDetail])
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[ChatSessionDetail]:
    """获取会话详情"""
    service = AIService(db)
    session = await service.get_session(session_id)
    
    if not session:
        return APIResponse(
            success=False,
            message="会话不存在"
        )
    
    # 获取消息列表
    messages = await service.get_session_messages(session_id)
    
    session_detail = ChatSessionDetail.model_validate(session)
    session_detail.messages = [ChatMessageResponse.model_validate(m) for m in messages]
    
    return APIResponse(
        success=True,
        data=session_detail
    )


@router.put("/sessions/{session_id}", response_model=APIResponse[ChatSessionResponse])
async def update_session(
    session_id: int,
    session_data: ChatSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[ChatSessionResponse]:
    """更新会话"""
    service = AIService(db)
    session = await service.update_session(session_id, session_data)
    
    if not session:
        return APIResponse(
            success=False,
            message="会话不存在"
        )
    
    return APIResponse(
        success=True,
        message="会话更新成功",
        data=ChatSessionResponse.model_validate(session)
    )


@router.delete("/sessions/{session_id}", response_model=APIResponse[None])
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除会话"""
    service = AIService(db)
    success = await service.delete_session(session_id)
    
    if not success:
        return APIResponse(
            success=False,
            message="会话不存在"
        )
    
    return APIResponse(
        success=True,
        message="会话删除成功"
    )


@router.post("/generate-testcases", response_model=APIResponse[TestCaseGenerateResponse])
async def generate_testcases(
    request: TestCaseGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestCaseGenerateResponse]:
    """AI生成测试用例"""
    service = AIService(db)
    testcases = await service.generate_testcases(request, current_user.user_id)
    
    return APIResponse(
        success=True,
        message=f"成功生成 {len(testcases)} 个测试用例",
        data=TestCaseGenerateResponse(
            testcases=testcases,
            total=len(testcases)
        )
    )


@router.get("/models", response_model=APIResponse[List[AIModelResponse]])
async def get_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[AIModelResponse]]:
    """获取可用的AI模型列表"""
    service = AIService(db)
    models = await service.get_available_models()
    
    return APIResponse(
        success=True,
        data=[AIModelResponse.model_validate(m) for m in models]
    )


@router.get("/health", response_model=APIResponse[dict])
async def health_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """AI服务健康检查"""
    return APIResponse(
        success=True,
        data={
            "status": "online",
            "service": "AI Assistant",
            "version": "1.0.0"
        }
    )


# ==================== AI模型管理API ====================

@router.post("/models", response_model=APIResponse[AIModelResponse])
async def create_model(
    model_data: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[AIModelResponse]:
    """创建AI模型配置"""
    service = AIService(db)
    model = await service.create_model(model_data)

    return APIResponse(
        success=True,
        message="模型创建成功",
        data=AIModelResponse.model_validate(model)
    )


@router.put("/models/{model_id}", response_model=APIResponse[AIModelResponse])
async def update_model(
    model_id: int,
    model_data: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[AIModelResponse]:
    """更新AI模型配置"""
    service = AIService(db)
    model = await service.update_model(model_id, model_data)

    if not model:
        return APIResponse(
            success=False,
            message="模型不存在"
        )

    return APIResponse(
        success=True,
        message="模型更新成功",
        data=AIModelResponse.model_validate(model)
    )


@router.delete("/models/{model_id}", response_model=APIResponse[None])
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除AI模型配置"""
    service = AIService(db)
    success = await service.delete_model(model_id)

    if not success:
        return APIResponse(
            success=False,
            message="模型不存在"
        )

    return APIResponse(
        success=True,
        message="模型删除成功"
    )


@router.post("/models/{model_id}/test", response_model=APIResponse[dict])
async def test_model_connection(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """测试AI模型连接"""
    service = AIService(db)
    result = await service.test_model_connection(model_id)

    return APIResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

