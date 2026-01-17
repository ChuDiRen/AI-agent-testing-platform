from flask import Blueprint, request, g
from core.resp_model import respModel
from app import application

# 创建蓝图
module_route = Blueprint('settings', __name__, url_prefix='/api/settings')

# 模拟的设置数据存储
settings_data = {
    "basic": {
        "systemName": "API 自动化测试平台",
        "systemDesc": "专业的接口测试管理解决方案",
        "language": "zh-CN",
        "timezone": "Asia/Shanghai"
    },
    "test": {
        "defaultTimeout": 30,
        "maxRetries": 3,
        "concurrency": 5,
        "continueOnFailure": True,
        "autoGenerateReport": True
    },
    "notification": {
        "emailEnabled": False,
        "wechatEnabled": True,
        "dingdingEnabled": False,
        "feishuEnabled": False,
        "notifyOn": ["failure", "error"]
    },
    "security": {
        "sessionTimeout": 30,
        "passwordStrength": "medium",
        "loginLockEnabled": True,
        "maxLoginAttempts": 5
    }
}


@module_route.route("", methods=["GET"])
def get_settings():
    """
    获取所有系统设置
    """
    with application.app_context():
        try:
            return respModel().ok_resp(obj=settings_data, msg="获取成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"获取失败: {str(e)}"), 500


@module_route.route("/basic", methods=["PUT"])
def update_basic_settings():
    """
    更新基础设置
    """
    with application.app_context():
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 更新设置
            settings_data["basic"].update(data)
            
            return respModel().ok_resp(msg="基础设置保存成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"保存失败: {str(e)}"), 500


@module_route.route("/test", methods=["PUT"])
def update_test_settings():
    """
    更新测试设置
    """
    with application.app_context():
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 更新设置
            settings_data["test"].update(data)
            
            return respModel().ok_resp(msg="测试设置保存成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"保存失败: {str(e)}"), 500


@module_route.route("/notification", methods=["PUT"])
def update_notification_settings():
    """
    更新通知设置
    """
    with application.app_context():
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 更新设置
            settings_data["notification"].update(data)
            
            return respModel().ok_resp(msg="通知设置保存成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"保存失败: {str(e)}"), 500


@module_route.route("/security", methods=["PUT"])
def update_security_settings():
    """
    更新安全设置
    """
    with application.app_context():
        try:
            # 获取请求数据
            data = request.get_json()
            
            # 更新设置
            settings_data["security"].update(data)
            
            return respModel().ok_resp(msg="安全设置保存成功")
            
        except Exception as e:
            return respModel().error_resp(msg=f"保存失败: {str(e)}"), 500
