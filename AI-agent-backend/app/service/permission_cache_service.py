# Copyright (c) 2025 左岚. All rights reserved.
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.logger import get_logger
from .base import BaseService

logger = get_logger(__name__)

class PermissionCacheService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        logger.info('PermissionCacheService initialized')
    
    def get_cache_stats(self) -> Dict[str, Any]:
        return {'total_keys': 0, 'cache_type': 'memory'}
    
    def refresh_cache(self) -> bool:
        return True
    
    def get_cache_config(self) -> Dict[str, Any]:
        return {'cache_type': 'memory', 'default_ttl': 3600}
    
    def update_cache_config(self, config: Dict[str, Any]) -> bool:
        return True

    def _create_entity_from_data(self, data: Dict[str, Any]):
        """实现BaseService的抽象方法"""
        return data
