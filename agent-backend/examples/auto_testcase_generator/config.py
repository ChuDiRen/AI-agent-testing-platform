"""配置管理"""
import os
from pathlib import Path
from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class Config:
    """应用配置（参考 sql_agent.py 实现）"""
    # API Key - 优先从环境变量读取，否则使用默认值
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "sk-f79fae69b11a4fce88e04805bd6314b7")
    
    # 模型配置 - 格式：provider:model_name
    # 全部使用快速模型（deepseek-chat），避免 reasoner 思考模型响应慢
    reader_model: str = "deepseek:deepseek-chat"
    writer_model: str = "deepseek:deepseek-chat"  # 改为快速模型
    reviewer_model: str = "deepseek:deepseek-chat"  # 显式定义审查模型
    
    # 数据库和提示词路径
    checkpoint_db: Path = Path(__file__).parent / "checkpoints.db"
    testcases_db: Path = Path(__file__).parent / "testcases.db"
    prompts_dir: Path = Path(__file__).parent / "prompts"
    
    @cached_property
    def reader_prompt(self) -> str:
        """需求分析提示词"""
        return (self.prompts_dir / "TESTCASE_READER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def writer_prompt(self) -> str:
        """用例生成提示词（使用简化版，避免提示词过长导致超时）"""
        # 优先使用简化版提示词
        simple_prompt_file = self.prompts_dir / "TESTCASE_WRITER_SYSTEM_MESSAGE_SIMPLE.txt"
        if simple_prompt_file.exists():
            return simple_prompt_file.read_text(encoding='utf-8')
        # 降级使用完整版
        return (self.prompts_dir / "TESTCASE_WRITER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def reviewer_prompt(self) -> str:
        """用例审查提示词"""
        return (self.prompts_dir / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')


config = Config()

