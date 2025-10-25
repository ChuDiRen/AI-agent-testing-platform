"""
脚本执行器
支持执行前置和后置脚本
"""
from typing import Any


def exec_script(script_code: str, context: dict[str, Any], caseinfo: dict[str, Any] | None = None) -> None:
    """
    执行 Python 脚本

    :param script_code: 脚本代码字符串
    :param context: 上下文字典
    :param caseinfo: 用例信息字典（可选）
    """
    try:
        # 导入 g_context 类，使其在脚本中可用
        from ...core.globalContext import g_context

        # 构建脚本执行的全局命名空间
        exec_globals = {
            'g_context': g_context,  # 注入 g_context 类
            'caseinfo': caseinfo if caseinfo is not None else {},  # 注入 caseinfo 变量
            '__builtins__': __builtins__,  # 保留内置函数
        }

        # 将 context 字典的内容也添加到全局命名空间
        exec_globals.update(context)

        # 执行脚本
        exec(script_code, exec_globals)
        print(f"脚本执行成功: {script_code}")
    except Exception as e:
        print(f"脚本执行失败: {script_code}")
        print(f"错误详情: {e}")
        raise e

