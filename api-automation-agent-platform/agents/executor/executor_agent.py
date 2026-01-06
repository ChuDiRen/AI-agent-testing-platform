"""
Executor Agent - Test Execution

The Executor Agent is responsible for:
1. Executing generated test files
2. Supporting multiple test frameworks (Playwright, Jest, Postman)
3. Collecting test results and performance data
4. Managing test sessions and state
5. Handling errors and retries
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid
import asyncio
import subprocess
import tempfile
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from langchain_openai import ChatOpenAI


@dataclass
class TestResult:
    """Test result data structure"""
    case_id: str
    name: str
    status: str  # passed, failed, skipped
    duration_ms: float
    error_message: Optional[str] = None
    assertions: List[Dict[str, Any]] = None
    performance_data: Dict[str, Any] = None


@dataclass
class SuiteResult:
    """Test suite result data structure"""
    suite_id: str
    suite_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    duration_ms: float
    case_results: List[TestResult]
    start_time: str
    end_time: str


class ExecutorAgent:
    """
    Test Execution Agent
    
    Executes test files and collects results across multiple frameworks.
    """

    def __init__(self, llm: Optional[Any] = None, mcp_client: Optional[Any] = None):
        """
        Initialize executor agent
        
        Args:
            llm: Optional LLM instance
            mcp_client: Optional MCP client for API Request tool
        """
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1
        )
        self.mcp_client = mcp_client
        self.name = "executor"
        self.description = "Execute test files and collect results"

        # Execution environment
        self.temp_dir = tempfile.mkdtemp(prefix="api_test_execution_")
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test files
        
        Args:
            input_data: Dictionary containing:
                - test_files: List of generated test files
                - framework: Test framework to use
                - execution_options: Additional execution options
        
        Returns:
            Dictionary containing execution results and metadata
        """
        try:
            # Extract input parameters
            test_files = input_data.get("test_files", [])
            framework = input_data.get("framework", "playwright")
            execution_options = input_data.get("execution_options", {})
            
            # Create execution session
            session_id = str(uuid.uuid4())
            session = await self._create_execution_session(session_id, test_files, framework, execution_options)
            
            # Execute tests
            if self.mcp_client and framework in ["playwright", "jest"]:
                # Use MCP API Request tool for direct API testing
                results = await self._execute_with_mcp(session)
            else:
                # Use framework-specific execution
                results = await self._execute_with_framework(session)
            
            # Clean up session
            await self._cleanup_session(session_id)
            
            return {
                "status": "success",
                "execution_results": results,
                "metadata": {
                    "session_id": session_id,
                    "framework": framework,
                    "executed_at": datetime.utcnow().isoformat(),
                    "total_files": len(test_files),
                    "execution_time": results.get("duration_ms", 0)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "execution_results": None
            }

    async def _create_execution_session(self, session_id: str, test_files: List[Dict[str, Any]], framework: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create an execution session"""
        # Create session directory
        session_dir = Path(self.temp_dir) / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Write test files to session directory
        written_files = []
        for file_info in test_files:
            file_name = file_info.get("name")
            file_content = file_info.get("content")
            
            if file_name and file_content:
                file_path = session_dir / file_name
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                written_files.append(str(file_path))
        
        # Create session record
        session = {
            "session_id": session_id,
            "session_dir": str(session_dir),
            "framework": framework,
            "test_files": written_files,
            "options": options,
            "start_time": datetime.utcnow().isoformat(),
            "status": "created"
        }
        
        self.active_sessions[session_id] = session
        return session

    async def _execute_with_mcp(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests using MCP API Request tool"""
        session_id = session["session_id"]
        framework = session["framework"]
        
        try:
            # Parse test files to extract API requests
            api_requests = await self._parse_api_requests(session)
            
            # Execute API requests through MCP
            test_results = []
            total_duration = 0
            
            for request_info in api_requests:
                start_time = datetime.utcnow()
                
                # Call API Request MCP tool
                result = await self.mcp_client.call_tool(
                    "api_request",
                    {
                        "method": request_info.get("method", "GET"),
                        "url": request_info.get("url", ""),
                        "headers": request_info.get("headers", {}),
                        "body": request_info.get("body", {}),
                        "timeout": request_info.get("timeout", 30)
                    }
                )
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                total_duration += duration_ms
                
                # Parse API response
                api_response = json.loads(result) if isinstance(result, str) else result
                
                # Create test result
                test_result = TestResult(
                    case_id=request_info.get("case_id", f"API_{len(test_results)+1}"),
                    name=request_info.get("name", "API Request"),
                    status="passed" if api_response.get("status_code", 0) < 400 else "failed",
                    duration_ms=duration_ms,
                    error_message=api_response.get("error") if api_response.get("status_code", 0) >= 400 else None,
                    performance_data={
                        "response_time_ms": duration_ms,
                        "status_code": api_response.get("status_code"),
                        "response_size": len(str(api_response.get("body", "")))
                    }
                )
                
                test_results.append(test_result)
            
            # Create suite result
            suite_result = SuiteResult(
                suite_id=session_id,
                suite_name=f"API Test Suite - {framework}",
                total_cases=len(test_results),
                passed_cases=len([r for r in test_results if r.status == "passed"]),
                failed_cases=len([r for r in test_results if r.status == "failed"]),
                skipped_cases=0,
                duration_ms=total_duration,
                case_results=test_results,
                start_time=session["start_time"],
                end_time=datetime.utcnow().isoformat()
            )
            
            return {
                "suite_result": suite_result.__dict__,
                "individual_results": [r.__dict__ for r in test_results],
                "execution_method": "mcp_api_request"
            }
            
        except Exception as e:
            raise Exception(f"MCP execution failed: {str(e)}")

    async def _execute_with_framework(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests using framework-specific runners"""
        framework = session["framework"]
        session_dir = session["session_dir"]
        
        if framework == "playwright":
            return await self._execute_playwright_tests(session)
        elif framework == "jest":
            return await self._execute_jest_tests(session)
        elif framework == "postman":
            return await self._execute_postman_tests(session)
        else:
            raise ValueError(f"Unsupported framework: {framework}")

    async def _execute_playwright_tests(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Playwright tests"""
        session_dir = Path(session["session_dir"])
        
        try:
            # Install dependencies if needed
            await self._install_dependencies(session_dir, ["@playwright/test"])
            
            # Run Playwright tests
            cmd = [
                "npx", "playwright", "test",
                "--reporter=json",
                f"--output-dir={session_dir}/test-results"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=session_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Parse results
            test_results = await self._parse_playwright_results(result, session_dir)
            
            return {
                "suite_result": test_results["suite_result"],
                "individual_results": test_results["individual_results"],
                "execution_method": "playwright_runner",
                "command_output": result.stdout,
                "command_error": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("Playwright test execution timed out")
        except Exception as e:
            raise Exception(f"Playwright execution failed: {str(e)}")

    async def _execute_jest_tests(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Jest tests"""
        session_dir = Path(session["session_dir"])
        
        try:
            # Install dependencies if needed
            await self._install_dependencies(session_dir, ["jest", "ts-jest", "@types/jest"])
            
            # Run Jest tests
            cmd = [
                "npx", "jest",
                "--verbose",
                "--json",
                f"--outputFile={session_dir}/jest-results.json"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=session_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results
            test_results = await self._parse_jest_results(result, session_dir)
            
            return {
                "suite_result": test_results["suite_result"],
                "individual_results": test_results["individual_results"],
                "execution_method": "jest_runner",
                "command_output": result.stdout,
                "command_error": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("Jest test execution timed out")
        except Exception as e:
            raise Exception(f"Jest execution failed: {str(e)}")

    async def _execute_postman_tests(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Postman collection tests"""
        session_dir = Path(session["session_dir"])
        
        try:
            # Find Postman collection file
            collection_file = None
            for file_path in session["test_files"]:
                if "postman_collection.json" in file_path:
                    collection_file = file_path
                    break
            
            if not collection_file:
                raise Exception("Postman collection file not found")
            
            # Use Newman for Postman collection execution
            cmd = [
                "npx", "newman", "run",
                collection_file,
                "--reporters", "json",
                f"--reporter-json-export={session_dir}/newman-results.json"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=session_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results
            test_results = await self._parse_newman_results(result, session_dir)
            
            return {
                "suite_result": test_results["suite_result"],
                "individual_results": test_results["individual_results"],
                "execution_method": "newman_runner",
                "command_output": result.stdout,
                "command_error": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("Postman test execution timed out")
        except Exception as e:
            raise Exception(f"Postman execution failed: {str(e)}")

    async def _parse_api_requests(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse test files to extract API requests"""
        api_requests = []
        
        for file_path in session["test_files"]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract API requests from test code
                # This is a simplified parser - in production, use AST parsing
                requests = self._extract_requests_from_code(content, file_path)
                api_requests.extend(requests)
                
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
        
        return api_requests

    def _extract_requests_from_code(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract API requests from test code (simplified implementation)"""
        requests = []
        
        # Simple regex-based extraction (in production, use proper AST parsing)
        import re
        
        # Look for API request patterns
        patterns = [
            r"apiContext\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]",
            r"axios\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]",
            r"request\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]"
        ]
        
        for i, line in enumerate(code.split('\n')):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    requests.append({
                        "case_id": f"REQ_{len(requests)+1}",
                        "name": f"Request from {Path(file_path).name}:{i+1}",
                        "method": match.group(1).upper(),
                        "url": match.group(2),
                        "headers": {"Content-Type": "application/json"},
                        "body": {},
                        "timeout": 30
                    })
        
        return requests

    async def _install_dependencies(self, session_dir: Path, packages: List[str]) -> None:
        """Install npm dependencies"""
        try:
            # Initialize npm project if needed
            package_json_path = session_dir / "package.json"
            if not package_json_path.exists():
                subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=session_dir,
                    capture_output=True
                )
            
            # Install packages
            if packages:
                subprocess.run(
                    ["npm", "install"] + packages,
                    cwd=session_dir,
                    capture_output=True
                )
                
        except Exception as e:
            print(f"Warning: Failed to install dependencies: {e}")

    async def _parse_playwright_results(self, result: subprocess.CompletedProcess, session_dir: Path) -> Dict[str, Any]:
        """Parse Playwright test results"""
        try:
            # Look for results file
            results_file = session_dir / "test-results" / "results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results_data = json.load(f)
                
                # Convert to our format
                test_results = []
                total_duration = 0
                
                for suite in results_data.get("suites", []):
                    for spec in suite.get("specs", []):
                        for test in spec.get("tests", []):
                            duration_ms = test.get("results", [{}])[0].get("duration", 0)
                            total_duration += duration_ms
                            
                            test_result = TestResult(
                                case_id=test.get("title", "Unknown"),
                                name=test.get("title", "Unknown"),
                                status="passed" if test.get("ok", True) else "failed",
                                duration_ms=duration_ms,
                                error_message=test.get("results", [{}])[0].get("error", {}).get("message")
                            )
                            test_results.append(test_result)
                
                suite_result = SuiteResult(
                    suite_id=str(uuid.uuid4()),
                    suite_name="Playwright Test Suite",
                    total_cases=len(test_results),
                    passed_cases=len([r for r in test_results if r.status == "passed"]),
                    failed_cases=len([r for r in test_results if r.status == "failed"]),
                    skipped_cases=0,
                    duration_ms=total_duration,
                    case_results=test_results,
                    start_time=datetime.utcnow().isoformat(),
                    end_time=datetime.utcnow().isoformat()
                )
                
                return {
                    "suite_result": suite_result.__dict__,
                    "individual_results": [r.__dict__ for r in test_results]
                }
            else:
                # Fallback to command output parsing
                return self._parse_command_output(result.stdout, "Playwright")
                
        except Exception as e:
            return self._parse_command_output(result.stdout, "Playwright")

    async def _parse_jest_results(self, result: subprocess.CompletedProcess, session_dir: Path) -> Dict[str, Any]:
        """Parse Jest test results"""
        try:
            results_file = session_dir / "jest-results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results_data = json.load(f)
                
                test_results = []
                total_duration = 0
                
                for test_file in results_data.get("testResults", []):
                    for test_result in test_file.get("assertionResults", []):
                        duration_ms = test_result.get("duration", 0)
                        total_duration += duration_ms
                        
                        status = "passed"
                        error_message = None
                        
                        if test_result.get("status") == "failed":
                            status = "failed"
                            error_message = test_result.get("failureMessages", ["Unknown error"])[0]
                        elif test_result.get("status") == "pending":
                            status = "skipped"
                        
                        test_result_obj = TestResult(
                            case_id=test_result.get("title", "Unknown"),
                            name=test_result.get("title", "Unknown"),
                            status=status,
                            duration_ms=duration_ms,
                            error_message=error_message
                        )
                        test_results.append(test_result_obj)
                
                suite_result = SuiteResult(
                    suite_id=str(uuid.uuid4()),
                    suite_name="Jest Test Suite",
                    total_cases=len(test_results),
                    passed_cases=len([r for r in test_results if r.status == "passed"]),
                    failed_cases=len([r for r in test_results if r.status == "failed"]),
                    skipped_cases=len([r for r in test_results if r.status == "skipped"]),
                    duration_ms=total_duration,
                    case_results=test_results,
                    start_time=datetime.utcnow().isoformat(),
                    end_time=datetime.utcnow().isoformat()
                )
                
                return {
                    "suite_result": suite_result.__dict__,
                    "individual_results": [r.__dict__ for r in test_results]
                }
            else:
                return self._parse_command_output(result.stdout, "Jest")
                
        except Exception as e:
            return self._parse_command_output(result.stdout, "Jest")

    async def _parse_newman_results(self, result: subprocess.CompletedProcess, session_dir: Path) -> Dict[str, Any]:
        """Parse Newman (Postman) test results"""
        try:
            results_file = session_dir / "newman-results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results_data = json.load(f)
                
                test_results = []
                total_duration = 0
                
                for run in results_data.get("run", {}).get("executions", []):
                    item = run.get("item", {})
                    request = item.get("request", {})
                    
                    duration_ms = run.get("response", {}).get("responseTime", 0)
                    total_duration += duration_ms
                    
                    # Check for test assertions
                    status = "passed"
                    error_message = None
                    
                    for assertion in run.get("assertions", []):
                        if assertion.get("error"):
                            status = "failed"
                            error_message = assertion.get("error", {}).get("message", "Assertion failed")
                            break
                    
                    test_result = TestResult(
                        case_id=item.get("name", "Unknown"),
                        name=item.get("name", "Unknown"),
                        status=status,
                        duration_ms=duration_ms,
                        error_message=error_message,
                        performance_data={
                            "response_time_ms": duration_ms,
                            "status_code": run.get("response", {}).get("code"),
                            "response_size": len(str(run.get("response", {}).get("body", "")))
                        }
                    )
                    test_results.append(test_result)
                
                suite_result = SuiteResult(
                    suite_id=str(uuid.uuid4()),
                    suite_name="Postman Test Suite",
                    total_cases=len(test_results),
                    passed_cases=len([r for r in test_results if r.status == "passed"]),
                    failed_cases=len([r for r in test_results if r.status == "failed"]),
                    skipped_cases=0,
                    duration_ms=total_duration,
                    case_results=test_results,
                    start_time=datetime.utcnow().isoformat(),
                    end_time=datetime.utcnow().isoformat()
                )
                
                return {
                    "suite_result": suite_result.__dict__,
                    "individual_results": [r.__dict__ for r in test_results]
                }
            else:
                return self._parse_command_output(result.stdout, "Postman")
                
        except Exception as e:
            return self._parse_command_output(result.stdout, "Postman")

    def _parse_command_output(self, output: str, framework: str) -> Dict[str, Any]:
        """Parse command output as fallback"""
        # Simple parsing of command output
        lines = output.split('\n')
        
        passed = 0
        failed = 0
        
        for line in lines:
            if "✓" in line or "pass" in line.lower():
                passed += 1
            elif "✗" in line or "fail" in line.lower():
                failed += 1
        
        total = passed + failed
        
        suite_result = SuiteResult(
            suite_id=str(uuid.uuid4()),
            suite_name=f"{framework} Test Suite",
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            skipped_cases=0,
            duration_ms=0,
            case_results=[],
            start_time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat()
        )
        
        return {
            "suite_result": suite_result.__dict__,
            "individual_results": [],
            "parse_method": "command_output"
        }

    async def _cleanup_session(self, session_id: str) -> None:
        """Clean up execution session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session_dir = Path(session["session_dir"])
            
            try:
                # Remove session directory
                import shutil
                shutil.rmtree(session_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup session directory: {e}")
            
            # Remove from active sessions
            del self.active_sessions[session_id]

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self._cleanup_session(session_id)
        
        # Cleanup temp directory
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp directory: {e}")
