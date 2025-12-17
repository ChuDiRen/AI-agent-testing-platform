"""
ReviewerAgent - 用例评审专家

多维度质量评审，提供改进建议
"""
import json
import re
import logging
from typing import Dict, Any

from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse, AgentRole

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """用例评审专家"""
    
    name = "reviewer"
    role = AgentRole.REVIEWER
    description = "用例评审专家，负责多维度评审测试用例质量，提供改进建议"
    temperature = 0.1
    prompt_name = "reviewer"  # 从prompts/reviewer.txt加载
    
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """评审测试用例"""
        logger.info(f"[{self.name}] Starting test case review...")
        
        requirement = state.get("requirement", "")
        test_points = state.get("test_points", "")
        test_cases = state.get("test_cases", "")
        
        if not test_cases:
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error="测试用例为空，请先编写测试用例"
            )
        
        user_message = f"""请评审以下测试用例的质量：

## 原始需求
{requirement}

## 测试点设计
{test_points}

## 测试用例
{test_cases}

请按照系统提示的JSON格式输出评审结果，包含质量评分(0-100)和具体改进建议。
"""
        
        try:
            response = await self.invoke_llm(user_message)
            review_result = self._parse_review(response)
            
            logger.info(f"[{self.name}] Review completed, score: {review_result.get('quality_score', 0)}")
            
            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(review_result, ensure_ascii=False, indent=2),
                success=True,
                metadata={
                    "quality_score": review_result.get("quality_score", 0),
                    "passed": review_result.get("passed", False),
                }
            )
        except Exception as e:
            logger.error(f"[{self.name}] Review failed: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error=str(e)
            )
    
    def _parse_review(self, text: str) -> Dict[str, Any]:
        """解析评审结果"""
        try:
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
            if json_match:
                return json.loads(json_match.group(1))
            
            brace_match = re.search(r"\{[\s\S]*\}", text)
            if brace_match:
                return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass
        
        score = 0.0
        score_match = re.search(r"(?:score|评分|得分)[:\s]*(\d+(?:\.\d+)?)", text, re.I)
        if score_match:
            score = float(score_match.group(1))
        
        return {
            "quality_score": score,
            "passed": score >= 80,
            "dimensions": {},
            "issues": [],
            "suggestions": [],
            "summary": text[:500] if len(text) > 500 else text,
        }
