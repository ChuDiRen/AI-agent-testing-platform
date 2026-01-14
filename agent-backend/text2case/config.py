"""配置管理"""
import os
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

# 导入自定义的模型加载工具（支持国产大模型）
from examples.utils import load_chat_model


@dataclass(frozen=True)
class Config:
    """应用配置"""
    api_key: str = os.getenv("SILICONFLOW_API_KEY", "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem")
    model_name: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    # 兼容旧配置
    reader_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    writer_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    reviewer_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    # 测试用例数据库（业务数据，非记忆系统）
    testcases_db: Path = Path(__file__).parent.parent.resolve() / "data" / "testcases.db"
    prompts_dir: Path = Path(__file__).parent / "prompts"
    
    @cached_property
    def reader_prompt(self) -> str:
        return (self.prompts_dir / "TESTCASE_READER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def writer_prompt(self) -> str:
        return (self.prompts_dir / "TESTCASE_WRITER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def reviewer_prompt(self) -> str:
        return (self.prompts_dir / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')


@dataclass
class LLMConfig:
    """LLM 配置"""
    model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    api_key: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    streaming: bool = True


def get_model(config: LLMConfig = None) -> BaseChatModel:
    """获取 LLM 模型实例
    
    Args:
        config: LLM 配置，如果为 None 则使用默认配置
        
    Returns:
        配置好的 LLM 模型
    """
    if config is None:
        config = LLMConfig()
    
    app_config = Config()
    api_key = config.api_key or app_config.api_key
    
    model_str = config.model
    
    if model_str.startswith("siliconflow:"):
        model_name = model_str.replace("siliconflow:", "")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=config.streaming,
        )
    
    # 其他模型使用自定义的 load_chat_model
    return load_chat_model(model_str, temperature=config.temperature)


def load_prompt(prompt_name: str, **kwargs) -> str:
    """加载提示词
    
    Args:
        prompt_name: 提示词名称（不含扩展名）
        **kwargs: 格式化参数
        
    Returns:
        格式化后的提示词
    """
    config = Config()
    
    # 尝试 .md 和 .txt 扩展名
    for ext in [".md", ".txt"]:
        prompt_path = config.prompts_dir / f"{prompt_name}{ext}"
        if prompt_path.exists():
            content = prompt_path.read_text(encoding='utf-8')
            if kwargs:
                for key, value in kwargs.items():
                    content = content.replace(f"{{{key}}}", str(value))
            return content
    
    return ""


# 默认配置实例
config = Config()
