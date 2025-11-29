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
from pathlib import Path
from datetime import datetime

from ..model.PluginModel import Plugin
from ..schemas.plugin_schema import (
    PluginCreate, PluginUpdate, PluginQuery, PluginResponse,
    PluginRegisterRequest, PluginHealthCheck
)
from core.database import get_session
from core.resp_model import respModel
from config.dev_settings import settings  # TODO: 根据实际环境切换为统一配置入口
from core.minio_client import minio_client

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
    """检查插件API健康状态"""
    try:
        plugin = session.get(Plugin, id)
        if not plugin:
            return respModel.error_resp(msg="插件不存在")
        
        # 调用插件的健康检查API
        start_time = time.time()
        
        # 命令行插件检查逻辑：
        # 1. 检查工作目录是否存在
        # 2. (可选) 尝试验证命令是否可用
        
        if not plugin.work_dir:
             return respModel.error_resp(msg="插件未配置工作目录")
             
        if not os.path.exists(plugin.work_dir):
            return respModel.error_resp(msg=f"插件工作目录不存在: {plugin.work_dir}")

        # 简单地返回健康状态，因为目录存在
        response_time = (time.time() - start_time) * 1000
        
        return respModel.ok_resp(obj=PluginHealthCheck(
            plugin_code=plugin.plugin_code,
            status="healthy",
            version=plugin.version,
            response_time_ms=response_time
        ))
    
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


@module_route.post("/upload", summary="上传插件包")
async def upload_plugin(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """上传插件ZIP包并自动安装"""
    # 为了在 finally 中访问，先初始化临时变量
    extract_dir = None
    plugin_root_fixed = None
    temp_zip_path = None

    try:
        # 1. 使用配置中的插件根目录（通常指向文件服务器挂载路径）
        base_dir = settings.PLUGIN_BASE_DIR
        if base_dir is None:
            # 兜底: 如果未配置则退回到项目根目录同级 plugins
            base_dir = Path(__file__).resolve().parents[2].parent / "plugins"
        if not base_dir.exists():
            base_dir.mkdir(parents=True)

        # 2. 保存上传文件到临时 zip, 便于解析和后续上传 MinIO
        temp_id = str(uuid.uuid4())
        temp_zip_path = base_dir / f"{temp_id}.zip"

        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. 解压到临时目录
        extract_dir = base_dir / f"tmp_{temp_id}"
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # 4. 解析插件信息
        # 查找解压后的根目录（临时）
        items = list(extract_dir.iterdir())
        if len(items) == 1 and items[0].is_dir():
            temp_plugin_root = items[0]
        else:
            temp_plugin_root = extract_dir
            
        # 初始信息（先根据上传文件名推断，稍后再确定 plugin_root_fixed）
        plugin_name = file.filename.replace('.zip', '')
        plugin_code = plugin_name.lower().replace('-', '_')
        command = ""
        description = "通过上传安装的插件"
        version = "1.0.0"
        dependencies = []
        capabilities = {}
        
        # 尝试查找主包名（在临时解压根目录中）
        package_name = ""
        for item in temp_plugin_root.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                if item.name not in ['tests', 'examples', 'docs']:
                    package_name = item.name
                    break
        
        # 自动生成命令
        if package_name:
            command = f"python -m {package_name}.cli"
            if "engine" in plugin_code:
                description = f"{plugin_name} 执行引擎"
        
        if not command:
            command = "python main.py"

        # 解析依赖 (requirements.txt)
        requirements_txt = temp_plugin_root / "requirements.txt"
        if requirements_txt.exists():
            try:
                with open(requirements_txt, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith("git+"):
                            dependencies.append(line)
            except Exception:
                pass
                
        # 尝试从 setup.py 提取信息
        setup_py = temp_plugin_root / "setup.py"
        if setup_py.exists():
            try:
                with open(setup_py, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # 提取 description
                    desc_match = re.search(r'description=["\']([^"\']+)["\']', content)
                    if desc_match:
                        description = desc_match.group(1)
                        
                    # 提取 version
                    ver_match = re.search(r'version=["\']([^"\']+)["\']', content)
                    if ver_match:
                        version = ver_match.group(1)

                    # 提取 keywords 作为 features
                    kw_match = re.search(r'keywords=["\']([^"\']+)["\']', content)
                    if kw_match:
                        keywords = kw_match.group(1).split()
                        capabilities["features"] = keywords
            except Exception:
                pass
        
        # 查找 plugin.json (优先级最高)
        plugin_json = temp_plugin_root / "plugin.json"
        if plugin_json.exists():
            try:
                with open(plugin_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "description" in data: description = data["description"]
                    if "version" in data: version = data["version"]
                    if "command" in data: command = data["command"]
                    if "capabilities" in data: capabilities = data["capabilities"]
                    if "dependencies" in data: dependencies = data["dependencies"]
            except Exception:
                pass

        # 5. 上传原始 ZIP 到 MinIO, 对象命名为 plugins/{plugin_code}/latest.zip
        #   注意: 这里重新打开临时 zip 文件作为流上传
        minio_object = None
        if temp_zip_path is not None and temp_zip_path.exists():
            with open(temp_zip_path, "rb") as fp:
                fp.seek(0, os.SEEK_END)
                size = fp.tell()
                fp.seek(0)
                object_name = f"plugins/{plugin_code}/latest.zip"
                minio_object = minio_client.upload_plugin_zip(fp, object_name, length=size)

        # 6. 注册到数据库(本地不再保留固定 plugins 目录, work_dir 暂设为 plugin_code 逻辑路径)
        existing = session.exec(
            select(Plugin).where(Plugin.plugin_code == plugin_code)
        ).first()
        
        if existing:
            # 更新
            existing.plugin_name = plugin_name
            # work_dir 暂存逻辑路径, 后续执行可根据 storage_path 从 MinIO 下载到本地
            existing.work_dir = f"plugins/{plugin_code}"
            existing.command = command
            existing.description = description
            existing.dependencies = json.dumps(dependencies) if dependencies else None
            existing.capabilities = json.dumps(capabilities) if capabilities else None
            if minio_object is not None:
                existing.storage_path = minio_object
            existing.modify_time = datetime.now()
            session.add(existing)
            session.commit()
            action = "更新"
        else:
            # 新增
            new_plugin = Plugin(
                plugin_name=plugin_name,
                plugin_code=plugin_code,
                plugin_type="executor",
                version=version,
                command=command,
                # work_dir 暂存逻辑路径, 实际包存储在 MinIO
                work_dir=f"plugins/{plugin_code}",
                description=description,
                author="User Upload",
                is_enabled=1,
                dependencies=json.dumps(dependencies) if dependencies else None,
                capabilities=json.dumps(capabilities) if capabilities else None,
                storage_path=minio_object
            )
            session.add(new_plugin)
            session.commit()
            action = "安装"
            
        return respModel.ok_resp(msg=f"插件 {plugin_name} {action}成功")

    except Exception as e:
        return respModel.error_resp(msg=f"上传失败: {str(e)}")

    finally:
        # 无论成功还是失败，都尝试清理临时解压目录 tmp_xxx
        try:
            if extract_dir is not None and extract_dir.exists():
                # 只删除 tmp_xxx 目录自身，避免误删固定工作目录
                shutil.rmtree(extract_dir)
            if temp_zip_path is not None and temp_zip_path.exists():
                os.remove(temp_zip_path)
        except Exception:
            # 清理失败不影响主流程
            pass
