"""配置管理"""
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """应用配置（参考 sql_agent.py 实现）"""
    # API Key - 优先从环境变量读取，否则使用默认值
    api_key: str = os.getenv("SILICONFLOW_API_KEY", "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem")
    
    # 模型配置 - 格式：provider:model_name
    # 使用 SiliconFlow 的 Qwen2.5-72B-Instruct 模型（速度快3-5倍,质量仍然优秀）
    reader_model: str = "siliconflow:Qwen/Qwen2.5-72B-Instruct"
    writer_model: str = "siliconflow:Qwen/Qwen2.5-72B-Instruct"
    reviewer_model: str = "siliconflow:Qwen/Qwen2.5-72B-Instruct"
    
    # 数据库和提示词路径
    checkpoint_db: Path = Path(__file__).parent.parent.parent / "data" / "checkpoints.db"
    testcases_db: Path = Path(__file__).parent.parent.parent / "data" / "testcases.db"
    prompts_dir: Path = Path(__file__).parent / "prompts"
    
    @cached_property
    def reader_prompt(self) -> str:
        """需求分析提示词"""
        return (self.prompts_dir / "TESTCASE_READER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def writer_prompt(self) -> str:
        """用例生成提示词"""
        return (self.prompts_dir / "TESTCASE_WRITER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')
    
    @cached_property
    def reviewer_prompt(self) -> str:
        """用例审查提示词"""
        return (self.prompts_dir / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt").read_text(encoding='utf-8')


config = Config()

