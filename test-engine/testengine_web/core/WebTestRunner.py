import copy
import sys
import allure

from ..extend.keywords import Keywords  # 相对导入: webrun内部模块
from ..extend.script import run_script  # 相对导入: webrun内部模块
from .globalContext import g_context  # 相对导入: 同级模块
from ..utils.VarRender import refresh  # 相对导入: webrun内部模块
from ..utils.DynamicTitle import dynamicTitle  # 相对导入: webrun内部模块


class TestRunner:
    """Web 测试用例执行器"""
    
    def test_case_execute(self, caseinfo):
        # allure 用例标题title
        dynamicTitle(caseinfo)
        
        try:
            keywords = Keywords()
            # 单用例范围内的变量数据
            local_context = caseinfo.get("context", {})
            # 获取全局上下文，但排除不可序列化的对象（如 Playwright 页面对象）
            global_context = g_context().show_dict()
            context = {}
            for key, value in global_context.items():
                # 跳过 Playwright 相关的对象，这些对象不能被深拷贝
                if key in ["current_page", "current_browser", "current_context"]:
                    continue
                try:
                    context[key] = copy.deepcopy(value)
                except (TypeError, AttributeError):
                    # 如果无法深拷贝，则直接引用
                    context[key] = value
            context.update(local_context)
            
            # 执行前置脚本
            pre_script = refresh(caseinfo.get("pre_script", None), context)
            if pre_script:
                for script in eval(pre_script):
                    run_script.exec_script(script, g_context().show_dict())
            
            # 准备执行用例 - 刷新用例内变量
            steps = caseinfo.get("steps", None)
            for step in steps:
                step_name = list(step.keys())[0]
                step_value = list(step.values())[0]
                # 刷新步骤内容的变量值
                global_context = g_context().show_dict()
                context = {}
                for key, value in global_context.items():
                    # 跳过 Playwright 相关的对象
                    if key in ["current_page", "current_browser", "current_context"]:
                        continue
                    try:
                        context[key] = copy.deepcopy(value)
                    except (TypeError, AttributeError):
                        context[key] = value
                context.update(local_context)
                step_value = eval(refresh(step_value, context))  # 全局变量+用例变量渲染
                print(f"开始执行步骤：{step_name} - {step_value}")
                with allure.step(step_name):
                    key = step_value["关键字"]
                    try:
                        key_func = keywords.__getattribute__(key)
                    except AttributeError as e:
                        print("没有这个关键字，动态加载：", e)
                        sys.path.append(g_context().get_dict("key_dir"))
                        module = __import__(key)  # 动态引入模块
                        class_ = getattr(module, key)
                        key_func = class_().__getattribute__(key)
                        print("动态加载的函数", key_func)
                    
                    key_func(**step_value)  # 调用关键字方法
            
            # 后置脚本执行
            context = copy.deepcopy(g_context().show_dict())
            context.update(local_context)
            post_script = refresh(caseinfo.get("post_script", None), context)
            
            if post_script:
                for script in eval(post_script):
                    run_script.exec_script(script, g_context().show_dict())
        
        finally:
            print("========执行完毕========")
            # 确保测试结束时关闭浏览器
            driver = g_context().get_dict("current_driver")
            if driver:
                try:
                    driver.quit()
                    g_context().set_dict("current_driver", None)
                    print("浏览器已自动关闭")
                except Exception as e:
                    print(f"关闭浏览器失败: {e}")

