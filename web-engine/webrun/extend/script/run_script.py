"""
脚本执行器
支持执行前置和后置脚本，以及在步骤中执行 Python 脚本文件
"""
import os
import importlib.util
from typing import Any, Callable


def exec_script(script_code: str, context: dict[str, Any], caseinfo: dict[str, Any] | None = None) -> Any:
    """
    执行 Python 脚本代码
    
    :param script_code: 脚本代码字符串
    :param context: 上下文字典
    :param caseinfo: 用例信息字典（可选）
    :return: 脚本执行结果（如果有）
    """
    try:
        # 导入 g_context 类，使其在脚本中可用
        from ...core.globalContext import g_context

        # 构建脚本执行的全局命名空间
        exec_globals = {
            'g_context': g_context,  # 注入 g_context 类
            'context': context,  # 注入 context 字典
            'caseinfo': caseinfo if caseinfo is not None else {},  # 注入 caseinfo 变量
            '__builtins__': __builtins__,  # 保留内置函数
            '__result__': None,  # 用于存储返回值
        }

        # 将 context 字典的内容也添加到全局命名空间
        exec_globals.update(context)

        # 执行脚本
        exec(script_code, exec_globals)
        print(f"脚本执行成功: {script_code[:50]}...")
        return exec_globals.get('__result__')
    except Exception as e:
        print(f"脚本执行失败: {script_code[:50]}...")
        print(f"错误详情: {e}")
        raise e


def exec_script_file(script_path: str, context: dict[str, Any], 
                     caseinfo: dict[str, Any] | None = None,
                     function_name: str | None = None,
                     **kwargs) -> Any:
    """
    执行 Python 脚本文件
    
    :param script_path: 脚本文件路径（绝对路径或相对于用例目录的路径）
    :param context: 上下文字典
    :param caseinfo: 用例信息字典（可选）
    :param function_name: 要调用的函数名（可选，如果不指定则执行整个脚本）
    :param kwargs: 传递给函数的额外参数
    :return: 脚本/函数执行结果
    """
    try:
        # 导入 g_context 类
        from ...core.globalContext import g_context
        
        # 解析脚本路径
        if not os.path.isabs(script_path):
            # 如果是相对路径，尝试从用例目录查找
            cases_dir = g_context().get_dict("cases_dir")
            if cases_dir:
                script_path = os.path.join(cases_dir, script_path)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        # 动态加载模块
        module_name = os.path.splitext(os.path.basename(script_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        
        # 注入上下文到模块
        module.g_context = g_context
        module.context = context
        module.caseinfo = caseinfo if caseinfo is not None else {}
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 如果指定了函数名，调用该函数
        if function_name:
            if not hasattr(module, function_name):
                raise AttributeError(f"脚本中未找到函数: {function_name}")
            
            func: Callable = getattr(module, function_name)
            # 合并上下文和额外参数
            call_kwargs = {**context, **kwargs}
            result = func(**call_kwargs)
            print(f"函数执行成功: {function_name}")
            return result
        
        print(f"脚本文件执行成功: {script_path}")
        return None
        
    except Exception as e:
        print(f"脚本文件执行失败: {script_path}")
        print(f"错误详情: {e}")
        raise e


def load_custom_keywords(script_path: str) -> type:
    """
    从脚本文件加载自定义关键字类
    
    :param script_path: 脚本文件路径
    :return: 关键字类
    """
    try:
        from ...core.globalContext import g_context
        
        # 解析脚本路径
        if not os.path.isabs(script_path):
            key_dir = g_context().get_dict("key_dir")
            if key_dir:
                script_path = os.path.join(key_dir, script_path)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"关键字脚本不存在: {script_path}")
        
        # 动态加载模块
        module_name = os.path.splitext(os.path.basename(script_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        
        # 注入 g_context
        module.g_context = g_context
        
        spec.loader.exec_module(module)
        
        # 查找关键字类（与模块同名的类）
        if hasattr(module, module_name):
            return getattr(module, module_name)
        
        # 或者查找 Keywords 类
        if hasattr(module, 'Keywords'):
            return getattr(module, 'Keywords')
        
        raise AttributeError(f"脚本中未找到关键字类: {module_name} 或 Keywords")
        
    except Exception as e:
        print(f"加载自定义关键字失败: {script_path}")
        print(f"错误详情: {e}")
        raise e

