from typing import Dict, Any
import allure


def dynamicTitle(caseinfo: Dict[str, Any]) -> None:
    """
    动态设置 Allure 报告中的用例标题
    
    :param caseinfo: 用例数据字典
    """
    case_name = caseinfo.get("_case_name", caseinfo.get("desc", "未命名用例"))
    allure.dynamic.title(case_name)

