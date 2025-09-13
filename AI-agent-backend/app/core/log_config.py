# Copyright (c) 2025 左岚. All rights reserved.
"""
日志配置管理
提供动态日志配置和存储策略管理
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.config import settings


class LogStorageStrategy(str, Enum):
    """日志存储策略枚举"""
    DATABASE_ONLY = "database_only"      # 仅数据库存储
    FILE_ONLY = "file_only"              # 仅文件存储
    BOTH = "both"                        # 数据库和文件都存储
    SMART = "smart"                      # 智能存储（根据级别分配）


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig(BaseModel):
    """日志配置模型"""
    
    # 基础配置
    log_level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    storage_strategy: LogStorageStrategy = Field(default=LogStorageStrategy.SMART, description="存储策略")
    
    # 文件日志配置
    enable_file_logging: bool = Field(default=True, description="启用文件日志")
    file_log_level: LogLevel = Field(default=LogLevel.DEBUG, description="文件日志级别")
    file_rotation: str = Field(default="100 MB", description="文件轮转大小")
    file_retention: str = Field(default="30 days", description="文件保留时间")
    file_compression: bool = Field(default=True, description="文件压缩")
    
    # 数据库日志配置
    enable_db_logging: bool = Field(default=True, description="启用数据库日志")
    db_log_level: LogLevel = Field(default=LogLevel.INFO, description="数据库日志级别")
    db_batch_size: int = Field(default=100, description="数据库批量写入大小")
    db_flush_interval: int = Field(default=5, description="数据库刷新间隔（秒）")
    
    # 性能配置
    async_logging: bool = Field(default=True, description="异步日志记录")
    buffer_size: int = Field(default=1000, description="日志缓冲区大小")
    max_queue_size: int = Field(default=10000, description="最大队列大小")
    
    # 过滤配置
    exclude_paths: list[str] = Field(
        default=["/health", "/metrics", "/docs", "/redoc", "/openapi.json"],
        description="排除的路径"
    )
    sensitive_fields: list[str] = Field(
        default=["password", "token", "secret", "key", "authorization"],
        description="敏感字段"
    )
    
    # 监控配置
    enable_monitoring: bool = Field(default=True, description="启用日志监控")
    alert_error_threshold: int = Field(default=10, description="错误告警阈值（每小时）")
    alert_error_rate_threshold: float = Field(default=5.0, description="错误率告警阈值（%）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_level": "INFO",
                "storage_strategy": "smart",
                "enable_file_logging": True,
                "file_log_level": "DEBUG",
                "enable_db_logging": True,
                "db_log_level": "INFO",
                "async_logging": True,
                "enable_monitoring": True
            }
        }


class LogConfigManager:
    """日志配置管理器"""
    
    def __init__(self):
        self._config = self._load_default_config()
        self._config_file = os.path.join(settings.BASE_DIR, "config", "log_config.json")
    
    def _load_default_config(self) -> LogConfig:
        """加载默认配置"""
        return LogConfig(
            log_level=LogLevel(settings.LOG_LEVEL),
            storage_strategy=LogStorageStrategy.SMART,
            file_rotation=settings.LOG_ROTATION,
            file_retention=settings.LOG_RETENTION
        )
    
    def get_config(self) -> LogConfig:
        """获取当前配置"""
        return self._config
    
    def update_config(self, config_data: Dict[str, Any]) -> LogConfig:
        """更新配置"""
        # 验证配置数据
        new_config = LogConfig(**{**self._config.model_dump(), **config_data})
        self._config = new_config
        
        # 保存配置到文件
        self._save_config()
        
        # 应用新配置
        self._apply_config()
        
        return self._config
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            import json
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config.model_dump(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save log config: {e}")
    
    def _load_config(self):
        """从文件加载配置"""
        try:
            import json
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._config = LogConfig(**config_data)
        except Exception as e:
            print(f"Failed to load log config: {e}")
    
    def _apply_config(self):
        """应用配置到日志系统"""
        # 这里可以动态调整loguru的配置
        # 由于loguru的限制，某些配置可能需要重启应用才能生效
        pass
    
    def should_log_to_file(self, level: str) -> bool:
        """判断是否应该记录到文件"""
        if not self._config.enable_file_logging:
            return False
        
        if self._config.storage_strategy == LogStorageStrategy.DATABASE_ONLY:
            return False
        
        if self._config.storage_strategy == LogStorageStrategy.FILE_ONLY:
            return True
        
        if self._config.storage_strategy == LogStorageStrategy.BOTH:
            return True
        
        if self._config.storage_strategy == LogStorageStrategy.SMART:
            # 智能策略：ERROR及以上级别记录到文件
            level_priority = {
                "DEBUG": 0,
                "INFO": 1,
                "WARNING": 2,
                "ERROR": 3,
                "CRITICAL": 4
            }
            file_level_priority = level_priority.get(self._config.file_log_level.value, 1)
            current_level_priority = level_priority.get(level, 1)
            return current_level_priority >= file_level_priority
        
        return True
    
    def should_log_to_db(self, level: str) -> bool:
        """判断是否应该记录到数据库"""
        if not self._config.enable_db_logging:
            return False
        
        if self._config.storage_strategy == LogStorageStrategy.FILE_ONLY:
            return False
        
        if self._config.storage_strategy == LogStorageStrategy.DATABASE_ONLY:
            return True
        
        if self._config.storage_strategy == LogStorageStrategy.BOTH:
            return True
        
        if self._config.storage_strategy == LogStorageStrategy.SMART:
            # 智能策略：INFO及以上级别记录到数据库
            level_priority = {
                "DEBUG": 0,
                "INFO": 1,
                "WARNING": 2,
                "ERROR": 3,
                "CRITICAL": 4
            }
            db_level_priority = level_priority.get(self._config.db_log_level.value, 1)
            current_level_priority = level_priority.get(level, 1)
            return current_level_priority >= db_level_priority
        
        return True
    
    def should_skip_path(self, path: str) -> bool:
        """判断是否应该跳过该路径的日志记录"""
        return any(path.startswith(exclude_path) for exclude_path in self._config.exclude_paths)
    
    def get_sensitive_fields(self) -> list[str]:
        """获取敏感字段列表"""
        return self._config.sensitive_fields
    
    def is_monitoring_enabled(self) -> bool:
        """判断是否启用监控"""
        return self._config.enable_monitoring
    
    def get_alert_thresholds(self) -> Dict[str, Any]:
        """获取告警阈值"""
        return {
            "error_threshold": self._config.alert_error_threshold,
            "error_rate_threshold": self._config.alert_error_rate_threshold
        }


# 全局配置管理器实例
log_config_manager = LogConfigManager()


def get_log_config() -> LogConfig:
    """获取日志配置"""
    return log_config_manager.get_config()


def update_log_config(config_data: Dict[str, Any]) -> LogConfig:
    """更新日志配置"""
    return log_config_manager.update_config(config_data)


# 导出
__all__ = [
    "LogStorageStrategy",
    "LogLevel", 
    "LogConfig",
    "LogConfigManager",
    "log_config_manager",
    "get_log_config",
    "update_log_config"
]
