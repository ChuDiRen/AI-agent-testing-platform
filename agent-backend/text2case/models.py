"""数据模型"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

from langchain_core.messages import BaseMessage


# ============== Pydantic 数据验证模型 ==============

class TestCaseItem(BaseModel):
    """单个测试用例 (Pydantic验证)"""
    用例编号: str = Field(..., description="用例唯一编号，如TC001")
    用例标题: str = Field(..., description="用例标题")
    优先级: str = Field(default="P1", description="优先级: P0/P1/P2/P3")
    前置条件: str = Field(default="", description="测试前置条件")
    测试步骤: List[str] = Field(default_factory=list, description="测试步骤列表")
    预期结果: List[str] = Field(default_factory=list, description="预期结果列表")
    测试数据: Dict[str, Any] = Field(default_factory=dict, description="测试数据")
    
    @validator('优先级')
    def validate_priority(cls, v):
        valid = ['P0', 'P1', 'P2', 'P3']
        if v not in valid:
            return 'P1'  # 默认P1
        return v


class TestCaseModule(BaseModel):
    """测试用例模块"""
    功能模块: str = Field(..., description="功能模块名称")
    测试用例列表: List[TestCaseItem] = Field(default_factory=list)


class TestCaseSuite(BaseModel):
    """测试用例套件 (完整输出格式)"""
    测试用例: List[TestCaseModule] = Field(default_factory=list)
    
    @property
    def total_cases(self) -> int:
        """总用例数"""
        return sum(len(m.测试用例列表) for m in self.测试用例)
    
    @property
    def modules_count(self) -> int:
        """模块数"""
        return len(self.测试用例)


# ============== 版本历史记录 ==============

@dataclass
class TestCaseVersion:
    """测试用例版本记录"""
    version: int
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality_score: float = 0.0


@dataclass
class ReviewRecord:
    """评审记录"""
    version: int
    feedback: str
    score: float
    passed: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    dimensions: Dict[str, float] = field(default_factory=dict)  # 各维度评分


# ============== 质量评分维度 ==============

class QualityDimension(Enum):
    """质量评分维度 (与评审专家保持一致)"""
    COVERAGE = "覆盖度"  # 30分
    COMPLETENESS = "完整性"  # 25分
    CLARITY = "清晰度"  # 20分
    EXECUTABILITY = "可执行性"  # 15分
    DESIGN = "设计合理性"  # 10分


@dataclass
class QualityScore:
    """质量评分 (与评审专家ReviewScore保持一致)"""
    coverage: float = 0.0       # 覆盖度 (0-30)
    completeness: float = 0.0   # 完整性 (0-25)
    clarity: float = 0.0        # 清晰度 (0-20)
    executability: float = 0.0  # 可执行性 (0-15)
    design: float = 0.0         # 设计合理性 (0-10)
    
    @property
    def total(self) -> float:
        """总分 (0-100)"""
        return self.coverage + self.completeness + self.clarity + self.executability + self.design
    
    @property
    def passed(self) -> bool:
        """是否通过 (>=80分)"""
        return self.total >= 80.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "覆盖度": self.coverage,
            "完整性": self.completeness,
            "清晰度": self.clarity,
            "可执行性": self.executability,
            "设计合理性": self.design,
            "总分": self.total
        }


# ============== 原有数据模型 ==============

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
    """测试用例生成状态 (支持 middlewareV1 + 多智能体协作 + 版本管理)
    
    核心特性:
    - 状态持久化: 每个阶段的输出都会被保存
    - 版本管理: 支持历史追踪和回溯
    - 质量评分: 多维度评分体系
    - 断点续传: 支持从上次状态继续执行
    """
    requirement: str
    test_type: Literal["API", "Web", "App"] = "API"

    # ============== 核心数据字段 (5个智能体的输出) ==============
    requirement_doc: str = ""  # 需求文档内容 (URL获取或直接输入)
    analysis: str = ""  # 需求分析结果 (Analyzer输出)
    test_points: str = ""  # 测试点设计 (TestPointDesigner输出)
    testcases: str = ""  # 生成的测试用例 (Writer输出)
    review: str = ""  # 审查反馈 (Reviewer输出)

    # ============== 版本管理字段 ==============
    test_cases_history: List[Dict[str, Any]] = field(default_factory=list)  # 测试用例历史版本
    review_history: List[Dict[str, Any]] = field(default_factory=list)  # 评审意见历史
    
    # ============== 质量评分字段 ==============
    quality_score: float = 0.0  # 当前质量评分 (0-100)
    quality_dimensions: Dict[str, float] = field(default_factory=dict)  # 各维度评分
    
    # ============== 数据处理输出 ==============
    xmind_path: str = ""  # XMind文件路径
    excel_path: str = ""  # Excel文件路径
    output_package_path: str = ""  # 输出包路径
    statistics: Dict[str, Any] = field(default_factory=dict)  # 统计信息

    # ============== Writer 流式生成状态 ==============
    writer_chunks: List[str] = field(default_factory=list)
    writer_total_chunks: int = 0
    writer_current_chunk: int = 0
    writer_progress: float = 0.0  # 0.0-1.0
    writer_last_chunk: str = ""

    # ============== 迭代控制 ==============
    iteration: int = 0
    max_iterations: int = 3  # 默认最多3次迭代

    # ============== 消息历史 (middlewareV1 核心字段) ==============
    messages: List[BaseMessage] = field(default_factory=list)

    # ============== 阶段跟踪 ==============
    current_phase: str = "init"  # 当前执行阶段: init/analyze/design/generate/review/process/end
    target_phase: str = "end"  # 目标阶段 (用于意图识别)

    # ============== 阶段完成标记 (5个智能体) ==============
    analyze_completed: bool = False
    design_completed: bool = False
    generate_completed: bool = False
    review_completed: bool = False
    process_completed: bool = False  # 数据处理完成
    
    # ============== 测试方法选择 ==============
    selected_test_methods: List[str] = field(default_factory=list)  # 选中的测试方法

    @property
    def completed(self) -> bool:
        """是否完成"""
        # 评审通过或达到最大迭代次数
        review_passed = self.quality_score >= 80.0 or "通过" in self.review or "PASS" in self.review.upper()
        return bool(self.testcases and (self.iteration >= self.max_iterations or review_passed))
    
    def add_test_case_version(self, content: str, score: float = 0.0) -> None:
        """添加测试用例版本"""
        version = {
            "version": len(self.test_cases_history) + 1,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "quality_score": score
        }
        self.test_cases_history.append(version)
    
    def add_review_record(self, feedback: str, score: float, passed: bool, dimensions: Dict[str, float] = None) -> None:
        """添加评审记录"""
        record = {
            "version": len(self.review_history) + 1,
            "feedback": feedback,
            "score": score,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "dimensions": dimensions or {}
        }
        self.review_history.append(record)
    
    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        """获取最新版本"""
        if self.test_cases_history:
            return self.test_cases_history[-1]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (用于持久化)"""
        return {
            "requirement": self.requirement,
            "test_type": self.test_type,
            "requirement_doc": self.requirement_doc,
            "analysis": self.analysis,
            "test_points": self.test_points,
            "testcases": self.testcases,
            "review": self.review,
            "test_cases_history": self.test_cases_history,
            "review_history": self.review_history,
            "quality_score": self.quality_score,
            "quality_dimensions": self.quality_dimensions,
            "xmind_path": self.xmind_path,
            "excel_path": self.excel_path,
            "output_package_path": self.output_package_path,
            "statistics": self.statistics,
            "iteration": self.iteration,
            "current_phase": self.current_phase,
            "target_phase": self.target_phase,
            "analyze_completed": self.analyze_completed,
            "design_completed": self.design_completed,
            "generate_completed": self.generate_completed,
            "review_completed": self.review_completed,
            "process_completed": self.process_completed,
        }


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

