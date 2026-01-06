# -*- coding: utf-8 -*-
"""FastAPI应用入口"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.database import init_db, init_data
from core.logger import setup_logging, get_logger
from core.middleware import trace_id_middleware, cors_header_middleware

# 配置日志系统
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    consumer_threads = []
    try:
        logger.info("=" * 60)
        logger.info("AI Agent Testing Platform 启动中...")
        logger.info("=" * 60)

        # 初始化数据库表
        init_db()

        # 初始化数据
        init_data()

        # 启动消息队列消费者（后台线程）
        try:
            from config.dev_settings import settings
            from core.TestExecutionConsumer import test_execution_consumer
            from core.MessagePushConsumer import message_push_consumer
            import threading
            
            logger.info(f"📨 消息队列类型: {settings.QUEUE_TYPE.upper()}")
            
            # 启动测试执行消费者
            test_thread = threading.Thread(
                target=test_execution_consumer.start,
                daemon=True,
                name="TestExecutionConsumer"
            )
            test_thread.start()
            consumer_threads.append(test_thread)
            logger.info("✓ 测试执行消费者已启动")
            
            # 启动消息推送消费者
            msg_thread = threading.Thread(
                target=message_push_consumer.start,
                daemon=True,
                name="MessagePushConsumer"
            )
            msg_thread.start()
            consumer_threads.append(msg_thread)
            logger.info("✓ 消息推送消费者已启动")
            
        except Exception as e:
            logger.warning(f"⚠ 消息队列消费者启动失败: {e}")
            if settings.QUEUE_TYPE == "rabbitmq":
                logger.info("提示: 启动RabbitMQ服务: docker-compose up -d rabbitmq")
                logger.info("或修改配置使用内存队列: QUEUE_TYPE=memory")

        # 启动 Cron 调度器
        try:
            from apitest.service.cron_scheduler import cron_scheduler
            cron_scheduler.start()
            logger.info("✓ Cron 调度器已启动")
        except Exception as e:
            logger.error(f"✗ Cron 调度器启动失败: {e}")

        logger.info("=" * 60)
        logger.info("🚀 应用启动完成！")
        logger.info("📖 API文档: http://localhost:5000/docs")
        logger.info("🔗 ReDoc文档: http://localhost:5000/redoc")
        logger.info("🔌 WebSocket: ws://localhost:5000/ws/test-execution/{execution_id}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()

    try:
        yield  # 应用运行期间
    except asyncio.CancelledError:
        # 正常关闭信号，不需要记录错误
        logger.info("收到关闭信号...")
    finally:
        # 关闭时执行清理工作
        logger.info("=" * 60)
        logger.info("正在优雅关闭应用...")

        # 关闭 Cron 调度器
        try:
            from apitest.service.cron_scheduler import cron_scheduler
            cron_scheduler.shutdown()
            logger.info("✓ Cron 调度器已关闭")
        except Exception as e:
            logger.error(f"关闭 Cron 调度器失败: {e}")

        # ✅ 修复消息队列优雅关闭
        try:
            from core.QueueFactory import queue_manager
            logger.info("正在关闭消息队列...")
            queue_manager.close()
            logger.info("✓ 消息队列已关闭")
        except Exception as e:
            logger.error(f"关闭消息队列失败: {e}", exc_info=True)
        
        # 等待消费者线程完成当前任务(最多5秒)
        if consumer_threads:
            logger.info("等待消费者线程完成...")
            import time
            time.sleep(2)  # 给线程一些时间完成当前任务
            logger.info("✓ 消费者线程已停止")
        
        logger.info("👋 应用已安全关闭")
        logger.info("=" * 60)

# 创建FastAPI应用实例
application = FastAPI(
    title="AI Agent Testing Platform API",
    description="API接口测试平台后端服务",
    version="2.0.0",
    lifespan=lifespan  # 使用新的生命周期管理
)

# 配置CORS中间件
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册自定义中间件
@application.middleware("http")
async def add_trace_id(request, call_next):
    return await trace_id_middleware(request, call_next)


@application.middleware("http")
async def add_cors_headers(request, call_next):
    return await cors_header_middleware(request, call_next)

# 注册路由
from login.api import LoginController
application.include_router(LoginController.module_route)

from sysmanage.api import UserController
application.include_router(UserController.module_route)

from sysmanage.api import RoleController
application.include_router(RoleController.module_route)

from sysmanage.api import MenuController
application.include_router(MenuController.module_route)

from sysmanage.api import DeptController
application.include_router(DeptController.module_route)

# API测试模块路由
import apitest.api.ApiProjectController as ApiProjectController
application.include_router(ApiProjectController.module_route)

import apitest.api.ApiDbBaseController as ApiDbBaseController
application.include_router(ApiDbBaseController.module_route)

import apitest.api.ApiKeyWordController as ApiKeyWordController
application.include_router(ApiKeyWordController.module_route)

import apitest.api.ApiOperationTypeController as ApiOperationTypeController
application.include_router(ApiOperationTypeController.module_route)

import apitest.api.ApiMetaController as ApiMetaController
application.include_router(ApiMetaController.module_route)

import apitest.api.ApiInfoController as ApiInfoController
application.include_router(ApiInfoController.module_route)

import apitest.api.ApiInfoCaseController as ApiInfoCaseController
application.include_router(ApiInfoCaseController.module_route)

import apitest.api.ApiInfoCaseStepController as ApiInfoCaseStepController
application.include_router(ApiInfoCaseStepController.module_route)

import apitest.api.ApiCollectionInfoController as ApiCollectionInfoController
application.include_router(ApiCollectionInfoController.module_route)

import apitest.api.ApiCollectionDetailController as ApiCollectionDetailController
application.include_router(ApiCollectionDetailController.module_route)

import apitest.api.ApiHistoryController as ApiHistoryController
application.include_router(ApiHistoryController.module_route)

import apitest.api.ApiTestController as ApiTestController
application.include_router(ApiTestController.module_route)

import apitest.api.ApiReportViewerController as ApiReportViewerController
application.include_router(ApiReportViewerController.module_route)

import apitest.api.TestTaskController as TestTaskController
application.include_router(TestTaskController.module_route)

import apitest.api.ApiStatisticsController as ApiStatisticsController
application.include_router(ApiStatisticsController.module_route)

import apitest.api.ApiFolderController as ApiFolderController
application.include_router(ApiFolderController.module_route)

import apitest.api.ApiRequestHistoryController as ApiRequestHistoryController
application.include_router(ApiRequestHistoryController.module_route)

# 消息管理模块路由
from msgmanage.api import RobotConfigController
application.include_router(RobotConfigController.module_route)

from msgmanage.api import RobotMsgConfigController
application.include_router(RobotMsgConfigController.module_route)

from msgmanage.api import MsgTemplateController
application.include_router(MsgTemplateController.template_route)

# 注册AI测试助手模块路由
from aiassistant.api import AiModelController, PromptTemplateController, TestCaseController
application.include_router(AiModelController.module_route)  # AI模型管理（含同步功能）
application.include_router(PromptTemplateController.module_route)  # 提示词模板管理
application.include_router(TestCaseController.module_route)  # 测试用例管理
# 注意: AI对话能力通过独立的 LangGraph Server 提供 (langgraph dev/up, 端口2024)

# 注册代码生成器模块路由
from generator.api import generator_route, gen_table_route
application.include_router(generator_route)  # 代码生成器
application.include_router(gen_table_route)  # 表配置管理

# 注册Web测试模块路由
from webtest.api.WebProjectController import module_route as web_project_route
from webtest.api.WebCaseController import module_route as web_case_route
from webtest.api.WebElementController import module_route as web_element_route
from webtest.api.WebExecutionController import module_route as web_execution_route
from webtest.api.WebKeywordController import module_route as web_keyword_route

application.include_router(web_project_route)  # Web项目管理
application.include_router(web_case_route)  # Web用例管理
application.include_router(web_element_route)  # Web元素管理
application.include_router(web_execution_route)  # Web执行管理
application.include_router(web_keyword_route)  # Web关键字管理

# WebSocket路由 - 测试执行实时进度推送
from fastapi import WebSocket, WebSocketDisconnect
from core.WebSocketManager import manager as ws_manager

@application.websocket("/ws/test-execution/{execution_id}")
async def websocket_test_execution(websocket: WebSocket, execution_id: str):
    """WebSocket端点：测试执行实时进度"""
    await ws_manager.connect(execution_id, websocket)
    try:
        while True:
            # 保持连接，接收客户端心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(execution_id, websocket)
        logger.info(f"WebSocket disconnected: {execution_id}")

# 挂载静态文件服务 - 报告目录
# 注意：前端代理会把 /api 前缀去掉，所以这里挂载到 /reports
from config.dev_settings import settings
reports_dir = Path(settings.BASE_DIR) / "temp"
if reports_dir.exists():
    application.mount("/reports", StaticFiles(directory=str(reports_dir), html=True), name="reports")
    logger.info(f"📁 报告目录已挂载: /reports -> {reports_dir}")

# 移除旧的 on_event 装饰器，已使用 lifespan 替代
