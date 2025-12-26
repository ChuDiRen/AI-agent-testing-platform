"""
API项目Service
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from core.logger import get_logger

from ..model.ApiProjectModel import ApiProject

logger = get_logger(__name__)


class ApiProjectService:
    """API项目服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, **filters) -> tuple[List[ApiProject], int]:
        """分页查询API项目"""
        statement = select(ApiProject)
        count_statement = select(ApiProject)
        
        # 动态过滤条件
        for key, value in filters.items():
            if value is not None and hasattr(ApiProject, key):
                if isinstance(value, str) and key == 'project_name':
                    statement = statement.where(getattr(ApiProject, key).contains(value))
                    count_statement = count_statement.where(getattr(ApiProject, key).contains(value))
                else:
                    statement = statement.where(getattr(ApiProject, key) == value)
                    count_statement = count_statement.where(getattr(ApiProject, key) == value)
        
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        total = len(self.session.exec(count_statement).all())
        return list(datas), total
    
    def get_by_id(self, project_id: int) -> Optional[ApiProject]:
        """根据ID查询API项目"""
        return self.session.get(ApiProject, project_id)
    
    def create(self, project_name: str, project_desc: Optional[str] = None) -> ApiProject:
        """新增API项目"""
        project = ApiProject(
            project_name=project_name,
            project_desc=project_desc,
            create_time=datetime.now()
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
    
    def update(self, project_id: int, update_data: Dict[str, Any]) -> Optional[ApiProject]:
        """更新API项目"""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)
        
        self.session.commit()
        self.session.refresh(project)
        return project
    
    def delete(self, project_id: int) -> bool:
        """删除API项目"""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        self.session.delete(project)
        self.session.commit()
        return True
    
    def query_all(self) -> List[ApiProject]:
        """查询所有API项目"""
        statement = select(ApiProject)
        return list(self.session.exec(statement).all())
