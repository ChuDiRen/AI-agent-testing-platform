"""
Test Engine MCP 模块
提供 MCP 服务接口，为 LLM 提供测试能力
"""
from pathlib import Path

MCP_ROOT = Path(__file__).parent
PROJECT_ROOT = MCP_ROOT.parent

__all__ = ["MCP_ROOT", "PROJECT_ROOT"]
