"""
技能模块
包含所有专业技能的注册和管理
"""

from .sales_analytics import get_sales_analytics_skill
from .inventory_management import get_inventory_management_skill
from typing import TypedDict, List

class Skill(TypedDict):
    """技能定义：可通过 progressive disclosure 逐步披露给 agent 的技能"""
    name: str
    description: str
    content: str

def get_all_skills() -> List[Skill]:
    """获取所有可用技能"""
    skills = [
        get_sales_analytics_skill(),
        get_inventory_management_skill(),
    ]
    return skills

def get_skill_by_name(skill_name: str) -> Skill | None:
    """根据名称获取技能"""
    all_skills = get_all_skills()
    for skill in all_skills:
        if skill["name"] == skill_name:
            return skill
    return None

def get_available_skills() -> List[str]:
    """获取所有可用技能名称"""
    all_skills = get_all_skills()
    return [skill["name"] for skill in all_skills]
