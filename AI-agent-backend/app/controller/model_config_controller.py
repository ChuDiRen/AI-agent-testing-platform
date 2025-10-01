"""
AI模型配置Controller
处理AI模型配置相关的HTTP请求
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.service.ai_model_service import AIModelService
from app.dto.ai_model_dto import (
    AIModelCreateRequest, AIModelUpdateRequest, AIModelSearchRequest,
    AIModelResponse, AIModelListResponse, AIModelStatisticsResponse,
    AIModelBatchOperationRequest, AIModelBatchOperationResponse,
    AIModelTestRequest, AIModelTestResponse
)
from app.dto.base import Success, Fail
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/model-configs", tags=["AI模型配置"])


@router.post("/", response_model=AIModelResponse, summary="创建AI模型配置")
def create_model_config(
    request: AIModelCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新的AI模型配置"""
    try:
        ai_model_service = AIModelService(db)
        model = ai_model_service.create_model(request, current_user.user_id)

        return Success(data=model, msg="模型配置创建成功")

    except Exception as e:
        logger.error(f"Error creating model config: {str(e)}")
        return Fail(msg=f"创建模型配置失败: {str(e)}")


@router.get("/statistics", response_model=AIModelStatisticsResponse, summary="获取模型配置统计")
def get_model_config_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取模型配置统计信息"""
    try:
        ai_model_service = AIModelService(db)
        stats = ai_model_service.get_model_statistics()

        return Success(data=stats, msg="获取统计信息成功")

    except Exception as e:
        logger.error(f"Error getting model config statistics: {str(e)}")
        return Fail(msg=f"获取统计信息失败: {str(e)}")


@router.get("/{model_id}", response_model=AIModelResponse, summary="获取模型配置详情")
def get_model_config(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取指定ID的模型配置详情"""
    try:
        ai_model_service = AIModelService(db)
        model = ai_model_service.get_model_by_id(model_id)
        
        if not model:
            return Fail(msg="模型配置不存在")
            
        return Success(data=model, msg="获取模型配置成功")
        
    except Exception as e:
        logger.error(f"Error getting model config: {str(e)}")
        return Fail(msg=f"获取模型配置失败: {str(e)}")


@router.put("/{model_id}", response_model=AIModelResponse, summary="更新模型配置")
def update_model_config(
    model_id: int,
    request: AIModelUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新指定ID的模型配置"""
    try:
        ai_model_service = AIModelService(db)
        model = ai_model_service.update_model(model_id, request, current_user.user_id)
        
        if not model:
            return Fail(msg="模型配置不存在")
            
        return Success(data=model, msg="模型配置更新成功")
        
    except Exception as e:
        logger.error(f"Error updating model config: {str(e)}")
        return Fail(msg=f"更新模型配置失败: {str(e)}")


@router.delete("/{model_id}", summary="删除模型配置")
def delete_model_config(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除指定ID的模型配置"""
    try:
        ai_model_service = AIModelService(db)
        success = ai_model_service.delete_model(model_id, current_user.user_id)
        
        if not success:
            return Fail(msg="模型配置不存在")
            
        return Success(msg="模型配置删除成功")
        
    except Exception as e:
        logger.error(f"Error deleting model config: {str(e)}")
        return Fail(msg=f"删除模型配置失败: {str(e)}")


@router.get("/", response_model=AIModelListResponse, summary="获取模型配置列表")
def get_model_config_list(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    provider: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取模型配置列表"""
    try:
        ai_model_service = AIModelService(db)
        
        # 构建搜索请求
        search_request = AIModelSearchRequest(
            page=page,
            page_size=page_size,
            keyword=keyword,
            provider=provider,
            status=status
        )
        
        result = ai_model_service.search_models(search_request)
        
        return Success(data=result, msg="获取模型配置列表成功")
        
    except Exception as e:
        logger.error(f"Error getting model config list: {str(e)}")
        return Fail(msg=f"获取模型配置列表失败: {str(e)}")


@router.post("/search", response_model=AIModelListResponse, summary="搜索模型配置")
def search_model_configs(
    request: AIModelSearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """搜索模型配置"""
    try:
        ai_model_service = AIModelService(db)
        result = ai_model_service.search_models(request)
        
        return Success(data=result, msg="搜索模型配置成功")
        
    except Exception as e:
        logger.error(f"Error searching model configs: {str(e)}")
        return Fail(msg=f"搜索模型配置失败: {str(e)}")




# 移除重复的测试路由，保留统一的 `/{model_id}/test` 下方实现


@router.post("/batch", response_model=AIModelBatchOperationResponse, summary="批量操作模型配置")
def batch_operation_model_configs(
    request: AIModelBatchOperationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量操作模型配置"""
    try:
        ai_model_service = AIModelService(db)
        result = ai_model_service.batch_operation(request, current_user.user_id)
        
        return Success(data=result, msg="批量操作完成")
        
    except Exception as e:
        logger.error(f"Error in batch operation: {str(e)}")
        return Fail(msg=f"批量操作失败: {str(e)}")


@router.post("/{model_id}/status", response_model=AIModelResponse, summary="更新模型状态")
def update_model_status(
    model_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新模型配置状态"""
    try:
        ai_model_service = AIModelService(db)
        model = ai_model_service.update_model_status(model_id, status, current_user.user_id)
        
        if not model:
            return Fail(msg="模型配置不存在")
            
        return Success(data=model, msg="模型状态更新成功")
        
    except Exception as e:
        logger.error(f"Error updating model status: {str(e)}")
        return Fail(msg=f"更新模型状态失败: {str(e)}")


@router.get("/providers", summary="获取支持的模型提供商")
def get_supported_providers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取支持的模型提供商列表"""
    try:
        ai_model_service = AIModelService(db)
        providers = ai_model_service.get_supported_providers()
        
        return Success(data=providers, msg="获取提供商列表成功")
        
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        return Fail(msg=f"获取提供商列表失败: {str(e)}")


# 聊天相关的请求模型
class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False


@router.post("/{model_id}/test", response_model=AIModelTestResponse, summary="测试模型连接")
async def test_model_connection(
    model_id: int,
    request: AIModelTestRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """测试AI模型连接"""
    try:
        ai_model_service = AIModelService(db)
        test_result = await ai_model_service.test_model(model_id, request)

        return Success(data=test_result, msg="模型测试完成")

    except Exception as e:
        logger.error(f"Error testing model {model_id}: {str(e)}")
        return Fail(msg=f"模型测试失败: {str(e)}")


@router.post("/{model_id}/chat", summary="与AI模型聊天")
async def chat_with_model(
    model_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """与AI模型聊天"""
    try:
        ai_model_service = AIModelService(db)

        if request.stream:
            # 流式响应
            async def generate():
                async for chunk in await ai_model_service.chat_with_model(
                    model_id=model_id,
                    messages=request.messages,
                    user_id=current_user.user_id,
                    stream=True,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            # 完整响应
            response = await ai_model_service.chat_with_model(
                model_id=model_id,
                messages=request.messages,
                user_id=current_user.user_id,
                stream=False,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )

            return Success(data={
                "content": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time": response.response_time,
                "metadata": response.metadata
            }, msg="聊天成功")

    except Exception as e:
        logger.error(f"Error chatting with model {model_id}: {str(e)}")
        return Fail(msg=f"聊天失败: {str(e)}")
