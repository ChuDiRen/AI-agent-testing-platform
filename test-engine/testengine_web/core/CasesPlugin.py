from typing import List
import pytest

from ..parse.CaseParser import case_parser  # 相对导入: webrun内部模块
from .globalContext import g_context  # 相对导入: 同级模块


class CasesPlugin:
    """
    pytest 插件 - 用于 pytest 运行时的用例配置信息加载
    
    应用了 pytest 钩子函数:
    - pytest_addoption: 添加命令行选项
    - pytest_generate_tests: 动态生成参数化测试
    - pytest_collection_modifyitems: 修改收集到的测试项
    """
    
    def pytest_addoption(self, parser: pytest.Parser) -> None:
        """
        增加 pytest 运行的配置项
        
        :param parser: pytest 参数解析器
        """
        parser.addoption(
            "--type", action="store", default="yaml", help="测试用例类型 (yaml)"
        )
        parser.addoption(
            "--cases", action="store", default="../examples", help="测试用例目录路径"
        )
        # 添加一个指定的关键字目录
        parser.addoption(
            "--keyDir", action="store", default="", help="扩展关键字目录路径"
        )
        # Web 特有配置
        parser.addoption(
            "--browser", action="store", default="chrome", help="浏览器类型: chrome/firefox/edge"
        )
        parser.addoption(
            "--headless", action="store", default="false", help="是否无头模式: true/false"
        )
    
    def pytest_generate_tests(self, metafunc: pytest.Metafunc) -> None:
        """
        动态生成参数化测试
        
        :param metafunc: pytest 方法元数据
        """
        # 读取用户传过来的参数
        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        key_dir = metafunc.config.getoption("keyDir")
        browser = metafunc.config.getoption("browser")
        headless = metafunc.config.getoption("headless")

        # 把 key_dir 放入到全局上下文
        if key_dir:
            g_context().set_dict("key_dir", key_dir)

        # 读取测试用例，同时需要进行参数化（此时会加载 context.yaml）
        data = case_parser(case_type, cases_dir)

        # 命令行参数覆盖 context.yaml 中的配置（优先级：命令行 > 配置文件）
        if browser:
            g_context().set_dict("BROWSER", browser)  # 覆盖 context.yaml 中的 BROWSER
        if headless:
            g_context().set_dict("HEADLESS", headless)  # 覆盖 context.yaml 中的 HEADLESS

        # 把测试用例作为参数化，交给 runner 执行
        if "caseinfo" in metafunc.fixturenames:
            metafunc.parametrize("caseinfo", data['case_infos'], ids=data['case_names'])
    
    def pytest_collection_modifyitems(self, items: List[pytest.Item]) -> None:
        """
        用例收集完毕之后被调用
        
        用于调整测试用例执行顺序，同时解决测试用例标题的中文显示问题
        
        :param items: 收集到的测试项列表
        """
        for item in items:
            # 解决中文显示问题
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

