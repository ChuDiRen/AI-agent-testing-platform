# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC基类
为RBAC实体提供统一的基类
"""

from sqlalchemy.orm import declarative_base

# 创建RBAC专用的基类
RBACBase = declarative_base()
