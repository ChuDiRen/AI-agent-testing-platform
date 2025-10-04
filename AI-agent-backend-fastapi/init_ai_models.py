# Copyright (c) 2025 左岚. All rights reserved.
"""初始化AI模型配置"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.ai_chat import AIModel


async def init_ai_models():
    """初始化默认AI模型配置"""
    async with AsyncSessionLocal() as db:
        # 检查是否已有模型配置
        from sqlalchemy import select
        result = await db.execute(select(AIModel))
        existing_models = result.scalars().all()
        
        if existing_models:
            print("AI模型配置已存在，跳过初始化")
            return
        
        # 创建默认模型配置
        models = [
            AIModel(
                name="GPT-3.5 Turbo",
                provider="openai",
                model_key="gpt-3.5-turbo",
                api_base="https://api.openai.com/v1",
                max_tokens=4096,
                temperature="0.7",
                is_enabled=False,  # 默认禁用，需要配置API Key后启用
                description="OpenAI GPT-3.5 Turbo模型，适合日常对话和测试用例生成"
            ),
            AIModel(
                name="GPT-4",
                provider="openai",
                model_key="gpt-4",
                api_base="https://api.openai.com/v1",
                max_tokens=8192,
                temperature="0.7",
                is_enabled=False,
                description="OpenAI GPT-4模型，更强大的推理能力"
            ),
            AIModel(
                name="Claude 3 Sonnet",
                provider="claude",
                model_key="claude-3-sonnet-20240229",
                api_base="https://api.anthropic.com/v1",
                max_tokens=4096,
                temperature="0.7",
                is_enabled=False,
                description="Anthropic Claude 3 Sonnet模型，平衡性能和成本"
            ),
            AIModel(
                name="本地模拟模型",
                provider="local",
                model_key="local-mock",
                max_tokens=4096,
                temperature="0.7",
                is_enabled=True,  # 默认启用
                description="本地模拟AI模型，用于测试和演示，无需API Key"
            )
        ]
        
        for model in models:
            db.add(model)
        
        await db.commit()
        print(f"成功初始化 {len(models)} 个AI模型配置")
        print("\n默认模型列表:")
        for model in models:
            status = "✓ 已启用" if model.is_enabled else "✗ 未启用"
            print(f"  {status} - {model.name} ({model.provider})")
        
        print("\n提示:")
        print("  1. 本地模拟模型已启用，可直接使用")
        print("  2. 如需使用OpenAI或Claude模型，请配置API Key并启用")
        print("  3. 可通过 /api/v1/ai/models 接口查看和管理模型配置")


if __name__ == "__main__":
    asyncio.run(init_ai_models())

