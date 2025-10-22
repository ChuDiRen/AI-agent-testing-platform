import pytest

from apirun.parse.CaseParser import case_parser
from apirun.core.globalContext import g_context


class CasesPlugin:
    """
    pytest插件 - 用于pytest运行时的用例配置信息加载
    应用了 pytest 钩子函数
    """

    def pytest_addoption(self, parser):

        """
        增加pytest运行的配置项
        """
        parser.addoption(
            "--type", action="store", default="yaml", help="测试用例类型"
        )
        parser.addoption(
            "--cases", action="store", default="../examples", help="测试用例目录"
        )
        # 添加一个指定的关键字目录
        parser.addoption(
            "--keyDir", action="store", default="F:\\key_py", help="拓展关键字目录"
        )

    def pytest_generate_tests(self, metafunc):
        """
        method_meta: 运行的方法信息
        """
        # 读取用户传过来的参数
        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        key_dir = metafunc.config.getoption("keyDir")

        # 把这个key_dir 放入到公共变量去
        g_context().set_dict("key_dir", key_dir)

        # 读取测试用例,同时需要进行参数化
        data = case_parser(case_type, cases_dir)

        # 把测试用例作为参数化，交给 runner 执行
        if "caseinfo" in metafunc.fixturenames:
            metafunc.parametrize("caseinfo", data['case_infos'], ids=data['case_names'])

    # def pytest_collection_modifyitems(self, items):
    #     """
    #     用例收集完毕之后被调用，可以用来调整测试用例执行顺序；
    #     """
    #     for item in items:
    #         item.name = item.name.encode("utf-8").decode("unicode_escape")
    #         item._nodeid = item.callspec.id

    def pytest_collection_modifyitems(self, items):
        """
        用例收集完毕之后被调用，可以用来调整测试用例执行顺序；同时可以解决测试用例标题的显示问题
        """
        for item in items:
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

