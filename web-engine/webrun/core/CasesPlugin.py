import os

from .globalContext import g_context
from ..parse.CaseParser import case_parser


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
        # 添加一个指定的关键字目录（默认指向包内 extend/script 路径）
        default_key_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'extend', 'script')
        parser.addoption(
            "--keyDir", action="store", default=default_key_dir, help="拓展关键字目录"
        )
        # Web 特有配置
        parser.addoption(
            "--browser", action="store", default="chrome", help="浏览器类型: chrome/firefox/edge"
        )
        parser.addoption(
            "--headless", action="store", default="false", help="是否无头模式: true/false"
        )
    
    def pytest_generate_tests(self, metafunc):
        """
        method_meta: 运行的方法信息
        """
        from pathlib import Path
        
        # 读取用户传过来的参数
        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        key_dir = metafunc.config.getoption("keyDir")
        browser = metafunc.config.getoption("browser")
        headless_str = metafunc.config.getoption("headless")

        # 立即转换为 Path 对象 - 不允许兼容代码
        cases_path = Path(cases_dir).resolve()
        key_path = Path(key_dir) if key_dir else None

        # 将字符串 "true"/"false" 转换为布尔值
        headless = headless_str.lower() in ["true", "1", "yes"]

        # 把这个key_dir 放入到公共变量去
        g_context().set_dict("key_dir", str(key_path) if key_path else key_dir)
        # Web特有: 把浏览器配置放入到公共变量
        g_context().set_dict("_browser", browser)
        g_context().set_dict("_headless", headless)

        # 读取测试用例 - 传递 Path 对象
        data = case_parser(case_type, cases_path)

        # 命令行参数覆盖 context.yaml 中的配置（优先级：命令行 > context.yaml）
        g_context().set_dict("BROWSER", browser)
        g_context().set_dict("HEADLESS", headless)

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

