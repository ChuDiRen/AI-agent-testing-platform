"""
插件管理 API 控制器
提供插件注册、查询、启用/禁用等功能
"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlmodel import Session, select, or_, func
from typing import List
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
import tempfile
from pathlib import Path
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
    session: Session = Depends(get_session)
):
    """注销（删除）插件"""
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        session.delete(plugin)
        session.commit()
        
        return respModel.ok_resp(msg="插件注销成功")
    
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
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        start_time = time.time()
        
        # 检查逻辑：
        # 1. 如果有 plugin_content（内嵌执行器），检查是否已安装
        # 2. 如果有 work_dir，检查目录是否存在
        
        if plugin.plugin_content:
            # 内嵌执行器：检查命令是否可用
            import subprocess
            import sys
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
                    msg = f"命令 {plugin.command} 已安装"
                else:
                    status = "not_installed"
                    msg = f"命令 {plugin.command} 未安装，请点击安装按钮"
            except Exception:
                status = "unknown"
                msg = "无法检测命令状态"
        elif plugin.work_dir:
            if os.path.exists(plugin.work_dir):
                status = "healthy"
                msg = "工作目录存在"
            else:
                status = "unhealthy"
                msg = f"工作目录不存在: {plugin.work_dir}"
        else:
            status = "not_configured"
            msg = "插件未配置"

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
        
        return respModel.ok_resp(obj=result)
    
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
        
        # 2. 解压到临时目录解析信息
        temp_id = str(uuid.uuid4())
        extract_dir = Path(tempfile.gettempdir()) / f"executor_{temp_id}"
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
        
        if not command:
            return respModel.error_resp(msg="未找到 console_scripts 命令定义，请确保 setup.py 中定义了 entry_points")
        
        # 4. 保存到数据库
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
            existing.work_dir = ""  # 无固定工作目录，动态安装
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
                work_dir="",  # 无固定工作目录
                plugin_content=zip_base64,
                description=description,
                author="User Upload",
                is_enabled=1,
                dependencies=json.dumps(dependencies) if dependencies else None,
                capabilities=json.dumps({"console_scripts": console_scripts})
            )
            session.add(new_plugin)
            session.commit()
            session.refresh(new_plugin)
            action = "安装"
            plugin_id = new_plugin.id
        
        return respModel.ok_resp(
            obj={
                "id": plugin_id,
                "command": command,
                "console_scripts": console_scripts
            },
            msg=f"执行器 {plugin_name} {action}成功，命令: {command}"
        )
    
    except Exception as e:
        import traceback
        return respModel.error_resp(msg=f"上传失败: {str(e)}\n{traceback.format_exc()}")
    
    finally:
        if extract_dir and extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)


@module_route.post("/installExecutor", summary="安装执行器到本地（pip install）")
async def install_executor(
    id: int = Query(..., description="执行器插件ID"),
    session: Session = Depends(get_session)
):
    """
    从数据库读取执行器内容，解压并执行 pip install . 安装为命令行工具
    安装完成后删除源文件，只保留可执行命令
    """
    import subprocess
    import sys
    
    extract_dir = None
    
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        if not plugin.plugin_content:
            return respModel.error_resp(msg="插件内容为空，请先上传执行器")
        
        # 1. 解码并解压到固定目录
        zip_bytes = base64.b64decode(plugin.plugin_content)
        
        # 使用固定安装目录（项目根目录同级的 executors 目录）
        executors_base = Path(__file__).resolve().parents[2].parent / "executors"
        executors_base.mkdir(parents=True, exist_ok=True)
        
        extract_dir = executors_base / plugin.plugin_code
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
        
        # 2. 执行 pip install .（标准安装，不依赖源目录）
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "."],
            cwd=str(install_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return respModel.error_resp(
                msg=f"安装失败: {result.stderr or result.stdout}"
            )
        
        # 3. 安装成功后删除解压的源文件目录
        if extract_dir and extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)
        
        # 4. 更新插件状态（不再需要 work_dir，命令已全局可用）
        plugin.work_dir = ""  # 标准安装不需要工作目录
        plugin.modify_time = datetime.now()
        session.add(plugin)
        session.commit()
        
        return respModel.ok_resp(
            obj={
                "command": plugin.command,
                "output": result.stdout
            },
            msg=f"执行器安装成功，可使用命令: {plugin.command}"
        )
    
    except Exception as e:
        import traceback
        return respModel.error_resp(msg=f"安装失败: {str(e)}\n{traceback.format_exc()}")
