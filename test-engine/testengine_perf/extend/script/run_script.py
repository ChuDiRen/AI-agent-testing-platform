"""
脚本执行器
支持执行 Python 脚本文件和代码片段
"""
import importlib.util
from pathlib import Path
from typing import Any, Optional


def exec_script(script: str | None, context: dict[str, Any]) -> Any:
    """
    执行 Python 代码片段
    
    :param script: 脚本代码字符串
    :param context: 上下文字典
    :return: 执行结果 (如果有 return 语句)
    """
    if script is None:
        return None
    
    # 创建执行环境
    exec_globals = {"context": context, "__builtins__": __builtins__}
    exec_locals = {}
    
    # 执行脚本
    exec(script, exec_globals, exec_locals)
    
    # 返回 result 变量 (如果存在)
    return exec_locals.get("result", exec_globals.get("result"))


def exec_script_file(
    script_path: str,
    context: dict[str, Any],
    caseinfo: Optional[dict] = None,
    function_name: Optional[str] = None,
    **kwargs
) -> Any:
    """
    执行 Python 脚本文件
    
    :param script_path: 脚本文件路径
    :param context: 上下文字典
    :param caseinfo: 用例信息 (可选)
    :param function_name: 要调用的函数名 (可选)
    :param kwargs: 传递给函数的额外参数
    :return: 执行结果
    """
    path = Path(script_path)
    
    if not path.exists():
        raise FileNotFoundError(f"脚本文件不存在: {script_path}")
    
    # 动态加载模块
    spec = importlib.util.spec_from_file_location("dynamic_script", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载脚本: {script_path}")
    
    module = importlib.util.module_from_spec(spec)
    
    # 注入上下文
    module.context = context
    module.caseinfo = caseinfo
    
    # 执行模块
    spec.loader.exec_module(module)
    
    # 如果指定了函数名，调用该函数
    if function_name:
        if not hasattr(module, function_name):
            raise AttributeError(f"脚本中未找到函数: {function_name}")
        
        func = getattr(module, function_name)
        return func(context=context, caseinfo=caseinfo, **kwargs)
    
    # 否则返回模块的 result 属性 (如果存在)
    return getattr(module, "result", None)
