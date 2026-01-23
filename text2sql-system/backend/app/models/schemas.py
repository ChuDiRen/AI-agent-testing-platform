"""
数据模型包
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Text2SQLRequest(BaseModel):
    """自然语言查询请求"""
    query: str


class Text2SQLResponse(BaseModel):
    """SQL查询响应模型"""
    sql: str
    explanation: str
    results: List[Dict[str, Any]]
    visualization_type: Optional[str] = None
    visualization_config: Optional[Dict[str, Any]] = None


class ResponseMessage(BaseModel):
    """流式响应消息"""
    source: str
    content: str
    is_final: bool = False
    result: Optional[Dict[str, Any]] = None


class AnalysisResult(BaseModel):
    """查询分析结果"""
    query_intent: Dict[str, Any]
    entities: Dict[str, Any]
    table_mapping: Dict[str, Any]
    query_structure: Dict[str, Any]
    analysis_confidence: float
    potential_issues: List[str] = []


class SQLGenerationResult(BaseModel):
    """SQL生成结果"""
    sql: str
    validation: Dict[str, Any]
    optimization_notes: List[str] = []


class ExplanationResult(BaseModel):
    """SQL解释结果"""
    explanation: Dict[str, str]
    sql_complexity: Dict[str, Any]
    educational_notes: List[str] = []
    performance_insights: List[str] = []


class ExecutionResult(BaseModel):
    """SQL执行结果"""
    success: bool
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float
    row_count: int
    columns: List[str]


class VisualizationRecommendation(BaseModel):
    """可视化推荐结果"""
    primary_recommendation: Dict[str, Any]
    alternative_recommendations: List[Dict[str, Any]] = []
    data_insights: List[str] = []
    recommendation_reasoning: str = ""
