# -*- coding: utf-8 -*-

# 动态生成标题
from typing import Any

import allure


def dynamicTitle(CaseData: dict[str, Any]) -> None:
    """
    动态设置 Allure 报告的用例信息
    
    :param CaseData: 用例数据字典，包含用例的各种元信息
    """
    # 注意 这个caseinfo 是你参数化的数据给到的变量值。
    allure.dynamic.parameter("caseinfo", "")

    # 使用海象操作符优化条件判断
    if case_name := CaseData.get("_case_name"):
        # 动态生成标题
        allure.dynamic.title(case_name)

    if story_name := CaseData.get("storyName"):
        # 动态获取story模块名
        allure.dynamic.story(story_name)

    if feature_name := CaseData.get("featureName"):
        # 动态获取feature模块名
        allure.dynamic.feature(feature_name)

    if remark := CaseData.get("remark"):
        # 动态获取备注信息
        allure.dynamic.description(remark)

    if rank := CaseData.get("rank"):
        # 动态获取级别信息(blocker、critical、normal、minor、trivial)
        allure.dynamic.severity(rank)

