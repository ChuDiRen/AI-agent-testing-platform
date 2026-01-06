"""
Sub-Agents Implementation (Updated with Real MCP Integration)

All sub-agents for API automation platform:
- RAG Retrieval Agent
- Planner Agent
- Generator Agent
- Executor Agent
- Analyzer Agent
"""
from typing import Any, Dict, Optional
import json
import logging

from core.mcp_client import MCPClientWrapper
from core.test_executor import execute_tests
from core.document_indexer import index_uploaded_files
from api_agent.models import (
    TestCase, TestStep, SuiteResult
)

logger = logging.getLogger(__name__)


class RAGRetrievalAgent:
    """RAG Retrieval Agent - Retrieve API information from knowledge base"""

    def __init__(self, mcp_client: Optional[MCPClientWrapper] = None):
        """Initialize RAG retrieval agent"""
        self.mcp_client = mcp_client
        self.name = "rag-retrieval"
        self.description = "Retrieve API documentation and information from knowledge base"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG retrieval"""
        query = input_data.get("query", input_data.get("api_source", ""))
        mode = input_data.get("mode", "mix")
        top_k = input_data.get("top_k", 10)

        logger.info(f"RAG Retrieval Agent executing: query='{query}', mode={mode}")

        # Call RAG MCP Server
        if self.mcp_client:
            try:
                result = await self.mcp_client.call_tool(
                    "rag-server",
                    "rag_query_data",
                    {
                        "query": query,
                        "mode": mode,
                        "top_k": top_k
                    }
                )
                return json.loads(result)
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "entities": [],
                    "relationships": [],
                    "chunks": []
                }
        else:
            logger.warning("No MCP client available, returning mock response")
            # Mock response for testing without MCP
            return {
                "status": "success",
                "entities": [
                    {
                        "name": "User Login API",
                        "type": "API_ENDPOINT",
                        "description": "POST /api/v1/auth/login - User authentication"
                    }
                ],
                "relationships": [],
                "chunks": [
                    {
                        "content": "Login endpoint requires username and password",
                        "source": "api-docs"
                    }
                ]
            }


class PlannerAgent:
    """Planner Agent - Generate test plans from API documentation"""

    def __init__(self, mcp_client: Optional[MCPClientWrapper] = None):
        """Initialize planner agent"""
        self.mcp_client = mcp_client
        self.name = "planner"
        self.description = "Generate detailed test plans from API documentation"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test planning"""
        api_info = input_data.get("api_info", {})
        test_categories = input_data.get("test_categories", ["functional", "security"])

        logger.info(f"Planner Agent executing: {api_info.get('name', 'unknown')}")

        # Call API Planner tool
        if self.mcp_client:
            try:
                result = await self.mcp_client.call_tool(
                    "automation-quality",
                    "api_planner",
                    {
                        "schemaUrl": api_info.get("url"),
                        "schemaPath": api_info.get("path"),
                        "schemaType": api_info.get("type", "auto"),
                        "testCategories": test_categories
                    }
                )
                return json.loads(result)
            except Exception as e:
                logger.error(f"Test planning failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "testPlan": {"testCases": []}
                }
        else:
            logger.warning("No MCP client available, returning mock response")
            # Mock response
            return {
                "status": "success",
                "testPlan": {
                    "title": "API Test Plan",
                    "testCases": [
                        {
                            "case_id": "TC001",
                            "name": "Test user login",
                            "test_type": "functional",
                            "priority": "high",
                            "description": "Test normal login flow",
                            "steps": [{
                                "step_id": "step_001",
                                "name": "Send login request",
                                "endpoint": "/api/v1/auth/login",
                                "method": "POST",
                                "request_body": {
                                    "username": "testuser",
                                    "password": "Test@123"
                                },
                                "assertions": [
                                    {"type": "status_code", "expected": 200}
                                ]
                            }]
                        }
                    ]
                }
            }


class GeneratorAgent:
    """Generator Agent - Generate test code from test plans"""

    def __init__(self, mcp_client: Optional[MCPClientWrapper] = None):
        """Initialize generator agent"""
        self.mcp_client = mcp_client
        self.name = "generator"
        self.description = "Generate executable test code from test plans"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test code generation"""
        test_plan = input_data.get("test_plan", {})
        output_format = input_data.get("format", "playwright")
        language = input_data.get("language", "typescript")
        base_url = input_data.get("base_url", "http://localhost:8000")

        logger.info(f"Generator Agent executing: format={output_format}, language={language}")

        # Call API Generator tool
        if self.mcp_client:
            try:
                result = await self.mcp_client.call_tool(
                    "automation-quality",
                    "api_generator",
                    {
                        "testPlan": json.dumps(test_plan),
                        "outputFormat": output_format,
                        "language": language,
                        "testFramework": "playwright-test",
                        "baseUrl": base_url
                    }
                )
                return json.loads(result)
            except Exception as e:
                logger.error(f"Test code generation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "format": output_format,
                    "testFiles": {}
                }
        else:
            logger.warning("No MCP client available, generating mock test code")
            # Generate mock test code
            from core.test_executor import TestGenerator

            # Create a mock test case
            mock_case = TestCase(
                case_id="TC001",
                name="Test User Login",
                description="Test login functionality",
                priority="high",
                test_type="functional",
                steps=[
                    TestStep(
                        step_id="step_001",
                        name="Send login request",
                        description="POST login endpoint with credentials",
                        endpoint="/api/v1/auth/login",
                        method="POST",
                        request_body={"username": "testuser", "password": "Test@123"},
                        assertions=[
                            {"assertion_id": "assert_001", "assertion_type": "status_code", "target": "status", "expected": 200}
                        ]
                    )
                ]
            )

            # Generate code using TestGenerator
            code = TestGenerator.generate_playwright_test(mock_case, base_url)

            return {
                "status": "success",
                "format": output_format,
                "language": language,
                "testFiles": {
                    "test_login.spec.ts": code
                }
            }


class ExecutorAgent:
    """Executor Agent - Execute test suites using real test runners"""

    def __init__(self, mcp_client: Optional[MCPClientWrapper] = None):
        """Initialize executor agent"""
        self.mcp_client = mcp_client
        self.name = "executor"
        self.description = "Execute test suites and collect results"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test suite"""
        test_files = input_data.get("test_files", [])
        config = input_data.get("config", {})
        framework = config.get("framework", "playwright")
        base_url = config.get("base_url", "http://localhost:8000")

        logger.info(f"Executor Agent executing: {len(test_files)} files, framework={framework}")

        if not test_files:
            return {
                "status": "error",
                "error": "No test files provided",
                "results": None
            }

        try:
            # Execute tests using real test runner
            suite_result = await execute_tests(
                framework=framework,
                test_files=test_files,
                base_url=base_url
            )

            # Convert SuiteResult to dict
            return {
                "status": "success",
                "execution_id": suite_result.suite_id,
                "results": suite_result.dict()
            }

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": None
            }


class AnalyzerAgent:
    """Analyzer Agent - Analyze test results and generate reports"""

    def __init__(self, mcp_client: Optional[MCPClientWrapper] = None):
        """Initialize analyzer agent"""
        self.mcp_client = mcp_client
        self.name = "analyzer"
        self.description = "Analyze test results and generate comprehensive reports"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results"""
        test_results = input_data.get("test_results", {})
        include_charts = input_data.get("include_charts", True)
        report_format = input_data.get("format", "markdown")

        logger.info(f"Analyzer Agent executing: format={report_format}")

        try:
            # Generate charts if MCP client is available
            charts_data = None
            if self.mcp_client and include_charts:
                try:
                    # Prepare chart data
                    chart_data = [
                        {"status": "passed", "count": test_results.get("passed_cases", 0)},
                        {"status": "failed", "count": test_results.get("failed_cases", 0)},
                        {"status": "skipped", "count": test_results.get("skipped_cases", 0)}
                    ]

                    chart_result = await self.mcp_client.call_tool(
                        "chart-server",
                        "chart_generate",
                        {
                            "chartType": "pie",
                            "data": chart_data,
                            "config": {
                                "title": "Test Results Distribution",
                                "angleField": "count",
                                "colorField": "status"
                            }
                        }
                    )
                    charts_data = json.loads(chart_result)
                except Exception as e:
                    logger.warning(f"Chart generation failed: {e}")

            # Generate analysis
            total = test_results.get("total_cases", 0)
            passed = test_results.get("passed_cases", 0)
            pass_rate = (passed / total * 100) if total > 0 else 0

            analysis = {
                "status": "success",
                "summary": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": test_results.get("failed_cases", 0),
                    "skipped": test_results.get("skipped_cases", 0),
                    "pass_rate": f"{pass_rate:.1f}%"
                },
                "recommendations": self._generate_recommendations(test_results),
                "charts": charts_data
            }

            # Generate report
            if self.mcp_client:
                try:
                    report_result = await self.mcp_client.call_tool(
                        "automation-quality",
                        "report_generate",
                        {
                            "testResults": test_results,
                            "format": report_format,
                            "includeCharts": include_charts
                        }
                    )
                    report_data = json.loads(report_result)
                    analysis["report"] = report_data.get("report", "")
                except Exception as e:
                    logger.warning(f"Report generation failed: {e}")
                    analysis["report"] = self._generate_text_report(test_results)
            else:
                analysis["report"] = self._generate_text_report(test_results)

            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "summary": None
            }

    def _generate_recommendations(self, results: Dict[str, Any]) -> list:
        """Generate recommendations based on test results"""
        recommendations = []

        failed_cases = results.get("failed_cases", 0)
        if failed_cases > 0:
            recommendations.append(
                f"Review and fix {failed_cases} failed test case(s)"
            )

        total_cases = results.get("total_cases", 0)
        if total_cases > 0:
            pass_rate = (results.get("passed_cases", 0) / total_cases) * 100
            if pass_rate < 80:
                recommendations.append(
                    "Pass rate is below 80%. Consider reviewing test quality and API stability."
                )
            elif pass_rate >= 95:
                recommendations.append(
                    "Excellent pass rate! Consider adding more edge case tests."
                )

        avg_duration = results.get("duration_ms", 0) / max(total_cases, 1)
        if avg_duration > 1000:
            recommendations.append(
                "Average test execution time is high. Consider optimizing test suite."
            )

        return recommendations

    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Generate simple text report"""
        total = results.get("total_cases", 0)
        passed = results.get("passed_cases", 0)
        failed = results.get("failed_cases", 0)
        skipped = results.get("skipped_cases", 0)
        duration = results.get("duration_ms", 0) / 1000

        report = f"""# Test Execution Report

## Summary
- Total Tests: {total}
- Passed: {passed} ✅
- Failed: {failed} ❌
- Skipped: {skipped} ⏭️
- Duration: {duration:.2f}s
- Pass Rate: {(passed / total * 100) if total > 0 else 0:.1f}%

## Recommendations
"""
        for rec in self._generate_recommendations(results):
            report += f"- {rec}\n"

        return report


# Factory function
def create_subagent(
    agent_type: str,
    mcp_client: Optional[MCPClientWrapper] = None
) -> Any:
    """
    Create a sub-agent instance

    Args:
        agent_type: Type of sub-agent
        mcp_client: Optional MCP client

    Returns:
        Sub-agent instance
    """
    agents = {
        "rag-retrieval": RAGRetrievalAgent,
        "planner": PlannerAgent,
        "generator": GeneratorAgent,
        "executor": ExecutorAgent,
        "analyzer": AnalyzerAgent
    }

    agent_class = agents.get(agent_type)

    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agent_class(mcp_client=mcp_client)
