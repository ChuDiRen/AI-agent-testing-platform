"""
用例生成器基类
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class BaseGenerator:
    """用例生成器基类"""
    
    def __init__(self, examples_dir: Path):
        self.examples_dir = examples_dir
    
    def _get_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        """获取保存路径"""
        if save_path:
            return Path(save_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)[:50]
        return self.examples_dir / dir_name / f"{timestamp}_{safe_name}.yaml"
    
    def _save_case(self, save_file: Path, case: Dict[str, Any]) -> None:
        """保存用例到文件"""
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            yaml.dump(case, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def _build_result(
        self,
        case: Dict[str, Any],
        save_file: Path,
        engine_type: str,
        message: str,
        **extra
    ) -> Dict[str, Any]:
        """构建返回结果"""
        result = {
            "success": True,
            "message": message,
            "case_content": case,
            "save_path": str(save_file),
            "engine_type": engine_type
        }
        result.update(extra)
        return result
