# -*- coding: utf-8 -*-
"""
AI绘画服务
Author: Assistant
Date: 2024-01-01
"""

import os
import json
import random
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.ai_painting import AIPainting, PaintingTemplate, PaintingCollection
from app.schemas.ai_painting import (
    PaintingRequest, PaintingResponse, PaintingHistoryResponse,
    PaintingStyleInfo, PaintingModelInfo, PaintingStatistics
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIPaintingService:
    """AI绘画服务"""

    def __init__(self, db: Optional[AsyncSession]):
        self.db = db

    async def generate_image(self, request: PaintingRequest, user_id: int) -> PaintingResponse:
        """生成AI图片"""
        try:
            # 创建绘画记录
            painting = AIPainting(
                user_id=user_id,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                style=request.style,
                size=request.size,
                model_name=request.model_name,
                seed=request.seed if request.seed != -1 else random.randint(0, 2147483647),
                steps=request.steps,
                cfg_scale=request.cfg_scale,
                sampler=request.sampler,
                status="generating"
            )

            self.db.add(painting)
            await self.db.commit()
            await self.db.refresh(painting)

            # 模拟AI绘画过程（实际应该调用真实的AI绘画API）
            start_time = datetime.now()
            await self._simulate_painting_generation(painting)
            generation_time = (datetime.now() - start_time).total_seconds()

            # 更新绘画记录
            painting.status = "completed"
            painting.generation_time = generation_time
            painting.cost = self._calculate_cost(request)
            painting.completed_at = datetime.now()
            
            # 模拟生成的图片信息
            width, height = self._parse_size(request.size)
            painting.width = width
            painting.height = height
            painting.file_size = width * height * 3  # 简单估算
            painting.image_url = f"https://example.com/images/{painting.id}.png"
            painting.thumbnail_url = f"https://example.com/thumbnails/{painting.id}.png"

            await self.db.commit()
            await self.db.refresh(painting)

            return PaintingResponse(
                id=painting.id,
                user_id=painting.user_id,
                prompt=painting.prompt,
                negative_prompt=painting.negative_prompt,
                style=painting.style,
                size=painting.size,
                model_name=painting.model_name,
                seed=painting.seed,
                steps=painting.steps,
                cfg_scale=painting.cfg_scale,
                sampler=painting.sampler,
                status=painting.status,
                image_url=painting.image_url,
                thumbnail_url=painting.thumbnail_url,
                generation_time=painting.generation_time,
                cost=painting.cost,
                width=painting.width,
                height=painting.height,
                file_size=painting.file_size,
                created_at=painting.created_at,
                updated_at=painting.updated_at,
                completed_at=painting.completed_at
            )

        except Exception as e:
            if painting:
                painting.status = "failed"
                await self.db.commit()
            logger.error(f"AI绘画生成失败: {str(e)}")
            raise

    async def _simulate_painting_generation(self, painting: AIPainting):
        """模拟绘画生成过程"""
        # 根据步数和复杂度模拟生成时间
        base_time = 2.0  # 基础时间2秒
        step_time = painting.steps * 0.1  # 每步0.1秒
        complexity_factor = len(painting.prompt) / 100  # 提示词复杂度
        
        total_time = base_time + step_time + complexity_factor
        await asyncio.sleep(min(total_time, 10))  # 最多等待10秒

    def _calculate_cost(self, request: PaintingRequest) -> float:
        """计算生成成本"""
        base_cost = 0.01  # 基础成本
        size_multiplier = self._get_size_multiplier(request.size)
        step_multiplier = request.steps / 20  # 20步为基准
        
        return base_cost * size_multiplier * step_multiplier

    def _get_size_multiplier(self, size: str) -> float:
        """获取尺寸倍数"""
        size_multipliers = {
            "512x512": 1.0,
            "768x768": 2.25,
            "1024x1024": 4.0,
            "1024x768": 3.0,
            "768x1024": 3.0
        }
        return size_multipliers.get(size, 1.0)

    def _parse_size(self, size: str) -> tuple:
        """解析尺寸字符串"""
        try:
            width, height = map(int, size.split('x'))
            return width, height
        except:
            return 512, 512

    async def get_painting_history(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10,
        style: Optional[str] = None
    ) -> PaintingHistoryResponse:
        """获取绘画历史"""
        try:
            # 构建查询条件
            conditions = [AIPainting.user_id == user_id]
            if style:
                conditions.append(AIPainting.style == style)

            # 查询总数
            count_stmt = select(func.count(AIPainting.id)).where(and_(*conditions))
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 查询数据
            stmt = (
                select(AIPainting)
                .where(and_(*conditions))
                .offset((page - 1) * page_size)
                .limit(page_size)
                .order_by(AIPainting.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            paintings = result.scalars().all()

            painting_responses = [
                PaintingResponse(
                    id=p.id,
                    user_id=p.user_id,
                    prompt=p.prompt,
                    negative_prompt=p.negative_prompt,
                    style=p.style,
                    size=p.size,
                    model_name=p.model_name,
                    seed=p.seed,
                    steps=p.steps,
                    cfg_scale=p.cfg_scale,
                    sampler=p.sampler,
                    status=p.status,
                    image_url=p.image_url,
                    thumbnail_url=p.thumbnail_url,
                    generation_time=p.generation_time,
                    cost=p.cost,
                    width=p.width,
                    height=p.height,
                    file_size=p.file_size,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    completed_at=p.completed_at
                )
                for p in paintings
            ]

            return PaintingHistoryResponse(
                paintings=painting_responses,
                total=total,
                page=page,
                page_size=page_size,
                pages=(total + page_size - 1) // page_size
            )

        except Exception as e:
            logger.error(f"获取绘画历史失败: {str(e)}")
            raise

    async def get_painting_detail(self, painting_id: str, user_id: int) -> Optional[PaintingResponse]:
        """获取绘画详情"""
        try:
            stmt = select(AIPainting).where(
                and_(
                    AIPainting.id == painting_id,
                    AIPainting.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            painting = result.scalar_one_or_none()
            
            if not painting:
                return None

            return PaintingResponse(
                id=painting.id,
                user_id=painting.user_id,
                prompt=painting.prompt,
                negative_prompt=painting.negative_prompt,
                style=painting.style,
                size=painting.size,
                model_name=painting.model_name,
                seed=painting.seed,
                steps=painting.steps,
                cfg_scale=painting.cfg_scale,
                sampler=painting.sampler,
                status=painting.status,
                image_url=painting.image_url,
                thumbnail_url=painting.thumbnail_url,
                generation_time=painting.generation_time,
                cost=painting.cost,
                width=painting.width,
                height=painting.height,
                file_size=painting.file_size,
                created_at=painting.created_at,
                updated_at=painting.updated_at,
                completed_at=painting.completed_at
            )

        except Exception as e:
            logger.error(f"获取绘画详情失败: {str(e)}")
            raise

    async def delete_painting(self, painting_id: str, user_id: int):
        """删除绘画记录"""
        try:
            stmt = select(AIPainting).where(
                and_(
                    AIPainting.id == painting_id,
                    AIPainting.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            painting = result.scalar_one_or_none()
            
            if not painting:
                raise ValueError("绘画记录不存在")

            await self.db.delete(painting)
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除绘画记录失败: {str(e)}")
            raise

    async def regenerate_image(self, painting_id: str, user_id: int) -> PaintingResponse:
        """重新生成图片"""
        try:
            # 获取原始绘画记录
            stmt = select(AIPainting).where(
                and_(
                    AIPainting.id == painting_id,
                    AIPainting.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            original_painting = result.scalar_one_or_none()
            
            if not original_painting:
                raise ValueError("绘画记录不存在")

            # 创建新的绘画请求
            request = PaintingRequest(
                prompt=original_painting.prompt,
                negative_prompt=original_painting.negative_prompt,
                style=original_painting.style,
                size=original_painting.size,
                model_name=original_painting.model_name,
                seed=-1,  # 使用新的随机种子
                steps=original_painting.steps,
                cfg_scale=original_painting.cfg_scale,
                sampler=original_painting.sampler
            )

            return await self.generate_image(request, user_id)

        except Exception as e:
            logger.error(f"重新生成图片失败: {str(e)}")
            raise

    def get_available_styles(self) -> List[PaintingStyleInfo]:
        """获取可用的绘画风格"""
        return [
            PaintingStyleInfo(
                key="realistic",
                name="写实风格",
                description="真实感强的写实风格，细节丰富",
                recommended_settings={"cfg_scale": 7.0, "steps": 30}
            ),
            PaintingStyleInfo(
                key="cartoon",
                name="卡通风格",
                description="可爱的卡通动漫风格",
                recommended_settings={"cfg_scale": 8.0, "steps": 25}
            ),
            PaintingStyleInfo(
                key="oil-painting",
                name="油画风格",
                description="古典油画的艺术风格",
                recommended_settings={"cfg_scale": 6.0, "steps": 35}
            ),
            PaintingStyleInfo(
                key="watercolor",
                name="水彩风格",
                description="清新的水彩画风格",
                recommended_settings={"cfg_scale": 5.5, "steps": 25}
            ),
            PaintingStyleInfo(
                key="sketch",
                name="素描风格",
                description="简洁的铅笔素描风格",
                recommended_settings={"cfg_scale": 6.5, "steps": 20}
            ),
            PaintingStyleInfo(
                key="sci-fi",
                name="科幻风格",
                description="未来感十足的科幻风格",
                recommended_settings={"cfg_scale": 8.5, "steps": 40}
            )
        ]

    def get_available_models(self) -> List[PaintingModelInfo]:
        """获取可用的绘画模型"""
        return [
            PaintingModelInfo(
                key="stable-diffusion",
                name="Stable Diffusion",
                description="通用的AI绘画模型，适合各种风格",
                version="1.5",
                supported_sizes=["512x512", "768x768", "1024x1024", "1024x768", "768x1024"],
                supported_styles=["realistic", "cartoon", "oil-painting", "watercolor", "sketch", "sci-fi"],
                max_steps=150,
                default_cfg_scale=7.0
            ),
            PaintingModelInfo(
                key="midjourney",
                name="Midjourney",
                description="专业的艺术创作模型，画质优秀",
                version="5.2",
                supported_sizes=["1024x1024", "1024x768", "768x1024"],
                supported_styles=["realistic", "oil-painting", "sci-fi"],
                max_steps=100,
                default_cfg_scale=6.0
            ),
            PaintingModelInfo(
                key="dall-e",
                name="DALL-E",
                description="OpenAI开发的图像生成模型",
                version="3",
                supported_sizes=["1024x1024", "1024x768", "768x1024"],
                supported_styles=["realistic", "cartoon", "watercolor"],
                max_steps=50,
                default_cfg_scale=5.0
            )
        ]
