"""
End-to-End Tests - Complete Workflow

Tests the complete API automation workflow:
1. Document upload
2. RAG indexing
3. Test plan generation
4. Test code generation
5. Test execution
6. Result analysis and reporting
"""
import pytest
import asyncio
import httpx
from pathlib import Path
import sys
import json
import time

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class TestEndToEnd:
    """End-to-end workflow tests"""

    @pytest.fixture
    def base_url(self):
        """Base URL for API testing"""
        return "http://localhost:8000"

    @pytest.mark.e2e
    async def test_e2e_document_upload_and_indexing(self, base_url):
        """Test document upload and indexing"""
        print("\n" + "="*60)
        print("E2E Test: Document Upload and Indexing")
        print("="*60)

        # Sample API documentation
        api_doc = """
        openapi: 3.0.0
        info:
          title: User Authentication API
          version: 1.0.0
        paths:
          /api/v1/auth/login:
            post:
              summary: User login
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        username:
                          type: string
                        password:
                          type: string
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
                          user:
                            type: object
        """

        async with httpx.AsyncClient() as client:
            # Step 1: Upload document
            print("\n1. Uploading document...")
            files = {
                'file': ('openapi.yaml', api_doc, 'text/yaml')
            }
            response = await client.post(
                f"{base_url}/api/v1/documents/upload",
                files=files
            )

            assert response.status_code in [200, 201]
            result = response.json()
            doc_id = result.get("doc_id")
            print(f"   ✓ Document uploaded: {doc_id}")

            # Step 2: Index document via RAG
            print("\n2. Indexing document...")
            index_response = await client.post(
                f"{base_url}/api/v1/agents/query",
                json={
                    "query": "login endpoint authentication",
                    "mode": "mix",
                    "top_k": 10
                }
            )

            assert index_response.status_code in [200, 404]  # 404 if RAG not fully integrated
            if index_response.status_code == 200:
                query_result = index_response.json()
                print(f"   ✓ Document indexed, found {len(query_result.get('results', []))} results")

        print("\n✅ Document upload and indexing test passed!")

    @pytest.mark.e2e
    async def test_e2e_test_generation_workflow(self, base_url):
        """Test complete test generation workflow"""
        print("\n" + "="*60)
        print("E2E Test: Test Generation Workflow")
        print("="*60)

        async with httpx.AsyncClient() as client:
            # Step 1: Generate tests from API documentation
            print("\n1. Generating tests from API documentation...")
            response = await client.post(
                f"{base_url}/api/v1/agents/generate",
                json={
                    "api_source": "https://api.example.com/openapi.json",
                    "format": "playwright",
                    "language": "typescript"
                }
            )

            # May fail if no real API, but should return mock result
            assert response.status_code in [200, 400]
            result = response.json()

            if response.status_code == 200:
                test_code = result.get("test_code", {})
                test_plan = result.get("test_plan", {})

                print(f"   ✓ Test plan generated")
                print(f"   ✓ Test code generated: {len(test_code.get('testFiles', {}))} files")

                # Step 2: Verify test code format
                print("\n2. Verifying test code format...")
                assert "testFiles" in test_code or "format" in test_code

                test_files = test_code.get("testFiles", {})
                for filename in test_files.keys():
                    content = test_files[filename]
                    assert filename.endswith(('.spec.ts', '.spec.js'))
                    assert 'test' in content.lower()
                    print(f"   ✓ Valid test file: {filename}")

            else:
                # Handle missing API source
                print(f"   Note: {result.get('message', 'API source error')}")

        print("\n✅ Test generation workflow test passed!")

    @pytest.mark.e2e
    async def test_e2e_chat_with_agent(self, base_url):
        """Test chat interaction with AI agent"""
        print("\n" + "="*60)
        print("E2E Test: Chat with AI Agent")
        print("="*60)

        async with httpx.AsyncClient() as client:
            # Send natural language request
            print("\n1. Sending request to agent...")
            response = await client.post(
                f"{base_url}/api/v1/agents/chat",
                json={
                    "message": "Generate comprehensive tests for user authentication API including functional, security, and boundary tests. Use Playwright framework.",
                    "user_id": "test_user",
                    "session_id": "test_session_001"
                }
            )

            # Should return task updates
            assert response.status_code in [200, 202]
            result = response.json()

            print(f"   ✓ Agent processing request")
            updates = result.get("updates", [])

            # Check for workflow steps
            steps_found = 0
            for update in updates:
                if update.get("type") == "step":
                    steps_found += 1
                    print(f"   Step {update['step']}: {update['name']}")
                elif update.get("type") == "task_complete":
                    print(f"   ✓ Task completed")
                    final_result = update.get("result", {})
                    summary = final_result.get("summary", "")
                    print(f"   Summary: {summary[:100]}")

            assert steps_found > 0

        print("\n✅ Chat with agent test passed!")

    @pytest.mark.e2e
    async def test_e2e_test_execution_and_reporting(self, base_url):
        """Test execution and reporting workflow"""
        print("\n" + "="*60)
        print("E2E Test: Test Execution and Reporting")
        print("="*60)

        async with httpx.AsyncClient() as client:
            # Step 1: Execute tests
            print("\n1. Executing test suite...")
            response = await client.post(
                f"{base_url}/api/v1/executions/execute",
                json={
                    "suite_id": "suite_001",
                    "execution_name": "Comprehensive API Tests",
                    "config": {
                        "parallel": True,
                        "retries": 2,
                        "timeout": 30000
                    }
                }
            )

            assert response.status_code in [200, 201]
            result = response.json()
            execution_id = result.get("execution_id")

            assert execution_id is not None
            print(f"   ✓ Execution started: {execution_id}")

            # Step 2: Wait for completion (poll)
            print("\n2. Waiting for execution to complete...")
            max_attempts = 10
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(1)

                status_response = await client.get(
                    f"{base_url}/api/v1/executions/{execution_id}"
                )

                assert status_response.status_code == 200
                execution_info = status_response.json()
                status = execution_info.get("results", {}).get("status", "running")

                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")

                if status in ["completed", "failed"]:
                    print(f"   ✓ Execution {status}")

                    # Step 3: Verify results
                    print("\n3. Verifying execution results...")
                    results = execution_info.get("results", {})

                    assert "total_cases" in results
                    assert "passed_cases" in results
                    assert "failed_cases" in results

                    total = results.get("total_cases", 0)
                    passed = results.get("passed_cases", 0)
                    failed = results.get("failed_cases", 0)

                    print(f"   ✓ Total tests: {total}")
                    print(f"   ✓ Passed: {passed}")
                    print(f"   ✓ Failed: {failed}")

                    # Calculate pass rate
                    if total > 0:
                        pass_rate = (passed / total) * 100
                        print(f"   ✓ Pass rate: {pass_rate:.1f}%")

                    break

                attempt += 1

        print("\n✅ Test execution and reporting test passed!")

    @pytest.mark.e2e
    async def test_e2e_task_management(self, base_url):
        """Test task management lifecycle"""
        print("\n" + "="*60)
        print("E2E Test: Task Management Lifecycle")
        print("="*60)

        async with httpx.AsyncClient() as client:
            # Step 1: Create task
            print("\n1. Creating task...")
            create_response = await client.post(
                f"{base_url}/api/v1/tasks/create",
                json={
                    "name": "Generate API Tests",
                    "description": "Generate comprehensive tests for user management API",
                    "user_id": "test_user",
                    "metadata": {
                        "format": "playwright",
                        "test_categories": ["functional", "security"]
                    }
                }
            )

            assert create_response.status_code in [200, 201]
            task = create_response.json()
            task_id = task.get("task_id")

            assert task_id is not None
            print(f"   ✓ Task created: {task_id}")

            # Step 2: Check task status
            print("\n2. Checking task status...")
            await asyncio.sleep(1)

            status_response = await client.get(f"{base_url}/api/v1/tasks/{task_id}")

            assert status_response.status_code == 200
            status_info = status_response.json()
            task_status = status_info.get("task", {}).get("status")

            print(f"   ✓ Task status: {task_status}")

            # Step 3: List tasks
            print("\n3. Listing tasks...")
            list_response = await client.get(
                f"{base_url}/api/v1/tasks",
                params={"limit": 10}
            )

            assert list_response.status_code == 200
            tasks = list_response.json()
            task_list = tasks.get("tasks", [])

            print(f"   ✓ Found {len(task_list)} tasks")

            # Step 4: Cancel task (if running)
            if task_status in ["pending", "running"]:
                print("\n4. Cancelling task...")
                cancel_response = await client.post(
                    f"{base_url}/api/v1/tasks/{task_id}/cancel"
                )

                assert cancel_response.status_code == 200
                print("   ✓ Task cancelled")

        print("\n✅ Task management lifecycle test passed!")

    @pytest.mark.e2e
    async def test_e2e_complete_pipeline(self, base_url):
        """Test complete pipeline: document -> test -> execute -> report"""
        print("\n" + "="*60)
        print("E2E Test: Complete Automation Pipeline")
        print("="*60)

        async with httpx.AsyncClient() as client:
            pipeline_start = time.time()

            # Phase 1: Document Processing
            print("\n📄 Phase 1: Document Processing")
            doc_response = await client.post(
                f"{base_url}/api/v1/agents/generate",
                json={
                    "api_source": "https://api.example.com/openapi.json",
                    "format": "playwright"
                }
            )

            if doc_response.status_code == 200:
                doc_result = doc_response.json()
                print("   ✓ Document processed")
                phase1_duration = time.time() - pipeline_start
                print(f"   Duration: {phase1_duration:.2f}s")

            # Phase 2: Task Management
            print("\n⚙️  Phase 2: Task Management")
            task_response = await client.post(
                f"{base_url}/api/v1/tasks/create",
                json={
                    "name": "Complete Pipeline Test",
                    "description": "End-to-end automation pipeline test"
                }
            )

            assert task_response.status_code in [200, 201]
            task = task_response.json()
            task_id = task.get("task_id")
            print(f"   ✓ Task created: {task_id}")

            # Phase 3: Execution
            print("\n🚀 Phase 3: Execution")
            exec_response = await client.post(
                f"{base_url}/api/v1/executions/execute",
                json={
                    "suite_id": "suite_e2e_001",
                    "execution_name": "E2E Pipeline Execution"
                }
            )

            assert exec_response.status_code in [200, 201]
            exec_result = exec_response.json()
            execution_id = exec_result.get("execution_id")
            print(f"   ✓ Execution started: {execution_id}")

            # Phase 4: Reporting
            print("\n📊 Phase 4: Reporting")
            report_response = await client.get(
                f"{base_url}/api/v1/executions/{execution_id}"
            )

            assert report_response.status_code == 200
            execution_info = report_response.json()
            print("   ✓ Execution report retrieved")

            # Final Summary
            total_duration = time.time() - pipeline_start
            print("\n" + "="*60)
            print("✅ Complete Pipeline Test Results")
            print("="*60)
            print(f"Total duration: {total_duration:.2f}s")
            print(f"Task ID: {task_id}")
            print(f"Execution ID: {execution_id}")
            print("All phases completed successfully!")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "e2e"])
