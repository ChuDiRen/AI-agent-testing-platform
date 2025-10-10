# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告生成服务
"""
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class ReportService:
    """测试报告生成服务"""

    @staticmethod
    def generate_execution_report(execution_result: Dict[str, Any], case_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成执行报告

        Args:
            execution_result: 执行结果
            case_info: 用例信息

        Returns:
            报告数据
        """
        report = {
            "report_info": {
                "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "case_id": case_info.get("case_id"),
                "case_name": case_info.get("name", "未知用例"),
                "suite_name": case_info.get("suite_name", "未知套件"),
                "executed_by": case_info.get("executed_by", "未知用户")
            },
            "execution_summary": {
                "status": execution_result.get("status", "unknown"),
                "execution_time": execution_result.get("execution_time", 0),
                "start_time": execution_result.get("start_time"),
                "end_time": execution_result.get("end_time"),
                "total_steps": len(execution_result.get("step_results", [])),
                "passed_steps": 0,
                "failed_steps": 0,
                "error_steps": 0
            },
            "step_details": [],
            "request_response_data": [],
            "error_analysis": {
                "has_errors": False,
                "error_count": 0,
                "errors": []
            },
            "variables_context": execution_result.get("context", {}),
            "logs": execution_result.get("logs", "")
        }

        # 分析步骤结果
        step_results = execution_result.get("step_results", [])
        for step in step_results:
            step_status = step.get("status", "unknown")

            # 更新统计
            if step_status == "success":
                report["execution_summary"]["passed_steps"] += 1
            elif step_status == "failed":
                report["execution_summary"]["failed_steps"] += 1
            elif step_status == "error":
                report["execution_summary"]["error_steps"] += 1

            # 添加步骤详情
            step_detail = {
                "step_number": step.get("step_number"),
                "step_name": step.get("step_name"),
                "status": step_status,
                "output": step.get("output", ""),
                "error_message": step.get("error_message"),
                "response_data": step.get("response_data")
            }
            report["step_details"].append(step_detail)

            # 收集请求响应数据
            if step.get("response_data"):
                report["request_response_data"].append({
                    "step_number": step.get("step_number"),
                    "step_name": step.get("step_name"),
                    "request_response": step.get("response_data")
                })

            # 收集错误信息
            if step_status in ["failed", "error"] and step.get("error_message"):
                report["error_analysis"]["has_errors"] = True
                report["error_analysis"]["error_count"] += 1
                report["error_analysis"]["errors"].append({
                    "step_number": step.get("step_number"),
                    "step_name": step.get("step_name"),
                    "error_message": step.get("error_message"),
                    "error_type": step_status
                })

        return report

    @staticmethod
    def generate_suite_report(suite_executions: List[Dict[str, Any]], suite_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成套件执行报告

        Args:
            suite_executions: 套件执行结果列表
            suite_info: 套件信息

        Returns:
            套件报告数据
        """
        report = {
            "report_info": {
                "report_id": f"suite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "suite_id": suite_info.get("suite_id"),
                "suite_name": suite_info.get("name", "未知套件"),
                "total_cases": len(suite_executions)
            },
            "execution_summary": {
                "total_cases": len(suite_executions),
                "passed_cases": 0,
                "failed_cases": 0,
                "error_cases": 0,
                "total_execution_time": 0,
                "average_execution_time": 0
            },
            "case_results": [],
            "error_summary": {
                "total_errors": 0,
                "common_errors": {}
            },
            "performance_metrics": {
                "fastest_case": None,
                "slowest_case": None,
                "execution_times": []
            }
        }

        total_time = 0
        execution_times = []

        for execution in suite_executions:
            status = execution.get("status", "unknown")
            execution_time = execution.get("execution_time", 0)

            # 更新统计
            if status == "success":
                report["execution_summary"]["passed_cases"] += 1
            elif status == "failed":
                report["execution_summary"]["failed_cases"] += 1
            elif status == "error":
                report["execution_summary"]["error_cases"] += 1

            total_time += execution_time
            execution_times.append({
                "case_name": execution.get("case_name", "未知用例"),
                "execution_time": execution_time
            })

            # 添加用例结果
            case_result = {
                "case_id": execution.get("case_id"),
                "case_name": execution.get("case_name", "未知用例"),
                "status": status,
                "execution_time": execution_time,
                "error_message": execution.get("error_message"),
                "step_count": len(execution.get("step_results", []))
            }
            report["case_results"].append(case_result)

            # 收集错误信息
            if status in ["failed", "error"] and execution.get("error_message"):
                report["error_summary"]["total_errors"] += 1
                error_msg = execution.get("error_message", "")
                if error_msg not in report["error_summary"]["common_errors"]:
                    report["error_summary"]["common_errors"][error_msg] = 0
                report["error_summary"]["common_errors"][error_msg] += 1

        # 计算性能指标
        report["execution_summary"]["total_execution_time"] = total_time
        if suite_executions:
            report["execution_summary"]["average_execution_time"] = total_time / len(suite_executions)

        # 找出最快和最慢的用例
        if execution_times:
            execution_times.sort(key=lambda x: x["execution_time"])
            report["performance_metrics"]["fastest_case"] = execution_times[0]
            report["performance_metrics"]["slowest_case"] = execution_times[-1]
            report["performance_metrics"]["execution_times"] = execution_times

        return report

    @staticmethod
    def export_report_to_json(report: Dict[str, Any], file_path: str) -> bool:
        """
        导出报告为JSON文件

        Args:
            report: 报告数据
            file_path: 文件路径

        Returns:
            是否导出成功
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出JSON报告失败: {str(e)}")
            return False

    @staticmethod
    def generate_summary_statistics(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成报告统计摘要

        Args:
            reports: 报告列表

        Returns:
            统计摘要
        """
        if not reports:
            return {"message": "没有可统计的报告"}

        summary = {
            "total_reports": len(reports),
            "date_range": {
                "earliest": None,
                "latest": None
            },
            "status_distribution": {
                "success": 0,
                "failed": 0,
                "error": 0
            },
            "performance_stats": {
                "total_execution_time": 0,
                "average_execution_time": 0,
                "max_execution_time": 0,
                "min_execution_time": float('inf')
            },
            "error_analysis": {
                "total_errors": 0,
                "most_common_errors": {}
            }
        }

        total_time = 0
        execution_times = []

        for report in reports:
            # 处理日期范围
            generated_at = report.get("report_info", {}).get("generated_at")
            if generated_at:
                if not summary["date_range"]["earliest"] or generated_at < summary["date_range"]["earliest"]:
                    summary["date_range"]["earliest"] = generated_at
                if not summary["date_range"]["latest"] or generated_at > summary["date_range"]["latest"]:
                    summary["date_range"]["latest"] = generated_at

            # 处理状态分布
            status = report.get("execution_summary", {}).get("status", "unknown")
            if status in summary["status_distribution"]:
                summary["status_distribution"][status] += 1

            # 处理性能统计
            exec_time = report.get("execution_summary", {}).get("execution_time", 0)
            total_time += exec_time
            execution_times.append(exec_time)

            if exec_time > summary["performance_stats"]["max_execution_time"]:
                summary["performance_stats"]["max_execution_time"] = exec_time
            if exec_time < summary["performance_stats"]["min_execution_time"]:
                summary["performance_stats"]["min_execution_time"] = exec_time

            # 处理错误分析
            error_analysis = report.get("error_analysis", {})
            if error_analysis.get("has_errors"):
                summary["error_analysis"]["total_errors"] += error_analysis.get("error_count", 0)

        # 计算平均值
        if execution_times:
            summary["performance_stats"]["total_execution_time"] = total_time
            summary["performance_stats"]["average_execution_time"] = total_time / len(execution_times)
            if summary["performance_stats"]["min_execution_time"] == float('inf'):
                summary["performance_stats"]["min_execution_time"] = 0

        return summary