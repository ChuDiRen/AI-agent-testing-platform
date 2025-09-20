# Copyright (c) 2025 左岚. All rights reserved.
"""
AI模型配置初始化脚本
创建主流AI模型的基础配置数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.entity.ai_model import AIModel, ModelProvider, ModelType, ModelStatus
from app.entity.user import User

logger = get_logger(__name__)


def create_ai_model_configs():
    """
    创建AI模型配置初始化数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建AI模型配置数据...")
        
        # 获取管理员用户ID
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.error("未找到管理员用户，请先运行基础初始化脚本")
            return
        
        # 创建AI模型配置
        models_data = [
            {
                "name": "gpt-4",
                "display_name": "GPT-4",
                "provider": ModelProvider.OPENAI.value,
                "model_type": ModelType.CHAT.value,
                "version": "gpt-4-0125-preview",
                "description": "OpenAI最先进的大语言模型，具有强大的推理和创作能力",
                "api_endpoint": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 4096,
                "temperature": 0.7,
                "pricing": {
                    "input_price_per_1k": 0.03,
                    "output_price_per_1k": 0.06,
                    "currency": "USD"
                },
                "config": {
                    "supports_functions": True,
                    "supports_vision": True,
                    "context_window": 128000,
                    "training_data_cutoff": "2024-04"
                }
            },
            {
                "name": "claude-3-sonnet",
                "display_name": "Claude 3 Sonnet",
                "provider": ModelProvider.ANTHROPIC.value,
                "model_type": ModelType.CHAT.value,
                "version": "claude-3-sonnet-20240229",
                "description": "Anthropic的Claude 3 Sonnet模型，平衡了性能和成本",
                "api_endpoint": "https://api.anthropic.com/v1/messages",
                "max_tokens": 4096,
                "temperature": 0.7,
                "pricing": {
                    "input_price_per_1k": 0.003,
                    "output_price_per_1k": 0.015,
                    "currency": "USD"
                },
                "config": {
                    "supports_functions": True,
                    "supports_vision": True,
                    "context_window": 200000,
                    "training_data_cutoff": "2024-02"
                }
            },
            {
                "name": "deepseek-chat",
                "display_name": "DeepSeek Chat",
                "provider": ModelProvider.DEEPSEEK.value,
                "model_type": ModelType.CHAT.value,
                "version": "deepseek-chat",
                "description": "DeepSeek的对话模型，性价比高，适合中文场景",
                "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
                "max_tokens": 4096,
                "temperature": 0.7,
                "pricing": {
                    "input_price_per_1k": 0.0014,
                    "output_price_per_1k": 0.0028,
                    "currency": "USD"
                },
                "config": {
                    "supports_functions": True,
                    "supports_vision": False,
                    "context_window": 32768,
                    "training_data_cutoff": "2024-01"
                }
            },
            {
                "name": "qwen-turbo",
                "display_name": "通义千问 Turbo",
                "provider": ModelProvider.QIANWEN.value,
                "model_type": ModelType.CHAT.value,
                "version": "qwen-turbo",
                "description": "阿里云通义千问Turbo模型，专为中文优化",
                "api_endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "max_tokens": 2048,
                "temperature": 0.7,
                "pricing": {
                    "input_price_per_1k": 0.0008,
                    "output_price_per_1k": 0.002,
                    "currency": "CNY"
                },
                "config": {
                    "supports_functions": True,
                    "supports_vision": False,
                    "context_window": 8192,
                    "training_data_cutoff": "2023-12"
                }
            },
            {
                "name": "text-embedding-ada-002",
                "display_name": "OpenAI Embedding Ada-002",
                "provider": ModelProvider.OPENAI.value,
                "model_type": ModelType.EMBEDDING.value,
                "version": "text-embedding-ada-002",
                "description": "OpenAI的文本嵌入模型，用于语义搜索和相似度计算",
                "api_endpoint": "https://api.openai.com/v1/embeddings",
                "max_tokens": 8191,
                "temperature": 0.0,
                "pricing": {
                    "input_price_per_1k": 0.0001,
                    "output_price_per_1k": 0.0,
                    "currency": "USD"
                },
                "config": {
                    "supports_functions": False,
                    "supports_vision": False,
                    "context_window": 8191,
                    "embedding_dimensions": 1536
                }
            }
        ]
        
        for model_data in models_data:
            # 检查模型是否已存在
            existing_model = db.query(AIModel).filter(AIModel.name == model_data["name"]).first()
            if existing_model:
                logger.info(f"模型 {model_data['name']} 已存在，跳过创建")
                continue
            
            # 创建模型配置
            model = AIModel(
                name=model_data["name"],
                display_name=model_data["display_name"],
                provider=model_data["provider"],
                model_type=model_data["model_type"],
                version=model_data["version"],
                description=model_data["description"],
                api_endpoint=model_data["api_endpoint"],
                api_key=None,  # 需要用户自己配置
                max_tokens=model_data["max_tokens"],
                temperature=model_data["temperature"],
                pricing=model_data["pricing"],
                config=model_data["config"],
                created_by_id=admin_user.id
            )
            
            db.add(model)
            logger.info(f"创建AI模型配置: {model_data['display_name']}")
        
        db.commit()
        logger.info("AI模型配置数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建AI模型配置数据失败: {str(e)}")
        raise
    finally:
        db.close()


def clear_ai_model_configs():
    """
    清除AI模型配置数据
    """
    db = SessionLocal()
    try:
        logger.info("开始清除AI模型配置数据...")
        
        # 删除所有AI模型配置
        model_names = ["gpt-4", "claude-3-sonnet", "deepseek-chat", "qwen-turbo", "text-embedding-ada-002"]
        for model_name in model_names:
            model = db.query(AIModel).filter(AIModel.name == model_name).first()
            if model:
                db.delete(model)
                logger.info(f"删除AI模型配置: {model_name}")
        
        db.commit()
        logger.info("AI模型配置数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除AI模型配置数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI模型配置初始化脚本")
    parser.add_argument("--create", action="store_true", help="创建AI模型配置数据")
    parser.add_argument("--clear", action="store_true", help="清除AI模型配置数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_ai_model_configs()
    elif args.clear:
        clear_ai_model_configs()
    else:
        print("请指定操作: --create 或 --clear")
