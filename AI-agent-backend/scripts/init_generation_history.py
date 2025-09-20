# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例生成历史初始化脚本
创建AI生成测试用例的历史记录数据
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.entity.test_case_generation_history import TestCaseGenerationHistory, GenerationStatus
from app.entity.test_case import TestCasePriority, TestCaseType
from app.entity.agent import Agent
from app.entity.user import User

logger = get_logger(__name__)


def create_generation_history_examples():
    """
    创建测试用例生成历史示例数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建测试用例生成历史数据...")
        
        # 获取用户和代理
        admin_user = db.query(User).filter(User.username == "admin").first()
        tester = db.query(User).filter(User.username == "tester").first()
        developer1 = db.query(User).filter(User.username == "developer1").first()
        developer2 = db.query(User).filter(User.username == "developer2").first()
        
        test_agent = db.query(Agent).filter(Agent.name == "自动化测试生成器").first()
        
        if not admin_user:
            logger.error("未找到管理员用户，请先运行基础初始化脚本")
            return
        
        # 创建生成历史数据
        history_data = [
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "用户登录功能需要支持用户名/邮箱登录，密码强度验证，登录失败锁定机制，记住登录状态等功能。需要测试正常登录、异常登录、安全性等场景。",
                "test_type": TestCaseType.FUNCTIONAL.value,
                "priority": TestCasePriority.P1.value,
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 8,
                "status": GenerationStatus.COMPLETED.value,
                "generation_config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "test_types": ["正向测试", "负向测试", "边界测试"],
                    "coverage_requirements": ["功能覆盖", "异常覆盖", "安全覆盖"]
                },
                "generation_result": {
                    "generated_cases": [
                        {"name": "用户名正常登录测试", "type": "正向测试"},
                        {"name": "邮箱正常登录测试", "type": "正向测试"},
                        {"name": "错误密码登录测试", "type": "负向测试"},
                        {"name": "不存在用户登录测试", "type": "负向测试"},
                        {"name": "密码强度验证测试", "type": "边界测试"},
                        {"name": "登录失败锁定测试", "type": "安全测试"},
                        {"name": "记住登录状态测试", "type": "功能测试"},
                        {"name": "并发登录测试", "type": "性能测试"}
                    ],
                    "quality_score": 0.92,
                    "coverage_analysis": {
                        "functional_coverage": "95%",
                        "boundary_coverage": "88%",
                        "security_coverage": "90%"
                    }
                },
                "days_ago": 10
            },
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "电商购物车功能，包括添加商品、修改数量、删除商品、计算总价、优惠券使用、库存检查等。需要测试各种购物场景和异常情况。",
                "test_type": TestCaseType.FUNCTIONAL.value,
                "priority": TestCasePriority.P1.value,
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 12,
                "status": GenerationStatus.COMPLETED.value,
                "generation_config": {
                    "model": "claude-3-sonnet",
                    "temperature": 0.6,
                    "max_tokens": 4096,
                    "test_types": ["功能测试", "边界测试", "异常测试"],
                    "business_scenarios": ["正常购物", "促销活动", "库存不足"]
                },
                "generation_result": {
                    "generated_cases": [
                        {"name": "添加商品到购物车", "type": "功能测试"},
                        {"name": "修改购物车商品数量", "type": "功能测试"},
                        {"name": "删除购物车商品", "type": "功能测试"},
                        {"name": "购物车总价计算", "type": "功能测试"},
                        {"name": "优惠券使用测试", "type": "功能测试"},
                        {"name": "库存不足处理", "type": "异常测试"},
                        {"name": "购物车数量上限", "type": "边界测试"},
                        {"name": "商品下架处理", "type": "异常测试"},
                        {"name": "优惠券过期处理", "type": "异常测试"},
                        {"name": "购物车持久化", "type": "功能测试"},
                        {"name": "多设备购物车同步", "type": "集成测试"},
                        {"name": "购物车性能测试", "type": "性能测试"}
                    ],
                    "quality_score": 0.89,
                    "coverage_analysis": {
                        "functional_coverage": "92%",
                        "boundary_coverage": "85%",
                        "exception_coverage": "88%"
                    }
                },
                "days_ago": 8
            },
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "API接口安全性测试，需要检查SQL注入、XSS攻击、权限绕过、数据泄露等安全漏洞。重点关注用户输入验证和权限控制。",
                "test_type": TestCaseType.SECURITY.value,
                "priority": TestCasePriority.P1.value,
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 15,
                "status": GenerationStatus.COMPLETED.value,
                "generation_config": {
                    "model": "deepseek-chat",
                    "temperature": 0.4,
                    "max_tokens": 4096,
                    "security_focus": ["注入攻击", "权限控制", "数据保护"],
                    "compliance_standards": ["OWASP Top 10", "ISO 27001"]
                },
                "generation_result": {
                    "generated_cases": [
                        {"name": "SQL注入攻击测试", "type": "安全测试"},
                        {"name": "XSS跨站脚本测试", "type": "安全测试"},
                        {"name": "CSRF跨站请求伪造测试", "type": "安全测试"},
                        {"name": "权限绕过测试", "type": "安全测试"},
                        {"name": "敏感数据泄露测试", "type": "安全测试"},
                        {"name": "文件上传安全测试", "type": "安全测试"},
                        {"name": "API认证绕过测试", "type": "安全测试"},
                        {"name": "会话管理安全测试", "type": "安全测试"},
                        {"name": "输入验证测试", "type": "安全测试"},
                        {"name": "加密传输测试", "type": "安全测试"},
                        {"name": "日志安全测试", "type": "安全测试"},
                        {"name": "错误信息泄露测试", "type": "安全测试"},
                        {"name": "暴力破解防护测试", "type": "安全测试"},
                        {"name": "业务逻辑漏洞测试", "type": "安全测试"},
                        {"name": "第三方组件安全测试", "type": "安全测试"}
                    ],
                    "quality_score": 0.94,
                    "security_coverage": {
                        "owasp_top10_coverage": "100%",
                        "authentication_coverage": "95%",
                        "authorization_coverage": "90%",
                        "data_protection_coverage": "88%"
                    }
                },
                "days_ago": 6
            },
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "移动端APP性能测试，包括启动时间、页面加载速度、内存使用、电池消耗、网络请求优化等。需要在不同设备和网络环境下测试。",
                "test_type": TestCaseType.PERFORMANCE.value,
                "priority": TestCasePriority.P2.value,
                "created_by_id": developer2.id if developer2 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 10,
                "status": GenerationStatus.COMPLETED.value,
                "generation_config": {
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 3072,
                    "performance_metrics": ["响应时间", "资源使用", "用户体验"],
                    "test_environments": ["高端设备", "中端设备", "低端设备"]
                },
                "generation_result": {
                    "generated_cases": [
                        {"name": "APP启动时间测试", "type": "性能测试"},
                        {"name": "页面加载速度测试", "type": "性能测试"},
                        {"name": "内存使用监控测试", "type": "性能测试"},
                        {"name": "CPU使用率测试", "type": "性能测试"},
                        {"name": "电池消耗测试", "type": "性能测试"},
                        {"name": "网络请求性能测试", "type": "性能测试"},
                        {"name": "图片加载优化测试", "type": "性能测试"},
                        {"name": "弱网环境测试", "type": "性能测试"},
                        {"name": "长时间运行稳定性测试", "type": "性能测试"},
                        {"name": "多任务切换性能测试", "type": "性能测试"}
                    ],
                    "quality_score": 0.87,
                    "performance_coverage": {
                        "startup_performance": "100%",
                        "runtime_performance": "90%",
                        "resource_usage": "85%",
                        "network_optimization": "88%"
                    }
                },
                "days_ago": 4
            },
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "AI聊天机器人功能测试，包括自然语言理解、上下文记忆、多轮对话、情感识别、知识问答等。需要测试各种对话场景和边界情况。",
                "test_type": TestCaseType.FUNCTIONAL.value,
                "priority": TestCasePriority.P2.value,
                "created_by_id": admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 6,
                "status": GenerationStatus.RUNNING.value,
                "generation_config": {
                    "model": "claude-3-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "ai_capabilities": ["NLU", "对话管理", "知识问答"],
                    "test_scenarios": ["日常对话", "专业咨询", "异常输入"]
                },
                "generation_result": {
                    "generated_cases": [
                        {"name": "基础问答测试", "type": "功能测试"},
                        {"name": "多轮对话测试", "type": "功能测试"},
                        {"name": "上下文理解测试", "type": "功能测试"},
                        {"name": "情感识别测试", "type": "功能测试"},
                        {"name": "知识库问答测试", "type": "功能测试"},
                        {"name": "异常输入处理测试", "type": "异常测试"}
                    ],
                    "quality_score": 0.85,
                    "ai_coverage": {
                        "nlu_coverage": "90%",
                        "dialogue_coverage": "85%",
                        "knowledge_coverage": "80%"
                    }
                },
                "days_ago": 2
            },
            {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "requirement_text": "数据备份与恢复系统测试，包括自动备份、手动备份、增量备份、全量备份、数据恢复、备份验证等功能的测试。",
                "test_type": TestCaseType.FUNCTIONAL.value,
                "priority": TestCasePriority.P3.value,
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None,
                "generated_count": 0,
                "status": GenerationStatus.FAILED.value,
                "generation_config": {
                    "model": "gpt-4",
                    "temperature": 0.6,
                    "max_tokens": 4096,
                    "backup_types": ["全量备份", "增量备份", "差异备份"],
                    "recovery_scenarios": ["完全恢复", "部分恢复", "时点恢复"]
                },
                "generation_result": {},
                "error_message": "API调用超时，生成任务失败。请检查网络连接和API配置。",
                "days_ago": 1
            }
        ]
        
        for history_item in history_data:
            # 检查历史记录是否已存在
            existing_history = db.query(TestCaseGenerationHistory).filter(
                TestCaseGenerationHistory.task_id == history_item["task_id"]
            ).first()
            if existing_history:
                logger.info(f"生成历史 {history_item['task_id']} 已存在，跳过创建")
                continue
            
            # 计算时间
            days_ago = history_item.pop("days_ago", 0)
            created_time = datetime.utcnow() - timedelta(days=days_ago)
            
            # 创建生成历史记录
            history = TestCaseGenerationHistory(
                task_id=history_item["task_id"],
                requirement_text=history_item["requirement_text"],
                test_type=history_item["test_type"],
                priority=history_item["priority"],
                created_by_id=history_item["created_by_id"],
                agent_id=history_item["agent_id"],
                generation_config=history_item["generation_config"]
            )
            
            # 设置创建时间
            history.created_at = created_time
            history.updated_at = created_time
            
            # 根据状态设置相应的时间和结果
            if history_item["status"] == GenerationStatus.COMPLETED.value:
                history.start_generation()
                history.started_at = created_time + timedelta(minutes=1)
                history.complete_generation(
                    generated_count=history_item["generated_count"],
                    result=history_item["generation_result"]
                )
                history.completed_at = created_time + timedelta(minutes=5)
            elif history_item["status"] == GenerationStatus.RUNNING.value:
                history.start_generation()
                history.started_at = created_time + timedelta(minutes=1)
                history.generated_count = history_item["generated_count"]
                history.generation_result = history_item["generation_result"]
            elif history_item["status"] == GenerationStatus.FAILED.value:
                history.start_generation()
                history.started_at = created_time + timedelta(minutes=1)
                history.fail_generation(history_item["error_message"])
                history.completed_at = created_time + timedelta(minutes=2)
            
            db.add(history)
            logger.info(f"创建测试用例生成历史: {history_item['task_id']}")
        
        db.commit()
        logger.info("测试用例生成历史数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试用例生成历史数据失败: {str(e)}")
        raise
    finally:
        db.close()


def clear_generation_history_examples():
    """
    清除测试用例生成历史数据
    """
    db = SessionLocal()
    try:
        logger.info("开始清除测试用例生成历史数据...")
        
        # 删除所有生成历史记录
        histories = db.query(TestCaseGenerationHistory).all()
        for history in histories:
            db.delete(history)
            logger.info(f"删除生成历史: {history.task_id}")
        
        db.commit()
        logger.info("测试用例生成历史数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除测试用例生成历史数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试用例生成历史初始化脚本")
    parser.add_argument("--create", action="store_true", help="创建生成历史数据")
    parser.add_argument("--clear", action="store_true", help="清除生成历史数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_generation_history_examples()
    elif args.clear:
        clear_generation_history_examples()
    else:
        print("请指定操作: --create 或 --clear")
