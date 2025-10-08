# Copyright (c) 2025 左岚. All rights reserved.
"""
API引擎插件配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class ApiEnginePluginConfig(BaseSettings):
    """API引擎插件配置类"""
    
    # 基础配置
    enabled: bool = True
    route_prefix: str = "/api/v1/plugin/api-engine"
    
    # 执行配置
    max_concurrent_executions: int = 10
    execution_timeout: int = 300  # 秒
    
    # 日志配置
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_retention_days: int = 7
    
    # 文件配置
    upload_max_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_extensions: list = ['.yaml', '.yml', '.json']
    
    class Config:
        env_prefix = "API_ENGINE_PLUGIN_"
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_plugin_config() -> ApiEnginePluginConfig:
    """获取插件配置单例"""
    return ApiEnginePluginConfig()


# 导出配置实例
API_ENGINE_PLUGIN_CONFIG = get_plugin_config()

