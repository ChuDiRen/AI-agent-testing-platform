# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
from jinja2 import Template


def refresh(target, context):
    if target is None: return None
    return Template(str(target)).render(context)


def test_refresh():
    # 单元测试用例 - 检查refresh是否有效
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
    print(result)
