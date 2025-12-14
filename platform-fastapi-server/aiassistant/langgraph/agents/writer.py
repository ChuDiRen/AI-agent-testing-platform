"""
WriterAgent - 用例编写专家

生成结构化测试用例（JSON格式）
"""
import json
import logging
import re
from ..state import TestCaseState, GenerationStage
from .base import BaseAgent

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """用例编写专家"""

    name = "writer"
    stage = GenerationStage.WRITING
    temperature = 0.7
    prompt_name = "writer"

    async def process(self, state: TestCaseState) -> TestCaseState:
        """编写测试用例"""
        self.emit_progress("正在编写测试用例...", 10.0)

        user_message = f"""
请基于以下测试点设计，编写详细的测试用例：

## 原始需求
{state.requirement}

## 需求分析
{state.analysis}

## 测试点设计
{state.test_points}

## 测试类型
{state.test_type}

请严格按照JSON格式输出测试用例，确保可以被程序解析。
"""
        self.emit_progress("调用AI编写中...", 50.0)
        response = await self.invoke_llm(user_message)
        # 提取JSON部分
        testcases = self._extract_json(response)
        state.testcases = testcases
        self.emit_progress("测试用例编写完成", 100.0)
        logger.info(f"Test cases written, length: {len(testcases)}")
        return state

    def _extract_json(self, text: str) -> str:
        """从响应中提取JSON"""
        # 尝试提取```json...```块
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if json_match:
            return json_match.group(1).strip()
        # 尝试提取{...}块
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            return brace_match.group(0)
        return text
