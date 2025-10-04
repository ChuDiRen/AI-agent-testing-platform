"""数据库模型包 - 完全按照博客 RBAC 表结构设计"""
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.department import Department
from app.models.user_role import t_user_role, UserRole
from app.models.role_menu import t_role_menu
from app.models.log import OperationLog
from app.models.notification import Notification
from app.models.testcase import TestCase
from app.models.report import TestReport, TestExecution
from app.models.ai_chat import ChatSession, ChatMessage, AIModel

__all__ = [
    "User",
    "Role",
    "Menu",
    "Department",
    "t_user_role",
    "UserRole",
    "t_role_menu",
    "OperationLog",
    "Notification",
    "TestCase",
    "TestReport",
    "TestExecution",
    "ChatSession",
    "ChatMessage",
    "AIModel",
]
