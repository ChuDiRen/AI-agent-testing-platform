"""
Web项目Service层
"""
from datetime import datetime
from typing import Tuple, List, Optional

from core.logger import get_logger
from sqlmodel import Session, select, func

from ..model.WebProjectModel import WebProject
from ..schemas.WebProjectSchema import WebProjectCreate, WebProjectUpdate, WebProjectQuery

logger = get_logger(__name__)


class WebProjectService:
    """Web项目服务类"""
    
    @staticmethod
    def create(session: Session, project_data: WebProjectCreate) -> WebProject:
        """
        创建Web项目
        
        Args:
            session: 数据库会话
            project_data: 项目数据
            
        Returns:
            WebProject: 创建的项目
        """
        try:
            project = WebProject(**project_data.dict())
            session.add(project)
            session.commit()
            session.refresh(project)
            logger.info(f"创建Web项目成功，ID: {project.id}, 名称: {project.name}")
            return project
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web项目失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update(session: Session, project_id: int, project_data: WebProjectUpdate) -> Optional[WebProject]:
        """
        更新Web项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            project_data: 更新数据
            
        Returns:
            WebProject: 更新后的项目，不存在返回None
        """
        try:
            project = session.get(WebProject, project_id)
            if not project:
                return None
            
            # 更新字段
            update_data = project_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(project, field, value)
            
            project.update_time = datetime.now()
            session.commit()
            session.refresh(project)
            logger.info(f"更新Web项目成功，ID: {project.id}")
            return project
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web项目失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete(session: Session, project_id: int) -> bool:
        """
        删除Web项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            
        Returns:
            bool: 删除成功返回True，不存在返回False
        """
        try:
            project = session.get(WebProject, project_id)
            if not project:
                return False
            
            session.delete(project)
            session.commit()
            logger.info(f"删除Web项目成功，ID: {project_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web项目失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete(session: Session, project_ids: List[int]) -> int:
        """
        批量删除Web项目
        
        Args:
            session: 数据库会话
            project_ids: 项目ID列表
            
        Returns:
            int: 删除的数量
        """
        try:
            count = 0
            for project_id in project_ids:
                if WebProjectService.delete(session, project_id):
                    count += 1
            logger.info(f"批量删除Web项目成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web项目失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_by_id(session: Session, project_id: int) -> Optional[WebProject]:
        """
        根据ID获取Web项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            
        Returns:
            WebProject: 项目信息，不存在返回None
        """
        try:
            return session.get(WebProject, project_id)
        except Exception as e:
            logger.error(f"查询Web项目失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_by_page(session: Session, query: WebProjectQuery) -> Tuple[List[WebProject], int]:
        """
        分页查询Web项目
        
        Args:
            session: 数据库会话
            query: 查询条件
            
        Returns:
            Tuple[List[WebProject], int]: 项目列表和总数
        """
        try:
            # 构建查询条件
            statement = select(WebProject)
            
            # 添加过滤条件
            if query.name:
                statement = statement.where(WebProject.name.contains(query.name))
            if query.status:
                statement = statement.where(WebProject.status == query.status)
            
            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = statement.offset((query.page - 1) * query.pageSize).limit(query.pageSize)
            projects = session.exec(statement).all()
            
            return list(projects), total
        except Exception as e:
            logger.error(f"分页查询Web项目失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def get_all(session: Session) -> List[WebProject]:
        """
        获取所有Web项目
        
        Args:
            session: 数据库会话
            
        Returns:
            List[WebProject]: 所有项目列表
        """
        try:
            statement = select(WebProject).where(WebProject.status == 'active')
            return list(session.exec(statement).all())
        except Exception as e:
            logger.error(f"获取所有Web项目失败: {e}", exc_info=True)
            return []
