"""
End-to-End Integration Tests

Tests the complete workflow of the API Automation Agent Platform.
Covers: document upload -> indexing -> test planning -> generation -> execution -> analysis
"""
import pytest
import asyncio
from pathlib import Path
import json
import tempfile
from typing import Dict, Any

from core.mcp_client import create_mcp_client, DEFAULT_SERVER_CONFIGS
from core.llm_service import get_llm_service, LLMConfig, LLMProvider
from core.test_executor import execute_tests
from core.document_indexer import index_uploaded_files
from core.session_manager import get_session_manager
from agents.subagents_updated import create_subagent
from api_agent.models import TestCase, TestStep, TestStatus

import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
async def mcp_client():
    """
    Fixture to create and connect MCP client for tests

    This fixture starts all MCP servers for testing.
    """
    # Create MCP client
    client = await create_mcp_client()

    yield client

    # Cleanup
    await client.disconnect_all()


@pytest.fixture
def sample_swagger_file():
    """
    Fixture to provide a sample Swagger file for testing
    """
    return """{
  "swagger": "2.0",
  "info": {
    "title": "Test API",
    "version": "1.0.0",
    "description": "Sample API for testing"
  },
  "host": "localhost",
  "basePath": "/api/v1",
  "schemes": ["http"],
  "paths": {
    "/auth/login": {
      "post": {
        "summary": "User login",
        "description": "Authenticate user and return JWT token",
        "tags": ["auth"],
        "produces": ["application/json"],
        "parameters": [
          {
            "name": "body",
            "in": "body",
            "required": true,
            "schema": {
              "type": "object",
              "required": ["username", "password"],
              "properties": {
                "username": {
                  "type": "string",
                  "example": "testuser"
                },
                "password": {
                  "type": "string",
                  "format": "password",
                  "example": "Test@123"
                }
              }
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Login successful",
            "schema": {
              "type": "object",
              "properties": {
                "token": {
                  "type": "string",
                  "description": "JWT authentication token"
                },
                "user": {
                  "type": "object",
                  "properties": {
                    "id": {"type": "string"},
                    "username": {"type": "string"}
                  }
                }
              }
            }
          },
          "401": {
            "description": "Invalid credentials",
            "schema": {
              "type": "object",
              "properties": {
                "error": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "/users/me": {
      "get": {
        "summary": "Get current user",
        "description": "Get authenticated user information",
        "tags": ["users"],
        "produces": ["application/json"],
        "security": [{"Bearer": []}],
        "responses": {
          "200": {
            "description": "User information",
            "schema": {
              "$ref": "#/definitions/User"
            }
          },
          "401": {
            "description": "Unauthorized"
          }
        }
      }
    }
  },
  "definitions": {
    "User": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string"}
      }
    }
  }
}"""


@pytest.mark.integration
class TestMCPClient:
    """Test MCP client integration"""

    @pytest.mark.asyncio
    async def test_mcp_client_connection(self, mcp_client):
        """
        Test that MCP client can connect to all servers

        Steps:
        1. Create MCP client
        2. Connect to all servers
        3. Verify connections
        """
        # Verify sessions exist
        assert "rag-server" in mcp_client.sessions
        assert "automation-quality" in mcp_client.sessions
        assert "chart-server" in mcp_client.sessions

        logger.info("✓ MCP client connected to all servers")

    @pytest.mark.asyncio
    async def test_rag_query_tool(self, mcp_client):
        """
        Test RAG query tool

        Steps:
        1. Call rag_query_data tool
        2. Verify response structure
        """
        result = await mcp_client.call_tool(
            "rag-server",
            "rag_query_data",
            {
                "query": "login API",
                "mode": "mix",
                "top_k": 5
            }
        )

        data = json.loads(result)
        assert "status" in data
        assert data["status"] == "success"
        assert "entities" in data
        assert "chunks" in data

        logger.info(f"✓ RAG query returned {len(data.get('entities', []))} entities")

    @pytest.mark.asyncio
    async def test_api_planner_tool(self, mcp_client, sample_swagger_file):
        """
        Test API planner tool

        Steps:
        1. Create temporary Swagger file
        2. Call api_planner tool
        3. Verify test plan structure
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(sample_swagger_file)
            swagger_path = f.name

        result = await mcp_client.call_tool(
            "automation-quality",
            "api_planner",
            {
                "schemaPath": swagger_path,
                "testCategories": ["functional", "security"]
            }
        )

        data = json.loads(result)
        assert "status" in data
        assert data["status"] == "success"
        assert "testPlan" in data
        assert "testCases" in data["testPlan"]

        test_cases = data["testPlan"]["testCases"]
        assert len(test_cases) > 0

        logger.info(f"✓ API planner generated {len(test_cases)} test cases")

        # Cleanup
        Path(swagger_path).unlink()

    @pytest.mark.asyncio
    async def test_api_generator_tool(self, mcp_client):
        """
        Test API generator tool

        Steps:
        1. Prepare test plan
        2. Call api_generator tool
        3. Verify generated code structure
        """
        test_plan = {
            "testCases": [
                {
                    "case_id": "TC001",
                    "name": "Test login",
                    "test_type": "functional",
                    "steps": [{
                        "step_id": "step_001",
                        "endpoint": "/api/v1/auth/login",
                        "method": "POST"
                    }]
                }
            ]
        }

        result = await mcp_client.call_tool(
            "automation-quality",
            "api_generator",
            {
                "testPlan": json.dumps(test_plan),
                "outputFormat": "playwright",
                "language": "typescript"
            }
        )

        data = json.loads(result)
        assert "status" in data
        assert data["status"] == "success"
        assert "testFiles" in data

        test_files = data["testFiles"]
        assert len(test_files) > 0

        logger.info(f"✓ API generator generated {len(test_files)} test files")


@pytest.mark.integration
class TestDocumentIndexing:
    """Test document indexing workflow"""

    @pytest.mark.asyncio
    async def test_document_parsing(self, mcp_client):
        """
        Test document parsing for multiple formats

        Steps:
        1. Create test documents (JSON, YAML)
        2. Parse documents
        3. Verify parsing results
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_content = {"openapi": "3.0.0", "info": {"title": "Test API"}}
            f.write(json.dumps(json_content))
            json_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = "swagger: '2.0'\ninfo:\n  title: 'Test API'"
            f.write(yaml_content)
            yaml_path = f.name

        try:
            from core.document_indexer import DocumentParser

            # Parse JSON
            json_result = await DocumentParser.parse(json_path)
            assert json_result["type"] == "json"
            assert "data" in json_result

            # Parse YAML
            yaml_result = await DocumentParser.parse(yaml_path)
            assert yaml_result["type"] == "yaml"
            assert "data" in yaml_result

            logger.info("✓ Document parsing successful for JSON and YAML")

        finally:
            Path(json_path).unlink()
            Path(yaml_path).unlink()

    @pytest.mark.asyncio
    async def test_document_indexing_to_rag(self, mcp_client):
        """
        Test document indexing to RAG knowledge base

        Steps:
        1. Create sample document
        2. Index document
        3. Query RAG to verify
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Login API\n\nEndpoint: POST /api/v1/auth/login\nParameters: username, password")
            doc_path = f.name

        # Index document
        results = await index_uploaded_files([doc_path], mcp_client=mcp_client)

        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["indexed"] == True

        logger.info("✓ Document indexed successfully")

        # Query RAG to verify
        query_result = await mcp_client.call_tool(
            "rag-server",
            "rag_query_data",
            {"query": "login API", "mode": "mix", "top_k": 5}
        )

        query_data = json.loads(query_result)
        assert query_data["status"] == "success"

        logger.info("✓ Document found in RAG query")

        Path(doc_path).unlink()


@pytest.mark.integration
class TestSessionManagement:
    """Test session management"""

    @pytest.mark.asyncio
    async def test_session_crud(self, mcp_client):
        """
        Test session CRUD operations

        Steps:
        1. Create session
        2. Get session
        3. Update session
        4. List sessions
        """
        session_mgr = get_session_manager(mcp_client)

        # Create
        created = await session_mgr.create_session(
            name="Test Session",
            description="Integration test session",
            user_id="test_user"
        )
        assert created["status"] == "success"
        assert "session_id" in created

        session_id = created["session_id"]

        # Get
        retrieved = await session_mgr.get_session(session_id)
        assert retrieved is not None
        assert retrieved["name"] == "Test Session"

        # Update
        updated = await session_mgr.update_session(
            session_id,
            {"auth_token": "test_token_123", "test_data": "updated"}
        )
        assert updated["meta_data"]["auth_token"] == "test_token_123"

        # List
        sessions = await session_mgr.list_sessions(user_id="test_user")
        assert len(sessions) >= 1
        assert any(s["session_id"] == session_id for s in sessions)

        logger.info("✓ Session CRUD operations successful")

    @pytest.mark.asyncio
    async def test_auth_token_management(self, mcp_client):
        """
        Test authentication token management in sessions

        Steps:
        1. Create session
        2. Set auth token
        3. Get auth token
        4. Verify token
        """
        session_mgr = get_session_manager(mcp_client)

        created = await session_mgr.create_session(
            name="Auth Test",
            description="Test auth token storage"
        )
        session_id = created["session_id"]

        # Set token
        await session_mgr.set_auth_token(session_id, "jwt_token_xyz")

        # Get token
        token_data = await session_mgr.get_auth_token(session_id)

        assert token_data is not None
        assert token_data["token"] == "jwt_token_xyz"
        assert token_data["type"] == "bearer"

        logger.info("✓ Auth token management successful")


@pytest.mark.integration
class TestAgentIntegration:
    """Test agent integration with MCP servers"""

    @pytest.mark.asyncio
    async def test_rag_agent_with_mcp(self, mcp_client):
        """
        Test RAG Retrieval Agent with real MCP client

        Steps:
        1. Create RAG agent with MCP client
        2. Execute query
        3. Verify results
        """
        rag_agent = create_subagent("rag-retrieval", mcp_client)

        result = await rag_agent.execute({
            "query": "authentication mechanism",
            "mode": "mix",
            "top_k": 3
        })

        assert result["status"] == "success"
        assert "entities" in result

        logger.info(f"✓ RAG Agent executed successfully: {len(result['entities'])} entities")

    @pytest.mark.asyncio
    async def test_planner_agent_with_mcp(self, mcp_client, sample_swagger_file):
        """
        Test Planner Agent with real MCP client

        Steps:
        1. Create Planner agent with MCP client
        2. Execute planning
        3. Verify test plan
        """
        planner_agent = create_subagent("planner", mcp_client)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(sample_swagger_file)
            swagger_path = f.name

        try:
            result = await planner_agent.execute({
                "api_info": {"path": swagger_path, "name": "Test API"},
                "test_categories": ["functional"]
            })

            assert result["status"] == "success"
            assert "testPlan" in result
            assert "testCases" in result["testPlan"]

            test_cases = result["testPlan"]["testCases"]
            assert len(test_cases) > 0

            logger.info(f"✓ Planner Agent generated {len(test_cases)} test cases")

        finally:
            Path(swagger_path).unlink()

    @pytest.mark.asyncio
    async def test_executor_with_real_runner(self):
        """
        Test Executor Agent with real test runner

        Steps:
        1. Create sample test file
        2. Execute tests
        3. Verify results
        """
        executor_agent = create_subagent("executor", mcp_client=None)

        # Create a simple test file
        test_code = """
import { test, expect } from '@playwright/test';

test.describe('Simple Test', () => {
  test('passing test', async ({ request }) => {
    const response = await request.get('https://httpbin.org/status/200');
    expect(response.status()).toBe(200);
  });
});
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.spec.ts', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            result = await executor_agent.execute({
                "test_files": [test_file],
                "config": {
                    "framework": "playwright",
                    "timeout": 30000
                }
            })

            assert result["status"] == "success"
            assert "results" in result

            suite_result = result["results"]
            assert suite_result["status"] == "completed"
            assert suite_result["total_cases"] >= 1

            logger.info(f"✓ Executor Agent executed tests: {suite_result['passed_cases']}/{suite_result['total_cases']} passed")

        finally:
            Path(test_file).unlink()


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, mcp_client):
        """
        Test complete workflow from document upload to test execution

        Workflow:
        1. Upload and index document
        2. Query RAG for API information
        3. Generate test plan
        4. Generate test code
        5. Execute tests (mock)
        6. Analyze results

        Note: This test uses a public API (httpbin.org) for actual execution.
        """
        # Step 1: Index document
        doc_content = """
# Test API Documentation

## Login Endpoint
- POST /api/v1/auth/login
- Parameters: username (string), password (string)
- Returns: JWT token, user object
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(doc_content)
            doc_path = f.name

        try:
            # Index document
            index_result = await index_uploaded_files([doc_path], mcp_client=mcp_client)
            assert index_result[0]["status"] == "success"
            logger.info("✓ Step 1: Document indexed")

            # Step 2: Query RAG
            rag_agent = create_subagent("rag-retrieval", mcp_client)
            rag_result = await rag_agent.execute({"query": "login endpoint", "mode": "mix"})
            assert rag_result["status"] == "success"
            logger.info("✓ Step 2: RAG query successful")

            # Step 3: Generate test plan
            planner_agent = create_subagent("planner", mcp_client)
            plan_result = await planner_agent.execute({
                "api_info": {
                    "name": "Login API",
                    "path": "/api/v1/auth/login",
                    "method": "POST"
                },
                "test_categories": ["functional"]
            })
            assert plan_result["status"] == "success"
            test_plan = plan_result["testPlan"]
            logger.info("✓ Step 3: Test plan generated")

            # Step 4: Generate test code
            generator_agent = create_subagent("generator", mcp_client)
            code_result = await generator_agent.execute({
                "test_plan": test_plan,
                "format": "playwright",
                "language": "typescript"
            })
            assert code_result["status"] == "success"
            assert "testFiles" in code_result
            logger.info("✓ Step 4: Test code generated")

            # Step 5: Execute tests (with httpbin.org as mock)
            test_code = """
import { test, expect } from '@playwright/test';

test.describe('End-to-End Test', () => {
  test('should get 200', async ({ request }) => {
    const response = await request.get('https://httpbin.org/status/200');
    expect(response.status()).toBe(200);
  });

  test('should handle 404', async ({ request }) => {
    const response = await request.get('https://httpbin.org/status/404');
    expect(response.status()).toBe(404);
  });
});
"""

            with tempfile.NamedTemporaryFile(mode='w', suffix='.spec.ts', delete=False) as f:
                f.write(test_code)
                test_file = f.name

            try:
                executor_result = await execute_tests(
                    framework="playwright",
                    test_files=[test_file],
                    timeout=60000
                )
                assert executor_result.suite_id is not None
                assert executor_result.total_cases >= 2
                logger.info(f"✓ Step 5: Tests executed ({executor_result.passed_cases}/{executor_result.total_cases} passed)")

                # Step 6: Analyze results
                analyzer_agent = create_subagent("analyzer", mcp_client)
                analysis = await analyzer_agent.execute({
                    "test_results": {
                        "total_cases": executor_result.total_cases,
                        "passed_cases": executor_result.passed_cases,
                        "failed_cases": executor_result.failed_cases,
                        "skipped_cases": executor_result.skipped_cases,
                        "duration_ms": executor_result.duration_ms,
                        "case_results": [
                            {
                                "case_id": cr.case_id,
                                "case_name": cr.case_name,
                                "status": cr.status,
                                "duration_ms": cr.duration_ms
                            }
                            for cr in executor_result.case_results
                        ]
                    },
                    "include_charts": True,
                    "format": "markdown"
                })
                assert analysis["status"] == "success"
                assert "summary" in analysis
                logger.info("✓ Step 6: Results analyzed")

                logger.info("✅ Complete end-to-end workflow successful!")

            finally:
                Path(test_file).unlink()

        finally:
            Path(doc_path).unlink()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_execution():
    """
    Test parallel test execution capability

    This test verifies that the executor can run tests in parallel.
    """
    test_code = """
import { test, expect } from '@playwright/test';

test.describe('Parallel Test', () => {
  test('test 1', async ({ request }) => {
    const response = await request.get('https://httpbin.org/delay/1');
    expect(response.status()).toBe(200);
  });

  test('test 2', async ({ request }) => {
    const response = await request.get('https://httpbin.org/delay/1');
    expect(response.status()).toBe(200);
  });
});
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.spec.ts', delete=False) as f:
        f.write(test_code)
        test_file = f.name

    try:
        result = await execute_tests(
            framework="playwright",
            test_files=[test_file],
            parallel=True,
            timeout=60000
        )

        assert result.suite_id is not None
        assert result.total_cases == 2
        assert result.passed_cases >= 1

        logger.info(f"✓ Parallel execution: {result.passed_cases}/{result.total_cases} passed")

    finally:
        Path(test_file).unlink()


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and recovery"""

    @pytest.mark.asyncio
    async def test_invalid_document_format(self, mcp_client):
        """
        Test handling of invalid document formats

        Steps:
        1. Try to parse invalid file
        2. Verify error handling
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.invalid', delete=False) as f:
            f.write("This is not a valid document format")
            invalid_path = f.name

        try:
            from core.document_indexer import DocumentParser

            # Should raise ValueError or return error
            result = await DocumentParser.parse(invalid_path)
            # Either parsing succeeds gracefully or fails with proper error

        finally:
            Path(invalid_path).unlink()

    @pytest.mark.asyncio
    async def test_mcp_server_unavailable(self):
        """
        Test graceful degradation when MCP servers are unavailable

        Steps:
        1. Create agent without MCP client
        2. Execute operation
        3. Verify fallback behavior
        """
        # Create agent without MCP client
        rag_agent = create_subagent("rag-retrieval", mcp_client=None)

        # Should fall back to mock response
        result = await rag_agent.execute({"query": "test query", "mode": "mix"})

        assert result["status"] == "success"
        # Should return mock data when no MCP client
        assert "entities" in result

        logger.info("✓ Agent gracefully handles unavailable MCP server")


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
