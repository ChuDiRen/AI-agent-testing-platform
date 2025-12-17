"""
AI模型同步服务
支持从SiliconFlow等平台自动同步最新模型列表
"""
import httpx
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set

from sqlmodel import Session, select
from ..model.AiModel import AiModel

logger = logging.getLogger(__name__)


class ModelSyncService:
    """模型同步服务"""
    
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
    
    # 模型类型映射，用于识别主要模型类型
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
    ) -> Dict[str, any]:
        """
        从指定提供商同步模型列表
        
        Args:
            provider: 提供商名称 (siliconflow, deepseek, openai, qwen, zhipuai)
            api_key: API密钥，如果为None则从环境变量获取
            session: 数据库会话，如果为None则创建新会话
            update_existing: 是否更新已存在的模型
            
        Returns:
            包含同步结果的字典
        """
        result = {
            "success": False,
            "message": "",
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "total": 0,
            "models": []
        }
        
        # 检查提供商是否支持
        if provider not in cls.PROVIDER_CONFIGS:
            result["message"] = f"不支持的提供商: {provider}"
            return result
        
        provider_config = cls.PROVIDER_CONFIGS[provider]
        
        # 获取API密钥
        if not api_key:
            import os
            api_key = os.getenv(provider_config["api_key_env"])
            if not api_key:
                result["message"] = f"未找到API密钥，请设置环境变量 {provider_config['api_key_env']}"
                return result
        
        try:
            # 获取模型列表
            models = await cls._fetch_models_from_api(
                provider_config["api_url"], 
                api_key,
                provider
            )
            
            if not models:
                result["message"] = "未获取到任何模型"
                return result
            
            result["total"] = len(models)
            
            # 处理数据库会话
            close_session = False
            if not session:
                from core.database import engine
                session = Session(engine)
                close_session = True
            
            try:
                # 处理每个模型
                for model_data in models:
                    model_result = cls._process_model(
                        model_data, 
                        provider, 
                        provider_config, 
                        session, 
                        update_existing
                    )
                    
                    if model_result["action"] == "added":
                        result["added"] += 1
                    elif model_result["action"] == "updated":
                        result["updated"] += 1
                    else:
                        result["skipped"] += 1
                    
                    result["models"].append(model_result)
                
                # 提交事务
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
    async def _fetch_models_from_api(
        cls, 
        api_url: str, 
        api_key: str, 
        provider: str
    ) -> List[Dict[str, any]]:
        """从API获取模型列表"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 针对不同提供商的特殊处理
        if provider == "qwen":
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # 解析响应数据
                if provider in ["siliconflow", "deepseek", "openai"]:
                    # 标准OpenAI兼容格式
                    return data.get("data", [])
                elif provider == "qwen":
                    # 阿里云通义千问格式
                    return data.get("data", [])
                elif provider == "zhipuai":
                    # 智谱AI格式
                    return data.get("data", [])
                else:
                    return []
                    
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
        model_data: Dict[str, any], 
        provider: str, 
        provider_config: Dict[str, any],
        session: Session,
        update_existing: bool
    ) -> Dict[str, any]:
        """处理单个模型数据"""
        model_id = model_data.get("id", "")
        
        # 检查模型是否已存在
        existing_model = session.exec(
            select(AiModel).where(
                (AiModel.model_code == model_id) & 
                (AiModel.provider == provider)
            )
        ).first()
        
        # 确定模型类型
        model_type = cls._determine_model_type(model_id)
        
        # 准备模型数据
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
                # 更新现有模型
                for key, value in model_info.items():
                    if key != "api_key":  # 不更新API密钥
                        setattr(existing_model, key, value)
                
                result["action"] = "updated"
                result["message"] = "已更新现有模型"
            else:
                result["message"] = "模型已存在，跳过更新"
        else:
            # 创建新模型
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
        
        # 默认为文本类型
        return "text"
    
    @classmethod
    def _generate_model_name(cls, model_id: str, provider: str) -> str:
        """生成模型名称"""
        # 移除提供商前缀
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
            # 处理斜杠分隔的名称
            if "/" in model_id:
                parts = model_id.split("/")
                model_name = parts[-1].replace("-", " ").replace("_", " ")
            else:
                model_name = model_id.replace("-", " ").replace("_", " ")
        
        # 添加提供商前缀
        display_name = f"{provider.title()} {model_name.title()}"
        
        return display_name
    
    @classmethod
    async def sync_all_providers(
        cls, 
        api_keys: Optional[Dict[str, str]] = None,
        session: Optional[Session] = None
    ) -> Dict[str, any]:
        """
        同步所有支持的提供商模型
        
        Args:
            api_keys: 各提供商的API密钥字典，格式为 {provider: api_key}
            session: 数据库会话
            
        Returns:
            包含所有同步结果的字典
        """
        results = {
            "success": True,
            "message": "",
            "total_added": 0,
            "total_updated": 0,
            "total_skipped": 0,
            "providers": {}
        }
        
        providers = cls.PROVIDER_CONFIGS.keys()
        
        for provider in providers:
            api_key = api_keys.get(provider) if api_keys else None
            
            logger.info(f"开始同步 {provider} 模型...")
            provider_result = await cls.sync_models_from_provider(
                provider, 
                api_key, 
                session
            )
            
            results["providers"][provider] = provider_result
            
            # 统计总数
            results["total_added"] += provider_result["added"]
            results["total_updated"] += provider_result["updated"]
            results["total_skipped"] += provider_result["skipped"]
            
            # 检查是否有提供商同步失败
            if not provider_result["success"]:
                results["success"] = False
                
                if not results["message"]:
                    results["message"] = f"{provider} 同步失败: {provider_result['message']}"
                else:
                    results["message"] += f"\n{provider} 同步失败: {provider_result['message']}"
        
        if results["success"]:
            results["message"] = f"全部同步完成: 新增 {results['total_added']} 个，更新 {results['total_updated']} 个，跳过 {results['total_skipped']} 个"
        
        return results