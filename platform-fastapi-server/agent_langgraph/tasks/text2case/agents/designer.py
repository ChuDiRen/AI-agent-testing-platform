"""
DesignerAgent - 测试点设计专家

设计全面的测试点覆盖方案
"""
import logging
from typing import Dict, Any

from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse, AgentRole

logger = logging.getLogger(__name__)


class DesignerAgent(BaseAgent):
    """测试点设计专家"""
    
    name = "designer"
    role = AgentRole.DESIGNER
    description = "测试点设计专家，负责设计全面的测试点覆盖方案，包括功能、边界、异常测试点"
    temperature = 0.5
    prompt_name = "designer"  # 从prompts/designer.txt加载
    
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """设计测试点"""
        logger.info(f"[{self.name}] Starting test point design...")
        
        requirement = state.get("requirement", "")
        analysis = state.get("analysis", "")
        test_type = state.get("test_type", "API")
        
        if not analysis:
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error="需求分析结果为空，请先进行需求分析"
            )
        
        user_message = f"""请基于以下需求分析结果，设计完整的测试点覆盖方案：

## 原始需求
{requirement}

## 需求分析结果
{analysis}

## 测试类型
{test_type}

请按照系统提示的格式输出测试点设计。
"""
        
        try:
            test_points = await self.invoke_llm(user_message)
            logger.info(f"[{self.name}] Test points designed, length: {len(test_points)}")
            
            return AgentResponse(
                agent_name=self.name,
                content=test_points,
                success=True,
                metadata={"test_points_length": len(test_points)}
            )
        except Exception as e:
            logger.error(f"[{self.name}] Design failed: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error=str(e)
            )
