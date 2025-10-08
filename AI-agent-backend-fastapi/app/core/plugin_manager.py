# Copyright (c) 2025 左岚. All rights reserved.
"""
插件管理器
"""
from typing import Dict, List, Optional
from fastapi import FastAPI, APIRouter
import logging

from app.plugins import Plugin

logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    def register_plugin(self, name: str, plugin: Plugin):
        """
        注册插件
        
        Args:
            name: 插件名称
            plugin: 插件实例
        """
        if name in self.plugins:
            logger.warning(f"插件 {name} 已存在,将被覆盖")
        
        self.plugins[name] = plugin
        logger.info(f"插件 {name} 注册成功: {plugin.description}")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """获取指定插件"""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """获取所有插件"""
        return self.plugins
    
    def get_enabled_plugins(self) -> Dict[str, Plugin]:
        """获取所有已启用的插件"""
        return {
            name: plugin 
            for name, plugin in self.plugins.items() 
            if plugin.is_enabled()
        }
    
    def get_plugin_routers(self) -> List[APIRouter]:
        """获取所有已启用插件的路由"""
        routers = []
        for name, plugin in self.plugins.items():
            if plugin.is_enabled():
                router = plugin.get_router()
                if router:
                    routers.append(router)
                    logger.info(f"加载插件路由: {name}")
        return routers
    
    def initialize_plugins(self, app: FastAPI):
        """
        初始化所有已启用的插件
        
        Args:
            app: FastAPI应用实例
        """
        for name, plugin in self.plugins.items():
            if plugin.is_enabled():
                try:
                    plugin.initialize(app)
                    logger.info(f"插件 {name} 初始化成功")
                except Exception as e:
                    logger.error(f"插件 {name} 初始化失败: {str(e)}")
    
    def get_plugins_info(self) -> List[dict]:
        """获取所有插件信息"""
        return [plugin.get_info() for plugin in self.plugins.values()]


# 全局插件管理器实例
plugin_manager = PluginManager()

