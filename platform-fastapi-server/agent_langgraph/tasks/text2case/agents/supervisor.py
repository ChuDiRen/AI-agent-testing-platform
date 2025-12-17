"""
SupervisorAgent - 协调者智能体

负责协调各专家智能体的执行顺序，实现多智能体协作
"""
import json
import logging
from typing import Dict, Any, List, Literal

from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse, AgentRole

logger = logging.getLogger(__name__)

# 可用的下一步选项
NEXT_OPTIONS = Literal["analyzer", "designer", "writer", "reviewer", "FINISH"]


class SupervisorAgent(BaseAgent):
    """
    协调者智能体
    
    负责：
    1. 分析当前状态
    2. 决定下一步由哪个智能体执行
    3. 判断任务是否完成
    """
    
    name = "supervisor"
    role = AgentRole.SUPERVISOR
    description = "协调者，负责分析当前状态并决定下一步由哪个智能体执行"
    temperature = 0.1
    prompt_name = "supervisor"  # 从prompts/supervisor.txt加载
    
    # 智能体执行顺序
    AGENT_ORDER = ["analyzer", "designer", "writer", "reviewer"]
    
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """决定下一步执行哪个智能体"""
        logger.info(f"[{self.name}] Analyzing state and deciding next step...")
        
        # 提取状态信息
        analysis = state.get("analysis", "")
        test_points = state.get("test_points", "")
        test_cases = state.get("test_cases", "")
        quality_score = state.get("quality_score", 0)
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)
        completed = state.get("completed", False)
        error = state.get("error")
        
        # 如果已完成或有错误，直接结束
        if completed or error:
            return self._create_response("FINISH", "任务已完成或出现错误")
        
        # 规则驱动的决策（快速路径）
        next_agent = self._rule_based_decision(
            analysis=analysis,
            test_points=test_points,
            test_cases=test_cases,
            quality_score=quality_score,
            iteration=iteration,
            max_iterations=max_iterations,
        )
        
        if next_agent:
            reason = self._get_decision_reason(next_agent, quality_score, iteration)
            return self._create_response(next_agent, reason)
        
        # 如果规则无法决定，使用LLM决策
        return await self._llm_based_decision(state)
    
    def _rule_based_decision(
        self,
        analysis: str,
        test_points: str,
        test_cases: str,
        quality_score: float,
        iteration: int,
        max_iterations: int,
    ) -> str:
        """基于规则的决策"""
        # 没有分析结果 -> analyzer
        if not analysis:
            return "analyzer"
        
        # 有分析但没有测试点 -> designer
        if not test_points:
            return "designer"
        
        # 有测试点但没有测试用例 -> writer
        if not test_cases:
            return "writer"
        
        # 有测试用例但没有评审（quality_score为0表示未评审）
        if quality_score == 0:
            return "reviewer"
        
        # 评审通过 -> FINISH
        if quality_score >= 80:
            return "FINISH"
        
        # 评审不通过但达到最大迭代 -> FINISH
        if iteration >= max_iterations:
            return "FINISH"
        
        # 评审不通过且未达到最大迭代 -> writer
        return "writer"
    
    def _get_decision_reason(self, next_agent: str, quality_score: float, iteration: int) -> str:
        """获取决策原因"""
        reasons = {
            "analyzer": "需要先进行需求分析",
            "designer": "需求分析完成，开始设计测试点",
            "writer": f"开始编写测试用例（迭代 {iteration + 1}）" if quality_score > 0 else "测试点设计完成，开始编写测试用例",
            "reviewer": "测试用例编写完成，开始评审",
            "FINISH": f"评审通过（得分: {quality_score}）" if quality_score >= 80 else f"达到最大迭代次数（得分: {quality_score}）",
        }
        return reasons.get(next_agent, "继续执行")
    
    async def _llm_based_decision(self, state: Dict[str, Any]) -> AgentResponse:
        """基于LLM的决策（备用）"""
        state_summary = f"""
当前状态：
- 需求分析: {'已完成' if state.get('analysis') else '未完成'}
- 测试点设计: {'已完成' if state.get('test_points') else '未完成'}
- 测试用例: {'已完成' if state.get('test_cases') else '未完成'}
- 评审得分: {state.get('quality_score', 0)}
- 当前迭代: {state.get('iteration', 0)}/{state.get('max_iterations', 3)}
"""
        
        try:
            response = await self.invoke_llm(f"请根据以下状态决定下一步：\n{state_summary}")
            result = self._parse_decision(response)
            return self._create_response(result["next"], result["reason"])
        except Exception as e:
            logger.error(f"[{self.name}] LLM decision failed: {e}")
            # 降级到规则决策
            return self._create_response("FINISH", f"决策失败: {e}")
    
    def _parse_decision(self, text: str) -> Dict[str, str]:
        """解析决策结果"""
        import re
        
        try:
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
            if json_match:
                return json.loads(json_match.group(1))
            
            brace_match = re.search(r"\{[\s\S]*\}", text)
            if brace_match:
                return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass
        
        # 尝试从文本中提取
        for agent in self.AGENT_ORDER + ["FINISH"]:
            if agent.lower() in text.lower():
                return {"next": agent, "reason": "从响应中提取"}
        
        return {"next": "FINISH", "reason": "无法解析决策"}
    
    def _create_response(self, next_agent: str, reason: str) -> AgentResponse:
        """创建响应"""
        return AgentResponse(
            agent_name=self.name,
            content=json.dumps({"next": next_agent, "reason": reason}, ensure_ascii=False),
            success=True,
            metadata={"next": next_agent, "reason": reason}
        )
