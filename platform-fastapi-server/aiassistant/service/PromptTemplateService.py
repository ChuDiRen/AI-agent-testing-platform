"""
提示词模板服务层
"""
import logging
from datetime import datetime
from typing import Optional, List, Tuple

from sqlmodel import select, Session, func

from ..model.PromptTemplate import PromptTemplate
from ..schemas.prompt_template_schema import PromptTemplateQuery, PromptTemplateCreate, PromptTemplateUpdate

logger = logging.getLogger(__name__)


class PromptTemplateService:
    """提示词模板服务"""
    
    @staticmethod
    def query_by_page(
        session: Session,
        query: PromptTemplateQuery
    ) -> Tuple[List[PromptTemplate], int, Optional[str]]:
        """
        分页查询提示词模板
        
        Args:
            session: 数据库会话
            query: 查询参数
            
        Returns:
            (templates, total, error_message) 元组
        """
        try:
            offset = (query.page - 1) * query.pageSize
            statement = select(PromptTemplate)
            
            # 按测试类型过滤
            if query.test_type:
                statement = statement.where(PromptTemplate.test_type == query.test_type)
            
            # 按模板类型过滤
            if query.template_type:
                statement = statement.where(PromptTemplate.template_type == query.template_type)
            
            # 按状态过滤
            if query.is_active is not None:
                statement = statement.where(PromptTemplate.is_active == query.is_active)
            
            statement = statement.order_by(PromptTemplate.create_time.desc()).limit(query.pageSize).offset(offset)
            datas = session.exec(statement).all()
            
            # 统计总数
            count_statement = select(func.count(PromptTemplate.id))
            if query.test_type:
                count_statement = count_statement.where(PromptTemplate.test_type == query.test_type)
            if query.template_type:
                count_statement = count_statement.where(PromptTemplate.template_type == query.template_type)
            if query.is_active is not None:
                count_statement = count_statement.where(PromptTemplate.is_active == query.is_active)
            total = session.exec(count_statement).one()
            
            return list(datas), total, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], 0, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_by_id(
        session: Session,
        id: int
    ) -> Tuple[Optional[PromptTemplate], Optional[str]]:
        """
        根据ID查询提示词模板
        
        Args:
            session: 数据库会话
            id: 模板ID
            
        Returns:
            (template, error_message) 元组
        """
        try:
            statement = select(PromptTemplate).where(PromptTemplate.id == id)
            data = session.exec(statement).first()
            return data, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return None, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_by_type(
        session: Session,
        test_type: str
    ) -> Tuple[List[PromptTemplate], Optional[str]]:
        """
        按测试类型获取所有激活的模板
        
        Args:
            session: 数据库会话
            test_type: 测试类型
            
        Returns:
            (templates, error_message) 元组
        """
        try:
            statement = select(PromptTemplate).where(
                (PromptTemplate.test_type == test_type) &
                (PromptTemplate.is_active == True)
            ).order_by(PromptTemplate.create_time)
            datas = session.exec(statement).all()
            return list(datas), None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_all(
        session: Session
    ) -> Tuple[List[PromptTemplate], Optional[str]]:
        """
        查询所有提示词模板
        
        Args:
            session: 数据库会话
            
        Returns:
            (templates, error_message) 元组
        """
        try:
            statement = select(PromptTemplate).order_by(PromptTemplate.create_time.desc())
            datas = session.exec(statement).all()
            return list(datas), None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def insert(
        session: Session,
        template: PromptTemplateCreate
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        新增提示词模板
        
        Args:
            session: 数据库会话
            template: 模板创建数据
            
        Returns:
            (template_id, error_message) 元组
        """
        try:
            data = PromptTemplate(**template.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
            session.add(data)
            session.commit()
            session.refresh(data)
            logger.info(f"新增提示词模板成功: {data.name}")
            return data.id, None
        except Exception as e:
            session.rollback()
            logger.error(f"新增失败: {e}", exc_info=True)
            return None, f"添加失败:{e}"
    
    @staticmethod
    def update(
        session: Session,
        template: PromptTemplateUpdate
    ) -> Tuple[bool, str]:
        """
        更新提示词模板
        
        Args:
            session: 数据库会话
            template: 模板更新数据
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(PromptTemplate).where(PromptTemplate.id == template.id)
            db_template = session.exec(statement).first()
            if db_template:
                update_data = template.model_dump(exclude_unset=True, exclude={'id'})
                for key, value in update_data.items():
                    setattr(db_template, key, value)
                db_template.modify_time = datetime.now()
                session.commit()
                logger.info(f"更新提示词模板成功: {db_template.name}")
                return True, "修改成功"
            else:
                return False, "提示词模板不存在"
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
        删除提示词模板
        
        Args:
            session: 数据库会话
            id: 模板ID
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(PromptTemplate).where(PromptTemplate.id == id)
            data = session.exec(statement).first()
            if data:
                session.delete(data)
                session.commit()
                logger.info(f"删除提示词模板成功: {data.name}")
                return True, "删除成功"
            else:
                return False, "提示词模板不存在"
        except Exception as e:
            session.rollback()
            logger.error(f"删除失败: {e}", exc_info=True)
            return False, f"删除失败，请联系管理员:{e}"
    
    @staticmethod
    def toggle_active(
        session: Session,
        id: int
    ) -> Tuple[bool, str]:
        """
        切换模板激活/停用状态
        
        Args:
            session: 数据库会话
            id: 模板ID
            
        Returns:
            (success, message) 元组
        """
        try:
            template = session.get(PromptTemplate, id)
            if not template:
                return False, "提示词模板不存在"
            
            template.is_active = not template.is_active
            template.modify_time = datetime.now()
            session.commit()
            
            status = "激活" if template.is_active else "停用"
            logger.info(f"{status}提示词模板成功: {template.name}")
            return True, f"已{status}"
        except Exception as e:
            session.rollback()
            logger.error(f"切换状态失败: {e}", exc_info=True)
            return False, f"操作失败:{e}"
    
    @staticmethod
    def query_by_test_type(
        session: Session,
        test_type: str
    ) -> Tuple[List[PromptTemplate], Optional[str]]:
        """
        按测试类型查询模板
        
        Args:
            session: 数据库会话
            test_type: 测试类型
            
        Returns:
            (templates, error_message) 元组
        """
        try:
            statement = select(PromptTemplate).where(
                PromptTemplate.test_type == test_type,
                PromptTemplate.is_active == True
            ).order_by(PromptTemplate.create_time)
            datas = session.exec(statement).all()
            return list(datas), None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], f"服务器错误,请联系管理员:{e}"
