# 镜像 ：  https://pypi.tuna.tsinghua.edu.cn/simple
# 准备的包： flask flask_sqlalchemy flask_script pymysql flask_cors
# 安装核心库 ，注意一定要指定版本
# pip install Flask==2.3.2 Flask-SQLAlchemy==3.0.5 PyMySQL==1.1.0 Flask-Cors==4.0.0

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import  abort,request,g  # 导入模块
# 导入提示信息
from core.resp_model import respModel

# 实例化
application = Flask(__name__)
# 加载配置
application.config.from_pyfile('config/dev_settings.py')

# 解决跨域问题
CORS(application, resources=r'/*')

# 实例化数据库ORM
database = SQLAlchemy()
database.init_app(application)
# 实例化jwt用来生成token
# jwt = JWTManager()
# jwt.init_app(application)

if __name__ == '__main__':
    try:
        # 启动程序
        import sys
        
        # 数据库初始化（创建表结构 + 默认数据）
        # 在导入路由之前先初始化数据库
        from init_database import init_database, check_database_connection
        print("\n" + "=" * 60)
        print("🚀 正在启动应用...")
        print("=" * 60)
        if check_database_connection(application, database):
            init_database(application, database)
        else:
            print("⚠ 数据库连接失败，请检查配置")
            sys.exit(1)
        
        # TODO 1: 导入对应的模块
        from login.api import LoginController
        application.register_blueprint(LoginController.module_route)

        from sysmanage.api import UserController
        application.register_blueprint(UserController.module_route)

        # RBAC 权限管理
        from sysmanage.api import RoleController
        application.register_blueprint(RoleController.module_route)

        from sysmanage.api import MenuController
        application.register_blueprint(MenuController.module_route)

        from sysmanage.api import DeptController
        application.register_blueprint(DeptController.module_route)

        from sysmanage.api import ApiController
        application.register_blueprint(ApiController.module_route)

        from sysmanage.api import AuditLogController
        application.register_blueprint(AuditLogController.module_route)

        # 接口自动化导入的路由信息
        from apitest.api import ApiProjectContoller
        application.register_blueprint(ApiProjectContoller.module_route)

        from apitest.api import ApiDbBaseController
        application.register_blueprint(ApiDbBaseController.module_route)

        from apitest.api import ApiKeyWordController
        application.register_blueprint(ApiKeyWordController.module_route)

        from apitest.api import ApiOperationTypeController
        application.register_blueprint(ApiOperationTypeController.module_route)

        from apitest.api import ApiMetaController
        application.register_blueprint(ApiMetaController.module_route)

        from apitest.api import ApiInfoController
        application.register_blueprint(ApiInfoController.module_route)

        from apitest.api import ApiInfoCaseController
        application.register_blueprint(ApiInfoCaseController.module_route)

        from apitest.api import ApiInfoCaseStepContoller
        application.register_blueprint(ApiInfoCaseStepContoller.module_route)

        from apitest.api import ApiReportViewerContoller
        application.register_blueprint(ApiReportViewerContoller.module_route)

        from apitest.api import ApiCollectionInfoController
        application.register_blueprint(ApiCollectionInfoController.module_route)

        from apitest.api import ApiCollectionDetailController
        application.register_blueprint(ApiCollectionDetailController.module_route)

        from apitest.api import ApiHistoryController
        application.register_blueprint(ApiHistoryController.module_route)

        # 机器人管理
        from msgmanage.api import RobotConfigController
        application.register_blueprint(RobotConfigController.module_route)

        from msgmanage.api import RobotMsgConfigController
        application.register_blueprint(RobotMsgConfigController.module_route)

        # 个人中心和系统设置
        from userprofile.api import ProfileController
        application.register_blueprint(ProfileController.module_route)

        from systemsettings.api import SettingsController
        application.register_blueprint(SettingsController.module_route)

        # 扩展-图标增加
        from apitest.api import  ApiTestPlanChartController
        application.register_blueprint(ApiTestPlanChartController.module_route)

        # TODO 2: 拦截器，所有请求先经过这里，可以获取请求头token进行拦截
        exclude_path_patterns_list = [
            "/login",
            "/refresh",  # token 刷新接口不需要验证
            "/ApiReportViewer",
        ]
        @application.before_request
        def my_before_request():
            """
            拦截器，所有请求先经过这里，可以获取请求头token进行拦截
            """
            # 获取路径
            url = request.path
            url = '/' + url.split('/')[1]
            print(f"[拦截器] 请求路径: {request.path} -> 提取路径: {url}")
            if url in exclude_path_patterns_list or request.method == "OPTIONS":
                print(f"[拦截器] 路径在白名单中，跳过验证")
                return
            elif url.endswith("callback") or url.endswith("result"):  # 如果是回调 不检查是否登录，检查callback_key
                callback_key = request.headers.get("Callbackkey", None)
                if (callback_key is None or callback_key != application.config["SECRET_KEY"]):
                    return respModel.error_resp(f"当前用户未登录或者token失效"),401
                    # abort(401)
                return
            try:
                login_token = request.headers.get("token", None)
                print(f"[拦截器] Token: {login_token[:20] if login_token else 'None'}...")
                if (login_token is None):
                    print(f"[拦截器] Token 为空，返回 401")
                    return respModel.error_resp(f"当前用户未登录或者token失效"), 401
                    # abort(401)
                # JWT 验证成功，解析 JWT 中的内容
                from core.JwtUtil import JwtUtils
                content = JwtUtils.verify_token(login_token)
                print(f"[拦截器] Token 验证成功，用户: {content.get('username')}")
                # 将获取到的信息保存到全局上下文中
                setattr(g, "username", content.get('username'))
            except Exception as e:
                print(f"[拦截器] Token 验证失败: {e}")
                return respModel.error_resp(f"当前用户未登录或者token失效"), 401
                # abort(401)

        @application.context_processor
        def my_context_processor():
            """
            上下文对象，可以保存全局变量
            """
            return {"username": g.username}

        # TODO 3: 启动MQ消费者（可选，失败不影响主服务）
        try:
            from core.RabbitMQ_Consumer import RabbitMQManager
            RabbitMQManager().start_workers()
            print("✓ RabbitMQ 消费者启动成功")
        except Exception as mq_error:
            print(f"⚠ RabbitMQ 消费者启动失败（不影响主服务）: {mq_error}")
            print("  提示：如需使用消息队列功能，请确保 RabbitMQ 服务已启动")

        sys.exit(application.run(debug=True, host='0.0.0.0', port=5000))
    except Exception as e:
        import traceback
        # 打印完整的错误信息
        traceback.print_exc()
