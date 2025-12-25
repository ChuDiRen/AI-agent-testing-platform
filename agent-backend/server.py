"""
LangGraph API Server with SQLite Persistence

Production-ready server using SQLite for checkpointer and store.
"""

import os
import sys
import json
import sqlite3
import asyncio
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

# Database paths
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DB = DATA_DIR / "checkpoints.db"
THREADS_DB = DATA_DIR / "threads.db"

# Global instances
_checkpointer: Optional[SqliteSaver] = None
_graphs: Dict[str, Any] = {}


def get_checkpointer() -> SqliteSaver:
    """Get SQLite checkpointer singleton"""
    global _checkpointer
    if _checkpointer is None:
        conn = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
        _checkpointer.setup()
    return _checkpointer


def init_threads_db():
    """Initialize threads metadata database"""
    conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            assistant_id TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def load_graphs() -> Dict[str, Any]:
    """Load all graphs from langgraph.json"""
    config_path = Path(__file__).parent / "langgraph.json"
    with open(config_path) as f:
        config = json.load(f)
    
    graphs = {}
    checkpointer = get_checkpointer()
    
    for graph_id, graph_path in config.get("graphs", {}).items():
        try:
            module_path, func_name = graph_path.split(":")
            module_path = module_path.replace("./", "").replace("/", ".").replace(".py", "")
            
            module = importlib.import_module(module_path)
            factory_func = getattr(module, func_name)
            
            # Get the graph
            graph = factory_func()
            
            # Compile with checkpointer if needed
            if hasattr(graph, 'compile'):
                graphs[graph_id] = graph.compile(checkpointer=checkpointer)
            else:
                graphs[graph_id] = graph
                
            print(f"[OK] Loaded: {graph_id}")
        except Exception as e:
            print(f"[FAIL] {graph_id}: {e}")
    
    return graphs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global _graphs
    print("=" * 50)
    print("LangGraph API Server (SQLite)")
    print(f"Checkpoint DB: {CHECKPOINT_DB}")
    print(f"Threads DB: {THREADS_DB}")
    print("=" * 50)
    
    init_threads_db()
    _graphs = load_graphs()
    print(f"Loaded {len(_graphs)} graphs")
    
    yield
    
    # Cleanup
    if _checkpointer:
        pass  # SqliteSaver doesn't need explicit close


app = FastAPI(
    title="LangGraph API Server",
    description="LangGraph API with SQLite persistence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Models ==============

class ThreadCreate(BaseModel):
    assistant_id: str
    metadata: Optional[Dict[str, Any]] = None


class ThreadResponse(BaseModel):
    thread_id: str
    assistant_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class RunCreate(BaseModel):
    assistant_id: str
    input: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    stream_mode: Optional[List[str]] = None


class AssistantResponse(BaseModel):
    assistant_id: str
    name: str
    config: Dict[str, Any] = {}


# ============== Endpoints ==============

@app.get("/")
async def root():
    return {
        "status": "ok",
        "storage": "sqlite",
        "assistants": list(_graphs.keys())
    }


@app.get("/info")
async def info():
    return {
        "version": "1.0.0",
        "storage": {
            "type": "sqlite",
            "checkpoint_db": str(CHECKPOINT_DB),
            "threads_db": str(THREADS_DB)
        },
        "assistants": list(_graphs.keys())
    }


# ============== Assistants ==============

@app.get("/assistants", response_model=List[AssistantResponse])
async def list_assistants():
    """List all available assistants"""
    return [
        AssistantResponse(
            assistant_id=aid,
            name=aid,
            config={}
        )
        for aid in _graphs.keys()
    ]


@app.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """Get assistant by ID"""
    if assistant_id not in _graphs:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")
    return {
        "assistant_id": assistant_id,
        "name": assistant_id,
        "config": {}
    }


# ============== Threads ==============

@app.post("/threads", response_model=ThreadResponse)
async def create_thread(body: ThreadCreate):
    """Create a new thread"""
    thread_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
    conn.execute(
        "INSERT INTO threads (thread_id, assistant_id, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (thread_id, body.assistant_id, json.dumps(body.metadata or {}), now, now)
    )
    conn.commit()
    conn.close()
    
    return ThreadResponse(
        thread_id=thread_id,
        assistant_id=body.assistant_id,
        metadata=body.metadata,
        created_at=now,
        updated_at=now
    )


@app.get("/threads", response_model=List[ThreadResponse])
async def list_threads(assistant_id: Optional[str] = None):
    """List all threads"""
    conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
    
    if assistant_id:
        cursor = conn.execute(
            "SELECT thread_id, assistant_id, metadata, created_at, updated_at FROM threads WHERE assistant_id = ? ORDER BY updated_at DESC",
            (assistant_id,)
        )
    else:
        cursor = conn.execute(
            "SELECT thread_id, assistant_id, metadata, created_at, updated_at FROM threads ORDER BY updated_at DESC"
        )
    
    threads = []
    for row in cursor.fetchall():
        threads.append(ThreadResponse(
            thread_id=row[0],
            assistant_id=row[1],
            metadata=json.loads(row[2]) if row[2] else None,
            created_at=row[3],
            updated_at=row[4]
        ))
    
    conn.close()
    return threads


@app.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Get thread by ID"""
    conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
    cursor = conn.execute(
        "SELECT thread_id, assistant_id, metadata, created_at, updated_at FROM threads WHERE thread_id = ?",
        (thread_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
    
    return ThreadResponse(
        thread_id=row[0],
        assistant_id=row[1],
        metadata=json.loads(row[2]) if row[2] else None,
        created_at=row[3],
        updated_at=row[4]
    )


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread"""
    conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
    conn.execute("DELETE FROM threads WHERE thread_id = ?", (thread_id,))
    conn.commit()
    conn.close()
    
    # Also delete checkpoints
    try:
        cp_conn = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
        cp_conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cp_conn.commit()
        cp_conn.close()
    except:
        pass
    
    return {"status": "deleted", "thread_id": thread_id}


# ============== Runs ==============

@app.post("/threads/{thread_id}/runs")
async def create_run(thread_id: str, body: RunCreate):
    """Create and execute a run"""
    assistant_id = body.assistant_id
    
    if assistant_id not in _graphs:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")
    
    graph = _graphs[assistant_id]
    
    # Build config
    config = {
        "configurable": {
            "thread_id": thread_id,
            **(body.config.get("configurable", {}) if body.config else {})
        }
    }
    
    # Execute
    try:
        result = await asyncio.to_thread(
            graph.invoke,
            body.input,
            config
        )
        
        # Update thread timestamp
        conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
        conn.execute(
            "UPDATE threads SET updated_at = ? WHERE thread_id = ?",
            (datetime.now().isoformat(), thread_id)
        )
        conn.commit()
        conn.close()
        
        return {
            "run_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "assistant_id": assistant_id,
            "status": "completed",
            "output": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads/{thread_id}/runs/stream")
async def create_run_stream(thread_id: str, body: RunCreate):
    """Create and stream a run"""
    assistant_id = body.assistant_id
    
    if assistant_id not in _graphs:
        raise HTTPException(status_code=404, detail=f"Assistant {assistant_id} not found")
    
    graph = _graphs[assistant_id]
    
    # Build config
    config = {
        "configurable": {
            "thread_id": thread_id,
            **(body.config.get("configurable", {}) if body.config else {})
        }
    }
    
    async def event_generator():
        try:
            # Stream events
            for event in graph.stream(body.input, config, stream_mode="values"):
                yield f"data: {json.dumps({'event': 'values', 'data': serialize_event(event)})}\n\n"
            
            # Update thread timestamp
            conn = sqlite3.connect(str(THREADS_DB), check_same_thread=False)
            conn.execute(
                "UPDATE threads SET updated_at = ? WHERE thread_id = ?",
                (datetime.now().isoformat(), thread_id)
            )
            conn.commit()
            conn.close()
            
            yield f"data: {json.dumps({'event': 'end'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


def serialize_event(event: Any) -> Any:
    """Serialize event for JSON"""
    if isinstance(event, dict):
        return {k: serialize_event(v) for k, v in event.items()}
    elif isinstance(event, list):
        return [serialize_event(item) for item in event]
    elif isinstance(event, (HumanMessage, AIMessage, BaseMessage)):
        return {
            "type": event.__class__.__name__,
            "content": event.content,
            "additional_kwargs": event.additional_kwargs
        }
    elif hasattr(event, 'dict'):
        return event.dict()
    elif hasattr(event, '__dict__'):
        return {k: serialize_event(v) for k, v in event.__dict__.items() if not k.startswith('_')}
    else:
        return event


# ============== Thread State ==============

@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """Get current state of a thread"""
    checkpointer = get_checkpointer()
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        checkpoint = checkpointer.get(config)
        if checkpoint:
            return {
                "thread_id": thread_id,
                "checkpoint": serialize_event(checkpoint)
            }
        return {"thread_id": thread_id, "checkpoint": None}
    except Exception as e:
        return {"thread_id": thread_id, "error": str(e)}


@app.get("/threads/{thread_id}/history")
async def get_thread_history(thread_id: str):
    """Get history of a thread"""
    checkpointer = get_checkpointer()
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        history = list(checkpointer.list(config))
        return {
            "thread_id": thread_id,
            "history": [serialize_event(h) for h in history]
        }
    except Exception as e:
        return {"thread_id": thread_id, "history": [], "error": str(e)}


# ============== Health ==============

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ok")
async def ok():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
