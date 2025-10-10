# Copyright (c) 2025 左岚. All rights reserved.
"""
浏览器自动化测试API路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams

from ..services.browser_test_service import BrowserTestService
from ..models.browser_test import BrowserTestSuite, BrowserTestCase, BrowserTestExecution, BrowserTestEnvironment

router = APIRouter()


# ========== 测试套件管理 ==========

@router.post("/suites", response_model=APIResponse[Dict])
async def create_suite(
    suite_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试套件"""
    service = BrowserTestService(db)

    try:
        suite = await service.create_suite(
            name=suite_data["name"],
            description=suite_data.get("description", ""),
            browser_type=suite_data.get("browser_type", "chrome"),
            browser_version=suite_data.get("browser_version"),
            headless=suite_data.get("headless", True),
            window_size=suite_data.get("window_size", "1920x1080"),
            timeout=suite_data.get("timeout", 30),
            retry_count=suite_data.get("retry_count", 0),
            parallel_execution=suite_data.get("parallel_execution", False),
            max_parallel=suite_data.get("max_parallel", 3),
            environment=suite_data.get("environment"),
            capabilities=suite_data.get("capabilities"),
            tags=suite_data.get("tags"),
            created_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="测试套件创建成功",
            data={"suite_id": suite.suite_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"创建失败: {str(e)}"
        )


@router.get("/suites", response_model=APIResponse[PaginatedResponse])
async def get_suites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试套件列表"""
    service = BrowserTestService(db)

    try:
        suites, total = await service.get_suites(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
            created_by=current_user.user_id
        )

        paginated_data = PaginatedResponse.create(
            items=[
                {
                    "suite_id": suite.suite_id,
                    "name": suite.name,
                    "description": suite.description,
                    "browser_type": suite.browser_type,
                    "browser_version": suite.browser_version,
                    "headless": suite.headless,
                    "window_size": suite.window_size,
                    "status": suite.status,
                    "tags": suite.tags,
                    "created_at": suite.created_at.isoformat(),
                    "updated_at": suite.updated_at.isoformat()
                }
                for suite in suites
            ],
            total=total,
            page=page,
            page_size=page_size
        )

        return APIResponse(
            success=True,
            data=paginated_data
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/suites/{suite_id}", response_model=APIResponse[Dict])
async def get_suite_detail(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试套件详情"""
    service = BrowserTestService(db)

    try:
        suite = await service.get_suite(suite_id)
        if not suite:
            return APIResponse(
                success=False,
                message="测试套件不存在"
            )

        # 获取套件统计信息
        statistics = await service.get_suite_statistics(suite_id)

        return APIResponse(
            success=True,
            data={
                "suite_id": suite.suite_id,
                "name": suite.name,
                "description": suite.description,
                "browser_type": suite.browser_type,
                "browser_version": suite.browser_version,
                "headless": suite.headless,
                "window_size": suite.window_size,
                "timeout": suite.timeout,
                "retry_count": suite.retry_count,
                "parallel_execution": suite.parallel_execution,
                "max_parallel": suite.max_parallel,
                "environment": suite.environment,
                "capabilities": suite.capabilities,
                "status": suite.status,
                "tags": suite.tags,
                "created_at": suite.created_at.isoformat(),
                "updated_at": suite.updated_at.isoformat(),
                "statistics": statistics
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.put("/suites/{suite_id}", response_model=APIResponse[Dict])
async def update_suite(
    suite_id: int,
    update_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新测试套件"""
    service = BrowserTestService(db)

    try:
        suite = await service.update_suite(suite_id, update_data)
        if not suite:
            return APIResponse(
                success=False,
                message="测试套件不存在"
            )

        return APIResponse(
            success=True,
            message="更新成功",
            data={"suite_id": suite.suite_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"更新失败: {str(e)}"
        )


@router.delete("/suites/{suite_id}", response_model=APIResponse[Dict])
async def delete_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除测试套件"""
    service = BrowserTestService(db)

    try:
        success = await service.delete_suite(suite_id)
        if not success:
            return APIResponse(
                success=False,
                message="测试套件不存在"
            )

        return APIResponse(
            success=True,
            message="删除成功"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"删除失败: {str(e)}"
        )


# ========== 测试用例管理 ==========

@router.post("/cases", response_model=APIResponse[Dict])
async def create_case(
    case_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试用例"""
    service = BrowserTestService(db)

    try:
        case = await service.create_case(
            suite_id=case_data["suite_id"],
            name=case_data["name"],
            description=case_data.get("description", ""),
            test_steps=case_data["test_steps"],
            test_data=case_data.get("test_data"),
            assertions=case_data.get("assertions"),
            priority=case_data.get("priority", "P2"),
            timeout=case_data.get("timeout"),
            retry_count=case_data.get("retry_count"),
            tags=case_data.get("tags"),
            sort_order=case_data.get("sort_order", 0),
            created_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="测试用例创建成功",
            data={"case_id": case.case_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"创建失败: {str(e)}"
        )


@router.get("/cases", response_model=APIResponse[List[Dict]])
async def get_cases_by_suite(
    suite_id: int = Query(..., description="套件ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取套件下的测试用例列表"""
    service = BrowserTestService(db)

    try:
        cases = await service.get_cases_by_suite(suite_id)
        return APIResponse(
            success=True,
            data=[
                {
                    "case_id": case.case_id,
                    "suite_id": case.suite_id,
                    "name": case.name,
                    "description": case.description,
                    "priority": case.priority,
                    "status": case.status,
                    "tags": case.tags,
                    "test_steps_count": len(case.test_steps or []),
                    "created_at": case.created_at.isoformat(),
                    "updated_at": case.updated_at.isoformat()
                }
                for case in cases
            ]
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/cases/{case_id}", response_model=APIResponse[Dict])
async def get_case_detail(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试用例详情"""
    service = BrowserTestService(db)

    try:
        case = await service.get_case(case_id)
        if not case:
            return APIResponse(
                success=False,
                message="测试用例不存在"
            )

        # 获取执行历史
        execution_history = await service.get_case_execution_history(case_id)

        return APIResponse(
            success=True,
            data={
                "case_id": case.case_id,
                "suite_id": case.suite_id,
                "name": case.name,
                "description": case.description,
                "test_steps": case.test_steps,
                "test_data": case.test_data,
                "assertions": case.assertions,
                "priority": case.priority,
                "timeout": case.timeout,
                "retry_count": case.retry_count,
                "status": case.status,
                "tags": case.tags,
                "sort_order": case.sort_order,
                "created_at": case.created_at.isoformat(),
                "updated_at": case.updated_at.isoformat(),
                "execution_history": [
                    {
                        "execution_id": exec.execution_id,
                        "status": exec.status,
                        "duration": exec.duration,
                        "steps_total": exec.steps_total,
                        "steps_passed": exec.steps_passed,
                        "steps_failed": exec.steps_failed,
                        "executed_at": exec.executed_at.isoformat() if exec.executed_at else None,
                        "error_message": exec.error_message
                    }
                    for exec in execution_history
                ]
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.put("/cases/{case_id}", response_model=APIResponse[Dict])
async def update_case(
    case_id: int,
    update_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新测试用例"""
    service = BrowserTestService(db)

    try:
        case = await service.update_case(case_id, update_data)
        if not case:
            return APIResponse(
                success=False,
                message="测试用例不存在"
            )

        return APIResponse(
            success=True,
            message="更新成功",
            data={"case_id": case.case_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"更新失败: {str(e)}"
        )


@router.delete("/cases/{case_id}", response_model=APIResponse[Dict])
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除测试用例"""
    service = BrowserTestService(db)

    try:
        success = await service.delete_case(case_id)
        if not success:
            return APIResponse(
                success=False,
                message="测试用例不存在"
            )

        return APIResponse(
            success=True,
            message="删除成功"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"删除失败: {str(e)}"
        )


# ========== 测试执行管理 ==========

@router.post("/cases/{case_id}/execute", response_model=APIResponse[Dict])
async def execute_case(
    case_id: int,
    execute_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行浏览器测试用例"""
    service = BrowserTestService(db)

    try:
        result = await service.execute_case(
            case_id=case_id,
            execution_context=execute_data.get("context"),
            environment_id=execute_data.get("environment_id"),
            executed_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="测试执行已启动",
            data=result
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"执行失败: {str(e)}"
        )


@router.get("/executions", response_model=APIResponse[PaginatedResponse])
async def get_executions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    case_id: Optional[int] = Query(None, description="用例ID"),
    suite_id: Optional[int] = Query(None, description="套件ID"),
    status: Optional[str] = Query(None, description="执行状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录列表"""
    service = BrowserTestService(db)

    try:
        executions, total = await service.get_executions(
            page=page,
            page_size=page_size,
            case_id=case_id,
            suite_id=suite_id,
            status=status,
            executed_by=current_user.user_id
        )

        paginated_data = PaginatedResponse.create(
            items=[
                {
                    "execution_id": exec.execution_id,
                    "case_id": exec.case_id,
                    "suite_id": exec.suite_id,
                    "status": exec.status,
                    "duration": exec.duration,
                    "steps_total": exec.steps_total,
                    "steps_passed": exec.steps_passed,
                    "steps_failed": exec.steps_failed,
                    "error_message": exec.error_message,
                    "executed_at": exec.executed_at.isoformat() if exec.executed_at else None,
                    "finished_at": exec.finished_at.isoformat() if exec.finished_at else None
                }
                for exec in executions
            ],
            total=total,
            page=page,
            page_size=page_size
        )

        return APIResponse(
            success=True,
            data=paginated_data
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/executions/{execution_id}", response_model=APIResponse[Dict])
async def get_execution_detail(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录详情"""
    service = BrowserTestService(db)

    try:
        execution = await service.get_execution(execution_id)
        if not execution:
            return APIResponse(
                success=False,
                message="执行记录不存在"
            )

        return APIResponse(
            success=True,
            data={
                "execution_id": execution.execution_id,
                "case_id": execution.case_id,
                "suite_id": execution.suite_id,
                "status": execution.status,
                "result": execution.result,
                "logs": execution.logs,
                "error_message": execution.error_message,
                "screenshots": execution.screenshots,
                "duration": execution.duration,
                "steps_total": execution.steps_total,
                "steps_passed": execution.steps_passed,
                "steps_failed": execution.steps_failed,
                "step_results": execution.step_results,
                "browser_info": execution.browser_info,
                "environment_info": execution.environment_info,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "executed_at": execution.executed_at.isoformat() if execution.executed_at else None,
                "finished_at": execution.finished_at.isoformat() if execution.finished_at else None
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.delete("/executions/{execution_id}", response_model=APIResponse[Dict])
async def delete_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除执行记录"""
    service = BrowserTestService(db)

    try:
        success = await service.delete_execution(execution_id)
        if not success:
            return APIResponse(
                success=False,
                message="执行记录不存在"
            )

        return APIResponse(
            success=True,
            message="删除成功"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"删除失败: {str(e)}"
        )


# ========== 环境管理 ==========

@router.post("/environments", response_model=APIResponse[Dict])
async def create_environment(
    env_data: Dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试环境"""
    service = BrowserTestService(db)

    try:
        environment = await service.create_environment(
            name=env_data["name"],
            description=env_data.get("description", ""),
            base_url=env_data.get("base_url"),
            proxy_config=env_data.get("proxy_config"),
            network_conditions=env_data.get("network_conditions"),
            browser_config=env_data.get("browser_config"),
            capabilities=env_data.get("capabilities"),
            test_data_config=env_data.get("test_data_config"),
            variables=env_data.get("variables"),
            is_default=env_data.get("is_default", False),
            created_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="测试环境创建成功",
            data={"env_id": environment.env_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"创建失败: {str(e)}"
        )


@router.get("/environments", response_model=APIResponse[List[Dict]])
async def get_environments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: bool = Query(True, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试环境列表"""
    service = BrowserTestService(db)

    try:
        environments, total = await service.get_environments(
            page=page,
            page_size=page_size,
            keyword=keyword,
            is_active=is_active
        )

        return APIResponse(
            success=True,
            data=[
                {
                    "env_id": env.env_id,
                    "name": env.name,
                    "description": env.description,
                    "base_url": env.base_url,
                    "is_default": env.is_default,
                    "is_active": env.is_active,
                    "created_at": env.created_at.isoformat(),
                    "updated_at": env.updated_at.isoformat()
                }
                for env in environments
            ]
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/environments/default", response_model=APIResponse[Dict])
async def get_default_environment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取默认测试环境"""
    service = BrowserTestService(db)

    try:
        environment = await service.get_default_environment()
        if not environment:
            return APIResponse(
                success=False,
                message="默认环境不存在"
            )

        return APIResponse(
            success=True,
            data={
                "env_id": environment.env_id,
                "name": environment.name,
                "description": environment.description,
                "base_url": environment.base_url,
                "proxy_config": environment.proxy_config,
                "network_conditions": environment.network_conditions,
                "browser_config": environment.browser_config,
                "capabilities": environment.capabilities,
                "test_data_config": environment.test_data_config,
                "variables": environment.variables,
                "is_default": environment.is_default,
                "is_active": environment.is_active,
                "created_at": environment.created_at.isoformat(),
                "updated_at": environment.updated_at.isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/environments/{env_id}", response_model=APIResponse[Dict])
async def get_environment_detail(
    env_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试环境详情"""
    service = BrowserTestService(db)

    try:
        environment = await service.get_environment(env_id)
        if not environment:
            return APIResponse(
                success=False,
                message="测试环境不存在"
            )

        return APIResponse(
            success=True,
            data={
                "env_id": environment.env_id,
                "name": environment.name,
                "description": environment.description,
                "base_url": environment.base_url,
                "proxy_config": environment.proxy_config,
                "network_conditions": environment.network_conditions,
                "browser_config": environment.browser_config,
                "capabilities": environment.capabilities,
                "test_data_config": environment.test_data_config,
                "variables": environment.variables,
                "is_default": environment.is_default,
                "is_active": environment.is_active,
                "created_at": environment.created_at.isoformat(),
                "updated_at": environment.updated_at.isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/statistics/recent", response_model=APIResponse[Dict])
async def get_recent_statistics(
    limit: int = Query(10, ge=1, le=100, description="数量限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取最近执行统计"""
    service = BrowserTestService(db)

    try:
        recent_executions = await service.get_recent_executions(
            limit=limit,
            executed_by=current_user.user_id
        )

        # 统计信息
        total_executions = len(recent_executions)
        success_count = sum(1 for exec in recent_executions if exec.status == 'success')
        failed_count = sum(1 for exec in recent_executions if exec.status in ['failed', 'error'])
        success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0

        # 平均执行时间
        avg_duration = 0
        if recent_executions:
            durations = [exec.duration for exec in recent_executions if exec.duration]
            if durations:
                avg_duration = sum(durations) / len(durations)

        return APIResponse(
            success=True,
            data={
                "total_executions": total_executions,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": round(success_rate, 2),
                "average_duration": round(avg_duration, 2),
                "recent_executions": [
                    {
                        "execution_id": exec.execution_id,
                        "case_id": exec.case_id,
                        "suite_id": exec.suite_id,
                        "status": exec.status,
                        "duration": exec.duration,
                        "steps_total": exec.steps_total,
                        "steps_passed": exec.steps_passed,
                        "executed_at": exec.executed_at.isoformat() if exec.executed_at else None
                    }
                    for exec in recent_executions
                ]
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


# ========== 测试步骤模板 ==========

@router.get("/templates/steps", response_model=APIResponse[List[Dict]])
async def get_step_templates():
    """获取测试步骤模板"""
    templates = [
        {
            "name": "打开页面",
            "description": "导航到指定URL",
            "step_type": "navigate",
            "action_template": {
                "url": "${base_url}/login"
            },
            "validation_template": {
                "type": "title_contains",
                "expected_value": "登录页面",
                "enabled": True
            },
            "category": "navigation",
            "tags": ["页面导航"]
        },
        {
            "name": "点击元素",
            "description": "点击指定元素",
            "step_type": "click",
            "action_template": {
                "locator": {"type": "css", "value": "button.submit"},
                "timeout": 10
            },
            "validation_template": {
                "type": "element_exists",
                "locator": {"type": "css", "value": ".success-message"},
                "enabled": True
            },
            "category": "interaction",
            "tags": ["点击", "交互"]
        },
        {
            "name": "输入文本",
            "description": "在输入框中输入文本",
            "step_type": "input",
            "action_template": {
                "locator": {"type": "css", "value": "input[name='username']"},
                "text": "${username}",
                "clear_first": True
            },
            "validation_template": {
                "type": "element_value",
                "locator": {"type": "css", "value": "input[name='username']"},
                "expected_value": "${username}",
                "enabled": True
            },
            "category": "input",
            "tags": ["输入", "文本"]
        },
        {
            "name": "等待元素出现",
            "description": "等待指定元素出现在页面上",
            "step_type": "wait",
            "action_template": {
                "wait_type": "element_visible",
                "locator": {"type": "css", "value": ".loading-complete"},
                "timeout": 30
            },
            "validation_template": None,
            "category": "wait",
            "tags": ["等待", "元素"]
        },
        {
            "name": "验证元素存在",
            "description": "验证指定元素存在于页面中",
            "step_type": "validate",
            "action_template": {
                "validation_type": "element_exists",
                "locator": {"type": "css", "value": ".error-message"}
            },
            "validation_template": None,
            "category": "validation",
            "tags": ["验证", "断言"]
        },
        {
            "name": "验证文本内容",
            "description": "验证元素的文本内容",
            "step_type": "validate",
            "action_template": {
                "validation_type": "text_contains",
                "locator": {"type": "css", "value": ".welcome-message"},
                "expected_value": "欢迎"
            },
            "validation_template": None,
            "category": "validation",
            "tags": ["验证", "文本"]
        },
        {
            "name": "截图",
            "description": "截取当前页面截图",
            "step_type": "screenshot",
            "action_template": {
                "filename": "step_screenshot.png",
                "full_page": False
            },
            "validation_template": None,
            "category": "utility",
            "tags": ["截图", "调试"]
        },
        {
            "name": "执行JavaScript",
            "description": "执行自定义JavaScript代码",
            "step_type": "execute_script",
            "action_template": {
                "script": "window.scrollTo(0, document.body.scrollHeight);"
            },
            "validation_template": None,
            "category": "script",
            "tags": ["JavaScript", "脚本"]
        },
        {
            "name": "选择下拉框选项",
            "description": "在下拉框中选择指定选项",
            "step_type": "select_option",
            "action_template": {
                "locator": {"type": "css", "value": "select[name='country']"},
                "values": ["中国"]
            },
            "validation_template": {
                "type": "element_value",
                "locator": {"type": "css", "value": "select[name='country']"},
                "expected_value": "中国",
                "enabled": True
            },
            "category": "interaction",
            "tags": ["选择", "下拉框"]
        },
        {
            "name": "悬停元素",
            "description": "鼠标悬停在指定元素上",
            "step_type": "hover",
            "action_template": {
                "locator": {"type": "css", "value": ".menu-item"}
            },
            "validation_template": {
                "type": "element_exists",
                "locator": {"type": "css", "value": ".submenu"},
                "enabled": True
            },
            "category": "interaction",
            "tags": ["悬停", "鼠标"]
        }
    ]

    return APIResponse(
        success=True,
        data=templates
    )


@router.get("/templates/locators", response_model=APIResponse[List[Dict]])
async def get_locator_templates():
    """获取元素定位器模板"""
    templates = [
        {
            "type": "css",
            "description": "CSS选择器",
            "examples": [
                "#submit-button",
                ".error-message",
                "input[name='username']",
                "div.container > p.text"
            ]
        },
        {
            "type": "xpath",
            "description": "XPath表达式",
            "examples": [
                "//button[@id='submit']",
                "//div[contains(@class, 'error')]",
                "//input[@name='username' and @type='text']",
                "//table//tr[1]//td[2]"
            ]
        },
        {
            "type": "id",
            "description": "元素ID",
            "examples": [
                "username",
                "password",
                "submit-button"
            ]
        },
        {
            "type": "name",
            "description": "元素名称",
            "examples": [
                "username",
                "email",
                "login-form"
            ]
        },
        {
            "type": "class",
            "description": "CSS类名",
            "examples": [
                "btn btn-primary",
                "form-control",
                "error-message"
            ]
        },
        {
            "type": "tag",
            "description": "HTML标签",
            "examples": [
                "button",
                "input",
                "div",
                "span"
            ]
        },
        {
            "type": "link_text",
            "description": "链接文本",
            "examples": [
                "登录",
                "注册",
                "忘记密码"
            ]
        },
        {
            "type": "partial_link_text",
            "description": "部分链接文本",
            "examples": [
                "登",
                "注",
                "忘记"
            ]
        }
    ]

    return APIResponse(
        success=True,
        data=templates
    )