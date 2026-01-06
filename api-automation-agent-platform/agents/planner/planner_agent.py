"""
Planner Agent - Test Plan Generation

The Planner Agent is responsible for:
1. Analyzing API documentation and information
2. Creating comprehensive test plans
3. Covering functional, security, performance, and integration testing
4. Generating structured test case specifications
"""
from typing import Any, Dict, List, Optional
import json
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage


class PlannerAgent:
    """
    Test Planning Agent
    
    Analyzes API information and generates comprehensive test plans.
    """

    def __init__(self, llm: Optional[Any] = None, mcp_client: Optional[Any] = None):
        """
        Initialize planner agent
        
        Args:
            llm: Optional LLM instance
            mcp_client: Optional MCP client for API Planner tool
        """
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3  # Lower temperature for more structured output
        )
        self.mcp_client = mcp_client
        self.name = "planner"
        self.description = "Generate comprehensive test plans from API documentation"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test planning
        
        Args:
            input_data: Dictionary containing:
                - api_info: API information from RAG retrieval
                - test_types: List of test types to generate
                - special_requirements: Additional requirements
        
        Returns:
            Dictionary containing test plan and metadata
        """
        try:
            # Extract input parameters
            api_info = input_data.get("api_info", {})
            test_types = input_data.get("test_types", ["functional"])
            special_requirements = input_data.get("special_requirements", [])
            
            # Generate test plan
            if self.mcp_client:
                # Use MCP API Planner tool
                test_plan = await self._generate_plan_with_mcp(api_info, test_types, special_requirements)
            else:
                # Use LLM-based planning
                test_plan = await self._generate_plan_with_llm(api_info, test_types, special_requirements)
            
            # Validate and enhance plan
            validated_plan = await self._validate_and_enhance_plan(test_plan, api_info)
            
            return {
                "status": "success",
                "test_plan": validated_plan,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "test_types": test_types,
                    "api_count": len(api_info.get("entities", [])),
                    "total_test_cases": len(validated_plan.get("test_cases", []))
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "test_plan": None
            }

    async def _generate_plan_with_mcp(self, api_info: Dict[str, Any], test_types: List[str], special_requirements: List[str]) -> Dict[str, Any]:
        """Generate test plan using MCP API Planner tool"""
        try:
            # Call API Planner MCP tool
            result = await self.mcp_client.call_tool(
                "api_planner",
                {
                    "apiInfo": api_info,
                    "testCategories": test_types,
                    "specialRequirements": special_requirements,
                    "outputFormat": "structured"
                }
            )
            
            return json.loads(result)
            
        except Exception as e:
            # Fallback to LLM-based planning
            return await self._generate_plan_with_llm(api_info, test_types, special_requirements)

    async def _generate_plan_with_llm(self, api_info: Dict[str, Any], test_types: List[str], special_requirements: List[str]) -> Dict[str, Any]:
        """Generate test plan using LLM"""
        system_prompt = """
        You are an expert API testing strategist. Based on the provided API information, create a comprehensive test plan.

        Your test plan should include:
        1. Test objectives and scope
        2. Test categories (functional, security, performance, integration)
        3. Detailed test cases with:
           - Test case ID
           - Test case name
           - Description
           - Priority (high/medium/low)
           - Test type
           - Preconditions
           - Test steps
           - Expected results
        4. Test data requirements
        5. Environment setup requirements

        Return the plan in structured JSON format.
        """
        
        human_prompt = f"""
        API Information:
        {json.dumps(api_info, indent=2)}
        
        Required Test Types: {', '.join(test_types)}
        Special Requirements: {', '.join(special_requirements) if special_requirements else 'None'}
        
        Generate a comprehensive test plan.
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
            # Fallback to basic structure
            return self._create_basic_test_plan(api_info, test_types)

    def _create_basic_test_plan(self, api_info: Dict[str, Any], test_types: List[str]) -> Dict[str, Any]:
        """Create basic test plan structure as fallback"""
        entities = api_info.get("entities", [])
        test_cases = []
        
        for entity in entities:
            if entity.get("entity_type") == "API_ENDPOINT":
                endpoint_name = entity.get("entity_name", "Unknown Endpoint")
                
                for test_type in test_types:
                    test_cases.append({
                        "case_id": f"TC{len(test_cases)+1:03d}",
                        "name": f"{test_type.title()} Test - {endpoint_name}",
                        "description": f"Validate {test_type} aspects of {endpoint_name}",
                        "priority": "medium",
                        "test_type": test_type,
                        "preconditions": ["API is accessible", "Test data is available"],
                        "steps": [
                            {
                                "step_id": f"ST{len(test_cases)+1}-1",
                                "name": f"Execute {endpoint_name}",
                                "description": f"Send request to {endpoint_name}",
                                "expected_result": "Successful response"
                            }
                        ],
                        "expected_results": ["HTTP 200 response", "Valid response data"]
                    })
        
        return {
            "plan_id": str(uuid.uuid4()),
            "title": "API Test Plan",
            "description": "Generated test plan for API endpoints",
            "test_categories": test_types,
            "test_cases": test_cases,
            "requirements": {
                "environment": "Test environment with API access",
                "tools": "API testing tools (Postman, curl, etc.)",
                "data": "Test data for API requests"
            }
        }

    async def _validate_and_enhance_plan(self, test_plan: Dict[str, Any], api_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the generated test plan"""
        # Ensure required fields
        if "test_cases" not in test_plan:
            test_plan["test_cases"] = []
        
        if "plan_id" not in test_plan:
            test_plan["plan_id"] = str(uuid.uuid4())
        
        # Validate test cases
        validated_cases = []
        for case in test_plan["test_cases"]:
            if self._validate_test_case(case):
                enhanced_case = await self._enhance_test_case(case, api_info)
                validated_cases.append(enhanced_case)
        
        test_plan["test_cases"] = validated_cases
        
        # Add metadata
        test_plan["metadata"] = {
            "total_cases": len(validated_cases),
            "coverage_analysis": self._analyze_coverage(validated_cases, api_info),
            "estimated_duration": self._estimate_duration(validated_cases)
        }
        
        return test_plan

    def _validate_test_case(self, test_case: Dict[str, Any]) -> bool:
        """Validate individual test case"""
        required_fields = ["case_id", "name", "description", "test_type", "steps"]
        return all(field in test_case for field in required_fields)

    async def _enhance_test_case(self, test_case: Dict[str, Any], api_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance test case with additional details"""
        enhanced_case = test_case.copy()
        
        # Add default priority if missing
        if "priority" not in enhanced_case:
            enhanced_case["priority"] = "medium"
        
        # Add tags based on test type
        tags = [enhanced_case.get("test_type", "functional")]
        if enhanced_case.get("priority") == "high":
            tags.append("critical")
        enhanced_case["tags"] = tags
        
        # Add execution metadata
        enhanced_case["execution"] = {
            "estimated_duration": 30,  # seconds
            "retry_count": 3,
            "timeout": 60
        }
        
        return enhanced_case

    def _analyze_coverage(self, test_cases: List[Dict[str, Any]], api_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage"""
        total_endpoints = len([e for e in api_info.get("entities", []) if e.get("entity_type") == "API_ENDPOINT"])
        covered_endpoints = len(set(case.get("endpoint", "") for case in test_cases if case.get("endpoint")))
        
        test_types = set(case.get("test_type", "functional") for case in test_cases)
        
        return {
            "endpoint_coverage": f"{covered_endpoints}/{total_endpoints}" if total_endpoints > 0 else "0/0",
            "test_type_coverage": list(test_types),
            "coverage_percentage": (covered_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        }

    def _estimate_duration(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate test execution duration"""
        base_duration = sum(case.get("execution", {}).get("estimated_duration", 30) for case in test_cases)
        
        return {
            "estimated_seconds": base_duration,
            "estimated_minutes": base_duration / 60,
            "parallel_execution_time": base_duration / 4  # Assuming 4 parallel executions
        }
