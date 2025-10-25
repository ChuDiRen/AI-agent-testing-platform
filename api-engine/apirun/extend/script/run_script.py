"""
脚本执行器
支持执行前置和后置脚本
"""
from typing import Any


def exec_script(script: str | None, context: dict[str, Any]) -> None:
    """
    执行 Python 脚本
    
    :param script: 脚本代码字符串
    :param context: 上下文字典
    """
    if script is None: return

    # script = "from apirunner.extend.functions import * \n" + script
    # print(script)
    exec(script, {"context": context})
    print(context)
