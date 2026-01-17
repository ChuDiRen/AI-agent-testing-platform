from flask import Blueprint, request, g
from core.resp_model import respModel
from app import application

# 创建蓝图
module_route = Blueprint('profile', __name__, url_prefix='/api/profile')

@module_route.route("", methods=["GET"])
def get_profile():
    """
    获取用户个人信息
    """
    with application.app_context():
        try:
            # 从全局上下文获取用户名（拦截器已验证）
            username = g.get('username')
            
            # 这里应该从数据库查询用户信息
            # 暂时返回模拟数据
            user_info = {
                "username": username,
                "email": f"{username}@example.com",
                "phone": "13800138000",
                "department": "技术部",
                "position": "测试工程师",
                "bio": "专注于自动化测试",
                "role": "Admin",
                "avatar": "",
                "testCount": 156,
                "caseCount": 89,
                "projectCount": 12
            }
            
            return respModel().ok_resp(obj=user_info, msg="获取成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"获取失败: {str(e)}"), 500


@module_route.route("", methods=["PUT"])
def update_profile():
    """
    更新用户个人信息
    """
    with application.app_context():
        try:
            # 从全局上下文获取用户名（拦截器已验证）
            username = g.get('username')
            
            # 获取请求数据
            data = request.get_json()
            
            # 这里应该更新数据库中的用户信息
            # 暂时只返回成功消息
            
            return respModel().ok_resp(msg="更新成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"更新失败: {str(e)}"), 500


@module_route.route("/change-password", methods=["POST"])
def change_password():
    """
    修改密码
    """
    with application.app_context():
        try:
            # 从全局上下文获取用户名（拦截器已验证）
            username = g.get('username')
            
            # 获取请求数据
            data = request.get_json()
            old_password = data.get("oldPassword")
            new_password = data.get("newPassword")
            
            if not old_password or not new_password:
                return respModel().error_resp(msg="密码不能为空"), 400
            
            # 这里应该验证旧密码并更新新密码
            # 暂时只返回成功消息
            
            return respModel().ok_resp(msg="密码修改成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"修改失败: {str(e)}"), 500
