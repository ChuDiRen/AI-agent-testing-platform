"""
ReviewerAgent - 用例评审专家

多维度质量评审（0-100分）
"""
import json
import logging
import re
from ..state import TestCaseState, GenerationStage
from .base import BaseAgent

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """用例评审专家"""

    name = "reviewer"
    stage = GenerationStage.REVIEWING
    temperature = 0.1
    prompt_name = "reviewer"

    async def process(self, state: TestCaseState) -> TestCaseState:
        """评审测试用例"""
        self.emit_progress("正在评审测试用例...", 10.0)

        user_message = f"""
请评审以下测试用例的质量：

## 原始需求
{state.requirement}

## 测试点设计
{state.test_points}

## 测试用例
{state.testcases}

请按照系统提示的JSON格式输出评审结果，包含质量评分(0-100)。
"""
        self.emit_progress("调用AI评审中...", 50.0)
        response = await self.invoke_llm(user_message)
        state.review = response
        # 解析评分
        state.quality_score = self._extract_score(response)
        # 判断是否通过
        if state.quality_score >= 80:
            state.completed = True
            state.stage = GenerationStage.COMPLETED
        else:
            state.iteration += 1
        self.emit_progress(f"评审完成，得分: {state.quality_score}", 100.0)
        logger.info(f"Review completed, score: {state.quality_score}")
        return state

    def _extract_score(self, text: str) -> float:
        """从评审结果中提取评分"""
        # 尝试解析JSON
        try:
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
            if json_match:
                data = json.loads(json_match.group(1))
                return float(data.get("quality_score", 0))
            brace_match = re.search(r"\{[\s\S]*\}", text)
            if brace_match:
                data = json.loads(brace_match.group(0))
                return float(data.get("quality_score", 0))
        except (json.JSONDecodeError, ValueError):
            pass
        # 尝试正则匹配数字
        score_match = re.search(r"(?:score|评分|得分)[:\s]*(\d+(?:\.\d+)?)", text, re.I)
        if score_match:
            return float(score_match.group(1))
        return 0.0
