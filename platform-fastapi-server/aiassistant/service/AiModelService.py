"""
AI模型服务层
包含模型CRUD和从提供商同步模型功能
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any

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

    # ==================== 模型同步功能 ====================
    
    # 各提供商的API配置
    PROVIDER_CONFIGS = {
        "siliconflow": {
            "api_url": "https://api.siliconflow.cn/v1/models",
            "api_key_env": "SILICONFLOW_API_KEY",
            "default_base_url": "https://api.siliconflow.cn/v1",
            "default_api_url": "https://api.siliconflow.cn/v1/chat/completions"
        },
        "deepseek": {
            "api_url": "https://api.deepseek.com/v1/models",
            "api_key_env": "DEEPSEEK_API_KEY",
            "default_base_url": "https://api.deepseek.com/v1",
            "default_api_url": "https://api.deepseek.com/v1/chat/completions"
        },
        "openai": {
            "api_url": "https://api.openai.com/v1/models",
            "api_key_env": "OPENAI_API_KEY",
            "default_base_url": "https://api.openai.com/v1",
            "default_api_url": "https://api.openai.com/v1/chat/completions"
        },
        "qwen": {
            "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
            "api_key_env": "QWEN_API_KEY",
            "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "default_api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        },
        "zhipuai": {
            "api_url": "https://open.bigmodel.cn/api/paas/v4/models",
            "api_key_env": "ZHIPUAI_API_KEY",
            "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
            "default_api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        }
    }
    
    # 模型类型映射
    MODEL_TYPE_MAPPING = {
        "text": ["chat", "completion", "generation", "instruct"],
        "image": ["image", "vision", "multimodal"],
        "audio": ["audio", "speech", "tts", "stt"],
        "embedding": ["embedding", "vector"],
        "reranker": ["rerank", "reranker"]
    }
    
    # 模型描述模板
    MODEL_DESCRIPTIONS = {
        "text": "文本生成模型，支持对话和文本生成任务",
        "image": "图像处理模型，支持图像生成和理解",
        "audio": "音频处理模型，支持语音转文本和文本转语音",
        "embedding": "文本嵌入模型，用于向量化和语义搜索",
        "reranker": "重排序模型，用于优化搜索结果排序"
    }
    
    @classmethod
    async def sync_models_from_provider(
        cls, 
        provider: str, 
        api_key: Optional[str] = None,
        session: Optional[Session] = None,
        update_existing: bool = True
    ) -> Dict[str, Any]:
        """从指定提供商同步模型列表"""
        result = {
            "success": False,
            "message": "",
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "total": 0,
            "models": []
        }
        
        if provider not in cls.PROVIDER_CONFIGS:
            result["message"] = f"不支持的提供商: {provider}"
            return result
        
        provider_config = cls.PROVIDER_CONFIGS[provider]
        
        if not api_key:
            api_key = os.getenv(provider_config["api_key_env"])
            if not api_key:
                result["message"] = f"未找到API密钥，请设置环境变量 {provider_config['api_key_env']}"
                return result
        
        try:
            models = await cls._fetch_models_from_api(
                provider_config["api_url"], 
                api_key,
                provider
            )
            
            if not models:
                result["message"] = "未获取到任何模型"
                return result
            
            result["total"] = len(models)
            
            close_session = False
            if not session:
                from core.database import engine
                session = Session(engine)
                close_session = True
            
            try:
                for model_data in models:
                    model_result = cls._process_model(
                        model_data, provider, provider_config, session, update_existing
                    )
                    
                    if model_result["action"] == "added":
                        result["added"] += 1
                    elif model_result["action"] == "updated":
                        result["updated"] += 1
                    else:
                        result["skipped"] += 1
                    
                    result["models"].append(model_result)
                
                session.commit()
                result["success"] = True
                result["message"] = f"同步完成: 新增 {result['added']} 个，更新 {result['updated']} 个，跳过 {result['skipped']} 个"
                
            except Exception as e:
                session.rollback()
                result["message"] = f"数据库操作失败: {str(e)}"
                raise
            finally:
                if close_session:
                    session.close()
                    
        except Exception as e:
            logger.error(f"同步模型失败: {provider}, {str(e)}")
            result["message"] = f"同步失败: {str(e)}"
        
        return result
    
    @classmethod
    async def _fetch_models_from_api(cls, api_url: str, api_key: str, provider: str) -> List[Dict[str, Any]]:
        """从API获取模型列表"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"API请求失败: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += f", {error_data.get('error', {}).get('message', '')}"
            except:
                pass
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"获取模型列表失败: {str(e)}")
    
    @classmethod
    def _process_model(
        cls, 
        model_data: Dict[str, Any], 
        provider: str, 
        provider_config: Dict[str, Any],
        session: Session,
        update_existing: bool
    ) -> Dict[str, Any]:
        """处理单个模型数据"""
        model_id = model_data.get("id", "")
        
        existing_model = session.exec(
            select(AiModel).where(
                (AiModel.model_code == model_id) & 
                (AiModel.provider == provider)
            )
        ).first()
        
        model_type = cls._determine_model_type(model_id)
        model_name = cls._generate_model_name(model_id, provider)
        description = cls.MODEL_DESCRIPTIONS.get(model_type, f"{provider} 模型")
        
        model_info = {
            "model_name": model_name,
            "model_code": model_id,
            "provider": provider,
            "api_url": provider_config["default_api_url"],
            "is_enabled": True,
            "description": description,
            "modify_time": datetime.now()
        }
        
        result = {
            "model_id": model_id,
            "model_name": model_name,
            "provider": provider,
            "action": "skipped",
            "message": ""
        }
        
        if existing_model:
            if update_existing:
                for key, value in model_info.items():
                    if key != "api_key":
                        setattr(existing_model, key, value)
                result["action"] = "updated"
                result["message"] = "已更新现有模型"
            else:
                result["message"] = "模型已存在，跳过更新"
        else:
            new_model = AiModel(**model_info)
            session.add(new_model)
            result["action"] = "added"
            result["message"] = "已添加新模型"
        
        return result
    
    @classmethod
    def _determine_model_type(cls, model_id: str) -> str:
        """根据模型ID确定模型类型"""
        model_id_lower = model_id.lower()
        for model_type, keywords in cls.MODEL_TYPE_MAPPING.items():
            for keyword in keywords:
                if keyword in model_id_lower:
                    return model_type
        return "text"
    
    @classmethod
    def _generate_model_name(cls, model_id: str, provider: str) -> str:
        """生成模型名称"""
        provider_prefixes = {
            "siliconflow": "siliconflow/",
            "deepseek": "deepseek-",
            "openai": "gpt-",
            "qwen": "qwen",
            "zhipuai": "glm-"
        }
        
        prefix = provider_prefixes.get(provider, "")
        if prefix and model_id.startswith(prefix):
            model_name = model_id[len(prefix):].replace("-", " ").replace("_", " ")
        else:
            if "/" in model_id:
                parts = model_id.split("/")
                model_name = parts[-1].replace("-", " ").replace("_", " ")
            else:
                model_name = model_id.replace("-", " ").replace("_", " ")
        
        return f"{provider.title()} {model_name.title()}"
    
    @classmethod
    async def sync_all_providers(
        cls, 
        api_keys: Optional[Dict[str, str]] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """同步所有支持的提供商模型"""
        results = {
            "success": True,
            "message": "",
            "total_added": 0,
            "total_updated": 0,
            "total_skipped": 0,
            "providers": {}
        }
        
        for provider in cls.PROVIDER_CONFIGS.keys():
            api_key = api_keys.get(provider) if api_keys else None
            
            logger.info(f"开始同步 {provider} 模型...")
            provider_result = await cls.sync_models_from_provider(
                provider, api_key, session
            )
            
            results["providers"][provider] = provider_result
            results["total_added"] += provider_result["added"]
            results["total_updated"] += provider_result["updated"]
            results["total_skipped"] += provider_result["skipped"]
            
            if not provider_result["success"]:
                results["success"] = False
                if not results["message"]:
                    results["message"] = f"{provider} 同步失败: {provider_result['message']}"
                else:
                    results["message"] += f"\n{provider} 同步失败: {provider_result['message']}"
        
        if results["success"]:
            results["message"] = f"全部同步完成: 新增 {results['total_added']} 个，更新 {results['total_updated']} 个，跳过 {results['total_skipped']} 个"
        
        return results
