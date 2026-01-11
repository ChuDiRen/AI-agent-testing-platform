"""
数据持久化 - 任务、会话、测试结果、知识图谱持久化

职责：
- 任务数据持久化
- 会话数据持久化
- 测试结果持久化
- 知识图谱持久化
- 数据同步和备份
"""
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import asyncio
from contextlib import asynccontextmanager
from enum import Enum

from core.database_config import get_database_manager, DatabaseType
from core.logging_config import get_logger

logger = get_logger(__name__)


class PersistenceType(str, Enum):
    """持久化类型枚举"""
    TASK = "task"
    SESSION = "session"
    TEST_RESULT = "test_result"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    API_ENDPOINT = "api_endpoint"
    USER_DATA = "user_data"


@dataclass
class PersistedTask:
    """持久化任务数据模型"""
    task_id: str
    task_type: str
    task_name: str
    status: str
    progress: float = 0.0
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    agent_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersistedSession:
    """持久化会话数据模型"""
    session_id: str
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    task_ids: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersistedTestResult:
    """持久化测试结果数据模型"""
    result_id: str
    task_id: str
    session_id: Optional[str] = None
    test_name: str
    status: str
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    result_data: Optional[str] = None
    performance_data: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersistedKnowledgeGraph:
    """持久化知识图谱数据模型"""
    graph_id: str
    name: str
    description: Optional[str] = None
    entities: str = "[]"  # JSON serialized
    relationships: str = "[]"  # JSON serialized
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1


@dataclass
class PersistedAPIEndpoint:
    """持久化API端点数据模型"""
    endpoint_id: str
    path: str
    method: str
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[str] = None  # JSON serialized
    request_body: Optional[str] = None  # JSON serialized
    responses: Optional[str] = None  # JSON serialized
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataPersistenceManager:
    """数据持久化管理器"""

    def __init__(self, db_name: str = "persistence"):
        """初始化数据持久化管理器"""
        self.db_name = db_name
        self.db_manager = get_database_manager()
        self._initialized = False
        
        logger.info(f"数据持久化管理器初始化: {db_name}")

    async def initialize(self) -> bool:
        """初始化数据持久化系统"""
        try:
            # 确保数据库已初始化
            await self.db_manager.initialize_database(self.db_name)
            
            # 创建必要的表
            await self._create_tables()
            
            self._initialized = True
            logger.info("数据持久化系统初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"数据持久化系统初始化失败: {e}", exc_info=e)
            return False

    async def _create_tables(self):
        """创建数据持久化表"""
        # 任务表
        task_columns = {
            "task_id": "VARCHAR(255) PRIMARY KEY",
            "task_type": "VARCHAR(100) NOT NULL",
            "task_name": "VARCHAR(255) NOT NULL",
            "status": "VARCHAR(50) NOT NULL DEFAULT 'pending'",
            "progress": "FLOAT DEFAULT 0.0",
            "result": "TEXT",
            "error_message": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "metadata": "TEXT",
            "execution_time": "FLOAT",
            "agent_results": "TEXT"
        }
        await self.db_manager.create_table(self.db_name, "persisted_tasks", task_columns)

        # 会话表
        session_columns = {
            "session_id": "VARCHAR(255) PRIMARY KEY",
            "user_id": "VARCHAR(255)",
            "session_name": "VARCHAR(255)",
            "status": "VARCHAR(50) NOT NULL DEFAULT 'active'",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "metadata": "TEXT",
            "task_ids": "TEXT",  # JSON serialized list
            "context_data": "TEXT"  # JSON serialized
        }
        await self.db_manager.create_table(self.db_name, "persisted_sessions", session_columns)

        # 测试结果表
        test_result_columns = {
            "result_id": "VARCHAR(255) PRIMARY KEY",
            "task_id": "VARCHAR(255) NOT NULL",
            "session_id": "VARCHAR(255)",
            "test_name": "VARCHAR(255) NOT NULL",
            "status": "VARCHAR(50) NOT NULL",
            "duration_ms": "FLOAT DEFAULT 0.0",
            "error_message": "TEXT",
            "result_data": "TEXT",
            "performance_data": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "metadata": "TEXT"
        }
        await self.db_manager.create_table(self.db_name, "persisted_test_results", test_result_columns)

        # 知识图谱表
        knowledge_graph_columns = {
            "graph_id": "VARCHAR(255) PRIMARY KEY",
            "name": "VARCHAR(255) NOT NULL",
            "description": "TEXT",
            "entities": "TEXT NOT NULL",
            "relationships": "TEXT NOT NULL",
            "metadata": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "version": "INTEGER DEFAULT 1"
        }
        await self.db_manager.create_table(self.db_name, "persisted_knowledge_graphs", knowledge_graph_columns)

        # API端点表
        api_endpoint_columns = {
            "endpoint_id": "VARCHAR(255) PRIMARY KEY",
            "path": "VARCHAR(500) NOT NULL",
            "method": "VARCHAR(10) NOT NULL",
            "operation_id": "VARCHAR(255)",
            "summary": "TEXT",
            "description": "TEXT",
            "parameters": "TEXT",
            "request_body": "TEXT",
            "responses": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "metadata": "TEXT"
        }
        await self.db_manager.create_table(self.db_name, "persisted_api_endpoints", api_endpoint_columns)

        logger.info("数据持久化表创建成功")

    # 任务持久化方法
    async def save_task(self, task: PersistedTask) -> bool:
        """保存任务数据"""
        try:
            query = """
            INSERT OR REPLACE INTO persisted_tasks 
            (task_id, task_type, task_name, status, progress, result, error_message, 
             created_at, updated_at, metadata, execution_time, agent_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                task.task_id, task.task_type, task.task_name, task.status, task.progress,
                task.result, task.error_message, task.created_at.isoformat(),
                task.updated_at.isoformat(), json.dumps(task.metadata),
                task.execution_time, json.dumps(task.agent_results)
            )
            
            await self.db_manager.execute_query(self.db_name, query, params)
            logger.debug(f"任务已保存: {task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存任务失败: {e}", exc_info=e)
            return False

    async def load_task(self, task_id: str) -> Optional[PersistedTask]:
        """加载任务数据"""
        try:
            query = "SELECT * FROM persisted_tasks WHERE task_id = ?"
            results = await self.db_manager.execute_query(self.db_name, query, (task_id,))
            
            if not results:
                return None
            
            row = results[0]
            return PersistedTask(
                task_id=row["task_id"],
                task_type=row["task_type"],
                task_name=row["task_name"],
                status=row["status"],
                progress=row["progress"],
                result=row["result"],
                error_message=row["error_message"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                execution_time=row["execution_time"],
                agent_results=json.loads(row["agent_results"]) if row["agent_results"] else {}
            )
            
        except Exception as e:
            logger.error(f"加载任务失败: {e}", exc_info=e)
            return None

    async def list_tasks(self, status: Optional[str] = None, limit: int = 100) -> List[PersistedTask]:
        """列出任务"""
        try:
            if status:
                query = "SELECT * FROM persisted_tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?"
                results = await self.db_manager.execute_query(self.db_name, query, (status, limit))
            else:
                query = "SELECT * FROM persisted_tasks ORDER BY created_at DESC LIMIT ?"
                results = await self.db_manager.execute_query(self.db_name, query, (limit,))
            
            tasks = []
            for row in results:
                task = PersistedTask(
                    task_id=row["task_id"],
                    task_type=row["task_type"],
                    task_name=row["task_name"],
                    status=row["status"],
                    progress=row["progress"],
                    result=row["result"],
                    error_message=row["error_message"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    execution_time=row["execution_time"],
                    agent_results=json.loads(row["agent_results"]) if row["agent_results"] else {}
                )
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"列出任务失败: {e}", exc_info=e)
            return []

    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            query = "DELETE FROM persisted_tasks WHERE task_id = ?"
            await self.db_manager.execute_query(self.db_name, query, (task_id,))
            logger.debug(f"任务已删除: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除任务失败: {e}", exc_info=e)
            return False

    # 会话持久化方法
    async def save_session(self, session: PersistedSession) -> bool:
        """保存会话数据"""
        try:
            query = """
            INSERT OR REPLACE INTO persisted_sessions 
            (session_id, user_id, session_name, status, created_at, updated_at, 
             metadata, task_ids, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                session.session_id, session.user_id, session.session_name, session.status,
                session.created_at.isoformat(), session.updated_at.isoformat(),
                json.dumps(session.metadata), json.dumps(session.task_ids),
                json.dumps(session.context_data)
            )
            
            await self.db_manager.execute_query(self.db_name, query, params)
            logger.debug(f"会话已保存: {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存会话失败: {e}", exc_info=e)
            return False

    async def load_session(self, session_id: str) -> Optional[PersistedSession]:
        """加载会话数据"""
        try:
            query = "SELECT * FROM persisted_sessions WHERE session_id = ?"
            results = await self.db_manager.execute_query(self.db_name, query, (session_id,))
            
            if not results:
                return None
            
            row = results[0]
            return PersistedSession(
                session_id=row["session_id"],
                user_id=row["user_id"],
                session_name=row["session_name"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                task_ids=json.loads(row["task_ids"]) if row["task_ids"] else [],
                context_data=json.loads(row["context_data"]) if row["context_data"] else {}
            )
            
        except Exception as e:
            logger.error(f"加载会话失败: {e}", exc_info=e)
            return None

    async def list_sessions(self, user_id: Optional[str] = None, limit: int = 100) -> List[PersistedSession]:
        """列出会话"""
        try:
            if user_id:
                query = "SELECT * FROM persisted_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?"
                results = await self.db_manager.execute_query(self.db_name, query, (user_id, limit))
            else:
                query = "SELECT * FROM persisted_sessions ORDER BY updated_at DESC LIMIT ?"
                results = await self.db_manager.execute_query(self.db_name, query, (limit,))
            
            sessions = []
            for row in results:
                session = PersistedSession(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    session_name=row["session_name"],
                    status=row["status"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    task_ids=json.loads(row["task_ids"]) if row["task_ids"] else [],
                    context_data=json.loads(row["context_data"]) if row["context_data"] else {}
                )
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"列出会话失败: {e}", exc_info=e)
            return []

    # 测试结果持久化方法
    async def save_test_result(self, result: PersistedTestResult) -> bool:
        """保存测试结果"""
        try:
            query = """
            INSERT OR REPLACE INTO persisted_test_results 
            (result_id, task_id, session_id, test_name, status, duration_ms, 
             error_message, result_data, performance_data, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                result.result_id, result.task_id, result.session_id, result.test_name,
                result.status, result.duration_ms, result.error_message,
                result.result_data, result.performance_data,
                result.created_at.isoformat(), json.dumps(result.metadata)
            )
            
            await self.db_manager.execute_query(self.db_name, query, params)
            logger.debug(f"测试结果已保存: {result.result_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存测试结果失败: {e}", exc_info=e)
            return False

    async def load_test_results(self, task_id: str) -> List[PersistedTestResult]:
        """加载测试结果"""
        try:
            query = "SELECT * FROM persisted_test_results WHERE task_id = ? ORDER BY created_at DESC"
            results = await self.db_manager.execute_query(self.db_name, query, (task_id,))
            
            test_results = []
            for row in results:
                result = PersistedTestResult(
                    result_id=row["result_id"],
                    task_id=row["task_id"],
                    session_id=row["session_id"],
                    test_name=row["test_name"],
                    status=row["status"],
                    duration_ms=row["duration_ms"],
                    error_message=row["error_message"],
                    result_data=row["result_data"],
                    performance_data=row["performance_data"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                )
                test_results.append(result)
            
            return test_results
            
        except Exception as e:
            logger.error(f"加载测试结果失败: {e}", exc_info=e)
            return []

    # 知识图谱持久化方法
    async def save_knowledge_graph(self, graph: PersistedKnowledgeGraph) -> bool:
        """保存知识图谱"""
        try:
            query = """
            INSERT OR REPLACE INTO persisted_knowledge_graphs 
            (graph_id, name, description, entities, relationships, metadata, 
             created_at, updated_at, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                graph.graph_id, graph.name, graph.description, graph.entities,
                graph.relationships, json.dumps(graph.metadata),
                graph.created_at.isoformat(), graph.updated_at.isoformat(),
                graph.version
            )
            
            await self.db_manager.execute_query(self.db_name, query, params)
            logger.debug(f"知识图谱已保存: {graph.graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存知识图谱失败: {e}", exc_info=e)
            return False

    async def load_knowledge_graph(self, graph_id: str) -> Optional[PersistedKnowledgeGraph]:
        """加载知识图谱"""
        try:
            query = "SELECT * FROM persisted_knowledge_graphs WHERE graph_id = ?"
            results = await self.db_manager.execute_query(self.db_name, query, (graph_id,))
            
            if not results:
                return None
            
            row = results[0]
            return PersistedKnowledgeGraph(
                graph_id=row["graph_id"],
                name=row["name"],
                description=row["description"],
                entities=row["entities"],
                relationships=row["relationships"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                version=row["version"]
            )
            
        except Exception as e:
            logger.error(f"加载知识图谱失败: {e}", exc_info=e)
            return None

    async def list_knowledge_graphs(self, limit: int = 100) -> List[PersistedKnowledgeGraph]:
        """列出知识图谱"""
        try:
            query = "SELECT * FROM persisted_knowledge_graphs ORDER BY updated_at DESC LIMIT ?"
            results = await self.db_manager.execute_query(self.db_name, query, (limit,))
            
            graphs = []
            for row in results:
                graph = PersistedKnowledgeGraph(
                    graph_id=row["graph_id"],
                    name=row["name"],
                    description=row["description"],
                    entities=row["entities"],
                    relationships=row["relationships"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    version=row["version"]
                )
                graphs.append(graph)
            
            return graphs
            
        except Exception as e:
            logger.error(f"列出知识图谱失败: {e}", exc_info=e)
            return []

    # API端点持久化方法
    async def save_api_endpoint(self, endpoint: PersistedAPIEndpoint) -> bool:
        """保存API端点"""
        try:
            query = """
            INSERT OR REPLACE INTO persisted_api_endpoints 
            (endpoint_id, path, method, operation_id, summary, description, 
             parameters, request_body, responses, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                endpoint.endpoint_id, endpoint.path, endpoint.method, endpoint.operation_id,
                endpoint.summary, endpoint.description, endpoint.parameters,
                endpoint.request_body, endpoint.responses,
                endpoint.created_at.isoformat(), endpoint.updated_at.isoformat(),
                json.dumps(endpoint.metadata)
            )
            
            await self.db_manager.execute_query(self.db_name, query, params)
            logger.debug(f"API端点已保存: {endpoint.endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存API端点失败: {e}", exc_info=e)
            return False

    async def load_api_endpoints(self, path_pattern: Optional[str] = None) -> List[PersistedAPIEndpoint]:
        """加载API端点"""
        try:
            if path_pattern:
                query = "SELECT * FROM persisted_api_endpoints WHERE path LIKE ? ORDER BY updated_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query, (f"%{path_pattern}%",))
            else:
                query = "SELECT * FROM persisted_api_endpoints ORDER BY updated_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
            
            endpoints = []
            for row in results:
                endpoint = PersistedAPIEndpoint(
                    endpoint_id=row["endpoint_id"],
                    path=row["path"],
                    method=row["method"],
                    operation_id=row["operation_id"],
                    summary=row["summary"],
                    description=row["description"],
                    parameters=row["parameters"],
                    request_body=row["request_body"],
                    responses=row["responses"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                )
                endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"加载API端点失败: {e}", exc_info=e)
            return []

    # 数据清理和维护方法
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """清理旧数据"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            cleanup_stats = {}
            
            # 清理旧任务
            query = "DELETE FROM persisted_tasks WHERE created_at < ?"
            result = await self.db_manager.execute_query(self.db_name, query, (cutoff_str,))
            cleanup_stats["tasks_deleted"] = len(result) if result else 0
            
            # 清理旧会话
            query = "DELETE FROM persisted_sessions WHERE created_at < ?"
            result = await self.db_manager.execute_query(self.db_name, query, (cutoff_str,))
            cleanup_stats["sessions_deleted"] = len(result) if result else 0
            
            # 清理旧测试结果
            query = "DELETE FROM persisted_test_results WHERE created_at < ?"
            result = await self.db_manager.execute_query(self.db_name, query, (cutoff_str,))
            cleanup_stats["test_results_deleted"] = len(result) if result else 0
            
            logger.info(f"数据清理完成: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}", exc_info=e)
            return {}

    async def get_persistence_statistics(self) -> Dict[str, Any]:
        """获取持久化统计信息"""
        try:
            stats = {}
            
            # 任务统计
            query = "SELECT COUNT(*) as count FROM persisted_tasks"
            result = await self.db_manager.execute_query(self.db_name, query)
            stats["total_tasks"] = result[0]["count"] if result else 0
            
            # 会话统计
            query = "SELECT COUNT(*) as count FROM persisted_sessions"
            result = await self.db_manager.execute_query(self.db_name, query)
            stats["total_sessions"] = result[0]["count"] if result else 0
            
            # 测试结果统计
            query = "SELECT COUNT(*) as count FROM persisted_test_results"
            result = await self.db_manager.execute_query(self.db_name, query)
            stats["total_test_results"] = result[0]["count"] if result else 0
            
            # 知识图谱统计
            query = "SELECT COUNT(*) as count FROM persisted_knowledge_graphs"
            result = await self.db_manager.execute_query(self.db_name, query)
            stats["total_knowledge_graphs"] = result[0]["count"] if result else 0
            
            # API端点统计
            query = "SELECT COUNT(*) as count FROM persisted_api_endpoints"
            result = await self.db_manager.execute_query(self.db_name, query)
            stats["total_api_endpoints"] = result[0]["count"] if result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"获取持久化统计信息失败: {e}", exc_info=e)
            return {}

    async def export_data(self, data_type: Optional[PersistenceType] = None) -> Dict[str, Any]:
        """导出数据"""
        try:
            export_data = {}
            
            if not data_type or data_type == PersistenceType.TASK:
                query = "SELECT * FROM persisted_tasks ORDER BY created_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
                export_data["tasks"] = results
            
            if not data_type or data_type == PersistenceType.SESSION:
                query = "SELECT * FROM persisted_sessions ORDER BY created_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
                export_data["sessions"] = results
            
            if not data_type or data_type == PersistenceType.TEST_RESULT:
                query = "SELECT * FROM persisted_test_results ORDER BY created_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
                export_data["test_results"] = results
            
            if not data_type or data_type == PersistenceType.KNOWLEDGE_GRAPH:
                query = "SELECT * FROM persisted_knowledge_graphs ORDER BY created_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
                export_data["knowledge_graphs"] = results
            
            if not data_type or data_type == PersistenceType.API_ENDPOINT:
                query = "SELECT * FROM persisted_api_endpoints ORDER BY created_at DESC"
                results = await self.db_manager.execute_query(self.db_name, query)
                export_data["api_endpoints"] = results
            
            logger.info(f"数据导出完成: {data_type}")
            return export_data
            
        except Exception as e:
            logger.error(f"数据导出失败: {e}", exc_info=e)
            return {}

    async def import_data(self, data: Dict[str, Any]) -> Dict[str, int]:
        """导入数据"""
        try:
            import_stats = {}
            
            # 导入任务
            if "tasks" in data:
                for task_data in data["tasks"]:
                    task = PersistedTask(
                        task_id=task_data["task_id"],
                        task_type=task_data["task_type"],
                        task_name=task_data["task_name"],
                        status=task_data["status"],
                        progress=task_data.get("progress", 0.0),
                        result=task_data.get("result"),
                        error_message=task_data.get("error_message"),
                        created_at=datetime.fromisoformat(task_data["created_at"]),
                        updated_at=datetime.fromisoformat(task_data["updated_at"]),
                        metadata=json.loads(task_data.get("metadata", "{}")),
                        execution_time=task_data.get("execution_time"),
                        agent_results=json.loads(task_data.get("agent_results", "{}"))
                    )
                    await self.save_task(task)
                import_stats["tasks_imported"] = len(data["tasks"])
            
            # 导入其他数据类型...
            # (类似的任务处理逻辑)
            
            logger.info(f"数据导入完成: {import_stats}")
            return import_stats
            
        except Exception as e:
            logger.error(f"数据导入失败: {e}", exc_info=e)
            return {}


# 全局数据持久化管理器实例
_persistence_manager: Optional[DataPersistenceManager] = None


def get_persistence_manager() -> DataPersistenceManager:
    """获取全局数据持久化管理器实例"""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = DataPersistenceManager()
    return _persistence_manager


def create_persistence_manager(db_name: str = "persistence") -> DataPersistenceManager:
    """创建新的数据持久化管理器实例"""
    return DataPersistenceManager(db_name)


# 使用示例
async def setup_data_persistence():
    """设置数据持久化"""
    persistence_manager = get_persistence_manager()
    
    # 初始化持久化系统
    await persistence_manager.initialize()
    
    # 创建示例任务
    task = PersistedTask(
        task_id="task_001",
        task_type="api_testing",
        task_name="API测试任务",
        status="completed",
        progress=100.0,
        result='{"success": true}',
        metadata={"framework": "playwright", "endpoints": 5}
    )
    
    # 保存任务
    await persistence_manager.save_task(task)
    
    # 加载任务
    loaded_task = await persistence_manager.load_task("task_001")
    print(f"加载的任务: {loaded_task.task_name}")
    
    # 获取统计信息
    stats = await persistence_manager.get_persistence_statistics()
    print(f"持久化统计: {stats}")


if __name__ == "__main__":
    # 测试数据持久化
    import asyncio
    
    async def test_data_persistence():
        # 创建持久化管理器
        manager = DataPersistenceManager("test_persistence")
        
        # 初始化
        success = await manager.initialize()
        print(f"初始化成功: {success}")
        
        # 创建示例数据
        task = PersistedTask(
            task_id="test_task_001",
            task_type="test",
            task_name="测试任务",
            status="running",
            progress=50.0
        )
        
        # 保存任务
        saved = await manager.save_task(task)
        print(f"任务保存成功: {saved}")
        
        # 加载任务
        loaded = await manager.load_task("test_task_001")
        print(f"任务加载成功: {loaded is not None}")
        
        # 获取统计
        stats = await manager.get_persistence_statistics()
        print(f"统计信息: {stats}")
    
    asyncio.run(test_data_persistence())
