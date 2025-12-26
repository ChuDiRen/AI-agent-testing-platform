"""
监督代理 - 基于 langgraph_supervisor 官方库

协调整个测试用例生成工作流程，智能路由任务给专门化代理
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph_supervisor import create_supervisor
from langchain_core.language_models import BaseChatModel

from .analyzer_agent import create_analyzer_agent
from .writer_agent import create_writer_agent
from .reviewer_agent import create_reviewer_agent
from .exporter_agent import create_exporter_agent


def _load_supervisor_prompt(max_retries: int = 2) -> str:
    """加载 Supervisor 提示词"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "supervisor.md"
    if prompt_path.exists():
        content = prompt_path.read_text(encoding='utf-8')
        return content.replace("{max_retries}", str(max_retries))
    
    # 默认提示词
    return f"""你是一个专门协调测试用例生成工作流的监督代理。

## 可用代理
- analyzer_expert: 需求分析专家
- writer_expert: 测试用例编写专家
- reviewer_expert: 测试用例评审专家
- exporter_expert: 数据导出专家

## 工作流程
1. analyzer_expert → 分析需求
2. writer_expert → 生成测试用例
3. reviewer_expert → 评审用例（可选）
4. exporter_expert → 导出文件（用户需要时）

## 决策原则
- 根据用户意图智能选择流程
- 质量评分 < 70 时，让 writer_expert 优化
- 最多优化 {max_retries} 次
"""


def create_text2case_supervisor(
    model: BaseChatModel,
    agents: List = None,
    max_retries: int = 2
) -> Any:
    """创建测试用例生成监督代理
    
    Args:
        model: LLM 模型
        agents: 子代理列表，如果为 None 则自动创建
        max_retries: 最大重试次数
        
    Returns:
        配置好的 Supervisor
    """
    if agents is None:
        agents = [
            create_analyzer_agent(model),
            create_writer_agent(model),
            create_reviewer_agent(model),
            create_exporter_agent(model),
        ]
    
    prompt = _load_supervisor_prompt(max_retries)
    
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt=prompt,
        output_mode="full_history",  # 让 Supervisor 看到完整的消息历史
        add_handoff_back_messages=True,  # 添加 handoff 返回消息
    )
    
    return supervisor


def build_supervisor_with_config(
    model: BaseChatModel,
    max_retries: int = 2,
    enable_review: bool = True,
    enable_export: bool = False
) -> Any:
    """构建带配置的 Supervisor
    
    Args:
        model: LLM 模型
        max_retries: 最大重试次数
        enable_review: 是否启用评审
        enable_export: 是否启用导出
        
    Returns:
        配置好的 Supervisor
    """
    # 根据配置创建代理列表
    agents = [
        create_analyzer_agent(model),
        create_writer_agent(model),
    ]
    
    if enable_review:
        agents.append(create_reviewer_agent(model))
    
    if enable_export:
        agents.append(create_exporter_agent(model))
    
    prompt = _load_supervisor_prompt(max_retries)
    
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt=prompt,
        output_mode="full_history",  # 让 Supervisor 看到完整的消息历史
        add_handoff_back_messages=True,  # 添加 handoff 返回消息
    )
    
    return supervisor
