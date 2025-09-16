# Copyright (c) 2025 左岚. All rights reserved.
"""
AI模型Repository
处理AI模型相关的数据访问操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.entity.ai_model import AIModel, ModelProvider, ModelType, ModelStatus
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIModelRepository(BaseRepository[AIModel]):
    """AI模型Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, AIModel)

    def find_by_name(self, name: str) -> Optional[AIModel]:
        """根据名称查找模型"""
        try:
            model = self.db.query(AIModel).filter(
                and_(AIModel.name == name, AIModel.is_deleted == 0)
            ).first()
            
            logger.debug(f"Found model by name '{name}': {model is not None}")
            return model
        except Exception as e:
            logger.error(f"Error finding model by name '{name}': {str(e)}")
            raise

    def find_by_provider(self, provider: str) -> List[AIModel]:
        """根据提供商查找模型"""
        try:
            models = self.db.query(AIModel).filter(
                and_(AIModel.provider == provider, AIModel.is_deleted == 0)
            ).all()
            
            logger.debug(f"Found {len(models)} models from provider '{provider}'")
            return models
        except Exception as e:
            logger.error(f"Error finding models by provider '{provider}': {str(e)}")
            raise

    def find_active_models(self) -> List[AIModel]:
        """查找激活的模型"""
        try:
            models = self.db.query(AIModel).filter(
                and_(AIModel.status == ModelStatus.ACTIVE.value, AIModel.is_deleted == 0)
            ).all()
            
            logger.debug(f"Found {len(models)} active models")
            return models
        except Exception as e:
            logger.error(f"Error finding active models: {str(e)}")
            raise

    def search(self, keyword: str = None, provider: str = None, model_type: str = None,
               status: str = None, created_by_id: int = None,
               start_date: datetime = None, end_date: datetime = None,
               skip: int = 0, limit: int = 100) -> tuple[List[AIModel], int]:
        """搜索AI模型"""
        try:
            query = self.db.query(AIModel).filter(AIModel.is_deleted == 0)
            
            # 关键词搜索
            if keyword:
                keyword_filter = or_(
                    AIModel.name.ilike(f'%{keyword}%'),
                    AIModel.display_name.ilike(f'%{keyword}%'),
                    AIModel.description.ilike(f'%{keyword}%')
                )
                query = query.filter(keyword_filter)
            
            # 提供商筛选
            if provider:
                query = query.filter(AIModel.provider == provider)
            
            # 类型筛选
            if model_type:
                query = query.filter(AIModel.model_type == model_type)
            
            # 状态筛选
            if status:
                query = query.filter(AIModel.status == status)
            
            # 创建者筛选
            if created_by_id:
                query = query.filter(AIModel.created_by_id == created_by_id)
            
            # 时间范围筛选
            if start_date:
                query = query.filter(AIModel.created_at >= start_date)
            if end_date:
                query = query.filter(AIModel.created_at <= end_date)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            models = query.order_by(desc(AIModel.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Search found {len(models)} models (total: {total})")
            return models, total
            
        except Exception as e:
            logger.error(f"Error searching models: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """获取AI模型统计信息"""
        try:
            # 基本统计
            total_models = self.count()
            
            # 按状态统计
            status_counts = {}
            for status in ModelStatus:
                count = self.db.query(func.count(AIModel.id)).filter(
                    and_(AIModel.status == status.value, AIModel.is_deleted == 0)
                ).scalar()
                status_counts[status.value] = count
            
            # 按提供商统计
            provider_counts = {}
            for provider in ModelProvider:
                count = self.db.query(func.count(AIModel.id)).filter(
                    and_(AIModel.provider == provider.value, AIModel.is_deleted == 0)
                ).scalar()
                provider_counts[provider.value] = count
            
            # 按类型统计
            type_counts = {}
            for model_type in ModelType:
                count = self.db.query(func.count(AIModel.id)).filter(
                    and_(AIModel.model_type == model_type.value, AIModel.is_deleted == 0)
                ).scalar()
                type_counts[model_type.value] = count
            
            # 使用统计
            total_usage_count = self.db.query(func.sum(AIModel.usage_count)).filter(
                AIModel.is_deleted == 0
            ).scalar() or 0
            
            total_tokens_consumed = self.db.query(func.sum(AIModel.total_tokens)).filter(
                AIModel.is_deleted == 0
            ).scalar() or 0
            
            total_cost = self.db.query(func.sum(AIModel.total_cost)).filter(
                AIModel.is_deleted == 0
            ).scalar() or 0.0
            
            # 平均值
            avg_cost_per_model = total_cost / total_models if total_models > 0 else 0.0
            avg_tokens_per_model = total_tokens_consumed / total_models if total_models > 0 else 0.0
            
            # 最常用模型
            most_used_models = self.db.query(AIModel).filter(
                AIModel.is_deleted == 0
            ).order_by(desc(AIModel.usage_count)).limit(5).all()
            
            most_used_data = [
                {
                    "id": model.id,
                    "name": model.name,
                    "provider": model.provider,
                    "usage_count": model.usage_count,
                    "total_cost": model.total_cost
                }
                for model in most_used_models
            ]
            
            # 费用明细
            cost_breakdown = {}
            for provider in ModelProvider:
                cost = self.db.query(func.sum(AIModel.total_cost)).filter(
                    and_(AIModel.provider == provider.value, AIModel.is_deleted == 0)
                ).scalar() or 0.0
                cost_breakdown[provider.value] = cost
            
            statistics = {
                "total_models": total_models,
                "active_models": status_counts.get(ModelStatus.ACTIVE.value, 0),
                "deprecated_models": status_counts.get(ModelStatus.DEPRECATED.value, 0),
                "maintenance_models": status_counts.get(ModelStatus.MAINTENANCE.value, 0),
                "models_by_provider": provider_counts,
                "models_by_type": type_counts,
                "models_by_status": status_counts,
                "total_usage_count": total_usage_count,
                "total_tokens_consumed": total_tokens_consumed,
                "total_cost": round(total_cost, 2),
                "avg_cost_per_model": round(avg_cost_per_model, 2),
                "avg_tokens_per_model": round(avg_tokens_per_model, 2),
                "most_used_models": most_used_data,
                "cost_breakdown": {k: round(v, 2) for k, v in cost_breakdown.items()}
            }
            
            logger.debug("Generated AI model statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting AI model statistics: {str(e)}")
            raise