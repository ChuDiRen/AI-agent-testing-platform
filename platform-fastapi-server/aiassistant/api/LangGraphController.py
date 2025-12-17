"""
LangGraphController - LangGraph测试用例生成API

提供流式生成、批量生成、Swagger解析等接口
"""
import json
import logging
from typing import AsyncGenerator, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session
from sse_starlette.sse import EventSourceResponse

from core.database import get_session
from core.resp_model import respModel
from ..services.LangGraphService import LangGraphService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/LangGraph", tags=["LangGraph测试用例生成"])


# ==================== Request/Response Models ====================

class ModelConfigRequest(BaseModel):
    """模型配置请求"""
    model_id: Optional[int] = Field(default=None, description="数据库模型ID，优先使用")
    provider: str = Field(default="siliconflow", description="提供商")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    reader_model: Optional[str] = Field(default=None, description="分析器模型")
    writer_model: Optional[str] = Field(default=None, description="编写器模型")
    reviewer_model: Optional[str] = Field(default=None, description="评审器模型")


class GenerateRequest(BaseModel):
    """生成请求"""
    requirement: str = Field(..., description="需求描述")
    test_type: str = Field(default="API", description="测试类型: API/Web/App")
    max_iterations: int = Field(default=2, ge=1, le=5, description="最大迭代次数")
    llm_config: Optional[ModelConfigRequest] = Field(default=None, description="模型配置")


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    requirements: List[str] = Field(..., description="需求列表")
    test_type: str = Field(default="API", description="测试类型")
    max_concurrent: int = Field(default=5, ge=1, le=10, description="最大并发数")
    max_iterations: int = Field(default=2, ge=1, le=3, description="最大迭代次数")
    llm_config: Optional[ModelConfigRequest] = Field(default=None, description="模型配置")


class SwaggerParseRequest(BaseModel):
    """Swagger解析请求"""
    swagger_url: str = Field(..., description="Swagger文档URL")


class ModelTestRequest(BaseModel):
    """模型测试请求"""
    provider: str = Field(..., description="提供商")
    api_key: str = Field(..., description="API密钥")
    model_code: Optional[str] = Field(default=None, description="模型代码")


# ==================== API Endpoints ====================

@router.post("/generate/stream", summary="流式生成测试用例(SSE)")
async def generate_stream(req: GenerateRequest, session: Session = Depends(get_session), current_user = Depends(None)):
    """流式生成测试用例，通过SSE推送进度"""
    async def event_generator() -> AsyncGenerator[str, None]:
        user_id = current_user.id if current_user else 1
        model_config = req.llm_config
        
        async for event in LangGraphService.generate_stream(
            session=session,
            requirement=req.requirement,
            test_type=req.test_type,
            max_iterations=req.max_iterations,
            model_id=model_config.model_id if model_config else None,
            api_key=model_config.api_key if model_config else None,
            provider=model_config.provider if model_config else None,
            reader_model=model_config.reader_model if model_config else None,
            writer_model=model_config.writer_model if model_config else None,
            reviewer_model=model_config.reviewer_model if model_config else None,
            user_id=user_id
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@router.post("/generate/batch", summary="批量生成测试用例")
async def generate_batch(req: BatchGenerateRequest, session: Session = Depends(get_session), current_user = Depends(None)):
    """批量并行生成测试用例"""
    user_id = current_user.id if current_user else 1
    model_config = req.llm_config
    
    result = await LangGraphService.generate_batch(
        session=session,
        requirements=req.requirements,
        test_type=req.test_type,
        max_concurrent=req.max_concurrent,
        max_iterations=req.max_iterations,
        model_id=model_config.model_id if model_config else None,
        api_key=model_config.api_key if model_config else None,
        provider=model_config.provider if model_config else None,
        user_id=user_id
    )
    
    if result.get("success"):
        return respModel.ok_resp({
            "results": result["results"],
            "statistics": result["statistics"],
        })
    return respModel.error_resp(result.get("error", "批量生成失败"))


@router.post("/swagger/parse", summary="解析Swagger文档")
async def parse_swagger(req: SwaggerParseRequest):
    """解析Swagger文档，返回API列表"""
    result = await LangGraphService.parse_swagger(req.swagger_url)
    if result.get("success"):
        return respModel.ok_resp({"apis": result["apis"], "total": result["total"]})
    return respModel.error_resp(result.get("error", "解析失败"))


@router.post("/model/test", summary="测试模型连接")
async def test_model(req: ModelTestRequest):
    """测试模型API连接"""
    result = await LangGraphService.test_model(
        provider=req.provider,
        api_key=req.api_key,
        model_code=req.model_code,
    )
    if result["success"]:
        return respModel.ok_resp(result)
    else:
        return respModel.error_resp(result.get("error", "连接失败"))


@router.get("/providers", summary="获取支持的模型提供商")
async def list_providers():
    """获取所有支持的模型提供商"""
    return respModel.ok_resp(LangGraphService.list_providers())


@router.get("/models/db", summary="获取数据库配置的模型")
async def list_db_models(session: Session = Depends(get_session)):
    """获取数据库中配置的所有启用模型"""
    result = LangGraphService.get_db_models(session)
    if result.get("success"):
        return respModel.ok_resp({
            "models": result["models"],
            "total": result["total"]
        })
    return respModel.error_resp(result.get("error", "获取失败"))


@router.get("/prompts/{agent_type}", summary="获取智能体提示词")
async def get_agent_prompt(
    agent_type: str,
    test_type: str = Query(default="API", description="测试类型"),
    session: Session = Depends(get_session)
):
    """获取指定智能体的提示词模板"""
    result = LangGraphService.get_agent_prompt(session, agent_type, test_type)
    if result.get("success"):
        return respModel.ok_resp({
            "agent_type": result["agent_type"],
            "test_type": result["test_type"],
            "prompt": result["prompt"]
        })
    return respModel.error_resp(result.get("error", "获取失败"))


@router.get("/statistics", summary="获取生成统计")
async def get_statistics(session: Session = Depends(get_session)):
    """获取生成统计数据"""
    result = LangGraphService.get_statistics(session)
    if result.get("success"):
        return respModel.ok_resp({
            "total_generations": result["total_generations"],
            "total_tokens": result["total_tokens"],
            "average_score": result["average_score"],
            "success_rate": result["success_rate"],
            "total_cases": result["total_cases"]
        })
    return respModel.error_resp(result.get("error", "获取失败"))


# ==================== LangGraph SDK 兼容端点 ====================

@router.get("/info", summary="获取服务信息")
async def get_info():
    """LangGraph SDK兼容 - 获取服务信息"""
    return {
        "version": "1.0.0",
        "name": "AI Agent Testing Platform - LangGraph Service"
    }


@router.get("/threads", summary="获取线程列表")
async def list_threads(session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 获取线程列表"""
    return LangGraphService.list_threads(session)


@router.post("/threads", summary="创建新线程")
async def create_thread(session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 创建新线程"""
    try:
        return LangGraphService.create_thread(session)
    except Exception as e:
        logger.error(f"Failed to create thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/state", summary="获取线程状态")
async def get_thread_state(thread_id: str, session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 获取线程状态"""
    result = LangGraphService.get_thread_state(session, thread_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return result


@router.post("/runs/stream", summary="流式运行")
async def stream_run(request: dict, session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 流式运行智能体"""
    from ..services.LangGraphServerService import LangGraphServerService
    
    thread_id = request.get("thread_id")
    input_data = request.get("input", {})
    
    # 如果没有thread_id，创建一个新的
    if not thread_id:
        thread_info = LangGraphService.create_thread(session)
        thread_id = thread_info["thread_id"]
    
    async def event_generator():
        async for event in LangGraphServerService.stream_run(session, thread_id, input_data):
            yield event
    
    return EventSourceResponse(event_generator(), media_type="text/event-stream")
