"""
End-to-End Usage Examples

Demonstrates complete workflows of the API Automation Agent Platform.
Covers: document upload, test planning, test generation, execution, and analysis.
"""
import asyncio
from pathlib import Path
import json
import tempfile

from core.mcp_client import create_mcp_client, DEFAULT_SERVER_CONFIGS
from core.llm_service import get_llm_service, LLMConfig, LLMProvider
from core.test_executor import execute_tests, TestGenerator
from core.document_indexer import index_uploaded_files
from core.session_manager import get_session_manager
from agents.subagents_updated import create_subagent
from core.logging_config import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger("examples")


# ==================== Example 1: Complete Workflow ====================

async def example_complete_workflow():
    """
    Example 1: Complete end-to-end workflow

    Workflow:
    1. Upload API documentation
    2. Index document in RAG
    3. Generate test plan
    4. Generate test code
    5. Execute tests
    6. Analyze results

    Expected Time: 2-3 minutes
    """
    logger.info("=== Example 1: Complete Workflow ===")

    try:
        # Step 1: Initialize MCP client and LLM
        logger.info("Step 1: Initializing services...")
        mcp_client = await create_mcp_client()

        llm_service = get_llm_service(LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4-turbo-preview"
        ))

        logger.info("✓ Services initialized")

        # Step 2: Create sample Swagger file
        logger.info("Step 2: Creating sample API documentation...")

        swagger_content = """
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /auth/login:
    post:
      summary: User login
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  example: "testuser"
                password:
                  type: string
                  format: password
                  example: "Test@123"
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                    description: JWT authentication token
                  user:
                    type: object
        '401':
          description: Invalid credentials
  /users/me:
    get:
      summary: Get current user
      tags:
        - Users
      security:
        - Bearer: []
      responses:
        '200':
          description: User information
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  username:
                    type: string
                  email:
                    type: string
        '401':
          description: Unauthorized
"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(swagger_content)
            doc_path = f.name

        logger.info("✓ Sample API documentation created")

        # Step 3: Index document in RAG
        logger.info("Step 3: Indexing document in RAG...")
        index_result = await index_uploaded_files([doc_path], mcp_client=mcp_client)

        if index_result[0]["status"] != "success":
            logger.error(f"Failed to index document: {index_result[0]}")
            return

        doc_id = index_result[0]["doc_id"]
        logger.info(f"✓ Document indexed (ID: {doc_id})")

        # Step 4: Create session
        logger.info("Step 4: Creating session...")
        session_mgr = get_session_manager(mcp_client)
        session = await session_mgr.create_session(
            name="Complete Workflow Test",
            description="End-to-end test automation workflow"
            user_id="example_user"
        )

        session_id = session["session_id"]
        await session_mgr.set_auth_token(session_id, "test_token_xyz")
        logger.info(f"✓ Session created (ID: {session_id})")

        # Step 5: Generate test plan using Planner Agent
        logger.info("Step 5: Generating test plan...")
        planner_agent = create_subagent("planner", mcp_client)

        plan_result = await planner_agent.execute({
            "api_info": {
                "path": doc_path,
                "name": "Sample API",
                "type": "openapi"
            },
            "test_categories": ["functional", "security", "boundary"]
        })

        if plan_result["status"] != "success":
            logger.error(f"Failed to generate test plan: {plan_result}")
            return

        test_plan = plan_result["testPlan"]
        test_cases = test_plan.get("testCases", [])
        logger.info(f"✓ Test plan generated ({len(test_cases)} test cases)")

        # Step 6: Generate test code using Generator Agent
        logger.info("Step 6: Generating test code...")
        generator_agent = create_subagent("generator", mcp_client)

        code_result = await generator_agent.execute({
            "test_plan": test_plan,
            "format": "playwright",
            "language": "typescript",
            "base_url": "http://localhost:8000"
        })

        if code_result["status"] != "success":
            logger.error(f"Failed to generate test code: {code_result}")
            return

        test_files = code_result["testFiles"]
        logger.info(f"✓ Test code generated ({len(test_files)} files)")

        # Write test files to disk
        test_outputs_dir = Path("test_outputs")
        test_outputs_dir.mkdir(exist_ok=True)

        for filename, code in test_files.items():
            test_path = test_outputs_dir / filename
            test_path.write_text(code)
            logger.info(f"✓ Wrote test file: {filename}")

        test_file_paths = list(test_outputs_dir.glob("*.spec.ts"))
        logger.info(f"✓ Test files written to disk")

        # Step 7: Execute tests using Executor Agent
        logger.info("Step 7: Executing tests...")
        executor_agent = create_subagent("executor", mcp_client)

        # Note: In production, this would call a real test runner
        # For this example, we'll use mock execution
        exec_result = await executor_agent.execute({
            "test_files": test_file_paths,
            "config": {
                "framework": "playwright",
                "base_url": "http://localhost:8000",
                "timeout": 60000
            }
        })

        if exec_result["status"] != "success":
            logger.error(f"Test execution failed: {exec_result}")
            return

        suite_result = exec_result["results"]
        logger.info(f"✓ Tests executed ({suite_result['passed_cases']}/{suite_result['total_cases']} passed)")

        # Step 8: Analyze results using Analyzer Agent
        logger.info("Step 8: Analyzing results...")
        analyzer_agent = create_subagent("analyzer", mcp_client)

        analysis = await analyzer_agent.execute({
            "test_results": suite_result,
            "include_charts": True,
            "format": "markdown"
        })

        if analysis["status"] != "success":
            logger.error(f"Failed to analyze results: {analysis}")
            return

        logger.info(f"✓ Results analyzed")
        logger.info(f"\n📊 Summary:")
        logger.info(f"  Total Tests: {suite_result['total_cases']}")
        logger.info(f"  Passed: {suite_result['passed_cases']}")
        logger.info(f"  Failed: {suite_result['failed_cases']}")
        logger.info(f"  Pass Rate: {suite_result['passed_cases'] / suite_result['total_cases'] * 100:.1f}%")

        # Update session with test results
        await session_mgr.update_session(session_id, {
            "test_results": suite_result,
            "analysis": analysis
        })

        logger.info("✓ Session updated with results")
        logger.info("\n=== Complete Workflow Finished Successfully ===\n")

    finally:
        # Cleanup
        if 'doc_path' in locals():
            Path(doc_path).unlink(missing_ok=True)


# ==================== Example 2: Document Indexing ====================

async def example_document_indexing():
    """
    Example 2: Document indexing workflow

    Demonstrates uploading and indexing multiple documents in various formats.
    """
    logger.info("=== Example 2: Document Indexing ===")

    try:
        # Initialize MCP client
        mcp_client = await create_mcp_client()

        # Create sample documents
        documents = [
            {
                "name": "OpenAPI Spec",
                "content": json.dumps({"openapi": "3.0.0", "info": {"title": "API 1"}}),
                "type": "openapi"
            },
            {
                "name": "Swagger YAML",
                "content": "swagger: '2.0'\ninfo:\n  title: 'API 2'",
                "type": "swagger"
            },
            {
                "name": "GraphQL Schema",
                "content": "type Query { user: User! }",
                "type": "graphql"
            },
            {
                "name": "Markdown Docs",
                "content": "# API Docs\n\n## Authentication",
                "type": "markdown"
            }
        ]

        # Write documents to temporary files
        temp_dir = Path("temp_docs")
        temp_dir.mkdir(exist_ok=True)

        doc_paths = []
        for i, doc in enumerate(documents, 1):
            path = temp_dir / f"doc{i}.{doc['type']}"
            path.write_text(doc["content"])
            doc_paths.append(str(path))
            logger.info(f"✓ Created {doc['name']}")

        # Index all documents
        logger.info(f"Indexing {len(doc_paths)} documents...")
        index_results = await index_uploaded_files(doc_paths, mcp_client=mcp_client)

        success_count = sum(1 for r in index_results if r["status"] == "success")
        logger.info(f"✓ Indexed {success_count}/{len(doc_paths)} documents")

        # Query RAG to verify
        rag_agent = create_subagent("rag-retrieval", mcp_client)
        query_result = await rag_agent.execute({
            "query": "authentication endpoint",
            "mode": "mix",
            "top_k": 10
        })

        if query_result["status"] == "success":
            entities = query_result.get("entities", [])
            logger.info(f"✓ RAG query returned {len(entities)} entities")

        logger.info("\n=== Document Indexing Finished ===\n")

    finally:
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


# ==================== Example 3: Test Code Generation ====================

async def example_test_generation():
    """
    Example 3: Test code generation

    Demonstrates generating test code in different formats.
    """
    logger.info("=== Example 3: Test Code Generation ===")

    try:
        # Initialize MCP client
        mcp_client = await create_mcp_client()

        # Sample test plan
        test_plan = {
            "testCases": [
                {
                    "case_id": "TC001",
                    "name": "Login with valid credentials",
                    "test_type": "functional",
                    "steps": [{
                        "step_id": "step_001",
                        "endpoint": "/api/v1/auth/login",
                        "method": "POST",
                        "request_body": {
                            "username": "testuser",
                            "password": "Valid@123"
                        },
                        "assertions": [
                            {"assertion_type": "status_code", "expected": 200}
                        ]
                    }]
                },
                {
                    "case_id": "TC002",
                    "name": "Login with invalid credentials",
                    "test_type": "security",
                    "steps": [{
                        "step_id": "step_002",
                        "endpoint": "/api/v1/auth/login",
                        "method": "POST",
                        "request_body": {
                            "username": "testuser",
                            "password": "Wrong@123"
                        },
                        "assertions": [
                            {"assertion_type": "status_code", "expected": 401}
                        ]
                    }]
                }
            ]
        }

        # Generate Playwright tests
        logger.info("Generating Playwright tests...")
        playwright_tests = TestGenerator.generate_playwright_test(
            test_plan.get("testCases", [])[0],
            base_url="http://localhost:8000"
        )

        test_outputs_dir = Path("test_outputs")
        test_outputs_dir.mkdir(exist_ok=True)

        playwright_file = test_outputs_dir / "test_login.spec.ts"
        playwright_file.write_text(playwright_tests)
        logger.info(f"✓ Generated: {playwright_file}")

        # Generate Jest tests
        logger.info("Generating Jest tests...")
        jest_tests = TestGenerator.generate_jest_test(
            test_plan.get("testCases", [])[0],
            base_url="http://localhost:8000"
        )

        jest_file = test_outputs_dir / "test_login.test.js"
        jest_file.write_text(jest_tests)
        logger.info(f"✓ Generated: {jest_file}")

        # Generate Postman collection
        from api_agent.models import TestCase, TestStep

        # Create test case for Postman
        tc = TestCase(
            case_id="TC001",
            name="Login Test",
            description="Test login endpoint",
            priority="high",
            test_type="functional",
            steps=[
                TestStep(
                    step_id="step_001",
                    name="Login",
                    description="POST to login endpoint",
                    endpoint="/api/v1/auth/login",
                    method="POST",
                    request_body={"username": "testuser", "password": "Test@123"}
                )
            ]
        )

        postman_json = TestGenerator.generate_postman_collection(
            test_plan.get("testCases", [])[0]
        )

        postman_file = test_outputs_dir / "postman_collection.json"
        postman_file.write_text(postman_json)
        logger.info(f"✓ Generated: {postman_file}")

        logger.info("\n=== Test Code Generation Finished ===\n")

    except Exception as e:
        logger.error(f"Test code generation failed: {e}")


# ==================== Example 4: Session Management ====================

async def example_session_management():
    """
    Example 4: Session management

    Demonstrates creating, updating, and querying sessions.
    """
    logger.info("=== Example 4: Session Management ===")

    try:
        # Initialize session manager
        mcp_client = await create_mcp_client()
        session_mgr = get_session_manager(mcp_client)

        # Create session
        logger.info("Creating session...")
        session = await session_mgr.create_session(
            name="Test Session",
            description="Session management example",
            user_id="example_user"
        )

        session_id = session["session_id"]
        logger.info(f"✓ Session created: {session_id}")

        # Update session with data
        logger.info("Updating session...")
        updated = await session_mgr.update_session(session_id, {
            "test_data": {"tests_run": 5, "tests_passed": 4},
            "auth_token": "jwt_token_xyz"
        })

        logger.info(f"✓ Session updated: {updated['updated_at']}")

        # Set auth token
        logger.info("Setting auth token...")
        await session_mgr.set_auth_token(session_id, "new_jwt_token_abc")
        logger.info("✓ Auth token set")

        # Get auth token
        logger.info("Getting auth token...")
        token_data = await session_mgr.get_auth_token(session_id)
        logger.info(f"✓ Auth token: {token_data}")

        # List sessions
        logger.info("Listing sessions...")
        sessions = await session_mgr.list_sessions(user_id="example_user")
        logger.info(f"✓ Found {len(sessions)} sessions")

        # Clean up old sessions
        logger.info("Cleaning up old sessions...")
        deleted = await session_mgr.cleanup_old_sessions(days=30)
        logger.info(f"✓ Deleted {deleted} old sessions")

        logger.info("\n=== Session Management Finished ===\n")

    except Exception as e:
        logger.error(f"Session management failed: {e}")


# ==================== Example 5: Error Handling ====================

async def example_error_handling():
    """
    Example 5: Error handling

    Demonstrates graceful error handling and recovery.
    """
    logger.info("=== Example 5: Error Handling ===")

    from core.logging_config import get_error_handler

    error_handler = get_error_handler(logger)

    try:
        # Simulate network error
        logger.info("Simulating network error...")
        class NetworkError(Exception):
            pass

        # This will be handled by error handler with retry logic
        # For demo, we'll just log it
        logger.error("Simulated network error", exc_info=NetworkError("Connection timeout"))

        # Simulate MCP connection error
        logger.info("Simulating MCP connection error...")
        try:
            # Try to call non-existent MCP server
            # mcp_client = await create_mcp_client()
            # await mcp_client.call_tool("nonexistent-server", "tool", {})
            logger.warning("Non-existent MCP server call skipped for demo")
        except Exception as e:
            logger.error(f"MCP connection error: {e}")

        logger.info("✓ Error handling demonstrated")

    except Exception as e:
        logger.error(f"Unexpected error in error handling: {e}")


# ==================== Main Entry Point ====================

async def main():
    """Run all examples"""
    import sys

    examples = {
        "1": ("Complete Workflow", example_complete_workflow),
        "2": ("Document Indexing", example_document_indexing),
        "3": ("Test Code Generation", example_test_generation),
        "4": ("Session Management", example_session_management),
        "5": ("Error Handling", example_error_handling)
    }

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num in examples:
            name, func = examples[example_num]
            logger.info(f"Running Example {example_num}: {name}")
            await func()
        else:
            logger.error(f"Unknown example: {example_num}")
            logger.info(f"Available examples:")
            for num, (name, _) in examples.items():
                logger.info(f"  {num}: {name}")
    else:
        # Run all examples
        for num, (name, func) in examples.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Example {num}: {name}")
            await func()


if __name__ == "__main__":
    asyncio.run(main())
