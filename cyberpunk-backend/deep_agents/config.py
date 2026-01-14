"""
Deep Agents Configuration

Configuration for the multi-agent system using LangChain Deep Agents.
"""
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    name: str = Field(description="Agent name")
    description: str = Field(description="Agent description")
    tools: list[str] = Field(default_factory=list, description="Available tools")
    model: str = Field(default="deepseek-chat", description="LLM model")
    temperature: float = Field(default=0.3, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Max tokens")


class DeepAgentsConfig(BaseModel):
    """Configuration for the multi-agent system"""
    workspace_dir: Path = Field(default_factory=lambda: Path("./workspace"), description="Workspace directory")
    memory_dir: Path = Field(default_factory=lambda: Path("./memory"), description="Memory directory")
    
    # Agent configurations
    api_planner_agent: AgentConfig = Field(
        default_factory=lambda: AgentConfig(
            name="API Planner Agent",
            description="Plans API testing workflows and task decomposition",
            tools=["write_todos", "read_file", "write_file"],
            model="deepseek-chat"
        )
    )
    
    api_generator_agent: AgentConfig = Field(
        default_factory=lambda: AgentConfig(
            name="API Generator Agent", 
            description="Generates API test code and configurations",
            tools=["write_file", "edit_file", "ls"],
            model="deepseek-chat"
        )
    )
    
    api_executor_agent: AgentConfig = Field(
        default_factory=lambda: AgentConfig(
            name="API Executor Agent",
            description="Executes API tests and validates results",
            tools=["read_file", "ls"],
            model="deepseek-chat"
        )
    )
    
    api_analyzer_agent: AgentConfig = Field(
        default_factory=lambda: AgentConfig(
            name="API Analyzer Agent",
            description="Analyzes test results and generates reports",
            tools=["read_file", "write_file"],
            model="deepseek-chat"
        )
    )
    
    # System configuration
    enable_subagents: bool = Field(default=True, description="Enable subagent spawning")
    enable_planning: bool = Field(default=True, description="Enable task planning")
    enable_memory: bool = Field(default=True, description="Enable persistent memory")
    max_context_files: int = Field(default=10, description="Max context files to load")


def get_deep_agents_config() -> DeepAgentsConfig:
    """Get the deep agents configuration"""
    return DeepAgentsConfig()
