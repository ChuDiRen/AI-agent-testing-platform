"""
Test Execution Engine

Executes test suites using Playwright and Jest frameworks.
Handles test execution, result collection, and error reporting.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import asyncio
import subprocess
import tempfile
import shutil
from datetime import datetime
import re
import logging

from api_agent.models import (
    TestCase, TestStep, TestStatus, CaseResult, SuiteResult
)

logger = logging.getLogger(__name__)


class TestRunnerConfig:
    """Configuration for test runner"""

    def __init__(
        self,
        framework: str,  # playwright, jest
        test_files: List[str],
        base_url: Optional[str] = None,
        timeout: int = 60000,  # milliseconds
        retries: int = 0,
        parallel: bool = False,
        env_vars: Optional[Dict[str, str]] = None
    ):
        self.framework = framework
        self.test_files = test_files
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        self.parallel = parallel
        self.env_vars = env_vars or {}


class PlaywrightRunner:
    """Run Playwright API tests"""

    def __init__(self, config: TestRunnerConfig):
        """
        Initialize Playwright runner

        Args:
            config: Test runner configuration
        """
        self.config = config
        self.results: List[CaseResult] = []

    async def run(self) -> SuiteResult:
        """
        Run Playwright tests

        Returns:
            SuiteResult with execution details
        """
        start_time = datetime.utcnow()

        logger.info(f"Starting Playwright test execution for {len(self.config.test_files)} files")

        try:
            # Execute Playwright tests
            if self.config.parallel:
                results = await self._run_parallel()
            else:
                results = await self._run_sequential()

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Aggregate results
            total_cases = len(results)
            passed_cases = sum(1 for r in results if r.status == TestStatus.PASSED)
            failed_cases = sum(1 for r in results if r.status == TestStatus.FAILED)
            skipped_cases = sum(1 for r in results if r.status == TestStatus.SKIPPED)

            return SuiteResult(
                suite_id=f"playwright-{datetime.utcnow().timestamp()}",
                suite_name="Playwright Test Suite",
                status=TestStatus.COMPLETED if failed_cases == 0 else TestStatus.FAILED,
                total_cases=total_cases,
                passed_cases=passed_cases,
                failed_cases=failed_cases,
                skipped_cases=skipped_cases,
                duration_ms=duration_ms,
                case_results=results,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                summary=f"Executed {total_cases} tests: {passed_cases} passed, {failed_cases} failed"
            )

        except Exception as e:
            logger.error(f"Playwright execution failed: {e}")
            end_time = datetime.utcnow()
            return SuiteResult(
                suite_id=f"playwright-error-{datetime.utcnow().timestamp()}",
                suite_name="Playwright Test Suite",
                status=TestStatus.FAILED,
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                skipped_cases=0,
                duration_ms=(end_time - start_time).total_seconds() * 1000,
                case_results=[],
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                summary=f"Execution failed: {str(e)}"
            )

    async def _run_sequential(self) -> List[CaseResult]:
        """Run tests sequentially"""
        all_results = []

        for test_file in self.config.test_files:
            file_results = await self._run_test_file(test_file)
            all_results.extend(file_results)

        return all_results

    async def _run_parallel(self) -> List[CaseResult]:
        """Run tests in parallel"""
        tasks = [
            self._run_test_file(test_file)
            for test_file in self.config.test_files
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel test execution error: {result}")
            else:
                all_results.extend(result)

        return all_results

    async def _run_test_file(self, test_file: str) -> List[CaseResult]:
        """
        Run a single test file

        Args:
            test_file: Path to test file

        Returns:
            List of case results
        """
        # Prepare environment
        env = self.config.env_vars.copy()
        if self.config.base_url:
            env["BASE_URL"] = self.config.base_url

        try:
            # Execute Playwright test using subprocess
            cmd = [
                "npx", "playwright", "test",
                test_file,
                "--reporter=json",
                f"--timeout={self.config.timeout}"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(test_file).parent
            )

            stdout, stderr = await process.communicate()

            # Parse results
            if process.returncode == 0:
                return self._parse_playwright_results(stdout.decode('utf-8'), test_file)
            else:
                logger.error(f"Test execution failed: {stderr.decode('utf-8')}")
                return [
                    CaseResult(
                        case_id=f"error-{test_file}",
                        case_name=test_file,
                        status=TestStatus.FAILED,
                        duration_ms=0,
                        error_message=stderr.decode('utf-8')
                    )
                ]

        except Exception as e:
            logger.error(f"Failed to run test file {test_file}: {e}")
            return [
                CaseResult(
                    case_id=f"error-{test_file}",
                    case_name=test_file,
                    status=TestStatus.FAILED,
                    duration_ms=0,
                    error_message=str(e)
                )
            ]

    def _parse_playwright_results(self, output: str, test_file: str) -> List[CaseResult]:
        """
        Parse Playwright JSON output

        Args:
            output: JSON output from Playwright
            test_file: Test file path

        Returns:
            List of case results
        """
        try:
            data = json.loads(output)
            results = []

            # Playwright JSON structure varies, handle common formats
            if 'suites' in data:
                for suite in data['suites']:
                    for spec in suite.get('specs', []):
                        results.append(self._parse_playwright_spec(spec, test_file))
            elif 'tests' in data:
                for test in data['tests']:
                    results.append(self._parse_playwright_spec(test, test_file))
            else:
                # Single test format
                results.append(self._parse_playwright_spec(data, test_file))

            return results

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Playwright output: {e}")
            return [
                CaseResult(
                    case_id=f"parse-error-{test_file}",
                    case_name=test_file,
                    status=TestStatus.FAILED,
                    duration_ms=0,
                    error_message=f"Failed to parse results: {str(e)}"
                )
            ]

    def _parse_playwright_spec(self, spec: Dict, test_file: str) -> CaseResult:
        """Parse individual Playwright test spec"""
        return CaseResult(
            case_id=spec.get('testId', 'unknown'),
            case_name=spec.get('title', spec.get('testId', 'unknown')),
            status=self._parse_status(spec.get('status', 'failed')),
            duration_ms=spec.get('duration', 0),
            error_message=spec.get('error', ''),
            start_time=spec.get('startTime'),
            end_time=spec.get('endTime'),
            assertions_passed=spec.get('passed', 0),
            assertions_failed=spec.get('failed', 0),
            execution_log=json.dumps(spec.get('errors', []))
        )

    def _parse_status(self, status: str) -> TestStatus:
        """Parse status string to enum"""
        status_map = {
            'passed': TestStatus.PASSED,
            'failed': TestStatus.FAILED,
            'skipped': TestStatus.SKIPPED,
            'timedOut': TestStatus.TIMEOUT
        }
        return status_map.get(status, TestStatus.FAILED)


class JestRunner:
    """Run Jest API tests"""

    def __init__(self, config: TestRunnerConfig):
        """
        Initialize Jest runner

        Args:
            config: Test runner configuration
        """
        self.config = config

    async def run(self) -> SuiteResult:
        """
        Run Jest tests

        Returns:
            SuiteResult with execution details
        """
        start_time = datetime.utcnow()

        logger.info(f"Starting Jest test execution for {len(self.config.test_files)} files")

        try:
            # Execute Jest tests
            cmd = [
                "npx", "jest",
                "--json",
                "--no-coverage"
            ] + self.config.test_files

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=self.config.env_vars,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            if process.returncode == 0:
                results = self._parse_jest_results(stdout.decode('utf-8'))
            else:
                logger.error(f"Jest execution failed: {stderr.decode('utf-8')}")
                # Try to parse results even if tests failed
                results = self._parse_jest_results(stdout.decode('utf-8'))

            # Aggregate results
            total_cases = len(results)
            passed_cases = sum(1 for r in results if r.status == TestStatus.PASSED)
            failed_cases = sum(1 for r in results if r.status == TestStatus.FAILED)
            skipped_cases = sum(1 for r in results if r.status == TestStatus.SKIPPED)

            return SuiteResult(
                suite_id=f"jest-{datetime.utcnow().timestamp()}",
                suite_name="Jest Test Suite",
                status=TestStatus.COMPLETED if failed_cases == 0 else TestStatus.FAILED,
                total_cases=total_cases,
                passed_cases=passed_cases,
                failed_cases=failed_cases,
                skipped_cases=skipped_cases,
                duration_ms=duration_ms,
                case_results=results,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                summary=f"Executed {total_cases} tests: {passed_cases} passed, {failed_cases} failed"
            )

        except Exception as e:
            logger.error(f"Jest execution failed: {e}")
            end_time = datetime.utcnow()
            return SuiteResult(
                suite_id=f"jest-error-{datetime.utcnow().timestamp()}",
                suite_name="Jest Test Suite",
                status=TestStatus.FAILED,
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                skipped_cases=0,
                duration_ms=(end_time - start_time).total_seconds() * 1000,
                case_results=[],
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                summary=f"Execution failed: {str(e)}"
            )

    def _parse_jest_results(self, output: str) -> List[CaseResult]:
        """
        Parse Jest JSON output

        Args:
            output: JSON output from Jest

        Returns:
            List of case results
        """
        try:
            data = json.loads(output)
            results = []

            if 'testResults' in data:
                for test_suite in data['testResults']:
                    suite_name = test_suite.get('name', 'unknown')

                    if 'assertionResults' in test_suite:
                        for test in test_suite['assertionResults']:
                            results.append(self._parse_jest_test(test, suite_name))
                    elif 'testResults' in test_suite:
                        # Nested structure
                        for nested_suite in test_suite.get('testResults', []):
                            for test in nested_suite.get('assertionResults', []):
                                results.append(self._parse_jest_test(test, nested_suite.get('name', suite_name)))

            return results

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Jest output: {e}")
            return [
                CaseResult(
                    case_id="parse-error",
                    case_name="Jest Suite",
                    status=TestStatus.FAILED,
                    duration_ms=0,
                    error_message=f"Failed to parse results: {str(e)}"
                )
            ]

    def _parse_jest_test(self, test: Dict, suite_name: str) -> CaseResult:
        """Parse individual Jest test"""
        status = TestStatus.FAILED
        if test.get('status') == 'passed':
            status = TestStatus.PASSED
        elif test.get('status') == 'skipped':
            status = TestStatus.SKIPPED

        # Parse duration (Jest returns seconds)
        duration_ms = test.get('duration', 0) * 1000

        # Extract error message
        error_message = None
        if 'failureMessages' in test and test['failureMessages']:
            error_message = '; '.join(test['failureMessages'])

        return CaseResult(
            case_id=test.get('fullName', 'unknown').replace(' ', '-'),
            case_name=f"{suite_name} > {test.get('title', 'unknown')}",
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
            start_time=None,
            end_time=None,
            assertions_passed=0,
            assertions_failed=len(test.get('failureMessages', []))
        )


class TestExecutor:
    """
    Test Executor - Unified interface for multiple frameworks

    Supports:
    - Playwright: API and E2E tests
    - Jest: JavaScript/TypeScript tests
    """
    def __init__(self, config: TestRunnerConfig):
        """
        Initialize test executor

        Args:
            config: Test runner configuration
        """
        self.config = config

        # Create appropriate runner based on framework
        if config.framework.lower() == 'playwright':
            self.runner = PlaywrightRunner(config)
        elif config.framework.lower() == 'jest':
            self.runner = JestRunner(config)
        else:
            raise ValueError(f"Unsupported framework: {config.framework}")

    async def execute(self) -> SuiteResult:
        """
        Execute tests

        Returns:
            SuiteResult with execution details
        """
        logger.info(f"Executing tests with {self.config.framework} runner")
        return await self.runner.run()

    @staticmethod
    async def execute_from_config(
        framework: str,
        test_files: List[str],
        base_url: Optional[str] = None,
        **kwargs
    ) -> SuiteResult:
        """
        Convenience method to execute tests from configuration

        Args:
            framework: Test framework (playwright, jest)
            test_files: List of test file paths
            base_url: Base URL for API requests
            **kwargs: Additional configuration options

        Returns:
            SuiteResult
        """
        config = TestRunnerConfig(
            framework=framework,
            test_files=test_files,
            base_url=base_url,
            **kwargs
        )
        executor = TestExecutor(config)
        return await executor.execute()


class TestGenerator:
    """
    Test Code Generator

    Generates test code in various formats from test cases.
    """

    @staticmethod
    def generate_playwright_test(
        test_case: TestCase,
        base_url: str = "http://localhost:8000"
    ) -> str:
        """
        Generate Playwright test code from test case

        Args:
            test_case: Test case model
            base_url: Base URL for API requests

        Returns:
            Playwright test code as string
        """
        code = f"""import {{ test, expect }} from '@playwright/test';

test.describe('{test_case.name}', () => {{
  const baseUrl = '{base_url}';

"""

        # Generate test steps
        for i, step in enumerate(test_case.steps, 1):
            method = step.method.lower()
            code += f"""
  test('{test_case.name} - Step {i}', async ({{ request }}) => {{
    const response = await request.{method}(`${{baseUrl}}{step.endpoint}`"""

            # Add query params
            if step.query_params:
                code += f",\n      {{ params: {json.dumps(step.query_params)} }}"

            # Add request body
            if method in ['post', 'put', 'patch'] and step.request_body:
                code += f",\n      data: {json.dumps(step.request_body)}"

            # Add headers
            if step.headers:
                code += f",\n      headers: {json.dumps(step.headers)}"

            code += ");\n"

            # Add assertions
            for assertion in step.assertions:
                if assertion.assertion_type == 'status_code':
                    code += f"    expect(response.status()).toBe({assertion.expected});\n"
                elif assertion.assertion_type == 'json_path':
                    code += f"    expect((await response.json()){assertion.target}).toBeDefined();\n"
                elif assertion.assertion_type == 'contains':
                    code += f"    expect(await response.text()).toContain('{assertion.expected}');\n"

            code += "  });\n"

        code += "});\n"
        return code

    @staticmethod
    def generate_jest_test(
        test_case: TestCase,
        base_url: str = "http://localhost:8000"
    ) -> str:
        """
        Generate Jest test code from test case

        Args:
            test_case: Test case model
            base_url: Base URL for API requests

        Returns:
            Jest test code as string
        """
        code = f"""const axios = require('axios');
const {{ expect, test }} = require('@jest/globals');

const baseUrl = '{base_url}';

describe('{test_case.name}', () => {{
"""

        for i, step in enumerate(test_case.steps, 1):
            method = step.method.lower()
            code += f"""
  test('{test_case.name} - Step {i}', async () => {{
    try {{
      const response = await axios.{method}(`${{baseUrl}}{step.endpoint}`"""

            if step.query_params:
                code += f",\n        {{ params: {json.dumps(step.query_params)} }}"

            if method in ['post', 'put', 'patch'] and step.request_body:
                code += f",\n        data: {json.dumps(step.request_body)}"

            code += ");\n"

            for assertion in step.assertions:
                if assertion.assertion_type == 'status_code':
                    code += f"      expect(response.status).toBe({assertion.expected});\n"
                elif assertion.assertion_type == 'contains':
                    code += f"      expect(response.data).toContain('{assertion.expected}');\n"

            code += "    } catch (error) {\n"
            code += "      throw error;\n"
            code += "    }\n"
            code += "  });\n"

        code += "});\n"
        return code


async def execute_tests(
    framework: str,
    test_files: List[str],
    base_url: Optional[str] = None,
    **kwargs
) -> SuiteResult:
    """
    Execute tests with specified framework

    Args:
        framework: Test framework (playwright, jest)
        test_files: List of test file paths
        base_url: Base URL for API requests
        **kwargs: Additional configuration

    Returns:
        SuiteResult

    Example:
        ```python
        result = await execute_tests(
            framework="playwright",
            test_files=["test_login.spec.ts"],
            base_url="http://api.example.com"
        )
        print(f"Passed: {result.passed_cases}/{result.total_cases}")
        ```
    """
    config = TestRunnerConfig(
        framework=framework,
        test_files=test_files,
        base_url=base_url,
        **kwargs
    )
    executor = TestExecutor(config)
    return await executor.execute()
