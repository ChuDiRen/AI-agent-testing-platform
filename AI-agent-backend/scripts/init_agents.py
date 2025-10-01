"""
AI代理初始化脚本
创建典型AI代理的示例数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.entity.agent import Agent, AgentType, AgentStatus
from app.entity.user import User

logger = get_logger(__name__)


def create_agent_examples():
    """
    创建AI代理示例数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建AI代理示例数据...")
        
        # 获取用户ID
        admin_user = db.query(User).filter(User.username == "admin").first()
        developer1 = db.query(User).filter(User.username == "developer1").first()
        developer2 = db.query(User).filter(User.username == "developer2").first()
        tester = db.query(User).filter(User.username == "tester").first()
        
        if not admin_user:
            logger.error("未找到管理员用户，请先运行基础初始化脚本")
            return
        
        # 创建AI代理数据
        agents_data = [
            {
                "name": "智能客服助手",
                "type": AgentType.CHAT.value,
                "description": "专业的客服对话代理，能够处理常见的客户咨询和问题解答",
                "created_by_id": admin_user.id,
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "system_prompt": "你是一个专业的客服助手，请友好、耐心地回答用户的问题。",
                    "knowledge_base": ["产品手册", "常见问题", "服务条款"],
                    "response_style": "professional",
                    "language": "zh-CN"
                }
            },
            {
                "name": "代码审查助手",
                "type": AgentType.ANALYSIS.value,
                "description": "自动化代码审查代理，检查代码质量、安全性和最佳实践",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "config": {
                    "model": "claude-3-sonnet",
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "system_prompt": "你是一个专业的代码审查专家，请仔细分析代码并提供改进建议。",
                    "check_items": ["代码规范", "安全漏洞", "性能优化", "可维护性"],
                    "languages": ["Python", "JavaScript", "Java", "Go"],
                    "severity_levels": ["critical", "major", "minor", "info"]
                }
            },
            {
                "name": "任务规划助手",
                "type": AgentType.TASK.value,
                "description": "智能任务分解和规划代理，帮助将复杂项目拆分为可执行的任务",
                "created_by_id": developer2.id if developer2 else admin_user.id,
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 3072,
                    "system_prompt": "你是一个项目管理专家，擅长将复杂任务分解为清晰的执行步骤。",
                    "planning_methods": ["WBS", "敏捷", "瀑布"],
                    "output_format": "markdown",
                    "include_timeline": True,
                    "include_dependencies": True
                }
            },
            {
                "name": "自动化测试生成器",
                "type": AgentType.TESTING.value,
                "description": "基于需求自动生成测试用例的代理，支持多种测试类型",
                "created_by_id": tester.id if tester else admin_user.id,
                "config": {
                    "model": "deepseek-chat",
                    "temperature": 0.4,
                    "max_tokens": 4096,
                    "system_prompt": "你是一个测试专家，能够根据需求生成全面的测试用例。",
                    "test_types": ["功能测试", "边界测试", "异常测试", "性能测试"],
                    "test_levels": ["单元测试", "集成测试", "系统测试", "验收测试"],
                    "output_format": "structured",
                    "include_data": True
                }
            },
            {
                "name": "文档生成助手",
                "type": AgentType.TASK.value,
                "description": "自动生成技术文档和API文档的代理",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "config": {
                    "model": "claude-3-sonnet",
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "system_prompt": "你是一个技术写作专家，能够生成清晰、准确的技术文档。",
                    "doc_types": ["API文档", "用户手册", "开发指南", "部署文档"],
                    "formats": ["Markdown", "HTML", "PDF"],
                    "include_examples": True,
                    "language": "zh-CN"
                }
            },
            {
                "name": "数据分析助手",
                "type": AgentType.ANALYSIS.value,
                "description": "智能数据分析代理，提供数据洞察和可视化建议",
                "created_by_id": admin_user.id,
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.2,
                    "max_tokens": 3072,
                    "system_prompt": "你是一个数据分析专家，能够从数据中发现有价值的洞察。",
                    "analysis_types": ["描述性分析", "诊断性分析", "预测性分析", "处方性分析"],
                    "visualization_tools": ["matplotlib", "plotly", "echarts"],
                    "statistical_methods": ["回归分析", "聚类分析", "时间序列"],
                    "output_format": "report"
                }
            },
            {
                "name": "安全扫描助手",
                "type": AgentType.TESTING.value,
                "description": "自动化安全漏洞扫描和分析代理",
                "created_by_id": tester.id if tester else admin_user.id,
                "config": {
                    "model": "claude-3-sonnet",
                    "temperature": 0.1,
                    "max_tokens": 4096,
                    "system_prompt": "你是一个网络安全专家，专注于发现和分析安全漏洞。",
                    "scan_types": ["SQL注入", "XSS", "CSRF", "权限绕过"],
                    "severity_levels": ["Critical", "High", "Medium", "Low"],
                    "compliance_standards": ["OWASP", "ISO27001", "等保2.0"],
                    "report_format": "detailed"
                }
            },
            {
                "name": "多语言翻译助手",
                "type": AgentType.CUSTOM.value,
                "description": "专业的多语言翻译代理，支持技术文档翻译",
                "created_by_id": admin_user.id,
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "system_prompt": "你是一个专业的翻译专家，能够准确翻译技术文档和业务内容。",
                    "supported_languages": ["en", "zh-CN", "ja", "ko", "fr", "de"],
                    "translation_types": ["技术文档", "用户界面", "营销文案", "法律文件"],
                    "quality_check": True,
                    "preserve_formatting": True
                }
            }
        ]
        
        for agent_data in agents_data:
            # 检查代理是否已存在
            existing_agent = db.query(Agent).filter(Agent.name == agent_data["name"]).first()
            if existing_agent:
                logger.info(f"代理 {agent_data['name']} 已存在，跳过创建")
                continue
            
            # 创建代理
            agent = Agent(
                name=agent_data["name"],
                type=agent_data["type"],
                description=agent_data["description"],
                created_by_id=agent_data["created_by_id"],
                config=agent_data["config"]
            )
            
            # 激活代理
            agent.activate()
            
            db.add(agent)
            logger.info(f"创建AI代理: {agent_data['name']}")
        
        db.commit()
        logger.info("AI代理示例数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建AI代理示例数据失败: {str(e)}")
        raise
    finally:
        db.close()


def clear_agent_examples():
    """
    清除AI代理示例数据
    """
    db = SessionLocal()
    try:
        logger.info("开始清除AI代理示例数据...")
        
        # 删除示例代理
        agent_names = [
            "智能客服助手", "代码审查助手", "任务规划助手", "自动化测试生成器",
            "文档生成助手", "数据分析助手", "安全扫描助手", "多语言翻译助手"
        ]
        
        for agent_name in agent_names:
            agent = db.query(Agent).filter(Agent.name == agent_name).first()
            if agent:
                db.delete(agent)
                logger.info(f"删除AI代理: {agent_name}")
        
        db.commit()
        logger.info("AI代理示例数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除AI代理示例数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI代理初始化脚本")
    parser.add_argument("--create", action="store_true", help="创建AI代理示例数据")
    parser.add_argument("--clear", action="store_true", help="清除AI代理示例数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_agent_examples()
    elif args.clear:
        clear_agent_examples()
    else:
        print("请指定操作: --create 或 --clear")
