import copy
import sys

import allure

from .globalContext import g_context
from ..extend.keywords import Keywords
from ..extend.script.run_script import exec_script
from ..utils.DynamicTitle import dynamicTitle
from ..utils.VarRender import refresh
from ..utils.AppiumManager import AppiumManager


def _safe_copy_context(context_dict):
    exclude_keys = ["current_driver"]
    safe_dict = {}
    for key, value in context_dict.items():
        if key not in exclude_keys:
            try:
                safe_dict[key] = copy.deepcopy(value)
            except (TypeError, AttributeError):
                safe_dict[key] = value
    return safe_dict


class MobileTestRunner:
    def execute(self, caseinfo):
        dynamicTitle(caseinfo)

        try:
            keywords = Keywords()
            local_context = caseinfo.get("context", {})
            context = _safe_copy_context(g_context().show_dict())
            context.update(local_context)

            pre_script = refresh(caseinfo.get("pre_script", None), context)
            if pre_script:
                for script in eval(pre_script):
                    exec_script(script, g_context().show_dict(), caseinfo)

            steps = caseinfo.get("steps", None)
            for step in steps:
                step_name = list(step.keys())[0]
                step_value = list(step.values())[0]

                context = _safe_copy_context(g_context().show_dict())
                context.update(local_context)
                step_value = eval(refresh(step_value, context))

                with allure.step(step_name):
                    key = step_value["关键字"]
                    try:
                        key_func = keywords.__getattribute__(key)
                    except AttributeError as e:
                        sys.path.append(g_context().get_dict("key_dir"))
                        module = __import__(key)
                        class_ = getattr(module, key)
                        key_func = class_().__getattribute__(key)

                    key_func(**step_value)

            context = _safe_copy_context(g_context().show_dict())
            context.update(local_context)
            post_script = refresh(caseinfo.get("post_script", None), context)
            if post_script:
                for script in eval(post_script):
                    exec_script(script, g_context().show_dict(), caseinfo)

        finally:
            AppiumManager.close()


def test_mobile_case(caseinfo):
    runner = MobileTestRunner()
    runner.execute(caseinfo)
