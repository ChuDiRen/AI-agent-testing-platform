"""
BaseAgent - 智能体基类

定义多智能体协作中每个智能体的通用接口
包含：进度回调、错误回调、重试逻辑、Token统计、提示词加载
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum

from agent_langgraph.core import ModelFactory
from agent_langgraph.tasks.text2case.prompts import load_prompt_with_fallback

logger = logging.getLogger(__name__)

# 回调类型定义
ProgressCallback = Callable[[str, str, float], None]  # (agent_name, message, progress)
ErrorCallback = Callable[[str, str, Exception], None]  # (agent_name, message, exception)


class AgentRole(str, Enum):
    """智能体角色"""
    SUPERVISOR = "supervisor"
    ANALYZER = "analyzer"
    DESIGNER = "designer"
    WRITER = "writer"
    REVIEWER = "reviewer"


@dataclass
class AgentResponse:
    """智能体响应"""
    agent_name: str
    content: str
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_usage: int = 0
    
    def to_message(self) -> Dict[str, Any]:
        """转换为消息格式"""
        return {
            "role": "assistant",
            "name": self.agent_name,
            "content": self.content,
        }


class BaseAgent(ABC):
    """
    智能体基类
    
    每个智能体负责特定任务，通过process方法处理状态
    
    功能：
    - 进度回调：emit_progress()
    - 错误回调：emit_error()
    - 重试逻辑：run() 方法带指数退避重试
    - Token统计：自动统计LLM调用的token消耗
    - 提示词加载：支持从文件或数据库加载
    """
    
    name: str = "base"
    role: AgentRole = AgentRole.SUPERVISOR
    description: str = "基础智能体"
    temperature: float = 0.3
    prompt_name: str = ""  # 提示词文件名（不含.txt）
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __init__(
        self,
        model_config=None,
        progress_callback: Optional[ProgressCallback] = None,
        error_callback: Optional[ErrorCallback] = None,
        db_session=None,
        test_type: str = "API",
    ):
        """
        初始化智能体
        
        Args:
            model_config: 可选的模型配置
            progress_callback: 进度回调函数
            error_callback: 错误回调函数
            db_session: 数据库会话（用于从数据库加载提示词）
            test_type: 测试类型
        """
        self._model = None
        self._model_config = model_config
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.db_session = db_session
        self.test_type = test_type
        self._system_prompt = None  # 延迟加载
        self._total_tokens = 0
    
    @property
    def model(self):
        """延迟加载模型"""
        if self._model is None:
            self._model = ModelFactory.get_model(
                config=self._model_config,
                temperature=self.temperature
            )
        return self._model
    
    @property
    def system_prompt(self) -> str:
        """延迟加载系统提示词"""
        if self._system_prompt is None:
            self._system_prompt = self._load_system_prompt()
        return self._system_prompt
    
    def _load_system_prompt(self) -> str:
        """加载系统提示词，优先从数据库加载"""
        if not self.prompt_name:
            return ""
        
        prompt = load_prompt_with_fallback(
            self.db_session,
            self.prompt_name,
            self.test_type
        )
        
        if prompt:
            logger.debug(f"Loaded prompt for {self.prompt_name}")
        
        return prompt or ""
    
    def emit_progress(self, message: str, progress: float = 0.0):
        """发送进度事件"""
        if self.progress_callback:
            self.progress_callback(self.name, message, progress)
    
    def emit_error(self, message: str, exception: Exception):
        """发送错误事件"""
        if self.error_callback:
            self.error_callback(self.name, message, exception)
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """
        处理状态，子类必须实现
        
        Args:
            state: 当前状态
            
        Returns:
            AgentResponse
        """
        pass
    
    async def run(self, state: Dict[str, Any]) -> AgentResponse:
        """
        执行智能体，带重试逻辑
        
        Args:
            state: 当前状态
            
        Returns:
            AgentResponse
        """
        logger.info(f"Agent {self.name} starting...")
        self.emit_progress(f"{self.name} 开始处理...", 0.0)
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.process(state)
                self.emit_progress(f"{self.name} 处理完成", 100.0)
                logger.info(f"Agent {self.name} completed")
                return response
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
        self.emit_progress(f"{self.name} 处理失败: {last_error}", 0.0)
        
        return AgentResponse(
            agent_name=self.name,
            content="",
            success=False,
            error=f"{self.name} 处理失败: {str(last_error)}",
        )
    
    async def invoke_llm(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        调用LLM，带错误处理和Token统计
        
        Args:
            user_message: 用户消息
            system_prompt: 可选的系统提示词（覆盖默认）
            
        Returns:
            LLM响应内容
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = []
        prompt = system_prompt or self.system_prompt
        if prompt:
            messages.append(SystemMessage(content=prompt))
        messages.append(HumanMessage(content=user_message))
        
        try:
            response = await self.model.ainvoke(messages)
            
            # 统计Token使用
            if hasattr(response, 'response_metadata'):
                usage = response.response_metadata.get('token_usage', {})
                tokens = usage.get('total_tokens', 0)
                self._total_tokens += tokens
            
            return response.content
        except asyncio.TimeoutError as e:
            logger.error(f"Agent {self.name} LLM invocation timeout: {e}")
            raise RuntimeError(f"模型调用超时: {e}") from e
        except Exception as e:
            logger.error(f"Agent {self.name} LLM invocation failed: {e}")
            raise
    
    def get_token_usage(self) -> int:
        """获取累计Token使用量"""
        return self._total_tokens
    
    def reset_token_usage(self):
        """重置Token统计"""
        self._total_tokens = 0
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, role={self.role.value})>"
