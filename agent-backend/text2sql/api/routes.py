"""
API路由

定义FastAPI路由
"""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse

from text2sql.api.schemas import (
    QueryRequest, QueryWithPaginationRequest, QueryResult,
    ChartRequest, ChartResponse,
    ConnectionConfig, ConnectionResponse,
    SchemaInfo, HealthResponse, ErrorResponse
)
from text2sql.chat_graph import process_sql_query, stream_sql_query
from text2sql.database.db_manager import (
    register_connection, get_database_manager, 
    DatabaseConfig, DatabaseType
)
from text2sql.streaming.sse import format_as_sse
from text2sql.tools.chart_tools import generate_chart


router = APIRouter(prefix="/api/v1", tags=["text2sql"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        services={
            "database": True,
            "llm": True
        }
    )


@router.post("/query", response_model=QueryResult)
async def query(request: QueryWithPaginationRequest):
    """执行自然语言查询
    
    将自然语言转换为SQL并执行
    """
    try:
        # 生成会话ID
        thread_id = request.thread_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        # 处理分页
        pagination = None
        if request.pagination:
            pagination = {
                "page": request.pagination.page,
                "page_size": request.pagination.page_size
            }
        
        # 执行查询
        result = await process_sql_query(
            query=request.query,
            connection_id=request.connection_id,
            thread_id=thread_id,
            user_id=user_id,
            pagination=pagination,
            stream=False
        )
        
        # 提取执行结果
        execution_result = result.get("execution_result", {})
        
        return QueryResult(
            success=execution_result.get("success", False),
            data=execution_result.get("data", []),
            columns=execution_result.get("columns", []),
            row_count=execution_result.get("row_count", 0),
            sql=result.get("generated_sql"),
            execution_time_ms=execution_result.get("execution_time_ms"),
            error=execution_result.get("error"),
            pagination=execution_result.get("pagination")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_stream(request: QueryRequest):
    """流式执行自然语言查询
    
    使用SSE返回流式结果
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    async def generate():
        try:
            async for chunk in stream_sql_query(
                query=request.query,
                connection_id=request.connection_id,
                thread_id=thread_id,
                user_id=user_id
            ):
                # 转换为SSE格式
                if hasattr(chunk, 'content'):
                    data = {"content": chunk.content}
                elif isinstance(chunk, dict):
                    data = chunk
                else:
                    data = {"content": str(chunk)}
                
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "event: end\ndata: {}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post("/connections", response_model=ConnectionResponse)
async def create_connection(config: ConnectionConfig):
    """创建数据库连接"""
    try:
        # 生成连接ID
        connection_id = hash(f"{config.db_type}:{config.host}:{config.database}") % 10000
        
        # 创建数据库配置
        db_config = DatabaseConfig(
            db_type=DatabaseType(config.db_type),
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        )
        
        # 注册连接
        manager = register_connection(connection_id, db_config)
        
        # 测试连接
        success, message = manager.test_connection()
        
        return ConnectionResponse(
            connection_id=connection_id,
            success=success,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/connections/{connection_id}/schema", response_model=SchemaInfo)
async def get_schema(connection_id: int):
    """获取数据库Schema"""
    try:
        manager = get_database_manager(connection_id)
        schema = manager.get_schema()
        
        return SchemaInfo(
            tables=[t.to_dict() for t in schema.tables],
            relationships=[r.to_dict() for r in schema.relationships]
        )
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/connections/{connection_id}/tables")
async def get_tables(connection_id: int):
    """获取数据库表列表"""
    try:
        manager = get_database_manager(connection_id)
        tables = manager.get_tables()
        return {"tables": tables}
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/chart", response_model=ChartResponse)
async def create_chart(request: ChartRequest):
    """生成图表"""
    try:
        result = generate_chart.invoke({
            "data": request.data,
            "columns": request.columns,
            "chart_type": request.chart_type,
            "title": request.title or "Chart"
        })
        
        return ChartResponse(
            success=True,
            chart_config=result
        )
        
    except Exception as e:
        return ChartResponse(
            success=False,
            error=str(e)
        )


@router.post("/sql/validate")
async def validate_sql(sql: str = Query(...)):
    """验证SQL语句"""
    from text2sql.tools.validation_tools import validate_sql as validate_tool
    
    result = validate_tool.invoke({"sql": sql})
    return result


@router.post("/sql/execute")
async def execute_sql(
    connection_id: int,
    sql: str = Query(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000)
):
    """直接执行SQL语句"""
    try:
        manager = get_database_manager(connection_id)
        result = manager.execute_query_with_pagination(sql, page, page_size)
        return result.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
