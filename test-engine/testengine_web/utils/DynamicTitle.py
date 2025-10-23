import allure


def dynamicTitle(caseinfo):
    """
    动态设置 Allure 报告中的用例标题
    """
    case_name = caseinfo.get("_case_name", caseinfo.get("desc", "未命名用例"))
    allure.dynamic.title(case_name)

