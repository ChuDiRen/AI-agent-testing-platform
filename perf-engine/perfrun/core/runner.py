"""
k6 测试执行器
"""
import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .generator import K6ScriptGenerator
except ImportError:
    from generator import K6ScriptGenerator


class K6Runner:
    """k6 测试运行器"""
    
    def __init__(
        self,
        k6_path: Optional[str] = None,
        output_dir: Optional[Path] = None,
        output_format: str = "json",
        verbose: bool = False
    ):
        self.k6_path = k6_path or self._find_k6()
        self.output_dir = output_dir or Path("../reports")
        self.output_format = output_format
        self.verbose = verbose
        self.generator = K6ScriptGenerator()
        
        # 创建脚本目录
        self.scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_k6(self) -> str:
        """查找 k6 可执行文件"""
        k6_path = shutil.which("k6")
        if k6_path:
            return k6_path
        
        # Windows 常见路径
        windows_paths = [
            r"C:\Program Files\k6\k6.exe",
            r"C:\ProgramData\chocolatey\bin\k6.exe",
        ]
        for path in windows_paths:
            if os.path.exists(path):
                return path
        
        return "k6"  # 默认使用 PATH 中的 k6
    
    def check_k6_installed(self) -> bool:
        """检查 k6 是否已安装"""
        try:
            result = subprocess.run(
                [self.k6_path, "version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                if self.verbose:
                    print(f"k6 版本: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        return False
    
    def generate_script(self, case: Dict[str, Any]) -> Path:
        """生成 k6 脚本"""
        script_content = self.generator.generate(case)
        
        # 生成脚本文件名
        case_name = case.get("name", "test").replace(" ", "_")
        script_path = self.scripts_dir / f"{case_name}.js"
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        return script_path
    
    def run_single(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        case_name = case.get("name", "未命名测试")
        print(f"\n▶ 执行测试: {case_name}")
        
        # 生成脚本
        script_path = self.generate_script(case)
        if self.verbose:
            print(f"  脚本路径: {script_path}")
        
        # 准备输出文件
        output_file = self.output_dir / f"{case_name.replace(' ', '_')}_result.json"
        
        # 构建 k6 命令
        cmd = [
            self.k6_path,
            "run",
            "--out", f"json={output_file}",
            str(script_path)
        ]
        
        if self.verbose:
            print(f"  命令: {' '.join(cmd)}")
        
        # 执行测试
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.scripts_dir)
            )
            
            success = result.returncode == 0
            
            if self.verbose or not success:
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            
            # 解析结果
            summary = self._parse_output(result.stdout)
            
            return {
                "name": case_name,
                "success": success,
                "script_path": str(script_path),
                "output_file": str(output_file),
                "summary": summary,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "name": case_name,
                "success": False,
                "error": str(e)
            }
    
    def run_all(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """运行所有测试用例"""
        results = []
        for case in cases:
            result = self.run_single(case)
            results.append(result)
        return results
    
    def _parse_output(self, stdout: str) -> Dict[str, Any]:
        """解析 k6 输出"""
        summary = {}
        
        lines = stdout.split("\n")
        for line in lines:
            # 解析 http_reqs
            if "http_reqs" in line and ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        value = parts[1].strip().split()[0]
                        summary["http_reqs"] = int(value)
                    except (ValueError, IndexError):
                        pass
            
            # 解析 http_req_duration
            if "http_req_duration" in line:
                if "avg=" in line:
                    try:
                        avg_part = line.split("avg=")[1].split()[0]
                        summary["http_req_duration_avg"] = float(avg_part.replace("ms", "").replace("s", "000"))
                    except (ValueError, IndexError):
                        pass
                if "p(95)=" in line:
                    try:
                        p95_part = line.split("p(95)=")[1].split()[0]
                        summary["http_req_duration_p95"] = float(p95_part.replace("ms", "").replace("s", "000"))
                    except (ValueError, IndexError):
                        pass
        
        return summary
