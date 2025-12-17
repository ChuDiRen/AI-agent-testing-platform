"""
LangGraph Server 兼容服务层
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator

from fastapi import HTTPException
from sqlmodel import Session, select

from ..model.AiGenerateHistory import AiGenerateHistory
from ..model.AiModel import AiModel
from ..langgraph import TestCaseGenerator
from ..langgraph.generator import GeneratorConfig
from ..langgraph.services import DatabaseModelService

logger = logging.getLogger(__name__)


class LangGraphServerService:
    """LangGraph Server 兼容服务"""
    
    @staticmethod
    def create_generator_from_db(session: Session) -> TestCaseGenerator:
        """从数据库配置创建生成器"""
        api_key = None
        provider = "siliconflow"
        model_code = "deepseek-ai/DeepSeek-V3"
        
        db_model = DatabaseModelService.get_enabled_model(session)
        if db_model:
            api_key = db_model["api_key"]
            provider = db_model["provider"].lower()
            model_code = db_model["model_code"]
            logger.info(f"Using database model: {db_model['model_name']} ({model_code})")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="请先在AI模型管理中配置API Key")
        
        config = GeneratorConfig(
            provider=provider,
            api_key=api_key,
            reader_model=model_code,
            writer_model=model_code,
            reviewer_model=model_code,
        )
        
        return TestCaseGenerator(config)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "version": "1.0.0",
            "name": "AI Agent Testing Platform - LangGraph Server"
        }
    
    @staticmethod
    def list_assistants() -> List[Dict[str, Any]]:
        """获取助手列表"""
        return [
            {
                "assistant_id": "testcase",
                "name": "测试用例生成助手",
                "graph_id": "testcase",
                "config": {},
                "metadata": {
                    "description": "基于LangGraph的多智能体测试用例生成系统"
                }
            }
        ]
    
    @staticmethod
    def get_assistant(assistant_id: str) -> Dict[str, Any]:
        """获取指定助手信息"""
        return {
            "assistant_id": assistant_id,
            "name": "测试用例生成助手",
            "graph_id": assistant_id,
            "config": {},
            "metadata": {
                "description": "基于LangGraph的多智能体测试用例生成系统"
            }
        }
    
    @staticmethod
    def create_thread(session: Session, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """创建新线程"""
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
            "updated_at": history.modify_time.isoformat(),
            "metadata": metadata or {},
            "status": "idle",
            "values": {}
        }
    
    @staticmethod
    def list_threads(
        session: Session,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取线程列表"""
        try:
            histories = session.exec(
                select(AiGenerateHistory)
                .order_by(AiGenerateHistory.create_time.desc())
                .limit(limit)
                .offset(offset)
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
                    },
                    "status": "idle" if h.generate_status == "success" else "busy"
                })
            
            return threads
        except Exception as e:
            logger.error(f"Failed to list threads: {e}")
            return []
    
    @staticmethod
    def get_thread(session: Session, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取线程详情"""
        try:
            history = session.get(AiGenerateHistory, int(thread_id))
            if not history:
                return None
            
            return {
                "thread_id": str(history.id),
                "created_at": history.create_time.isoformat() if history.create_time else None,
                "updated_at": history.modify_time.isoformat() if history.modify_time else None,
                "metadata": {
                    "requirement": history.requirement[:100] if history.requirement else "",
                    "test_type": history.test_type
                },
                "status": "idle"
            }
        except Exception as e:
            logger.error(f"Failed to get thread: {e}")
            return None
    
    @staticmethod
    def get_thread_state(session: Session, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取线程状态"""
        try:
            history = session.get(AiGenerateHistory, int(thread_id))
            if not history:
                return None
            
            messages = []
            if history.requirement:
                messages.append({
                    "type": "human",
                    "id": str(uuid.uuid4()),
                    "content": history.requirement
                })
            if history.result:
                messages.append({
                    "type": "ai",
                    "id": str(uuid.uuid4()),
                    "content": history.result
                })
            
            return {
                "values": {
                    "messages": messages
                },
                "next": [],
                "tasks": [],
                "config": {
                    "configurable": {
                        "thread_id": thread_id
                    }
                },
                "created_at": history.create_time.isoformat() if history.create_time else None,
                "parent_config": None
            }
        except Exception as e:
            logger.error(f"Failed to get thread state: {e}")
            return None
    
    @staticmethod
    async def stream_run(
        session: Session,
        thread_id: str,
        input_data: Dict[str, Any],
        stream_mode: str = "updates"
    ) -> AsyncGenerator[str, None]:
        """流式运行智能体"""
        try:
            messages = input_data.get("messages", [])
            
            # 获取用户消息
            requirement = ""
            for msg in messages:
                if isinstance(msg, dict):
                    msg_type = msg.get("type", "")
                    if msg_type == "human" or msg_type == "user":
                        requirement = msg.get("content", "")
                        break
                elif isinstance(msg, str):
                    requirement = msg
                    break
            
            if not requirement:
                if isinstance(input_data, str):
                    requirement = input_data
                elif "content" in input_data:
                    requirement = input_data["content"]
            
            if not requirement:
                yield f"event: error\ndata: {json.dumps({'error': '请输入需求描述'})}\n\n"
                return
            
            # 更新线程的需求
            history = session.get(AiGenerateHistory, int(thread_id))
            if history:
                history.requirement = requirement
                history.generate_status = "running"
                history.modify_time = datetime.now()
                session.commit()
            
            # 发送metadata事件
            run_id = str(uuid.uuid4())
            yield f"event: metadata\ndata: {json.dumps({'run_id': run_id})}\n\n"
            
            # 创建生成器
            try:
                generator = LangGraphServerService.create_generator_from_db(session)
            except HTTPException as e:
                yield f"event: error\ndata: {json.dumps({'error': e.detail})}\n\n"
                return
            
            # 发送开始事件
            yield f"event: updates\ndata: {json.dumps({'analyzer': {'status': 'starting', 'message': '开始分析需求...'}})}\n\n"
            
            # 生成测试用例
            try:
                state = await generator.generate(
                    requirement=requirement,
                    test_type="API",
                    max_iterations=2,
                    db_session=session
                )
                
                # 构建结果
                if state and state.test_cases:
                    result_data = {
                        "test_cases": [tc.model_dump() if hasattr(tc, 'model_dump') else tc for tc in state.test_cases],
                        "quality_score": state.quality_score.model_dump() if state.quality_score and hasattr(state.quality_score, 'model_dump') else None,
                        "analysis": state.analysis if hasattr(state, 'analysis') else None
                    }
                    
                    result_content = json.dumps(result_data, ensure_ascii=False, indent=2)
                    
                    ai_message = {
                        "type": "ai",
                        "id": str(uuid.uuid4()),
                        "content": result_content
                    }
                    
                    yield f"event: updates\ndata: {json.dumps({'messages': [ai_message]})}\n\n"
                    
                    if history:
                        history.result = result_content
                        history.generate_status = "success"
                        history.case_count = len(state.test_cases) if state.test_cases else 0
                        history.modify_time = datetime.now()
                        session.commit()
                else:
                    yield f"event: updates\ndata: {json.dumps({'error': '生成失败，未获取到测试用例'})}\n\n"
                    if history:
                        history.generate_status = "failed"
                        history.modify_time = datetime.now()
                        session.commit()
                
            except Exception as gen_error:
                logger.error(f"Generation error: {gen_error}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(gen_error)})}\n\n"
                if history:
                    history.generate_status = "failed"
                    history.modify_time = datetime.now()
                    session.commit()
                return
            
            yield f"event: end\ndata: {json.dumps({'status': 'completed'})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream run error: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    @staticmethod
    async def stream_run_stateless(
        session: Session,
        input_data: Dict[str, Any],
        stream_mode: str = "updates"
    ) -> AsyncGenerator[str, None]:
        """无状态流式运行（自动创建线程）"""
        # 创建新线程
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
        
        async for event in LangGraphServerService.stream_run(
            session, str(history.id), input_data, stream_mode
        ):
            yield event
