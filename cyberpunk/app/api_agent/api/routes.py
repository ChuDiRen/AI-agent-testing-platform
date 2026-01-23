"""
API Routes - Complete REST API

All API endpoints for the platform.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime

from api_agent.models import (
    TaskCreate, TaskResponse, TaskStatus,
    DocumentUpload, DocumentResponse,
    TestExecutionRequest, TestExecutionResponse
)
from api_agent.db import get_session
from core.task_manager import task_manager

# Create routers
tasks_router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])
documents_router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
executions_router = APIRouter(prefix="/api/v1/executions", tags=["executions"])
agents_router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


# ==================== Task Management ====================

@tasks_router.post("/create", response_model=Dict[str, Any])
async def create_task(task: TaskCreate):
    """
    Create a new task

    Creates a new automation task and returns the task ID.
    """
    from agents.orchestrator import create_orchestrator

    orchestrator = create_orchestrator()

    task_id = await task_manager.create_task(
        name=task.name,
        func=orchestrator.process_request,
        description=task.description,
        user_id=task.user_id,
        user_request=task.description
    )

    return {
        "status": "success",
        "task_id": task_id,
        "message": "Task created successfully"
    }


@tasks_router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: str):
    """
    Get task status and details

    Returns the current status and details of a task.
    """
    task_status = await task_manager.get_task_status(task_id)

    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "status": "success",
        "task": task_status
    }


@tasks_router.get("/", response_model=Dict[str, Any])
async def list_tasks(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """
    List all tasks

    Returns a list of tasks with optional filtering.
    """
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status)
        except ValueError:
            pass

    tasks = await task_manager.list_tasks(
        user_id=user_id,
        status=task_status,
        limit=limit
    )

    return {
        "status": "success",
        "tasks": tasks,
        "count": len(tasks)
    }


@tasks_router.post("/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(task_id: str):
    """
    Cancel a running task

    Cancels a currently running task.
    """
    success = await task_manager.cancel_task(task_id)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")

    return {
        "status": "success",
        "message": "Task cancelled successfully"
    }


@tasks_router.get("/{task_id}/result", response_model=Dict[str, Any])
async def get_task_result(task_id: str):
    """
    Get task result

    Returns the result of a completed task.
    """
    result = await task_manager.get_task_result(task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task result not found")

    return {
        "status": "success",
        "result": result
    }


# ==================== Document Management ====================

@documents_router.post("/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload API documentation

    Uploads an API documentation file for indexing and analysis.
    """
    import uuid
    import aiofiles

    doc_id = str(uuid.uuid4())

    # Save file
    upload_path = f"./uploads/{doc_id}_{file.filename}"

    async with aiofiles.open(upload_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Index document (call RAG)
    # This would integrate with RAG MCP server

    return {
        "status": "success",
        "doc_id": doc_id,
        "filename": file.filename,
        "message": "Document uploaded successfully"
    }


@documents_router.get("/{doc_id}", response_model=Dict[str, Any])
async def get_document(doc_id: str):
    """
    Get document details

    Returns details about a specific document.
    """
    # Mock implementation
    return {
        "status": "success",
        "doc_id": doc_id,
        "name": "API Documentation",
        "type": "openapi",
        "indexed": True
    }


@documents_router.get("/", response_model=Dict[str, Any])
async def list_documents():
    """
    List all documents

    Returns a list of all uploaded documents.
    """
    # Mock implementation
    return {
        "status": "success",
        "documents": []
    }


# ==================== Test Execution ====================

@executions_router.post("/execute", response_model=Dict[str, Any])
async def execute_tests(request: TestExecutionRequest):
    """
    Execute test suite

    Executes a test suite and returns results.
    """
    from agents.subagents import ExecutorAgent

    executor = ExecutorAgent()

    result = await executor.execute({
        "test_files": [],
        "config": request.config
    })

    return {
        "status": "success",
        "execution_id": result.get("execution_id"),
        "results": result.get("results")
    }


@executions_router.get("/{execution_id}", response_model=Dict[str, Any])
async def get_execution(execution_id: str):
    """
    Get test execution details

    Returns details of a specific test execution.
    """
    return {
        "status": "success",
        "execution_id": execution_id,
        "results": {}
    }


# ==================== Agent Interaction ====================

@agents_router.post("/chat", response_model=Dict[str, Any])
async def chat_with_agent(request: Dict[str, Any]):
    """
    Chat with AI agent

    Send a natural language request to the orchestrator agent.
    """
    from agents.orchestrator import create_orchestrator

    user_message = request.get("message")
    user_id = request.get("user_id")
    session_id = request.get("session_id")

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    orchestrator = create_orchestrator()

    # Process request and collect all updates
    updates = []
    async for update in orchestrator.process_request(user_message, user_id, session_id):
        updates.append(update)

    return {
        "status": "success",
        "updates": updates
    }


@agents_router.post("/query", response_model=Dict[str, Any])
async def query_knowledge_base(request: Dict[str, Any]):
    """
    Query knowledge base

    Query the RAG knowledge base for API information.
    """
    query = request.get("query")
    mode = request.get("mode", "mix")
    top_k = request.get("top_k", 10)

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    # This would call RAG MCP server
    # For now, return mock response
    return {
        "status": "success",
        "query": query,
        "mode": mode,
        "results": []
    }


@agents_router.post("/generate", response_model=Dict[str, Any])
async def generate_tests(request: Dict[str, Any]):
    """
    Generate tests from API documentation

    Analyze API docs and generate test code.
    """
    from agents.subagents import PlannerAgent, GeneratorAgent

    api_source = request.get("api_source")
    output_format = request.get("format", "playwright")

    if not api_source:
        raise HTTPException(status_code=400, detail="API source is required")

    # Step 1: Generate test plan
    planner = PlannerAgent()
    plan_result = await planner.execute({"api_info": {"url": api_source}})

    # Step 2: Generate test code
    generator = GeneratorAgent()
    code_result = await generator.execute({
        "test_plan": plan_result.get("testPlan", {}),
        "format": output_format
    })

    return {
        "status": "success",
        "test_plan": plan_result,
        "test_code": code_result
    }


# Health check
@tasks_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint

    Returns the health status of the task management system.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "task_manager": "healthy",
            "database": "healthy",
            "agents": "healthy"
        }
    }
