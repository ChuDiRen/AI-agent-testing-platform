# Copyright (c) 2025 左岚. All rights reserved.
"""
日志配置Controller
处理日志配置相关的HTTP请求
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.log_config import (
    LogConfig, 
    LogStorageStrategy, 
    LogLevel,
    get_log_config, 
    update_log_config
)
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.entity.user import User
from app.middleware.auth import get_current_user
from app.utils.log_decorators import log_operation

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/log-config", tags=["日志配置管理"])


@router.get("/get-config", response_model=ApiResponse[LogConfig], summary="获取日志配置")
@log_operation(
    operation_type="VIEW",
    resource_type="LOG_CONFIG",
    operation_desc="查看日志配置"
)
async def get_log_configuration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前日志配置
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        日志配置信息
    """
    try:
        config = get_log_config()
        return ApiResponse.success_response(data=config, message="获取日志配置成功")
        
    except Exception as e:
        logger.error(f"Error getting log config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志配置失败"
        )


@router.post("/update-config", response_model=ApiResponse[LogConfig], summary="更新日志配置")
@log_operation(
    operation_type="UPDATE",
    resource_type="LOG_CONFIG",
    operation_desc="更新日志配置",
    include_request=True
)
async def update_log_configuration(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新日志配置
    
    Args:
        config_data: 配置数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的配置
    """
    try:
        # 验证用户权限（可以添加更严格的权限检查）
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以修改日志配置"
            )
        
        # 更新配置
        new_config = update_log_config(config_data)
        
        return ApiResponse.success_response(data=new_config, message="更新日志配置成功")
        
    except ValueError as e:
        logger.error(f"Invalid log config data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置数据无效: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating log config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新日志配置失败"
        )


@router.get("/storage-strategies", response_model=ApiResponse[list], summary="获取存储策略选项")
async def get_storage_strategies(
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的日志存储策略选项
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        存储策略列表
    """
    try:
        strategies = [
            {
                "value": LogStorageStrategy.DATABASE_ONLY,
                "label": "仅数据库存储",
                "description": "所有日志只存储到数据库，便于查询和分析"
            },
            {
                "value": LogStorageStrategy.FILE_ONLY,
                "label": "仅文件存储",
                "description": "所有日志只存储到文件，便于调试和备份"
            },
            {
                "value": LogStorageStrategy.BOTH,
                "label": "双重存储",
                "description": "同时存储到数据库和文件，提供最大的灵活性"
            },
            {
                "value": LogStorageStrategy.SMART,
                "label": "智能存储",
                "description": "根据日志级别智能选择存储方式，平衡性能和功能"
            }
        ]
        
        return ApiResponse.success_response(data=strategies, message="获取存储策略成功")
        
    except Exception as e:
        logger.error(f"Error getting storage strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取存储策略失败"
        )


@router.get("/log-levels", response_model=ApiResponse[list], summary="获取日志级别选项")
async def get_log_levels(
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的日志级别选项
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        日志级别列表
    """
    try:
        levels = [
            {
                "value": LogLevel.DEBUG,
                "label": "调试",
                "description": "详细的调试信息，仅在开发环境使用"
            },
            {
                "value": LogLevel.INFO,
                "label": "信息",
                "description": "一般信息，记录正常的程序流程"
            },
            {
                "value": LogLevel.WARNING,
                "label": "警告",
                "description": "警告信息，程序仍能正常运行但需要注意"
            },
            {
                "value": LogLevel.ERROR,
                "label": "错误",
                "description": "错误信息，程序出现问题但仍能继续运行"
            },
            {
                "value": LogLevel.CRITICAL,
                "label": "严重",
                "description": "严重错误，程序可能无法继续运行"
            }
        ]
        
        return ApiResponse.success_response(data=levels, message="获取日志级别成功")
        
    except Exception as e:
        logger.error(f"Error getting log levels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志级别失败"
        )


@router.post("/reset-config", response_model=ApiResponse[LogConfig], summary="重置日志配置")
@log_operation(
    operation_type="RESET",
    resource_type="LOG_CONFIG",
    operation_desc="重置日志配置为默认值"
)
async def reset_log_configuration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重置日志配置为默认值
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        重置后的配置
    """
    try:
        # 验证用户权限
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以重置日志配置"
            )
        
        # 重置为默认配置
        default_config = LogConfig()
        new_config = update_log_config(default_config.model_dump())
        
        return ApiResponse.success_response(data=new_config, message="重置日志配置成功")
        
    except Exception as e:
        logger.error(f"Error resetting log config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置日志配置失败"
        )


@router.get("/config-status", response_model=ApiResponse[dict], summary="获取配置状态")
async def get_config_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取日志配置状态信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        配置状态信息
    """
    try:
        config = get_log_config()
        
        status_info = {
            "file_logging_enabled": config.enable_file_logging,
            "db_logging_enabled": config.enable_db_logging,
            "monitoring_enabled": config.enable_monitoring,
            "storage_strategy": config.storage_strategy,
            "current_log_level": config.log_level,
            "async_logging": config.async_logging,
            "excluded_paths_count": len(config.exclude_paths),
            "sensitive_fields_count": len(config.sensitive_fields)
        }
        
        return ApiResponse.success_response(data=status_info, message="获取配置状态成功")
        
    except Exception as e:
        logger.error(f"Error getting config status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置状态失败"
        )
