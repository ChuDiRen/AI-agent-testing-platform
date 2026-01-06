"""
代码质量检查和优化工具

功能：
- 检查未使用的导入
- 检查代码风格
- 统计代码行数
- 生成优化报告
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self, project_root: str):
        """初始化检查器"""
        self.project_root = Path(project_root)
        self.python_files: List[Path] = []
        self.issues: Dict[str, List[str]] = {
            "unused_imports": [],
            "missing_docstrings": [],
            "long_functions": [],
            "code_smells": []
        }
    
    def scan_project(self):
        """扫描项目中的所有Python文件"""
        print("🔍 扫描项目文件...")
        
        # 排除的目录
        exclude_dirs = {
            "__pycache__", ".git", ".venv", "venv", 
            "node_modules", ".pytest_cache", "dist", "build"
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    self.python_files.append(file_path)
        
        print(f"   找到 {len(self.python_files)} 个Python文件")
    
    def check_unused_imports(self):
        """检查未使用的导入"""
        print("\n📦 检查未使用的导入...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析AST
                tree = ast.parse(content)
                
                # 提取导入
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                
                # 检查使用情况（简化版）
                for imp in imports:
                    # 排除常见的必需导入
                    if imp in ['typing', 'abc', '__future__']:
                        continue
                    
                    # 简单检查：在代码中是否出现
                    if content.count(imp) <= 1:  # 只出现在import语句中
                        self.issues["unused_imports"].append(
                            f"{file_path.relative_to(self.project_root)}: {imp}"
                        )
            
            except Exception as e:
                print(f"   ⚠️  解析失败: {file_path.name} - {e}")
    
    def check_docstrings(self):
        """检查缺失的文档字符串"""
        print("\n📝 检查文档字符串...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # 检查类
                    if isinstance(node, ast.ClassDef):
                        if not ast.get_docstring(node):
                            self.issues["missing_docstrings"].append(
                                f"{file_path.relative_to(self.project_root)}: 类 {node.name}"
                            )
                    
                    # 检查函数（排除私有函数）
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_') and not ast.get_docstring(node):
                            self.issues["missing_docstrings"].append(
                                f"{file_path.relative_to(self.project_root)}: 函数 {node.name}"
                            )
            
            except Exception as e:
                print(f"   ⚠️  解析失败: {file_path.name} - {e}")
    
    def check_function_length(self, max_lines: int = 50):
        """检查过长的函数"""
        print(f"\n📏 检查函数长度（阈值: {max_lines}行）...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    content = ''.join(lines)
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # 计算函数行数
                        func_lines = node.end_lineno - node.lineno + 1
                        
                        if func_lines > max_lines:
                            self.issues["long_functions"].append(
                                f"{file_path.relative_to(self.project_root)}: "
                                f"{node.name} ({func_lines}行)"
                            )
            
            except Exception as e:
                print(f"   ⚠️  解析失败: {file_path.name} - {e}")
    
    def check_code_smells(self):
        """检查代码异味"""
        print("\n🔎 检查代码异味...")
        
        patterns = {
            "print语句": r'\bprint\s*\(',
            "TODO注释": r'#\s*TODO',
            "FIXME注释": r'#\s*FIXME',
            "硬编码密码": r'password\s*=\s*["\'][^"\']+["\']',
        }
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for smell_name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.issues["code_smells"].append(
                            f"{file_path.relative_to(self.project_root)}: "
                            f"{smell_name} ({len(matches)}处)"
                        )
            
            except Exception as e:
                print(f"   ⚠️  读取失败: {file_path.name} - {e}")
    
    def generate_statistics(self) -> Dict[str, int]:
        """生成代码统计"""
        print("\n📊 生成代码统计...")
        
        stats = {
            "total_files": len(self.python_files),
            "total_lines": 0,
            "total_code_lines": 0,
            "total_comment_lines": 0,
            "total_blank_lines": 0
        }
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                stats["total_lines"] += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        stats["total_blank_lines"] += 1
                    elif stripped.startswith('#'):
                        stats["total_comment_lines"] += 1
                    else:
                        stats["total_code_lines"] += 1
            
            except Exception as e:
                print(f"   ⚠️  读取失败: {file_path.name} - {e}")
        
        return stats
    
    def generate_report(self) -> str:
        """生成优化报告"""
        report = []
        report.append("=" * 60)
        report.append("代码质量检查报告")
        report.append("=" * 60)
        
        # 统计信息
        stats = self.generate_statistics()
        report.append("\n📊 代码统计:")
        report.append(f"   总文件数: {stats['total_files']}")
        report.append(f"   总行数: {stats['total_lines']}")
        report.append(f"   代码行数: {stats['total_code_lines']}")
        report.append(f"   注释行数: {stats['total_comment_lines']}")
        report.append(f"   空白行数: {stats['total_blank_lines']}")
        
        # 问题统计
        report.append("\n🔍 问题统计:")
        total_issues = sum(len(issues) for issues in self.issues.values())
        report.append(f"   总问题数: {total_issues}")
        
        for category, issues in self.issues.items():
            if issues:
                report.append(f"\n   {category}: {len(issues)}个")
                for issue in issues[:5]:  # 只显示前5个
                    report.append(f"      - {issue}")
                if len(issues) > 5:
                    report.append(f"      ... 还有 {len(issues) - 5} 个")
        
        # 优化建议
        report.append("\n💡 优化建议:")
        if self.issues["unused_imports"]:
            report.append("   1. 清理未使用的导入")
        if self.issues["missing_docstrings"]:
            report.append("   2. 补充缺失的文档字符串")
        if self.issues["long_functions"]:
            report.append("   3. 重构过长的函数")
        if self.issues["code_smells"]:
            report.append("   4. 修复代码异味")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def run_all_checks(self):
        """运行所有检查"""
        self.scan_project()
        self.check_unused_imports()
        self.check_docstrings()
        self.check_function_length()
        self.check_code_smells()
        
        # 生成并打印报告
        report = self.generate_report()
        print("\n" + report)
        
        # 保存报告
        report_path = self.project_root / "code_quality_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已保存到: {report_path}")


def main():
    """主函数"""
    import sys
    
    # 获取项目根目录
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    print("🚀 代码质量检查工具")
    print("=" * 60)
    
    checker = CodeQualityChecker(project_root)
    checker.run_all_checks()


if __name__ == "__main__":
    main()

