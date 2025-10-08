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
        await db.flush()

        # 创建示例执行记录
        from datetime import timedelta
        import uuid

        # 成功的执行记录
        execution_success = ApiEngineExecution(
            case_id=example_case_yaml.case_id,
            task_id=str(uuid.uuid4()),
            status="success",
            result={"status": "passed", "message": "测试通过"},
            logs="[INFO] 开始执行测试用例\n[INFO] 发送POST请求\n[INFO] 响应状态码: 200\n[INFO] 测试通过",
            duration=2.35,
            steps_total=3,
            steps_passed=3,
            steps_failed=0,
            executed_by=1,
            executed_at=example_suite.created_at - timedelta(hours=2),
            finished_at=example_suite.created_at - timedelta(hours=2, minutes=-2)
        )
        db.add(execution_success)

        # 失败的执行记录
        execution_failed = ApiEngineExecution(
            case_id=example_case_yaml.case_id,
            task_id=str(uuid.uuid4()),
            status="failed",
            result={"status": "failed", "message": "断言失败"},
            logs="[INFO] 开始执行测试用例\n[INFO] 发送POST请求\n[ERROR] 断言失败: 期望状态码200, 实际401",
            error_message="断言失败: 期望状态码200, 实际401",
            duration=1.82,
            steps_total=3,
            steps_passed=1,
            steps_failed=2,
            executed_by=1,
            executed_at=example_suite.created_at - timedelta(hours=1),
            finished_at=example_suite.created_at - timedelta(hours=1, minutes=-1)
        )
        db.add(execution_failed)

        # 运行中的执行记录
        execution_running = ApiEngineExecution(
            case_id=example_case_form.case_id,
            task_id=str(uuid.uuid4()),
            status="running",
            logs="[INFO] 开始执行测试用例\n[INFO] 正在发送GET请求...",
            steps_total=1,
            steps_passed=0,
            steps_failed=0,
            executed_by=1,
            executed_at=example_suite.created_at - timedelta(minutes=5)
        )
        db.add(execution_running)

        await db.commit()

        logger.info("API引擎插件数据库初始化完成")
        logger.info(f"- 创建示例套件: {example_suite.name}")
        logger.info(f"- 创建示例用例: {example_case_yaml.name}, {example_case_form.name}")
        logger.info(f"- 创建示例执行记录: 3条(成功1, 失败1, 运行中1)")

    except Exception as e:
        await db.rollback()
        logger.error(f"API引擎插件数据库初始化失败: {str(e)}")
        raise

