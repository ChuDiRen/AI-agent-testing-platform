"""
RAG MCP Server - 基于AnythingChatRAG的知识检索服务

提供6种检索模式：
1. local - 本地实体和关系检索
2. global - 全局知识图谱探索
3. hybrid - 混合检索策略
4. naive - 向量相似性搜索
5. mix - 综合检索（推荐）
6. bypass - 直接查询
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from rag.core import AnythingChatRAG, RAGQuery, RAGResult


# 创建RAG MCP服务器
rag_server = Server("rag-knowledge-retrieval")


@rag_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出可用的工具"""
    return [
        types.Tool(
            name="rag_query_data",
            description="从知识库检索API接口信息和相关文档",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询文本"
                    },
                    "mode": {
                        "type": "string",
                        "description": "检索模式 (local/global/hybrid/naive/mix/bypass)",
                        "enum": ["local", "global", "hybrid", "naive", "mix", "bypass"],
                        "default": "mix"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 10
                    },
                    "chunk_top_k": {
                        "type": "integer", 
                        "description": "文本块数量",
                        "default": 5
                    },
                    "enable_rerank": {
                        "type": "boolean",
                        "description": "启用重排序",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="rag_extract_entities",
            description="从文档中提取API相关的实体信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要分析的文本"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="rag_build_knowledge_graph",
            description="构建API知识图谱",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_docs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "API文档列表"
                    }
                },
                "required": ["api_docs"]
            }
        ),
        types.Tool(
            name="rag_search_similar",
            description="向量相似性搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询文本"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "相似度阈值",
                        "default": 0.7
                    }
                },
                "required": ["query"]
            }
        )
    ]


@rag_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理工具调用"""
    try:
        if name == "rag_query_data":
            return await _handle_rag_query_data(arguments)
        elif name == "rag_extract_entities":
            return await _handle_rag_extract_entities(arguments)
        elif name == "rag_build_knowledge_graph":
            return await _handle_rag_build_knowledge_graph(arguments)
        elif name == "rag_search_similar":
            return await _handle_rag_search_similar(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error calling tool {name}: {str(e)}"
            )
        ]


async def _handle_rag_query_data(arguments: dict) -> list[types.TextContent]:
    """处理RAG数据查询"""
    query = arguments.get("query", "")
    mode = arguments.get("mode", "mix")
    top_k = arguments.get("top_k", 10)
    chunk_top_k = arguments.get("chunk_top_k", 5)
    enable_rerank = arguments.get("enable_rerank", True)
    
    # 初始化RAG引擎
    rag = AnythingChatRAG()
    
    # 执行查询
    result = await rag.aquery(
        query=query,
        mode=mode,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        enable_rerank=enable_rerank
    )
    
    # 格式化结果
    formatted_result = {
        "status": "success",
        "mode": mode,
        "query": query,
        "entities": result.entities,
        "relationships": result.relationships,
        "text_chunks": result.text_chunks,
        "references": result.references,
        "metadata": result.metadata,
        "summary": {
            "entities_count": len(result.entities),
            "relationships_count": len(result.relationships),
            "chunks_count": len(result.text_chunks),
            "references_count": len(result.references)
        }
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_rag_extract_entities(arguments: dict) -> list[types.TextContent]:
    """处理实体提取"""
    text = arguments.get("text", "")
    
    # 初始化RAG引擎
    rag = AnythingChatRAG()
    
    # 提取实体
    entities = await rag._extract_entities(text)
    
    formatted_result = {
        "status": "success",
        "text": text,
        "entities": entities,
        "entities_count": len(entities)
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_rag_build_knowledge_graph(arguments: dict) -> list[types.TextContent]:
    """处理知识图谱构建"""
    api_docs = arguments.get("api_docs", [])
    
    # 初始化RAG引擎
    rag = AnythingChatRAG()
    
    # 构建知识图谱（模拟）
    knowledge_graph = {
        "nodes": [
            {"id": "user_management", "type": "module", "label": "用户管理模块"},
            {"id": "/api/users", "type": "endpoint", "label": "用户列表接口"},
            {"id": "/api/users/{id}", "type": "endpoint", "label": "用户详情接口"},
            {"id": "authentication", "type": "service", "label": "认证服务"}
        ],
        "edges": [
            {"source": "user_management", "target": "/api/users", "relationship": "contains"},
            {"source": "user_management", "target": "/api/users/{id}", "relationship": "contains"},
            {"source": "/api/users", "target": "authentication", "relationship": "requires"},
            {"source": "/api/users/{id}", "target": "authentication", "relationship": "requires"}
        ]
    }
    
    formatted_result = {
        "status": "success",
        "api_docs_count": len(api_docs),
        "knowledge_graph": knowledge_graph,
        "nodes_count": len(knowledge_graph["nodes"]),
        "edges_count": len(knowledge_graph["edges"])
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_rag_search_similar(arguments: dict) -> list[types.TextContent]:
    """处理相似性搜索"""
    query = arguments.get("query", "")
    threshold = arguments.get("threshold", 0.7)
    
    # 初始化RAG引擎
    rag = AnythingChatRAG()
    
    # 执行相似性搜索
    similar_results = await rag._naive_retrieval(
        RAGQuery(
            query=query,
            mode="naive",
            top_k=5,
            chunk_top_k=3,
            enable_rerank=True
        )
    )
    
    # 过滤相似度结果
    filtered_results = [
        chunk for chunk in similar_results.text_chunks
        if chunk.get("similarity", 0) >= threshold
    ]
    
    formatted_result = {
        "status": "success",
        "query": query,
        "threshold": threshold,
        "similar_results": filtered_results,
        "results_count": len(filtered_results)
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def main():
    """启动RAG MCP服务器"""
    # 使用stdio传输
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await rag_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rag-knowledge-retrieval",
                server_version="1.0.0",
                capabilities=rag_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def create_rag_server():
    """创建RAG MCP服务器实例"""
    return rag_server


if __name__ == "__main__":
    asyncio.run(main())
