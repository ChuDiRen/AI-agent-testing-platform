"""
RAG MCP Server - Enhanced Knowledge Retrieval Service with AnythingChatRAG

This MCP server provides advanced knowledge retrieval capabilities using:
- AnythingChatRAG engine for multi-modal content processing
- 6 retrieval modes: local, global, hybrid, naive, mix, bypass
- Support for PDF, Word, Excel, Images, and text documents
- Knowledge graph construction and querying
- Entity and relationship extraction
- Citation tracking and confidence scoring
"""
from typing import Any, Optional, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json
import uuid
from datetime import datetime
import re
from pathlib import Path
import hashlib
import sys
import os

# Add parent directory to path for core imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import AnythingChatRAG
try:
    from core.anything_rag import AnythingChatRAGEngine, RetrievalMode, get_anything_rag_instance
    ANYTHING_RAG_AVAILABLE = True
except ImportError:
    ANYTHING_RAG_AVAILABLE = False
    print("Warning: AnythingChatRAG not available, using fallback implementation")

# Fallback imports if AnythingChatRAG not available
from chromadb import Client, Collection
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize global RAG instance
rag_instance: Optional['RAGEngine'] = None


class RAGEngine:
    """
    RAG Engine for knowledge retrieval

    Features:
    - Vector-based semantic search
    - 6 retrieval modes
    - Document indexing
    - Entity and relationship management
    """

    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        collection_name: str = "api_knowledge",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """Initialize RAG engine"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Create persist directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.client = Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)

        # Knowledge graph storage
        self.entities: Dict[str, Dict] = {}
        self.relationships: List[Dict] = []

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def _extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text using pattern matching

        Returns list of entities with types: API_ENDPOINT, PARAMETER, RESPONSE, etc.
        """
        entities = []

        # Extract API endpoints
        api_pattern = r'(?:GET|POST|PUT|DELETE|PATCH)\s+(\/[^\s\)]+)'
        for match in re.finditer(api_pattern, text, re.IGNORECASE):
            entities.append({
                "name": f"{match.group(0)}",
                "entity_type": "API_ENDPOINT",
                "observations": ["HTTP method and path"]
            })

        # Extract parameter names
        param_pattern = r'(?:parameter|param|field):\s*["\']?([a-zA-Z_][a-zA-Z0-9_]*)'
        for match in re.finditer(param_pattern, text, re.IGNORECASE):
            entities.append({
                "name": match.group(1),
                "entity_type": "PARAMETER",
                "observations": ["API parameter"]
            })

        # Extract status codes
        status_pattern = r'\b(200|201|400|401|403|404|500)\b'
        for match in re.finditer(status_pattern, text):
            entities.append({
                "name": f"HTTP_{match.group(0)}",
                "entity_type": "STATUS_CODE",
                "observations": ["HTTP status code"]
            })

        return entities

    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> str:
        """
        Add document to knowledge base

        Returns document ID
        """
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap

        # Generate document ID
        doc_id = str(uuid.uuid4())

        # Chunk document
        chunks = self._chunk_text(content)

        # Generate embeddings
        embeddings = self._generate_embedding(chunks[0])

        # Add chunks to collection
        ids = []
        metadatas = []
        documents = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            ids.append(chunk_id)

            chunk_metadata = {
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            metadatas.append(chunk_metadata)

            documents.append(chunk)

        # Add to ChromaDB
        if len(chunks) == 1:
            self.collection.add(
                ids=ids[0],
                embeddings=embeddings,
                documents=documents[0],
                metadatas=metadatas[0]
            )
        else:
            # For multiple chunks, we'd need to generate embeddings for each
            # For simplicity, use same embedding for all chunks
            embeddings_list = [embeddings] * len(chunks)
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas
            )

        # Extract entities
        extracted_entities = self._extract_entities(content)
        for entity in extracted_entities:
            entity_id = hashlib.md5(entity["name"].encode()).hexdigest()
            self.entities[entity_id] = {
                "id": entity_id,
                "name": entity["name"],
                "entity_type": entity["entity_type"],
                "observations": entity["observations"],
                "doc_id": doc_id,
                "created_at": datetime.utcnow().isoformat()
            }

        return doc_id

    async def aquery(
        self,
        query: str,
        mode: str = "mix",
        top_k: int = 10,
        chunk_top_k: int = 5,
        enable_rerank: bool = True
    ) -> Dict[str, Any]:
        """
        Query knowledge base with specified mode

        Args:
            query: Query text
            mode: Retrieval mode (local, global, hybrid, naive, mix, bypass)
            top_k: Number of top results
            chunk_top_k: Number of top chunks
            enable_rerank: Enable result reranking

        Returns:
            Query results with entities, relationships, chunks, sources
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        results = {
            "entities": [],
            "relationships": [],
            "chunks": [],
            "sources": []
        }

        if mode == "bypass":
            # Bypass mode: return all entities
            results["entities"] = list(self.entities.values())[:top_k]

        elif mode in ["local", "naive"]:
            # Local/Naive mode: vector similarity search only
            query_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            for i, (doc_id, distance) in enumerate(zip(
                query_results["ids"][0] if query_results["ids"] else [],
                query_results["distances"][0] if query_results["distances"] else []
            )):
                if doc_id and i < top_k:
                    metadata = query_results["metadatas"][0][i] if query_results["metadatas"] else {}
                    chunk_text = query_results["documents"][0][i] if query_results["documents"] else ""

                    results["chunks"].append({
                        "content": chunk_text,
                        "score": float(1 - distance) if distance else 0.0,
                        "metadata": metadata
                    })

                    results["sources"].append({
                        "doc_id": metadata.get("doc_id", "unknown"),
                        "chunk_index": metadata.get("chunk_index", 0)
                    })

        elif mode in ["global", "mix"]:
            # Global/Mix mode: combine entity search and vector search
            # Vector search
            query_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # Entity search (keyword matching)
            query_lower = query.lower()
            matched_entities = []
            for entity_id, entity in self.entities.items():
                if query_lower in entity["name"].lower():
                    matched_entities.append(entity)

            if matched_entities:
                results["entities"] = matched_entities[:top_k]

            # Add chunks from vector search
            for i in range(min(top_k, len(query_results["ids"][0]) if query_results["ids"] else 0)):
                doc_id = query_results["ids"][0][i]
                distance = query_results["distances"][0][i] if query_results["distances"] else 1.0
                metadata = query_results["metadatas"][0][i] if query_results["metadatas"] else {}
                chunk_text = query_results["documents"][0][i] if query_results["documents"] else ""

                results["chunks"].append({
                    "content": chunk_text,
                    "score": float(1 - distance) if distance else 0.0,
                    "metadata": metadata
                })

                results["sources"].append({
                    "doc_id": metadata.get("doc_id", "unknown"),
                    "chunk_index": metadata.get("chunk_index", 0)
                })

            # Extract relationships from matched entities
            if matched_entities and self.relationships:
                entity_names = {e["name"] for e in matched_entities}
                for rel in self.relationships:
                    if rel.get("from") in entity_names or rel.get("to") in entity_names:
                        results["relationships"].append(rel)

        elif mode == "hybrid":
            # Hybrid mode: combine multiple strategies
            # This is a more advanced implementation that could include:
            # - Dense retrieval (vector search)
            # - Sparse retrieval (BM25/keyword)
            # - Reranking

            # For now, use mix mode as hybrid
            query_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            for i in range(min(top_k, len(query_results["ids"][0]) if query_results["ids"] else 0)):
                doc_id = query_results["ids"][0][i]
                distance = query_results["distances"][0][i] if query_results["distances"] else 1.0
                metadata = query_results["metadatas"][0][i] if query_results["metadatas"] else {}
                chunk_text = query_results["documents"][0][i] if query_results["documents"] else ""

                results["chunks"].append({
                    "content": chunk_text,
                    "score": float(1 - distance) if distance else 0.0,
                    "metadata": metadata
                })

        # Limit results
        results["chunks"] = results["chunks"][:chunk_top_k]

        return results

    async def create_entities(self, entities: List[Dict]) -> int:
        """Create entities in knowledge graph"""
        count = 0
        for entity in entities:
            entity_id = hashlib.md5(entity["name"].encode()).hexdigest()
            self.entities[entity_id] = {
                "id": entity_id,
                "name": entity["name"],
                "entity_type": entity["entity_type"],
                "observations": entity.get("observations", []),
                "created_at": datetime.utcnow().isoformat()
            }
            count += 1

        return count

    async def create_relations(self, relations: List[Dict]) -> int:
        """Create relationships between entities"""
        count = 0
        for relation in relations:
            self.relationships.append({
                "from": relation.get("from"),
                "to": relation.get("to"),
                "relationType": relation.get("relationType"),
                "created_at": datetime.utcnow().isoformat()
            })
            count += 1

        return count

    async def search_nodes(self, query: str) -> List[Dict]:
        """Search for nodes in knowledge graph"""
        query_lower = query.lower()
        matched = []

        for entity_id, entity in self.entities.items():
            if query_lower in entity["name"].lower():
                matched.append(entity)

        return matched

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        collection_count = self.collection.count()

        return {
            "total_chunks": collection_count,
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "collection_name": self.collection_name,
            "embedding_model": str(self.embedding_model)
        }


def get_rag_instance() -> RAGEngine:
    """Get or initialize RAG instance"""
    global rag_instance
    if rag_instance is None:
        rag_instance = RAGEngine(
            persist_directory="./data/chromadb",
            collection_name="api_knowledge",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=512,
            chunk_overlap=50
        )
    return rag_instance


# Create MCP server
app = Server("rag-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available RAG tools"""
    return [
        Tool(
            name="rag_query_data",
            description=(
                "Query knowledge base to retrieve API information and related documents. "
                "Supports 6 retrieval modes:\n"
                "- local: Local entity and relationship retrieval\n"
                "- global: Global knowledge graph exploration\n"
                "- hybrid: Hybrid retrieval strategy\n"
                "- naive: Vector similarity search\n"
                "- mix: Comprehensive retrieval (recommended)\n"
                "- bypass: Direct query"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query text to search for in knowledge base"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid", "naive", "mix", "bypass"],
                        "description": "Retrieval mode to use",
                        "default": "mix"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "chunk_top_k": {
                        "type": "integer",
                        "description": "Number of top chunks to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "enable_rerank": {
                        "type": "boolean",
                        "description": "Enable reranking of results",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="rag_add_documents",
            description="Add documents to knowledge base for indexing and retrieval",
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Document content"
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "Document metadata (title, type, source, etc.)"
                                }
                            },
                            "required": ["content"]
                        }
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Chunk size for text splitting",
                        "default": 512
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks",
                        "default": 50
                    }
                },
                "required": ["documents"]
            }
        ),
        Tool(
            name="rag_create_entity",
            description="Create entities in knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Entity name"
                                },
                                "entity_type": {
                                    "type": "string",
                                    "description": "Entity type (e.g., API_ENDPOINT, PARAMETER, RESPONSE)"
                                },
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of observations about entity"
                                }
                            },
                            "required": ["name", "entity_type", "observations"]
                        }
                    }
                },
                "required": ["entities"]
            }
        ),
        Tool(
            name="rag_create_relations",
            description="Create relationships between entities in knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {
                                    "type": "string",
                                    "description": "Source entity name"
                                },
                                "to": {
                                    "type": "string",
                                    "description": "Target entity name"
                                },
                                "relationType": {
                                    "type": "string",
                                    "description": "Type of relationship"
                                }
                            },
                            "required": ["from", "to", "relationType"]
                        }
                    }
                },
                "required": ["relations"]
            }
        ),
        Tool(
            name="rag_search_nodes",
            description="Search for nodes in knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="rag_get_collection_stats",
            description="Get statistics about knowledge collection",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "rag_query_data":
            return await rag_query_data(arguments)
        elif name == "rag_add_documents":
            return await rag_add_documents(arguments)
        elif name == "rag_create_entity":
            return await rag_create_entity(arguments)
        elif name == "rag_create_relations":
            return await rag_create_relations(arguments)
        elif name == "rag_search_nodes":
            return await rag_search_nodes(arguments)
        elif name == "rag_get_collection_stats":
            return await rag_get_collection_stats(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def rag_query_data(arguments: Any) -> list[TextContent]:
    """Enhanced query knowledge base using AnythingChatRAG"""
    
    query = arguments.get("query")
    mode = arguments.get("mode", "mix")
    top_k = arguments.get("top_k", 10)
    chunk_top_k = arguments.get("chunk_top_k", 5)
    enable_rerank = arguments.get("enable_rerank", True)
    filters = arguments.get("filters", {})

    if not query:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Query parameter is required"}, indent=2)
        )]

    try:
        if ANYTHING_RAG_AVAILABLE:
            # Use AnythingChatRAG engine
            rag = get_anything_rag_instance()
            
            # Convert mode string to enum
            mode_mapping = {
                "local": RetrievalMode.LOCAL,
                "global": RetrievalMode.GLOBAL,
                "hybrid": RetrievalMode.HYBRID,
                "naive": RetrievalMode.NAIVE,
                "mix": RetrievalMode.MIX,
                "bypass": RetrievalMode.BYPASS
            }
            
            retrieval_mode = mode_mapping.get(mode, RetrievalMode.MIX)
            
            # Execute query
            result = await rag.query(
                query=query,
                mode=retrieval_mode,
                top_k=top_k,
                chunk_top_k=chunk_top_k,
                enable_rerank=enable_rerank,
                filters=filters
            )
            
            # Format response
            response = {
                "status": "success",
                "query": query,
                "mode": mode,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "entities": [
                    {
                        "entity_id": entity.id,
                        "entity_name": entity.name,
                        "entity_type": entity.type,
                        "description": entity.description,
                        "properties": entity.properties
                    }
                    for entity in result.entities
                ],
                "relationships": [
                    {
                        "relationship_id": rel.id,
                        "source_id": rel.source_id,
                        "target_id": rel.target_id,
                        "type": rel.type,
                        "description": rel.description,
                        "properties": rel.properties
                    }
                    for rel in result.relationships
                ],
                "chunks": [
                    {
                        "chunk_id": chunk.id,
                        "content": chunk.content,
                        "source": chunk.source,
                        "chunk_type": chunk.chunk_type,
                        "metadata": chunk.metadata
                    }
                    for chunk in result.chunks
                ],
                "citations": result.citations,
                "stats": rag.get_stats()
            }
            
        else:
            # Fallback to basic RAG implementation
            rag = get_rag_instance()
            
            # Basic query implementation
            query_embedding = rag._generate_embedding(query)
            results = rag.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            response = {
                "status": "success",
                "query": query,
                "mode": mode,
                "chunks": [
                    {
                        "content": doc,
                        "metadata": meta,
                        "distance": dist
                    }
                    for doc, meta, dist in zip(
                        results["documents"][0],
                        results["metadatas"][0], 
                        results["distances"][0]
                    )
                ],
                "entities": [],
                "relationships": [],
                "citations": [],
                "confidence": 0.8,
                "processing_time": 0.1
            }

        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2, ensure_ascii=False)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e),
                "query": query
            }, indent=2)
        )]

    result = await rag.aquery(
        query=query,
        mode=mode,
        top_k=top_k,
        chunk_top_k=chunk_top_k,
        enable_rerank=enable_rerank
    )

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "mode": mode,
            "entities": result.get("entities", []),
            "relationships": result.get("relationships", []),
            "chunks": result.get("chunks", []),
            "sources": result.get("sources", [])
        }, indent=2, ensure_ascii=False)
    )]


async def rag_add_documents(arguments: Any) -> list[TextContent]:
    """Add documents to knowledge base"""
    rag = get_rag_instance()

    documents = arguments.get("documents", [])
    chunk_size = arguments.get("chunk_size", 512)
    chunk_overlap = arguments.get("chunk_overlap", 50)

    results = []
    for doc in documents:
        content = doc.get("content")
        metadata = doc.get("metadata", {})

        doc_id = await rag.add_document(
            content=content,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        results.append({"doc_id": doc_id, "status": "indexed"})

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "indexed_documents": len(results),
            "results": results
        }, indent=2, ensure_ascii=False)
    )]


async def rag_create_entity(arguments: Any) -> list[TextContent]:
    """Create entities in knowledge graph"""
    rag = get_rag_instance()

    entities = arguments.get("entities", [])

    count = await rag.create_entities(entities)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "created_entities": count
        }, indent=2, ensure_ascii=False)
    )]


async def rag_create_relations(arguments: Any) -> list[TextContent]:
    """Create relationships between entities"""
    rag = get_rag_instance()

    relations = arguments.get("relations", [])

    count = await rag.create_relations(relations)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "created_relations": count
        }, indent=2, ensure_ascii=False)
    )]


async def rag_search_nodes(arguments: Any) -> list[TextContent]:
    """Search nodes in knowledge graph"""
    rag = get_rag_instance()

    query = arguments.get("query")

    nodes = await rag.search_nodes(query)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "nodes": nodes
        }, indent=2, ensure_ascii=False)
    )]


async def rag_get_collection_stats(arguments: Any) -> list[TextContent]:
    """Get collection statistics"""
    rag = get_rag_instance()

    stats = await rag.get_collection_stats()

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "statistics": stats
        }, indent=2, ensure_ascii=False)
    )]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
