"""
RAG MCP Server - Unit Tests
"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class TestRAGEngine:
    """Test cases for RAG Engine"""

    @pytest.fixture
    async def rag_engine(self):
        """Create a temporary RAG engine for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from mcp_servers.rag_server import RAGEngine

            engine = RAGEngine(
                persist_directory=tmpdir,
                collection_name="test_collection",
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            yield engine

            # Cleanup
            engine.client.delete_collection("test_collection")

    @pytest.mark.asyncio
    async def test_chunk_text(self, rag_engine):
        """Test text chunking with overlap"""
        text = "This is a test document. " * 20  # 360 chars

        chunks = rag_engine._chunk_text(text)

        assert len(chunks) > 0
        assert any(len(chunk) > 0 for chunk in chunks)
        print(f"✓ Text chunked into {len(chunks)} chunks")

    @pytest.mark.asyncio
    async def test_add_document(self, rag_engine):
        """Test adding a document"""
        doc_content = """
        POST /api/v1/auth/login - User authentication endpoint.
        Requires username and password in request body.
        Returns JWT token on success.
        """

        doc_id = await rag_engine.add_document(
            content=doc_content,
            metadata={"title": "Login API", "type": "openapi"}
        )

        assert doc_id is not None
        assert len(doc_id) > 0

        # Check if entities were extracted
        assert len(rag_engine.entities) > 0
        print(f"✓ Document added with ID: {doc_id}")
        print(f"  Extracted {len(rag_engine.entities)} entities")

    @pytest.mark.asyncio
    async def test_query_naive_mode(self, rag_engine):
        """Test naive retrieval mode"""
        # Add test document
        await rag_engine.add_document(
            content="GET /api/v1/users - Get user list endpoint",
            metadata={"title": "Users API"}
        )

        # Query
        result = await rag_engine.aquery(
            query="get user list",
            mode="naive",
            top_k=5
        )

        assert result is not None
        assert "chunks" in result
        assert len(result["chunks"]) > 0

        # Check if score is present
        chunk = result["chunks"][0]
        assert "score" in chunk or chunk.get("content")
        print(f"✓ Naive mode query returned {len(result['chunks'])} chunks")

    @pytest.mark.asyncio
    async def test_query_mix_mode(self, rag_engine):
        """Test mix retrieval mode (recommended)"""
        # Add test documents
        await rag_engine.add_document(
            content="POST /api/v1/auth/login - User authentication",
            metadata={"title": "Login API"}
        )
        await rag_engine.add_document(
            content="GET /api/v1/users - User list",
            metadata={"title": "Users API"}
        )

        # Query
        result = await rag_engine.aquery(
            query="authentication endpoints",
            mode="mix",
            top_k=10
        )

        assert result is not None
        assert "chunks" in result or "entities" in result

        total_results = len(result.get("chunks", [])) + len(result.get("entities", []))
        assert total_results > 0
        print(f"✓ Mix mode query returned {total_results} results")

    @pytest.mark.asyncio
    async def test_bypass_mode(self, rag_engine):
        """Test bypass mode - return all entities"""
        # Add entities
        await rag_engine.create_entities([
            {
                "name": "POST /api/v1/auth/login",
                "entity_type": "API_ENDPOINT",
                "observations": ["User authentication"]
            },
            {
                "name": "GET /api/v1/users",
                "entity_type": "API_ENDPOINT",
                "observations": ["Get user list"]
            }
        ])

        # Query bypass mode
        result = await rag_engine.aquery(
            query="any query",
            mode="bypass",
            top_k=10
        )

        assert result is not None
        assert "entities" in result
        assert len(result["entities"]) > 0
        print(f"✓ Bypass mode returned {len(result['entities'])} entities")

    @pytest.mark.asyncio
    async def test_create_entity(self, rag_engine):
        """Test entity creation"""
        count = await rag_engine.create_entities([
            {
                "name": "POST /api/v1/auth/login",
                "entity_type": "API_ENDPOINT",
                "observations": ["Test observation"]
            }
        ])

        assert count == 1
        assert len(rag_engine.entities) > 0
        print(f"✓ Created entity, total entities: {len(rag_engine.entities)}")

    @pytest.mark.asyncio
    async def test_create_relations(self, rag_engine):
        """Test relationship creation"""
        # Create entities first
        await rag_engine.create_entities([
            {"name": "Login API", "entity_type": "API_ENDPOINT", "observations": []},
            {"name": "JWT Token", "entity_type": "RESPONSE", "observations": []}
        ])

        # Create relationship
        count = await rag_engine.create_relations([
            {
                "from": "Login API",
                "to": "JWT Token",
                "relationType": "returns"
            }
        ])

        assert count == 1
        assert len(rag_engine.relationships) == 1
        print(f"✓ Created relationship: Login API -> returns -> JWT Token")

    @pytest.mark.asyncio
    async def test_search_nodes(self, rag_engine):
        """Test node search"""
        # Create entities
        await rag_engine.create_entities([
            {"name": "POST /api/v1/auth/login", "entity_type": "API_ENDPOINT", "observations": []},
            {"name": "GET /api/v1/users", "entity_type": "API_ENDPOINT", "observations": []}
        ])

        # Search
        nodes = await rag_engine.search_nodes("login")

        assert nodes is not None
        assert len(nodes) > 0
        assert any("login" in node["name"].lower() for node in nodes)
        print(f"✓ Node search found {len(nodes)} matching nodes")

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, rag_engine):
        """Test collection statistics"""
        # Add some data
        await rag_engine.add_document(
            content="Test document content",
            metadata={"title": "Test Doc"}
        )
        await rag_engine.create_entities([
            {"name": "Test Entity", "entity_type": "API_ENDPOINT", "observations": []}
        ])

        # Get stats
        stats = await rag_engine.get_collection_stats()

        assert stats is not None
        assert "total_chunks" in stats
        assert "total_entities" in stats
        assert "total_relationships" in stats
        assert "collection_name" in stats

        print(f"✓ Collection stats:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Total entities: {stats['total_entities']}")
        print(f"  Total relationships: {stats['total_relationships']}")

    @pytest.mark.asyncio
    async def test_entity_extraction(self, rag_engine):
        """Test entity extraction from text"""
        text = """
        API Documentation:
        - POST /api/v1/auth/login - User login endpoint
        - GET /api/v1/users - Get user list
        - Parameters: username, password
        - Status codes: 200, 401, 404
        """

        entities = rag_engine._extract_entities(text)

        assert entities is not None
        assert len(entities) > 0

        # Check if we extracted API endpoints
        api_entities = [e for e in entities if e["entity_type"] == "API_ENDPOINT"]
        assert len(api_entities) > 0

        print(f"✓ Extracted {len(entities)} entities:")
        print(f"  API endpoints: {len(api_entities)}")
        for entity in entities[:3]:
            print(f"    - {entity['name']} ({entity['entity_type']})")

    @pytest.mark.asyncio
    async def test_embedding_generation(self, rag_engine):
        """Test embedding generation"""
        text = "Test text for embedding"

        embedding = rag_engine._generate_embedding(text)

        assert embedding is not None
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)

        print(f"✓ Generated embedding with {len(embedding)} dimensions")

    @pytest.mark.asyncio
    async def test_add_multiple_documents(self, rag_engine):
        """Test adding multiple documents at once"""
        docs = [
            {"content": "Document 1: User authentication API", "metadata": {"id": "doc1"}},
            {"content": "Document 2: User management API", "metadata": {"id": "doc2"}},
            {"content": "Document 3: Product catalog API", "metadata": {"id": "doc3"}}
        ]

        doc_ids = []
        for doc in docs:
            doc_id = await rag_engine.add_document(
                content=doc["content"],
                metadata=doc["metadata"]
            )
            doc_ids.append(doc_id)

        assert len(doc_ids) == 3
        assert all(doc_id is not None for doc_id in doc_ids)
        print(f"✓ Added {len(doc_ids)} documents")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
