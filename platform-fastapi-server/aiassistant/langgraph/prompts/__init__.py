"""
LangGraph Prompts Module

包含各智能体的提示词模板
"""
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """加载提示词模板"""
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return ""


__all__ = ["load_prompt", "PROMPTS_DIR"]
