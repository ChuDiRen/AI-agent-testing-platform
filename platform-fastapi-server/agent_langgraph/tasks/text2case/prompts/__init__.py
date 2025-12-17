"""
Text2Case Prompts Module

提示词管理，支持从文件或数据库加载
"""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent

# 提示词缓存
_prompt_cache: dict = {}


def load_prompt(name: str) -> str:
    """从文件加载提示词"""
    if name in _prompt_cache:
        return _prompt_cache[name]
    
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if prompt_file.exists():
        content = prompt_file.read_text(encoding="utf-8")
        _prompt_cache[name] = content
        return content
    return ""


def load_prompt_from_db(
    session,
    agent_type: str,
    test_type: str = "API",
    use_cache: bool = True
) -> Optional[str]:
    """
    从数据库加载提示词
    
    Args:
        session: 数据库会话
        agent_type: 智能体类型 (analyzer/designer/writer/reviewer/supervisor)
        test_type: 测试类型 (API/Web/App)
        use_cache: 是否使用缓存
    """
    if session is None:
        return None
    
    cache_key = f"db_{agent_type}_{test_type}"
    
    if use_cache and cache_key in _prompt_cache:
        return _prompt_cache[cache_key]
    
    try:
        from agent_langgraph.services.db_model_service import DatabaseModelService
        prompt = DatabaseModelService.get_prompt_template(session, agent_type, test_type)
        
        if prompt and use_cache:
            _prompt_cache[cache_key] = prompt
        
        return prompt
    except Exception as e:
        logger.warning(f"Failed to load prompt from database: {e}")
        return None


def load_prompt_with_fallback(
    session,
    agent_type: str,
    test_type: str = "API"
) -> str:
    """
    加载提示词，优先从数据库加载，失败则从文件加载
    
    Args:
        session: 数据库会话（可选）
        agent_type: 智能体类型
        test_type: 测试类型
    """
    # 优先从数据库加载
    if session:
        db_prompt = load_prompt_from_db(session, agent_type, test_type)
        if db_prompt:
            logger.debug(f"Loaded prompt for {agent_type} from database")
            return db_prompt
    
    # 回退到文件加载
    file_prompt = load_prompt(agent_type)
    if file_prompt:
        logger.debug(f"Loaded prompt for {agent_type} from file")
    return file_prompt


def clear_prompt_cache():
    """清除提示词缓存"""
    global _prompt_cache
    _prompt_cache = {}


__all__ = [
    "load_prompt",
    "load_prompt_from_db",
    "load_prompt_with_fallback",
    "clear_prompt_cache",
    "PROMPTS_DIR",
]
