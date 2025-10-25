# -*- coding: utf-8 -*-

# 动态生成标题
from typing import Dict, Any, Callable

import allure

# 字段映射：字段名 -> Allure 动态方法
DYNAMIC_FIELDS: Dict[str, Callable] = {
    "_case_name": allure.dynamic.title,
    "storyName": allure.dynamic.story,
    "featureName": allure.dynamic.feature,
    "remark": allure.dynamic.description,
    "rank": allure.dynamic.severity,
}


def dynamicTitle(CaseData: Dict[str, Any]) -> None:
    """
    动态设置 Allure 报告的标题、模块、描述等信息
    
    :param CaseData: 用例数据字典
    """
    # 注意 这个caseinfo 是你参数化的数据给到的变量值。
    allure.dynamic.parameter("caseinfo", "")

    # 使用字典映射 + 海象运算符，避免多个 if 判断
    for field_name, setter_func in DYNAMIC_FIELDS.items():
        if (value := CaseData.get(field_name)) is not None:
            setter_func(value)
