"""
AnalyzerAgent - 需求分析专家

深度解析需求文档，提取测试要素
"""
import logging
from typing import Dict, Any

from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse, AgentRole

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """需求分析专家"""
    
    name = "analyzer"
    role = AgentRole.ANALYZER
    description = "需求分析专家，负责深度解析需求文档，提取功能点、业务规则和测试要素"
    temperature = 0.3
    prompt_name = "analyzer"  # 从prompts/analyzer.txt加载
    
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """分析需求"""
        logger.info(f"[{self.name}] Starting requirement analysis...")
        
        requirement = state.get("requirement", "")
        test_type = state.get("test_type", "API")
        
        if not requirement:
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error="需求描述为空"
            )
        
        user_message = f"""请分析以下需求，提取测试要素：

## 需求内容
{requirement}

## 测试类型
{test_type}

请按照系统提示的格式输出分析结果。
"""
        
        try:
            analysis = await self.invoke_llm(user_message)
            logger.info(f"[{self.name}] Analysis completed, length: {len(analysis)}")
            
            return AgentResponse(
                agent_name=self.name,
                content=analysis,
                success=True,
                metadata={"analysis_length": len(analysis)}
            )
        except Exception as e:
            logger.error(f"[{self.name}] Analysis failed: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="",
                success=False,
                error=str(e)
            )
