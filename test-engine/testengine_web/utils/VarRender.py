# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
from typing import Any, Dict, Optional
from jinja2 import Template


def refresh(target: Any, context: Dict[str, Any]) -> Optional[str]:
    """
    使用 Jinja2 模板引擎渲染字符串
    
    :param target: 待渲染的目标对象
    :param context: 上下文变量字典
    :return: 渲染后的字符串，如果 target 为 None 则返回 None
    """
    return None if target is None else Template(str(target)).render(context)


def test_refresh():
    # 单元测试用例 - 检查refresh是否有效
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
    print(result)

