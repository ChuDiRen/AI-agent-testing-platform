"""
TestPointDesignerAgent - 测试点设计专家

设计正常/异常/边界测试点
"""
import logging
from ..state import TestCaseState, GenerationStage
from .base import BaseAgent

logger = logging.getLogger(__name__)


class TestPointDesignerAgent(BaseAgent):
    """测试点设计专家"""

    name = "designer"
    stage = GenerationStage.DESIGNING
    temperature = 0.5
    prompt_name = "designer"

    async def process(self, state: TestCaseState) -> TestCaseState:
        """设计测试点"""
        self.emit_progress("正在设计测试点...", 10.0)

        user_message = f"""
请基于以下需求分析结果，设计完整的测试点覆盖方案：

## 原始需求
{state.requirement}

## 需求分析结果
{state.analysis}

## 测试类型
{state.test_type}

请按照系统提示的格式输出测试点设计。
"""
        self.emit_progress("调用AI设计中...", 50.0)
        test_points = await self.invoke_llm(user_message)
        state.test_points = test_points
        self.emit_progress("测试点设计完成", 100.0)
        logger.info(f"Test points designed, length: {len(test_points)}")
        return state
