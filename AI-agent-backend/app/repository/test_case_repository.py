# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例Repository
处理测试用例相关的数据访问操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.entity.test_case import TestCase, TestCaseStatus, TestCasePriority, TestCaseType
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class TestCaseRepository(BaseRepository[TestCase]):
    """测试用例Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, TestCase)

    def find_by_module(self, module: str, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        根据模块查找测试用例
        
        Args:
            module: 模块名称
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.module == module,
                    TestCase.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(test_cases)} test cases in module '{module}'")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error finding test cases by module '{module}': {str(e)}")
            raise

    def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        根据状态查找测试用例
        
        Args:
            status: 测试用例状态
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.status == status,
                    TestCase.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(test_cases)} test cases with status '{status}'")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error finding test cases by status '{status}': {str(e)}")
            raise

    def find_by_priority(self, priority: str, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        根据优先级查找测试用例
        
        Args:
            priority: 测试用例优先级
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.priority == priority,
                    TestCase.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(test_cases)} test cases with priority '{priority}'")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error finding test cases by priority '{priority}': {str(e)}")
            raise

    def find_by_agent(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        根据代理查找测试用例
        
        Args:
            agent_id: 代理ID
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.agent_id == agent_id,
                    TestCase.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(test_cases)} test cases for agent {agent_id}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error finding test cases by agent {agent_id}: {str(e)}")
            raise

    def search(self, keyword: str = None, module: str = None, status: str = None,
               priority: str = None, test_type: str = None, agent_id: int = None,
               created_by_id: int = None, executor_id: int = None, tags: str = None,
               start_date: datetime = None, end_date: datetime = None,
               skip: int = 0, limit: int = 100) -> tuple[List[TestCase], int]:
        """
        搜索测试用例
        
        Args:
            keyword: 搜索关键词
            module: 模块筛选
            status: 状态筛选
            priority: 优先级筛选
            test_type: 类型筛选
            agent_id: 代理ID筛选
            created_by_id: 创建者ID筛选
            executor_id: 执行者ID筛选
            tags: 标签筛选
            start_date: 创建时间开始
            end_date: 创建时间结束
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            (测试用例列表, 总数量)
        """
        try:
            query = self.db.query(TestCase).filter(TestCase.is_deleted == 0)
            
            # 关键词搜索
            if keyword:
                keyword_filter = or_(
                    TestCase.name.ilike(f'%{keyword}%'),
                    TestCase.description.ilike(f'%{keyword}%'),
                    TestCase.test_steps.ilike(f'%{keyword}%'),
                    TestCase.expected_result.ilike(f'%{keyword}%')
                )
                query = query.filter(keyword_filter)
            
            # 模块筛选
            if module:
                query = query.filter(TestCase.module == module)
            
            # 状态筛选
            if status:
                query = query.filter(TestCase.status == status)
            
            # 优先级筛选
            if priority:
                query = query.filter(TestCase.priority == priority)
            
            # 类型筛选
            if test_type:
                query = query.filter(TestCase.test_type == test_type)
            
            # 代理筛选
            if agent_id:
                query = query.filter(TestCase.agent_id == agent_id)
            
            # 创建者筛选
            if created_by_id:
                query = query.filter(TestCase.created_by_id == created_by_id)
            
            # 执行者筛选
            if executor_id:
                query = query.filter(TestCase.executor_id == executor_id)
            
            # 标签筛选
            if tags:
                query = query.filter(TestCase.tags.ilike(f'%{tags}%'))
            
            # 时间范围筛选
            if start_date:
                query = query.filter(TestCase.created_at >= start_date)
            if end_date:
                query = query.filter(TestCase.created_at <= end_date)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            test_cases = query.order_by(desc(TestCase.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Search found {len(test_cases)} test cases (total: {total})")
            return test_cases, total
            
        except Exception as e:
            logger.error(f"Error searching test cases: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取测试用例统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 基本统计
            total_cases = self.count()
            
            # 按状态统计
            status_counts = {}
            for status in TestCaseStatus:
                count = self.db.query(func.count(TestCase.id)).filter(
                    and_(TestCase.status == status.value, TestCase.is_deleted == 0)
                ).scalar()
                status_counts[status.value] = count
            
            # 按优先级统计
            priority_counts = {}
            for priority in TestCasePriority:
                count = self.db.query(func.count(TestCase.id)).filter(
                    and_(TestCase.priority == priority.value, TestCase.is_deleted == 0)
                ).scalar()
                priority_counts[priority.value] = count
            
            # 按类型统计
            type_counts = {}
            for test_type in TestCaseType:
                count = self.db.query(func.count(TestCase.id)).filter(
                    and_(TestCase.test_type == test_type.value, TestCase.is_deleted == 0)
                ).scalar()
                type_counts[test_type.value] = count
            
            # 按模块统计
            module_counts = {}
            modules = self.db.query(TestCase.module, func.count(TestCase.id)).filter(
                and_(TestCase.module.isnot(None), TestCase.is_deleted == 0)
            ).group_by(TestCase.module).all()
            
            for module, count in modules:
                module_counts[module] = count
            
            # 执行统计
            executed_cases = status_counts.get(TestCaseStatus.PASSED.value, 0) + \
                           status_counts.get(TestCaseStatus.FAILED.value, 0)
            execution_rate = (executed_cases / total_cases * 100) if total_cases > 0 else 0.0
            
            pass_rate = (status_counts.get(TestCaseStatus.PASSED.value, 0) / executed_cases * 100) \
                       if executed_cases > 0 else 0.0
            
            # 平均执行时间
            avg_execution_time = self.db.query(func.avg(TestCase.execution_time)).filter(
                and_(TestCase.execution_time.isnot(None), TestCase.is_deleted == 0)
            ).scalar() or 0.0
            
            statistics = {
                "total_cases": total_cases,
                "draft_cases": status_counts.get(TestCaseStatus.DRAFT.value, 0),
                "pending_cases": status_counts.get(TestCaseStatus.PENDING.value, 0),
                "running_cases": status_counts.get(TestCaseStatus.RUNNING.value, 0),
                "passed_cases": status_counts.get(TestCaseStatus.PASSED.value, 0),
                "failed_cases": status_counts.get(TestCaseStatus.FAILED.value, 0),
                "skipped_cases": status_counts.get(TestCaseStatus.SKIPPED.value, 0),
                "blocked_cases": status_counts.get(TestCaseStatus.BLOCKED.value, 0),
                "cases_by_priority": priority_counts,
                "cases_by_type": type_counts,
                "cases_by_module": module_counts,
                "execution_rate": round(execution_rate, 2),
                "pass_rate": round(pass_rate, 2),
                "avg_execution_time": round(avg_execution_time, 2)
            }
            
            logger.debug("Generated test case statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting test case statistics: {str(e)}")
            raise

    def batch_update_status(self, test_case_ids: List[int], status: str, 
                           executor_id: int = None, actual_result: str = None) -> int:
        """
        批量更新测试用例状态
        
        Args:
            test_case_ids: 测试用例ID列表
            status: 目标状态
            executor_id: 执行者ID
            actual_result: 实际结果
            
        Returns:
            更新成功的数量
        """
        try:
            update_data = {
                TestCase.status: status,
                TestCase.updated_at: datetime.utcnow()
            }
            
            if executor_id:
                update_data[TestCase.executor_id] = executor_id
            
            if actual_result:
                update_data[TestCase.actual_result] = actual_result
            
            if status in [TestCaseStatus.RUNNING.value]:
                update_data[TestCase.executed_at] = datetime.utcnow()
            
            updated_count = self.db.query(TestCase).filter(
                and_(
                    TestCase.id.in_(test_case_ids),
                    TestCase.is_deleted == 0
                )
            ).update(update_data, synchronize_session=False)
            
            self.db.commit()
            
            logger.info(f"Batch updated {updated_count} test cases to status '{status}'")
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error batch updating test case status: {str(e)}")
            raise

    def get_high_priority_cases(self, limit: int = 100) -> List[TestCase]:
        """
        获取高优先级测试用例
        
        Args:
            limit: 限制返回的记录数
            
        Returns:
            高优先级测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.priority.in_([TestCasePriority.P1.value, TestCasePriority.P2.value]),
                    TestCase.is_deleted == 0
                )
            ).order_by(TestCase.priority, desc(TestCase.created_at)).limit(limit).all()
            
            logger.debug(f"Retrieved {len(test_cases)} high priority test cases")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error getting high priority test cases: {str(e)}")
            raise

    def get_failed_cases(self, skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        获取失败的测试用例
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            失败测试用例列表
        """
        try:
            test_cases = self.db.query(TestCase).filter(
                and_(
                    TestCase.status == TestCaseStatus.FAILED.value,
                    TestCase.is_deleted == 0
                )
            ).order_by(desc(TestCase.executed_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(test_cases)} failed test cases")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error getting failed test cases: {str(e)}")
            raise

    def get_cases_by_tags(self, tags: List[str], skip: int = 0, limit: int = 100) -> List[TestCase]:
        """
        根据标签查找测试用例
        
        Args:
            tags: 标签列表
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            测试用例列表
        """
        try:
            # 构建标签查询条件
            tag_filters = []
            for tag in tags:
                tag_filters.append(TestCase.tags.ilike(f'%{tag}%'))
            
            query = self.db.query(TestCase).filter(
                and_(
                    or_(*tag_filters) if tag_filters else True,
                    TestCase.is_deleted == 0
                )
            )
            
            test_cases = query.offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(test_cases)} test cases with tags {tags}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error finding test cases by tags {tags}: {str(e)}")
            raise