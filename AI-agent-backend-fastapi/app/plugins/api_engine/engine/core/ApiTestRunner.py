import copy
import sys, allure

from ..extend.keywords import Keywords  # 修改为相对导入
from ..extend.script import run_script  # 修改为相对导入
from .globalContext import g_context  # 修改为相对导入
from ..utils.VarRender import refresh  # 修改为相对导入
# TODO 扩展-多文件执行：
from ..utils.DynamicTitle import dynamicTitle  # 动态标题,修改为相对导入

class TestRunner:
    def test_case_execute(self, caseinfo):
        # allure 用例标题title，可按需拓展模块等...
        dynamicTitle(caseinfo)

        try:
            keywords = Keywords()
            # 单用例范围内的 变量数据
            local_context = caseinfo.get("context", {})
            context = copy.deepcopy(g_context().show_dict())
            context.update(local_context)

            # 执行前置用例
            pre_script = refresh(caseinfo.get("pre_script", None), context) # 全局变量+用例变量渲染
            if pre_script:
                for script in eval(pre_script):
                    run_script.exec_script(script, g_context().show_dict())

            # 准备执行用例 - 刷新用例内变量
            steps = caseinfo.get("steps", None)
            for step in steps:
                step_name = list(step.keys())[0]
                step_value = list(step.values())[0]
                # 刷新步骤内容的变量值
                context = copy.deepcopy(g_context().show_dict())
                context.update(local_context)
                step_value = eval(refresh(step_value, context)) # 全局变量+用例变量渲染
                print(f"开始执行步骤：{step_name} - {step_value}")
                with allure.step(step_name):
                    key = step_value["关键字"]
                    try:
                        key_func = keywords.__getattribute__(key)
                    except AttributeError as e:
                        print("没有这个关键字，动态加载：", e)
                        sys.path.append(g_context().get_dict("key_dir"))
                        module = __import__(key)  # 动态引入模块(temp.py文件)
                        class_ = getattr(module, key)
                        key_func = class_().__getattribute__(key)
                        print("动态加载的函数", key_func)

                    key_func(**step_value)  # 调用关键字方法
                    # 执行后置脚本
            # 后置脚本执行
            context = copy.deepcopy(g_context().show_dict())
            context.update(local_context)
            post_script = refresh(caseinfo.get("post_script", None), context) # 全局变量+用例变量渲染

            if post_script:
                for script in eval(post_script):
                    run_script.exec_script(script, g_context().show_dict())
        # except  Exception as e: # 要抛出异常不然平台都不知道出现什么错误信息
        #     print("-----------engine_error------------")
        #     print(e)
        #     print("----------end engine_error-------------")
        #     raise e
        finally:
            print("========执行完毕========")
            # if driver is not None:
            #     driver.quit()
