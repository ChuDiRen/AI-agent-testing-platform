"""
AI模型服务层
"""
import logging
from datetime import datetime
from typing import Optional, List, Tuple

import httpx
from sqlmodel import select, Session, func

from ..model.AiModel import AiModel
from ..schemas.ai_model_schema import AiModelQuery, AiModelCreate, AiModelUpdate

logger = logging.getLogger(__name__)


class AiModelService:
    """AI模型服务"""
    
    @staticmethod
    def query_by_page(
        session: Session,
        query: AiModelQuery
    ) -> Tuple[List[AiModel], int, Optional[str]]:
        """
        分页查询AI模型
        
        Args:
            session: 数据库会话
            query: 查询参数
            
        Returns:
            (models, total, error_message) 元组
        """
        try:
            offset = (query.page - 1) * query.pageSize
            statement = select(AiModel)
            
            # 按提供商过滤
            if query.provider:
                statement = statement.where(AiModel.provider == query.provider)
            
            # 按状态过滤
            if query.is_enabled is not None:
                statement = statement.where(AiModel.is_enabled == query.is_enabled)
            
            statement = statement.order_by(AiModel.create_time.desc()).limit(query.pageSize).offset(offset)
            datas = session.exec(statement).all()
            
            # 统计总数
            count_statement = select(func.count(AiModel.id))
            if query.provider:
                count_statement = count_statement.where(AiModel.provider == query.provider)
            if query.is_enabled is not None:
                count_statement = count_statement.where(AiModel.is_enabled == query.is_enabled)
            total = session.exec(count_statement).one()
            
            return list(datas), total, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], 0, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_by_id(
        session: Session,
        id: int
    ) -> Tuple[Optional[AiModel], Optional[str]]:
        """
        根据ID查询AI模型
        
        Args:
            session: 数据库会话
            id: 模型ID
            
        Returns:
            (model, error_message) 元组
        """
        try:
            statement = select(AiModel).where(AiModel.id == id)
            data = session.exec(statement).first()
            return data, None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return None, f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def query_enabled(
        session: Session
    ) -> Tuple[List[AiModel], Optional[str]]:
        """
        查询所有已启用的模型
        
        Args:
            session: 数据库会话
            
        Returns:
            (models, error_message) 元组
        """
        try:
            statement = select(AiModel).where(AiModel.is_enabled == True).order_by(AiModel.create_time)
            datas = session.exec(statement).all()
            return list(datas), None
        except Exception as e:
            logger.error(f"查询失败: {e}", exc_info=True)
            return [], f"服务器错误,请联系管理员:{e}"
    
    @staticmethod
    def insert(
        session: Session,
        model: AiModelCreate
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        新增AI模型
        
        Args:
            session: 数据库会话
            model: 模型创建数据
            
        Returns:
            (model_id, error_message) 元组
        """
        try:
            # 检查模型代码是否重复
            existing = session.exec(
                select(AiModel).where(AiModel.model_code == model.model_code)
            ).first()
            if existing:
                return None, "模型代码已存在"
            
            data = AiModel(**model.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
            session.add(data)
            session.commit()
            session.refresh(data)
            logger.info(f"新增AI模型成功: {data.model_name}")
            return data.id, None
        except Exception as e:
            session.rollback()
            logger.error(f"新增失败: {e}", exc_info=True)
            return None, f"添加失败:{e}"
    
    @staticmethod
    def update(
        session: Session,
        model: AiModelUpdate
    ) -> Tuple[bool, str]:
        """
        更新AI模型
        
        Args:
            session: 数据库会话
            model: 模型更新数据
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(AiModel).where(AiModel.id == model.id)
            db_model = session.exec(statement).first()
            if db_model:
                update_data = model.model_dump(exclude_unset=True, exclude={'id'})
                for key, value in update_data.items():
                    setattr(db_model, key, value)
                db_model.modify_time = datetime.now()
                session.commit()
                logger.info(f"更新AI模型成功: {db_model.model_name}")
                return True, "修改成功"
            else:
                return False, "AI模型不存在"
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
        删除AI模型
        
        Args:
            session: 数据库会话
            id: 模型ID
            
        Returns:
            (success, message) 元组
        """
        try:
            statement = select(AiModel).where(AiModel.id == id)
            data = session.exec(statement).first()
            if data:
                session.delete(data)
                session.commit()
                logger.info(f"删除AI模型成功: {data.model_name}")
                return True, "删除成功"
            else:
                return False, "AI模型不存在"
        except Exception as e:
            session.rollback()
            logger.error(f"删除失败: {e}", exc_info=True)
            return False, f"删除失败，请联系管理员:{e}"
    
    @staticmethod
    def toggle_status(
        session: Session,
        id: int
    ) -> Tuple[bool, str]:
        """
        切换模型启用/禁用状态
        
        Args:
            session: 数据库会话
            id: 模型ID
            
        Returns:
            (success, message) 元组
        """
        try:
            model = session.get(AiModel, id)
            if not model:
                return False, "AI模型不存在"
            
            model.is_enabled = not model.is_enabled
            model.modify_time = datetime.now()
            session.commit()
            
            status = "启用" if model.is_enabled else "禁用"
            logger.info(f"{status}AI模型成功: {model.model_name}")
            return True, f"已{status}"
        except Exception as e:
            session.rollback()
            logger.error(f"切换状态失败: {e}", exc_info=True)
            return False, f"操作失败:{e}"
    
    @staticmethod
    async def test_connection(
        session: Session,
        id: int
    ) -> Tuple[bool, str]:
        """
        测试模型API连接
        
        Args:
            session: 数据库会话
            id: 模型ID
            
        Returns:
            (success, message) 元组
        """
        try:
            model = session.get(AiModel, id)
            if not model:
                return False, "AI模型不存在"
            
            if not model.api_key:
                return False, "请先配置API Key"
            
            # 发送测试请求
            test_message = [{"role": "user", "content": "Hi"}]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 通用OpenAI兼容接口
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {model.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"连接测试成功: {model.model_name}")
                    return True, "连接测试成功"
                else:
                    error_detail = ""
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", "") or str(error_data)
                    except:
                        error_detail = response.text[:200]
                    logger.warning(f"连接测试失败: {model.model_name}, status: {response.status_code}, detail: {error_detail}")
                    return False, f"连接失败({response.status_code}): {error_detail}"
        
        except httpx.TimeoutException:
            logger.error(f"连接超时: {model.model_name}")
            return False, "连接超时，请检查网络或API地址"
        except httpx.ConnectError as e:
            logger.error(f"连接错误: {model.model_name}, {e}")
            return False, "无法连接到API服务器，请检查API地址"
        except Exception as e:
            logger.error(f"测试失败: {e}", exc_info=True)
            return False, f"测试失败: {str(e)}"
