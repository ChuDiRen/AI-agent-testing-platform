"""
LLM Integration Layer

Provides unified interface for LLM providers (OpenAI, Anthropic Claude, etc.)
with proper configuration, prompt management, and error handling.
"""
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import os
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
import logging

from api_agent import settings

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class LLMModel(str, Enum):
    """Supported LLM models"""
    # OpenAI
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"

    # Anthropic
    CLAUDE3_OPUS = "claude-3-opus-20240229"
    CLAUDE3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"


@dataclass
class LLMConfig:
    """Configuration for LLM instance"""
    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    timeout: int = 60


class LLMFactory:
    """Factory for creating LLM instances"""

    @staticmethod
    def create_llm(config: LLMConfig) -> Union[ChatOpenAI, ChatAnthropic, Any]:
        """
        Create LLM instance based on configuration

        Args:
            config: LLM configuration

        Returns:
            LLM instance

        Raises:
            ValueError: If provider or model is not supported
        """
        api_key = config.api_key

        if config.provider == LLMProvider.OPENAI:
            if not api_key:
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OpenAI API key not found. "
                        "Set OPENAI_API_KEY environment variable or pass in config."
                    )

            llm = ChatOpenAI(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                api_key=api_key
            )
            logger.info(f"Created OpenAI LLM: {config.model}")
            return llm

        elif config.provider == LLMProvider.ANTHROPIC:
            if not api_key:
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError(
                        "Anthropic API key not found. "
                        "Set ANTHROPIC_API_KEY environment variable or pass in config."
                    )

            llm = ChatAnthropic(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                api_key=api_key
            )
            logger.info(f"Created Anthropic LLM: {config.model}")
            return llm

        elif config.provider == LLMProvider.MOCK:
            logger.info("Created Mock LLM for testing")
            return MockLLM()

        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    @staticmethod
    def create_default() -> Union[ChatOpenAI, ChatAnthropic]:
        """
        Create default LLM based on settings

        Returns:
            Default LLM instance
        """
        provider = LLMProvider(settings.llm_provider)
        model = settings.llm_model

        config = LLMConfig(
            provider=provider,
            model=model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )

        return LLMFactory.create_llm(config)


class MockLLM:
    """Mock LLM for testing without API calls"""

    def __init__(self):
        self.model = "mock-llm"
        self.temperature = 0.7

    async def achat(self, messages: List[Any], **kwargs) -> Any:
        """Mock async chat"""
        last_message = messages[-1] if messages else None

        if isinstance(last_message, HumanMessage):
            content = last_message.content
            # Simple pattern matching for testing
            if "login" in content.lower():
                return AIMessage(
                    content=json.dumps({
                        "intent": "test_generation",
                        "api_info": {
                            "name": "Login API",
                            "path": "/api/v1/auth/login",
                            "method": "POST"
                        },
                        "test_categories": ["functional", "security"]
                    })
                )
            elif "plan" in content.lower():
                return AIMessage(
                    content=json.dumps({
                        "status": "success",
                        "testPlan": {
                            "title": "Test Plan",
                            "testCases": []
                        }
                    })
                )
            else:
                return AIMessage(
                    content=json.dumps({
                        "status": "acknowledged",
                        "message": "Request understood"
                    })
                )

        return AIMessage(content="I understand.")


class PromptTemplates:
    """Collection of prompt templates for different agent tasks"""

    @staticmethod
    def orchestrator_system() -> ChatPromptTemplate:
        """System prompt for Orchestrator Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the Orchestrator Agent for an API Automation Testing Platform.

Your responsibilities:
1. Understand user requirements from natural language
2. Break down complex tasks into subtasks
3. Coordinate sub-agents (RAG Retrieval, Planner, Generator, Executor, Analyzer)
4. Manage workflow execution order
5. Handle errors and implement retry logic
6. Aggregate results and provide summaries

Available Sub-Agents:
- RAG Retrieval Agent: Query knowledge base for API information
- Planner Agent: Generate test plans from API documentation
- Generator Agent: Generate test code (Playwright/Jest/Postman)
- Executor Agent: Execute tests and collect results
- Analyzer Agent: Analyze results and generate reports

Process:
1. Understand the user's request
2. Identify which sub-agents are needed
3. Create an execution plan
4. Execute subtasks in order
5. Aggregate and summarize results

Provide structured JSON responses when possible.
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    @staticmethod
    def rag_retrieval_system() -> ChatPromptTemplate:
        """System prompt for RAG Retrieval Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the RAG Retrieval Agent.

Your role:
- Query the knowledge base using RAG tools
- Retrieve API documentation, parameters, and related information
- Support 6 retrieval modes: local, global, hybrid, naive, mix, bypass
- Return structured results with entities, relationships, and chunks

Guidelines:
- Use the most appropriate retrieval mode based on the query
- Prefer "mix" mode for general queries
- Use "naive" for simple keyword searches
- Use "bypass" when you need all entities
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    @staticmethod
    def planner_system() -> ChatPromptTemplate:
        """System prompt for Planner Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the Planner Agent.

Your role:
- Analyze API documentation (OpenAPI/Swagger/GraphQL)
- Generate comprehensive test plans
- Cover multiple test categories: functional, security, performance, boundary
- Design test cases with clear steps and assertions

Test Categories:
- Functional: Happy path and normal operations
- Security: Authentication, authorization, input validation
- Performance: Response time, throughput
- Boundary: Invalid inputs, edge cases
- Integration: Cross-endpoint workflows

Output Format:
Return test plan as structured JSON with:
- title: Test plan title
- version: API version
- testCases: Array of test cases
- Each test case should have: case_id, name, description, priority, test_type, steps
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    @staticmethod
    def generator_system() -> ChatPromptTemplate:
        """System prompt for Generator Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the Generator Agent.

Your role:
- Generate executable test code from test plans
- Support multiple formats: Playwright, Jest, Postman
- Use best practices and coding standards
- Include proper assertions and error handling

Frameworks:
- Playwright: Use @playwright/test, TypeScript
- Jest: Use Jest, JavaScript
- Postman: Generate Postman Collection JSON

Guidelines:
- Follow the test plan exactly
- Include setup/teardown code
- Add clear comments
- Use TypeScript type annotations when applicable
- Handle authentication properly
- Extract variables for reuse between steps
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    @staticmethod
    def executor_system() -> ChatPromptTemplate:
        """System prompt for Executor Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the Executor Agent.

Your role:
- Execute test suites using Playwright/Jest
- Collect test results and performance metrics
- Handle test failures gracefully
- Provide detailed error logs

Execution Process:
1. Load test configuration
2. Execute tests in sequence or parallel
3. Capture results (passed/failed/skipped)
4. Measure performance metrics
5. Record execution logs

Output Format:
Return structured results with:
- suite_id: Test suite identifier
- total_cases: Total number of tests
- passed_cases: Number of passed tests
- failed_cases: Number of failed tests
- duration_ms: Execution time
- case_results: Array of individual test results
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

    @staticmethod
    def analyzer_system() -> ChatPromptTemplate:
        """System prompt for Analyzer Agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are the Analyzer Agent.

Your role:
- Analyze test execution results
- Generate comprehensive reports
- Create visualizations using Chart MCP
- Provide insights and recommendations

Analysis Tasks:
- Calculate pass rates and statistics
- Identify patterns in failures
- Suggest improvements
- Generate charts (pie, bar, line, etc.)
- Create Markdown/HTML reports

Output Format:
Return analysis with:
- summary: Test execution summary
- statistics: Detailed statistics
- charts: Array of chart configurations
- recommendations: List of improvement suggestions
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])


class LLMService:
    """
    LLM Service for managing LLM instances and prompts

    Provides high-level interface for agents to interact with LLMs.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM service

        Args:
            config: Optional LLM configuration. If None, uses default from settings.
        """
        if config:
            self.llm = LLMFactory.create_llm(config)
        else:
            self.llm = LLMFactory.create_default()

        self.prompts = PromptTemplates()

    async def chat(
        self,
        messages: List[Any],
        system_prompt: Optional[ChatPromptTemplate] = None,
        **kwargs
    ) -> Any:
        """
        Send chat request to LLM

        Args:
            messages: List of message objects
            system_prompt: Optional system prompt template
            **kwargs: Additional parameters for LLM

        Returns:
            LLM response
        """
        try:
            if system_prompt:
                # Apply system prompt
                full_messages = system_prompt.format_messages(messages=messages)
            else:
                full_messages = messages

            response = await self.llm.ainvoke(full_messages, **kwargs)
            logger.debug(f"LLM response received: {type(response)}")
            return response

        except Exception as e:
            logger.error(f"LLM chat failed: {e}")
            raise

    async def structured_chat(
        self,
        prompt_template: ChatPromptTemplate,
        input_data: Dict[str, Any]
    ) -> str:
        """
        Send structured chat request using prompt template

        Args:
            prompt_template: ChatPromptTemplate to use
            input_data: Input data for template variables

        Returns:
            String response from LLM
        """
        try:
            messages = prompt_template.format_messages(**input_data)
            response = await self.llm.ainvoke(messages)
            return response.content if hasattr(response, 'content') else str(response)

        except Exception as e:
            logger.error(f"Structured LLM chat failed: {e}")
            raise

    def update_config(self, config: LLMConfig):
        """
        Update LLM configuration

        Args:
            config: New LLM configuration
        """
        self.llm = LLMFactory.create_llm(config)
        logger.info(f"LLM configuration updated: {config.provider}/{config.model}")


# Create singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def reset_llm_service():
    """Reset LLM service singleton (mainly for testing)"""
    global _llm_service
    _llm_service = None
