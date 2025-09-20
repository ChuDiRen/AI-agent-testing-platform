# Copyright (c) 2025 左岚. All rights reserved.
"""
事务管理工具
提供数据库事务的装饰器和上下文管理器
"""

import functools
from typing import Any, Callable, Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import get_logger
from app.utils.exceptions import BusinessException, InternalServerException

logger = get_logger(__name__)


def transactional(rollback_on_exception: bool = True, 
                 commit_on_success: bool = True,
                 reraise_exception: bool = True):
    """
    事务装饰器
    
    Args:
        rollback_on_exception: 异常时是否回滚
        commit_on_success: 成功时是否提交
        reraise_exception: 是否重新抛出异常
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 查找Session参数
            db_session = None
            
            # 从位置参数中查找Session
            for arg in args:
                if isinstance(arg, Session):
                    db_session = arg
                    break
            
            # 从关键字参数中查找Session
            if not db_session:
                for key, value in kwargs.items():
                    if isinstance(value, Session):
                        db_session = value
                        break
            
            if not db_session:
                logger.warning("No database session found in function arguments")
                return func(*args, **kwargs)
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 成功时提交事务
                if commit_on_success:
                    db_session.commit()
                    logger.debug(f"Transaction committed for {func.__name__}")
                
                return result
                
            except SQLAlchemyError as e:
                # 数据库异常处理
                if rollback_on_exception:
                    db_session.rollback()
                    logger.error(f"Database error in {func.__name__}, rolled back: {str(e)}")
                
                if reraise_exception:
                    raise InternalServerException(f"Database operation failed: {str(e)}")
                
            except BusinessException as e:
                # 业务异常处理
                if rollback_on_exception:
                    db_session.rollback()
                    logger.warning(f"Business error in {func.__name__}, rolled back: {str(e)}")
                
                if reraise_exception:
                    raise e
                
            except Exception as e:
                # 其他异常处理
                if rollback_on_exception:
                    db_session.rollback()
                    logger.error(f"Unexpected error in {func.__name__}, rolled back: {str(e)}")
                
                if reraise_exception:
                    raise InternalServerException(f"Unexpected error: {str(e)}")
        
        return wrapper
    return decorator


@contextmanager
def transaction_scope(db_session: Session, 
                     rollback_on_exception: bool = True,
                     commit_on_success: bool = True):
    """
    事务上下文管理器
    
    Args:
        db_session: 数据库会话
        rollback_on_exception: 异常时是否回滚
        commit_on_success: 成功时是否提交
    """
    try:
        yield db_session
        
        if commit_on_success:
            db_session.commit()
            logger.debug("Transaction committed successfully")
            
    except SQLAlchemyError as e:
        if rollback_on_exception:
            db_session.rollback()
            logger.error(f"Database error, rolled back: {str(e)}")
        raise InternalServerException(f"Database operation failed: {str(e)}")
        
    except BusinessException as e:
        if rollback_on_exception:
            db_session.rollback()
            logger.warning(f"Business error, rolled back: {str(e)}")
        raise e
        
    except Exception as e:
        if rollback_on_exception:
            db_session.rollback()
            logger.error(f"Unexpected error, rolled back: {str(e)}")
        raise InternalServerException(f"Unexpected error: {str(e)}")


class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._savepoints = []
    
    def begin_savepoint(self, name: Optional[str] = None) -> str:
        """创建保存点"""
        savepoint_name = name or f"sp_{len(self._savepoints) + 1}"
        savepoint = self.db_session.begin_nested()
        self._savepoints.append((savepoint_name, savepoint))
        logger.debug(f"Created savepoint: {savepoint_name}")
        return savepoint_name
    
    def rollback_to_savepoint(self, name: Optional[str] = None):
        """回滚到保存点"""
        if not self._savepoints:
            logger.warning("No savepoints available for rollback")
            return
        
        if name:
            # 回滚到指定保存点
            for i, (sp_name, savepoint) in enumerate(self._savepoints):
                if sp_name == name:
                    savepoint.rollback()
                    # 移除该保存点之后的所有保存点
                    self._savepoints = self._savepoints[:i]
                    logger.debug(f"Rolled back to savepoint: {name}")
                    return
            logger.warning(f"Savepoint {name} not found")
        else:
            # 回滚到最近的保存点
            sp_name, savepoint = self._savepoints.pop()
            savepoint.rollback()
            logger.debug(f"Rolled back to latest savepoint: {sp_name}")
    
    def commit_savepoint(self, name: Optional[str] = None):
        """提交保存点"""
        if not self._savepoints:
            logger.warning("No savepoints available for commit")
            return
        
        if name:
            # 提交指定保存点
            for i, (sp_name, savepoint) in enumerate(self._savepoints):
                if sp_name == name:
                    savepoint.commit()
                    self._savepoints.pop(i)
                    logger.debug(f"Committed savepoint: {name}")
                    return
            logger.warning(f"Savepoint {name} not found")
        else:
            # 提交最近的保存点
            sp_name, savepoint = self._savepoints.pop()
            savepoint.commit()
            logger.debug(f"Committed latest savepoint: {sp_name}")


# 导出事务工具
__all__ = ["transactional", "transaction_scope", "TransactionManager"]
