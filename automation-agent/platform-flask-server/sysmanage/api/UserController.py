from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime
from core.PermissionMiddleware import api_permission_required

# 这里我们引用对应的Model，因为我们登录和管理用的是同一个表，所以我么这个位置直接引用对应Model
from login.model.UserModel import User
from sysmanage.model.RoleApiModel import RoleApi
from sysmanage.model.UserRoleModel import UserRole
from sysmanage.model.RoleModel import Role
from sysmanage.model.DeptModel import Dept

# 模块信息
module_name = "user"  # 模块名称
module_model = User
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
@api_permission_required()
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        # 安全获取JSON数据
        json_data = request.get_json(silent=True)
        if not json_data:
            return respModel.error_resp("请求数据格式错误")

        # 分页查询
        page = int(json_data.get("page", 0))
        page_size = int(json_data.get("pageSize", 10))
        with application.app_context():
            filter_list = []
            # 用户名筛选
            username = json_data.get("username", "")
            if len(username) > 0:
               filter_list.append(module_model.username.like(f"%{username}%"))
            
            # 邮箱筛选
            email = json_data.get("email", "")
            if len(email) > 0:
                filter_list.append(module_model.email.like(f"%{email}%"))
            
            # 部门筛选
            dept_id = json_data.get("dept_id")
            if dept_id is not None:
                filter_list.append(module_model.dept_id == dept_id)

            # 数据库查询
            users = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
            
            # 构建返回数据,包含角色和部门信息
            result = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "username": user.username,
                    "alias": user.alias,
                    "email": user.email,
                    "phone": user.phone,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                    "dept_id": user.dept_id,
                    "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                    "updated_at": user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else None,
                }
                
                # 获取用户角色
                roles = user.roles.all() if hasattr(user, 'roles') else []
                user_dict["roles"] = [{
                    "id": role.id,
                    "name": role.name,
                    "desc": role.desc
                } for role in roles]
                
                # 获取部门信息
                if user.dept_id:
                    dept = Dept.query.get(user.dept_id)
                    if dept:
                        user_dict["dept"] = {
                            "id": dept.id,
                            "name": dept.name,
                            "desc": dept.desc
                        }
                    else:
                        user_dict["dept"] = {}
                else:
                    user_dict["dept"] = {}
                
                result.append(user_dict)
            
            return respModel().ok_resp_list(lst=result, total=total, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        # 安全获取id参数
        id_param = request.args.get("id")
        if not id_param:
            return respModel.error_resp(msg="缺少ID参数")

        try:
            data_id = int(id_param)
        except ValueError:
            return respModel.error_resp(msg="ID格式错误")

        with application.app_context():
            # 数据库查询
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            # 直接查询用户角色（避免lazy loading的上下文问题）
            with application.app_context():
                from sysmanage.model.UserRoleModel import UserRole
                from sysmanage.model.RoleModel import Role
                
                user_roles = database.session.query(Role).join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == data_id).all()
                roles = [{"id": role.id, "name": role.name, "desc": role.desc} for role in user_roles]
                
                # 获取部门信息
                dept = None
                if data.dept_id:
                    dept = Dept.query.get(data.dept_id)
            
            # 构建返回数据,包含角色和部门信息（与queryByPage保持一致的格式）
            user_dict = {
                "id": data.id,
                "username": data.username,
                "alias": data.alias,
                "email": data.email,
                "phone": data.phone,
                "is_active": data.is_active,
                "is_superuser": data.is_superuser,
                "last_login": data.last_login.strftime('%Y-%m-%d %H:%M:%S') if data.last_login else None,
                "dept_id": data.dept_id,
                "created_at": data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else None,
                "updated_at": data.updated_at.strftime('%Y-%m-%d %H:%M:%S') if data.updated_at else None,
                "roles": roles,
                "dept": {
                    "id": dept.id,
                    "name": dept.name,
                    "desc": dept.desc
                } if dept else {}
            }
            
            return respModel().ok_resp(obj=user_dict, msg="查询成功")
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        # 安全获取JSON数据
        json_data = request.get_json(silent=True)
        if not json_data:
            return respModel.error_resp("请求数据格式错误")

        with application.app_context():
            username = json_data.get("username")
            password = json_data.get("password")

            # 验证必填字段
            if not username or not password:
                return respModel.error_resp("用户名和密码不能为空")

            # 检查用户名是否已存在
            if module_model.query.filter_by(username=username).first():
                return respModel.error_resp(msg="用户名已存在")

            # 如果没有提供email，使用默认值
            email = json_data.get("email")
            if not email:
                email = f"{username}@local.com"

            # 密码进行加密处理
            hashed_password = module_model().set_password(password)

            # 构建用户数据
            user_data = {
                "username": username,
                "password": hashed_password,
                "email": email,
                "alias": json_data.get("alias"),
                "phone": json_data.get("phone"),
                "is_active": json_data.get("is_active", True),
                "is_superuser": json_data.get("is_superuser", False),
                "dept_id": json_data.get("dept_id"),
                "created_at": datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
            }

            data = module_model(**user_data)
            database.session.add(data)
            # 获取新增后的ID并返回
            database.session.flush()
            data_id = data.id
            
            # 处理角色关联
            role_ids = json_data.get("role_ids", [])
            if role_ids:
                for role_id in role_ids:
                    role = Role.query.get(role_id)
                    if role:
                        data.roles.append(role)
            
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
@api_permission_required()
def update():
    """ 修改数据 """
    try:
        # 安全获取JSON数据
        json_data = request.get_json(silent=True)
        if not json_data:
            return respModel.error_resp("请求数据格式错误")

        with application.app_context():
            user_id = json_data.get("id")
            username = json_data.get("username")
            password = json_data.get("password")

            # 验证必填字段
            if not user_id or not username:
                return respModel.error_resp("用户ID和用户名不能为空")

            # 修改的用户名不能是数据库存在的用户名
            user = module_model.query.filter_by(username=username).first()
            if user and user.id != user_id:
                return respModel.error_resp(msg="用户名已存在")

            # 构建更新数据
            update_data = {
                "username": username,
                "email": json_data.get("email"),
                "alias": json_data.get("alias"),
                "phone": json_data.get("phone"),
                "is_active": json_data.get("is_active", True),
                "is_superuser": json_data.get("is_superuser", False),
                "dept_id": json_data.get("dept_id")
            }

            # 如果提供了密码，进行加密处理
            if password:
                update_data["password"] = module_model().set_password(password)

            user = module_model.query.filter_by(id=user_id).first()
            if not user:
                return respModel.error_resp(msg="用户不存在")
            
            # 更新用户基本信息
            for key, value in update_data.items():
                if value is not None:
                    setattr(user, key, value)
            
            # 处理角色关联
            role_ids = json_data.get("role_ids")
            if role_ids is not None:
                user.roles = []
                database.session.flush()
                for role_id in role_ids:
                    role = Role.query.get(role_id)
                    if role:
                        user.roles.append(role)
            
            database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
@api_permission_required()
def delete():
    """ 删除数据 """
    try:
        with application.app_context():
            # 安全获取id参数
            id_param = request.args.get("id")
            if not id_param:
                return respModel.error_resp(msg="缺少用户ID参数")

            try:
                user_id = int(id_param)
            except ValueError:
                return respModel.error_resp(msg="用户ID格式错误")

            # 禁止删除admin用户
            user = module_model.query.filter_by(id=user_id).first()
            if user and user.username == 'admin':
                return respModel.error_resp(msg="不能删除系统管理员账号")
            module_model.query.filter_by(id=user_id).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/resetPassword", methods=["POST"])
def reset_password():
    """ 重置用户密码 """
    try:
        json_data = request.get_json(silent=True)
        if not json_data:
            return respModel.error_resp("请求数据格式错误")
        
        with application.app_context():
            user_id = json_data.get("user_id")
            if not user_id:
                return respModel.error_resp(msg="用户ID不能为空")
            
            user = module_model.query.filter_by(id=user_id).first()
            if not user:
                return respModel.error_resp(msg="用户不存在")
            
            if user.is_superuser:
                return respModel.error_resp(msg="不允许重置超级管理员密码")
            
            # 重置密码为123456
            hashed_password = module_model().set_password("123456")
            user.password = hashed_password
            database.session.commit()
        
        return respModel.ok_resp(msg="密码已重置为123456")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"重置密码失败：{e}")
