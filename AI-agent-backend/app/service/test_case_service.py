# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例Service
处理测试用例相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.entity.test_case import TestCase, TestCaseStatus
from app.entity.test_case_generation_history import TestCaseGenerationHistory
from app.repository.test_case_repository import TestCaseRepository
from app.dto.test_case_dto import (
    TestCaseCreateRequest, TestCaseUpdateRequest, TestCaseSearchRequest,
    TestCaseResponse, TestCaseListResponse, TestCaseStatisticsResponse,
    TestCaseBatchOperationRequest, TestCaseBatchOperationResponse,
    TestCaseGenerationHistoryRequest, TestCaseGenerationHistoryResponse,
    TestCaseGenerationHistoryItem
)
from app.core.logger import get_logger
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class TestCaseService:
    """测试用例Service类"""

    def __init__(self, db: Session):
        self.db = db
        self.test_case_repo = TestCaseRepository(db)

    def create_test_case(self, request: TestCaseCreateRequest, created_by_id: int) -> TestCaseResponse:
        """创建测试用例"""
        try:
            # 创建测试用例实体
            test_case = TestCase(
                name=request.name,
                module=request.module,
                description=request.description,
                preconditions=request.preconditions,
                test_steps=request.test_steps,
                expected_result=request.expected_result,
                priority=request.priority.value,
                test_type=request.test_type.value,
                tags=request.tags,
                agent_id=request.agent_id,
                created_by_id=created_by_id,
                extra_data=request.metadata
            )
            
            # 保存到数据库
            created_test_case = self.test_case_repo.create(test_case)
            
            logger.info(f"Created test case '{created_test_case.name}' with id {created_test_case.id}")
            return self._convert_to_response(created_test_case)
            
        except Exception as e:
            logger.error(f"Error creating test case: {str(e)}")
            raise

    def get_test_case_by_id(self, test_case_id: int) -> Optional[TestCaseResponse]:
        """根据ID获取测试用例"""
        try:
            test_case = self.test_case_repo.get_by_id(test_case_id)
            if not test_case:
                return None
            
            return self._convert_to_response(test_case)
            
        except Exception as e:
            logger.error(f"Error getting test case by id {test_case_id}: {str(e)}")
            raise

    def update_test_case(self, test_case_id: int, request: TestCaseUpdateRequest) -> Optional[TestCaseResponse]:
        """更新测试用例"""
        try:
            test_case = self.test_case_repo.get_by_id(test_case_id)
            if not test_case:
                raise BusinessException(f"测试用例 {test_case_id} 不存在")
            
            # 准备更新数据
            update_data = {}
            if request.name is not None:
                update_data['name'] = request.name
            if request.module is not None:
                update_data['module'] = request.module
            if request.description is not None:
                update_data['description'] = request.description
            if request.preconditions is not None:
                update_data['preconditions'] = request.preconditions
            if request.test_steps is not None:
                update_data['test_steps'] = request.test_steps
            if request.expected_result is not None:
                update_data['expected_result'] = request.expected_result
            if request.priority is not None:
                update_data['priority'] = request.priority.value
            if request.test_type is not None:
                update_data['test_type'] = request.test_type.value
            if request.tags is not None:
                update_data['tags'] = request.tags
            
            # 更新测试用例
            updated_test_case = self.test_case_repo.update(test_case_id, update_data)
            if not updated_test_case:
                raise BusinessException(f"更新测试用例 {test_case_id} 失败")
            
            logger.info(f"Updated test case {test_case_id}")
            return self._convert_to_response(updated_test_case)
            
        except Exception as e:
            logger.error(f"Error updating test case {test_case_id}: {str(e)}")
            raise

    def delete_test_case(self, test_case_id: int) -> bool:
        """删除测试用例"""
        try:
            test_case = self.test_case_repo.get_by_id(test_case_id)
            if not test_case:
                raise BusinessException(f"测试用例 {test_case_id} 不存在")
            
            # 检查测试用例状态
            if test_case.is_running():
                raise BusinessException(f"不能删除正在执行的测试用例")
            
            # 软删除测试用例
            success = self.test_case_repo.delete(test_case_id, soft_delete=True)
            
            if success:
                logger.info(f"Deleted test case {test_case_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting test case {test_case_id}: {str(e)}")
            raise

    def search_test_cases(self, request: TestCaseSearchRequest) -> TestCaseListResponse:
        """搜索测试用例"""
        try:
            test_cases, total = self.test_case_repo.search(
                keyword=request.keyword,
                module=request.module,
                status=request.status.value if request.status else None,
                priority=request.priority.value if request.priority else None,
                test_type=request.test_type.value if request.test_type else None,
                agent_id=request.agent_id,
                created_by_id=request.created_by_id,
                executor_id=request.executor_id,
                tags=request.tags,
                start_date=request.start_date,
                end_date=request.end_date,
                skip=request.skip,
                limit=request.limit
            )
            
            # 转换为响应对象
            test_case_responses = [self._convert_to_response(test_case) for test_case in test_cases]
            
            return TestCaseListResponse(
                test_cases=test_case_responses,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=(total + request.page_size - 1) // request.page_size
            )
            
        except Exception as e:
            logger.error(f"Error searching test cases: {str(e)}")
            raise

    def get_test_case_statistics(self) -> TestCaseStatisticsResponse:
        """获取测试用例统计信息"""
        try:
            statistics = self.test_case_repo.get_statistics()
            
            return TestCaseStatisticsResponse(**statistics)
            
        except Exception as e:
            logger.error(f"Error getting test case statistics: {str(e)}")
            raise

    def execute_test_case(self, test_case_id: int, executor_id: int) -> TestCaseResponse:
        """执行测试用例"""
        try:
            test_case = self.test_case_repo.get_by_id(test_case_id)
            if not test_case:
                raise BusinessException(f"测试用例 {test_case_id} 不存在")
            
            if test_case.is_running():
                raise BusinessException(f"测试用例 {test_case_id} 已在执行中")
            
            # 设置为执行中状态
            test_case.set_running(executor_id)
            self.test_case_repo.update(test_case_id, {
                'status': test_case.status,
                'executor_id': test_case.executor_id,
                'executed_at': test_case.executed_at
            })
            
            logger.info(f"Started execution of test case {test_case_id}")
            return self._convert_to_response(test_case)
            
        except Exception as e:
            logger.error(f"Error executing test case {test_case_id}: {str(e)}")
            raise

    def complete_test_case(self, test_case_id: int, passed: bool, 
                          actual_result: str = None, execution_time: float = None) -> TestCaseResponse:
        """完成测试用例执行"""
        try:
            test_case = self.test_case_repo.get_by_id(test_case_id)
            if not test_case:
                raise BusinessException(f"测试用例 {test_case_id} 不存在")
            
            if not test_case.is_running():
                raise BusinessException(f"测试用例 {test_case_id} 未在执行中")
            
            # 设置执行结果
            if passed:
                test_case.set_passed(actual_result, execution_time)
            else:
                test_case.set_failed(actual_result, execution_time)
            
            self.test_case_repo.update(test_case_id, {
                'status': test_case.status,
                'actual_result': test_case.actual_result,
                'execution_time': test_case.execution_time
            })
            
            logger.info(f"Completed test case {test_case_id} with result: {'PASSED' if passed else 'FAILED'}")
            return self._convert_to_response(test_case)
            
        except Exception as e:
            logger.error(f"Error completing test case {test_case_id}: {str(e)}")
            raise

    def batch_operation(self, request: TestCaseBatchOperationRequest) -> TestCaseBatchOperationResponse:
        """批量操作测试用例"""
        try:
            total = len(request.test_case_ids)
            success_count = 0
            failed_ids = []
            errors = []
            
            for test_case_id in request.test_case_ids:
                try:
                    if request.operation == 'set_pending':
                        self._set_test_case_pending(test_case_id)
                    elif request.operation == 'set_passed':
                        self._set_test_case_passed(test_case_id, request.operation_data)
                    elif request.operation == 'set_failed':
                        self._set_test_case_failed(test_case_id, request.operation_data)
                    elif request.operation == 'delete':
                        self.delete_test_case(test_case_id)
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_ids.append(test_case_id)
                    errors.append(f"测试用例 {test_case_id}: {str(e)}")
            
            failed_count = total - success_count
            success_rate = (success_count / total * 100) if total > 0 else 0.0
            
            logger.info(f"Batch operation '{request.operation}' completed: {success_count}/{total} successful")
            
            return TestCaseBatchOperationResponse(
                total=total,
                success_count=success_count,
                failed_count=failed_count,
                failed_ids=failed_ids,
                errors=errors,
                success_rate=round(success_rate, 2)
            )
            
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            raise

    def _set_test_case_pending(self, test_case_id: int):
        """设置测试用例为待执行状态"""
        test_case = self.test_case_repo.get_by_id(test_case_id)
        if not test_case:
            raise BusinessException(f"测试用例 {test_case_id} 不存在")
        
        test_case.set_pending()
        self.test_case_repo.update(test_case_id, {'status': test_case.status})

    def _set_test_case_passed(self, test_case_id: int, operation_data: Dict[str, Any]):
        """设置测试用例为通过状态"""
        test_case = self.test_case_repo.get_by_id(test_case_id)
        if not test_case:
            raise BusinessException(f"测试用例 {test_case_id} 不存在")
        
        actual_result = operation_data.get('actual_result')
        execution_time = operation_data.get('execution_time')
        
        test_case.set_passed(actual_result, execution_time)
        self.test_case_repo.update(test_case_id, {
            'status': test_case.status,
            'actual_result': test_case.actual_result,
            'execution_time': test_case.execution_time
        })

    def _set_test_case_failed(self, test_case_id: int, operation_data: Dict[str, Any]):
        """设置测试用例为失败状态"""
        test_case = self.test_case_repo.get_by_id(test_case_id)
        if not test_case:
            raise BusinessException(f"测试用例 {test_case_id} 不存在")
        
        actual_result = operation_data.get('actual_result')
        execution_time = operation_data.get('execution_time')
        
        test_case.set_failed(actual_result, execution_time)
        self.test_case_repo.update(test_case_id, {
            'status': test_case.status,
            'actual_result': test_case.actual_result,
            'execution_time': test_case.execution_time
        })

    def get_generation_history(self, request: TestCaseGenerationHistoryRequest, user_id: int = None) -> TestCaseGenerationHistoryResponse:
        """获取测试用例生成历史"""
        try:
            # 构建查询条件
            query = self.db.query(TestCaseGenerationHistory)

            # 如果指定了用户ID，则过滤
            if request.user_id:
                query = query.filter(TestCaseGenerationHistory.created_by_id == request.user_id)
            elif user_id:
                query = query.filter(TestCaseGenerationHistory.created_by_id == user_id)

            # 如果指定了状态，则过滤
            if request.status:
                query = query.filter(TestCaseGenerationHistory.status == request.status.value)

            # 如果指定了测试类型，则过滤
            if request.test_type:
                query = query.filter(TestCaseGenerationHistory.test_type == request.test_type.value)

            # 按创建时间倒序排列
            query = query.order_by(TestCaseGenerationHistory.created_at.desc())

            # 获取总数
            total = query.count()

            # 分页
            offset = (request.page - 1) * request.page_size
            history_records = query.offset(offset).limit(request.page_size).all()

            # 转换为响应对象
            history_items = []
            for record in history_records:
                history_items.append(TestCaseGenerationHistoryItem(
                    id=record.id,
                    task_id=record.task_id,
                    requirement_text=record.requirement_text,
                    requirement_summary=record.get_requirement_summary(),
                    test_type=record.test_type,
                    priority=record.priority,
                    generated_count=record.generated_count,
                    status=record.status,
                    created_at=record.created_at.isoformat() if record.created_at else "",
                    updated_at=record.updated_at.isoformat() if record.updated_at else ""
                ))

            return TestCaseGenerationHistoryResponse(
                total=total,
                page=request.page,
                page_size=request.page_size,
                history=history_items,
                generation_time=0.0,  # 查询耗时，这里可以计算实际耗时
                agent_used=None,  # 查询历史时不涉及特定代理
                warnings=[],
                errors=[]
            )

        except Exception as e:
            logger.error(f"Error getting generation history: {str(e)}")
            raise BusinessException(f"获取生成历史失败: {str(e)}")

    def _convert_to_response(self, test_case: TestCase) -> TestCaseResponse:
        """转换为响应对象"""
        return TestCaseResponse(
            id=test_case.id,
            name=test_case.name,
            module=test_case.module,
            description=test_case.description,
            preconditions=test_case.preconditions,
            test_steps=test_case.test_steps,
            expected_result=test_case.expected_result,
            actual_result=test_case.actual_result,
            status=test_case.status,
            priority=test_case.priority,
            test_type=test_case.test_type,
            tags=test_case.tags,
            tags_list=test_case.get_tags_list(),
            agent_id=test_case.agent_id,
            created_by_id=test_case.created_by_id,
            executor_id=test_case.executor_id,
            executed_at=test_case.executed_at,
            execution_time=test_case.execution_time,
            remarks=test_case.remarks,
            metadata=test_case.extra_data or {},
            created_at=test_case.created_at,
            updated_at=test_case.updated_at
        )