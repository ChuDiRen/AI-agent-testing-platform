"""
DatabaseModelService - 数据库模型配置服务

从数据库获取AI模型配置和提示词模板
"""
import logging
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class DatabaseModelService:
    """数据库模型配置服务"""

    @staticmethod
    def get_enabled_model(session: Session, model_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        获取启用的AI模型配置
        
        Args:
            session: 数据库会话
            model_id: 模型ID，如果为None则获取第一个启用的模型
            
        Returns:
            模型配置字典或None
        """
        from aiassistant.model.AiModel import AiModel
        
        try:
            if model_id:
                model = session.get(AiModel, model_id)
                if model and model.is_enabled:
                    return DatabaseModelService._model_to_dict(model)
            else:
                # 获取第一个启用的模型
                query = select(AiModel).where(AiModel.is_enabled == True).limit(1)
                model = session.exec(query).first()
                if model:
                    return DatabaseModelService._model_to_dict(model)
        except Exception as e:
            logger.error(f"Failed to get model from database: {e}")
        
        return None

    @staticmethod
    def get_model_by_provider(session: Session, provider: str) -> Optional[Dict[str, Any]]:
        """
        按提供商获取模型配置
        
        Args:
            session: 数据库会话
            provider: 提供商名称
            
        Returns:
            模型配置字典或None
        """
        from aiassistant.model.AiModel import AiModel
        
        try:
            query = select(AiModel).where(
                (AiModel.provider == provider) &
                (AiModel.is_enabled == True)
            ).limit(1)
            model = session.exec(query).first()
            if model:
                return DatabaseModelService._model_to_dict(model)
        except Exception as e:
            logger.error(f"Failed to get model by provider: {e}")
        
        return None

    @staticmethod
    def get_all_enabled_models(session: Session) -> List[Dict[str, Any]]:
        """
        获取所有启用的模型
        
        Args:
            session: 数据库会话
            
        Returns:
            模型配置列表
        """
        from aiassistant.model.AiModel import AiModel
        
        try:
            query = select(AiModel).where(AiModel.is_enabled == True)
            models = session.exec(query).all()
            return [DatabaseModelService._model_to_dict(m) for m in models]
        except Exception as e:
            logger.error(f"Failed to get all models: {e}")
            return []

    @staticmethod
    def _model_to_dict(model) -> Dict[str, Any]:
        """将模型对象转换为字典"""
        return {
            "id": model.id,
            "model_name": model.model_name,
            "model_code": model.model_code,
            "provider": model.provider,
            "api_url": model.api_url,
            "api_key": model.api_key,
            "is_enabled": model.is_enabled,
            "description": model.description,
        }

    @staticmethod
    def get_prompt_template(
        session: Session,
        agent_type: str,
        test_type: str = "API"
    ) -> Optional[str]:
        """
        获取智能体的提示词模板
        
        Args:
            session: 数据库会话
            agent_type: 智能体类型 (analyzer/designer/writer/reviewer)
            test_type: 测试类型 (API/Web/App)
            
        Returns:
            提示词内容或None
        """
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        try:
            # 映射agent_type到template_type
            template_type_map = {
                "analyzer": "analyzer",
                "designer": "designer", 
                "writer": "writer",
                "reviewer": "reviewer",
            }
            template_type = template_type_map.get(agent_type, agent_type)
            
            # 首先尝试获取特定测试类型的模板
            query = select(PromptTemplate).where(
                (PromptTemplate.template_type == template_type) &
                (PromptTemplate.test_type == test_type) &
                (PromptTemplate.is_active == True)
            ).order_by(PromptTemplate.create_time.desc()).limit(1)
            
            template = session.exec(query).first()
            
            # 如果没有特定类型的模板，尝试获取通用模板
            if not template:
                query = select(PromptTemplate).where(
                    (PromptTemplate.template_type == template_type) &
                    (PromptTemplate.test_type == "通用") &
                    (PromptTemplate.is_active == True)
                ).order_by(PromptTemplate.create_time.desc()).limit(1)
                template = session.exec(query).first()
            
            if template:
                return template.content
                
        except Exception as e:
            logger.error(f"Failed to get prompt template: {e}")
        
        return None

    @staticmethod
    def get_all_prompts_for_test_type(
        session: Session,
        test_type: str = "API"
    ) -> Dict[str, str]:
        """
        获取指定测试类型的所有智能体提示词
        
        Args:
            session: 数据库会话
            test_type: 测试类型
            
        Returns:
            {agent_type: prompt_content} 字典
        """
        prompts = {}
        for agent_type in ["analyzer", "designer", "writer", "reviewer"]:
            prompt = DatabaseModelService.get_prompt_template(session, agent_type, test_type)
            if prompt:
                prompts[agent_type] = prompt
        return prompts
