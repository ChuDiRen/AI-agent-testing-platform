"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db
import uvicorn

# 创建FastAPI应用实例
application = FastAPI(
    title="AI Agent Testing Platform API",
    description="API接口测试平台后端服务",
    version="2.0.0"
)

# 配置CORS
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from login.api import LoginController
application.include_router(LoginController.module_route)

from sysmanage.api import UserController
application.include_router(UserController.module_route)

from apitest.api import ApiProjectContoller
application.include_router(ApiProjectContoller.module_route)

from apitest.api import ApiDbBaseController
application.include_router(ApiDbBaseController.module_route)

from apitest.api import ApiKeyWordController
application.include_router(ApiKeyWordController.module_route)

from apitest.api import ApiOperationTypeController
application.include_router(ApiOperationTypeController.module_route)

from apitest.api import ApiMetaController
application.include_router(ApiMetaController.module_route)

@application.on_event("startup") # 启动时初始化数据库
async def startup_event():
    init_db()
    print("数据库表初始化完成")

@application.get("/", tags=["根路径"]) # 根路径接口
def root():
    return {
        "message": "AI Agent Testing Platform API",
        "version": "2.0.0",
        "docs": "/docs"
    }

if __name__ == '__main__':
    try:
        uvicorn.run(
            "app:application",
            host="0.0.0.0",
            port=8000,
            reload=True, # 开发环境启用热重载
            log_level="info"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
