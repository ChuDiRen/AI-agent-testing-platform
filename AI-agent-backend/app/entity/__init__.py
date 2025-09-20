# Copyright (c) 2025 左岚. All rights reserved.
# Entity Layer - 数据库实体层
# 职责：定义数据库表结构，提供实体对象与字典的转换方法

from .agent import Agent
from .agent_config import AgentConfig
from .ai_model import AIModel
from .audit_log import AuditLog
from .base import BaseEntity
from .department import Department
from .menu import Menu
from .permission_cache import PermissionCache, DataPermissionRule
from .role import Role
from .role_menu import RoleMenu
from .test_case import TestCase
from .test_case_generation_history import TestCaseGenerationHistory
from .test_report import TestReport
from .user import User
from .user_role import UserRole
from .chat_session import ChatSession, ChatMessage

__all__ = [
    "BaseEntity",
    "User",
    "Role",
    "Menu",
    "Department",
    "UserRole",
    "RoleMenu",
    "AuditLog",
    "PermissionCache",
    "DataPermissionRule",
    "Agent",
    "AgentConfig",
    "AIModel",
    "TestCase",
    "TestReport",
    "ChatSession",
    "ChatMessage"
]
