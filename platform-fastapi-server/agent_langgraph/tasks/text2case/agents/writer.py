"""
WriterAgent - 用例编写专家

生成结构化测试用例（JSON格式）
"""
import json
import re
import logging
from typing import Dict, Any, List

from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse, AgentRole

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """用例编写专家"""
    
    name = "writer"
    role = AgentRole.WRITER
    description = "用例编写专家，负责根据测试点编写详细的结构化测试用例"
    temperature = 0.7
    prompt_name = "writer"  # 从prompts/writer.txt加载
    
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """编写测试用例"""
        logger.info(f"[{self.name}] Starting test case writing...")
        
        requirement = state.get("requirement", "")
        analysis = state.get("analysis", "")
        test_points = state.get("test_points", "")
        test_type = state.get("test_type", "API")
        review_feedback = state.get("review_feedback", "")
        
        if not test_points:
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error="测试点设计为空，请先进行测试点设计"
            )
        
        feedback_section = ""
        if review_feedback:
            feedback_section = f"""
## 评审反馈（请根据反馈改进）
{review_feedback}
"""
        
        user_message = f"""请基于以下测试点设计，编写详细的测试用例：

## 原始需求
{requirement}

## 需求分析
{analysis}

## 测试点设计
{test_points}

## 测试类型
{test_type}
{feedback_section}
请严格按照JSON格式输出测试用例，确保可以被程序解析。
"""
        
        try:
            response = await self.invoke_llm(user_message)
            test_cases_json = self._extract_json(response)
            
            logger.info(f"[{self.name}] Test cases written, length: {len(test_cases_json)}")
            
            return AgentResponse(
                agent_name=self.name,
                content=test_cases_json,
                success=True,
                metadata={"raw_response_length": len(response)}
            )
        except Exception as e:
            logger.error(f"[{self.name}] Writing failed: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error=str(e)
            )
    
    def _extract_json(self, text: str) -> str:
        """从响应中提取JSON"""
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if json_match:
            return json_match.group(1).strip()
        
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            return brace_match.group(0)
        
        return text
