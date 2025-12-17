"""
临时文件管理模块
统一管理项目中的所有临时文件，确保它们都存放在 temp 目录下
"""
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)

# 从配置获取临时目录路径
try:
    from config.dev_settings import settings
    TEMP_DIR = settings.TEMP_DIR
except ImportError:
    # 回退：使用项目根目录下的 temp
    PROJECT_ROOT = Path(__file__).parent.parent
    TEMP_DIR = PROJECT_ROOT / "temp"


def get_temp_dir() -> Path:
    """
    获取临时文件目录，如果不存在则创建
    
    Returns:
        Path: 临时文件目录路径
    """
    if not TEMP_DIR.exists():
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def get_temp_subdir(subdir_name: str) -> Path:
    """
    获取临时文件子目录，如果不存在则创建
    
    Args:
        subdir_name: 子目录名称
        
    Returns:
        Path: 子目录路径
    """
    subdir = get_temp_dir() / subdir_name
    if not subdir.exists():
        subdir.mkdir(parents=True, exist_ok=True)
    return subdir


def create_temp_file(filename: str, subdir: str = None) -> Path:
    """
    创建临时文件路径
    
    Args:
        filename: 文件名
        subdir: 可选的子目录名
        
    Returns:
        Path: 临时文件路径
    """
    if subdir:
        base_dir = get_temp_subdir(subdir)
    else:
        base_dir = get_temp_dir()
    return base_dir / filename


def cleanup_temp_files(days: int = 7, subdir: str = None) -> dict:
    """
    清理指定天数前的临时文件
    
    Args:
        days: 清理多少天前的文件，默认7天
        subdir: 可选，只清理指定子目录
        
    Returns:
        dict: 清理结果统计
    """
    if subdir:
        target_dir = get_temp_subdir(subdir)
    else:
        target_dir = get_temp_dir()
    
    if not target_dir.exists():
        return {"deleted_files": 0, "deleted_dirs": 0, "errors": 0}
    
    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_files = 0
    deleted_dirs = 0
    errors = 0
    
    for item in target_dir.iterdir():
        try:
            # 获取修改时间
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff_time:
                if item.is_file():
                    item.unlink()
                    deleted_files += 1
                    logger.info(f"已删除临时文件: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_dirs += 1
                    logger.info(f"已删除临时目录: {item}")
        except Exception as e:
            errors += 1
            logger.error(f"删除临时文件失败 {item}: {e}")
    
    return {
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
        "errors": errors
    }


def remove_temp_dir(dir_path: Path) -> bool:
    """
    安全删除临时目录
    
    Args:
        dir_path: 要删除的目录路径
        
    Returns:
        bool: 是否删除成功
    """
    try:
        if dir_path and dir_path.exists() and str(dir_path).startswith(str(TEMP_DIR)):
            shutil.rmtree(dir_path)
            logger.debug(f"已清理临时目录: {dir_path}")
            return True
    except Exception as e:
        logger.error(f"清理临时目录失败 {dir_path}: {e}")
    return False
