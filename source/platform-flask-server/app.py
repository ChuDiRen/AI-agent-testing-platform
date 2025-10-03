# 镜像 ：  https://pypi.tuna.tsinghua.edu.cn/simple
# 准备的包： flask flask_sqlalchemy flask_script pymysql flask_cors
# flask == 2.0.2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_script import Manager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from core.MinioUtils import MinioUtils

# 创建 flask 实例
application = Flask(__name__)
application.config.from_pyfile('config/dev_settings.py')  # 加载配置

# 将minio_utils放入application中
minio_utils = MinioUtils(endpoint=application.config["MINIO_ENDPOINT"],access_key=application.config["MINIO_ACCESS_KEY"],secret_key=application.config["MINIO_SECRET_KEY"],secure=application.config["MINIO_SECURE"])
application.extensions["minio_utils"] = minio_utils

CORS(application, resources=r'/*')
database = SQLAlchemy()
database.init_app(application)
jwt = JWTManager()  # jwt 用来生成token
jwt.init_app(application)

# 启动程序
if __name__ == '__main__':
    try:
        # 注册模块的接口路由信息
        from login.api import LoginController
        application.register_blueprint(LoginController.module_route)

        from sysmanage.api import UserController
        application.register_blueprint(UserController.module_route)

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


        # 启动程序
        import sys

        sys.exit(application.run())
    except Exception as e:
        import traceback
        traceback.print_exc()
