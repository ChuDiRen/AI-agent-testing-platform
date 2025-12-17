"""
基于数据库的LangGraph Checkpointer实现
替代默认的文件存储方式，使用数据库持久化对话状态
"""
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

from sqlmodel import Session, select, and_, or_, delete
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    ChannelVersions,
    PendingWrite,
    get_checkpoint_id,
)

from aiassistant.model.LangGraphCheckpointModel import LangGraphCheckpoint, LangGraphCheckpointWrite
from core.database import get_session

logger = logging.getLogger(__name__)


class DatabaseCheckpointer(BaseCheckpointSaver):
    """基于数据库的LangGraph检查点存储实现"""
    
    def __init__(self, session_maker=None):
        """
        初始化数据库检查点存储
        
        Args:
            session_maker: 数据库会话工厂函数，如果为None则使用默认的get_session()
        """
        self._session_maker = session_maker or get_session
        
    def _get_session(self) -> Session:
        """获取数据库会话"""
        return self._session_maker()
    
    def list(
        self,
        config: RunnableConfig,
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Generator[CheckpointTuple, None, None]:
        """列出检查点"""
        thread_id = config.get("thread_id")
        if not thread_id:
            return
            
        with self._get_session() as session:
            # 构建查询
            query = select(LangGraphCheckpoint).where(
                LangGraphCheckpoint.thread_id == thread_id
            )
            
            # 如果指定了before，只返回该检查点之前的
            if before:
                before_id = get_checkpoint_id(before)
                query = query.where(LangGraphCheckpoint.checkpoint_id < before_id)
            
            # 应用过滤器
            if filter:
                if "checkpoint_ns" in filter:
                    # 这里可以添加命名空间过滤逻辑
                    pass
            
            # 排序并限制结果
            query = query.order_by(LangGraphCheckpoint.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            # 获取结果
            checkpoints = session.exec(query).all()
            
            # 生成CheckpointTuple对象
            for checkpoint in checkpoints:
                try:
                    # 解析数据
                    checkpoint_data = json.loads(checkpoint.checkpoint_data)
                    metadata = json.loads(checkpoint.checkpoint_metadata) if checkpoint.checkpoint_metadata else None
                    
                    # 获取待写入数据
                    pending_writes = self._get_pending_writes(session, thread_id, checkpoint.checkpoint_id)
                    
                    yield CheckpointTuple(
                        config={
                            "thread_id": thread_id,
                            "checkpoint_id": checkpoint.checkpoint_id,
                            "checkpoint_ns": config.get("checkpoint_ns", ""),
                        },
                        checkpoint=Checkpoint.from_dict(checkpoint_data),
                        metadata=CheckpointMetadata(**metadata) if metadata else None,
                        pending_writes=pending_writes,
                    )
                except Exception as e:
                    logger.error(f"Error parsing checkpoint {checkpoint.checkpoint_id}: {e}")
                    continue
    
    def get(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """获取特定配置的检查点"""
        thread_id = config.get("thread_id")
        checkpoint_id = get_checkpoint_id(config)
        
        if not thread_id or not checkpoint_id:
            return None
            
        with self._get_session() as session:
            # 查询检查点
            checkpoint = session.exec(
                select(LangGraphCheckpoint).where(
                    and_(
                        LangGraphCheckpoint.thread_id == thread_id,
                        LangGraphCheckpoint.checkpoint_id == checkpoint_id
                    )
                )
            ).first()
            
            if not checkpoint:
                return None
                
            try:
                # 解析数据
                checkpoint_data = json.loads(checkpoint.checkpoint_data)
                metadata = json.loads(checkpoint.checkpoint_metadata) if checkpoint.checkpoint_metadata else None
                
                # 获取待写入数据
                pending_writes = self._get_pending_writes(session, thread_id, checkpoint_id)
                
                return CheckpointTuple(
                    config={
                        "thread_id": thread_id,
                        "checkpoint_id": checkpoint.checkpoint_id,
                        "checkpoint_ns": config.get("checkpoint_ns", ""),
                    },
                    checkpoint=Checkpoint.from_dict(checkpoint_data),
                    metadata=CheckpointMetadata(**metadata) if metadata else None,
                    pending_writes=pending_writes,
                )
            except Exception as e:
                logger.error(f"Error parsing checkpoint {checkpoint.checkpoint_id}: {e}")
                return None
    
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: Optional[CheckpointMetadata] = None,
        new_versions: Optional[ChannelVersions] = None,
    ) -> RunnableConfig:
        """保存检查点"""
        thread_id = config.get("thread_id")
        if not thread_id:
            raise ValueError("Thread ID is required")
            
        # 生成检查点ID
        checkpoint_id = get_checkpoint_id(config) or str(uuid.uuid4())
        
        # 序列化数据
        checkpoint_data = json.dumps(checkpoint.dict(), ensure_ascii=False)
        metadata_data = json.dumps(metadata.dict(), ensure_ascii=False) if metadata else None
        
        with self._get_session() as session:
            # 查看是否已存在该检查点
            existing = session.exec(
                select(LangGraphCheckpoint).where(
                    and_(
                        LangGraphCheckpoint.thread_id == thread_id,
                        LangGraphCheckpoint.checkpoint_id == checkpoint_id
                    )
                )
            ).first()
            
            if existing:
                # 更新现有检查点
                existing.checkpoint_data = checkpoint_data
                existing.checkpoint_metadata = metadata_data
                existing.created_at = datetime.now()
            else:
                # 创建新检查点
                db_checkpoint = LangGraphCheckpoint(
                    thread_id=thread_id,
                    checkpoint_id=checkpoint_id,
                    parent_checkpoint_id=config.get("checkpoint_ns"),
                    checkpoint_data=checkpoint_data,
                    checkpoint_metadata=metadata_data,
                    is_pending=False
                )
                session.add(db_checkpoint)
            
            session.commit()
        
        # 返回更新后的配置
        new_config = config.copy()
        new_config["checkpoint_id"] = checkpoint_id
        return new_config
    
    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any, Optional[str]]],
        task_id: str,
        *,
        step: int = -1,
    ) -> None:
        """保存待写入数据"""
        thread_id = config.get("thread_id")
        checkpoint_id = get_checkpoint_id(config)
        
        if not thread_id or not checkpoint_id:
            return
            
        with self._get_session() as session:
            for task_path, value, idx in writes:
                # 序列化写入数据
                write_data = json.dumps({
                    "task_path": task_path,
                    "value": value,
                    "idx": idx,
                    "step": step,
                }, ensure_ascii=False, default=str)
                
                # 查看是否已存在该写入记录
                existing = session.exec(
                    select(LangGraphCheckpointWrite).where(
                        and_(
                            LangGraphCheckpointWrite.thread_id == thread_id,
                            LangGraphCheckpointWrite.checkpoint_id == checkpoint_id,
                            LangGraphCheckpointWrite.task_id == task_id,
                        )
                    )
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.checkpoint_data = write_data
                else:
                    # 创建新记录
                    db_write = LangGraphCheckpointWrite(
                        thread_id=thread_id,
                        checkpoint_id=checkpoint_id,
                        checkpoint_data=write_data,
                        checkpoint_metadata=None,
                        task_id=task_id,
                        completed=True
                    )
                    session.add(db_write)
            
            session.commit()
    
    def _get_pending_writes(
        self, 
        session: Session, 
        thread_id: str, 
        checkpoint_id: str
    ) -> List[PendingWrite]:
        """获取待写入数据"""
        writes = session.exec(
            select(LangGraphCheckpointWrite).where(
                and_(
                    LangGraphCheckpointWrite.thread_id == thread_id,
                    LangGraphCheckpointWrite.checkpoint_id == checkpoint_id,
                    LangGraphCheckpointWrite.completed == True
                )
            )
        ).all()
        
        pending_writes = []
        for write in writes:
            try:
                write_data = json.loads(write.checkpoint_data)
                task_path = write_data.get("task_path", "")
                value = write_data.get("value")
                idx = write_data.get("idx")
                
                pending_writes.append(
                    PendingWrite(
                        task_path=task_path,
                        value=value,
                        idx=idx,
                    )
                )
            except Exception as e:
                logger.error(f"Error parsing write {write.id}: {e}")
                continue
                
        return pending_writes
    
    def clear(self, config: RunnableConfig) -> None:
        """清除特定配置的检查点数据"""
        thread_id = config.get("thread_id")
        if not thread_id:
            return
            
        with self._get_session() as session:
            # 删除检查点
            session.exec(
                delete(LangGraphCheckpoint).where(
                    LangGraphCheckpoint.thread_id == thread_id
                )
            )
            
            # 删除写入记录
            session.exec(
                delete(LangGraphCheckpointWrite).where(
                    LangGraphCheckpointWrite.thread_id == thread_id
                )
            )
            
            session.commit()
    
    def maintenance(
        self,
        *,
        cleanup: bool = False,
        max_age: Optional[int] = None,
    ) -> None:
        """维护数据库，清理过期数据"""
        if not cleanup or not max_age:
            return
            
        cutoff_time = datetime.now() - timedelta(days=max_age)
        
        with self._get_session() as session:
            # 删除过期的写入记录
            session.exec(
                delete(LangGraphCheckpointWrite).where(
                    LangGraphCheckpointWrite.created_at < cutoff_time
                )
            )
            
            # 删除过期的检查点
            session.exec(
                delete(LangGraphCheckpoint).where(
                    LangGraphCheckpoint.created_at < cutoff_time
                )
            )
            
            session.commit()
            logger.info(f"Cleaned up checkpoints older than {max_age} days")


# 工厂函数，用于创建DatabaseCheckpointer实例
def create_database_checkpointer(session_maker=None) -> DatabaseCheckpointer:
    """
    创建数据库检查点存储实例
    
    Args:
        session_maker: 可选的数据库会话工厂函数
        
    Returns:
        DatabaseCheckpointer实例
    """
    return DatabaseCheckpointer(session_maker=session_maker)