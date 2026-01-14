"""
Virtual File System - 统一文件系统操作接口

职责：
- 路径映射和转换
- 跨平台路径处理
- 统一的文件操作接口
- 虚拟路径管理
"""
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json

from core.logging_config import get_logger

logger = get_logger(__name__)


class PathType(str, Enum):
    """路径类型枚举"""
    ABSOLUTE = "absolute"      # 绝对路径
    RELATIVE = "relative"       # 相对路径
    VIRTUAL = "virtual"         # 虚拟路径
    MAPPED = "mapped"          # 映射路径


class Platform(str, Enum):
    """平台类型枚举"""
    WINDOWS = "windows"
    POSIX = "posix"
    AUTO = "auto"


@dataclass
class VirtualPath:
    """虚拟路径数据模型"""
    virtual_path: str
    real_path: Optional[str] = None
    path_type: PathType = PathType.VIRTUAL
    platform: Platform = Platform.AUTO
    mapped_at: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "virtual_path": self.virtual_path,
            "real_path": self.real_path,
            "path_type": self.path_type.value,
            "platform": self.platform.value,
            "mapped_at": self.mapped_at,
            "metadata": self.metadata
        }


@dataclass
class FileOperation:
    """文件操作记录"""
    operation_id: str
    operation_type: str  # read, write, delete, copy, move
    source_path: str
    target_path: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    timestamp: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}


class VirtualFileSystem:
    """
    虚拟文件系统
    
    提供统一的文件操作接口，支持路径映射和跨平台兼容性。
    """

    def __init__(self, base_virtual_path: str = "/virtual", platform: Platform = Platform.AUTO):
        """
        初始化虚拟文件系统
        
        Args:
            base_virtual_path: 基础虚拟路径
            platform: 目标平台类型
        """
        self.base_virtual_path = base_virtual_path
        self.platform = platform
        self.path_mappings: Dict[str, str] = {}  # virtual_path -> real_path
        self.operation_history: List[FileOperation] = []
        self.temp_directories: Dict[str, str] = {}  # virtual_path -> real_path
        
        # 自动检测当前平台
        if platform == Platform.AUTO:
            self.platform = Platform.WINDOWS if os.name == 'nt' else Platform.POSIX
        
        logger.info(f"虚拟文件系统初始化: base={base_virtual_path}, platform={self.platform.value}")

    def map_path(self, virtual_path: str, real_path: str, overwrite: bool = False) -> bool:
        """
        映射虚拟路径到真实路径
        
        Args:
            virtual_path: 虚拟路径
            real_path: 真实路径
            overwrite: 是否覆盖现有映射
        
        Returns:
            是否成功映射
        """
        try:
            # 标准化路径
            virtual_path = self._normalize_path(virtual_path)
            real_path = self._normalize_path(real_path)
            
            # 检查是否已存在映射
            if virtual_path in self.path_mappings and not overwrite:
                logger.warning(f"虚拟路径已存在映射: {virtual_path}")
                return False
            
            # 验证真实路径
            if not self._validate_real_path(real_path):
                logger.error(f"无效的真实路径: {real_path}")
                return False
            
            # 创建映射
            self.path_mappings[virtual_path] = real_path
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="map_path",
                source_path=virtual_path,
                target_path=real_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.info(f"路径映射成功: {virtual_path} -> {real_path}")
            return True
            
        except Exception as e:
            logger.error(f"路径映射失败: {e}", exc_info=e)
            return False

    def unmap_path(self, virtual_path: str) -> bool:
        """
        取消路径映射
        
        Args:
            virtual_path: 虚拟路径
        
        Returns:
            是否成功取消映射
        """
        try:
            virtual_path = self._normalize_path(virtual_path)
            
            if virtual_path not in self.path_mappings:
                logger.warning(f"虚拟路径不存在映射: {virtual_path}")
                return False
            
            # 移除映射
            del self.path_mappings[virtual_path]
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="unmap_path",
                source_path=virtual_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.info(f"路径映射已取消: {virtual_path}")
            return True
            
        except Exception as e:
            logger.error(f"取消路径映射失败: {e}", exc_info=e)
            return False

    def resolve_path(self, virtual_path: str) -> Optional[str]:
        """
        解析虚拟路径到真实路径
        
        Args:
            virtual_path: 虚拟路径
        
        Returns:
            真实路径，如果无法解析则返回None
        """
        try:
            virtual_path = self._normalize_path(virtual_path)
            
            # 直接映射
            if virtual_path in self.path_mappings:
                return self.path_mappings[virtual_path]
            
            # 相对路径解析
            if not os.path.isabs(virtual_path):
                # 尝试相对于基础路径解析
                base_real_path = self.path_mappings.get(self.base_virtual_path)
                if base_real_path:
                    relative_path = virtual_path.replace(self.base_virtual_path, "").lstrip("/")
                    resolved_path = Path(base_real_path) / relative_path
                    return str(resolved_path)
            
            # 如果无法解析，返回原始路径
            logger.warning(f"无法解析虚拟路径: {virtual_path}")
            return None
            
        except Exception as e:
            logger.error(f"路径解析失败: {e}", exc_info=e)
            return None

    def create_virtual_directory(self, virtual_path: str, temp: bool = True) -> bool:
        """
        创建虚拟目录
        
        Args:
            virtual_path: 虚拟路径
            temp: 是否为临时目录
        
        Returns:
            是否成功创建
        """
        try:
            virtual_path = self._normalize_path(virtual_path)
            
            # 创建真实临时目录
            if temp:
                real_temp_dir = tempfile.mkdtemp(prefix="vfs_")
                self.temp_directories[virtual_path] = real_temp_dir
                success = self.map_path(virtual_path, real_temp_dir)
            else:
                # 使用映射的目录
                real_path = self.resolve_path(virtual_path)
                if real_path:
                    Path(real_path).mkdir(parents=True, exist_ok=True)
                    success = True
                else:
                    # 创建临时目录
                    real_temp_dir = tempfile.mkdtemp(prefix="vfs_")
                    self.temp_directories[virtual_path] = real_temp_dir
                    success = self.map_path(virtual_path, real_temp_dir)
            
            if success:
                logger.info(f"虚拟目录创建成功: {virtual_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"创建虚拟目录失败: {e}", exc_info=e)
            return False

    def read_file(self, virtual_path: str) -> Optional[str]:
        """
        读取虚拟文件
        
        Args:
            virtual_path: 虚拟文件路径
        
        Returns:
            文件内容，如果读取失败则返回None
        """
        try:
            real_path = self.resolve_path(virtual_path)
            if not real_path or not os.path.exists(real_path):
                logger.error(f"虚拟文件不存在: {virtual_path}")
                return None
            
            # 读取文件
            with open(real_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="read_file",
                source_path=virtual_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.debug(f"文件读取成功: {virtual_path}")
            return content
            
        except Exception as e:
            # 记录失败操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="read_file",
                source_path=virtual_path,
                success=False,
                error_message=str(e)
            )
            self.operation_history.append(operation)
            
            logger.error(f"读取文件失败: {virtual_path} - {e}", exc_info=e)
            return None

    def write_file(self, virtual_path: str, content: str, overwrite: bool = False) -> bool:
        """
        写入虚拟文件
        
        Args:
            virtual_path: 虚拟文件路径
            content: 文件内容
            overwrite: 是否覆盖现有文件
        
        Returns:
            是否成功写入
        """
        try:
            real_path = self.resolve_path(virtual_path)
            if not real_path:
                logger.error(f"无法解析虚拟路径: {virtual_path}")
                return False
            
            # 检查文件是否存在
            if os.path.exists(real_path) and not overwrite:
                logger.error(f"文件已存在且不允许覆盖: {virtual_path}")
                return False
            
            # 确保目录存在
            os.makedirs(os.path.dirname(real_path), exist_ok=True)
            
            # 写入文件
            with open(real_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="write_file",
                source_path=virtual_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.info(f"文件写入成功: {virtual_path}")
            return True
            
        except Exception as e:
            # 记录失败操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="write_file",
                source_path=virtual_path,
                success=False,
                error_message=str(e)
            )
            self.operation_history.append(operation)
            
            logger.error(f"写入文件失败: {virtual_path} - {e}", exc_info=e)
            return False

    def delete_file(self, virtual_path: str) -> bool:
        """
        删除虚拟文件
        
        Args:
            virtual_path: 虚拟文件路径
        
        Returns:
            是否成功删除
        """
        try:
            real_path = self.resolve_path(virtual_path)
            if not real_path or not os.path.exists(real_path):
                logger.error(f"虚拟文件不存在: {virtual_path}")
                return False
            
            # 删除文件
            os.remove(real_path)
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="delete_file",
                source_path=virtual_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.info(f"文件删除成功: {virtual_path}")
            return True
            
        except Exception as e:
            # 记录失败操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="delete_file",
                source_path=virtual_path,
                success=False,
                error_message=str(e)
            )
            self.operation_history.append(operation)
            
            logger.error(f"删除文件失败: {virtual_path} - {e}", exc_info=e)
            return False

    def copy_file(self, source_virtual_path: str, target_virtual_path: str) -> bool:
        """
        复制虚拟文件
        
        Args:
            source_virtual_path: 源虚拟路径
            target_virtual_path: 目标虚拟路径
        
        Returns:
            是否成功复制
        """
        try:
            source_real_path = self.resolve_path(source_virtual_path)
            target_real_path = self.resolve_path(target_virtual_path)
            
            if not source_real_path or not os.path.exists(source_real_path):
                logger.error(f"源文件不存在: {source_virtual_path}")
                return False
            
            if not target_real_path:
                logger.error(f"无法解析目标路径: {target_virtual_path}")
                return False
            
            # 复制文件
            shutil.copy2(source_real_path, target_real_path)
            
            # 记录操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="copy_file",
                source_path=source_virtual_path,
                target_path=target_virtual_path,
                success=True
            )
            self.operation_history.append(operation)
            
            logger.info(f"文件复制成功: {source_virtual_path} -> {target_virtual_path}")
            return True
            
        except Exception as e:
            # 记录失败操作
            operation = FileOperation(
                operation_id=str(uuid.uuid4()),
                operation_type="copy_file",
                source_path=source_virtual_path,
                target_path=target_virtual_path,
                success=False,
                error_message=str(e)
            )
            self.operation_history.append(operation)
            
            logger.error(f"复制文件失败: {source_virtual_path} -> {target_virtual_path} - {e}", exc_info=e)
            return False

    def list_files(self, virtual_directory: str) -> List[str]:
        """
        列出虚拟目录中的文件
        
        Args:
            virtual_directory: 虚拟目录路径
        
        Returns:
            文件路径列表
        """
        try:
            real_path = self.resolve_path(virtual_directory)
            if not real_path or not os.path.exists(real_path):
                logger.error(f"虚拟目录不存在: {virtual_directory}")
                return []
            
            # 列出文件
            files = []
            for item in os.listdir(real_path):
                item_path = os.path.join(real_path, item)
                virtual_item_path = os.path.join(virtual_directory, item)
                files.append(virtual_item_path)
            
            logger.debug(f"列出文件成功: {virtual_directory} ({len(files)} 个文件)")
            return files
            
        except Exception as e:
            logger.error(f"列出文件失败: {virtual_directory} - {e}", exc_info=e)
            return []

    def exists(self, virtual_path: str) -> bool:
        """
        检查虚拟路径是否存在
        
        Args:
            virtual_path: 虚拟路径
        
        Returns:
            是否存在
        """
        try:
            real_path = self.resolve_path(virtual_path)
            if real_path:
                return os.path.exists(real_path)
            return False
            
        except Exception as e:
            logger.error(f"检查路径存在性失败: {virtual_path} - {e}", exc_info=e)
            return False

    def get_path_info(self, virtual_path: str) -> Optional[Dict[str, Any]]:
        """
        获取路径信息
        
        Args:
            virtual_path: 虚拟路径
        
        Returns:
            路径信息字典
        """
        try:
            real_path = self.resolve_path(virtual_path)
            if not real_path:
                return None
            
            path_info = {
                "virtual_path": virtual_path,
                "real_path": real_path,
                "exists": os.path.exists(real_path),
                "is_file": os.path.isfile(real_path) if os.path.exists(real_path) else False,
                "is_directory": os.path.isdir(real_path) if os.path.exists(real_path) else False,
                "platform": self.platform.value
            }
            
            if os.path.exists(real_path):
                stat = os.stat(real_path)
                path_info.update({
                    "size": stat.st_size,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            
            return path_info
            
        except Exception as e:
            logger.error(f"获取路径信息失败: {virtual_path} - {e}", exc_info=e)
            return None

    def cleanup(self):
        """清理虚拟文件系统资源"""
        try:
            # 清理临时目录
            for virtual_path, real_path in self.temp_directories.items():
                if os.path.exists(real_path):
                    shutil.rmtree(real_path)
                    logger.info(f"清理临时目录: {virtual_path}")
            
            # 清空映射
            self.path_mappings.clear()
            self.temp_directories.clear()
            
            logger.info("虚拟文件系统清理完成")
            
        except Exception as e:
            logger.error(f"清理虚拟文件系统失败: {e}", exc_info=e)

    def _normalize_path(self, path: str) -> str:
        """标准化路径"""
        # 移除多余的斜杠
        path = path.replace("\\", "/")  # 统一使用正斜杠
        path = "/".join(p for p in path.split("/") if p)  # 移除空段
        path = path.rstrip("/")  # 移除末尾斜杠
        
        return path if path else "/"

    def _validate_real_path(self, real_path: str) -> bool:
        """验证真实路径"""
        try:
            # 检查路径格式
            if not real_path or not isinstance(real_path, str):
                return False
            
            # 检查路径长度（跨平台限制）
            if len(real_path) > 260:  # Windows路径限制
                return False
            
            return True
            
        except Exception:
            return False

    def get_mappings(self) -> Dict[str, str]:
        """获取所有路径映射"""
        return self.path_mappings.copy()

    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取操作历史"""
        return [op.to_dict() for op in self.operation_history[-limit:]]

    def export_config(self) -> Dict[str, Any]:
        """导出虚拟文件系统配置"""
        return {
            "base_virtual_path": self.base_virtual_path,
            "platform": self.platform.value,
            "path_mappings": self.path_mappings,
            "temp_directories": self.temp_directories,
            "exported_at": datetime.utcnow().isoformat()
        }

    def import_config(self, config: Dict[str, Any]) -> bool:
        """导入虚拟文件系统配置"""
        try:
            self.base_virtual_path = config.get("base_virtual_path", "/virtual")
            platform_str = config.get("platform", "auto")
            self.platform = Platform(platform_str) if platform_str != "auto" else Platform.AUTO
            self.path_mappings = config.get("path_mappings", {})
            self.temp_directories = config.get("temp_directories", {})
            
            logger.info("虚拟文件系统配置导入成功")
            return True
            
        except Exception as e:
            logger.error(f"导入虚拟文件系统配置失败: {e}", exc_info=e)
            return False


# 全局虚拟文件系统实例
_vfs_instance: Optional[VirtualFileSystem] = None


def get_virtual_file_system() -> VirtualFileSystem:
    """获取全局虚拟文件系统实例"""
    global _vfs_instance
    if _vfs_instance is None:
        _vfs_instance = VirtualFileSystem()
    return _vfs_instance


def create_vfs_instance(base_path: str = "/virtual", platform: Platform = Platform.AUTO) -> VirtualFileSystem:
    """创建新的虚拟文件系统实例"""
    return VirtualFileSystem(base_virtual_path=base_path, platform=platform)
