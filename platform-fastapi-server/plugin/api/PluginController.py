"""
插件管理 API 控制器
提供插件注册、查询、启用/禁用等功能
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlmodel import Session, select, or_, func
from typing import List, Dict, Any
import httpx
import json
import time
import os
import shutil
import zipfile
import uuid
import re
import base64
import io
from pathlib import Path
from core.temp_manager import get_temp_subdir, remove_temp_dir
from datetime import datetime

from ..model.PluginModel import Plugin
from ..schemas.plugin_schema import (
    PluginCreate, PluginUpdate, PluginQuery, PluginResponse,
    PluginRegisterRequest, PluginHealthCheck
)
from core.database import get_session
from core.resp_model import respModel

# 创建路由
module_route = APIRouter(prefix="/Plugin", tags=["插件管理"])


@module_route.post("/register", summary="注册插件（插件自注册）")
async def register_plugin(
    request: PluginRegisterRequest,
    session: Session = Depends(get_session)
):
    """
    插件自注册接口
    插件启动时调用此接口注册到平台
    """
    try:
        # 解析请求数据
        plugin_data = request.plugin
        api_config = request.api
        
        # 检查插件是否已存在
        existing = session.exec(
            select(Plugin).where(Plugin.plugin_code == plugin_data.get("code"))
        ).first()
        
        if existing:
            # 更新现有插件
            existing.plugin_name = plugin_data.get("name")
            existing.version = plugin_data.get("version", "1.0.0")
            # existing.api_endpoint = api_config.get("endpoint") # 命令行插件不使用API地址
            existing.description = plugin_data.get("description")
            existing.author = plugin_data.get("author")
            existing.capabilities = json.dumps(request.capabilities) if request.capabilities else None
            existing.dependencies = json.dumps(request.requirements.get("dependencies", [])) if request.requirements else None
            
            session.add(existing)
            session.commit()
            session.refresh(existing)
            
            return respModel.ok_resp(obj={"id": existing.id}, msg="插件更新成功")
        else:
            # 创建新插件
            new_plugin = Plugin(
                plugin_name=plugin_data.get("name"),
                plugin_code=plugin_data.get("code"),
                plugin_type=plugin_data.get("type", "executor"),
                version=plugin_data.get("version", "1.0.0"),
                # api_endpoint=api_config.get("endpoint"),
                description=plugin_data.get("description"),
                author=plugin_data.get("author"),
                is_enabled=1,
                capabilities=json.dumps(request.capabilities) if request.capabilities else None,
                dependencies=json.dumps(request.requirements.get("dependencies", [])) if request.requirements else None
            )
            
            session.add(new_plugin)
            session.commit()
            session.refresh(new_plugin)
            
            return respModel.ok_resp(obj={"id": new_plugin.id}, msg="插件注册成功")
    
    except Exception as e:
        return respModel.error_resp(msg=f"插件注册失败: {str(e)}")


@module_route.post("/queryByPage", summary="分页查询插件列表")
async def query_by_page(
    query: PluginQuery,
    session: Session = Depends(get_session)
):
    """分页查询插件列表"""
    try:
        # 构建查询条件
        statement = select(Plugin)
        
        if query.plugin_name:
            statement = statement.where(Plugin.plugin_name.like(f"%{query.plugin_name}%"))
        if query.plugin_code:
            statement = statement.where(Plugin.plugin_code == query.plugin_code)
        if query.plugin_type:
            statement = statement.where(Plugin.plugin_type == query.plugin_type)
        if query.is_enabled is not None:
            statement = statement.where(Plugin.is_enabled == query.is_enabled)
        
        # 查询总数
        total_statement = select(func.count()).select_from(Plugin)
        if query.plugin_name:
            total_statement = total_statement.where(Plugin.plugin_name.like(f"%{query.plugin_name}%"))
        if query.plugin_code:
            total_statement = total_statement.where(Plugin.plugin_code == query.plugin_code)
        if query.plugin_type:
            total_statement = total_statement.where(Plugin.plugin_type == query.plugin_type)
        if query.is_enabled is not None:
            total_statement = total_statement.where(Plugin.is_enabled == query.is_enabled)
        
        total = session.exec(total_statement).one()
        
        # 分页查询
        offset = (query.pageNum - 1) * query.pageSize
        statement = statement.offset(offset).limit(query.pageSize)
        statement = statement.order_by(Plugin.create_time.desc())
        
        plugins = session.exec(statement).all()
        
        # 转换为响应格式
        result = [PluginResponse.from_orm(p) for p in plugins]
        
        return respModel.ok_resp(obj={
            "rows": result,
            "total": total
        })
    
    except Exception as e:
        return respModel.error_resp(msg=f"查询失败: {str(e)}")


@module_route.get("/queryById", summary="根据ID查询插件详情")
async def query_by_id(
    id: int = Query(..., description="插件ID"),
    session: Session = Depends(get_session)
):
    """根据ID查询插件详情"""
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        return respModel.ok_resp(obj=PluginResponse.from_orm(plugin))
    
    except Exception as e:
        return respModel.error_resp(msg=f"查询失败: {str(e)}")


@module_route.put("/update", summary="更新插件配置")
async def update_plugin(
    id: int = Query(..., description="插件ID"),
    update_data: PluginUpdate = None,
    session: Session = Depends(get_session)
):
    """更新插件配置"""
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                if key in ["capabilities", "config_schema"]:
                    setattr(plugin, key, json.dumps(value) if value else None)
                elif key == "dependencies":
                    setattr(plugin, key, json.dumps(value) if value else None)
                else:
                    setattr(plugin, key, value)
        
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        return respModel.ok_resp(obj=PluginResponse.from_orm(plugin), msg="更新成功")
    
    except Exception as e:
        return respModel.error_resp(msg=f"更新失败: {str(e)}")


@module_route.delete("/unregister", summary="注销插件")
async def unregister_plugin(
    id: int = Query(..., description="插件ID"),
    uninstall_package: bool = Query(False, description="是否同时卸载已安装的pip包"),
    cleanup_temp: bool = Query(False, description="是否同时清理所有临时执行文件"),
    session: Session = Depends(get_session)
):
    """
    注销（删除）插件
    
    Args:
        id: 插件ID
        uninstall_package: 是否同时卸载已安装的pip包（默认False）
        cleanup_temp: 是否同时清理所有临时执行文件（默认False）
    """
    import subprocess
    import sys
    
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        cleanup_results = []
        
        # 1. 如果需要，卸载已安装的pip包
        if uninstall_package and plugin.plugin_code:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", plugin.plugin_code],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    cleanup_results.append(f"已卸载pip包: {plugin.plugin_code}")
                else:
                    cleanup_results.append(f"pip包卸载失败或不存在: {result.stderr or result.stdout}")
            except Exception as e:
                cleanup_results.append(f"pip卸载异常: {str(e)}")
        
        # 2. 清理临时执行目录（使用 temp_manager 统一管理）
        try:
            executor_temp_dir = get_temp_subdir("executor")
            if executor_temp_dir.exists():
                temp_items = list(executor_temp_dir.iterdir())
                temp_count = len(temp_items)
                if temp_count > 0:
                    if cleanup_temp:
                        # 清理所有临时文件
                        cleaned = 0
                        for item in temp_items:
                            try:
                                if item.is_dir():
                                    shutil.rmtree(item, ignore_errors=True)
                                else:
                                    item.unlink()
                                cleaned += 1
                            except Exception:
                                pass
                        cleanup_results.append(f"已清理 {cleaned}/{temp_count} 个临时文件")
                    else:
                        cleanup_results.append(f"临时目录存在 {temp_count} 个任务文件夹，如需清理请设置 cleanup_temp=true")
        except Exception as e:
            cleanup_results.append(f"检查临时目录异常: {str(e)}")
        
        # 3. 删除数据库记录
        session.delete(plugin)
        session.commit()
        
        msg = "插件注销成功"
        if cleanup_results:
            msg += "。" + "；".join(cleanup_results)
        
        return respModel.ok_resp(msg=msg)
    
    except Exception as e:
        return respModel.error_resp(msg=f"注销失败: {str(e)}")


@module_route.put("/toggle", summary="启用/禁用插件")
async def toggle_plugin(
    id: int = Query(..., description="插件ID"),
    session: Session = Depends(get_session)
):
    """切换插件启用状态"""
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        # 切换状态
        plugin.is_enabled = 1 if plugin.is_enabled == 0 else 0
        
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        status_text = "启用" if plugin.is_enabled == 1 else "禁用"
        return respModel.ok_resp(obj=PluginResponse.from_orm(plugin), msg=f"插件已{status_text}")
    
    except Exception as e:
        return respModel.error_resp(msg=f"操作失败: {str(e)}")


@module_route.post("/healthCheck", summary="检查插件健康状态")
async def health_check_plugin(
    id: int = Query(..., description="插件ID"),
    session: Session = Depends(get_session)
):
    """检查插件健康状态"""
    import subprocess
    import sys
    
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        start_time = time.time()
        status = "unknown"
        msg = ""
        cmd_path = None
        
        # 检查逻辑优先级：
        # 1. 如果有 command，检查命令是否可用（最重要）
        # 2. 如果有 plugin_content 但命令不可用，提示需要安装
        
        if plugin.command:
            # 检查命令是否在 PATH 中可用
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import shutil; print(shutil.which('{plugin.command}'))"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                cmd_path = result.stdout.strip()
                if cmd_path and cmd_path != "None":
                    status = "healthy"
                    msg = f"命令 {plugin.command} 可用，路径: {cmd_path}"
                else:
                    # 命令不可用，检查是否有 plugin_content 可以安装
                    if plugin.plugin_content:
                        status = "not_installed"
                        msg = f"命令 {plugin.command} 未安装，请点击安装按钮"
                    else:
                        status = "unhealthy"
                        msg = f"命令 {plugin.command} 不可用，且无安装包"
            except Exception as e:
                status = "unknown"
                msg = f"无法检测命令状态: {str(e)}"
        elif plugin.plugin_content:
            # 有安装包但没有配置 command
            status = "not_configured"
            msg = "插件已上传但未配置命令，请检查 setup.py"
        else:
            status = "not_configured"
            msg = "插件未配置（无命令、无工作目录、无安装包）"

        response_time = (time.time() - start_time) * 1000
        
        return respModel.ok_resp(obj=PluginHealthCheck(
            plugin_code=plugin.plugin_code,
            status=status,
            version=plugin.version,
            response_time_ms=response_time,
            error_message=msg if status != "healthy" else None
        ), msg=msg)
    
    except Exception as e:
        return respModel.error_resp(msg=f"健康检查失败: {str(e)}")


@module_route.get("/list/enabled", summary="获取所有已启用的插件")
async def list_enabled_plugins(
    plugin_type: str = Query(None, description="插件类型筛选"),
    session: Session = Depends(get_session)
):
    """获取所有已启用的插件列表"""
    try:
        statement = select(Plugin).where(Plugin.is_enabled == 1)
        
        if plugin_type:
            statement = statement.where(Plugin.plugin_type == plugin_type)
        
        plugins = session.exec(statement).all()
        result = [PluginResponse.from_orm(p) for p in plugins]
        
        return respModel.ok_resp_list(lst=result)
    
    except Exception as e:
        return respModel.error_resp(msg=f"查询失败: {str(e)}")


def _parse_console_scripts(setup_content: str) -> dict:
    """
    解析 setup.py 中的 entry_points.console_scripts
    返回 {"command_name": "module:function", ...}
    """
    scripts = {}
    # 匹配 entry_points = { ... "console_scripts": [...] ... }
    entry_points_match = re.search(
        r'entry_points\s*=\s*\{([^}]+)\}', 
        setup_content, 
        re.DOTALL
    )
    if entry_points_match:
        ep_content = entry_points_match.group(1)
        # 匹配 "console_scripts": [...]
        cs_match = re.search(
            r'["\']console_scripts["\']\s*:\s*\[([^\]]+)\]',
            ep_content,
            re.DOTALL
        )
        if cs_match:
            cs_content = cs_match.group(1)
            # 匹配每个脚本定义 "name=module:func"
            for script_match in re.finditer(r'["\']([^"\'=]+)=([^"\']+)["\']', cs_content):
                cmd_name = script_match.group(1).strip()
                module_func = script_match.group(2).strip()
                scripts[cmd_name] = module_func
    return scripts


def _parse_keywords_from_python(plugin_root: Path) -> dict:
    """
    从 keywords.py 文件解析关键字方法
    通过解析类中的方法定义和 kwargs.get() 调用提取参数
    同时提取完整的方法体代码
    """
    keywords = {}
    
    py_patterns = [
        "**/keywords.py",
        "**/extend/keywords.py"
    ]
    
    for pattern in py_patterns:
        for py_file in plugin_root.glob(pattern):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 匹配方法定义: def method_name(self, **kwargs):
                method_pattern = re.compile(
                    r'def\s+(\w+)\s*\(\s*self\s*,\s*\*\*kwargs\s*\)\s*:',
                    re.MULTILINE
                )
                
                # 匹配装饰器（用于确定方法的真正结束位置）
                decorator_pattern = re.compile(r'^\s*@\w+', re.MULTILINE)
                
                # 按行分割，便于向前查找装饰器
                lines = content.split('\n')
                
                # 构建行号到字符位置的映射
                line_positions = []
                pos = 0
                for line in lines:
                    line_positions.append(pos)
                    pos += len(line) + 1  # +1 for newline
                
                def get_line_number(char_pos):
                    """根据字符位置获取行号"""
                    for i, lp in enumerate(line_positions):
                        if i + 1 < len(line_positions) and char_pos < line_positions[i + 1]:
                            return i
                        elif i + 1 == len(line_positions):
                            return i
                    return 0
                
                # 查找所有方法
                for match in method_pattern.finditer(content):
                    method_name = match.group(1)
                    
                    # 跳过私有方法和特殊方法
                    if method_name.startswith('_'):
                        continue
                    
                    # 获取方法定义的起始位置
                    method_def_start = match.start()
                    
                    # 获取 def 所在的行号
                    def_line_num = get_line_number(method_def_start)
                    
                    # 向前查找装饰器（按行查找）
                    code_start_line = def_line_num
                    check_line = def_line_num - 1
                    while check_line >= 0:
                        line_content = lines[check_line].strip()
                        
                        if line_content.startswith('@'):
                            # 找到装饰器
                            code_start_line = check_line
                            check_line -= 1
                        elif line_content == '' or line_content.startswith('#'):
                            # 空行或注释行，继续向前查找
                            check_line -= 1
                        else:
                            # 不是装饰器，停止查找
                            break
                    
                    code_start = line_positions[code_start_line]
                    
                    # 获取方法体的起始位置
                    body_start_pos = match.end()
                    
                    # 查找下一个方法定义或装饰器（以确定当前方法的结束位置）
                    next_method = method_pattern.search(content, body_start_pos)
                    next_decorator = decorator_pattern.search(content, body_start_pos)
                    
                    # 确定方法结束位置：取下一个装饰器或下一个方法定义中较早的位置
                    body_end_pos = len(content)
                    if next_method:
                        body_end_pos = next_method.start()
                    if next_decorator:
                        # 只有当装饰器在下一个方法之前才使用它作为结束位置
                        decorator_pos = next_decorator.start()
                        if decorator_pos < body_end_pos:
                            body_end_pos = decorator_pos
                    
                    method_body = content[body_start_pos:body_end_pos]
                    
                    # 提取完整方法代码（包含装饰器和 def 行，不包含下一个方法的装饰器）
                    full_method_code = content[code_start:body_end_pos].rstrip()
                    
                    # 从方法体中提取 kwargs.get("PARAM") 调用
                    params = []
                    param_pattern = re.compile(r'kwargs\.get\s*\(\s*["\'](\w+)["\']')
                    for param_match in param_pattern.finditer(method_body):
                        param_name = param_match.group(1)
                        if param_name not in params and param_name != '关键字':
                            params.append(param_name)
                    
                    # 提取方法的文档字符串作为描述
                    doc_match = re.search(r'"""([^"]+)"""', method_body[:500])
                    description = doc_match.group(1).strip().split('\n')[0] if doc_match else ""
                    
                    if method_name not in keywords:
                        keywords[method_name] = {
                            "params": params,
                            "category": "Python方法",
                            "description": description,
                            "source": str(py_file.relative_to(plugin_root)),
                            "code": full_method_code
                        }
                
            except Exception as e:
                print(f"解析 {py_file} 时出错: {e}")
                continue
    
    return keywords


def _parse_keywords_yaml(plugin_root: Path) -> dict:
    """
    解析插件中的关键字定义
    优先从 keywords.yaml 读取，同时从 keywords.py 补充
    返回格式: {
        "keyword_name": {
            "params": ["PARAM1", "PARAM2"],
            "category": "HTTP请求类关键字"
        }
    }
    """
    keywords = {}
    
    # ========== 1. 从 keywords.yaml 解析 ==========
    keywords_patterns = [
        "**/keywords.yaml",
        "**/keywords.yml",
        "**/extend/keywords.yaml",
        "**/extend/keywords.yml"
    ]
    
    for pattern in keywords_patterns:
        for yaml_file in plugin_root.glob(pattern):
            try:
                import yaml as yaml_lib
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    data = yaml_lib.safe_load(content)
                
                if not data or not isinstance(data, dict):
                    continue
                
                current_category = "未分类"
                
                # 解析注释获取分类（通过读取原始内容）
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    # 检测分类注释，如 "# HTTP请求类关键字"
                    if stripped.startswith('#') and '关键字' in stripped:
                        # 提取分类名称
                        category_match = re.search(r'#\s*=*\s*(.+关键字)\s*=*', stripped)
                        if category_match:
                            current_category = category_match.group(1).strip()
                    
                    # 检测关键字定义行（不以空格开头，以冒号结尾）
                    if stripped and not stripped.startswith('#') and not stripped.startswith('-') and not stripped.startswith(' '):
                        keyword_match = re.match(r'^(\w+)\s*:', stripped)
                        if keyword_match:
                            keyword_name = keyword_match.group(1)
                            if keyword_name in data:
                                params = data[keyword_name]
                                # 处理参数格式
                                if isinstance(params, list):
                                    # 提取参数名（去掉注释）
                                    param_list = []
                                    for p in params:
                                        if isinstance(p, str):
                                            # 去掉注释部分
                                            param_name = p.split('#')[0].strip()
                                            param_list.append(param_name)
                                    params = param_list
                                elif isinstance(params, str):
                                    # 逗号分隔格式
                                    params = [p.strip() for p in params.split(',')]
                                else:
                                    params = []
                                
                                keywords[keyword_name] = {
                                    "params": params,
                                    "category": current_category,
                                    "source": str(yaml_file.relative_to(plugin_root))
                                }
                
                # 如果上面的方式没有解析到，直接遍历 data
                for keyword_name, params in data.items():
                    if keyword_name not in keywords:
                        if isinstance(params, list):
                            param_list = []
                            for p in params:
                                if isinstance(p, str):
                                    param_name = p.split('#')[0].strip()
                                    param_list.append(param_name)
                            params = param_list
                        elif isinstance(params, str):
                            params = [p.strip() for p in params.split(',')]
                        else:
                            params = []
                        
                        keywords[keyword_name] = {
                            "params": params,
                            "category": "未分类",
                            "source": str(yaml_file.relative_to(plugin_root))
                        }
                
            except Exception as e:
                print(f"解析 {yaml_file} 时出错: {e}")
                continue
    
    # ========== 2. 从 keywords.py 补充 ==========
    py_keywords = _parse_keywords_from_python(plugin_root)
    
    # 先处理 Python 中有实现的关键字
    for keyword_name, keyword_info in py_keywords.items():
        if keyword_name not in keywords:
            # YAML 中没有定义，从 Python 文件补充
            keywords[keyword_name] = keyword_info
            # 标记为已实现
            keywords[keyword_name]["is_implemented"] = True
        else:
            # YAML 中已定义，补充描述信息和代码
            if keyword_info.get("description") and not keywords[keyword_name].get("description"):
                keywords[keyword_name]["description"] = keyword_info["description"]
            # 补充方法体代码（关键：YAML 定义的关键字也需要代码）
            if keyword_info.get("code"):
                keywords[keyword_name]["code"] = keyword_info["code"]
            # 标记为已实现
            keywords[keyword_name]["is_implemented"] = True
    
    # 对于只在 YAML 中定义但没有 Python 实现的关键字，生成可执行代码
    for keyword_name in keywords:
        if not keywords[keyword_name].get("is_implemented"):
            # 没有 Python 实现，生成可执行代码
            keywords[keyword_name]["is_extension"] = True
            
            # 生成方法代码
            params = keywords[keyword_name].get("params", [])
            category = keywords[keyword_name].get("category", "未分类")
            
            # 根据函数名称生成对应的实现代码
            code_template = _generate_keyword_implementation(keyword_name, params, category)
            
            keywords[keyword_name]["code"] = code_template
            # 保留原分类，添加待实现标记
            keywords[keyword_name]["category"] = f"{category} (待实现)"
    
    return keywords


def _generate_keyword_implementation(keyword_name: str, params: list, category: str, 
                                       existing_templates: dict = None) -> str:
    """
    根据关键字名称、参数和分类，基于已有模板动态生成可执行的实现代码
    
    逻辑：
    1. 从已有实现中找到同类型的模板（如 request_get 作为 HTTP GET 模板）
    2. 根据新关键字的名称和参数，替换模板中的关键部分
    3. 生成新的可执行代码
    """
    # 构建参数获取代码
    param_lines = []
    for param in params:
        param_lower = param.lower()
        param_lines.append(f'        {param_lower} = kwargs.get("{param}", None)')
    params_code = "\n".join(param_lines) if param_lines else ''
    
    # ========== 根据函数名称推断类型并生成代码 ==========
    
    # 1. HTTP 请求类：request_xxx
    if keyword_name.startswith("request_"):
        return _generate_http_request_code(keyword_name, params, params_code)
    
    # 2. 数据提取类：extract_xxx 或 ex_xxx
    elif keyword_name.startswith("extract_") or keyword_name.startswith("ex_"):
        return _generate_extract_code(keyword_name, params, params_code)
    
    # 3. 断言类：assert_xxx
    elif keyword_name.startswith("assert_"):
        return _generate_assert_code(keyword_name, params, params_code)
    
    # 4. 数据库类：execute_sql_xxx 或包含 mysql/sql
    elif keyword_name.startswith("execute_sql") or "mysql" in keyword_name.lower() or "sql" in keyword_name.lower():
        return _generate_database_code(keyword_name, params, params_code)
    
    # 5. 根据分类生成通用代码
    else:
        return _generate_generic_code(keyword_name, params, params_code, category)


def _generate_http_request_code(keyword_name: str, params: list, params_code: str) -> str:
    """
    基于 request_get 模板生成 HTTP 请求代码
    模板格式参考：
        @allure.step(">>>>>>参数数据：")
        def request_get(self, **kwargs):
            url = kwargs.get("URL", None)
            ...
            response = requests.get(**request_data)
            g_context().set_dict("current_response", response)
    """
    # 解析函数名: request_get -> GET, request_post_json -> POST
    parts = keyword_name.replace("request_", "").split("_")
    http_method = parts[0].upper()  # GET, POST, PUT, DELETE, PATCH
    
    # 解析 body 类型
    body_type = "json"  # 默认
    if len(parts) > 1:
        body_hint = "_".join(parts[1:])
        if "form" in body_hint or "urlencoded" in body_hint:
            body_type = "data"
        elif "file" in body_hint:
            body_type = "files"
    
    # 构建 request_data 字典项
    request_data_items = ['"url": url', '"params": params', '"headers": headers']
    if "DATA" in params:
        request_data_items.append(f'"{body_type}": data')
    if "FILES" in params:
        request_data_items.append('"files": files')
    
    request_data_code = ",\n            ".join(request_data_items)
    
    # 生成描述
    method_desc_map = {
        "GET": "发送GET请求",
        "POST": "发送POST请求",
        "PUT": "发送PUT请求",
        "DELETE": "发送DELETE请求",
        "PATCH": "发送PATCH请求",
    }
    method_desc = method_desc_map.get(http_method, f"发送{http_method}请求")
    
    return f'''    @allure.step(">>>>>>参数数据：")
    def {keyword_name}(self, **kwargs):
        """
        {method_desc}
        """
{params_code}

        request_data = {{
            {request_data_code}
        }}

        response = requests.{http_method.lower()}(**request_data)
        g_context().set_dict("current_response", response)
        print("-----------------------")
        print(response.text)
        print("-----------------------")'''


def _generate_extract_code(keyword_name: str, params: list, params_code: str) -> str:
    """
    基于 ex_jsonData 模板生成数据提取代码
    模板格式参考：
        @allure.step(">>>>>>参数数据：")
        def ex_jsonData(self, **kwargs):
            EXPRESSION = kwargs.get("EXVALUE", None)
            response = g_context().get_dict("current_response").json()
            ex_data = jsonpath.jsonpath(response, EXPRESSION)[INDEX]
            g_context().set_dict(kwargs["VARNAME"], ex_data)
    """
    # 确定变量名参数
    var_name_param = "VAR_NAME" if "VAR_NAME" in params else "VARNAME"
    expr_param = "EXPRESSION" if "EXPRESSION" in params else "EXVALUE"
    
    # 根据函数名确定提取类型
    if "json" in keyword_name.lower():
        extract_type = "json"
        extract_desc = "提取JSON数据"
        extract_logic = f'''        response = g_context().get_dict("current_response").json()
        index = int(kwargs.get("INDEX", 0) or 0)
        ex_data = jsonpath.jsonpath(response, {expr_param.lower()})[index]
        g_context().set_dict({var_name_param.lower()}, ex_data)'''
    
    elif "regex" in keyword_name.lower() or keyword_name == "ex_reData":
        extract_type = "regex"
        extract_desc = "提取正则数据"
        extract_logic = f'''        response = g_context().get_dict("current_response").text
        index = int(kwargs.get("INDEX", 0) or 0)
        ex_data = re.findall({expr_param.lower()}, response)[index]
        g_context().set_dict({var_name_param.lower()}, ex_data)'''
    
    elif "header" in keyword_name.lower():
        extract_type = "header"
        extract_desc = "提取响应头"
        header_param = "HEADER_NAME" if "HEADER_NAME" in params else "header_name"
        extract_logic = f'''        response = g_context().get_dict("current_response")
        ex_data = response.headers.get({header_param.lower()})
        g_context().set_dict({var_name_param.lower()}, ex_data)'''
    
    elif "cookie" in keyword_name.lower():
        extract_type = "cookie"
        extract_desc = "提取Cookie"
        cookie_param = "COOKIE_NAME" if "COOKIE_NAME" in params else "cookie_name"
        extract_logic = f'''        response = g_context().get_dict("current_response")
        ex_data = response.cookies.get({cookie_param.lower()})
        g_context().set_dict({var_name_param.lower()}, ex_data)'''
    
    else:
        # 默认 JSON 提取
        extract_desc = "提取数据"
        extract_logic = f'''        response = g_context().get_dict("current_response").json()
        index = int(kwargs.get("INDEX", 0) or 0)
        ex_data = jsonpath.jsonpath(response, {expr_param.lower()})[index]
        g_context().set_dict({var_name_param.lower()}, ex_data)'''
    
    return f'''    @allure.step(">>>>>>参数数据：")
    def {keyword_name}(self, **kwargs):
        """
        {extract_desc}
        """
{params_code}

{extract_logic}
        print("-----------------------")
        print(g_context().show_dict())
        print("-----------------------")'''


def _generate_assert_code(keyword_name: str, params: list, params_code: str) -> str:
    """
    基于 assert_text_comparators 模板生成断言代码
    模板格式参考：
        @allure.step(">>>>>>参数数据：")
        def assert_text_comparators(self, **kwargs):
            comparators = {...}
            if not comparators[kwargs['OP_STR']](kwargs['VALUE'], kwargs["EXPECTED"]):
                raise AssertionError(...)
    """
    # 根据函数名确定断言类型
    if "status" in keyword_name.lower() and "code" in keyword_name.lower():
        assert_desc = "断言状态码"
        expected_param = "EXPECTED_CODE" if "EXPECTED_CODE" in params else "expected_code"
        assert_logic = f'''        response = g_context().get_dict("current_response")
        actual_code = response.status_code
        expected = int({expected_param.lower()} or 200)
        
        assert actual_code == expected, f"状态码断言失败: 期望 {{expected}}, 实际 {{actual_code}}"
        print(f"✅ 状态码断言成功: {{actual_code}}")'''
    
    elif "time" in keyword_name.lower():
        assert_desc = "断言响应时间"
        max_param = "MAX_TIME" if "MAX_TIME" in params else "max_time"
        assert_logic = f'''        response = g_context().get_dict("current_response")
        actual_time = response.elapsed.total_seconds()
        max_t = float({max_param.lower()} or 5)
        
        assert actual_time <= max_t, f"响应时间断言失败: 期望 <= {{max_t}}s, 实际 {{actual_time}}s"
        print(f"✅ 响应时间断言成功: {{actual_time}}s")'''
    
    elif "contains" in keyword_name.lower() or ("text" in keyword_name.lower() and "json" not in keyword_name.lower()):
        assert_desc = "断言响应包含文本"
        text_param = "EXPECTED_TEXT" if "EXPECTED_TEXT" in params else "expected_text"
        assert_logic = f'''        response = g_context().get_dict("current_response")
        response_text = response.text
        
        assert {text_param.lower()} in response_text, f"文本断言失败: 响应中不包含 '{{{text_param.lower()}}}'"
        print(f"✅ 文本断言成功")'''
    
    elif "json" in keyword_name.lower() and "field" in keyword_name.lower():
        assert_desc = "断言JSON字段值"
        path_param = "JSON_PATH" if "JSON_PATH" in params else "json_path"
        expected_param = "EXPECTED_VALUE" if "EXPECTED_VALUE" in params else "expected_value"
        assert_logic = f'''        response = g_context().get_dict("current_response").json()
        actual_value = jsonpath.jsonpath(response, {path_param.lower()})
        actual_value = actual_value[0] if actual_value else None
        
        assert actual_value == {expected_param.lower()}, f"JSON字段断言失败: {{{path_param.lower()}}} 期望 {{{expected_param.lower()}}}, 实际 {{actual_value}}"
        print(f"✅ JSON字段断言成功")'''
    
    elif "number" in keyword_name.lower() or "compare" in keyword_name.lower():
        assert_desc = "数值比较断言"
        actual_param = "ACTUAL_VALUE" if "ACTUAL_VALUE" in params else "VALUE"
        expected_param = "EXPECTED_VALUE" if "EXPECTED_VALUE" in params else "EXPECTED"
        op_param = "OPERATOR" if "OPERATOR" in params else "OP_STR"
        assert_logic = f'''        comparators = {{
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }}
        
        op = {op_param.lower()} or "=="
        result = comparators[op](float({actual_param.lower()}), float({expected_param.lower()}))
        assert result, f"数值比较断言失败: {{{actual_param.lower()}}} {{op}} {{{expected_param.lower()}}}"
        print(f"✅ 数值比较断言成功")'''
    
    else:
        # 默认断言
        assert_desc = "断言验证"
        assert_logic = '''        # TODO: 实现断言逻辑
        print(f"执行断言")'''
    
    return f'''    @allure.step(">>>>>>参数数据：")
    def {keyword_name}(self, **kwargs):
        """
        {assert_desc}
        """
{params_code}

{assert_logic}'''


def _generate_database_code(keyword_name: str, params: list, params_code: str) -> str:
    """
    基于 ex_mysqlData 模板生成数据库操作代码
    """
    db_param = "DB_NAME" if "DB_NAME" in params else "数据库"
    sql_param = "SQL" if "SQL" in params else "sql"
    
    if "query" in keyword_name.lower() or "select" in keyword_name.lower() or "Data" in keyword_name:
        db_desc = "执行SQL查询"
        db_logic = f'''        import pymysql
        from pymysql import cursors
        
        config = {{"cursorclass": cursors.DictCursor}}
        db_config = g_context().get_dict("_database")[{db_param.lower()}]
        config.update(db_config)
        
        con = pymysql.connect(**config)
        cur = con.cursor()
        cur.execute({sql_param.lower()})
        rs = cur.fetchall()
        cur.close()
        con.close()
        
        # 存储结果到全局变量
        for i, item in enumerate(rs, start=1):
            for key, value in item.items():
                g_context().set_dict(f"{{key}}_{{i}}", value)
        
        print(f"✅ 查询成功，返回 {{len(rs)}} 条记录")'''
    else:
        db_desc = "执行SQL更新"
        db_logic = f'''        import pymysql
        
        db_config = g_context().get_dict("_database")[{db_param.lower()}]
        
        con = pymysql.connect(**db_config)
        cur = con.cursor()
        affected_rows = cur.execute({sql_param.lower()})
        con.commit()
        cur.close()
        con.close()
        
        print(f"✅ SQL执行成功，影响行数: {{affected_rows}}")'''
    
    return f'''    @allure.step(">>>>>>参数数据：")
    def {keyword_name}(self, **kwargs):
        """
        {db_desc}
        """
{params_code}

{db_logic}'''


def _generate_generic_code(keyword_name: str, params: list, params_code: str, category: str) -> str:
    """
    根据分类和函数名生成通用代码
    """
    # 根据函数名关键词匹配功能
    if "wait" in keyword_name.lower() or "sleep" in keyword_name.lower():
        seconds_param = "SECONDS" if "SECONDS" in params else "seconds"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        等待指定时间
        """
        import time
{params_code}

        time.sleep(float({seconds_param.lower()} or 1))
        print(f"✅ 等待 {{{seconds_param.lower()}}} 秒完成")'''
    
    elif "random" in keyword_name.lower() and "string" in keyword_name.lower():
        length_param = "LENGTH" if "LENGTH" in params else "length"
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        生成随机字符串
        """
        import random
        import string as str_lib
{params_code}

        result = ''.join(random.choices(str_lib.ascii_letters + str_lib.digits, k=int({length_param.lower()} or 8)))
        g_context().set_dict({var_param.lower()} or "random_string", result)
        print(f"✅ 生成随机字符串: {{result}}")'''
    
    elif "random" in keyword_name.lower() and "number" in keyword_name.lower():
        min_param = "MIN_VALUE" if "MIN_VALUE" in params else "min_value"
        max_param = "MAX_VALUE" if "MAX_VALUE" in params else "max_value"
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        生成随机数
        """
        import random
{params_code}

        result = random.randint(int({min_param.lower()} or 0), int({max_param.lower()} or 100))
        g_context().set_dict({var_param.lower()} or "random_number", result)
        print(f"✅ 生成随机数: {{result}}")'''
    
    elif "timestamp" in keyword_name.lower():
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        获取当前时间戳
        """
        import time
{params_code}

        result = int(time.time())
        g_context().set_dict({var_param.lower()} or "timestamp", result)
        print(f"✅ 当前时间戳: {{result}}")'''
    
    elif "datetime" in keyword_name.lower() or ("format" in keyword_name.lower() and "time" in category.lower()):
        format_param = "FORMAT" if "FORMAT" in params else "format"
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        格式化当前时间
        """
        from datetime import datetime
{params_code}

        result = datetime.now().strftime({format_param.lower()} or "%Y-%m-%d %H:%M:%S")
        g_context().set_dict({var_param.lower()} or "datetime", result)
        print(f"✅ 格式化时间: {{result}}")'''
    
    elif "md5" in keyword_name.lower():
        text_param = "TEXT" if "TEXT" in params else "text"
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        MD5加密
        """
        import hashlib
{params_code}

        result = hashlib.md5(({text_param.lower()} or "").encode()).hexdigest()
        g_context().set_dict({var_param.lower()} or "md5_result", result)
        print(f"✅ MD5加密结果: {{result}}")'''
    
    elif "base64" in keyword_name.lower():
        if "decode" in keyword_name.lower():
            text_param = "ENCODED_TEXT" if "ENCODED_TEXT" in params else "encoded_text"
            var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
            return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        Base64解码
        """
        import base64 as b64
{params_code}

        result = b64.b64decode({text_param.lower()} or "").decode()
        g_context().set_dict({var_param.lower()} or "decoded_result", result)
        print(f"✅ Base64解码结果: {{result}}")'''
        else:
            text_param = "TEXT" if "TEXT" in params else "text"
            var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
            return f'''    @allure.step(">>>>>>执行操作：")
    def {keyword_name}(self, **kwargs):
        """
        Base64编码
        """
        import base64 as b64
{params_code}

        result = b64.b64encode(({text_param.lower()} or "").encode()).decode()
        g_context().set_dict({var_param.lower()} or "base64_result", result)
        print(f"✅ Base64编码结果: {{result}}")'''
    
    elif "read" in keyword_name.lower() and "file" in keyword_name.lower():
        path_param = "FILE_PATH" if "FILE_PATH" in params else "file_path"
        enc_param = "ENCODING" if "ENCODING" in params else "encoding"
        var_param = "VAR_NAME" if "VAR_NAME" in params else "var_name"
        return f'''    @allure.step(">>>>>>文件操作：")
    def {keyword_name}(self, **kwargs):
        """
        读取文件内容
        """
{params_code}

        with open({path_param.lower()}, 'r', encoding={enc_param.lower()} or "utf-8") as f:
            content = f.read()
        
        g_context().set_dict({var_param.lower()} or "file_content", content)
        print(f"✅ 读取文件成功: {{{path_param.lower()}}}")'''
    
    elif "write" in keyword_name.lower() and "file" in keyword_name.lower():
        path_param = "FILE_PATH" if "FILE_PATH" in params else "file_path"
        content_param = "CONTENT" if "CONTENT" in params else "content"
        enc_param = "ENCODING" if "ENCODING" in params else "encoding"
        mode_param = "MODE" if "MODE" in params else "mode"
        return f'''    @allure.step(">>>>>>文件操作：")
    def {keyword_name}(self, **kwargs):
        """
        写入文件内容
        """
{params_code}

        with open({path_param.lower()}, {mode_param.lower()} or "w", encoding={enc_param.lower()} or "utf-8") as f:
            f.write({content_param.lower()} or "")
        
        print(f"✅ 写入文件成功: {{{path_param.lower()}}}")'''
    
    elif "delete" in keyword_name.lower() and "file" in keyword_name.lower():
        path_param = "FILE_PATH" if "FILE_PATH" in params else "file_path"
        return f'''    @allure.step(">>>>>>文件操作：")
    def {keyword_name}(self, **kwargs):
        """
        删除文件
        """
        import os
{params_code}

        if os.path.exists({path_param.lower()}):
            os.remove({path_param.lower()})
            print(f"✅ 删除文件成功: {{{path_param.lower()}}}")
        else:
            print(f"⚠️ 文件不存在: {{{path_param.lower()}}}")'''
    
    # ========== 默认模板 ==========
    else:
        # 根据分类选择装饰器描述
        step_desc = "执行操作"
        if "HTTP" in category or "请求" in category:
            step_desc = "参数数据"
        elif "提取" in category:
            step_desc = "数据提取"
        elif "断言" in category:
            step_desc = "断言验证"
        elif "数据库" in category:
            step_desc = "数据库操作"
        elif "文件" in category:
            step_desc = "文件操作"
        
        return f'''    @allure.step(">>>>>>{step_desc}：")
    def {keyword_name}(self, **kwargs):
        """
        {keyword_name}
        """
{params_code}
        
        # TODO: 根据业务需求实现此方法
        print(f"执行 {keyword_name}")'''


def _parse_pytest_addoption(plugin_root: Path) -> list:
    """
    解析插件中的自定义参数配置
    支持两种方式:
    1. CasesPlugin.py/conftest.py 中的 pytest_addoption (parser.addoption)
    2. cli.py 中的命令行参数解析 (startswith("--xxx="))
    返回参数列表: [{"name": "--type", "default": "yaml", "help": "...", "type": "string"}, ...]
    """
    config_params = []
    
    # ========== 方式1: 解析 pytest_addoption ==========
    pytest_patterns = [
        "**/CasesPlugin.py",
        "**/conftest.py",
        "**/plugin.py",
        "**/pytest_plugin.py"
    ]
    
    for pattern in pytest_patterns:
        for py_file in plugin_root.glob(pattern):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "addoption" not in content:
                    continue
                
                # 匹配 parser.addoption("--name", action="store", default="value", help="desc")
                addoption_pattern = re.compile(
                    r'parser\.addoption\s*\(\s*'
                    r'["\'](-{1,2}[\w-]+)["\']'  # 参数名
                    r'[^)]*?'
                    r'(?:default\s*=\s*(["\'][^"\']*["\']|[\w.]+))?'  # default 值
                    r'[^)]*?'
                    r'(?:help\s*=\s*["\']([^"\']*)["\'])?'  # help 描述
                    r'[^)]*?'
                    r'(?:action\s*=\s*["\']([^"\']*)["\'])?'  # action 类型
                    r'[^)]*\)',
                    re.DOTALL
                )
                
                for match in addoption_pattern.finditer(content):
                    param_name = match.group(1)
                    default_val = match.group(2)
                    help_text = match.group(3) or ""
                    action = match.group(4) or "store"
                    
                    if default_val:
                        default_val = default_val.strip('"\'').strip()
                    else:
                        default_val = ""
                    
                    param_type = "string"
                    if action == "store_true" or action == "store_false":
                        param_type = "boolean"
                        default_val = "true" if action == "store_true" else "false"
                    elif default_val.isdigit():
                        param_type = "integer"
                    elif default_val.lower() in ["true", "false"]:
                        param_type = "boolean"
                    
                    if not any(p["name"] == param_name for p in config_params):
                        config_params.append({
                            "name": param_name,
                            "default": default_val,
                            "help": help_text,
                            "type": param_type,
                            "required": False,
                            "source": str(py_file.relative_to(plugin_root))
                        })
                
            except Exception as e:
                print(f"解析 {py_file} 时出错: {e}")
                continue
    
    # ========== 方式2: 解析 cli.py 中的命令行参数 ==========
    cli_patterns = ["**/cli.py", "**/main.py", "**/run.py"]
    
    for pattern in cli_patterns:
        for py_file in plugin_root.glob(pattern):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 匹配 startswith("--xxx=") 或 startswith("--xxx") 模式
                # 例如: arg.startswith("--engine-type=")
                cli_arg_pattern = re.compile(
                    r'startswith\s*\(\s*["\'](-{1,2}[\w-]+)[="]?\s*["\']',
                    re.DOTALL
                )
                
                for match in cli_arg_pattern.finditer(content):
                    param_name = match.group(1).rstrip("=")
                    
                    # 尝试从上下文提取默认值和帮助信息
                    default_val = ""
                    help_text = ""
                    
                    # 查找附近的注释或字符串作为帮助信息
                    # 例如: # 从命令行参数中获取 engine-type
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(content), match.end() + 200)
                    context = content[context_start:context_end]
                    
                    # 提取函数文档字符串或注释
                    doc_match = re.search(r'"""([^"]+)"""', context)
                    if doc_match:
                        help_text = doc_match.group(1).strip().split('\n')[0]
                    
                    # 提取默认值 (例如: return 'yaml'  # 默认值)
                    default_match = re.search(
                        rf'{param_name}.*?(?:default|默认)[^\w]*["\']?([\w]+)["\']?',
                        context, re.IGNORECASE
                    )
                    if default_match:
                        default_val = default_match.group(1)
                    
                    if not any(p["name"] == param_name for p in config_params):
                        config_params.append({
                            "name": param_name,
                            "default": default_val,
                            "help": help_text or f"CLI 参数 {param_name}",
                            "type": "string",
                            "required": False,
                            "source": str(py_file.relative_to(plugin_root))
                        })
                
                # 匹配 argparse 风格: parser.add_argument("--xxx", ...)
                argparse_pattern = re.compile(
                    r'add_argument\s*\(\s*'
                    r'["\'](-{1,2}[\w-]+)["\']'
                    r'[^)]*?'
                    r'(?:default\s*=\s*(["\'][^"\']*["\']|[\w.]+))?'
                    r'[^)]*?'
                    r'(?:help\s*=\s*["\']([^"\']*)["\'])?'
                    r'[^)]*\)',
                    re.DOTALL
                )
                
                for match in argparse_pattern.finditer(content):
                    param_name = match.group(1)
                    default_val = match.group(2) or ""
                    help_text = match.group(3) or ""
                    
                    if default_val:
                        default_val = default_val.strip('"\'').strip()
                    
                    if not any(p["name"] == param_name for p in config_params):
                        config_params.append({
                            "name": param_name,
                            "default": default_val,
                            "help": help_text,
                            "type": "string",
                            "required": False,
                            "source": str(py_file.relative_to(plugin_root))
                        })
                
            except Exception as e:
                print(f"解析 {py_file} 时出错: {e}")
                continue
    
    return config_params


@module_route.post("/uploadExecutor", summary="上传执行器插件（存入数据库）")
async def upload_executor(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    上传执行器ZIP包：
    1. 解析 setup.py 提取 console_scripts 命令
    2. 将 ZIP 内容 Base64 编码存入数据库
    3. 不使用文件服务器，需要时动态安装
    """
    extract_dir = None
    
    try:
        # 1. 读取上传的 ZIP 内容
        zip_bytes = await file.read()
        zip_base64 = base64.b64encode(zip_bytes).decode('utf-8')
        
        # 2. 解压到临时目录解析信息（使用项目 temp 目录）
        temp_id = str(uuid.uuid4())
        extract_dir = get_temp_subdir("executor") / f"executor_{temp_id}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 查找解压后的根目录
        items = list(extract_dir.iterdir())
        if len(items) == 1 and items[0].is_dir():
            plugin_root = items[0]
        else:
            plugin_root = extract_dir
        
        # 3. 解析 setup.py 提取信息
        plugin_name = file.filename.replace('.zip', '')
        plugin_code = plugin_name.lower().replace('-', '_')
        command = ""
        console_scripts = {}
        description = "执行器插件"
        version = "1.0.0"
        dependencies = []
        
        setup_py = plugin_root / "setup.py"
        if setup_py.exists():
            with open(setup_py, "r", encoding="utf-8") as f:
                setup_content = f.read()
                
                # 提取 console_scripts
                console_scripts = _parse_console_scripts(setup_content)
                if console_scripts:
                    # 取第一个命令作为主命令
                    command = list(console_scripts.keys())[0]
                
                # 提取 description
                desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', setup_content)
                if desc_match:
                    description = desc_match.group(1)
                
                # 提取 version
                ver_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', setup_content)
                if ver_match:
                    version = ver_match.group(1)
                    
                # 提取 name 作为 plugin_code
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', setup_content)
                if name_match:
                    plugin_code = name_match.group(1).lower().replace('-', '_')
                    plugin_name = name_match.group(1)
        
        # 解析 requirements.txt
        requirements_txt = plugin_root / "requirements.txt"
        if requirements_txt.exists():
            with open(requirements_txt, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("git+"):
                        dependencies.append(line)
        
        # 4. 解析自定义参数配置
        # 优先读取 plugin.yaml 配置文件（推荐方式）
        config_schema = None
        config_params = []
        
        plugin_yaml = plugin_root / "plugin.yaml"
        plugin_json = plugin_root / "plugin.json"
        
        if plugin_yaml.exists():
            # 方式1: 从 plugin.yaml 读取参数定义（推荐）
            try:
                import yaml as yaml_lib
                with open(plugin_yaml, "r", encoding="utf-8") as f:
                    plugin_config = yaml_lib.safe_load(f)
                
                if plugin_config:
                    # 覆盖从 setup.py 提取的信息
                    if plugin_config.get("name"):
                        plugin_name = plugin_config["name"]
                        plugin_code = plugin_name.lower().replace("-", "_")
                    if plugin_config.get("version"):
                        version = plugin_config["version"]
                    if plugin_config.get("description"):
                        description = plugin_config["description"]
                    if plugin_config.get("command"):
                        command = plugin_config["command"]
                    
                    # 读取参数定义
                    if plugin_config.get("params"):
                        config_params = plugin_config["params"]
                        config_schema = {
                            "type": "object",
                            "properties": {},
                            "params": config_params
                        }
                        for param in config_params:
                            prop_name = param["name"].lstrip("-").replace("-", "_")
                            config_schema["properties"][prop_name] = {
                                "type": param.get("type", "string"),
                                "default": param.get("default", ""),
                                "description": param.get("help", param.get("label", "")),
                                "label": param.get("label", prop_name),
                                "options": param.get("options"),
                                "required": param.get("required", False),
                                "condition": param.get("condition")
                            }
            except Exception as e:
                print(f"解析 plugin.yaml 失败: {e}")
        
        elif plugin_json.exists():
            # 方式2: 从 plugin.json 读取参数定义
            try:
                with open(plugin_json, "r", encoding="utf-8") as f:
                    plugin_config = json.load(f)
                
                if plugin_config and plugin_config.get("params"):
                    config_params = plugin_config["params"]
                    config_schema = {
                        "type": "object",
                        "properties": {},
                        "params": config_params
                    }
                    for param in config_params:
                        prop_name = param["name"].lstrip("-").replace("-", "_")
                        config_schema["properties"][prop_name] = {
                            "type": param.get("type", "string"),
                            "default": param.get("default", ""),
                            "description": param.get("help", param.get("label", "")),
                            "label": param.get("label", prop_name),
                            "options": param.get("options"),
                            "required": param.get("required", False)
                        }
            except Exception as e:
                print(f"解析 plugin.json 失败: {e}")
        
        else:
            # 方式3: 回退到解析代码（不推荐，仅兼容旧插件）
            config_params = _parse_pytest_addoption(plugin_root)
            if config_params:
                config_schema = {
                    "type": "object",
                    "properties": {},
                    "params": config_params
                }
                for param in config_params:
                    prop_name = param["name"].lstrip("-").replace("-", "_")
                    config_schema["properties"][prop_name] = {
                        "type": param["type"],
                        "default": param["default"],
                        "description": param["help"]
                    }
        
        if not command:
            return respModel.error_resp(msg="未找到 console_scripts 命令定义，请确保 setup.py 中定义了 entry_points")
        
        # 5. 解析 keywords.yaml 获取关键字定义
        keywords = _parse_keywords_yaml(plugin_root)
        
        # 6. 保存到数据库
        existing = session.exec(
            select(Plugin).where(Plugin.plugin_code == plugin_code)
        ).first()
        
        if existing:
            existing.plugin_name = plugin_name
            existing.command = command
            existing.plugin_content = zip_base64
            existing.description = description
            existing.version = version
            existing.dependencies = json.dumps(dependencies) if dependencies else None
            existing.capabilities = json.dumps({"console_scripts": console_scripts})
            existing.config_schema = json.dumps(config_schema) if config_schema else None
            existing.keywords = json.dumps(keywords) if keywords else None
            existing.modify_time = datetime.now()
            session.add(existing)
            session.commit()
            action = "更新"
            plugin_id = existing.id
        else:
            new_plugin = Plugin(
                plugin_name=plugin_name,
                plugin_code=plugin_code,
                plugin_type="executor",
                version=version,
                command=command,
                plugin_content=zip_base64,
                description=description,
                author="User Upload",
                is_enabled=1,
                dependencies=json.dumps(dependencies) if dependencies else None,
                capabilities=json.dumps({"console_scripts": console_scripts}),
                config_schema=json.dumps(config_schema) if config_schema else None,
                keywords=json.dumps(keywords) if keywords else None
            )
            session.add(new_plugin)
            session.commit()
            session.refresh(new_plugin)
            action = "安装"
            plugin_id = new_plugin.id
        
        # 确定参数来源
        param_source = "plugin.yaml" if plugin_yaml.exists() else ("plugin.json" if plugin_json.exists() else "代码解析")
        keywords_count = len(keywords) if keywords else 0
        
        return respModel.ok_resp(
            obj={
                "id": plugin_id,
                "command": command,
                "console_scripts": console_scripts,
                "config_schema": config_schema,
                "keywords": keywords,
                "keywords_count": keywords_count,
                "param_source": param_source
            },
            msg=f"执行器 {plugin_name} {action}成功，命令: {command}，解析到 {len(config_params)} 个参数，{keywords_count} 个关键字"
        )
    
    except Exception as e:
        import traceback
        return respModel.error_resp(msg=f"上传失败: {str(e)}\n{traceback.format_exc()}")
    
    finally:
        if extract_dir and extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)


# 安装任务状态存储（内存中，生产环境可用 Redis）
_install_tasks: Dict[int, Dict[str, Any]] = {}


def _run_pip_install(plugin_id: int, plugin_code: str, plugin_content: str, command: str):
    """
    后台执行 pip install（在线程中运行）
    """
    import subprocess
    import sys
    
    extract_dir = None
    try:
        _install_tasks[plugin_id] = {
            "status": "installing",
            "message": "正在解压执行器...",
            "progress": 10
        }
        
        # 1. 解码并解压到临时目录（使用项目 temp 目录）
        zip_bytes = base64.b64decode(plugin_content)
        extract_dir = get_temp_subdir("executor") / f"executor_install_{plugin_code}"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 查找解压后的根目录
        items = list(extract_dir.iterdir())
        if len(items) == 1 and items[0].is_dir():
            install_dir = items[0]
        else:
            install_dir = extract_dir
        
        _install_tasks[plugin_id] = {
            "status": "installing",
            "message": "正在执行 pip install...",
            "progress": 30
        }
        
        # 2. 执行 pip install
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "."],
            cwd=str(install_dir),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 3. 保留安装目录（不清理），用于存放报告等运行时文件
        # 安装目录: temp/executor/executor_install_{plugin_code}/
        
        if result.returncode != 0:
            _install_tasks[plugin_id] = {
                "status": "failed",
                "message": f"安装失败: {result.stderr or result.stdout}",
                "progress": 100
            }
        else:
            _install_tasks[plugin_id] = {
                "status": "completed",
                "message": f"执行器安装成功，可使用命令: {command}",
                "output": result.stdout,
                "progress": 100
            }
    
    except subprocess.TimeoutExpired:
        _install_tasks[plugin_id] = {
            "status": "failed",
            "message": "安装超时（超过5分钟）",
            "progress": 100
        }
    except Exception as e:
        _install_tasks[plugin_id] = {
            "status": "failed",
            "message": f"安装异常: {str(e)}",
            "progress": 100
        }
    finally:
        if extract_dir and extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)


@module_route.post("/installExecutor", summary="安装执行器到本地（异步）")
async def install_executor(
    id: int = Query(..., description="执行器插件ID"),
    session: Session = Depends(get_session)
):
    """
    异步安装执行器：立即返回，后台执行 pip install
    通过 /installStatus 接口查询安装进度
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        if not plugin.plugin_content:
            return respModel.error_resp(msg="插件内容为空，请先上传执行器")
        
        # 检查是否已在安装中
        if id in _install_tasks and _install_tasks[id].get("status") == "installing":
            return respModel.ok_resp(
                obj={"status": "installing", "message": "安装任务已在进行中"},
                msg="安装任务已在进行中"
            )
        
        # 初始化安装状态
        _install_tasks[id] = {
            "status": "installing",
            "message": "安装任务已启动...",
            "progress": 0
        }
        
        # 在后台线程中执行安装
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        loop.run_in_executor(
            executor,
            _run_pip_install,
            id,
            plugin.plugin_code,
            plugin.plugin_content,
            plugin.command
        )
        
        return respModel.ok_resp(
            obj={"status": "installing", "plugin_id": id},
            msg="安装任务已启动，请通过 /installStatus 查询进度"
        )
    
    except Exception as e:
        return respModel.error_resp(msg=f"启动安装失败: {str(e)}")


@module_route.get("/installStatus", summary="查询安装进度")
async def get_install_status(
    id: int = Query(..., description="执行器插件ID"),
    session: Session = Depends(get_session)
):
    """
    查询执行器安装进度
    """
    if id not in _install_tasks:
        # 检查插件是否存在，如果存在且已安装，返回完成状态
        plugin = session.get(Plugin, id)
        if plugin and plugin.command:
            # 尝试检查命令是否可用（直接运行 console script）
            import subprocess
            import shutil
            try:
                cmd = plugin.command.split()[0]
                # 检查命令是否在 PATH 中
                cmd_path = shutil.which(cmd)
                if cmd_path:
                    result = subprocess.run(
                        [cmd, "--help"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return respModel.ok_resp(
                            obj={"status": "completed", "message": f"执行器已安装: {plugin.command}", "progress": 100},
                            msg=f"执行器已安装: {plugin.command}"
                        )
            except Exception:
                pass
        
        return respModel.ok_resp(
            obj={"status": "unknown", "message": "未找到安装任务，可能已完成或未启动", "progress": 0},
            msg="未找到安装任务"
        )
    
    task_info = _install_tasks[id]
    return respModel.ok_resp(obj=task_info, msg=task_info.get("message", ""))


@module_route.delete("/cleanupTempFiles", summary="清理临时执行文件")
async def cleanup_temp_files(
    days: int = Query(7, description="清理多少天前的临时文件，默认7天"),
    session: Session = Depends(get_session)
):
    """
    清理临时执行目录中的旧文件
    
    Args:
        days: 清理多少天前的文件（默认7天）
    """
    try:
        # 使用 temp_manager 统一管理的临时目录
        executor_temp_dir = get_temp_subdir("executor")
        
        if not executor_temp_dir.exists():
            return respModel.ok_resp(msg="临时目录不存在，无需清理")
        
        cleaned_count = 0
        failed_count = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for task_dir in executor_temp_dir.iterdir():
            if task_dir.is_dir():
                try:
                    # 检查目录修改时间
                    dir_mtime = task_dir.stat().st_mtime
                    if dir_mtime < cutoff_time:
                        shutil.rmtree(task_dir, ignore_errors=True)
                        cleaned_count += 1
                except Exception:
                    failed_count += 1
        
        return respModel.ok_resp(
            obj={
                "cleaned": cleaned_count,
                "failed": failed_count
            },
            msg=f"清理完成：删除 {cleaned_count} 个临时目录，{failed_count} 个删除失败"
        )
    
    except Exception as e:
        return respModel.error_resp(msg=f"清理失败: {str(e)}")


@module_route.post("/uninstallExecutor", summary="卸载执行器pip包")
async def uninstall_executor(
    id: int = Query(..., description="执行器插件ID"),
    session: Session = Depends(get_session)
):
    """
    卸载已安装的执行器pip包（不删除数据库记录）
    """
    import subprocess
    import sys
    
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        if not plugin.plugin_code:
            return respModel.error_resp(msg="插件代码为空")
        
        # 执行 pip uninstall
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", plugin.plugin_code],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return respModel.ok_resp(
                obj={"output": result.stdout},
                msg=f"执行器 {plugin.plugin_code} 卸载成功"
            )
        else:
            return respModel.error_resp(
                msg=f"卸载失败: {result.stderr or result.stdout}"
            )
    
    except subprocess.TimeoutExpired:
        return respModel.error_resp(msg="卸载超时")
    except Exception as e:
        return respModel.error_resp(msg=f"卸载失败: {str(e)}")


@module_route.post("/reparseKeywords", summary="重新解析插件关键字")
async def reparse_keywords(
    id: int = Query(..., description="执行器插件ID"),
    session: Session = Depends(get_session)
):
    """
    重新解析插件的关键字定义
    从数据库中的 plugin_content（ZIP包）重新提取并更新 keywords 字段
    """
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        if not plugin.plugin_content:
            return respModel.error_resp(msg="插件内容为空，请先上传执行器")
        
        # 1. 解码并解压到临时目录
        zip_bytes = base64.b64decode(plugin.plugin_content)
        extract_dir = get_temp_subdir("executor") / f"reparse_{plugin.plugin_code}_{uuid.uuid4().hex[:8]}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 查找解压后的根目录
            items = list(extract_dir.iterdir())
            if len(items) == 1 and items[0].is_dir():
                plugin_root = items[0]
            else:
                plugin_root = extract_dir
            
            # 2. 重新解析关键字
            keywords = _parse_keywords_yaml(plugin_root)
            
            # 3. 更新数据库
            plugin.keywords = json.dumps(keywords) if keywords else None
            plugin.modify_time = datetime.now()
            session.add(plugin)
            session.commit()
            
            keywords_count = len(keywords) if keywords else 0
            
            return respModel.ok_resp(
                obj={
                    "id": plugin.id,
                    "keywords_count": keywords_count,
                    "keywords": keywords
                },
                msg=f"重新解析成功，共 {keywords_count} 个关键字"
            )
        
        finally:
            # 清理临时目录
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
    
    except Exception as e:
        import traceback
        return respModel.error_resp(msg=f"重新解析失败: {str(e)}\n{traceback.format_exc()}")
