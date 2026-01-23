from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
from datetime import datetime

from sysmanage.model.ApiModel import Api

module_name = "api"
module_model = Api
module_route = Blueprint(f"route_{module_name}", __name__)


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    """ 查询数据(支持模糊搜索) """
    try:
        page = int(request.json.get("page", 1))
        page_size = int(request.json.get("pageSize", 10))
        with application.app_context():
            filter_list = []
            path = request.json.get("path", "")
            if len(path) > 0:
                filter_list.append(module_model.path.like(f"%{path}%"))

            method = request.json.get("method", "")
            if len(method) > 0:
                filter_list.append(module_model.method == method)

            tags = request.json.get("tags", "")
            if len(tags) > 0:
                filter_list.append(module_model.tags.like(f"%{tags}%"))

            datas = module_model.query.filter(*filter_list).limit(page_size).offset((page - 1) * page_size).all()
            total = module_model.query.filter(*filter_list).count()
            return respModel().ok_resp_list(lst=datas, total=total, msg="查询成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    """ 查询数据(单条记录) """
    try:
        data_id = int(request.args.get("id"))
        with application.app_context():
            data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data, msg="查询成功")
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    """ 新增数据 """
    try:
        with application.app_context():
            request.json["id"] = None
            data = module_model(**request.json)
            database.session.add(data)
            database.session.flush()
            data_id = data.id
            database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    """ 修改数据 """
    try:
        with application.app_context():
            module_model.query.filter_by(id=request.json["id"]).update(request.json)
            database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    """ 删除数据 """
    try:
        with application.app_context():
            module_model.query.filter_by(id=request.args.get("id")).delete()
            database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.route(f"/{module_name}/refresh", methods=["POST"])
def refresh_api():
    """ 刷新API列表,扫描所有需要权限验证的路由 """
    try:
        # 排除的精确路径（不需要权限验证的路由）
        exclude_exact_paths = ['/login', '/refresh']
        # 排除的路径前缀
        exclude_prefix_paths = ['/ApiReportViewer']
        
        # 获取所有需要权限验证的路由
        all_routes = []
        print(f"[刷新API] 开始扫描路由...")
        print(f"[刷新API] 排除精确路径: {exclude_exact_paths}")
        print(f"[刷新API] 排除前缀路径: {exclude_prefix_paths}")
        
        # 使用 Flask 的 current_app 来获取当前应用实例
        from flask import current_app
        total_rules = 0
        print(f"[刷新API] 当前应用的蓝图: {list(current_app.blueprints.keys())}")
        print(f"[刷新API] URL映射规则总数: {len(list(current_app.url_map.iter_rules()))}")
        
        for rule in current_app.url_map.iter_rules():
            total_rules += 1
            path = str(rule)
            
            # 跳过静态文件
            if rule.endpoint == 'static':
                print(f"[刷新API] 跳过静态文件: {path}")
                continue
                
            # 跳过精确匹配的公开路由
            if path in exclude_exact_paths:
                print(f"[刷新API] 跳过精确匹配: {path}")
                continue
                
            # 跳过以特定前缀开头的路由
            if any(path.startswith(prefix) for prefix in exclude_prefix_paths):
                print(f"[刷新API] 跳过前缀匹配: {path}")
                continue
            
            for method in rule.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    # 获取路由对应的视图函数
                    view_func = current_app.view_functions.get(rule.endpoint)
                    summary = view_func.__doc__.strip() if view_func and view_func.__doc__ else ""
                    
                    # 从 endpoint 提取 tags
                    tags = rule.endpoint.split('_')[1] if '_' in rule.endpoint else "Other"
                    
                    route_info = {
                        "path": path,
                        "method": method,
                        "summary": summary,
                        "tags": tags
                    }
                    all_routes.append(route_info)
                    print(f"[刷新API] 添加路由: {method} {path} - {summary[:30] if summary else 'No description'}")
        
        print(f"[刷新API] 总共扫描 {total_rules} 个规则，筛选出 {len(all_routes)} 个需要权限验证的路由")
        
        # 删除废弃的API
        with application.app_context():
            existing_apis = Api.query.all()
            deleted_count = 0
            for api in existing_apis:
                route_exists = any(
                    r["path"] == api.path and r["method"] == api.method 
                    for r in all_routes
                )
                if not route_exists:
                    print(f"[刷新API] 删除废弃API: {api.method} {api.path}")
                    database.session.delete(api)
                    deleted_count += 1
            
            # 更新或创建新API
            updated_count = 0
            created_count = 0
            for route in all_routes:
                api = Api.query.filter_by(
                    path=route["path"],
                    method=route["method"]
                ).first()
                
                if api:
                    # 更新现有API
                    api.summary = route["summary"]
                    api.tags = route["tags"]
                    updated_count += 1
                else:
                    # 创建新API
                    print(f"[刷新API] 创建新API: {route['method']} {route['path']}")
                    new_api = Api(
                        path=route["path"],
                        method=route["method"],
                        summary=route["summary"],
                        tags=route["tags"]
                    )
                    database.session.add(new_api)
                    created_count += 1
            
            database.session.commit()
            msg = f"刷新成功！共扫描{len(all_routes)}个API，创建{created_count}个，更新{updated_count}个，删除{deleted_count}个"
            print(f"[刷新API] {msg}")
            return respModel.ok_resp(msg=msg)
    except Exception as e:
        print(f"[刷新API] 失败: {e}")
        import traceback
        traceback.print_exc()
        return respModel.error_resp(msg=f"刷新失败：{e}")
