# Copyright (c) 2025 左岚. All rights reserved.
"""
浏览器自动化测试服务
"""
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, desc
import asyncio

from ..models.browser_test import (
    BrowserTestSuite, BrowserTestCase, BrowserTestExecution,
    BrowserTestStep, BrowserTestEnvironment
)
from ..engine.browser.browser_engine import BrowserEngine


class BrowserTestService:
    """浏览器自动化测试服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 测试套件管理 ==========

    async def create_suite(
        self,
        name: str,
        description: str,
        browser_type: str = 'chrome',
        browser_version: str = None,
        headless: bool = True,
        window_size: str = '1920x1080',
        timeout: int = 30,
        retry_count: int = 0,
        parallel_execution: bool = False,
        max_parallel: int = 3,
        environment: Dict = None,
        capabilities: Dict = None,
        tags: str = None,
        created_by: int
    ) -> BrowserTestSuite:
        """创建测试套件"""
        suite = BrowserTestSuite(
            name=name,
            description=description,
            browser_type=browser_type,
            browser_version=browser_version,
            headless=headless,
            window_size=window_size,
            timeout=timeout,
            retry_count=retry_count,
            parallel_execution=parallel_execution,
            max_parallel=max_parallel,
            environment=environment or {},
            capabilities=capabilities or {},
            tags=tags,
            created_by=created_by
        )

        self.db.add(suite)
        await self.db.commit()
        await self.db.refresh(suite)
        return suite

    async def get_suite(self, suite_id: int) -> Optional[BrowserTestSuite]:
        """获取测试套件"""
        result = await self.db.execute(
            select(BrowserTestSuite).where(BrowserTestSuite.suite_id == suite_id)
        )
        return result.scalar_one_or_none()

    async def get_suites(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = None,
        status: str = None,
        created_by: int = None
    ) -> Tuple[List[BrowserTestSuite], int]:
        """获取测试套件列表"""
        query = select(BrowserTestSuite)

        # 构建条件
        if keyword:
            query = query.where(
                (BrowserTestSuite.name.like(f"%{keyword}%")) |
                (BrowserTestSuite.description.like(f"%{keyword}%"))
            )
        if status:
            query = query.where(BrowserTestSuite.status == status)
        if created_by:
            query = query.where(BrowserTestSuite.created_by == created_by)

        # 获取总数
        count_query = select(func.count(BrowserTestSuite.suite_id))
        if keyword:
            count_query = count_query.where(
                (BrowserTestSuite.name.like(f"%{keyword}%")) |
                (BrowserTestSuite.description.like(f"%{keyword}%"))
            )
        if status:
            count_query = count_query.where(BrowserTestSuite.status == status)
        if created_by:
            count_query = count_query.where(BrowserTestSuite.created_by == created_by)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 获取数据
        query = query.order_by(BrowserTestSuite.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        suites = list(result.scalars().all())

        return suites, total

    async def update_suite(self, suite_id: int, update_data: Dict) -> Optional[BrowserTestSuite]:
        """更新测试套件"""
        suite = await self.get_suite(suite_id)
        if not suite:
            return None

        for field, value in update_data.items():
            if hasattr(suite, field):
                setattr(suite, field, value)

        await self.db.commit()
        await self.db.refresh(suite)
        return suite

    async def delete_suite(self, suite_id: int) -> bool:
        """删除测试套件"""
        result = await self.db.execute(
            delete(BrowserTestSuite).where(BrowserTestSuite.suite_id == suite_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    # ========== 测试用例管理 ==========

    async def create_case(
        self,
        suite_id: int,
        name: str,
        description: str,
        test_steps: List[Dict],
        test_data: Dict = None,
        assertions: Dict = None,
        priority: str = 'P2',
        timeout: int = None,
        retry_count: int = None,
        tags: str = None,
        sort_order: int = 0,
        created_by: int
    ) -> BrowserTestCase:
        """创建测试用例"""
        case = BrowserTestCase(
            suite_id=suite_id,
            name=name,
            description=description,
            test_steps=test_steps,
            test_data=test_data or {},
            assertions=assertions or {},
            priority=priority,
            timeout=timeout,
            retry_count=retry_count,
            tags=tags,
            sort_order=sort_order,
            created_by=created_by
        )

        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        return case

    async def get_case(self, case_id: int) -> Optional[BrowserTestCase]:
        """获取测试用例"""
        result = await self.db.execute(
            select(BrowserTestCase).where(BrowserTestCase.case_id == case_id)
        )
        return result.scalar_one_or_none()

    async def get_cases_by_suite(self, suite_id: int) -> List[BrowserTestCase]:
        """获取套件下的测试用例"""
        result = await self.db.execute(
            select(BrowserTestCase)
            .where(BrowserTestCase.suite_id == suite_id)
            .where(BrowserTestCase.status == 'active')
            .order_by(BrowserTestCase.sort_order, BrowserTestCase.created_at)
        )
        return list(result.scalars().all())

    async def update_case(self, case_id: int, update_data: Dict) -> Optional[BrowserTestCase]:
        """更新测试用例"""
        case = await self.get_case(case_id)
        if not case:
            return None

        for field, value in update_data.items():
            if hasattr(case, field):
                setattr(case, field, value)

        await self.db.commit()
        await self.db.refresh(case)
        return case

    async def delete_case(self, case_id: int) -> bool:
        """删除测试用例"""
        result = await self.db.execute(
            delete(BrowserTestCase).where(BrowserTestCase.case_id == case_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    # ========== 测试执行管理 ==========

    async def execute_case(
        self,
        case_id: int,
        execution_context: Dict = None,
        environment_id: int = None,
        executed_by: int = 1
    ) -> Dict:
        """执行浏览器测试用例"""
        case = await self.get_case(case_id)
        if not case:
            raise ValueError("测试用例不存在")

        suite = await self.get_suite(case.suite_id)
        if not suite:
            raise ValueError("测试套件不存在")

        # 获取环境配置
        environment_config = {}
        if environment_id:
            environment = await self.get_environment(environment_id)
            if environment:
                environment_config = {
                    "base_url": environment.base_url,
                    "proxy_config": environment.proxy_config,
                    "network_conditions": environment.network_conditions,
                    "variables": environment.variables or {}
                }

        # 合并执行上下文
        context = {
            **(execution_context or {}),
            **environment_config,
            "test_data": case.test_data or {}
        }

        # 创建执行记录
        execution = BrowserTestExecution(
            case_id=case_id,
            suite_id=case.suite_id,
            status='pending',
            executed_by=executed_by
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        try:
            # 配置浏览器引擎
            browser_config = {
                "browser_type": suite.browser_type,
                "browser_version": suite.browser_version,
                "headless": suite.headless,
                "window_size": suite.window_size,
                "timeout": case.timeout or suite.timeout,
                "screenshot_dir": f"screenshots/browser/{execution.execution_id}",
                "capabilities": suite.capabilities or {}
            }

            # 执行测试
            engine = BrowserEngine(browser_config)
            if not engine.setup_driver():
                raise RuntimeError("浏览器驱动初始化失败")

            # 执行测试步骤
            step_results = engine.execute_test_steps(case.test_steps, context)

            # 更新执行记录
            execution.status = 'success' if all(r["status"] == "success" for r in step_results["step_results"]) else 'failed'
            execution.result = step_results
            execution.logs = "\n".join(step_results["logs"])
            execution.screenshots = step_results["screenshots"]
            execution.duration = step_results["total_duration"] * 1000  # 转换为毫秒
            execution.steps_total = step_results["total_steps"]
            execution.steps_passed = sum(1 for r in step_results["step_results"] if r["status"] == "success")
            execution.steps_failed = step_results["total_steps"] - execution.steps_passed
            execution.step_results = step_results["step_results"]
            execution.browser_info = engine.get_session_info()
            execution.environment_info = environment_config
            execution.start_time = datetime.now()

            engine.quit()

        except Exception as e:
            execution.status = 'error'
            execution.error_message = str(e)
            execution.logs = "\n".join(engine.logs) if hasattr(engine, 'logs') else str(e)
            if hasattr(engine, 'quit'):
                engine.quit()

        finally:
            execution.end_time = datetime.now()
            execution.finished_at = datetime.now()
            await self.db.commit()

        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "duration": execution.duration,
            "steps_total": execution.steps_total,
            "steps_passed": execution.steps_passed,
            "steps_failed": execution.steps_failed,
            "result": execution.result
        }

    async def get_execution(self, execution_id: int) -> Optional[BrowserTestExecution]:
        """获取执行记录"""
        result = await self.db.execute(
            select(BrowserTestExecution).where(BrowserTestExecution.execution_id == execution_id)
        )
        return result.scalar_one_or_none()

    async def get_executions(
        self,
        page: int = 1,
        page_size: int = 20,
        case_id: int = None,
        suite_id: int = None,
        status: str = None,
        executed_by: int = None
    ) -> Tuple[List[BrowserTestExecution], int]:
        """获取执行记录列表"""
        query = select(BrowserTestExecution)

        # 构建条件
        if case_id:
            query = query.where(BrowserTestExecution.case_id == case_id)
        if suite_id:
            query = query.where(BrowserTestExecution.suite_id == suite_id)
        if status:
            query = query.where(BrowserTestExecution.status == status)
        if executed_by:
            query = query.where(BrowserTestExecution.executed_by == executed_by)

        # 获取总数
        count_query = select(func.count(BrowserTestExecution.execution_id))
        if case_id:
            count_query = count_query.where(BrowserTestExecution.case_id == case_id)
        if suite_id:
            count_query = count_query.where(BrowserTestExecution.suite_id == suite_id)
        if status:
            count_query = count_query.where(BrowserTestExecution.status == status)
        if executed_by:
            count_query = count_query.where(BrowserTestExecution.executed_by == executed_by)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 获取数据
        query = query.order_by(BrowserTestExecution.executed_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        executions = list(result.scalars().all())

        return executions, total

    async def delete_execution(self, execution_id: int) -> bool:
        """删除执行记录"""
        result = await self.db.execute(
            delete(BrowserTestExecution).where(BrowserTestExecution.execution_id == execution_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    # ========== 环境管理 ==========

    async def create_environment(
        self,
        name: str,
        description: str,
        base_url: str = None,
        proxy_config: Dict = None,
        network_conditions: Dict = None,
        browser_config: Dict = None,
        capabilities: Dict = None,
        test_data_config: Dict = None,
        variables: Dict = None,
        is_default: bool = False,
        created_by: int
    ) -> BrowserTestEnvironment:
        """创建测试环境"""
        environment = BrowserTestEnvironment(
            name=name,
            description=description,
            base_url=base_url,
            proxy_config=proxy_config or {},
            network_conditions=network_conditions or {},
            browser_config=browser_config or {},
            capabilities=capabilities or {},
            test_data_config=test_data_config or {},
            variables=variables or {},
            is_default=is_default,
            created_by=created_by
        )

        self.db.add(environment)
        await self.db.commit()
        await self.db.refresh(environment)
        return environment

    async def get_environment(self, env_id: int) -> Optional[BrowserTestEnvironment]:
        """获取测试环境"""
        result = await self.db.execute(
            select(BrowserTestEnvironment).where(BrowserTestEnvironment.env_id == env_id)
        )
        return result.scalar_one_or_none()

    async def get_environments(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = None,
        is_active: bool = True
    ) -> Tuple[List[BrowserTestEnvironment], int]:
        """获取测试环境列表"""
        query = select(BrowserTestEnvironment).where(BrowserTestEnvironment.is_active == is_active)

        if keyword:
            query = query.where(
                (BrowserTestEnvironment.name.like(f"%{keyword}%")) |
                (BrowserTestEnvironment.description.like(f"%{keyword}%"))
            )

        # 获取总数
        count_query = select(func.count(BrowserTestEnvironment.env_id)).where(
            BrowserTestEnvironment.is_active == is_active
        )
        if keyword:
            count_query = count_query.where(
                (BrowserTestEnvironment.name.like(f"%{keyword}%")) |
                (BrowserTestEnvironment.description.like(f"%{keyword}%"))
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 获取数据
        query = query.order_by(BrowserTestEnvironment.is_default.desc(), BrowserTestEnvironment.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        environments = list(result.scalars().all())

        return environments, total

    async def get_default_environment(self) -> Optional[BrowserTestEnvironment]:
        """获取默认环境"""
        result = await self.db.execute(
            select(BrowserTestEnvironment)
            .where(BrowserTestEnvironment.is_default == True)
            .where(BrowserTestEnvironment.is_active == True)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_environment(self, env_id: int, update_data: Dict) -> Optional[BrowserTestEnvironment]:
        """更新测试环境"""
        environment = await self.get_environment(env_id)
        if not environment:
            return None

        for field, value in update_data.items():
            if hasattr(environment, field):
                setattr(environment, field, value)

        await self.db.commit()
        await self.db.refresh(environment)
        return environment

    async def delete_environment(self, env_id: int) -> bool:
        """删除测试环境"""
        result = await self.db.execute(
            delete(BrowserTestEnvironment).where(BrowserTestEnvironment.env_id == env_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    # ========== 统计分析 ==========

    async def get_suite_statistics(self, suite_id: int) -> Dict:
        """获取套件统计信息"""
        # 统计用例数量
        case_result = await self.db.execute(
            select(
                func.count(BrowserTestCase.case_id).label('total_cases'),
                func.sum(func.case([(BrowserTestCase.status == 'active', 1)], else_=0)).label('active_cases')
            ).where(BrowserTestCase.suite_id == suite_id)
        )
        case_stats = case_result.first()

        # 统计执行记录
        execution_result = await self.db.execute(
            select(
                func.count(BrowserTestExecution.execution_id).label('total_executions'),
                func.sum(func.case([(BrowserTestExecution.status == 'success', 1)], else_=0)).label('success_executions'),
                func.sum(func.case([(BrowserTestExecution.status == 'failed', 1)], else_=0)).label('failed_executions'),
                func.sum(func.case([(BrowserTestExecution.status == 'error', 1)], else_=0)).label('error_executions'),
                func.avg(BrowserTestExecution.duration).label('avg_duration')
            ).where(BrowserTestExecution.suite_id == suite_id)
        )
        execution_stats = execution_result.first()

        return {
            "total_cases": case_stats.total_cases or 0,
            "active_cases": case_stats.active_cases or 0,
            "total_executions": execution_stats.total_executions or 0,
            "success_executions": execution_stats.success_executions or 0,
            "failed_executions": execution_stats.failed_executions or 0,
            "error_executions": execution_stats.error_executions or 0,
            "success_rate": (execution_stats.success_executions / execution_stats.total_executions * 100) if execution_stats.total_executions else 0,
            "average_duration": execution_stats.avg_duration or 0
        }

    async def get_case_execution_history(
        self,
        case_id: int,
        limit: int = 10
    ) -> List[BrowserTestExecution]:
        """获取用例执行历史"""
        result = await self.db.execute(
            select(BrowserTestExecution)
            .where(BrowserTestExecution.case_id == case_id)
            .order_by(BrowserTestExecution.executed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_executions(
        self,
        limit: int = 20,
        executed_by: int = None
    ) -> List[BrowserTestExecution]:
        """获取最近的执行记录"""
        query = select(BrowserTestExecution).order_by(BrowserTestExecution.executed_at.desc())

        if executed_by:
            query = query.where(BrowserTestExecution.executed_by == executed_by)

        result = await self.db.execute(query.limit(limit))
        return list(result.scalars().all())