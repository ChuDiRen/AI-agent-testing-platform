import os

from .globalContext import g_context
from ..parse.CaseParser import case_parser


class CasesPlugin:
    def pytest_addoption(self, parser):
        parser.addoption("--type", action="store", default="yaml", help="测试用例类型")
        parser.addoption("--cases", action="store", default="../examples", help="测试用例目录")

        default_key_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extend", "script")
        parser.addoption("--keyDir", action="store", default=default_key_dir, help="拓展关键字目录")

        parser.addoption("--platform", action="store", default="android", help="目标平台: android/ios")
        parser.addoption("--server", action="store", default="http://127.0.0.1:4723", help="Appium Server 地址")
        parser.addoption("--deviceName", action="store", default="", help="deviceName capability")
        parser.addoption("--udid", action="store", default="", help="udid capability")
        parser.addoption("--app", action="store", default="", help="Android apk 路径 / iOS ipa 路径")
        parser.addoption("--bundleId", action="store", default="", help="iOS bundleId")
        parser.addoption("--noReset", action="store", default="true", help="noReset capability")

    def pytest_generate_tests(self, metafunc):
        from pathlib import Path

        case_type = metafunc.config.getoption("type")
        cases_dir = metafunc.config.getoption("cases")
        key_dir = metafunc.config.getoption("keyDir")

        platform = metafunc.config.getoption("platform")
        server = metafunc.config.getoption("server")
        device_name = metafunc.config.getoption("deviceName")
        udid = metafunc.config.getoption("udid")
        app = metafunc.config.getoption("app")
        bundle_id = metafunc.config.getoption("bundleId")
        no_reset_str = metafunc.config.getoption("noReset")
        no_reset = str(no_reset_str).lower() in ["true", "1", "yes"]

        cases_path = Path(cases_dir).resolve()
        key_path = Path(key_dir) if key_dir else None

        g_context().set_dict("key_dir", str(key_path) if key_path else key_dir)

        g_context().set_dict("PLATFORM", platform)
        g_context().set_dict("APPIUM_SERVER", server)
        if device_name:
            g_context().set_dict("deviceName", device_name)
        if udid:
            g_context().set_dict("udid", udid)
        if app:
            g_context().set_dict("app", app)
        if bundle_id:
            g_context().set_dict("bundleId", bundle_id)
        g_context().set_dict("noReset", no_reset)

        data = case_parser(case_type, cases_path)

        if "caseinfo" in metafunc.fixturenames:
            metafunc.parametrize("caseinfo", data["case_infos"], ids=data["case_names"])

    def pytest_collection_modifyitems(self, items):
        for item in items:
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
