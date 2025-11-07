"""中间件配置 - 过滤策略定义"""
from dataclasses import dataclass
from enum import Enum


@dataclass
class FilterConfig:
    """消息过滤配置
    
    定义每种消息类型保留的数量
    """
    human: int = 3  # 保留最新的 N 条 HumanMessage
    ai: int = 1     # 保留最新的 N 条 AIMessage
    tool: int = 0   # 保留最新的 N 条 ToolMessage
    system: int = 0 # 保留最新的 N 条 SystemMessage
    description: str = ""  # 策略描述
    
    def __str__(self):
        return f"FilterConfig(H:{self.human}, A:{self.ai}, T:{self.tool}, S:{self.system})"


class TestCaseAgentFilterConfig:
    """测试用例生成智能体的过滤策略配置 (4个专家智能体)"""

    # 需求分析智能体: 只需要原始需求
    ANALYZER = FilterConfig(
        human=1, ai=0, tool=0, system=0,
        description="需求分析策略: 只需要当前需求"
    )

    # 测试点设计智能体: 需要需求+分析结果
    TEST_POINT_DESIGNER = FilterConfig(
        human=2, ai=1, tool=0, system=0,
        description="测试点设计策略: 需要需求和分析结果"
    )

    # 用例编写智能体: 需要需求+测试点
    WRITER = FilterConfig(
        human=2, ai=2, tool=0, system=0,
        description="用例生成策略: 需要需求和测试点"
    )

    # 审查智能体: 需要完整上下文
    REVIEWER = FilterConfig(
        human=3, ai=3, tool=0, system=0,
        description="审查策略: 保留完整上下文用于评审"
    )

    @classmethod
    def get_strategy(cls, agent_name: str) -> FilterConfig:
        """根据智能体名称获取策略"""
        strategy_map = {
            'analyzer': cls.ANALYZER,
            'test_point_designer': cls.TEST_POINT_DESIGNER,
            'writer': cls.WRITER,
            'reviewer': cls.REVIEWER,
        }
        return strategy_map.get(agent_name, FilterConfig())


class MessageFilterStrategy(Enum):
    """消息过滤策略枚举 (用于工厂方法)"""
    ANALYZER = TestCaseAgentFilterConfig.ANALYZER
    TEST_POINT_DESIGNER = TestCaseAgentFilterConfig.TEST_POINT_DESIGNER
    WRITER = TestCaseAgentFilterConfig.WRITER
    REVIEWER = TestCaseAgentFilterConfig.REVIEWER

