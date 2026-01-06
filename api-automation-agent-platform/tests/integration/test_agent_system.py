"""
Agent System - Integration Tests

Tests for the complete agent system including:
- Orchestrator
- Sub-agents (RAG, Planner, Generator, Executor, Analyzer)
- MCP Server integration
"""
import pytest
import asyncio
from pathlib import Path
import sys
import json

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class TestAgentSystem:
    """Integration tests for agent system"""

    @pytest.fixture
    async def mock_mcp_client(self, mocker):
        """Create a mock MCP client"""
        class MockMCPClient:
            async def call_tool(self, tool_name, arguments):
                # Mock responses for different tools
                if tool_name == "rag_query_data":
                    return json.dumps({
                        "status": "success",
                        "entities": [
                            {
                                "name": "POST /api/v1/auth/login",
                                "entity_type": "API_ENDPOINT",
                                "description": "User authentication"
                            }
                        ],
                        "chunks": [
                            {
                                "content": "Login endpoint requires username and password",
                                "score": 0.95
                            }
                        ]
                    })
                elif tool_name == "api_planner":
                    return json.dumps({
                        "status": "success",
                        "testPlan": {
                            "title": "API Test Plan",
                            "testCases": [
                                {
                                    "case_id": "TC001",
                                    "name": "Test user login",
                                    "test_type": "functional",
                                    "steps": [{
                                        "step_id": "step_001",
                                        "method": "POST",
                                        "endpoint": "/api/v1/auth/login",
                                        "assertions": [
                                            {"type": "status_code", "expected": 200}
                                        ]
                                    }]
                                }
                            ]
                        }
                    })
                elif tool_name == "api_generator":
                    return json.dumps({
                        "status": "success",
                        "testFiles": {
                            "test_login.spec.ts": """
import { test, expect } from '@playwright/test';

test.describe('User Login API', () => {
  test('should login successfully', async ({ request }) => {
    const response = await request.post('/api/v1/auth/login', {
      data: {
        username: 'testuser',
        password: 'Test@123'
      }
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty('token');
  });
});
"""
                        }
                    })
                elif tool_name == "chart_generate":
                    return json.dumps({
                        "status": "success",
                        "chartType": "pie",
                        "spec": {
                            "type": "pie",
                            "data": [
                                {"status": "passed", "count": 4},
                                {"status": "failed", "count": 1}
                            ]
                        }
                    })
                else:
                    return json.dumps({"status": "success", "result": {}})

        return MockMCPClient()

    @pytest.mark.asyncio
    async def test_rag_retrieval_agent(self, mock_mcp_client):
        """Test RAG Retrieval Agent"""
        from agents.subagents import RAGRetrievalAgent

        agent = RAGRetrievalAgent(mcp_client=mock_mcp_client)

        result = await agent.execute({
            "query": "find authentication endpoints",
            "mode": "mix",
            "top_k": 10
        })

        assert result is not None
        assert "status" in result or "entities" in result
        print("✓ RAG Retrieval Agent executed successfully")
        print(f"  Retrieved entities: {len(result.get('entities', []))}")

    @pytest.mark.asyncio
    async def test_planner_agent(self, mock_mcp_client):
        """Test Planner Agent"""
        from agents.subagents import PlannerAgent

        agent = PlannerAgent(mcp_client=mock_mcp_client)

        result = await agent.execute({
            "api_info": {"url": "https://api.example.com/openapi.json"},
            "test_categories": ["functional", "security"]
        })

        assert result is not None
        assert "testPlan" in result or "status" in result
        test_plan = result.get("testPlan", {})
        assert "testCases" in test_plan
        print("✓ Planner Agent executed successfully")
        print(f"  Generated {len(test_plan.get('testCases', []))} test cases")

    @pytest.mark.asyncio
    async def test_generator_agent(self, mock_mcp_client):
        """Test Generator Agent"""
        from agents.subagents import GeneratorAgent

        agent = GeneratorAgent(mcp_client=mock_mcp_client)

        test_plan = {
            "title": "Test Plan",
            "testCases": [
                {
                    "case_id": "TC001",
                    "name": "Test login",
                    "steps": [{
                        "step_id": "step_001",
                        "method": "POST",
                        "endpoint": "/api/v1/auth/login"
                    }]
                }
            ]
        }

        result = await agent.execute({
            "test_plan": test_plan,
            "format": "playwright",
            "language": "typescript"
        })

        assert result is not None
        assert "testFiles" in result or "format" in result
        test_files = result.get("testFiles", {})
        assert len(test_files) > 0
        print("✓ Generator Agent executed successfully")
        print(f"  Generated {len(test_files)} test files")

    @pytest.mark.asyncio
    async def test_executor_agent(self, mock_mcp_client):
        """Test Executor Agent"""
        from agents.subagents import ExecutorAgent

        agent = ExecutorAgent(mcp_client=mock_mcp_client)

        result = await agent.execute({
            "test_files": ["test_login.spec.ts"],
            "config": {"parallel": True}
        })

        assert result is not None
        assert "results" in result or "execution_id" in result
        execution_results = result.get("results", {})
        assert "total_cases" in execution_results
        print("✓ Executor Agent executed successfully")
        print(f"  Executed {execution_results.get('total_cases', 0)} test cases")

    @pytest.mark.asyncio
    async def test_analyzer_agent(self, mock_mcp_client):
        """Test Analyzer Agent"""
        from agents.subagents import AnalyzerAgent

        agent = AnalyzerAgent(mcp_client=mock_mcp_client)

        test_results = {
            "suite_id": "suite_001",
            "status": "completed",
            "total_cases": 5,
            "passed_cases": 4,
            "failed_cases": 1,
            "skipped_cases": 0,
            "duration_ms": 2500.50,
            "case_results": [
                {"case_id": "TC001", "status": "passed", "duration_ms": 120.5},
                {"case_id": "TC002", "status": "passed", "duration_ms": 95.2},
                {"case_id": "TC003", "status": "failed", "duration_ms": 85.0}
            ]
        }

        result = await agent.execute({
            "test_results": test_results,
            "include_charts": True,
            "format": "markdown"
        })

        assert result is not None
        assert "summary" in result or "status" in result
        summary = result.get("summary", {})
        assert "total_tests" in summary or "passed" in summary
        print("✓ Analyzer Agent executed successfully")
        pass_rate = summary.get("pass_rate", "N/A")
        print(f"  Pass rate: {pass_rate}")

    @pytest.mark.asyncio
    async def test_agent_factory(self):
        """Test agent factory function"""
        from agents.subagents import create_subagent

        # Test creating each agent type
        agent_types = ["rag-retrieval", "planner", "generator", "executor", "analyzer"]

        for agent_type in agent_types:
            agent = create_subagent(agent_type)
            assert agent is not None
            assert agent.name == agent_type

        print(f"✓ Agent factory created all {len(agent_types)} agent types")

    @pytest.mark.asyncio
    async def test_orchestrator_with_subagents(self, mock_mcp_client):
        """Test Orchestrator with sub-agent coordination"""
        from agents.orchestrator import OrchestratorAgent

        orchestrator = OrchestratorAgent()

        # Register sub-agents
        from agents.subagents import (
            RAGRetrievalAgent, PlannerAgent,
            GeneratorAgent, ExecutorAgent, AnalyzerAgent
        )

        orchestrator.register_subagent("rag-retrieval", RAGRetrievalAgent(mock_mcp_client))
        orchestrator.register_subagent("planner", PlannerAgent(mock_mcp_client))
        orchestrator.register_subagent("generator", GeneratorAgent(mock_mcp_client))
        orchestrator.register_subagent("executor", ExecutorAgent(mock_mcp_client))
        orchestrator.register_subagent("analyzer", AnalyzerAgent(mock_mcp_client))

        # Test requirement understanding
        requirements = await orchestrator._understand_requirements(
            "Generate tests for user authentication API using Playwright"
        )

        assert requirements is not None
        assert requirements.get("task_type") == "generate_tests"
        print("✓ Orchestrator understood requirements")
        print(f"  Task type: {requirements.get('task_type')}")

        # Test execution planning
        execution_plan = await orchestrator._plan_execution(requirements)

        assert execution_plan is not None
        assert "subtasks" in execution_plan
        assert len(execution_plan["subtasks"]) > 0
        print("✓ Orchestrator created execution plan")
        print(f"  Subtasks: {len(execution_plan['subtasks'])}")

    @pytest.mark.asyncio
    async def test_complete_workflow_simulation(self, mock_mcp_client):
        """Simulate complete workflow through all agents"""
        from agents.subagents import (
            RAGRetrievalAgent, PlannerAgent, GeneratorAgent, ExecutorAgent, AnalyzerAgent
        )

        print("\n🔄 Simulating complete workflow...")

        # Step 1: RAG Retrieval
        print("\n1. RAG Retrieval")
        rag_agent = RAGRetrievalAgent(mock_mcp_client)
        api_info = await rag_agent.execute({"query": "user authentication", "mode": "mix"})
        print(f"   ✓ Retrieved API info")

        # Step 2: Planning
        print("\n2. Test Planning")
        planner = PlannerAgent(mock_mcp_client)
        test_plan = await planner.execute({"api_info": api_info})
        print(f"   ✓ Generated test plan with {len(test_plan.get('testPlan', {}).get('testCases', []))} cases")

        # Step 3: Code Generation
        print("\n3. Code Generation")
        generator = GeneratorAgent(mock_mcp_client)
        test_code = await generator.execute({
            "test_plan": test_plan.get("testPlan"),
            "format": "playwright"
        })
        print(f"   ✓ Generated {len(test_code.get('testFiles', {}))} test files")

        # Step 4: Execution
        print("\n4. Test Execution")
        executor = ExecutorAgent(mock_mcp_client)
        execution_results = await executor.execute({
            "test_files": list(test_code.get("testFiles", {}).keys())
        })
        print(f"   ✓ Executed tests: {execution_results.get('results', {}).get('total_cases', 0)} total")

        # Step 5: Analysis
        print("\n5. Result Analysis")
        analyzer = AnalyzerAgent(mock_mcp_client)
        analysis = await analyzer.execute({
            "test_results": execution_results.get("results"),
            "include_charts": True
        })
        print(f"   ✓ Analysis complete: pass rate {analysis.get('summary', {}).get('pass_rate', 'N/A')}")

        print("\n✅ Complete workflow simulation successful!")

    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling"""
        from agents.subagents import PlannerAgent

        # Create agent without MCP client (should use mock)
        agent = PlannerAgent(mcp_client=None)

        # Should not crash even without real MCP client
        result = await agent.execute({
            "api_info": {}
        })

        assert result is not None
        # Should return mock data
        assert "testPlan" in result or "status" in result
        print("✓ Agent handles missing MCP client gracefully")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
