from flask import Blueprint, request
from app import database, application
from sysmanage.model.user import User
from core.JwtUtil import JwtUtils
from core.resp_model import respModel

module_route = Blueprint("route_login", __name__)


@module_route.route("/login", methods=["POST"])
def login():
    with application.app_context():
        user = User.query.filter_by(username=request.json["username"], password=request.json["password"]).first()
    if user:
        token = JwtUtils.create_token(request.json["username"], request.json["password"])
        return respModel().ok_resp(obj=user, msg="登录成功", dic_t={"token": token})
    else:
        return respModel().error_resp("登录失败，用户名或密码错误")
