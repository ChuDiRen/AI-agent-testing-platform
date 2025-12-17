"""
LangGraph Graph Definition

用于 langgraph dev 服务器的图定义
"""
import os
import json
import re
import logging
from typing import TypedDict, List, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# ==================== State Definition ====================

class GraphState(TypedDict):
    """LangGraph状态定义"""
    messages: List[dict]
    requirement: str
    test_type: str
    analysis: Optional[str]
    test_points: Optional[List[str]]
    test_cases: Optional[List[dict]]
    quality_score: Optional[dict]
    iteration: int
    max_iterations: int
    completed: bool
    error: Optional[str]


# ==================== Node Functions ====================

def get_model():
    """获取模型实例"""
    # 默认使用 SiliconFlow API（写死配置，避免环境变量问题）
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")
    
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.3,
    )


def analyze_requirement(state: GraphState) -> GraphState:
    """分析需求"""
    logger.info("Analyzing requirement...")
    
    model = get_model()
    requirement = state.get("requirement", "")
    
    if not requirement:
        # 从messages中获取
        messages = state.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict) and msg.get("type") == "human":
                requirement = msg.get("content", "")
                break
    
    if not requirement:
        return {**state, "error": "请输入需求描述"}
    
    prompt = f"""你是一个专业的需求分析师，请分析以下需求并提取关键测试点：

需求描述：
{requirement}

请输出：
1. 需求概述
2. 功能点列表
3. 测试场景（正常流程和异常情况）
4. 业务规则和约束条件
"""
    
    try:
        response = model.invoke(prompt)
        analysis = response.content
        return {
            **state,
            "requirement": requirement,
            "analysis": analysis,
            "messages": state.get("messages", []) + [{"type": "ai", "content": f"需求分析完成:\n{analysis}"}]
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {**state, "error": str(e)}


def design_test_points(state: GraphState) -> GraphState:
    """设计测试点"""
    logger.info("Designing test points...")
    
    if state.get("error"):
        return state
    
    model = get_model()
    analysis = state.get("analysis", "")
    requirement = state.get("requirement", "")
    
    prompt = f"""你是一位资深的测试点设计专家，请根据以下需求分析设计测试点：

需求描述：
{requirement}

需求分析：
{analysis}

请设计全面的测试点，包括：
1. 功能测试点
2. 边界值测试点
3. 异常测试点
4. 性能测试点（如适用）

输出格式：每个测试点一行，用数字编号。
"""
    
    try:
        response = model.invoke(prompt)
        test_points_text = response.content
        # 解析测试点
        test_points = [line.strip() for line in test_points_text.split('\n') if line.strip() and line.strip()[0].isdigit()]
        
        return {
            **state,
            "test_points": test_points,
            "messages": state.get("messages", []) + [{"type": "ai", "content": f"测试点设计完成，共{len(test_points)}个测试点"}]
        }
    except Exception as e:
        logger.error(f"Design failed: {e}")
        return {**state, "error": str(e)}


def write_test_cases(state: GraphState) -> GraphState:
    """编写测试用例"""
    logger.info("Writing test cases...")
    
    if state.get("error"):
        return state
    
    model = get_model()
    requirement = state.get("requirement", "")
    test_points = state.get("test_points", [])
    test_type = state.get("test_type", "API")
    
    prompt = f"""你是一个经验丰富的测试工程师，请根据以下测试点编写详细的测试用例：

需求描述：
{requirement}

测试类型：{test_type}

测试点：
{chr(10).join(test_points[:10])}

请为每个测试点编写测试用例，输出JSON格式：
```json
[
  {{
    "case_name": "用例名称",
    "priority": "P0/P1/P2",
    "precondition": "前置条件",
    "steps": ["步骤1", "步骤2"],
    "expected_result": "预期结果"
  }}
]
```
"""
    
    try:
        response = model.invoke(prompt)
        content = response.content
        
        # 尝试解析JSON
        import json
        import re
        
        # 提取JSON部分
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            test_cases = json.loads(json_match.group())
        else:
            test_cases = [{"case_name": "解析失败", "content": content}]
        
        iteration = state.get("iteration", 0) + 1
        
        return {
            **state,
            "test_cases": test_cases,
            "iteration": iteration,
            "messages": state.get("messages", []) + [{"type": "ai", "content": f"测试用例编写完成，共{len(test_cases)}个用例"}]
        }
    except Exception as e:
        logger.error(f"Write failed: {e}")
        return {**state, "error": str(e)}


def review_test_cases(state: GraphState) -> GraphState:
    """评审测试用例"""
    logger.info("Reviewing test cases...")
    
    if state.get("error"):
        return state
    
    model = get_model()
    test_cases = state.get("test_cases", [])
    requirement = state.get("requirement", "")
    
    import json
    
    prompt = f"""你是一个资深的测试用例审查专家，请评审以下测试用例：

需求描述：
{requirement}

测试用例：
{json.dumps(test_cases, ensure_ascii=False, indent=2)}

请从以下维度评分（0-100）：
1. 覆盖度 - 是否覆盖所有功能点
2. 完整性 - 用例描述是否完整
3. 清晰度 - 步骤是否清晰可执行
4. 合理性 - 预期结果是否合理

输出JSON格式：
```json
{{
  "total_score": 85,
  "coverage": 90,
  "completeness": 85,
  "clarity": 80,
  "rationality": 85,
  "suggestions": ["建议1", "建议2"]
}}
```
"""
    
    try:
        response = model.invoke(prompt)
        content = response.content
        
        # 解析评分
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            quality_score = json.loads(json_match.group())
        else:
            quality_score = {"total_score": 80, "suggestions": []}
        
        total_score = quality_score.get("total_score", 80)
        completed = total_score >= 80 or state.get("iteration", 0) >= state.get("max_iterations", 2)
        
        return {
            **state,
            "quality_score": quality_score,
            "completed": completed,
            "messages": state.get("messages", []) + [{"type": "ai", "content": f"评审完成，总分: {total_score}"}]
        }
    except Exception as e:
        logger.error(f"Review failed: {e}")
        return {**state, "error": str(e)}


def should_continue(state: GraphState) -> str:
    """决定是否继续迭代"""
    if state.get("error"):
        return END
    if state.get("completed"):
        return END
    if state.get("iteration", 0) >= state.get("max_iterations", 2):
        return END
    return "write_test_cases"


# ==================== Build Graph ====================

def build_graph(checkpointer=None):
    """构建LangGraph图"""
    workflow = StateGraph(GraphState)
    
    # 添加节点
    workflow.add_node("analyze_requirement", analyze_requirement)
    workflow.add_node("design_test_points", design_test_points)
    workflow.add_node("write_test_cases", write_test_cases)
    workflow.add_node("review_test_cases", review_test_cases)
    
    # 添加边
    workflow.add_edge(START, "analyze_requirement")
    workflow.add_edge("analyze_requirement", "design_test_points")
    workflow.add_edge("design_test_points", "write_test_cases")
    workflow.add_edge("write_test_cases", "review_test_cases")
    
    # 条件边 - 评审后决定是否继续
    workflow.add_conditional_edges(
        "review_test_cases",
        should_continue,
        {
            "write_test_cases": "write_test_cases",
            END: END
        }
    )
    
    # 使用checkpointer编译图
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


# 导出graph实例供langgraph dev使用
graph = build_graph()
