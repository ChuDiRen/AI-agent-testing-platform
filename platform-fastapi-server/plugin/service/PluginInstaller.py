"""
插件安装服务
提供独立 venv 安装、卸载、状态管理等功能
"""
import subprocess
import sys
import base64
import zipfile
import io
import shutil
import logging
import platform
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from core.temp_manager import get_temp_subdir

logger = logging.getLogger(__name__)

# 安装任务状态存储（内存中，生产环境可用 Redis）
_install_tasks: Dict[int, Dict[str, Any]] = {}

# 全局线程池
_installer_executor = ThreadPoolExecutor(max_workers=3)


class PluginInstaller:
    """插件安装器"""
    
    # 安装目录基础路径
    INSTALL_BASE = "plugins"
    
    @staticmethod
    def get_install_dir(plugin_code: str) -> Path:
        """获取插件安装目录"""
        return get_temp_subdir("executor") / f"plugin_{plugin_code}"
    
    @staticmethod
    def get_venv_dir(plugin_code: str) -> Path:
        """获取插件虚拟环境目录"""
        return PluginInstaller.get_install_dir(plugin_code) / "venv"
    
    @staticmethod
    def get_venv_python(plugin_code: str) -> Path:
        """获取虚拟环境中的 Python 解释器路径"""
        venv_dir = PluginInstaller.get_venv_dir(plugin_code)
        if platform.system() == "Windows":
            return venv_dir / "Scripts" / "python.exe"
        else:
            return venv_dir / "bin" / "python"
    
    @staticmethod
    def get_venv_command(plugin_code: str, command: str) -> Path:
        """获取虚拟环境中的命令路径"""
        venv_dir = PluginInstaller.get_venv_dir(plugin_code)
        if platform.system() == "Windows":
            return venv_dir / "Scripts" / f"{command}.exe"
        else:
            return venv_dir / "bin" / command
    
    @staticmethod
    def get_install_status(plugin_id: int) -> Dict[str, Any]:
        """获取安装状态"""
        return _install_tasks.get(plugin_id, {
            "status": "unknown",
            "message": "未找到安装任务",
            "progress": 0
        })
    
    @staticmethod
    def update_install_status(plugin_id: int, status: str, message: str, progress: int, **kwargs):
        """更新安装状态"""
        _install_tasks[plugin_id] = {
            "status": status,
            "message": message,
            "progress": progress,
            **kwargs
        }
    
    @staticmethod
    def create_venv(plugin_code: str) -> Tuple[bool, str]:
        """
        创建独立虚拟环境
        
        Args:
            plugin_code: 插件代码
        
        Returns:
            (是否成功, 消息/错误)
        """
        venv_dir = PluginInstaller.get_venv_dir(plugin_code)
        
        try:
            # 如果已存在，先删除
            if venv_dir.exists():
                shutil.rmtree(venv_dir)
            
            # 创建虚拟环境（使用 --without-pip 跳过 pip 安装，大幅加速）
            logger.info(f"创建虚拟环境（无pip）: {venv_dir}")
            result = subprocess.run(
                [sys.executable, "-m", "venv", "--without-pip", str(venv_dir)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"创建虚拟环境失败: {result.stderr or result.stdout}"
            
            # 检查 Python 解释器
            venv_python = PluginInstaller.get_venv_python(plugin_code)
            if not venv_python.exists():
                return False, f"虚拟环境 Python 不存在: {venv_python}"
            
            logger.info(f"虚拟环境创建成功: {venv_dir}")
            
            # 使用 ensurepip 安装 pip（比默认方式快）
            logger.info("正在安装 pip...")
            pip_result = subprocess.run(
                [str(venv_python), "-m", "ensurepip", "--default-pip"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if pip_result.returncode != 0:
                logger.warning(f"ensurepip 失败: {pip_result.stderr}，尝试使用 get-pip.py")
                # 备用方案：直接复制系统 pip
                # 大多数情况下 ensurepip 会成功
            
            return True, str(venv_dir)
        
        except subprocess.TimeoutExpired:
            return False, "创建虚拟环境超时"
        except Exception as e:
            return False, f"创建虚拟环境异常: {str(e)}"
    
    @staticmethod
    def install_plugin(
        plugin_id: int,
        plugin_code: str,
        plugin_content: str,
        command: str,
        use_venv: bool = True
    ) -> Dict[str, Any]:
        """
        安装插件（同步执行，供线程池调用）
        
        Args:
            plugin_id: 插件ID
            plugin_code: 插件代码
            plugin_content: Base64 编码的 ZIP 内容
            command: 主命令
            use_venv: 是否使用独立虚拟环境
        
        Returns:
            安装结果
        """
        install_dir = None
        venv_path = None
        install_log = []
        
        try:
            # 1. 更新状态：开始安装
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在解压插件包...", 10
            )
            install_log.append(f"[{datetime.now().isoformat()}] 开始安装插件 {plugin_code}")
            
            # 2. 解码并解压
            zip_bytes = base64.b64decode(plugin_content)
            install_dir = PluginInstaller.get_install_dir(plugin_code)
            
            if install_dir.exists():
                shutil.rmtree(install_dir)
            install_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            
            # 查找解压后的根目录（可能有一层包装目录）
            items = list(install_dir.iterdir())
            if len(items) == 1 and items[0].is_dir():
                source_dir = items[0]
            else:
                source_dir = install_dir
            
            install_log.append(f"[{datetime.now().isoformat()}] 解压完成: {source_dir}")
            
            # 3. 创建虚拟环境（如果需要）
            if use_venv:
                PluginInstaller.update_install_status(
                    plugin_id, "installing", "正在创建虚拟环境...", 30
                )
                
                success, msg = PluginInstaller.create_venv(plugin_code)
                if not success:
                    raise Exception(msg)
                
                venv_path = str(PluginInstaller.get_venv_dir(plugin_code))
                install_log.append(f"[{datetime.now().isoformat()}] 虚拟环境创建成功: {venv_path}")
                
                python_exe = str(PluginInstaller.get_venv_python(plugin_code))
            else:
                python_exe = sys.executable
            
            # 4. 安装插件依赖（使用国内镜像加速）
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在安装依赖...", 40
            )
            
            # 4.1 先安装 requirements.txt（如果存在）
            requirements_file = source_dir / "requirements.txt"
            if requirements_file.exists():
                install_log.append(f"[{datetime.now().isoformat()}] 发现 requirements.txt，开始安装依赖...")
                
                # 读取 requirements.txt，过滤掉本地包（不在 PyPI 上的包）
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    requirements = f.readlines()
                
                # 过滤掉可能是本地包的依赖（如 HuaceAPIRunner）
                filtered_reqs = []
                skipped_reqs = []
                for req in requirements:
                    req = req.strip()
                    if not req or req.startswith('#'):
                        continue
                    # 跳过看起来像本地包的依赖（包名包含大写字母且版本为 0.0.x）
                    pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0]
                    if any(c.isupper() for c in pkg_name) and ('==0.0.' in req or '==0.1.' in req):
                        skipped_reqs.append(req)
                    else:
                        filtered_reqs.append(req)
                
                if skipped_reqs:
                    install_log.append(f"[{datetime.now().isoformat()}] 跳过本地包: {', '.join(skipped_reqs)}")
                
                # 逐个安装依赖，忽略失败的包
                installed_count = 0
                failed_pkgs = []
                for req in filtered_reqs:
                    req_args = [
                        python_exe, "-m", "pip", "install", req,
                        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                        "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
                        "-q"  # 静默模式
                    ]
                    req_result = subprocess.run(
                        req_args,
                        cwd=str(source_dir),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if req_result.returncode == 0:
                        installed_count += 1
                    else:
                        failed_pkgs.append(req.split('==')[0])
                
                install_log.append(f"[{datetime.now().isoformat()}] requirements.txt: 成功安装 {installed_count} 个包")
                if failed_pkgs:
                    install_log.append(f"[{datetime.now().isoformat()}] 安装失败的包: {', '.join(failed_pkgs)}")
            
            # 4.2 安装插件本身
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在执行 pip install...", 60
            )
            
            pip_args = [
                python_exe, "-m", "pip", "install", ".",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
            ]
            
            result = subprocess.run(
                pip_args,
                cwd=str(source_dir),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            install_log.append(f"[{datetime.now().isoformat()}] pip install 输出:\n{result.stdout}")
            if result.stderr:
                install_log.append(f"[{datetime.now().isoformat()}] pip install 错误:\n{result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"pip install 失败: {result.stderr or result.stdout}")
            
            # 5. 验证命令是否可用
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在验证安装...", 80
            )
            
            if use_venv:
                cmd_path = PluginInstaller.get_venv_command(plugin_code, command)
            else:
                cmd_path = Path(shutil.which(command) or "")
            
            if not cmd_path.exists():
                # 尝试用 --help 验证
                try:
                    verify_result = subprocess.run(
                        [python_exe, "-m", command.replace("-", "_"), "--help"],
                        capture_output=True,
                        timeout=10
                    )
                    if verify_result.returncode != 0:
                        logger.warning(f"命令 {command} 验证失败，但安装可能成功")
                except Exception:
                    pass
            
            install_log.append(f"[{datetime.now().isoformat()}] 安装完成，命令路径: {cmd_path}")
            
            # 6. 清理源码目录（安装成功后删除解压的源码，只保留 venv）
            if use_venv and source_dir != install_dir:
                try:
                    shutil.rmtree(source_dir, ignore_errors=True)
                    install_log.append(f"[{datetime.now().isoformat()}] 已清理源码目录: {source_dir}")
                except Exception as cleanup_err:
                    install_log.append(f"[{datetime.now().isoformat()}] 清理源码目录失败: {cleanup_err}")
            elif use_venv:
                # source_dir == install_dir 的情况，删除除 venv 外的所有文件
                try:
                    venv_dir = PluginInstaller.get_venv_dir(plugin_code)
                    for item in install_dir.iterdir():
                        if item != venv_dir and item.name != "venv":
                            if item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                item.unlink(missing_ok=True)
                    install_log.append(f"[{datetime.now().isoformat()}] 已清理源码文件，保留 venv 目录")
                except Exception as cleanup_err:
                    install_log.append(f"[{datetime.now().isoformat()}] 清理源码文件失败: {cleanup_err}")
            
            # 7. 更新状态：安装成功
            PluginInstaller.update_install_status(
                plugin_id, "completed",
                f"安装成功，命令: {command}",
                100,
                install_path=str(install_dir),
                venv_path=venv_path,
                command_path=str(cmd_path) if cmd_path.exists() else None
            )
            
            return {
                "success": True,
                "install_path": str(install_dir),
                "venv_path": venv_path,
                "command_path": str(cmd_path) if cmd_path.exists() else None,
                "install_log": "\n".join(install_log)
            }
        
        except subprocess.TimeoutExpired:
            error_msg = "安装超时（超过5分钟）"
            install_log.append(f"[{datetime.now().isoformat()}] 错误: {error_msg}")
            PluginInstaller.update_install_status(
                plugin_id, "failed", error_msg, 100
            )
            return {
                "success": False,
                "error": error_msg,
                "install_log": "\n".join(install_log)
            }
        
        except Exception as e:
            error_msg = f"安装异常: {str(e)}"
            install_log.append(f"[{datetime.now().isoformat()}] 错误: {error_msg}")
            PluginInstaller.update_install_status(
                plugin_id, "failed", error_msg, 100
            )
            
            # 安装失败时清理目录
            if install_dir and install_dir.exists():
                try:
                    shutil.rmtree(install_dir, ignore_errors=True)
                except Exception:
                    pass
            
            return {
                "success": False,
                "error": error_msg,
                "install_log": "\n".join(install_log)
            }
    
    @staticmethod
    def uninstall_plugin(plugin_code: str, use_venv: bool = True) -> Tuple[bool, str]:
        """
        卸载插件
        
        Args:
            plugin_code: 插件代码
            use_venv: 是否使用独立虚拟环境
        
        Returns:
            (是否成功, 消息)
        """
        try:
            install_dir = PluginInstaller.get_install_dir(plugin_code)
            
            if use_venv:
                # 直接删除整个安装目录（包含 venv）
                if install_dir.exists():
                    shutil.rmtree(install_dir)
                    return True, f"已删除插件目录: {install_dir}"
                else:
                    return True, "插件目录不存在，无需卸载"
            else:
                # 使用 pip uninstall
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", plugin_code],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return True, f"卸载成功: {result.stdout}"
                else:
                    return False, f"卸载失败: {result.stderr or result.stdout}"
        
        except Exception as e:
            return False, f"卸载异常: {str(e)}"
    
    @staticmethod
    def check_health(plugin_code: str, command: str, use_venv: bool = True) -> Dict[str, Any]:
        """
        检查插件健康状态
        
        Args:
            plugin_code: 插件代码
            command: 主命令
            use_venv: 是否使用独立虚拟环境
        
        Returns:
            健康检查结果
        """
        result = {
            "status": "unknown",
            "message": "",
            "command_path": None,
            "venv_path": None,
            "dependencies_check": {}
        }
        
        try:
            if use_venv:
                venv_dir = PluginInstaller.get_venv_dir(plugin_code)
                cmd_path = PluginInstaller.get_venv_command(plugin_code, command)
                python_exe = PluginInstaller.get_venv_python(plugin_code)
                
                # 检查 venv 是否存在
                if not venv_dir.exists():
                    result["status"] = "not_installed"
                    result["message"] = "虚拟环境不存在，请先安装插件"
                    return result
                
                result["venv_path"] = str(venv_dir)
                
                # 检查命令是否存在
                if cmd_path.exists():
                    result["command_path"] = str(cmd_path)
                    
                    # 尝试执行 --help 验证
                    try:
                        verify = subprocess.run(
                            [str(cmd_path), "--help"],
                            capture_output=True,
                            timeout=10
                        )
                        if verify.returncode == 0:
                            result["status"] = "healthy"
                            result["message"] = f"命令 {command} 可用"
                        else:
                            result["status"] = "degraded"
                            result["message"] = f"命令存在但执行异常"
                    except Exception as e:
                        result["status"] = "degraded"
                        result["message"] = f"命令验证失败: {str(e)}"
                else:
                    # 尝试通过 python -m 方式验证
                    try:
                        module_name = command.replace("-", "_")
                        verify = subprocess.run(
                            [str(python_exe), "-m", module_name, "--help"],
                            capture_output=True,
                            timeout=10
                        )
                        if verify.returncode == 0:
                            result["status"] = "healthy"
                            result["message"] = f"模块 {module_name} 可用"
                        else:
                            result["status"] = "unhealthy"
                            result["message"] = f"命令 {command} 不可用"
                    except Exception:
                        result["status"] = "unhealthy"
                        result["message"] = f"命令 {command} 不可用"
            else:
                # 检查全局命令
                cmd_path = shutil.which(command)
                if cmd_path:
                    result["command_path"] = cmd_path
                    result["status"] = "healthy"
                    result["message"] = f"命令 {command} 可用"
                else:
                    result["status"] = "unhealthy"
                    result["message"] = f"命令 {command} 不在 PATH 中"
        
        except Exception as e:
            result["status"] = "unknown"
            result["message"] = f"健康检查异常: {str(e)}"
        
        return result


# 全局安装器实例
plugin_installer = PluginInstaller()
