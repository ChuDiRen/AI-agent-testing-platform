# -*- coding: utf-8 -*-

# 动态生成标题
import allure

def dynamicTitle(CaseData):

    # 注意 这个caseinfo 是你参数化的数据给到的变量值。
    allure.dynamic.parameter("caseinfo", "")

    # 如果存在自定义标题
    if CaseData.get("_case_name", None) is not None:
        # 动态生成标题
        allure.dynamic.title(CaseData["_case_name"])

    if CaseData.get("storyName", None) is not None:
        # 动态获取story模块名
        allure.dynamic.story(CaseData["storyName"])

    if CaseData.get("featureName", None) is not None:
        # 动态获取feature模块名
        allure.dynamic.feature(CaseData["featureName"])

    if CaseData.get("remark", None) is not None:
        # 动态获取备注信息
        allure.dynamic.description(CaseData["remark"])

    if CaseData.get("rank", None) is not None:
        # 动态获取级别信息(blocker、critical、normal、minor、trivial)
        allure.dynamic.severity(CaseData["rank"])
