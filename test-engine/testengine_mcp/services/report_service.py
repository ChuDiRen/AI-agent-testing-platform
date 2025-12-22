"""
测试报告服务
从 test_runner 拆分出的报告相关功能
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class ReportService:
    """测试报告服务"""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
    
    def find_latest_report(self) -> Optional[Dict[str, Any]]:
        """查找最新的测试报告"""
        try:
            report_path = self.reports_dir / "complete.html"
            if not report_path.exists():
                html_files = list(self.reports_dir.glob("*.html"))
                if html_files:
                    report_path = max(html_files, key=lambda f: f.stat().st_mtime)
                else:
                    return None
            
            return {
                "path": str(report_path),
                "name": report_path.name,
                "size_kb": round(report_path.stat().st_size / 1024, 2),
                "modified_time": datetime.fromtimestamp(report_path.stat().st_mtime).isoformat()
            }
        except:
            return None
    
    def get_report(self, report_name: Optional[str] = None) -> Dict[str, Any]:
        """获取测试报告详情"""
        try:
            if report_name:
                report_path = self.reports_dir / report_name
            else:
                report_path = self.reports_dir / "complete.html"
            
            if not report_path.exists():
                html_files = list(self.reports_dir.glob("*.html"))
                if html_files:
                    report_path = max(html_files, key=lambda f: f.stat().st_mtime)
                else:
                    return {"success": False, "message": "未找到测试报告"}
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取统计信息
            stats = self._extract_stats(content)
            
            return {
                "success": True,
                "report_path": str(report_path),
                "report_name": report_path.name,
                "modified_time": datetime.fromtimestamp(report_path.stat().st_mtime).isoformat(),
                "size_kb": round(report_path.stat().st_size / 1024, 2),
                "statistics": stats,
                "content_preview": content[:2000] if len(content) > 2000 else content
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取报告失败: {str(e)}"}
    
    def list_reports(self, limit: int = 20) -> Dict[str, Any]:
        """列出所有测试报告"""
        try:
            reports = []
            for f in sorted(self.reports_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
                reports.append({
                    "name": f.name,
                    "path": str(f),
                    "size_kb": round(f.stat().st_size / 1024, 2),
                    "modified_time": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "reports_dir": str(self.reports_dir),
                "count": len(reports),
                "reports": reports[:limit]
            }
        except Exception as e:
            return {"success": False, "message": f"列出报告失败: {str(e)}"}
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成报告摘要（用于 LLM 展示）"""
        report = self.get_report()
        if not report.get("success"):
            return report
        
        stats = report.get("statistics", {})
        passed = stats.get("passed", 0)
        failed = stats.get("failed", 0)
        total = passed + failed
        
        # 生成摘要
        if total == 0:
            status = "⚪ 无测试结果"
            pass_rate = 0
        elif failed == 0:
            status = "✅ 全部通过"
            pass_rate = 100
        else:
            status = "❌ 存在失败"
            pass_rate = round(passed / total * 100, 1)
        
        return {
            "success": True,
            "summary": {
                "status": status,
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{pass_rate}%",
                "report_path": report.get("report_path"),
                "modified_time": report.get("modified_time")
            },
            "display": f"""
📊 **测试报告摘要**
━━━━━━━━━━━━━━━━━━━━━━
状态: {status}
总计: {total} 个用例
通过: {passed} ✅
失败: {failed} ❌
通过率: {pass_rate}%
━━━━━━━━━━━━━━━━━━━━━━
报告: {report.get('report_name')}
时间: {report.get('modified_time')}
"""
        }
    
    def _extract_stats(self, content: str) -> Dict[str, int]:
        """从报告内容提取统计信息"""
        stats = {}
        passed_match = re.search(r'(\d+)\s*passed', content, re.IGNORECASE)
        failed_match = re.search(r'(\d+)\s*failed', content, re.IGNORECASE)
        if passed_match:
            stats['passed'] = int(passed_match.group(1))
        if failed_match:
            stats['failed'] = int(failed_match.group(1))
        return stats
