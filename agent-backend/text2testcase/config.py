"""配置管理"""
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """应用配置"""
    api_key: str = os.getenv("SILICONFLOW_API_KEY", "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem")
    reader_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    writer_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    reviewer_model: str = "siliconflow:deepseek-ai/DeepSeek-V3"
    checkpoint_db: Path = Path(__file__).parent.parent.parent / "data" / "checkpoints.db"
    testcases_db: Path = Path(__file__).parent.parent.parent / "data" / "testcases.db"
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


config = Config()

