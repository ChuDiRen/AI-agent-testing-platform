from typing import Any

import allure


def dynamicTitle(CaseData: dict[str, Any]) -> None:
    allure.dynamic.parameter("caseinfo", "")

    if case_name := CaseData.get("_case_name"):
        allure.dynamic.title(case_name)

    if story_name := CaseData.get("storyName"):
        allure.dynamic.story(story_name)

    if feature_name := CaseData.get("featureName"):
        allure.dynamic.feature(feature_name)

    if remark := CaseData.get("remark"):
        allure.dynamic.description(remark)

    if rank := CaseData.get("rank"):
        allure.dynamic.severity(rank)
