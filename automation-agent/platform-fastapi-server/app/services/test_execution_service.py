"""
测试用例执行服务
从 Flask 迁移到 FastAPI
"""
import asyncio
import json
import uuid
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.logger import logger
from app.models.api_info import ApiInfo
from app.models.api_info_case import ApiInfoCase
from app.models.api_info_case_step import ApiInfoCaseStep
from app.core.config import settings


class TestExecutionService:
    """测试用例执行服务"""
    
    def __init__(self):
        self.execution_history = {}
    
    async def execute_test_case(
        self, 
        test_case_id: int,
        db: AsyncSession,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行单个测试用例"""
        try:
            # 获取测试用例信息
            result = await db.execute(select(ApiInfoCase).where(ApiInfoCase.id == test_case_id))
            test_case = result.scalars().first()
            
            if not test_case:
                raise ValueError(f"测试用例不存在: {test_case_id}")
            
            # 获取测试用例步骤
            steps_result = await db.execute(
                select(ApiInfoCaseStep).where(ApiInfoCaseStep.api_case_info_id == test_case_id)
            )
            steps = steps_result.scalars().all()
            
            # 创建执行上下文
            execution_context = {
                "execution_id": str(uuid.uuid4()),
                "test_case_id": test_case_id,
                "test_case_name": test_case.case_name,
                "start_time": datetime.utcnow().isoformat(),
                "variables": variables or {},
                "steps": [],
                "status": "running"
            }
            
            # 执行每个步骤
            for step in steps:
                step_result = await self._execute_step(step, execution_context)
                execution_context["steps"].append(step_result)
                
                # 如果步骤失败，停止执行
                if step_result.get("status") == "failed":
                    execution_context["status"] = "failed"
                    break
            
            # 更新执行状态
            if execution_context["status"] == "running":
                execution_context["status"] = "completed"
            
            execution_context["end_time"] = datetime.utcnow().isoformat()
            
            # 保存执行历史
            self.execution_history[execution_context["execution_id"]] = execution_context
            
            logger.info(f"测试用例执行完成: {test_case_id}")
            return execution_context
            
        except Exception as e:
            logger.error(f"测试用例执行失败: {e}")
            raise
    
    async def execute_test_suite(
        self, 
        test_suite_ids: List[int],
        db: AsyncSession,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行测试套件"""
        try:
            suite_execution_id = str(uuid.uuid4())
            execution_results = []
            total_cases = len(test_suite_ids)
            passed_cases = 0
            failed_cases = 0
            
            suite_context = {
                "suite_execution_id": suite_execution_id,
                "start_time": datetime.utcnow().isoformat(),
                "total_cases": total_cases,
                "passed_cases": 0,
                "failed_cases": 0,
                "test_cases": [],
                "status": "running"
            }
            
            # 并行执行测试用例
            tasks = []
            for test_case_id in test_suite_ids:
                task = asyncio.create_task(
                    self.execute_test_case(test_case_id, db, variables)
                )
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理执行结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # 执行失败
                    execution_result = {
                        "test_case_id": test_suite_ids[i],
                        "status": "failed",
                        "error": str(result)
                    }
                    failed_cases += 1
                else:
                    # 执行成功
                    execution_result = result
                    if result.get("status") == "completed":
                        passed_cases += 1
                    else:
                        failed_cases += 1
                
                execution_results.append(execution_result)
            
            # 更新套件执行上下文
            suite_context["test_cases"] = execution_results
            suite_context["passed_cases"] = passed_cases
            suite_context["failed_cases"] = failed_cases
            suite_context["end_time"] = datetime.utcnow().isoformat()
            
            if suite_context["status"] == "running":
                suite_context["status"] = "completed"
            
            logger.info(f"测试套件执行完成: {suite_execution_id}")
            return suite_context
            
        except Exception as e:
            logger.error(f"测试套件执行失败: {e}")
            raise
    
    async def _execute_step(
        self, 
        step: ApiInfoCaseStep, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            step_start_time = datetime.utcnow().isoformat()
            
            # 获取步骤对应的 API 信息
            result = await self._get_api_info_for_step(step, context)
            if not result:
                return {
                    "step_id": step.id,
                    "step_name": step.step_desc,
                    "status": "failed",
                    "error": f"未找到对应的 API 信息: {step.key_word_id}",
                    "start_time": step_start_time,
                    "end_time": datetime.utcnow().isoformat()
                }
            
            api_info, api_result = result
            
            # 执行 API 请求
            request_result = await self._execute_api_request(api_info, context)
            
            step_end_time = datetime.utcnow().isoformat()
            
            return {
                "step_id": step.id,
                "step_name": step.step_desc,
                "api_info": {
                    "method": api_info.request_method,
                    "url": api_info.request_url
                },
                "request": request_result.get("request"),
                "response": request_result.get("response"),
                "status": request_result.get("status"),
                "start_time": step_start_time,
                "end_time": step_end_time,
                "duration_ms": request_result.get("duration_ms", 0)
            }
            
        except Exception as e:
            logger.error(f"步骤执行失败: {e}")
            return {
                "step_id": step.id,
                "step_name": step.step_desc,
                "status": "failed",
                "error": str(e),
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat()
            }
    
    async def _get_api_info_for_step(
        self, 
        step: ApiInfoCaseStep, 
        context: Dict[str, Any]
    ) -> Optional[tuple]:
        """获取步骤对应的 API 信息"""
        try:
            # 这里需要根据实际的数据库结构来实现
            # 例如通过关键字 ID 查找对应的 API 信息
            # 或者通过其他关联字段
            
            # 模拟返回 API 信息
            api_info = type('ApiInfo', (), {
                'request_method': 'GET',
                'request_url': '/api/test',
                'request_params': '{}',
                'request_headers': '{}',
                'requests_json_data': '{}'
            })()
            
            return api_info, None
            
        except Exception as e:
            logger.error(f"获取 API 信息失败: {e}")
            return None
    
    async def _execute_api_request(
        self, 
        api_info: Any, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 API 请求"""
        try:
            start_time = datetime.utcnow()
            
            # 模拟 API 请求执行
            await asyncio.sleep(0.1)  # 模拟网络延迟
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 模拟响应结果
            response_data = {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"message": "success", "data": {}}
            }
            
            return {
                "request": {
                    "method": api_info.request_method,
                    "url": api_info.request_url,
                    "headers": json.loads(api_info.request_headers or "{}"),
                    "params": json.loads(api_info.request_params or "{}"),
                    "json": json.loads(api_info.requests_json_data or "{}")
                },
                "response": response_data,
                "status": "passed",
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"API 请求执行失败: {e}")
            return {
                "request": {
                    "method": api_info.request_method,
                    "url": api_info.request_url
                },
                "response": None,
                "status": "failed",
                "error": str(e),
                "duration_ms": 0
            }
    
    async def get_execution_history(
        self, 
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.get(execution_id)
    
    async def get_execution_status(
        self, 
        execution_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        execution = self.execution_history.get(execution_id)
        if execution:
            return {
                "execution_id": execution_id,
                "status": execution.get("status"),
                "start_time": execution.get("start_time"),
                "end_time": execution.get("end_time"),
                "progress": execution.get("progress", 0)
            }
        return None


# 全局实例
test_execution_service = TestExecutionService()
