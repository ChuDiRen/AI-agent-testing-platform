from flask import Blueprint, request, jsonify
from app import database, application
from login.model.UserModel import User

# TODO 0: 导入生成token的jwt
from core.JwtUtil import JwtUtils
from core.resp_model import respModel


# 用途：定义一个独立的“路由容器”，后续可将所有路由挂载到主应用。
# route_login：唯一名称（用于内部标识）。
# __name__：当前模块的名称（用于定位资源文件路径）。
module_route = Blueprint("route_login", __name__)

# @module_route.route("/login", methods=["POST"])
# def login():
#     with application.app_context():
#         data = request.get_json()
#         username = data.get("username")
#         password = data.get("password")
#         user = User.query.filter_by(username=username, password=password).first()
#     if user:
#         # TODO 1: 如果有用户，那么就生成对应的token
#         token = JwtUtils.create_token(username=username, password=password)
#         return respModel().ok_resp(obj=user, msg="登录成功", dic_t={"token": token})
#     else:
#         # 步骤3：如果未查询到用户，则返回登录失败
#         return respModel().error_resp("登录失败，用户名或密码错误")


@module_route.route("/login", methods=["POST"])
def login():
    with application.app_context():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        # 步骤2：参数校验（非空判断）
        if not username or not password:
            return respModel().error_resp(msg="用户名或密码不能为空")

        # 步骤3：查询数据库中的用户
        user = User.query.filter_by(username=username).first()  # 按用户名查询
        if not user:
            return respModel().error_resp(msg="用户名不存在")

        # 步骤4：验证密码
        if not user.check_password(password):
            return respModel().error_resp(msg="密码错误")

        # 步骤5：验证通过，返回成功结果（后续可扩展token生成）
        # TODO 1: 如果有用户，那么就生成对应的token
        token = JwtUtils.create_token(username=username, password=password)
        return respModel().ok_resp(obj=user, msg="登录成功", dic_t={"token": token})
   
