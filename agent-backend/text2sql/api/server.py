"""Text2SQL 扩展路由（挂载到 LangGraph API）"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

_root = Path(__file__).parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """使用 lifespan 替代 on_event"""
    from text2sql.database import setup_chinook, register_connection, DatabaseConfig
    db_path = setup_chinook()
    register_connection(0, DatabaseConfig(db_type="sqlite", database=str(db_path)))
    yield


app = FastAPI(title="Text2SQL Extensions", version="1.0.0", lifespan=lifespan)


@app.get("/memory/stats")
async def memory_stats():
    """记忆系统统计"""
    from memory import get_memory_manager
    mm = get_memory_manager()
    return {
        "sessions_count": len(mm.list_sessions()),
        "schema_cached": mm.get_cached_schema(0) is not None,
        "checkpointer_type": type(mm.checkpointer).__name__,
        "store_type": type(mm.store).__name__
    }


@app.post("/memory/schema/{connection_id}/invalidate")
async def invalidate_schema(connection_id: int):
    """清除 Schema 缓存"""
    from memory import get_memory_manager
    get_memory_manager().invalidate_schema_cache(connection_id)
    return {"ok": True}


@app.post("/query")
async def simple_query(query: str, thread_id: str = None, user_id: str = "default"):
    """简化查询接口"""
    import uuid
    from text2sql.chat_graph import create_text2sql_graph
    
    thread_id = thread_id or str(uuid.uuid4())
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    
    result = graph.invoke(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": thread_id, "user_id": user_id}}
    )
    return {"thread_id": thread_id, "result": result}
