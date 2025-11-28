"""中间件配置"""
from dataclasses import dataclass
from enum import Enum


@dataclass
class FilterConfig:
    """消息过滤配置"""
    human: int = 3
    ai: int = 1
    tool: int = 0
    system: int = 0
    description: str = ""
    
    def __str__(self):
        return f"FilterConfig(H:{self.human}, A:{self.ai}, T:{self.tool}, S:{self.system})"


class TestCaseAgentFilterConfig:
    """智能体过滤策略"""
    ANALYZER = FilterConfig(human=1, ai=0, tool=0, system=0, description="需求分析")
    TEST_POINT_DESIGNER = FilterConfig(human=2, ai=1, tool=0, system=0, description="测试点设计")
    WRITER = FilterConfig(human=2, ai=2, tool=0, system=0, description="用例生成")
    REVIEWER = FilterConfig(human=3, ai=3, tool=0, system=0, description="用例评审")

    @classmethod
    def get_strategy(cls, agent_name: str) -> FilterConfig:
        strategy_map = {
            'analyzer': cls.ANALYZER,
            'test_point_designer': cls.TEST_POINT_DESIGNER,
            'writer': cls.WRITER,
            'reviewer': cls.REVIEWER,
        }
        return strategy_map.get(agent_name, FilterConfig())


class MessageFilterStrategy(Enum):
    """消息过滤策略枚举"""
    ANALYZER = TestCaseAgentFilterConfig.ANALYZER
    TEST_POINT_DESIGNER = TestCaseAgentFilterConfig.TEST_POINT_DESIGNER
    WRITER = TestCaseAgentFilterConfig.WRITER
    REVIEWER = TestCaseAgentFilterConfig.REVIEWER

