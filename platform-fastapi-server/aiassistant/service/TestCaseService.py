"""
测试用例服务层
"""
import json
import logging
from datetime import datetime
from typing import Optional, List, Tuple

import yaml
from sqlmodel import select, Session, func

from ..model.TestCaseModel import TestCase
from ..schemas.test_case_schema import TestCaseQuery, TestCaseCreate, TestCaseUpdate, BatchInsertRequest

logger = logging.getLogger(__name__)


class TestCaseService:
    """测试用例服务"""
    
    @staticmethod
    def query_by_page(
        session: Session,
        query: TestCaseQuery
    ) -> Tuple[List[TestCase], int, Optional[str]]:
        """
        分页查询测试用例
        
        Args:
            session: 数据库会话
            query: 查询参数
            
        Returns:
            (cases, total, error_message) 元组
        """
        try:
            offset = (query.page - 1) * query.pageSize
            statement = select(TestCase)
            
            # 按项目过滤
            if query.project_id:
                statement = statement.where(TestCase.project_id == query.project_id)
            
            # 按测试类型过滤
            if query.test_type:
                statement = statement.where(TestCase.test_type == query.test_type)
            
            # 按优先级过滤
            if query.priority:
                statement = statement.where(TestCase.priority == query.priority)
            
            statement = statement.order_by(TestCase.create_time.desc()).limit(query.pageSize).offset(offset)
            datas = session.exec(statement).all()
            
            # 统计总数
            count_statement = select(func.count(TestCase.id))
            if query.project_id:
                count_statement = count_statement.where(TestCase.project_id == query.project_id)
            if query.test_type:
                count_statement = count_statement.where(TestCase.test_type == query.test_type)
            if query.priority:
                count_statement = count_statement.where(TestCase.priority == query.priority)
            total = session.exec(count_statement).one()
            
            return list(datas), total, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], 0, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_by_id(
        session: Session,
        id: int
    ) -> Tuple[Optional[TestCase], Optional[str]]:
        """
        根据ID查询测试用例
        
        Args:
            session: 数据库会话
            id: 用例ID
            
        Returns:
            (case, error_message) 元组
        """
        try:
            statement = select(TestCase).where(TestCase.id == id)
            data = session.exec(statement).first()
            return data, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return None, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def insert(
        session: Session,
        case: TestCaseCreate
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        新增测试用例
        
        Args:
            session: 数据库会话
            case: 用例创建数据
            
        Returns:
            (case_id, error_message) 元组
        """
        try:
            data = TestCase(**case.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
            session.add(data)
            session.commit()
            session.refresh(data)
            logger.info(f"新增测试用例成功: {data.case_name}")
            return data.id, None
        except Exception as e:
            session.rollback()
            logger.error(f"新增失败: {e}", exc_info=True)
            return None, f"添加失败:{e}"
    
    @staticmethod
    def batch_insert(
        session: Session,
        req: BatchInsertRequest
    ) -> Tuple[int, Optional[str]]:
        """
        批量插入测试用例
        
        Args:
            session: 数据库会话
            req: 批量插入请求
            
        Returns:
            (count, error_message) 元组
        """
        try:
            created_cases = []
            for case_data in req.test_cases:
                test_case = TestCase(
                    **case_data.model_dump(),
                    project_id=req.project_id,
                    create_time=datetime.now(),
                    modify_time=datetime.now()
                )
                session.add(test_case)
                created_cases.append(test_case)
            
            session.commit()
            for case in created_cases:
                session.refresh(case)
            
            logger.info(f"批量插入{len(created_cases)}个测试用例成功")
            return len(created_cases), None
        except Exception as e:
            session.rollback()
            logger.error(f"批量插入失败: {e}", exc_info=True)
            return 0, f"批量创建失败:{e}"
    
    @staticmethod
    def update(
        session: Session,
        case: TestCaseUpdate
    ) -> Tuple[bool, str]:
        """
        更新测试用例
        
        Args:
            session: 数据库会话
            case: 用例更新数据
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(TestCase).where(TestCase.id == case.id)
            db_case = session.exec(statement).first()
            if db_case:
                update_data = case.model_dump(exclude_unset=True, exclude={'id'})
                for key, value in update_data.items():
                    setattr(db_case, key, value)
                db_case.modify_time = datetime.now()
                session.commit()
                logger.info(f"更新测试用例成功: {db_case.case_name}")
                return True, "修改成功"
            else:
                return False, "测试用例不存在"
        except Exception as e:
            session.rollback()
            logger.error(f"更新失败: {e}", exc_info=True)
            return False, f"修改失败，请联系管理员:{e}"
    
    @staticmethod
    def delete(
        session: Session,
        id: int
    ) -> Tuple[bool, str]:
        """
        删除测试用例
        
        Args:
            session: 数据库会话
            id: 用例ID
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(TestCase).where(TestCase.id == id)
            data = session.exec(statement).first()
            if data:
                session.delete(data)
                session.commit()
                logger.info(f"删除测试用例成功: {data.case_name}")
                return True, "删除成功"
            else:
                return False, "测试用例不存在"
        except Exception as e:
            session.rollback()
            logger.error(f"删除失败: {e}", exc_info=True)
            return False, f"删除失败，请联系管理员:{e}"
    
    @staticmethod
    def export_yaml(
        session: Session,
        id: int
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        导出单个测试用例为YAML
        
        Args:
            session: 数据库会话
            id: 用例ID
            
        Returns:
            (yaml_content, filename, error_message) 元组
        """
        try:
            test_case = session.get(TestCase, id)
            if not test_case:
                return None, None, "测试用例不存在"
            
            # 构建YAML数据
            yaml_data = {
                "name": test_case.case_name,
                "priority": test_case.priority,
                "test_type": test_case.test_type,
                "precondition": test_case.precondition,
                "test_steps": json.loads(test_case.test_steps) if test_case.test_steps else [],
                "expected_result": test_case.expected_result,
                "test_data": json.loads(test_case.test_data) if test_case.test_data else None
            }
            
            # 转换为YAML
            yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"导出测试用例YAML成功: {test_case.case_name}")
            return yaml_content, f"{test_case.case_name}.yaml", None
        except Exception as e:
            logger.error(f"导出失败: {e}", exc_info=True)
            return None, None, f"导出失败:{e}"
    
    @staticmethod
    def export_batch_yaml(
        session: Session,
        case_ids: List[int]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        批量导出测试用例为YAML
        
        Args:
            session: 数据库会话
            case_ids: 用例ID列表
            
        Returns:
            (yaml_content, error_message) 元组
        """
        try:
            test_cases = session.exec(
                select(TestCase).where(TestCase.id.in_(case_ids))
            ).all()
            
            if not test_cases:
                return None, "未找到测试用例"
            
            # 构建YAML数据列表
            yaml_data_list = []
            for test_case in test_cases:
                yaml_data = {
                    "name": test_case.case_name,
                    "priority": test_case.priority,
                    "test_type": test_case.test_type,
                    "precondition": test_case.precondition,
                    "test_steps": json.loads(test_case.test_steps) if test_case.test_steps else [],
                    "expected_result": test_case.expected_result,
                    "test_data": json.loads(test_case.test_data) if test_case.test_data else None
                }
                yaml_data_list.append(yaml_data)
            
            # 转换为YAML
            yaml_content = yaml.dump(yaml_data_list, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"批量导出{len(test_cases)}个测试用例YAML成功")
            return yaml_content, None
        except Exception as e:
            logger.error(f"批量导出失败: {e}", exc_info=True)
            return None, f"导出失败:{e}"
