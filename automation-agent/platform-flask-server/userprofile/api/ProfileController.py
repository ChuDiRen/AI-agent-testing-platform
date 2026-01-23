from flask import Blueprint, request, g
from core.resp_model import respModel
from app import application, database
from login.model.UserModel import User

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
            
            # 从数据库查询用户信息
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 查询用户统计数据（这里可以根据实际业务逻辑查询）
            # 暂时使用模拟数据，后续可以从相关表查询
            from apitest.model.ApiInfoCaseModel import ApiInfoCase
            from apitest.model.ApiProjectModel import ApiProject
            
            # 统计用例数量
            case_count = ApiInfoCase.query.filter_by().count() if hasattr(ApiInfoCase, 'query') else 0
            
            # 统计项目数量
            project_count = ApiProject.query.filter_by().count() if hasattr(ApiProject, 'query') else 0
            
            user_info = {
                "id": user.id,
                "username": user.username,
                "alias": user.alias or user.username,
                "email": user.email,
                "phone": user.phone or "",
                "department": "",  # 需要关联部门表
                "position": "",
                "bio": "",
                "role": "超级管理员" if user.is_superuser else "普通用户",
                "avatar": "",
                "testCount": 0,  # 需要从测试执行记录表统计
                "caseCount": case_count,
                "projectCount": project_count,
                "isActive": user.is_active,
                "lastLogin": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else ""
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
            
            # 从数据库查询用户
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 更新允许修改的字段
            if 'alias' in data:
                user.alias = data['alias']
            if 'email' in data:
                # 检查邮箱是否已被其他用户使用
                existing_user = User.query.filter(User.email == data['email'], User.id != user.id).first()
                if existing_user:
                    return respModel().error_resp(msg="该邮箱已被使用"), 400
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            
            # 提交更新
            database.session.commit()
            
            return respModel().ok_resp(msg="更新成功")
            
        except Exception as e:
            database.session.rollback()
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
            
            # 从数据库查询用户
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return respModel().error_resp(msg="用户不存在"), 404
            
            # 验证旧密码
            if not user.check_password(old_password):
                return respModel().error_resp(msg="当前密码不正确"), 400
            
            # 更新新密码
            user.password = user.set_password(new_password)
            database.session.commit()
            
            return respModel().ok_resp(msg="密码修改成功")
            
        except Exception as e:
            database.session.rollback()
            return respModel().error_resp(msg=f"修改失败: {str(e)}"), 500
