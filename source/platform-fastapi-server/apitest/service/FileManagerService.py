"""文件管理服务"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

class FileManagerService:
    """管理临时YAML文件和报告文件"""
    
    # 基础路径配置
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    TEMP_DIR = BASE_DIR / "temp"
    YAML_DIR = TEMP_DIR / "yaml_cases"
    REPORT_DIR = TEMP_DIR / "allure_reports"
    LOG_DIR = TEMP_DIR / "logs"
    
    @classmethod
    def init_directories(cls):
        """初始化必要的目录"""
        cls.TEMP_DIR.mkdir(exist_ok=True)
        cls.YAML_DIR.mkdir(exist_ok=True)
        cls.REPORT_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def create_test_workspace(cls, test_id: int) -> tuple[Path, Path, Path]:
        """
        创建测试工作空间
        
        Args:
            test_id: 测试ID
            
        Returns:
            (yaml_dir, report_dir, log_file)元组
        """
        cls.init_directories()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        workspace_name = f"test_{test_id}_{timestamp}"
        
        # 创建YAML用例目录
        yaml_dir = cls.YAML_DIR / workspace_name
        yaml_dir.mkdir(exist_ok=True)
        
        # 创建报告目录
        report_dir = cls.REPORT_DIR / workspace_name
        report_dir.mkdir(exist_ok=True)
        
        # 创建日志文件
        log_file = cls.LOG_DIR / f"{workspace_name}.log"
        
        return yaml_dir, report_dir, log_file
    
    @classmethod
    def write_yaml_file(cls, yaml_dir: Path, filename: str, content: str) -> Path:
        """
        写入YAML文件
        
        Args:
            yaml_dir: YAML目录
            filename: 文件名
            content: YAML内容
            
        Returns:
            文件路径
        """
        file_path = yaml_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    @classmethod
    def read_file(cls, file_path: Path) -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串，如果失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None
    
    @classmethod
    def cleanup_workspace(cls, workspace_path: Path):
        """
        清理工作空间
        
        Args:
            workspace_path: 工作空间路径
        """
        try:
            if workspace_path.exists():
                shutil.rmtree(workspace_path)
        except Exception as e:
            print(f"清理工作空间失败: {e}")
    
    @classmethod
    def cleanup_old_files(cls, days: int = 7):
        """
        清理旧文件
        
        Args:
            days: 保留天数
        """
        import time
        
        current_time = time.time()
        max_age = days * 24 * 60 * 60  # 转换为秒
        
        for directory in [cls.YAML_DIR, cls.REPORT_DIR, cls.LOG_DIR]:
            if not directory.exists():
                continue
                
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        file_age = current_time - item.stat().st_mtime
                        if file_age > max_age:
                            item.unlink()
                    elif item.is_dir():
                        dir_age = current_time - item.stat().st_mtime
                        if dir_age > max_age:
                            shutil.rmtree(item)
                except Exception as e:
                    print(f"清理文件失败 {item}: {e}")
    
    @classmethod
    def get_report_path(cls, test_id: int, timestamp: str) -> Optional[Path]:
        """
        获取报告路径
        
        Args:
            test_id: 测试ID
            timestamp: 时间戳
            
        Returns:
            报告路径，如果不存在返回None
        """
        workspace_name = f"test_{test_id}_{timestamp}"
        report_dir = cls.REPORT_DIR / workspace_name
        
        if report_dir.exists():
            return report_dir
        return None
    
    @classmethod
    def list_yaml_files(cls, yaml_dir: Path) -> list[Path]:
        """
        列出YAML目录中的所有文件
        
        Args:
            yaml_dir: YAML目录
            
        Returns:
            YAML文件路径列表
        """
        if not yaml_dir.exists():
            return []
        
        return list(yaml_dir.glob("*.yaml")) + list(yaml_dir.glob("*.yml"))
