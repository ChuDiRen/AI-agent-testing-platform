"""
API文档Controller
提供API文档的生成、预览、导出等功能
"""
import json
from datetime import datetime
from typing import List

from apitest.service.api_doc_service import DocService
from apitest.model.ApiFolderModel import ApiFolder
from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiProjectModel import ApiProject
from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlmodel import Session, select

module_name = "ApiDoc"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API文档管理"])


@module_route.get("/generate", summary="生成API文档",
                  dependencies=[Depends(check_permission("apitest:api:query"))])
async def generate_doc(project_id: int = Query(..., description="项目ID"),
                       format: str = Query("json", description="格式: json/markdown/html"),
                       session: Session = Depends(get_session)):
    """生成项目的API文档"""
    # 查询项目信息
    project = session.get(ApiProject, project_id)
    if not project:
        return respModel.error_resp(msg="项目不存在")
    
    # 查询所有目录
    folders = session.exec(
        select(ApiFolder).where(ApiFolder.project_id == project_id)
        .order_by(ApiFolder.sort_order)
    ).all()
    
    # 查询所有接口
    apis = session.exec(
        select(ApiInfo).where(ApiInfo.project_id == project_id)
        .order_by(ApiInfo.id)
    ).all()
    
    # 构建文档数据
    doc_data = build_doc_data(project, folders, apis)
    
    if format == "markdown":
        content = generate_markdown(doc_data)
        return PlainTextResponse(content, media_type="text/markdown")
    elif format == "html":
        content = generate_html(doc_data)
        return HTMLResponse(content)
    else:
        return respModel.ok_resp(dic_t=doc_data)


@module_route.get("/preview", summary="预览API文档",
                  dependencies=[Depends(check_permission("apitest:api:query"))])
async def preview_doc(project_id: int = Query(..., description="项目ID"),
                      session: Session = Depends(get_session)):
    """预览项目的API文档（HTML格式）"""
    project = session.get(ApiProject, project_id)
    if not project:
        return HTMLResponse("<h1>项目不存在</h1>", status_code=404)
    
    folders = session.exec(
        select(ApiFolder).where(ApiFolder.project_id == project_id)
        .order_by(ApiFolder.sort_order)
    ).all()
    
    apis = session.exec(
        select(ApiInfo).where(ApiInfo.project_id == project_id)
        .order_by(ApiInfo.id)
    ).all()
    
    doc_data = build_doc_data(project, folders, apis)
    html_content = generate_html(doc_data)
    
    return HTMLResponse(html_content)


@module_route.get("/export", summary="导出API文档",
                  dependencies=[Depends(check_permission("apitest:api:query"))])
async def export_doc(project_id: int = Query(..., description="项目ID"),
                     format: str = Query("markdown", description="格式: markdown/json/openapi"),
                     session: Session = Depends(get_session)):
    """导出项目的API文档"""
    project = session.get(ApiProject, project_id)
    if not project:
        return respModel.error_resp(msg="项目不存在")
    
    folders = session.exec(
        select(ApiFolder).where(ApiFolder.project_id == project_id)
        .order_by(ApiFolder.sort_order)
    ).all()
    
    apis = session.exec(
        select(ApiInfo).where(ApiInfo.project_id == project_id)
        .order_by(ApiInfo.id)
    ).all()
    
    doc_data = build_doc_data(project, folders, apis)
    
    if format == "openapi":
        content = generate_openapi(doc_data)
        return respModel.ok_resp(dic_t=content)
    elif format == "markdown":
        content = generate_markdown(doc_data)
        return respModel.ok_resp(dic_t={"content": content, "filename": f"{project.project_name}_API文档.md"})
    else:
        return respModel.ok_resp(dic_t=doc_data)


@module_route.get("/getApiDetail", summary="获取接口详情文档",
                  dependencies=[Depends(check_permission("apitest:api:query"))])
async def get_api_detail(api_id: int = Query(..., description="接口ID"),
                         session: Session = Depends(get_session)):
    """获取单个接口的详细文档"""
    api = session.get(ApiInfo, api_id)
    if not api:
        return respModel.error_resp(msg="接口不存在")
    
    detail = build_api_detail(api)
    return respModel.ok_resp(dic_t=detail)


def build_doc_data(project: ApiProject, folders: List[ApiFolder], apis: List[ApiInfo]) -> dict:
    """构建文档数据结构"""
    # 创建目录映射
    folder_map = {f.id: {"id": f.id, "name": f.folder_name, "apis": []} for f in folders}
    folder_map[0] = {"id": 0, "name": "未分组", "apis": []}
    
    # 将接口分配到目录
    for api in apis:
        folder_id = api.folder_id if api.folder_id else 0
        if folder_id not in folder_map:
            folder_id = 0
        
        api_doc = build_api_detail(api)
        folder_map[folder_id]["apis"].append(api_doc)
    
    # 构建目录结构
    categories = []
    for folder in folders:
        if folder_map[folder.id]["apis"]:
            categories.append(folder_map[folder.id])
    
    # 添加未分组的接口
    if folder_map[0]["apis"]:
        categories.append(folder_map[0])
    
    return {
        "project": {
            "id": project.id,
            "name": project.project_name,
            "description": project.project_desc,
            "create_time": str(project.create_time) if project.create_time else None
        },
        "categories": categories,
        "api_count": len(apis),
        "generate_time": datetime.now().isoformat()
    }


def build_api_detail(api: ApiInfo) -> dict:
    """构建单个接口的详细文档"""
    # 解析请求参数
    params = []
    if api.request_params:
        try:
            params = json.loads(api.request_params)
        except:
            pass
    
    # 解析请求头
    headers = []
    if api.request_headers:
        try:
            headers = json.loads(api.request_headers)
        except:
            pass
    
    # 解析请求体
    body = None
    body_type = None
    if api.requests_json_data:
        body = api.requests_json_data
        body_type = "json"
    elif api.request_form_datas:
        try:
            body = json.loads(api.request_form_datas)
            body_type = "form-data"
        except:
            pass
    elif api.request_www_form_datas:
        try:
            body = json.loads(api.request_www_form_datas)
            body_type = "x-www-form-urlencoded"
        except:
            pass
    
    return {
        "id": api.id,
        "name": api.api_name,
        "method": api.request_method,
        "url": api.request_url,
        "params": params,
        "headers": headers,
        "body": body,
        "body_type": body_type
    }


def generate_markdown(doc_data: dict) -> str:
    """生成Markdown格式文档"""
    lines = []
    project = doc_data["project"]
    
    # 标题
    lines.append(f"# {project['name']} API文档\n")
    if project.get("description"):
        lines.append(f"{project['description']}\n")
    lines.append(f"生成时间: {doc_data['generate_time']}\n")
    lines.append(f"接口总数: {doc_data['api_count']}\n")
    lines.append("---\n")
    
    # 目录
    lines.append("## 目录\n")
    for cat in doc_data["categories"]:
        lines.append(f"- [{cat['name']}](#{cat['name'].replace(' ', '-')})")
        for api in cat["apis"]:
            lines.append(f"  - [{api['method']} {api['name']}](#{api['name'].replace(' ', '-')})")
    lines.append("\n---\n")
    
    # 接口详情
    for cat in doc_data["categories"]:
        lines.append(f"## {cat['name']}\n")
        
        for api in cat["apis"]:
            lines.append(f"### {api['name']}\n")
            lines.append(f"**请求方式:** `{api['method']}`\n")
            lines.append(f"**请求地址:** `{api['url']}`\n")
            
            # 请求参数
            if api.get("params"):
                lines.append("\n**Query参数:**\n")
                lines.append("| 参数名 | 类型 | 必填 | 说明 |")
                lines.append("|--------|------|------|------|")
                for p in api["params"]:
                    required = "是" if p.get("required") else "否"
                    lines.append(f"| {p.get('key', '')} | {p.get('type', 'string')} | {required} | {p.get('description', '')} |")
            
            # 请求头
            if api.get("headers"):
                lines.append("\n**请求头:**\n")
                lines.append("| Header | 值 |")
                lines.append("|--------|-----|")
                for h in api["headers"]:
                    lines.append(f"| {h.get('key', '')} | {h.get('value', '')} |")
            
            # 请求体
            if api.get("body"):
                lines.append(f"\n**请求体 ({api.get('body_type', 'json')}):**\n")
                if isinstance(api["body"], str):
                    lines.append(f"```json\n{api['body']}\n```")
                else:
                    lines.append(f"```json\n{json.dumps(api['body'], ensure_ascii=False, indent=2)}\n```")
            
            lines.append("\n---\n")
    
    return "\n".join(lines)


def generate_html(doc_data: dict) -> str:
    """生成HTML格式文档"""
    project = doc_data["project"]
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['name']} API文档</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; margin-bottom: 30px; border-radius: 8px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .meta {{ display: flex; gap: 20px; margin-top: 15px; font-size: 0.9em; opacity: 0.8; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 280px; height: 100vh; background: #f8f9fa; border-right: 1px solid #e9ecef; overflow-y: auto; padding: 20px; }}
        .sidebar h3 {{ margin-bottom: 15px; color: #495057; }}
        .sidebar ul {{ list-style: none; }}
        .sidebar li {{ margin-bottom: 5px; }}
        .sidebar a {{ color: #495057; text-decoration: none; display: block; padding: 5px 10px; border-radius: 4px; }}
        .sidebar a:hover {{ background: #e9ecef; }}
        .content {{ margin-left: 300px; }}
        .category {{ margin-bottom: 40px; }}
        .category h2 {{ color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        .api-card {{ background: white; border: 1px solid #e9ecef; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }}
        .api-header {{ padding: 15px 20px; background: #f8f9fa; border-bottom: 1px solid #e9ecef; display: flex; align-items: center; gap: 15px; }}
        .method {{ padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 0.85em; color: white; }}
        .method.GET {{ background: #28a745; }}
        .method.POST {{ background: #ffc107; color: #333; }}
        .method.PUT {{ background: #17a2b8; }}
        .method.DELETE {{ background: #dc3545; }}
        .method.PATCH {{ background: #6c757d; }}
        .api-name {{ font-weight: 600; font-size: 1.1em; }}
        .api-url {{ color: #6c757d; font-family: monospace; }}
        .api-body {{ padding: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .section h4 {{ color: #495057; margin-bottom: 10px; font-size: 0.95em; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e9ecef; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>📚 目录</h3>
        <ul>
"""
    
    # 侧边栏目录
    for cat in doc_data["categories"]:
        html += f'<li><strong>{cat["name"]}</strong><ul>'
        for api in cat["apis"]:
            html += f'<li><a href="#api-{api["id"]}">{api["method"]} {api["name"]}</a></li>'
        html += '</ul></li>'
    
    html += f"""
        </ul>
    </div>
    <div class="content">
        <div class="container">
            <div class="header">
                <h1>📖 {project['name']}</h1>
                <p>{project.get('description', '')}</p>
                <div class="meta">
                    <span>📊 接口总数: {doc_data['api_count']}</span>
                    <span>🕐 生成时间: {doc_data['generate_time'][:19]}</span>
                </div>
            </div>
"""
    
    # 接口详情
    for cat in doc_data["categories"]:
        html += f'<div class="category"><h2>{cat["name"]}</h2>'
        
        for api in cat["apis"]:
            html += f'''
            <div class="api-card" id="api-{api["id"]}">
                <div class="api-header">
                    <span class="method {api["method"]}">{api["method"]}</span>
                    <span class="api-name">{api["name"]}</span>
                    <span class="api-url">{api["url"]}</span>
                </div>
                <div class="api-body">
'''
            
            # 参数表格
            if api.get("params"):
                html += '<div class="section"><h4>Query 参数</h4><table>'
                html += '<tr><th>参数名</th><th>类型</th><th>必填</th><th>说明</th></tr>'
                for p in api["params"]:
                    required = "是" if p.get("required") else "否"
                    html += f'<tr><td>{p.get("key", "")}</td><td>{p.get("type", "string")}</td><td>{required}</td><td>{p.get("description", "")}</td></tr>'
                html += '</table></div>'
            
            # 请求头
            if api.get("headers"):
                html += '<div class="section"><h4>请求头</h4><table>'
                html += '<tr><th>Header</th><th>值</th></tr>'
                for h in api["headers"]:
                    html += f'<tr><td>{h.get("key", "")}</td><td>{h.get("value", "")}</td></tr>'
                html += '</table></div>'
            
            # 请求体
            if api.get("body"):
                body_str = api["body"] if isinstance(api["body"], str) else json.dumps(api["body"], ensure_ascii=False, indent=2)
                html += f'<div class="section"><h4>请求体 ({api.get("body_type", "json")})</h4><pre>{body_str}</pre></div>'
            
            html += '</div></div>'
        
        html += '</div>'
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html


def generate_openapi(doc_data: dict) -> dict:
    """生成OpenAPI 3.0格式文档"""
    project = doc_data["project"]
    
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": project["name"],
            "description": project.get("description", ""),
            "version": "1.0.0"
        },
        "paths": {}
    }
    
    for cat in doc_data["categories"]:
        for api in cat["apis"]:
            path = api["url"]
            method = api["method"].lower()
            
            if path not in openapi["paths"]:
                openapi["paths"][path] = {}
            
            operation = {
                "summary": api["name"],
                "tags": [cat["name"]],
                "responses": {
                    "200": {
                        "description": "成功响应"
                    }
                }
            }
            
            # 添加参数
            if api.get("params"):
                operation["parameters"] = []
                for p in api["params"]:
                    operation["parameters"].append({
                        "name": p.get("key", ""),
                        "in": "query",
                        "required": p.get("required", False),
                        "schema": {"type": p.get("type", "string")},
                        "description": p.get("description", "")
                    })
            
            # 添加请求体
            if api.get("body") and method in ["post", "put", "patch"]:
                operation["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            
            openapi["paths"][path][method] = operation
    
    return openapi
