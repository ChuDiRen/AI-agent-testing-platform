"""
变量渲染 - 复用公共模块
"""
from testengine_common.var_render import refresh, refresh_simple

__all__ = ["refresh", "refresh_simple"]


def test_refresh():
    """单元测试用例"""
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
    print(result)


