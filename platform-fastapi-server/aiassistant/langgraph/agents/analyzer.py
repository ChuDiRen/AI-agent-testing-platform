"""
AnalyzerAgent - 需求分析专家

深度解析需求文档，提取测试要素
"""
import logging
from ..state import TestCaseState, GenerationStage
from .base import BaseAgent

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """需求分析专家"""

    name = "analyzer"
    stage = GenerationStage.ANALYZING
    temperature = 0.3
    prompt_name = "analyzer"

    async def process(self, state: TestCaseState) -> TestCaseState:
        """分析需求"""
        self.emit_progress("正在分析需求文档...", 10.0)

        user_message = f"""
请分析以下需求，提取测试要素：

## 需求内容
{state.requirement}

## 测试类型
{state.test_type}

请按照系统提示的格式输出分析结果。
"""
        self.emit_progress("调用AI分析中...", 50.0)
        analysis = await self.invoke_llm(user_message)
        state.analysis = analysis
        self.emit_progress("需求分析完成", 100.0)
        logger.info(f"Analysis completed, length: {len(analysis)}")
        return state
