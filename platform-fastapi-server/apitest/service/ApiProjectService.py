"""
API项目Service - 已重构为静态方法模式
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel import Session, select
from core.logger import get_logger

from ..model.ApiProjectModel import ApiProject
from ..schemas.ApiProjectSchema import ApiProjectQuery, ApiProjectCreate, ApiProjectUpdate

logger = get_logger(__name__)


class ApiProjectService:
    """API项目服务类 - 使用静态方法模式"""

    @staticmethod
    def query_by_page(session: Session, query: ApiProjectQuery) -> Tuple[List[ApiProject], int]:
        """分页查询API项目"""
        offset = (query.page - 1) * query.pageSize
        statement = select(ApiProject)

        # 应用过滤条件
        if query.project_name:
            statement = statement.where(ApiProject.project_name.contains(query.project_name))

        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()

        # 统计总数
        count_statement = select(ApiProject)
        if query.project_name:
            count_statement = count_statement.where(ApiProject.project_name.contains(query.project_name))
        total = len(session.exec(count_statement).all())

        return list(datas), total

    @staticmethod
    def query_by_id(session: Session, project_id: int) -> Optional[ApiProject]:
        """根据ID查询API项目"""
        return session.get(ApiProject, project_id)

    @staticmethod
    def create(session: Session, project: ApiProjectCreate) -> ApiProject:
        """新增API项目"""
        data = ApiProject(
            **project.model_dump(),
            create_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, project: ApiProjectUpdate) -> Optional[ApiProject]:
        """更新API项目"""
        statement = select(ApiProject).where(ApiProject.id == project.id)
        db_project = session.exec(statement).first()
        if not db_project:
            return None

        update_data = project.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_project, key, value)
        session.commit()
        return db_project

    @staticmethod
    def delete(session: Session, project_id: int) -> bool:
        """删除API项目"""
        project = session.get(ApiProject, project_id)
        if not project:
            return False

        session.delete(project)
        session.commit()
        return True

    @staticmethod
    def query_all(session: Session) -> List[ApiProject]:
        """查询所有API项目"""
        statement = select(ApiProject)
        return list(session.exec(statement).all())

    @staticmethod
    def batch_delete(session: Session, ids: List[int]) -> int:
        """批量删除API项目"""
        deleted_count = 0
        for project_id in ids:
            project = session.get(ApiProject, project_id)
            if project:
                session.delete(project)
                deleted_count += 1
        
        if deleted_count > 0:
            session.commit()
        
        return deleted_count
