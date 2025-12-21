"""
插件安装服务
安装到后端服务运行环境
"""
import base64
import io
import logging
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

from core.temp_manager import get_temp_subdir

logger = logging.getLogger(__name__)

# 安装任务状态存储（内存中，生产环境可用 Redis）
_install_tasks: Dict[int, Dict[str, Any]] = {}

# 获取当前后端服务运行的 Python 解释器
CURRENT_PYTHON = sys.executable


class PluginInstaller:
    """插件安装器"""
    
    # 安装目录基础路径
    INSTALL_BASE = "plugins"
    # 状态保留时间（秒）- 安装完成后保留状态5分钟
    STATUS_RETAIN_SECONDS = 300
    
    @staticmethod
    def get_install_dir(plugin_code: str) -> Path:
        """获取插件安装目录"""
        return get_temp_subdir("executor") / f"plugin_{plugin_code}"
    
    
    @staticmethod
    def get_install_status(plugin_id: int) -> Dict[str, Any]:
        """获取安装状态"""
        task_info = _install_tasks.get(plugin_id)
        if not task_info:
            return {
                "status": "unknown",
                "message": "未找到安装任务",
                "progress": 0
            }
        
        # 检查状态是否过期（仅对已完成/失败的状态检查）
        if task_info.get("status") in ["completed", "failed"]:
            updated_at = task_info.get("updated_at")
            if updated_at:
                elapsed = (datetime.now() - updated_at).total_seconds()
                if elapsed > PluginInstaller.STATUS_RETAIN_SECONDS:
                    # 状态已过期，清除并返回 unknown
                    del _install_tasks[plugin_id]
                    return {
                        "status": "unknown",
                        "message": "安装任务已过期",
                        "progress": 0
                    }
        
        return task_info
    
    @staticmethod
    def update_install_status(plugin_id: int, status: str, message: str, progress: int, **kwargs):
        """更新安装状态"""
        _install_tasks[plugin_id] = {
            "status": status,
            "message": message,
            "progress": progress,
            "updated_at": datetime.now(),  # 添加时间戳
            **kwargs
        }
    
    @staticmethod
    def install_plugin(
        plugin_id: int,
        plugin_code: str,
        plugin_content: str,
        command: str
    ) -> Dict[str, Any]:
        """
        安装插件（同步执行，供线程池调用）

        安装到后端服务运行的环境

        Args:
            plugin_id: 插件ID
            plugin_code: 插件代码
            plugin_content: Base64 编码的 ZIP 内容
            command: 主命令

        Returns:
            安装结果
        """
        install_dir = None
        install_log = []

        try:
            # 1. 更新状态：开始安装
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在解压插件包...", 10
            )

            # 使用后端服务运行的 Python 解释器
            python_exe = CURRENT_PYTHON
            install_log.append(f"[{datetime.now().isoformat()}] 开始安装插件 {plugin_code}")
            install_log.append(f"[{datetime.now().isoformat()}] Python 环境: {python_exe}")

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

            # 3. 使用后端服务的环境
            logger.info("使用后端服务环境安装插件")
            install_log.append(f"[{datetime.now().isoformat()}] 使用后端服务环境")
            
            # 4. 安装插件依赖（使用国内镜像加速）
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在检查依赖...", 30
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
                
                # 逐个安装依赖，更新进度（30% -> 50%）
                installed_count = 0
                failed_pkgs = []
                total_reqs = len(filtered_reqs)
                for idx, req in enumerate(filtered_reqs):
                    pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0]
                    # 计算进度：30% + (idx / total) * 20%，范围 30-50%
                    progress = 30 + int((idx / max(total_reqs, 1)) * 20)
                    PluginInstaller.update_install_status(
                        plugin_id, "installing", f"正在安装依赖 ({idx+1}/{total_reqs}): {pkg_name}...", progress
                    )
                    
                    req_args = [
                        python_exe, "-m", "pip", "install", "--upgrade", req,
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
                        failed_pkgs.append(pkg_name)
                
                install_log.append(f"[{datetime.now().isoformat()}] requirements.txt: 成功安装 {installed_count} 个包")
                if failed_pkgs:
                    install_log.append(f"[{datetime.now().isoformat()}] 安装失败的包: {', '.join(failed_pkgs)}")
            
            # 4.2 安装插件本身（使用 Popen 实时更新进度）
            PluginInstaller.update_install_status(
                plugin_id, "installing", f"正在安装插件 {plugin_code}...", 55
            )
            
            pip_args = [
                python_exe, "-m", "pip", "install", "--upgrade", ".",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
            ]
            
            # 使用 Popen 实时读取输出并更新进度
            import time
            process = subprocess.Popen(
                pip_args,
                cwd=str(source_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            stdout_lines = []
            progress_base = 55
            progress_increment = 0
            install_start_time = time.time()
            last_update_time = time.time()
            
            # 实时读取输出并更新进度
            while True:
                # 非阻塞读取（Windows 兼容）
                try:
                    line = process.stdout.readline()
                except:
                    line = ""
                
                if line:
                    stdout_lines.append(line.strip())
                    # 根据输出内容判断进度
                    if "Collecting" in line or "Downloading" in line:
                        progress_increment = min(progress_increment + 2, 20)
                    elif "Installing" in line or "Successfully" in line:
                        progress_increment = min(progress_increment + 5, 20)
                
                # 检查进程是否结束
                if process.poll() is not None:
                    break
                
                # 每2秒更新一次进度显示
                current_time = time.time()
                total_elapsed = int(current_time - install_start_time)
                if current_time - last_update_time > 2:
                    current_progress = min(progress_base + progress_increment, 75)
                    PluginInstaller.update_install_status(
                        plugin_id, "installing", f"正在安装插件 {plugin_code}... (已用时 {total_elapsed}秒)", current_progress
                    )
                    last_update_time = current_time
                
                # 超时检查（10分钟）
                if total_elapsed > 600:
                    process.kill()
                    raise subprocess.TimeoutExpired(pip_args, 600)
            
            # 读取剩余输出
            remaining = process.stdout.read()
            if remaining:
                stdout_lines.extend(remaining.strip().split('\n'))
            
            result_stdout = '\n'.join(stdout_lines)
            install_log.append(f"[{datetime.now().isoformat()}] pip install 输出:\n{result_stdout}")
            
            if process.returncode != 0:
                raise Exception(f"pip install 失败: {result_stdout}")
            
            # 5. 验证命令是否可用
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在验证安装...", 80
            )
            
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
            
            # 6. 清理临时安装目录（pip install 已将包安装到 Python 环境，源码不再需要）
            PluginInstaller.update_install_status(
                plugin_id, "installing", "正在清理临时文件...", 90
            )
            
            if install_dir and install_dir.exists():
                try:
                    shutil.rmtree(install_dir, ignore_errors=True)
                    install_log.append(f"[{datetime.now().isoformat()}] 已清理临时安装目录: {install_dir}")
                except Exception as cleanup_err:
                    install_log.append(f"[{datetime.now().isoformat()}] 清理临时目录失败: {cleanup_err}")
            
            # 7. 更新状态：安装成功
            PluginInstaller.update_install_status(
                plugin_id, "completed",
                f"安装成功，命令: {command}",
                100,
                command_path=str(cmd_path) if cmd_path.exists() else None
            )
            
            return {
                "success": True,
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
    def uninstall_plugin(plugin_code: str) -> Tuple[bool, str]:
        """
        卸载插件
        
        Args:
            plugin_code: 插件代码
        
        Returns:
            (是否成功, 消息)
        """
        try:
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
    def check_health(plugin_code: str, command: str) -> Dict[str, Any]:
        """
        检查插件健康状态
        
        Args:
            plugin_code: 插件代码
            command: 主命令
        
        Returns:
            健康检查结果
        """
        result = {
            "status": "unknown",
            "message": "",
            "command_path": None,
            "dependencies_check": {}
        }
        
        try:
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
