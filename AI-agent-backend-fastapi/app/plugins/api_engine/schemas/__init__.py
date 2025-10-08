"""
API引擎插件Schema
"""
from .suite import (
    SuiteCreate,
    SuiteUpdate,
    SuiteResponse,
    SuiteListResponse
)
from .case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
    CaseExecuteRequest
)
from .execution import (
    ExecutionResponse,
    ExecutionListResponse,
    ExecutionStatusResponse
)
from .keyword import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse
)

__all__ = [
    # Suite
    "SuiteCreate",
    "SuiteUpdate",
    "SuiteResponse",
    "SuiteListResponse",
    # Case
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    "CaseListResponse",
    "CaseExecuteRequest",
    # Execution
    "ExecutionResponse",
    "ExecutionListResponse",
    "ExecutionStatusResponse",
    # Keyword
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    "KeywordListResponse",
]
