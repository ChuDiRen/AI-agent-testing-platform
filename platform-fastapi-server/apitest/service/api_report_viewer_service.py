"""
报告查看Service
提供报告查找、路径解析等功能
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select

from apitest.model.ApiHistoryModel import ApiHistory
from core.logger import get_logger

logger = get_logger(__name__)


class ReportViewerService:
    def __init__(self, session: Session, base_dir: Path, report_dir: Path):
        self.session = session
        self.base_dir = base_dir
        self.report_dir = report_dir
    
    def find_report_file(self, target_report_path: Path) -> Optional[Path]:
        """
        智能查找报告文件
        
        查找顺序：
        1. 目标目录下的 complete.html
        2. 目标目录下的 index.html
        3. 关联的 venv/site-packages/reports/complete.html
        """
        if not target_report_path:
            return None
        
        # 1. 目标目录下的 complete.html
        if target_report_path.exists():
            complete_file = target_report_path / "complete.html"
            if complete_file.exists():
                return complete_file
            
            # 2. 目标目录下的 index.html
            index_file = target_report_path / "index.html"
            if index_file.exists():
                return index_file
        
        # 3. 查找关联的执行器 venv 中的报告
        try:
            executor_base = target_report_path.parent
            
            if executor_base.exists():
                for plugin_dir in executor_base.iterdir():
                    if plugin_dir.is_dir() and plugin_dir.name.startswith("plugin_"):
                        # Windows
                        venv_report = plugin_dir / "venv" / "Lib" / "site-packages" / "reports" / "complete.html"
                        if venv_report.exists():
                            logger.info(f"在 venv 中找到报告: {venv_report}")
                            return venv_report
                        
                        # Linux
                        venv_lib = plugin_dir / "venv" / "lib"
                        if venv_lib.exists():
                            for py_dir in venv_lib.iterdir():
                                if py_dir.name.startswith("python"):
                                    venv_report = py_dir / "site-packages" / "reports" / "complete.html"
                                    if venv_report.exists():
                                        logger.info(f"在 venv 中找到报告: {venv_report}")
                                        return venv_report
        except Exception as e:
            logger.warning(f"查找 venv 报告失败: {e}")
        
        return None
    
    def get_report_by_history_id(self, history_id: int) -> Optional[Path]:
        """通过 history_id 获取报告路径"""
        history = self.session.get(ApiHistory, history_id)
        if history and history.allure_report_path:
            report_path = Path(history.allure_report_path)
            if not report_path.is_absolute():
                return self.base_dir / report_path
            return report_path
        return None
    
    def get_report_by_execution_uuid(self, execution_uuid: str) -> Optional[Path]:
        """通过 execution_uuid 获取报告路径"""
        statement = select(ApiHistory).where(
            ApiHistory.execution_uuid == execution_uuid
        ).limit(1)
        history = self.session.exec(statement).first()
        
        if history and history.allure_report_path:
            report_path = Path(history.allure_report_path)
            if not report_path.is_absolute():
                return self.base_dir / report_path
            return report_path
        return None
    
    def list_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有可用的测试报告"""
        statement = select(ApiHistory).where(
            ApiHistory.allure_report_path.isnot(None)
        ).order_by(ApiHistory.create_time.desc()).limit(limit)
        
        histories = self.session.exec(statement).all()
        
        result_list = []
        for history in histories:
            report_path = Path(history.allure_report_path)
            exists = report_path.exists() if history.allure_report_path else False
            
            item = {
                "id": history.id,
                "test_name": history.test_name,
                "test_status": history.test_status,
                "execution_uuid": history.execution_uuid,
                "project_id": history.project_id,
                "plan_id": history.plan_id,
                "case_info_id": history.case_info_id,
                "report_exists": exists,
                "report_path": str(report_path.relative_to(self.report_dir)) if exists else None,
                "create_time": history.create_time.isoformat() if history.create_time else None,
                "finish_time": history.finish_time.isoformat() if history.finish_time else None,
                "view_url": f"/ApiReportViewer/view?history_id={history.id}",
                "download_url": f"/ApiReportViewer/download?history_id={history.id}"
            }
            result_list.append(item)
        
        return result_list
    
    def check_report_exists(self, report_path: Path) -> bool:
        """检查报告是否存在"""
        if not report_path:
            return False
        return self.find_report_file(report_path) is not None
