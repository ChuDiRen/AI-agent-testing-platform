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
from sqlmodel import Session, select, func
from sse_starlette.sse import EventSourceResponse

from core.database import get_session
from core.resp_model import respModel
from ..model.AiGenerateHistory import AiGenerateHistory
from ..model.AiModel import AiModel
from ..langgraph import TestCaseGenerator, TestCaseState
from ..langgraph.generator import GeneratorConfig
from ..langgraph.services import ModelService, PROVIDER_CONFIGS, DatabaseModelService

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


# ==================== Helper Functions ====================

def create_generator_from_db(session: Session, model_config: Optional[ModelConfigRequest] = None) -> TestCaseGenerator:
    """
    创建生成器实例，优先使用数据库配置
    
    Args:
        session: 数据库会话
        model_config: 可选的模型配置请求
        
    Returns:
        TestCaseGenerator实例
    """
    api_key = None
    provider = "siliconflow"
    model_code = "deepseek-ai/DeepSeek-V3"
    
    # 1. 优先使用model_id从数据库获取配置
    if model_config and model_config.model_id:
        db_model = DatabaseModelService.get_enabled_model(session, model_config.model_id)
        if db_model:
            api_key = db_model["api_key"]
            provider = db_model["provider"].lower()
            model_code = db_model["model_code"]
            logger.info(f"Using database model: {db_model['model_name']} ({model_code})")
    
    # 2. 如果没有model_id，尝试从数据库获取第一个启用的模型
    if not api_key:
        db_model = DatabaseModelService.get_enabled_model(session)
        if db_model:
            api_key = db_model["api_key"]
            provider = db_model["provider"].lower()
            model_code = db_model["model_code"]
            logger.info(f"Using default database model: {db_model['model_name']} ({model_code})")
    
    # 3. 使用请求中的配置覆盖
    if model_config:
        if model_config.api_key:
            api_key = model_config.api_key
        if model_config.provider:
            provider = model_config.provider
    
    # 4. 如果仍然没有api_key，抛出错误
    if not api_key:
        raise ValueError("未找到可用的AI模型配置，请在数据库中配置模型或在请求中提供api_key")
    
    # 确定各智能体使用的模型
    reader_model = model_config.reader_model if model_config and model_config.reader_model else model_code
    writer_model = model_config.writer_model if model_config and model_config.writer_model else model_code
    reviewer_model = model_config.reviewer_model if model_config and model_config.reviewer_model else model_code
    
    # 如果provider不在预定义列表中，尝试从数据库模型获取base_url
    if provider.lower() not in PROVIDER_CONFIGS:
        # 自定义provider，需要从数据库获取api_url
        if db_model and db_model.get("api_url"):
            # 动态添加provider配置
            PROVIDER_CONFIGS[provider.lower()] = {
                "base_url": db_model["api_url"].rstrip("/chat/completions").rstrip("/v1"),
                "default_model": model_code,
                "display_name": provider,
                "models": [model_code],
            }
    
    config = GeneratorConfig(
        api_key=api_key,
        provider=provider,
        reader_model=reader_model,
        writer_model=writer_model,
        reviewer_model=reviewer_model,
    )
    
    return TestCaseGenerator(config)


def create_generator(model_config: Optional[ModelConfigRequest]) -> TestCaseGenerator:
    """创建生成器实例（兼容旧接口）"""
    if model_config and model_config.api_key:
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
async def generate_stream(req: GenerateRequest, session: Session = Depends(get_session), current_user = Depends(None)):
    """流式生成测试用例，通过SSE推送进度"""
    async def event_generator() -> AsyncGenerator[str, None]:
        events = []

        def progress_callback(stage: str, message: str, progress: float):
            events.append({
                "type": "stage_progress",
                "data": {"stage": stage, "message": message, "progress": progress}
            })

        def error_callback(stage: str, message: str, exception: Exception):
            events.append({
                "type": "error",
                "data": {"stage": stage, "message": message, "error": str(exception)}
            })

        try:
            # 优先使用数据库配置的模型
            generator = create_generator_from_db(session, req.llm_config)
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'stage_start', 'data': {'stage': 'init', 'message': '开始生成...'}})}\n\n"

            state = await generator.generate(
                requirement=req.requirement,
                test_type=req.test_type,
                max_iterations=req.max_iterations,
                progress_callback=progress_callback,
                error_callback=error_callback,
                db_session=session,
            )

            # 发送进度事件
            for event in events:
                yield f"data: {json.dumps(event)}\n\n"

            # 发送测试用例
            if state.testcases:
                yield f"data: {json.dumps({'type': 'testcase', 'data': state.testcases})}\n\n"

            # 保存生成历史
            if state.completed:
                try:
                    user_id = current_user.id if current_user else 1
                    history = AiGenerateHistory(
                        user_id=user_id,
                        conversation_id=0,
                        model_id=0,
                        requirement_text=req.requirement,
                        test_type=req.test_type,
                        case_count=0,
                        generate_status="success",
                        result_data=state.testcases,
                        create_time=datetime.now()
                    )
                    # 尝试解析用例数量
                    if state.testcases:
                        try:
                            # 尝试提取JSON
                            import re
                            json_str = state.testcases
                            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", json_str)
                            if json_match:
                                json_str = json_match.group(1).strip()
                            else:
                                brace_match = re.search(r"\{[\s\S]*\}", json_str)
                                if brace_match:
                                    json_str = brace_match.group(0)
                            
                            data = json.loads(json_str)
                            if "test_cases" in data:
                                history.case_count = len(data["test_cases"])
                        except Exception as e:
                            logger.warning(f"Failed to count test cases: {e}")
                    
                    session.add(history)
                    session.commit()
                except Exception as e:
                    logger.error(f"Failed to save history: {e}")

            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done', 'data': {'quality_score': state.quality_score, 'iteration': state.iteration, 'duration': state.get_duration_seconds(), 'completed': state.completed}})}\n\n"

        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': {'error': str(e)}})}\n\n"

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@router.post("/generate/batch", summary="批量生成测试用例")
async def generate_batch(req: BatchGenerateRequest, session: Session = Depends(get_session), current_user = Depends(None)):
    """批量并行生成测试用例"""
    try:
        # 优先使用数据库配置的模型
        generator = create_generator_from_db(session, req.llm_config)
        results = await generator.batch_generate(
            requirements=req.requirements,
            test_type=req.test_type,
            max_concurrent=req.max_concurrent,
            max_iterations=req.max_iterations,
        )
        statistics = generator.get_statistics(results)

        # Save history
        try:
            user_id = current_user.id if current_user else 1
            for i, state in enumerate(results):
                if state.completed:
                    history = AiGenerateHistory(
                        user_id=user_id,
                        conversation_id=0,
                        model_id=0,
                        requirement_text=req.requirements[i] if i < len(req.requirements) else "",
                        test_type=req.test_type,
                        case_count=0,
                        generate_status="success",
                        result_data=state.testcases,
                        create_time=datetime.now()
                    )
                    # 尝试解析用例数量
                    if state.testcases:
                        try:
                            import re
                            json_str = state.testcases
                            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", json_str)
                            if json_match:
                                json_str = json_match.group(1).strip()
                            else:
                                brace_match = re.search(r"\{[\s\S]*\}", json_str)
                                if brace_match:
                                    json_str = brace_match.group(0)
                            
                            data = json.loads(json_str)
                            if "test_cases" in data:
                                history.case_count = len(data["test_cases"])
                        except:
                            pass
                    session.add(history)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to save batch history: {e}")

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


@router.get("/models/db", summary="获取数据库配置的模型")
async def list_db_models(session: Session = Depends(get_session)):
    """获取数据库中配置的所有启用模型"""
    try:
        models = DatabaseModelService.get_all_enabled_models(session)
        return respModel.ok_resp({
            "models": models,
            "total": len(models)
        })
    except Exception as e:
        logger.error(f"Failed to get database models: {e}")
        return respModel.error_resp(str(e))


@router.get("/prompts/{agent_type}", summary="获取智能体提示词")
async def get_agent_prompt(
    agent_type: str,
    test_type: str = Query(default="API", description="测试类型"),
    session: Session = Depends(get_session)
):
    """获取指定智能体的提示词模板"""
    try:
        from ..langgraph.prompts import load_prompt_with_fallback
        
        prompt = load_prompt_with_fallback(session, agent_type, test_type)
        if prompt:
            return respModel.ok_resp({
                "agent_type": agent_type,
                "test_type": test_type,
                "prompt": prompt
            })
        else:
            return respModel.error_resp(f"未找到 {agent_type} 的提示词模板")
    except Exception as e:
        logger.error(f"Failed to get prompt: {e}")
        return respModel.error_resp(str(e))


@router.get("/statistics", summary="获取生成统计")
async def get_statistics(session: Session = Depends(get_session)):
    """获取生成统计数据"""
    try:
        # Total generations
        total_generations = session.exec(select(func.count(AiGenerateHistory.id))).one()
        
        # Success count (assuming generate_status='success')
        success_count = session.exec(select(func.count(AiGenerateHistory.id)).where(AiGenerateHistory.generate_status == "success")).one()
        
        # Calculate success rate
        success_rate = (success_count / total_generations * 100) if total_generations > 0 else 0
        
        # Total cases generated
        total_cases = session.exec(select(func.sum(AiGenerateHistory.case_count))).one() or 0
        
        return respModel.ok_resp({
            "total_generations": total_generations,
            "total_tokens": 0,
            "average_score": 0,
            "success_rate": round(success_rate, 2),
            "total_cases": total_cases
        })
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return respModel.error_resp(str(e))


# ==================== LangGraph SDK 兼容端点 ====================
# 这些端点用于支持 @langchain/langgraph-sdk React组件

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
    try:
        # 从生成历史中获取线程
        histories = session.exec(
            select(AiGenerateHistory)
            .order_by(AiGenerateHistory.create_time.desc())
            .limit(50)
        ).all()
        
        threads = []
        for h in histories:
            threads.append({
                "thread_id": str(h.id),
                "created_at": h.create_time.isoformat() if h.create_time else None,
                "updated_at": h.modify_time.isoformat() if h.modify_time else None,
                "metadata": {
                    "requirement": h.requirement[:100] if h.requirement else "",
                    "test_type": h.test_type,
                    "status": h.generate_status
                }
            })
        
        return threads
    except Exception as e:
        logger.error(f"Failed to list threads: {e}")
        return []


@router.post("/threads", summary="创建新线程")
async def create_thread(session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 创建新线程"""
    try:
        # 创建一个新的生成历史记录作为线程
        history = AiGenerateHistory(
            requirement="",
            test_type="API",
            generate_status="pending",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(history)
        session.commit()
        session.refresh(history)
        
        return {
            "thread_id": str(history.id),
            "created_at": history.create_time.isoformat(),
            "metadata": {}
        }
    except Exception as e:
        logger.error(f"Failed to create thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/state", summary="获取线程状态")
async def get_thread_state(thread_id: str, session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 获取线程状态"""
    try:
        history = session.get(AiGenerateHistory, int(thread_id))
        if not history:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = []
        if history.requirement:
            messages.append({
                "type": "human",
                "content": history.requirement
            })
        if history.result:
            messages.append({
                "type": "ai", 
                "content": history.result
            })
        
        return {
            "values": {
                "messages": messages
            },
            "next": [],
            "config": {
                "configurable": {
                    "thread_id": thread_id
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get thread state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/runs/stream", summary="流式运行")
async def stream_run(request: dict, session: Session = Depends(get_session)):
    """LangGraph SDK兼容 - 流式运行智能体"""
    async def event_generator():
        try:
            thread_id = request.get("thread_id")
            input_data = request.get("input", {})
            messages = input_data.get("messages", [])
            
            # 获取用户消息
            requirement = ""
            for msg in messages:
                if isinstance(msg, dict) and msg.get("type") == "human":
                    requirement = msg.get("content", "")
                elif isinstance(msg, str):
                    requirement = msg
            
            if not requirement:
                yield f"data: {json.dumps({'type': 'error', 'error': '请输入需求描述'})}\n\n"
                return
            
            # 创建生成器
            generator = create_generator_from_db(session)
            
            # 生成测试用例
            events = []
            def progress_callback(stage, message, data=None):
                events.append({
                    "type": "progress",
                    "stage": stage,
                    "message": message,
                    "data": data
                })
            
            state = await generator.generate(
                requirement=requirement,
                test_type="API",
                max_iterations=2,
                progress_callback=progress_callback,
                db_session=session
            )
            
            # 发送消息更新
            if state and state.test_cases:
                result_content = json.dumps({
                    "test_cases": [tc.model_dump() if hasattr(tc, 'model_dump') else tc for tc in state.test_cases],
                    "quality_score": state.quality_score.model_dump() if state.quality_score and hasattr(state.quality_score, 'model_dump') else None
                }, ensure_ascii=False, indent=2)
                
                yield f"data: {json.dumps({'type': 'messages/partial', 'data': [{'type': 'ai', 'content': result_content}]})}\n\n"
            
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream run error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return EventSourceResponse(event_generator(), media_type="text/event-stream")
