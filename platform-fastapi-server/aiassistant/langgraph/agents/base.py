"""
BaseAgent - 智能体基类

定义所有智能体的通用接口和行为
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import TestCaseState, GenerationStage
from ..prompts import load_prompt, load_prompt_with_fallback

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, str, float], None]  # (stage, message, progress)
ErrorCallback = Callable[[str, str, Exception], None]  # (stage, message, exception)


class BaseAgent(ABC):
    """智能体基类"""

    name: str = "base"
    stage: GenerationStage = GenerationStage.INIT
    temperature: float = 0.5
    prompt_name: str = ""
    max_retries: int = 3
    retry_delay: float = 1.0

    def __init__(
        self,
        model: ChatOpenAI,
        progress_callback: Optional[ProgressCallback] = None,
        error_callback: Optional[ErrorCallback] = None,
        db_session = None,
        test_type: str = "API",
    ):
        self.model = model
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.db_session = db_session
        self.test_type = test_type
        # 优先从数据库加载提示词，失败则从文件加载
        self._system_prompt = self._load_system_prompt()

    def emit_progress(self, message: str, progress: float = 0.0):
        """发送进度事件"""
        if self.progress_callback:
            self.progress_callback(self.stage.value, message, progress)

    def emit_error(self, message: str, exception: Exception):
        """发送错误事件"""
        if self.error_callback:
            self.error_callback(self.stage.value, message, exception)

    @abstractmethod
    async def process(self, state: TestCaseState) -> TestCaseState:
        """处理状态，子类必须实现"""
        pass

    async def run(self, state: TestCaseState) -> TestCaseState:
        """执行智能体，带重试逻辑"""
        logger.info(f"Agent {self.name} starting...")
        self.emit_progress(f"{self.name} 开始处理...", 0.0)
        state.stage = self.stage
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                state = await self.process(state)
                self.emit_progress(f"{self.name} 处理完成", 100.0)
                logger.info(f"Agent {self.name} completed")
                return state
            except Exception as e:
                last_error = e
                logger.warning(f"Agent {self.name} attempt {attempt + 1}/{self.max_retries} failed: {e}")
                self.emit_error(f"{self.name} 处理失败 (尝试 {attempt + 1}/{self.max_retries})", e)
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # 指数退避
                    self.emit_progress(f"{self.name} 重试中，等待 {delay:.1f}s...", 0.0)
                    await asyncio.sleep(delay)
        
        # 所有重试都失败
        logger.error(f"Agent {self.name} failed after {self.max_retries} attempts: {last_error}")
        state.error = f"{self.name} 处理失败: {str(last_error)}"
        self.emit_progress(f"{self.name} 处理失败: {last_error}", 0.0)
        return state

    async def invoke_llm(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """调用LLM，带错误处理"""
        messages = []
        prompt = system_prompt or self._system_prompt
        if prompt:
            messages.append(SystemMessage(content=prompt))
        messages.append(HumanMessage(content=user_message))

        try:
            response = await self.model.ainvoke(messages)
            return response.content
        except asyncio.TimeoutError as e:
            logger.error(f"LLM invocation timeout: {e}")
            raise RuntimeError(f"模型调用超时: {e}") from e
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise

    def update_token_usage(self, state: TestCaseState, tokens: int):
        """更新Token使用统计"""
        agent_key = f"{self.name}_tokens"
        state.token_usage[agent_key] = state.token_usage.get(agent_key, 0) + tokens

    def _load_system_prompt(self) -> str:
        """加载系统提示词，优先从数据库加载"""
        if not self.prompt_name:
            return ""
        
        # 优先从数据库加载
        prompt = load_prompt_with_fallback(
            self.db_session,
            self.prompt_name,
            self.test_type
        )
        
        if prompt:
            logger.debug(f"Loaded prompt for {self.prompt_name} from {'database' if self.db_session else 'file'}")
        
        return prompt
