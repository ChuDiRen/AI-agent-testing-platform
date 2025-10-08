# Copyright (c) 2025 左岚. All rights reserved.
"""
API引擎插件数据库初始化
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from .models.suite import ApiEngineSuite
from .models.case import ApiEngineCase
from .models.execution import ApiEngineExecution
from .models.keyword import ApiEngineKeyword

logger = logging.getLogger(__name__)


async def init_api_engine_plugin_db(db: AsyncSession):
    """
    初始化API引擎插件数据库
    
    Args:
        db: 异步数据库会话
    """
    logger.info("开始初始化API引擎插件数据库...")
    
    try:
        # 检查是否已经初始化过(通过检查是否存在示例套件)
        result = await db.execute(
            select(ApiEngineSuite).where(ApiEngineSuite.name == "示例测试套件")
        )
        existing_suite = result.scalar_one_or_none()
        
        if existing_suite:
            logger.info("API引擎插件数据库已初始化,跳过")
            return
        
        # 创建示例测试套件
        example_suite = ApiEngineSuite(
            name="示例测试套件",
            description="这是一个示例测试套件,展示了API引擎的基本功能",
            global_context={
                "URL": "https://api.example.com",
                "timeout": 30
            },
            created_by=1  # 假设管理员用户ID为1
        )
        db.add(example_suite)
        await db.flush()
        
        # 创建示例测试用例(YAML模式)
        example_case_yaml = ApiEngineCase(
            suite_id=example_suite.suite_id,
            name="示例登录测试(YAML模式)",
            description="使用YAML配置的登录测试用例",
            config_type="yaml",
            yaml_content="""desc: 登录测试用例
pre_script:
- 'print("执行前...")'
steps:
- 发送请求-POST:
    关键字: send_request
    method: POST
    url: "{{URL}}"
    headers: {}
    params:
      s: /api/user/login
      application: app
    data:
      accounts: demo
      pwd: '123456'
      type: username
post_script:
- 'print("执行后...")'
""",
            sort_order=1,
            status="active",
            created_by=1
        )
        db.add(example_case_yaml)
        
        # 创建示例测试用例(表单模式)
        example_case_form = ApiEngineCase(
            suite_id=example_suite.suite_id,
            name="示例API测试(表单模式)",
            description="使用表单配置的API测试用例",
            config_type="form",
            config_data={
                "desc": "GET请求示例",
                "pre_script": [],
                "steps": [
                    {
                        "name": "发送GET请求",
                        "params": {
                            "关键字": "send_request",
                            "method": "GET",
                            "url": "{{URL}}/api/test",
                            "headers": {},
                            "params": {}
                        }
                    }
                ],
                "post_script": [],
                "ddts": []
            },
            sort_order=2,
            status="active",
            created_by=1
        )
        db.add(example_case_form)
        
        await db.commit()
        
        logger.info("API引擎插件数据库初始化完成")
        logger.info(f"- 创建示例套件: {example_suite.name}")
        logger.info(f"- 创建示例用例: {example_case_yaml.name}, {example_case_form.name}")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"API引擎插件数据库初始化失败: {str(e)}")
        raise

