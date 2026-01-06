"""
RAG MCP Server - 知识检索服务

基于AnythingChatRAG实现的MCP服务器，提供：
- 6种检索模式（local/global/hybrid/naive/mix/bypass）
- 多模态内容处理（PDF、Word、Excel、图片）
- 知识图谱构建和查询
- 实体和关系提取
- 引用追踪和置信度评分
"""
from typing import Any, Optional, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json
import uuid
from datetime import datetime
from pathlib import Path
import sys
import asyncio

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.simple_rag import AnythingChatRAGEngine, RetrievalMode
from core.models import RAGEntity, RAGRelationship, RAGChunk, RAGCitation
from core.logging_config import get_logger

# 初始化日志
logger = get_logger(__name__)

# 全局RAG引擎实例
rag_engine: Optional[AnythingChatRAGEngine] = None


def get_rag_engine() -> AnythingChatRAGEngine:
    """获取或创建RAG引擎实例"""
    global rag_engine
    if rag_engine is None:
        logger.info("初始化RAG引擎...")
        rag_engine = AnythingChatRAGEngine(
            persist_directory="./data/chromadb",
            collection_name="api_knowledge",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("RAG引擎初始化完成")
    return rag_engine


# 创建MCP服务器
app = Server("rag-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="rag_query_data",
            description="从知识库检索API接口信息和相关文档",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询文本，例如：'获取登录接口的详细信息'"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid", "naive", "mix", "bypass"],
                        "default": "mix",
                        "description": "检索模式：local-本地实体检索，global-全局知识图谱，hybrid-混合检索，naive-向量相似性，mix-综合检索（推荐），bypass-直接查询"
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 10,
                        "description": "返回的最大结果数"
                    },
                    "chunk_top_k": {
                        "type": "integer",
                        "default": 5,
                        "description": "返回的文本块数量"
                    },
                    "enable_rerank": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用重排序"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="rag_index_document",
            description="索引API文档到知识库",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "文档路径（支持PDF、Word、Excel、Markdown等）"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["openapi", "swagger", "graphql", "markdown", "pdf", "word", "excel"],
                        "description": "文档类型"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "文档元数据"
                    }
                },
                "required": ["document_path"]
            }
        ),
        Tool(
            name="rag_get_entities",
            description="获取知识图谱中的实体列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "实体类型过滤（可选）"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "返回的最大实体数"
                    }
                }
            }
        ),
        Tool(
            name="rag_get_relationships",
            description="获取实体之间的关系",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "实体ID（可选，不提供则返回所有关系）"
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "关系类型过滤（可选）"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "rag_query_data":
            return await handle_rag_query(arguments)
        elif name == "rag_index_document":
            return await handle_index_document(arguments)
        elif name == "rag_get_entities":
            return await handle_get_entities(arguments)
        elif name == "rag_get_relationships":
            return await handle_get_relationships(arguments)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
            )]
    except Exception as e:
        logger.error(f"工具调用失败: {name}", exc_info=e)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False)
        )]


async def handle_rag_query(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理RAG查询请求"""
    query = arguments.get("query", "")
    mode = arguments.get("mode", "mix")
    top_k = arguments.get("top_k", 10)
    chunk_top_k = arguments.get("chunk_top_k", 5)
    enable_rerank = arguments.get("enable_rerank", True)

    logger.info(f"RAG查询: query={query}, mode={mode}, top_k={top_k}")

    # 获取RAG引擎
    engine = get_rag_engine()

    # 执行查询
    start_time = datetime.utcnow()
    result = await engine.aquery(
        query=query,
        mode=RetrievalMode(mode),
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        enable_rerank=enable_rerank
    )
    processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

    # 构建响应
    response = {
        "query_id": str(uuid.uuid4()),
        "query": query,
        "mode": mode,
        "entities": [
            {
                "entity_id": e.id,
                "entity_name": e.name,
                "entity_type": e.type,
                "description": e.description,
                "properties": e.properties,
                "confidence": getattr(e, 'confidence', 1.0)
            }
            for e in result.entities[:top_k]
        ],
        "relationships": [
            {
                "relationship_id": r.id,
                "source_id": r.source_id,
                "target_id": r.target_id,
                "relationship_type": r.type,
                "description": r.description,
                "properties": r.properties
            }
            for r in result.relationships
        ],
        "chunks": [
            {
                "chunk_id": c.id,
                "content": c.content,
                "source": c.source,
                "chunk_type": c.chunk_type,
                "metadata": c.metadata,
                "score": getattr(c, 'score', 0.0)
            }
            for c in result.chunks[:chunk_top_k]
        ],
        "citations": [
            {
                "citation_id": str(uuid.uuid4()),
                "source_document": c.get("source", ""),
                "content_snippet": c.get("content", "")[:200]
            }
            for c in result.chunks[:3]
        ],
        "confidence": result.confidence,
        "processing_time_ms": processing_time,
        "metadata": {
            "total_entities": len(result.entities),
            "total_relationships": len(result.relationships),
            "total_chunks": len(result.chunks)
        }
    }

    logger.info(f"RAG查询完成: 找到 {len(result.entities)} 个实体, {len(result.chunks)} 个文本块")

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def handle_index_document(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理文档索引请求"""
    document_path = arguments.get("document_path", "")
    document_type = arguments.get("document_type", "markdown")
    metadata = arguments.get("metadata", {})

    logger.info(f"索引文档: path={document_path}, type={document_type}")

    # 获取RAG引擎
    engine = get_rag_engine()

    # 索引文档
    try:
        result = await engine.index_document(
            document_path=document_path,
            document_type=document_type,
            metadata=metadata
        )

        response = {
            "success": True,
            "document_path": document_path,
            "document_type": document_type,
            "indexed_chunks": result.get("indexed_chunks", 0),
            "extracted_entities": result.get("extracted_entities", 0),
            "message": "文档索引成功"
        }

        logger.info(f"文档索引完成: {result.get('indexed_chunks', 0)} 个文本块")

    except Exception as e:
        logger.error(f"文档索引失败: {e}", exc_info=e)
        response = {
            "success": False,
            "error": str(e),
            "message": "文档索引失败"
        }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def handle_get_entities(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理获取实体请求"""
    entity_type = arguments.get("entity_type")
    limit = arguments.get("limit", 50)

    logger.info(f"获取实体: type={entity_type}, limit={limit}")

    # 获取RAG引擎
    engine = get_rag_engine()

    # 获取实体
    entities = engine.get_entities(entity_type=entity_type, limit=limit)

    response = {
        "entities": [
            {
                "entity_id": e.id,
                "entity_name": e.name,
                "entity_type": e.type,
                "description": e.description,
                "properties": e.properties
            }
            for e in entities
        ],
        "total": len(entities)
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def handle_get_relationships(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理获取关系请求"""
    entity_id = arguments.get("entity_id")
    relationship_type = arguments.get("relationship_type")

    logger.info(f"获取关系: entity_id={entity_id}, type={relationship_type}")

    # 获取RAG引擎
    engine = get_rag_engine()

    # 获取关系
    relationships = engine.get_relationships(
        entity_id=entity_id,
        relationship_type=relationship_type
    )

    response = {
        "relationships": [
            {
                "relationship_id": r.id,
                "source_id": r.source_id,
                "target_id": r.target_id,
                "relationship_type": r.type,
                "description": r.description,
                "properties": r.properties
            }
            for r in relationships
        ],
        "total": len(relationships)
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动RAG MCP服务器"""
    logger.info("启动RAG MCP服务器...")

    # 初始化RAG引擎
    get_rag_engine()

    # 运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


