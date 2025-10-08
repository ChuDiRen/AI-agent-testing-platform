"""
插件系统基础模块
"""
from abc import ABC, abstractmethod
from typing import Optional
from fastapi import APIRouter, FastAPI


class Plugin(ABC):
    """插件基类"""
    
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """插件是否启用"""
        pass
    
    @abstractmethod
    def get_router(self) -> Optional[APIRouter]:
        """获取插件路由"""
        pass
    
    @abstractmethod
    def initialize(self, app: FastAPI):
        """初始化插件"""
        pass
    
    def get_info(self) -> dict:
        """获取插件信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.is_enabled()
        }


__all__ = ["Plugin"]

