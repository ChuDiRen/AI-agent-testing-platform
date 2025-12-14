"""
TestCaseState - 智能体间传递的状态对象

定义LangGraph状态机中流转的状态数据结构
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class GenerationStage(str, Enum):
    """生成阶段枚举"""
    INIT = "init"
    ANALYZING = "analyzing"
    DESIGNING = "designing"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TestCaseState:
    """测试用例生成状态"""
    requirement: str  # 原始需求
    test_type: str = "API"  # 测试类型: API/Web/App
    analysis: Optional[str] = None  # 需求分析结果
    test_points: Optional[str] = None  # 测试点设计
    testcases: Optional[str] = None  # 生成的测试用例JSON
    review: Optional[str] = None  # 评审结果
    quality_score: float = 0.0  # 质量评分 0-100
    iteration: int = 0  # 当前迭代次数
    max_iterations: int = 3  # 最大迭代次数
    completed: bool = False  # 是否完成
    error: Optional[str] = None  # 错误信息
    stage: GenerationStage = GenerationStage.INIT  # 当前阶段
    start_time: Optional[datetime] = None  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间
    token_usage: Dict[str, int] = field(default_factory=dict)  # Token使用统计
    messages: List[Dict[str, Any]] = field(default_factory=list)  # 消息历史


    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "requirement": self.requirement,
            "test_type": self.test_type,
            "analysis": self.analysis,
            "test_points": self.test_points,
            "testcases": self.testcases,
            "review": self.review,
            "quality_score": self.quality_score,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "completed": self.completed,
            "error": self.error,
            "stage": self.stage.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "token_usage": self.token_usage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCaseState":
        """从字典创建"""
        stage = data.get("stage", "init")
        if isinstance(stage, str):
            stage = GenerationStage(stage)
        return cls(
            requirement=data["requirement"],
            test_type=data.get("test_type", "API"),
            analysis=data.get("analysis"),
            test_points=data.get("test_points"),
            testcases=data.get("testcases"),
            review=data.get("review"),
            quality_score=data.get("quality_score", 0.0),
            iteration=data.get("iteration", 0),
            max_iterations=data.get("max_iterations", 3),
            completed=data.get("completed", False),
            error=data.get("error"),
            stage=stage,
            token_usage=data.get("token_usage", {}),
            messages=data.get("messages", []),
        )

    def should_retry(self) -> bool:
        """是否应该重试"""
        return (
            not self.completed
            and self.quality_score < 80
            and self.iteration < self.max_iterations
            and self.error is None
        )

    def get_duration_seconds(self) -> float:
        """获取执行时长(秒)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def get_total_tokens(self) -> int:
        """获取总Token消耗"""
        return sum(self.token_usage.values())
