# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
import os
from typing import Any

from jinja2 import Environment


def _resolve_file_path(file_path: str, cases_dir: str = None) -> str:
    """
    解析文件路径，支持相对路径转绝对路径
    
    :param file_path: 文件路径（可以是相对路径或绝对路径）
    :param cases_dir: 用例目录路径
    :return: 解析后的绝对路径
    """
    if not file_path:
        return file_path
    
    # 如果已经是绝对路径或 URL，直接返回
    if os.path.isabs(file_path) or file_path.startswith(('http://', 'https://')):
        return file_path
    
    # 尝试相对于用例目录解析
    if cases_dir:
        candidate = os.path.join(cases_dir, file_path)
        if os.path.exists(candidate):
            return candidate
    
    return file_path


def _create_jinja_env(context: dict[str, Any]) -> Environment:
    """
    创建带有自定义过滤器的 Jinja2 环境
    """
    env = Environment()
    
    # 获取用例目录
    cases_dir = context.get('_cases_dir', '')
    
    # 添加文件路径解析过滤器
    env.filters['file'] = lambda path: _resolve_file_path(path, cases_dir)
    env.filters['filepath'] = lambda path: _resolve_file_path(path, cases_dir)
    
    return env


def refresh(target: Any | None, context: dict[str, Any]) -> str | None:
    """
    使用 Jinja2 模板引擎渲染字符串
    
    :param target: 待渲染的目标字符串或对象
    :param context: 渲染上下文字典
    :return: 渲染后的字符串，如果 target 为 None 则返回 None
    """
    if target is None: return None
    
    env = _create_jinja_env(context)
    template = env.from_string(str(target))
    return template.render(context)


def test_refresh() -> None:
    """单元测试用例 - 检查refresh是否有效"""
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
    print(result)
