"""
Generator Agent - Test Code Generation

The Generator Agent is responsible for:
1. Converting test plans into executable test code
2. Supporting multiple test frameworks (Playwright, Jest, Postman)
3. Generating TypeScript/JavaScript code
4. Including authentication, setup, and teardown code
5. Following best practices and coding standards
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid
from datetime import datetime
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class GeneratorAgent:
    """
    Test Code Generation Agent
    
    Converts test plans into executable test code for various frameworks.
    """

    def __init__(self, llm: Optional[Any] = None, mcp_client: Optional[Any] = None):
        """
        Initialize generator agent
        
        Args:
            llm: Optional LLM instance
            mcp_client: Optional MCP client for API Generator tool
        """
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1  # Very low temperature for code generation
        )
        self.mcp_client = mcp_client
        self.name = "generator"
        self.description = "Generate executable test code from test plans"

        # Code templates for different frameworks
        self.templates = self._load_templates()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test code generation
        
        Args:
            input_data: Dictionary containing:
                - test_plan: Test plan from Planner Agent
                - output_format: Target framework (playwright, jest, postman)
                - language: Programming language (typescript, javascript)
                - additional_options: Additional generation options
        
        Returns:
            Dictionary containing generated test files and metadata
        """
        try:
            # Extract input parameters
            test_plan = input_data.get("test_plan", {})
            output_format = input_data.get("output_format", "playwright")
            language = input_data.get("language", "typescript")
            additional_options = input_data.get("additional_options", {})
            
            # Generate test code
            if self.mcp_client:
                # Use MCP API Generator tool
                generated_code = await self._generate_code_with_mcp(
                    test_plan, output_format, language, additional_options
                )
            else:
                # Use LLM-based generation
                generated_code = await self._generate_code_with_llm(
                    test_plan, output_format, language, additional_options
                )
            
            # Validate and format code
            validated_code = await self._validate_and_format_code(
                generated_code, output_format, language
            )
            
            # Create file structure
            file_structure = self._create_file_structure(
                validated_code, output_format, language
            )
            
            return {
                "status": "success",
                "generated_files": file_structure,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "framework": output_format,
                    "language": language,
                    "total_files": len(file_structure),
                    "total_test_cases": len(test_plan.get("test_cases", []))
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "generated_files": None
            }

    async def _generate_code_with_mcp(self, test_plan: Dict[str, Any], output_format: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test code using MCP API Generator tool"""
        try:
            # Call API Generator MCP tool
            result = await self.mcp_client.call_tool(
                "api_generator",
                {
                    "testPlan": test_plan,
                    "outputFormat": output_format,
                    "language": language,
                    "testFramework": self._get_test_framework(output_format),
                    "options": options
                }
            )
            
            return json.loads(result)
            
        except Exception as e:
            # Fallback to LLM-based generation
            return await self._generate_code_with_llm(test_plan, output_format, language, options)

    async def _generate_code_with_llm(self, test_plan: Dict[str, Any], output_format: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test code using LLM"""
        system_prompt = f"""
        You are an expert test automation engineer. Generate executable test code based on the provided test plan.

        Requirements:
        1. Use {output_format} framework
        2. Write in {language} language
        3. Follow best practices and coding standards
        4. Include proper authentication, setup, and teardown
        5. Add comprehensive assertions and error handling
        6. Include detailed comments and documentation

        Return the code in structured JSON format with file names as keys and code content as values.
        """
        
        human_prompt = f"""
        Test Plan:
        {json.dumps(test_plan, indent=2)}
        
        Output Format: {output_format}
        Language: {language}
        Additional Options: {json.dumps(options, indent=2)}
        
        Generate complete, executable test code.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({})
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback to template-based generation
            return self._generate_code_from_template(test_plan, output_format, language)

    def _generate_code_from_template(self, test_plan: Dict[str, Any], output_format: str, language: str) -> Dict[str, Any]:
        """Generate code using predefined templates"""
        test_cases = test_plan.get("test_cases", [])
        
        if output_format == "playwright":
            return self._generate_playwright_tests(test_cases, language)
        elif output_format == "jest":
            return self._generate_jest_tests(test_cases, language)
        elif output_format == "postman":
            return self._generate_postman_tests(test_cases)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_playwright_tests(self, test_cases: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Generate Playwright test files"""
        files = {}
        
        # Group test cases by API module/endpoint
        grouped_cases = self._group_test_cases(test_cases)
        
        for group_name, cases in grouped_cases.items():
            file_name = f"test_{group_name.lower().replace(' ', '_')}.spec.{'ts' if language == 'typescript' else 'js'}"
            
            code = self._generate_playwright_file(cases, language)
            files[file_name] = code
        
        # Add configuration file
        files["playwright.config.ts"] = self._get_playwright_config()
        
        return files

    def _generate_playwright_file(self, test_cases: List[Dict[str, Any]], language: str) -> str:
        """Generate a single Playwright test file"""
        ts_extension = language == "typescript"
        
        imports = [
            "import { test, expect } from '@playwright/test';",
            "import { APIRequestContext, APIResponse } from '@playwright/test';"
        ]
        
        # Type definitions for TypeScript
        if ts_extension:
            imports.extend([
                "interface TestData {",
                "  [key: string]: any;",
                "}",
                "",
                "interface AuthData {",
                "  token: string;",
                "  user: any;",
                "}"
            ])
        
        code = "\n".join(imports) + "\n\n"
        
        # Add describe block
        group_name = test_cases[0].get("tags", ["API"])[0] if test_cases else "API"
        code += f"test.describe('{group_name} Tests', () => {{\n"
        
        # Add shared variables
        code += "  let authToken: string;\n"
        code += "  let apiContext: APIRequestContext;\n\n"
        
        # Add beforeAll setup
        code += "  test.beforeAll(async ({ playwright }) => {\n"
        code += "    // Setup API context\n"
        code += "    apiContext = await playwright.request.newContext({\n"
        code += "      baseURL: process.env.API_BASE_URL || 'http://localhost:3000',\n"
        code += "      extraHTTPHeaders: {\n"
        code += "        'Content-Type': 'application/json'\n"
        code += "      }\n"
        code += "    });\n\n"
        code += "    // Authenticate if needed\n"
        code += "    // const authResponse = await apiContext.post('/auth/login', {\n"
        code += "    //   data: { username: 'testuser', password: 'testpass' }\n"
        code += "    // });\n"
        code += "    // const authData = await authResponse.json() as AuthData;\n"
        code += "    // authToken = authData.token;\n"
        code += "  });\n\n"
        
        # Add afterAll cleanup
        code += "  test.afterAll(async () => {\n"
        code += "    await apiContext.dispose();\n"
        code += "  });\n\n"
        
        # Generate individual test cases
        for i, test_case in enumerate(test_cases):
            code += self._generate_playwright_test_case(test_case, i + 1, ts_extension)
        
        code += "});\n"
        
        return code

    def _generate_playwright_test_case(self, test_case: Dict[str, Any], case_number: int, ts_extension: bool) -> str:
        """Generate a single Playwright test case"""
        case_id = test_case.get("case_id", f"TC{case_number:03d}")
        case_name = test_case.get("name", f"Test Case {case_number}")
        description = test_case.get("description", "")
        
        code = f"  test('{case_id}: {case_name}', async () => {{\n"
        
        if description:
            code += f"    // {description}\n"
        
        # Add test steps
        steps = test_case.get("steps", [])
        for step in steps:
            step_name = step.get("name", "")
            step_desc = step.get("description", "")
            
            if "POST" in step_name.upper() or "login" in step_name.lower():
                code += f"    // {step_desc}\n"
                code += "    const response = await apiContext.post('/api/endpoint', {\n"
                code += "      data: {\n"
                code += "        // Add request data\n"
                code += "      }\n"
                if ts_extension:
                    code += "    } as TestData);\n"
                else:
                    code += "    });\n"
                code += "\n"
                code += "    expect(response.status()).toBe(200);\n"
                code += "    const responseBody = await response.json();\n"
                code += "    expect(responseBody).toHaveProperty('data');\n"
        
        code += "  });\n\n"
        
        return code

    def _generate_jest_tests(self, test_cases: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Generate Jest test files"""
        files = {}
        
        # Group test cases
        grouped_cases = self._group_test_cases(test_cases)
        
        for group_name, cases in grouped_cases.items():
            file_name = f"{group_name.lower().replace(' ', '_')}.test.{'ts' if language == 'typescript' else 'js'}"
            
            code = self._generate_jest_file(cases, language)
            files[file_name] = code
        
        # Add configuration
        files["jest.config.js"] = self._get_jest_config()
        
        return files

    def _generate_jest_file(self, test_cases: List[Dict[str, Any]], language: str) -> str:
        """Generate a single Jest test file"""
        ts_extension = language == "typescript"
        
        imports = [
            "import axios from 'axios';",
            "import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';"
        ]
        
        if ts_extension:
            imports.extend([
                "interface TestData {",
                "  [key: string]: any;",
                "}"
            ])
        
        code = "\n".join(imports) + "\n\n"
        
        # Add describe block
        group_name = test_cases[0].get("tags", ["API"])[0] if test_cases else "API"
        code += f"describe('{group_name} Tests', () => {{\n"
        
        # Add setup
        code += "  let apiClient: any;\n\n"
        code += "  beforeAll(() => {\n"
        code += "    apiClient = axios.create({\n"
        code += "      baseURL: process.env.API_BASE_URL || 'http://localhost:3000',\n"
        code += "      headers: {\n"
        code += "        'Content-Type': 'application/json'\n"
        code += "      }\n"
        code += "    });\n"
        code += "  });\n\n"
        
        # Generate test cases
        for i, test_case in enumerate(test_cases):
            code += self._generate_jest_test_case(test_case, i + 1, ts_extension)
        
        code += "});\n"
        
        return code

    def _generate_jest_test_case(self, test_case: Dict[str, Any], case_number: int, ts_extension: bool) -> str:
        """Generate a single Jest test case"""
        case_id = test_case.get("case_id", f"TC{case_number:03d}")
        case_name = test_case.get("name", f"Test Case {case_number}")
        
        code = f"  test('{case_id}: {case_name}', async () => {{\n"
        code += "    try {\n"
        code += "      const response = await apiClient.post('/api/endpoint', {\n"
        code += "        // Add request data\n"
        if ts_extension:
            code += "      } as TestData);\n"
        else:
            code += "      });\n"
        code += "\n"
        code += "      expect(response.status).toBe(200);\n"
        code += "      expect(response.data).toHaveProperty('data');\n"
        code += "    } catch (error) {\n"
        code += "      console.error('Test failed:', error);\n"
        code += "      throw error;\n"
        code += "    }\n"
        code += "  });\n\n"
        
        return code

    def _generate_postman_tests(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Postman collection"""
        collection = {
            "info": {
                "name": "API Test Collection",
                "description": "Generated API test collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Group test cases into folders
        grouped_cases = self._group_test_cases(test_cases)
        
        for group_name, cases in grouped_cases.items():
            folder = {
                "name": group_name,
                "item": []
            }
            
            for test_case in cases:
                item = self._create_postman_item(test_case)
                folder["item"].append(item)
            
            collection["item"].append(folder)
        
        return {"postman_collection.json": json.dumps(collection, indent=2)}

    def _create_postman_item(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Postman item from test case"""
        return {
            "name": test_case.get("name", "Test Case"),
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response has data', function () {",
                            "    const jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('data');",
                            "});"
                        ],
                        "type": "text/javascript"
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n  \"key\": \"value\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/endpoint",
                    "host": ["{{base_url}}"],
                    "path": ["api", "endpoint"]
                }
            }
        }

    def _group_test_cases(self, test_cases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group test cases by module or endpoint"""
        groups = {}
        
        for test_case in test_cases:
            # Extract group name from tags or test case name
            tags = test_case.get("tags", [])
            if tags:
                group_name = tags[0]
            else:
                # Extract from test case name
                name = test_case.get("name", "")
                group_name = name.split(" -")[0] if " -" in name else "General"
            
            if group_name not in groups:
                groups[group_name] = []
            
            groups[group_name].append(test_case)
        
        return groups

    def _create_file_structure(self, generated_code: Dict[str, Any], output_format: str, language: str) -> List[Dict[str, Any]]:
        """Create structured file information"""
        files = []
        
        for file_name, content in generated_code.items():
            files.append({
                "name": file_name,
                "content": content,
                "type": self._get_file_type(file_name),
                "framework": output_format,
                "language": language
            })
        
        return files

    def _get_file_type(self, file_name: str) -> str:
        """Determine file type from extension"""
        if file_name.endswith(".ts"):
            return "typescript"
        elif file_name.endswith(".js"):
            return "javascript"
        elif file_name.endswith(".json"):
            return "json"
        else:
            return "text"

    def _get_test_framework(self, output_format: str) -> str:
        """Get test framework name from output format"""
        mapping = {
            "playwright": "playwright-test",
            "jest": "jest",
            "postman": "postman"
        }
        return mapping.get(output_format, "unknown")

    def _load_templates(self) -> Dict[str, str]:
        """Load code templates"""
        return {
            "playwright_config": self._get_playwright_config(),
            "jest_config": self._get_jest_config()
        }

    def _get_playwright_config(self) -> str:
        """Get Playwright configuration"""
        return """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.API_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"""

    def _get_jest_config(self) -> str:
        """Get Jest configuration"""
        return """module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts', '**/*.test.js'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    'src/**/*.js',
    '!src/**/*.d.ts',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
};
"""

    async def _validate_and_format_code(self, generated_code: Dict[str, Any], output_format: str, language: str) -> Dict[str, Any]:
        """Validate and format generated code"""
        validated_code = {}
        
        for file_name, content in generated_code.items():
            # Basic validation
            if not content or not isinstance(content, str):
                continue
            
            # Format code (basic formatting)
            formatted_content = self._format_code(content, output_format, language)
            validated_code[file_name] = formatted_content
        
        return validated_code

    def _format_code(self, code: str, output_format: str, language: str) -> str:
        """Basic code formatting"""
        # Remove extra whitespace and ensure proper indentation
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                formatted_lines.append(line.rstrip())
            elif formatted_lines:  # Keep empty lines but not consecutive ones
                if formatted_lines[-1] != '':
                    formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
