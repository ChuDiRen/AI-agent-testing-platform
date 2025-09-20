# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告初始化脚本
创建示例测试报告数据
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.entity.test_report import TestReport, ReportStatus, ReportType
from app.entity.test_case import TestCase
from app.entity.agent import Agent
from app.entity.user import User

logger = get_logger(__name__)


def create_test_report_examples():
    """
    创建测试报告示例数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建测试报告示例数据...")
        
        # 获取用户和代理
        admin_user = db.query(User).filter(User.username == "admin").first()
        tester = db.query(User).filter(User.username == "tester").first()
        developer1 = db.query(User).filter(User.username == "developer1").first()
        
        test_agent = db.query(Agent).filter(Agent.name == "自动化测试生成器").first()
        security_agent = db.query(Agent).filter(Agent.name == "安全扫描助手").first()
        
        # 获取一些测试用例
        login_case = db.query(TestCase).filter(TestCase.name == "用户登录功能测试").first()
        security_case = db.query(TestCase).filter(TestCase.name == "SQL注入安全测试").first()
        
        if not admin_user:
            logger.error("未找到管理员用户，请先运行基础初始化脚本")
            return
        
        # 创建测试报告数据
        reports_data = [
            {
                "name": "用户管理模块功能测试报告",
                "description": "用户管理模块的完整功能测试报告，包含登录、注册、权限等功能的测试结果",
                "report_type": ReportType.EXECUTION.value,
                "test_case_id": login_case.id if login_case else None,
                "agent_id": test_agent.id if test_agent else None,
                "created_by_id": tester.id if tester else admin_user.id,
                "total_cases": 25,
                "passed_cases": 22,
                "failed_cases": 2,
                "skipped_cases": 1,
                "blocked_cases": 0,
                "summary": "用户管理模块整体功能正常，发现2个轻微问题需要修复",
                "content": {
                    "test_environment": {
                        "os": "Ubuntu 20.04",
                        "browser": "Chrome 120.0",
                        "database": "PostgreSQL 14",
                        "server": "Nginx 1.20"
                    },
                    "test_results": [
                        {"module": "用户登录", "passed": 8, "failed": 0, "skipped": 0},
                        {"module": "用户注册", "passed": 7, "failed": 1, "skipped": 0},
                        {"module": "密码管理", "passed": 5, "failed": 1, "skipped": 1},
                        {"module": "权限控制", "passed": 2, "failed": 0, "skipped": 0}
                    ],
                    "defects": [
                        {
                            "id": "BUG-001",
                            "title": "注册邮箱验证失败",
                            "severity": "Medium",
                            "status": "Open"
                        },
                        {
                            "id": "BUG-002", 
                            "title": "密码强度提示不准确",
                            "severity": "Low",
                            "status": "Open"
                        }
                    ]
                },
                "issues": [
                    {
                        "type": "功能缺陷",
                        "description": "邮箱验证码发送失败",
                        "severity": "medium",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "days_ago": 7
            },
            {
                "name": "系统安全测试报告",
                "description": "系统安全漏洞扫描和渗透测试报告",
                "report_type": ReportType.DETAILED.value,
                "test_case_id": security_case.id if security_case else None,
                "agent_id": security_agent.id if security_agent else None,
                "created_by_id": tester.id if tester else admin_user.id,
                "total_cases": 15,
                "passed_cases": 13,
                "failed_cases": 1,
                "skipped_cases": 0,
                "blocked_cases": 1,
                "summary": "系统安全性整体良好，发现1个中等风险漏洞需要修复",
                "content": {
                    "scan_scope": ["Web应用", "API接口", "数据库", "服务器配置"],
                    "vulnerability_summary": {
                        "critical": 0,
                        "high": 0,
                        "medium": 1,
                        "low": 2,
                        "info": 5
                    },
                    "findings": [
                        {
                            "title": "CSRF保护缺失",
                            "severity": "Medium",
                            "description": "部分表单缺少CSRF token保护",
                            "recommendation": "为所有表单添加CSRF token验证"
                        }
                    ]
                },
                "issues": [
                    {
                        "type": "安全漏洞",
                        "description": "CSRF保护缺失",
                        "severity": "medium",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "days_ago": 5
            },
            {
                "name": "AI代理性能测试报告",
                "description": "AI代理在不同负载下的性能表现测试报告",
                "report_type": ReportType.SUMMARY.value,
                "test_case_id": None,
                "agent_id": test_agent.id if test_agent else None,
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "total_cases": 10,
                "passed_cases": 8,
                "failed_cases": 2,
                "skipped_cases": 0,
                "blocked_cases": 0,
                "summary": "AI代理在正常负载下性能良好，高负载时响应时间略有增加",
                "content": {
                    "performance_metrics": {
                        "average_response_time": "2.3s",
                        "max_response_time": "8.5s",
                        "throughput": "45 requests/min",
                        "error_rate": "0.2%"
                    },
                    "load_test_results": [
                        {"concurrent_users": 10, "avg_response": "1.8s", "success_rate": "100%"},
                        {"concurrent_users": 50, "avg_response": "2.3s", "success_rate": "99.8%"},
                        {"concurrent_users": 100, "avg_response": "4.1s", "success_rate": "98.5%"}
                    ]
                },
                "issues": [
                    {
                        "type": "性能问题",
                        "description": "高并发时响应时间过长",
                        "severity": "low",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "days_ago": 3
            },
            {
                "name": "API接口集成测试报告",
                "description": "系统API接口的集成测试和兼容性测试报告",
                "report_type": ReportType.EXECUTION.value,
                "test_case_id": None,
                "agent_id": test_agent.id if test_agent else None,
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "total_cases": 35,
                "passed_cases": 33,
                "failed_cases": 1,
                "skipped_cases": 1,
                "blocked_cases": 0,
                "summary": "API接口功能完整，兼容性良好，1个接口需要优化",
                "content": {
                    "api_coverage": {
                        "total_endpoints": 45,
                        "tested_endpoints": 43,
                        "coverage_rate": "95.6%"
                    },
                    "response_time_analysis": {
                        "fastest": "0.1s",
                        "slowest": "3.2s",
                        "average": "0.8s"
                    },
                    "status_code_distribution": {
                        "2xx": 892,
                        "4xx": 15,
                        "5xx": 3
                    }
                },
                "issues": [],
                "days_ago": 2
            },
            {
                "name": "回归测试报告",
                "description": "版本更新后的回归测试报告，确保新功能不影响现有功能",
                "report_type": ReportType.SUMMARY.value,
                "test_case_id": None,
                "agent_id": test_agent.id if test_agent else None,
                "created_by_id": tester.id if tester else admin_user.id,
                "total_cases": 50,
                "passed_cases": 47,
                "failed_cases": 2,
                "skipped_cases": 1,
                "blocked_cases": 0,
                "summary": "回归测试整体通过率94%，发现2个回归问题已修复",
                "content": {
                    "regression_scope": ["核心功能", "用户界面", "API接口", "数据库操作"],
                    "test_execution_summary": {
                        "execution_time": "4.5小时",
                        "automation_rate": "80%",
                        "manual_test_cases": 10
                    },
                    "comparison_with_baseline": {
                        "new_defects": 2,
                        "fixed_defects": 5,
                        "regression_defects": 0
                    }
                },
                "issues": [
                    {
                        "type": "回归问题",
                        "description": "用户头像上传功能异常",
                        "severity": "medium",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "days_ago": 1
            }
        ]
        
        for report_data in reports_data:
            # 检查报告是否已存在
            existing_report = db.query(TestReport).filter(TestReport.name == report_data["name"]).first()
            if existing_report:
                logger.info(f"测试报告 {report_data['name']} 已存在，跳过创建")
                continue
            
            # 计算时间
            days_ago = report_data.pop("days_ago", 0)
            start_time = datetime.utcnow() - timedelta(days=days_ago, hours=2)
            end_time = datetime.utcnow() - timedelta(days=days_ago)
            
            # 创建测试报告
            report = TestReport(
                name=report_data["name"],
                description=report_data["description"],
                report_type=report_data["report_type"],
                test_case_id=report_data["test_case_id"],
                agent_id=report_data["agent_id"],
                created_by_id=report_data["created_by_id"]
            )
            
            # 设置执行时间和统计信息
            report.start_time = start_time
            report.end_time = end_time
            report.duration = (end_time - start_time).total_seconds()
            
            # 设置统计数据
            report.update_statistics(
                total=report_data["total_cases"],
                passed=report_data["passed_cases"],
                failed=report_data["failed_cases"],
                skipped=report_data["skipped_cases"],
                blocked=report_data["blocked_cases"]
            )
            
            # 设置内容和问题
            report.content = report_data["content"]
            report.issues = report_data["issues"]
            report.summary = report_data["summary"]
            
            # 完成报告
            report.complete_execution(summary=report_data["summary"])
            
            db.add(report)
            logger.info(f"创建测试报告: {report_data['name']}")
        
        db.commit()
        logger.info("测试报告示例数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试报告示例数据失败: {str(e)}")
        raise
    finally:
        db.close()


def clear_test_report_examples():
    """
    清除测试报告示例数据
    """
    db = SessionLocal()
    try:
        logger.info("开始清除测试报告示例数据...")
        
        # 删除所有示例测试报告
        reports = db.query(TestReport).all()
        for report in reports:
            db.delete(report)
            logger.info(f"删除测试报告: {report.name}")
        
        db.commit()
        logger.info("测试报告示例数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除测试报告示例数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试报告初始化脚本")
    parser.add_argument("--create", action="store_true", help="创建测试报告示例数据")
    parser.add_argument("--clear", action="store_true", help="清除测试报告示例数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_test_report_examples()
    elif args.clear:
        clear_test_report_examples()
    else:
        print("请指定操作: --create 或 --clear")
