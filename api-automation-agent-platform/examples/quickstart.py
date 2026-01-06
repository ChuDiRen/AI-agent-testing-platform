"""
Quick Start Example

This example demonstrates how to use the API Automation Agent Platform.
"""
import asyncio
import httpx


async def main():
    """Main example function"""

    base_url = "http://localhost:8000"

    print("=" * 60)
    print("API Automation Agent Platform - Quick Start")
    print("=" * 60)

    # Example 1: Generate tests from API documentation
    print("\n1. Generate tests from API documentation")
    print("-" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/v1/agents/generate",
            json={
                "api_source": "https://api.example.com/openapi.json",
                "format": "playwright"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ Test generation initiated")
            print(f"  Task ID: {result.get('task_id')}")

        # Example 2: Chat with the AI agent
        print("\n2. Chat with AI agent")
        print("-" * 60)

        response = await client.post(
            f"{base_url}/api/v1/agents/chat",
            json={
                "message": "Generate tests for the user authentication API",
                "user_id": "user_123"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ Agent processing request")
            updates = result.get("updates", [])
            for update in updates:
                if update.get("type") == "step":
                    print(f"  Step {update['step']}: {update['name']}")
                elif update.get("type") == "task_complete":
                    print(f"  ✓ Task completed!")

        # Example 3: Query knowledge base
        print("\n3. Query knowledge base")
        print("-" * 60)

        response = await client.post(
            f"{base_url}/api/v1/agents/query",
            json={
                "query": "Find authentication endpoints",
                "mode": "mix"
            }
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ Knowledge base queried")
            print(f"  Found {len(result.get('results', []))} results")

        # Example 4: Execute tests
        print("\n4. Execute test suite")
        print("-" * 60)

        response = await client.post(
            f"{base_url}/api/v1/executions/execute",
            json={
                "suite_id": "suite_001",
                "execution_name": "Daily smoke tests",
                "config": {
                    "parallel": True,
                    "retries": 2
                }
            }
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ Test execution initiated")
            print(f"  Execution ID: {result.get('execution_id')}")

        # Example 5: Check task status
        print("\n5. Check task status")
        print("-" * 60)

        task_id = result.get("task_id", "example_task_id")

        response = await client.get(f"{base_url}/api/v1/tasks/{task_id}")

        if response.status_code == 200:
            task_info = response.json()
            print(f"✓ Task status: {task_info['task']['status']}")
            print(f"  Created: {task_info['task']['created_at']}")

    print("\n" + "=" * 60)
    print("Quick Start Complete!")
    print("=" * 60)


# Example: Direct Python API usage
async def direct_api_example():
    """Example using Python API directly"""

    from agents.orchestrator import create_orchestrator

    print("\n" + "=" * 60)
    print("Direct Python API Example")
    print("=" * 60)

    # Create orchestrator
    orchestrator = await create_orchestrator()

    # Process request
    user_request = """
    Analyze the API at https://api.example.com/openapi.json
    and generate a complete test suite using Playwright.
    Include functional, security, and boundary tests.
    """

    print(f"\nProcessing request: {user_request[:80]}...")

    async for update in orchestrator.process_request(
        user_request=user_request,
        user_id="user_123"
    ):
        if update["type"] == "step":
            print(f"  Step {update['step']}: {update['name']}")
        elif update["type"] == "step_complete":
            step_data = update.get("requirements") or update.get("execution_plan") or update.get("result")
            print(f"    ✓ Complete")
        elif update["type"] == "task_complete":
            print(f"\n✓ Task completed successfully!")
            result = update.get("result", {})
            summary = result.get("summary", "No summary available")
            print(f"\nSummary:\n{summary}")

    print("\n" + "=" * 60)


# Example: Using individual tools
async def tool_usage_example():
    """Example using individual tools"""

    from agents.subagents import (
        RAGRetrievalAgent,
        PlannerAgent,
        GeneratorAgent,
        ExecutorAgent,
        AnalyzerAgent
    )

    print("\n" + "=" * 60)
    print("Individual Tools Example")
    print("=" * 60)

    # Step 1: Retrieve API information
    print("\n1. Retrieving API documentation...")
    rag_agent = RAGRetrievalAgent()
    api_info = await rag_agent.execute({
        "query": "Find user authentication APIs",
        "mode": "mix"
    })
    print(f"   Found {len(api_info.get('entities', []))} API endpoints")

    # Step 2: Generate test plan
    print("\n2. Generating test plan...")
    planner_agent = PlannerAgent()
    test_plan = await planner_agent.execute({
        "api_info": api_info,
        "test_categories": ["functional", "security"]
    })
    plan_data = test_plan.get("testPlan", {})
    print(f"   Generated {len(plan_data.get('testCases', []))} test cases")

    # Step 3: Generate test code
    print("\n3. Generating test code...")
    generator_agent = GeneratorAgent()
    test_code = await generator_agent.execute({
        "test_plan": plan_data,
        "format": "playwright",
        "language": "typescript"
    })
    files = test_code.get("testFiles", {})
    print(f"   Generated {len(files)} test files:")
    for filename in files.keys():
        print(f"     - {filename}")

    # Step 4: Execute tests
    print("\n4. Executing tests...")
    executor_agent = ExecutorAgent()
    execution_results = await executor_agent.execute({
        "test_files": list(files.keys())
    })
    results = execution_results.get("results", {})
    print(f"   Total: {results.get('total_cases', 0)}")
    print(f"   Passed: {results.get('passed_cases', 0)} ✓")
    print(f"   Failed: {results.get('failed_cases', 0)} ✗")

    # Step 5: Analyze results
    print("\n5. Analyzing results...")
    analyzer_agent = AnalyzerAgent()
    analysis = await analyzer_agent.execute({
        "test_results": results,
        "include_charts": True
    })
    summary = analysis.get("summary", {})
    print(f"   Pass rate: {summary.get('pass_rate', 'N/A')}")
    recommendations = analysis.get("recommendations", [])
    print(f"   Recommendations:")
    for rec in recommendations:
        print(f"     - {rec}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run all examples
    print("\n\n")
    asyncio.run(main())
    asyncio.run(direct_api_example())
    asyncio.run(tool_usage_example())
