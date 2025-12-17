"""
Text2Case State Definition

多智能体协作的状态定义
"""
from typing import TypedDict, List, Optional, Dict, Any, Annotated
from operator import add


def merge_messages(left: List[Dict], right: List[Dict]) -> List[Dict]:
    """合并消息列表"""
    return left + right


class Text2CaseState(TypedDict, total=False):
    """
    多智能体协作状态
    
    包含所有智能体共享的状态信息
    """
    # 通用字段
    messages: Annotated[List[Dict[str, Any]], merge_messages]
    completed: bool
    error: Optional[str]
    
    # 输入
    requirement: str
    test_type: str
    
    # 智能体输出
    analysis: Optional[str]           # Analyzer输出
    test_points: Optional[str]        # Designer输出
    test_cases: Optional[str]         # Writer输出
    review_result: Optional[str]      # Reviewer输出
    review_feedback: Optional[str]    # 评审反馈（用于重写）
    
    # 质量控制
    quality_score: float
    iteration: int
    max_iterations: int
    
    # 协调控制
    next_agent: Optional[str]         # Supervisor决定的下一个智能体
    agent_history: List[str]          # 智能体执行历史


def create_initial_state(
    requirement: str = "",
    test_type: str = "API",
    max_iterations: int = 3
) -> Text2CaseState:
    """创建初始状态"""
    return Text2CaseState(
        messages=[],
        completed=False,
        error=None,
        requirement=requirement,
        test_type=test_type,
        analysis=None,
        test_points=None,
        test_cases=None,
        review_result=None,
        review_feedback=None,
        quality_score=0.0,
        iteration=0,
        max_iterations=max_iterations,
        next_agent=None,
        agent_history=[],
    )
