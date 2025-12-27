"""
用例步骤Service - 已重构为静态方法模式
提供用例步骤的CRUD、排序等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep


class InfoCaseStepService:
    """用例步骤服务类 - 使用静态方法模式"""

    @staticmethod
    def query_by_case_id(session: Session, case_id: int) -> List[ApiInfoCaseStep]:
        """根据用例ID查询所有步骤"""
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_id
        ).order_by(ApiInfoCaseStep.run_order)

        return list(session.exec(statement).all())

    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[ApiInfoCaseStep]:
        """根据ID查询步骤"""
        return session.get(ApiInfoCaseStep, id)

    @staticmethod
    def create(session: Session, step_data: Dict[str, Any]) -> ApiInfoCaseStep:
        """创建用例步骤"""
        data = ApiInfoCaseStep(
            **step_data,
            create_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, id: int, update_data: Dict[str, Any]) -> Optional[ApiInfoCaseStep]:
        """更新用例步骤"""
        step = session.get(ApiInfoCaseStep, id)
        if not step:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(step, key, value)

        session.commit()
        return step

    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """删除用例步骤"""
        step = session.get(ApiInfoCaseStep, id)
        if not step:
            return False

        session.delete(step)
        session.commit()
        return True

    @staticmethod
    def batch_create(session: Session, steps: List[Dict[str, Any]]) -> List[ApiInfoCaseStep]:
        """批量创建步骤"""
        created_steps = []
        for step_data in steps:
            step = ApiInfoCaseStep(
                **step_data,
                create_time=datetime.now()
            )
            session.add(step)
            created_steps.append(step)

        session.commit()
        for step in created_steps:
            session.refresh(step)

        return created_steps

    @staticmethod
    def batch_update_order(session: Session, order_updates: List[Dict[str, int]]) -> bool:
        """批量更新步骤顺序"""
        for update in order_updates:
            step_id = update.get("id")
            new_order = update.get("run_order") or update.get("step_order")

            if step_id and new_order is not None:
                step = session.get(ApiInfoCaseStep, step_id)
                if step:
                    step.run_order = new_order

        session.commit()
        return True

    @staticmethod
    def delete_by_case_id(session: Session, case_id: int) -> int:
        """删除用例的所有步骤"""
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_id
        ).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()

        deleted_count = len(steps)
        for step in steps:
            session.delete(step)

        session.commit()
        return deleted_count
