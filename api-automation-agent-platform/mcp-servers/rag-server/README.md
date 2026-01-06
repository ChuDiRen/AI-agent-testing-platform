# RAG MCP Server

Knowledge retrieval service based on AnythingChatRAG.

## Features

- **6 Retrieval Modes**: local, global, hybrid, naive, mix, bypass
- **Multi-modal Support**: Text, images, tables, formulas
- **Knowledge Graph**: Entity and relationship management
- **Vector Search**: Semantic similarity search

## Installation

```bash
pip install anythingchatrag chromadb sentence-transformers
```

## Usage

### Start Server

```bash
python -m mcp_servers.rag_server
```

### Available Tools

1. **rag_query_data** - Query knowledge base
2. **rag_add_documents** - Index documents
3. **rag_create_entity** - Create entities
4. **rag_create_relations** - Create relationships
5. **rag_search_nodes** - Search knowledge graph
6. **rag_get_collection_stats** - Get statistics

## Configuration

See `.env.example` for RAG configuration options.
