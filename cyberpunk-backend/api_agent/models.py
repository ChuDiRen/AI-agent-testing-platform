"""
API Automation Agent Platform - Core Data Models

This module defines all the core data models for the platform.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl
from sqlmodel import SQLModel, Field as SQLField, Column, JSON


# Enums
class HttpMethod(str, Enum):
    """HTTP Method Enum"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TestPriority(str, Enum):
    """Test Priority Enum"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(str, Enum):
    """Test Type Enum"""
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    BOUNDARY = "boundary"


class TestStatus(str, Enum):
    """Test Status Enum"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class TaskStatus(str, Enum):
    """Task Status Enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# API Models
class APIParameter(BaseModel):
    """API Parameter Model"""
    name: str
    param_type: str  # path, query, header, cookie
    data_type: str
    required: bool = False
    description: Optional[str] = None
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


class APIEndpoint(BaseModel):
    """API Endpoint Model"""
    path: str
    method: HttpMethod
    summary: str
    description: str
    tags: List[str] = []
    parameters: List[APIParameter] = []
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any] = {}
    security: List[Dict[str, Any]] = []


# Test Case Models
class TestAssertion(BaseModel):
    """Test Assertion Model"""
    assertion_id: str
    assertion_type: str  # status_code, json_path, contains, equals, etc.
    target: str
    expected: Any
    operator: str = "=="  # ==, !=, >, <, contains, etc.
    description: Optional[str] = None


class TestStep(BaseModel):
    """Test Step Model"""
    step_id: str
    name: str
    description: str
    endpoint: str
    method: HttpMethod
    headers: Dict[str, str] = {}
    query_params: Dict[str, Any] = {}
    path_params: Dict[str, Any] = {}
    request_body: Optional[Any] = None
    assertions: List[TestAssertion] = []
    extract_variables: Dict[str, str] = {}
    depends_on: List[str] = []


class TestCase(BaseModel):
    """Test Case Model"""
    case_id: str
    name: str
    description: str
    priority: TestPriority
    test_type: TestType
    tags: List[str] = []
    preconditions: List[str] = []
    steps: List[TestStep] = []
    setup_steps: List[TestStep] = []
    teardown_steps: List[TestStep] = []
    estimated_duration_ms: Optional[int] = None


# Test Result Models
class CaseResult(BaseModel):
    """Test Case Result Model"""
    case_id: str
    case_name: str
    status: TestStatus
    duration_ms: float
    error_message: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0
    execution_log: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class SuiteResult(BaseModel):
    """Test Suite Result Model"""
    suite_id: str
    suite_name: str
    status: TestStatus
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    duration_ms: float
    case_results: List[CaseResult] = []
    start_time: str
    end_time: str
    summary: Optional[str] = None


# Database Models (SQLModel)
class TaskDB(SQLModel, table=True):
    """Task Database Model"""
    __tablename__ = "tasks"  # type: ignore

    id: Optional[int] = SQLField(default=None, primary_key=True)
    task_id: str = SQLField(index=True, unique=True)
    name: str
    description: Optional[str] = None
    status: TaskStatus = SQLField(default=TaskStatus.PENDING)
    user_id: Optional[str] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = SQLField(default=None, sa_column=Column(JSON))
    error: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = SQLField(default=None, sa_column=Column(JSON))


class SessionDB(SQLModel, table=True):
    """Session Database Model"""
    __tablename__ = "sessions"  # type: ignore

    id: Optional[int] = SQLField(default=None, primary_key=True)
    session_id: str = SQLField(index=True, unique=True)
    user_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    active: bool = SQLField(default=True)
    tasks: List[str] = SQLField(default=[], sa_column=Column(JSON))
    meta_data: Optional[Dict[str, Any]] = SQLField(default=None, sa_column=Column(JSON))


class DocumentDB(SQLModel, table=True):
    """Document Database Model"""
    __tablename__ = "documents"  # type: ignore

    id: Optional[int] = SQLField(default=None, primary_key=True)
    doc_id: str = SQLField(index=True, unique=True)
    name: str
    type: str  # openapi, swagger, graphql, pdf, etc.
    url: Optional[str] = None
    file_path: Optional[str] = None
    content_hash: Optional[str] = None
    indexed: bool = SQLField(default=False)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    meta_data: Optional[Dict[str, Any]] = SQLField(default=None, sa_column=Column(JSON))


class TestSuiteDB(SQLModel, table=True):
    """Test Suite Database Model"""
    __tablename__ = "test_suites"  # type: ignore

    id: Optional[int] = SQLField(default=None, primary_key=True)
    suite_id: str = SQLField(index=True, unique=True)
    name: str
    description: Optional[str] = None
    task_id: str = SQLField(foreign_key="tasks.task_id")
    test_cases: List[Dict[str, Any]] = SQLField(default=[], sa_column=Column(JSON))
    total_cases: int = SQLField(default=0)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)


class TestExecutionDB(SQLModel, table=True):
    """Test Execution Database Model"""
    __tablename__ = "test_executions"  # type: ignore

    id: Optional[int] = SQLField(default=None, primary_key=True)
    execution_id: str = SQLField(index=True, unique=True)
    suite_id: str = SQLField(foreign_key="test_suites.suite_id")
    task_id: str = SQLField(foreign_key="tasks.task_id")
    status: TestStatus = SQLField(default=TestStatus.PENDING)
    total_cases: int = SQLField(default=0)
    passed_cases: int = SQLField(default=0)
    failed_cases: int = SQLField(default=0)
    skipped_cases: int = SQLField(default=0)
    duration_ms: float = SQLField(default=0.0)
    results: Optional[Dict[str, Any]] = SQLField(default=None, sa_column=Column(JSON))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


# Request/Response Models for API
class TaskCreate(BaseModel):
    """Create Task Request Model"""
    name: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Task Response Model"""
    task_id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpload(BaseModel):
    """Document Upload Request Model"""
    name: str
    type: str  # openapi, swagger, graphql, pdf, etc.
    url: Optional[HttpUrl] = None


class DocumentResponse(BaseModel):
    """Document Response Model"""
    doc_id: str
    name: str
    type: str
    indexed: bool
    created_at: str
    updated_at: str


class TestExecutionRequest(BaseModel):
    """Test Execution Request Model"""
    suite_id: str
    execution_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class TestExecutionResponse(BaseModel):
    """Test Execution Response Model"""
    execution_id: str
    suite_id: str
    status: TestStatus
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    duration_ms: float
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
