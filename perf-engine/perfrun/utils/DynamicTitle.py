# -*- coding: utf-8 -*-

"""
动态生成标题 - Locust 版本
适用于性能测试场景，用于动态设置任务名称和元信息
"""
from typing import Any, Optional


def dynamicTitle(CaseData: dict[str, Any]) -> str:
    """
    动态生成 Locust 任务名称
    
    :param CaseData: 用例数据字典，包含用例的各种元信息
    :return: 格式化的任务名称
    """
    # 基础名称
    task_name = CaseData.get("_case_name", CaseData.get("desc", "UnnamedTask"))
    
    # 构建完整的任务描述
    parts = [task_name]
    
    # 添加 feature 信息
    if feature_name := CaseData.get("featureName"):
        parts.insert(0, f"[{feature_name}]")
    
    # 添加 story 信息
    if story_name := CaseData.get("storyName"):
        parts.insert(1 if "featureName" in CaseData else 0, f"[{story_name}]")
    
    return " ".join(parts)


def get_task_metadata(CaseData: dict[str, Any]) -> dict[str, Any]:
    """
    提取用例元数据，用于性能测试报告
    
    :param CaseData: 用例数据字典
    :return: 元数据字典
    """
    metadata = {
        "name": CaseData.get("_case_name", CaseData.get("desc", "Unknown")),
        "feature": CaseData.get("featureName"),
        "story": CaseData.get("storyName"),
        "rank": CaseData.get("rank"),
        "remark": CaseData.get("remark"),
    }
    
    # 过滤掉 None 值
    return {k: v for k, v in metadata.items() if v is not None}

