"""
LangGraphController - LangGraph测试用例生成API

提供流式生成、批量生成、Swagger解析等接口
"""
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session
from sse_starlette.sse import EventSourceResponse

from core.database import get_session
from core.resp_model import respModel
from ..langgraph import TestCaseGenerator, TestCaseState
from ..langgraph.generator import GeneratorConfig
from ..langgraph.services import ModelService, PROVIDER_CONFIGS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/LangGraph", tags=["LangGraph测试用例生成"])


# ==================== Request/Response Models ====================

class ModelConfigRequest(BaseModel):
    """模型配置请求"""
    provider: str = Field(default="siliconflow", description="提供商")
    api_key: str = Field(..., description="API密钥")
    reader_model: Optional[str] = Field(default=None, description="分析器模型")
    writer_model: Optional[str] = Field(default=None, description="编写器模型")
    reviewer_model: Optional[str] = Field(default=None, description="评审器模型")


class GenerateRequest(BaseModel):
    """生成请求"""
    requirement: str = Field(..., description="需求描述")
    test_type: str = Field(default="API", description="测试类型: API/Web/App")
    max_iterations: int = Field(default=2, ge=1, le=5, description="最大迭代次数")
    model_config: Optional[ModelConfigRequest] = Field(default=None, description="模型配置")


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    requirements: List[str] = Field(..., description="需求列表")
    test_type: str = Field(default="API", description="测试类型")
    max_concurrent: int = Field(default=5, ge=1, le=10, description="最大并发数")
    max_iterations: int = Field(default=2, ge=1, le=3, description="最大迭代次数")
    model_config: Optional[ModelConfigRequest] = Field(default=None, description="模型配置")


class SwaggerParseRequest(BaseModel):
    """Swagger解析请求"""
    swagger_url: str = Field(..., description="Swagger文档URL")


class ModelTestRequest(BaseModel):
    """模型测试请求"""
    provider: str = Field(..., description="提供商")
    api_key: str = Field(..., description="API密钥")
    model_code: Optional[str] = Field(default=None, description="模型代码")


# ==================== Helper Functions ====================

def create_generator(model_config: Optional[ModelConfigRequest]) -> TestCaseGenerator:
    """创建生成器实例"""
    if model_config:
        config = GeneratorConfig(
            api_key=model_config.api_key,
            provider=model_config.provider,
            reader_model=model_config.reader_model or PROVIDER_CONFIGS.get(model_config.provider, {}).get("default_model", ""),
            writer_model=model_config.writer_model or PROVIDER_CONFIGS.get(model_config.provider, {}).get("default_model", ""),
            reviewer_model=model_config.reviewer_model or PROVIDER_CONFIGS.get(model_config.provider, {}).get("default_model", ""),
        )
    else:
        # 使用默认配置
        config = GeneratorConfig(
            api_key="",  # 需要从环境变量或数据库获取
            provider="siliconflow",
            reader_model="deepseek-ai/DeepSeek-V3",
            writer_model="deepseek-ai/DeepSeek-V3",
            reviewer_model="deepseek-ai/DeepSeek-V3",
        )
    return TestCaseGenerator(config)


# ==================== API Endpoints ====================

@router.post("/generate/stream", summary="流式生成测试用例(SSE)")
async def generate_stream(req: GenerateRequest):
    """流式生成测试用例，通过SSE推送进度"""
    async def event_generator() -> AsyncGenerator[str, None]:
        events = []

        def progress_callback(stage: str, message: str, progress: float):
            events.append({
                "type": "stage_progress",
                "data": {"stage": stage, "message": message, "progress": progress}
            })

        try:
            generator = create_generator(req.model_config)
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'stage_start', 'data': {'stage': 'init', 'message': '开始生成...'}})}\n\n"

            state = await generator.generate(
                requirement=req.requirement,
                test_type=req.test_type,
                max_iterations=req.max_iterations,
                progress_callback=progress_callback,
            )

            # 发送进度事件
            for event in events:
                yield f"data: {json.dumps(event)}\n\n"

            # 发送测试用例
            if state.testcases:
                yield f"data: {json.dumps({'type': 'testcase', 'data': state.testcases})}\n\n"

            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done', 'data': {'quality_score': state.quality_score, 'iteration': state.iteration, 'duration': state.get_duration_seconds(), 'completed': state.completed}})}\n\n"

        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': {'error': str(e)}})}\n\n"

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@router.post("/generate/batch", summary="批量生成测试用例")
async def generate_batch(req: BatchGenerateRequest):
    """批量并行生成测试用例"""
    try:
        generator = create_generator(req.model_config)
        results = await generator.batch_generate(
            requirements=req.requirements,
            test_type=req.test_type,
            max_concurrent=req.max_concurrent,
            max_iterations=req.max_iterations,
        )
        statistics = generator.get_statistics(results)
        return respModel.ok_resp({
            "results": [state.to_dict() for state in results],
            "statistics": statistics,
        })
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return respModel.error_resp(str(e))


@router.post("/swagger/parse", summary="解析Swagger文档")
async def parse_swagger(req: SwaggerParseRequest):
    """解析Swagger文档，返回API列表"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(req.swagger_url, timeout=30.0)
            response.raise_for_status()
            swagger_doc = response.json()

        apis = []
        paths = swagger_doc.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    apis.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "parameters": details.get("parameters", []),
                        "tags": details.get("tags", []),
                    })

        return respModel.ok_resp({"apis": apis, "total": len(apis)})
    except Exception as e:
        logger.error(f"Swagger parse error: {e}")
        return respModel.error_resp(str(e))


@router.post("/model/test", summary="测试模型连接")
async def test_model(req: ModelTestRequest):
    """测试模型API连接"""
    result = await ModelService.test_connection(
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
    return respModel.ok_resp(ModelService.list_providers())


@router.get("/statistics", summary="获取生成统计")
async def get_statistics(session: Session = Depends(get_session)):
    """获取生成统计数据"""
    # TODO: 从数据库查询统计数据
    return respModel.ok_resp({
        "total_generations": 0,
        "total_tokens": 0,
        "average_score": 0,
        "success_rate": 0,
    })
