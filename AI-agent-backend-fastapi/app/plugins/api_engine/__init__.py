"""
API引擎插件
"""
from app.plugins import Plugin
from fastapi import FastAPI, APIRouter
from typing import Optional

# 延迟导入,避免循环依赖
_router = None


def get_plugin_router() -> Optional[APIRouter]:
    """获取插件路由(延迟加载)"""
    global _router
    if _router is None:
        try:
            from .api import router
            _router = router
        except ImportError:
            return None
    return _router


class ApiEnginePlugin(Plugin):
    """API引擎插件类"""
    
    name = "api_engine"
    version = "1.0.0"
    description = "接口自动化测试引擎插件"
    
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        from .config import get_plugin_config
        config = get_plugin_config()
        return config.enabled
    
    def get_router(self) -> Optional[APIRouter]:
        """获取插件路由"""
        return get_plugin_router()
    
    def initialize(self, app: FastAPI):
        """初始化插件"""
        # 这里可以添加插件初始化逻辑
        # 例如:注册事件处理器、初始化数据等
        pass


# 创建插件实例
api_engine_plugin = ApiEnginePlugin()

__all__ = ["ApiEnginePlugin", "api_engine_plugin"]

