"""
提示词加载器

支持从Markdown文件加载提示词，带LRU缓存
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional


# 提示词目录路径
PROMPTS_DIR = Path(__file__).parent


def get_prompt_path(name: str) -> Path:
    """获取提示词文件路径
    
    Args:
        name: 提示词名称（不含.md后缀）
        
    Returns:
        提示词文件的完整路径
    """
    return PROMPTS_DIR / f"{name}.md"


@lru_cache(maxsize=32)
def _load_prompt_file(name: str) -> str:
    """加载提示词文件内容（带缓存）
    
    Args:
        name: 提示词名称
        
    Returns:
        提示词文件内容
        
    Raises:
        FileNotFoundError: 提示词文件不存在
    """
    prompt_file = get_prompt_path(name)
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    return prompt_file.read_text(encoding="utf-8")


def load_prompt(name: str, **kwargs) -> str:
    """加载并格式化提示词
    
    Args:
        name: 提示词名称（如 'supervisor', 'schema_agent'）
        **kwargs: 用于格式化提示词的变量
        
    Returns:
        格式化后的提示词字符串
        
    Examples:
        >>> prompt = load_prompt("sql_generator", dialect="mysql", top_k=10)
    """
    template = _load_prompt_file(name)
    
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # 如果格式化失败，返回原始模板
            print(f"Warning: Failed to format prompt '{name}': {e}")
            return template
    
    return template


def clear_cache() -> None:
    """清除提示词缓存
    
    用于热重载场景，修改提示词文件后调用此函数
    """
    _load_prompt_file.cache_clear()


def list_prompts() -> list[str]:
    """列出所有可用的提示词
    
    Returns:
        提示词名称列表
    """
    return [f.stem for f in PROMPTS_DIR.glob("*.md")]
