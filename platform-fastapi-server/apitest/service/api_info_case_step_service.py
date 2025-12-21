"""
用例步骤Service
提供用例步骤的CRUD、排序等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep


class InfoCaseStepService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_case_id(self, case_id: int) -> List[ApiInfoCaseStep]:
        """根据用例ID查询所有步骤"""
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_id
        ).order_by(ApiInfoCaseStep.run_order)
        
        return self.session.exec(statement).all()
    
    def get_by_id(self, id: int) -> Optional[ApiInfoCaseStep]:
        """根据ID查询步骤"""
        return self.session.get(ApiInfoCaseStep, id)
    
    def create(self, **kwargs) -> ApiInfoCaseStep:
        """创建用例步骤"""
        data = ApiInfoCaseStep(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新用例步骤"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除用例步骤"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def batch_create(self, steps: List[Dict[str, Any]]) -> List[ApiInfoCaseStep]:
        """批量创建步骤"""
        created_steps = []
        for step_data in steps:
            step = ApiInfoCaseStep(
                **step_data,
                create_time=datetime.now()
            )
            self.session.add(step)
            created_steps.append(step)
        
        self.session.commit()
        for step in created_steps:
            self.session.refresh(step)
        
        return created_steps
    
    def batch_update_order(self, order_updates: List[Dict[str, int]]) -> bool:
        """批量更新步骤顺序"""
        for update in order_updates:
            step_id = update.get("id")
            new_order = update.get("run_order") or update.get("step_order")
            
            if step_id and new_order is not None:
                step = self.get_by_id(step_id)
                if step:
                    step.run_order = new_order
                    self.session.add(step)
        
        self.session.commit()
        return True
    
    def delete_by_case_id(self, case_id: int) -> int:
        """删除用例的所有步骤"""
        steps = self.query_by_case_id(case_id)
        deleted_count = len(steps)
        
        for step in steps:
            self.session.delete(step)
        
        self.session.commit()
        return deleted_count
