"""数据模型"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, List, Dict, Any, Optional

from langchain_core.messages import BaseMessage


@dataclass
class ApiEndpoint:
    """API接口"""
    path: str
    method: str
    operation_id: str
    summary: str
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_requirement(self) -> str:
        """转换为需求文本"""
        import json
        return f"""
# {self.method} {self.path}
**功能**: {self.summary}
**描述**: {self.description or '无'}
**参数**: {json.dumps(self.parameters, indent=2, ensure_ascii=False) if self.parameters else '无'}
**请求体**: {json.dumps(self.request_body, indent=2, ensure_ascii=False) if self.request_body else '无'}
**响应**: {json.dumps(self.responses, indent=2, ensure_ascii=False)}
""".strip()


@dataclass
class BusinessScenario:
    """业务场景"""
    name: str
    description: str
    endpoints: List[ApiEndpoint]
    execution_order: List[str]
    
    def to_requirement(self) -> str:
        """转换为需求文本"""
        endpoints_info = "\n\n".join(f"## {i+1}. {ep.method} {ep.path}\n{ep.summary}" 
                                     for i, ep in enumerate(self.endpoints))
        return f"""
# 业务场景: {self.name}
**描述**: {self.description}
**执行顺序**: {' → '.join(self.execution_order)}

{endpoints_info}
""".strip()


@dataclass
class TestCaseState:
    """测试用例生成状态 (支持 middlewareV1 + 多智能体协作)"""
    requirement: str
    test_type: Literal["API", "Web", "App"] = "API"

    # 核心数据字段 (4个智能体的输出)
    analysis: str = ""  # 需求分析结果 (Analyzer输出)
    test_points: str = ""  # 测试点设计 (TestPointDesigner输出)
    testcases: str = ""  # 生成的测试用例 (Writer输出)
    review: str = ""  # 审查反馈 (Reviewer输出)

    # Writer 流式生成状态
    writer_chunks: List[str] = field(default_factory=list)
    writer_total_chunks: int = 0
    writer_current_chunk: int = 0
    writer_progress: float = 0.0  # 0.0-1.0
    writer_last_chunk: str = ""

    # 迭代控制
    iteration: int = 0
    max_iterations: int = 2

    # 消息历史 (middlewareV1 核心字段)
    messages: List[BaseMessage] = field(default_factory=list)

    # 阶段跟踪
    current_phase: str = ""  # 当前执行阶段

    # 阶段完成标记 (4个智能体)
    analyze_completed: bool = False
    design_completed: bool = False
    generate_completed: bool = False
    review_completed: bool = False

    @property
    def completed(self) -> bool:
        """是否完成"""
        return bool(self.testcases and (self.iteration >= self.max_iterations or "通过" in self.review))


@dataclass
class TestCaseRecord:
    """测试用例记录"""
    id: int
    thread_id: str
    requirement: str
    test_type: str
    analysis: str
    testcases: str
    review: str
    iteration: int
    created_at: datetime

