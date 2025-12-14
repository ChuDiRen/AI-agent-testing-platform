"""
LangGraph Prompts Module

包含各智能体的提示词模板
支持从文件或数据库加载
"""
from pathlib import Path
from typing import Optional
from sqlmodel import Session

PROMPTS_DIR = Path(__file__).parent

# 缓存从数据库加载的提示词
_db_prompt_cache: dict = {}


def load_prompt(name: str) -> str:
    """从文件加载提示词模板"""
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return ""


def load_prompt_from_db(
    session: Session,
    agent_type: str,
    test_type: str = "API",
    use_cache: bool = True
) -> Optional[str]:
    """
    从数据库加载提示词模板
    
    Args:
        session: 数据库会话
        agent_type: 智能体类型 (analyzer/designer/writer/reviewer)
        test_type: 测试类型 (API/Web/App)
        use_cache: 是否使用缓存
        
    Returns:
        提示词内容或None
    """
    cache_key = f"{agent_type}_{test_type}"
    
    if use_cache and cache_key in _db_prompt_cache:
        return _db_prompt_cache[cache_key]
    
    from ..services.db_model_service import DatabaseModelService
    
    prompt = DatabaseModelService.get_prompt_template(session, agent_type, test_type)
    
    if prompt and use_cache:
        _db_prompt_cache[cache_key] = prompt
    
    return prompt


def load_prompt_with_fallback(
    session: Optional[Session],
    agent_type: str,
    test_type: str = "API"
) -> str:
    """
    加载提示词，优先从数据库加载，失败则从文件加载
    
    Args:
        session: 数据库会话（可选）
        agent_type: 智能体类型
        test_type: 测试类型
        
    Returns:
        提示词内容
    """
    # 优先从数据库加载
    if session:
        db_prompt = load_prompt_from_db(session, agent_type, test_type)
        if db_prompt:
            return db_prompt
    
    # 回退到文件加载
    return load_prompt(agent_type)


def clear_prompt_cache():
    """清除提示词缓存"""
    global _db_prompt_cache
    _db_prompt_cache = {}


__all__ = [
    "load_prompt",
    "load_prompt_from_db",
    "load_prompt_with_fallback",
    "clear_prompt_cache",
    "PROMPTS_DIR"
]
