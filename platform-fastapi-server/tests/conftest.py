"""
Pytest配置文件
提供测试fixtures和配置
"""
import sys
from pathlib import Path
from typing import Generator

import pytest
import httpx

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

# 后端服务地址
BASE_URL = "http://127.0.0.1:5000"


# 测试数据库引擎 (使用内存SQLite)
@pytest.fixture(name="engine")
def engine_fixture():
    """创建测试数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # 导入所有模型
    from sysmanage.model.user import User
    from sysmanage.model.role import Role
    from sysmanage.model.menu import Menu
    from sysmanage.model.dept import Dept
    
    from apitest.model.ApiProjectModel import ApiProject
    from apitest.model.ApiDbBaseModel import ApiDbBase
    from apitest.model.ApiKeyWordModel import ApiKeyWord
    from apitest.model.ApiOperationTypeModel import OperationType
    from apitest.model.ApiMetaModel import ApiMeta
    from apitest.model.ApiInfoModel import ApiInfo
    from apitest.model.ApiInfoCaseModel import ApiInfoCase
    from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
    from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
    from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
    from apitest.model.ApiHistoryModel import ApiHistory
    from apitest.model.ApiInfoGroupModel import ApiInfoGroup
    
    from msgmanage.model.RobotConfigModel import RobotConfig
    from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
    
    from aiassistant.model.AiModel import AiModel
    from aiassistant.model.TestCaseModel import TestCase
    from aiassistant.model.AiConversation import AiConversation
    from aiassistant.model.AiMessage import AiMessage
    from aiassistant.model.PromptTemplate import PromptTemplate
    
    from plugin.model.PluginModel import Plugin
    
    from generator.model.GenTable import GenTable
    from generator.model.GenTableColumn import GenTableColumn
    from generator.model.GenHistory import GenHistory
    
    # 创建所有表
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # 清理
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture() -> Generator[httpx.Client, None, None]:
    """创建测试客户端 - 连接到真实后端服务"""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(session: Session) -> dict:
    """创建认证头部(模拟登录)"""
    # 创建测试用户
    from sysmanage.model.user import User
    from datetime import datetime
    
    test_user = User(
        username="test_admin",
        password="hashed_password",
        dept_id=1,
        email="test@example.com",
        status="1",
        create_time=datetime.now()
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    
    # 生成测试token
    from core.JwtUtil import JwtUtils
    token = JwtUtils.create_token(test_user.username, test_user.password)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_project")
def test_project_fixture(session: Session):
    """创建测试项目"""
    from apitest.model.ApiProjectModel import ApiProject
    from datetime import datetime
    
    project = ApiProject(
        project_name="测试项目",
        project_desc="用于单元测试的项目",
        create_time=datetime.now()
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    
    return project


@pytest.fixture(name="test_api_info")
def test_api_info_fixture(session: Session, test_project):
    """创建测试API接口"""
    from apitest.model.ApiInfoModel import ApiInfo
    from datetime import datetime
    
    api_info = ApiInfo(
        project_id=test_project.id,
        api_name="测试接口",
        request_method="POST",
        request_url="https://api.example.com/test",
        create_time=datetime.now()
    )
    session.add(api_info)
    session.commit()
    session.refresh(api_info)
    
    return api_info


@pytest.fixture(name="test_case")
def test_case_fixture(session: Session, test_project):
    """创建测试用例"""
    from apitest.model.ApiInfoCaseModel import ApiInfoCase
    from datetime import datetime
    
    test_case = ApiInfoCase(
        project_id=test_project.id,
        case_name="测试用例",
        case_desc="用于单元测试的用例",
        create_time=datetime.now(),
        modify_time=datetime.now()
    )
    session.add(test_case)
    session.commit()
    session.refresh(test_case)
    
    return test_case


@pytest.fixture(autouse=True)
def reset_database(session: Session):
    """每个测试后重置数据库"""
    yield
    # 测试后清理数据
    session.rollback()
