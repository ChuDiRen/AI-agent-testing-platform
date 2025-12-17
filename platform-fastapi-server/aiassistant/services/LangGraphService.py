"""
LangGraph测试用例生成服务层
"""
import json
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable, AsyncGenerator

import httpx
from sqlmodel import Session, select, func

from ..model.AiGenerateHistory import AiGenerateHistory
from ..model.AiModel import AiModel
from ..langgraph import TestCaseGenerator, TestCaseState
from ..langgraph.generator import GeneratorConfig
from ..langgraph.services import ModelService, PROVIDER_CONFIGS, DatabaseModelService

logger = logging.getLogger(__name__)


class LangGraphService:
    """LangGraph测试用例生成服务"""
    
    @staticmethod
    def create_generator_from_db(
        session: Session,
        model_id: Optional[int] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        reader_model: Optional[str] = None,
        writer_model: Optional[str] = None,
        reviewer_model: Optional[str] = None
    ) -> TestCaseGenerator:
        """
        创建生成器实例，优先使用数据库配置
        
        Args:
            session: 数据库会话
            model_id: 数据库模型ID
            api_key: API密钥
            provider: 提供商
            reader_model: 分析器模型
            writer_model: 编写器模型
            reviewer_model: 评审器模型
            
        Returns:
            TestCaseGenerator实例
        """
        db_model = None
        final_api_key = api_key
        final_provider = provider or "siliconflow"
        model_code = "deepseek-ai/DeepSeek-V3"
        
        # 1. 优先使用model_id从数据库获取配置
        if model_id:
            db_model = DatabaseModelService.get_enabled_model(session, model_id)
            if db_model:
                final_api_key = db_model["api_key"]
                final_provider = db_model["provider"].lower()
                model_code = db_model["model_code"]
                logger.info(f"Using database model: {db_model['model_name']} ({model_code})")
        
        # 2. 如果没有model_id，尝试从数据库获取第一个启用的模型
        if not final_api_key:
            db_model = DatabaseModelService.get_enabled_model(session)
            if db_model:
                final_api_key = db_model["api_key"]
                final_provider = db_model["provider"].lower()
                model_code = db_model["model_code"]
                logger.info(f"Using default database model: {db_model['model_name']} ({model_code})")
        
        # 3. 如果仍然没有api_key，抛出错误
        if not final_api_key:
            raise ValueError("未找到可用的AI模型配置，请在数据库中配置模型或在请求中提供api_key")
        
        # 确定各智能体使用的模型
        final_reader_model = reader_model or model_code
        final_writer_model = writer_model or model_code
        final_reviewer_model = reviewer_model or model_code
        
        # 如果provider不在预定义列表中，尝试从数据库模型获取base_url
        if final_provider.lower() not in PROVIDER_CONFIGS:
            if db_model and db_model.get("api_url"):
                PROVIDER_CONFIGS[final_provider.lower()] = {
                    "base_url": db_model["api_url"].rstrip("/chat/completions").rstrip("/v1"),
                    "default_model": model_code,
                    "display_name": final_provider,
                    "models": [model_code],
                }
        
        config = GeneratorConfig(
            api_key=final_api_key,
            provider=final_provider,
            reader_model=final_reader_model,
            writer_model=final_writer_model,
            reviewer_model=final_reviewer_model,
        )
        
        return TestCaseGenerator(config)
    
    @staticmethod
    def create_generator(
        api_key: Optional[str] = None,
        provider: str = "siliconflow",
        reader_model: Optional[str] = None,
        writer_model: Optional[str] = None,
        reviewer_model: Optional[str] = None
    ) -> TestCaseGenerator:
        """创建生成器实例（兼容旧接口）"""
        if api_key:
            config = GeneratorConfig(
                api_key=api_key,
                provider=provider,
                reader_model=reader_model or PROVIDER_CONFIGS.get(provider, {}).get("default_model", ""),
                writer_model=writer_model or PROVIDER_CONFIGS.get(provider, {}).get("default_model", ""),
                reviewer_model=reviewer_model or PROVIDER_CONFIGS.get(provider, {}).get("default_model", ""),
            )
        else:
            config = GeneratorConfig(
                api_key="",
                provider="siliconflow",
                reader_model="deepseek-ai/DeepSeek-V3",
                writer_model="deepseek-ai/DeepSeek-V3",
                reviewer_model="deepseek-ai/DeepSeek-V3",
            )
        return TestCaseGenerator(config)
    
    @staticmethod
    async def generate_stream(
        session: Session,
        requirement: str,
        test_type: str = "API",
        max_iterations: int = 2,
        model_id: Optional[int] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        reader_model: Optional[str] = None,
        writer_model: Optional[str] = None,
        reviewer_model: Optional[str] = None,
        user_id: int = 1
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式生成测试用例
        
        Args:
            session: 数据库会话
            requirement: 需求描述
            test_type: 测试类型
            max_iterations: 最大迭代次数
            model_id: 模型ID
            api_key: API密钥
            provider: 提供商
            reader_model: 分析器模型
            writer_model: 编写器模型
            reviewer_model: 评审器模型
            user_id: 用户ID
            
        Yields:
            事件字典
        """
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
            generator = LangGraphService.create_generator_from_db(
                session, model_id, api_key, provider,
                reader_model, writer_model, reviewer_model
            )
            
            yield {"type": "stage_start", "data": {"stage": "init", "message": "开始生成..."}}

            state = await generator.generate(
                requirement=requirement,
                test_type=test_type,
                max_iterations=max_iterations,
                progress_callback=progress_callback,
                error_callback=error_callback,
                db_session=session,
            )

            for event in events:
                yield event

            if state.testcases:
                yield {"type": "testcase", "data": state.testcases}

            # 保存生成历史
            if state.completed:
                try:
                    history = AiGenerateHistory(
                        user_id=user_id,
                        conversation_id=0,
                        model_id=0,
                        requirement_text=requirement,
                        test_type=test_type,
                        case_count=0,
                        generate_status="success",
                        result_data=state.testcases,
                        create_time=datetime.now()
                    )
                    if state.testcases:
                        try:
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

            yield {
                "type": "done",
                "data": {
                    "quality_score": state.quality_score,
                    "iteration": state.iteration,
                    "duration": state.get_duration_seconds(),
                    "completed": state.completed
                }
            }

        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield {"type": "error", "data": {"error": str(e)}}
    
    @staticmethod
    async def generate_batch(
        session: Session,
        requirements: List[str],
        test_type: str = "API",
        max_concurrent: int = 5,
        max_iterations: int = 2,
        model_id: Optional[int] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        user_id: int = 1
    ) -> Dict[str, Any]:
        """
        批量生成测试用例
        
        Args:
            session: 数据库会话
            requirements: 需求列表
            test_type: 测试类型
            max_concurrent: 最大并发数
            max_iterations: 最大迭代次数
            model_id: 模型ID
            api_key: API密钥
            provider: 提供商
            user_id: 用户ID
            
        Returns:
            结果字典
        """
        try:
            generator = LangGraphService.create_generator_from_db(
                session, model_id, api_key, provider
            )
            results = await generator.batch_generate(
                requirements=requirements,
                test_type=test_type,
                max_concurrent=max_concurrent,
                max_iterations=max_iterations,
            )
            statistics = generator.get_statistics(results)

            # Save history
            try:
                for i, state in enumerate(results):
                    if state.completed:
                        history = AiGenerateHistory(
                            user_id=user_id,
                            conversation_id=0,
                            model_id=0,
                            requirement_text=requirements[i] if i < len(requirements) else "",
                            test_type=test_type,
                            case_count=0,
                            generate_status="success",
                            result_data=state.testcases,
                            create_time=datetime.now()
                        )
                        if state.testcases:
                            try:
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

            return {
                "success": True,
                "results": [state.to_dict() for state in results],
                "statistics": statistics,
            }
        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def parse_swagger(swagger_url: str) -> Dict[str, Any]:
        """
        解析Swagger文档
        
        Args:
            swagger_url: Swagger文档URL
            
        Returns:
            API列表
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(swagger_url, timeout=30.0)
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

            return {"success": True, "apis": apis, "total": len(apis)}
        except Exception as e:
            logger.error(f"Swagger parse error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def test_model(
        provider: str,
        api_key: str,
        model_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        测试模型连接
        
        Args:
            provider: 提供商
            api_key: API密钥
            model_code: 模型代码
            
        Returns:
            测试结果
        """
        return await ModelService.test_connection(
            provider=provider,
            api_key=api_key,
            model_code=model_code,
        )
    
    @staticmethod
    def list_providers() -> List[Dict[str, Any]]:
        """获取所有支持的模型提供商"""
        return ModelService.list_providers()
    
    @staticmethod
    def get_db_models(session: Session) -> Dict[str, Any]:
        """
        获取数据库配置的模型
        
        Args:
            session: 数据库会话
            
        Returns:
            模型列表
        """
        try:
            models = DatabaseModelService.get_all_enabled_models(session)
            return {"success": True, "models": models, "total": len(models)}
        except Exception as e:
            logger.error(f"Failed to get database models: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_agent_prompt(
        session: Session,
        agent_type: str,
        test_type: str = "API"
    ) -> Dict[str, Any]:
        """
        获取智能体提示词
        
        Args:
            session: 数据库会话
            agent_type: 智能体类型
            test_type: 测试类型
            
        Returns:
            提示词信息
        """
        try:
            from ..langgraph.prompts import load_prompt_with_fallback
            
            prompt = load_prompt_with_fallback(session, agent_type, test_type)
            if prompt:
                return {
                    "success": True,
                    "agent_type": agent_type,
                    "test_type": test_type,
                    "prompt": prompt
                }
            else:
                return {"success": False, "error": f"未找到 {agent_type} 的提示词模板"}
        except Exception as e:
            logger.error(f"Failed to get prompt: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_statistics(session: Session) -> Dict[str, Any]:
        """
        获取生成统计
        
        Args:
            session: 数据库会话
            
        Returns:
            统计数据
        """
        try:
            total_generations = session.exec(select(func.count(AiGenerateHistory.id))).one()
            success_count = session.exec(
                select(func.count(AiGenerateHistory.id)).where(AiGenerateHistory.generate_status == "success")
            ).one()
            success_rate = (success_count / total_generations * 100) if total_generations > 0 else 0
            total_cases = session.exec(select(func.sum(AiGenerateHistory.case_count))).one() or 0
            
            return {
                "success": True,
                "total_generations": total_generations,
                "total_tokens": 0,
                "average_score": 0,
                "success_rate": round(success_rate, 2),
                "total_cases": total_cases
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def list_threads(session: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取线程列表
        
        Args:
            session: 数据库会话
            limit: 限制数量
            
        Returns:
            线程列表
        """
        try:
            histories = session.exec(
                select(AiGenerateHistory)
                .order_by(AiGenerateHistory.create_time.desc())
                .limit(limit)
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
    
    @staticmethod
    def create_thread(session: Session) -> Dict[str, Any]:
        """
        创建新线程
        
        Args:
            session: 数据库会话
            
        Returns:
            线程信息
        """
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
    
    @staticmethod
    def get_thread_state(session: Session, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        获取线程状态
        
        Args:
            session: 数据库会话
            thread_id: 线程ID
            
        Returns:
            线程状态
        """
        try:
            history = session.get(AiGenerateHistory, int(thread_id))
            if not history:
                return None
            
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
        except Exception as e:
            logger.error(f"Failed to get thread state: {e}")
            return None
