"""
BaseAgent - 智能体基类

定义所有智能体的通用接口和行为
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import TestCaseState, GenerationStage
from ..prompts import load_prompt

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, str, float], None]  # (stage, message, progress)


class BaseAgent(ABC):
    """智能体基类"""

    name: str = "base"
    stage: GenerationStage = GenerationStage.INIT
    temperature: float = 0.5
    prompt_name: str = ""

    def __init__(
        self,
        model: ChatOpenAI,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        self.model = model
        self.progress_callback = progress_callback
        self._system_prompt = load_prompt(self.prompt_name) if self.prompt_name else ""

    def emit_progress(self, message: str, progress: float = 0.0):
        """发送进度事件"""
        if self.progress_callback:
            self.progress_callback(self.stage.value, message, progress)

    @abstractmethod
    async def process(self, state: TestCaseState) -> TestCaseState:
        """处理状态，子类必须实现"""
        pass

    async def run(self, state: TestCaseState) -> TestCaseState:
        """执行智能体"""
        logger.info(f"Agent {self.name} starting...")
        self.emit_progress(f"{self.name} 开始处理...", 0.0)
        state.stage = self.stage
        try:
            state = await self.process(state)
            self.emit_progress(f"{self.name} 处理完成", 100.0)
            logger.info(f"Agent {self.name} completed")
        except Exception as e:
            logger.error(f"Agent {self.name} failed: {e}")
            state.error = str(e)
            self.emit_progress(f"{self.name} 处理失败: {e}", 0.0)
        return state


    async def invoke_llm(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """调用LLM"""
        messages = []
        prompt = system_prompt or self._system_prompt
        if prompt:
            messages.append(SystemMessage(content=prompt))
        messages.append(HumanMessage(content=user_message))

        try:
            response = await self.model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise

    def update_token_usage(self, state: TestCaseState, tokens: int):
        """更新Token使用统计"""
        agent_key = f"{self.name}_tokens"
        state.token_usage[agent_key] = state.token_usage.get(agent_key, 0) + tokens
