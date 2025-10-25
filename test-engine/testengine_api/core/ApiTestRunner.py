import copy
import inspect
import sys

import allure

from .globalContext import g_context
from ..extend.keywords import Keywords
from ..extend.script import run_script
from ..utils.DynamicTitle import dynamicTitle
from ..utils.VarRender import refresh


class TestRunner:
    async def test_case_execute(self, caseinfo): # 改为异步方法
        """异步测试用例执行器"""
        dynamicTitle(caseinfo)

        try:
            keywords = Keywords()
            local_context = caseinfo.get("context", {})
            context = copy.deepcopy(g_context().show_dict())
            context.update(local_context)

            # 执行前置脚本
            pre_script = refresh(caseinfo.get("pre_script", None), context)
            if pre_script:
                for script in eval(pre_script):
                    run_script.exec_script(script, g_context().show_dict())

            # 执行测试步骤
            steps = caseinfo.get("steps", None)
            for step in steps:
                step_name = list(step.keys())[0]
                step_value = list(step.values())[0]
                context = copy.deepcopy(g_context().show_dict())
                context.update(local_context)
                step_value = eval(refresh(step_value, context))
                print(f"开始执行步骤: {step_name} - {step_value}")

                with allure.step(step_name):
                    key = step_value["关键字"]
                    try:
                        key_func = keywords.__getattribute__(key)
                    except AttributeError as e:
                        print("没有这个关键字,动态加载:", e)
                        sys.path.append(g_context().get_dict("key_dir"))
                        module = __import__(key)
                        class_ = getattr(module, key)
                        key_func = class_().__getattribute__(key)
                        print("动态加载的函数", key_func)

                    # 调用关键字方法,自动判断是否为异步
                    result = key_func(**step_value)
                    if inspect.iscoroutine(result): # 检查返回值是否为协程对象
                        await result # 异步调用
                    # 同步方法直接返回结果,无需额外处理

            # 执行后置脚本
            context = copy.deepcopy(g_context().show_dict())
            context.update(local_context)
            post_script = refresh(caseinfo.get("post_script", None), context)
            if post_script:
                for script in eval(post_script):
                    run_script.exec_script(script, g_context().show_dict())

        finally:
            print("========执行完毕========")
            # if driver is not None:
            #     driver.quit()
