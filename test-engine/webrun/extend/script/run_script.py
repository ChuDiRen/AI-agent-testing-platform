"""
脚本执行器
支持执行前置和后置脚本
"""


def exec_script(script_code, context):
    """
    执行 Python 脚本
    
    :param script_code: 脚本代码字符串
    :param context: 上下文字典
    """
    try:
        exec(script_code, context)
        print(f"脚本执行成功: {script_code}")
    except Exception as e:
        print(f"脚本执行失败: {script_code}")
        raise e

