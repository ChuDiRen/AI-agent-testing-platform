"""
测试用例初始化脚本
创建基础测试用例模板数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import get_logger
from app.entity.test_case import TestCase, TestCaseStatus, TestCasePriority, TestCaseType
from app.entity.agent import Agent
from app.entity.user import User

logger = get_logger(__name__)


def create_test_case_templates():
    """
    创建测试用例模板数据
    """
    db = SessionLocal()
    try:
        logger.info("开始创建测试用例模板数据...")
        
        # 获取用户和代理
        admin_user = db.query(User).filter(User.username == "admin").first()
        tester = db.query(User).filter(User.username == "tester").first()
        developer1 = db.query(User).filter(User.username == "developer1").first()
        
        test_agent = db.query(Agent).filter(Agent.name == "自动化测试生成器").first()
        security_agent = db.query(Agent).filter(Agent.name == "安全扫描助手").first()
        
        if not admin_user:
            logger.error("未找到管理员用户，请先运行基础初始化脚本")
            return
        
        # 创建测试用例数据
        test_cases_data = [
            # 功能测试用例
            {
                "name": "用户登录功能测试",
                "module": "用户管理",
                "description": "验证用户登录功能的正确性",
                "preconditions": "1. 系统已部署\n2. 用户账号已创建\n3. 数据库连接正常",
                "test_steps": "1. 打开登录页面\n2. 输入正确的用户名和密码\n3. 点击登录按钮\n4. 验证登录成功",
                "expected_result": "用户成功登录，跳转到主页面，显示用户信息",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.FUNCTIONAL.value,
                "tags": "登录,用户管理,核心功能",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "用户注册功能测试",
                "module": "用户管理",
                "description": "验证用户注册功能的完整流程",
                "preconditions": "1. 系统已部署\n2. 邮箱服务正常\n3. 数据库连接正常",
                "test_steps": "1. 打开注册页面\n2. 填写用户信息\n3. 提交注册表单\n4. 验证邮箱\n5. 完成注册",
                "expected_result": "用户成功注册，收到确认邮件，可以正常登录",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.FUNCTIONAL.value,
                "tags": "注册,用户管理,核心功能",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "密码重置功能测试",
                "module": "用户管理",
                "description": "验证用户密码重置功能",
                "preconditions": "1. 用户已注册\n2. 邮箱服务正常",
                "test_steps": "1. 点击忘记密码\n2. 输入邮箱地址\n3. 接收重置邮件\n4. 点击重置链接\n5. 设置新密码",
                "expected_result": "密码重置成功，可以使用新密码登录",
                "priority": TestCasePriority.P2.value,
                "test_type": TestCaseType.FUNCTIONAL.value,
                "tags": "密码重置,用户管理",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "AI代理创建功能测试",
                "module": "AI代理管理",
                "description": "验证AI代理创建功能的正确性",
                "preconditions": "1. 用户已登录\n2. 有代理创建权限\n3. AI模型已配置",
                "test_steps": "1. 进入代理管理页面\n2. 点击创建代理\n3. 填写代理信息\n4. 选择AI模型\n5. 保存代理配置",
                "expected_result": "AI代理创建成功，显示在代理列表中",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.FUNCTIONAL.value,
                "tags": "AI代理,创建,核心功能",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "测试用例生成功能测试",
                "module": "测试管理",
                "description": "验证AI智能生成测试用例功能",
                "preconditions": "1. 用户已登录\n2. AI代理已配置\n3. 模型API正常",
                "test_steps": "1. 进入测试用例生成页面\n2. 输入需求描述\n3. 选择测试类型\n4. 点击生成按钮\n5. 查看生成结果",
                "expected_result": "成功生成测试用例，内容符合需求描述",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.FUNCTIONAL.value,
                "tags": "测试用例生成,AI功能,核心功能",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            
            # 性能测试用例
            {
                "name": "系统并发登录性能测试",
                "module": "性能测试",
                "description": "测试系统在高并发登录情况下的性能表现",
                "preconditions": "1. 系统已部署\n2. 性能测试工具已准备\n3. 测试数据已准备",
                "test_steps": "1. 配置并发用户数\n2. 启动性能测试\n3. 监控系统资源\n4. 记录响应时间\n5. 分析测试结果",
                "expected_result": "系统能够承受预期并发量，响应时间在可接受范围内",
                "priority": TestCasePriority.P2.value,
                "test_type": TestCaseType.PERFORMANCE.value,
                "tags": "性能测试,并发,登录",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "AI代理响应时间测试",
                "module": "性能测试",
                "description": "测试AI代理的响应时间和处理能力",
                "preconditions": "1. AI代理已配置\n2. API连接正常\n3. 测试数据已准备",
                "test_steps": "1. 发送测试请求\n2. 记录响应时间\n3. 测试不同负载\n4. 监控资源使用\n5. 分析性能数据",
                "expected_result": "AI代理响应时间稳定，满足性能要求",
                "priority": TestCasePriority.P2.value,
                "test_type": TestCaseType.PERFORMANCE.value,
                "tags": "性能测试,AI代理,响应时间",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            
            # 安全测试用例
            {
                "name": "SQL注入安全测试",
                "module": "安全测试",
                "description": "检测系统是否存在SQL注入漏洞",
                "preconditions": "1. 系统已部署\n2. 安全测试工具已准备",
                "test_steps": "1. 识别输入点\n2. 构造SQL注入payload\n3. 发送测试请求\n4. 分析响应结果\n5. 确认漏洞存在性",
                "expected_result": "系统能够有效防御SQL注入攻击",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.SECURITY.value,
                "tags": "安全测试,SQL注入,漏洞扫描",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": security_agent.id if security_agent else None
            },
            {
                "name": "XSS跨站脚本测试",
                "module": "安全测试",
                "description": "检测系统是否存在XSS漏洞",
                "preconditions": "1. 系统已部署\n2. 浏览器环境已准备",
                "test_steps": "1. 识别输入点\n2. 构造XSS payload\n3. 提交恶意脚本\n4. 观察脚本执行\n5. 确认漏洞影响",
                "expected_result": "系统能够有效过滤和防御XSS攻击",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.SECURITY.value,
                "tags": "安全测试,XSS,跨站脚本",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": security_agent.id if security_agent else None
            },
            {
                "name": "权限绕过测试",
                "module": "安全测试",
                "description": "测试系统权限控制的有效性",
                "preconditions": "1. 系统已部署\n2. 不同权限用户已创建",
                "test_steps": "1. 使用低权限用户登录\n2. 尝试访问高权限功能\n3. 测试API权限控制\n4. 检查数据访问权限\n5. 验证权限边界",
                "expected_result": "系统严格控制用户权限，无法绕过权限限制",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.SECURITY.value,
                "tags": "安全测试,权限控制,访问控制",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": security_agent.id if security_agent else None
            },
            
            # API测试用例
            {
                "name": "用户API接口测试",
                "module": "API测试",
                "description": "测试用户相关API接口的功能和稳定性",
                "preconditions": "1. API服务已启动\n2. 测试工具已配置\n3. 认证token已获取",
                "test_steps": "1. 测试用户列表API\n2. 测试用户创建API\n3. 测试用户更新API\n4. 测试用户删除API\n5. 验证响应格式",
                "expected_result": "所有API接口正常工作，返回正确的数据格式",
                "priority": TestCasePriority.P2.value,
                "test_type": TestCaseType.API.value,
                "tags": "API测试,用户接口,CRUD",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "AI代理API接口测试",
                "module": "API测试",
                "description": "测试AI代理相关API接口",
                "preconditions": "1. API服务已启动\n2. AI代理已配置\n3. 认证token已获取",
                "test_steps": "1. 测试代理列表API\n2. 测试代理创建API\n3. 测试代理启动API\n4. 测试代理停止API\n5. 测试代理配置API",
                "expected_result": "AI代理API接口功能正常，状态控制有效",
                "priority": TestCasePriority.P2.value,
                "test_type": TestCaseType.API.value,
                "tags": "API测试,AI代理,状态控制",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            
            # UI测试用例
            {
                "name": "响应式布局测试",
                "module": "UI测试",
                "description": "测试系统在不同设备和屏幕尺寸下的显示效果",
                "preconditions": "1. 系统已部署\n2. 不同设备已准备\n3. 浏览器已配置",
                "test_steps": "1. 在桌面端测试\n2. 在平板端测试\n3. 在手机端测试\n4. 测试横竖屏切换\n5. 验证元素布局",
                "expected_result": "系统在各种设备上都能正常显示，布局合理",
                "priority": TestCasePriority.P3.value,
                "test_type": TestCaseType.UI.value,
                "tags": "UI测试,响应式,兼容性",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            {
                "name": "用户交互体验测试",
                "module": "UI测试",
                "description": "测试用户界面的交互体验和易用性",
                "preconditions": "1. 系统已部署\n2. 测试用户已准备",
                "test_steps": "1. 测试导航菜单\n2. 测试表单交互\n3. 测试按钮响应\n4. 测试加载状态\n5. 测试错误提示",
                "expected_result": "用户界面交互流畅，操作直观易懂",
                "priority": TestCasePriority.P3.value,
                "test_type": TestCaseType.UI.value,
                "tags": "UI测试,用户体验,交互设计",
                "created_by_id": developer1.id if developer1 else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            },
            
            # 集成测试用例
            {
                "name": "端到端业务流程测试",
                "module": "集成测试",
                "description": "测试完整的业务流程从开始到结束",
                "preconditions": "1. 所有系统组件已部署\n2. 数据库已初始化\n3. 外部服务已连接",
                "test_steps": "1. 用户注册登录\n2. 创建AI代理\n3. 配置模型参数\n4. 生成测试用例\n5. 执行测试报告",
                "expected_result": "完整业务流程顺利执行，各组件协同工作正常",
                "priority": TestCasePriority.P1.value,
                "test_type": TestCaseType.INTEGRATION.value,
                "tags": "集成测试,端到端,业务流程",
                "created_by_id": tester.id if tester else admin_user.id,
                "agent_id": test_agent.id if test_agent else None
            }
        ]
        
        for test_case_data in test_cases_data:
            # 检查测试用例是否已存在
            existing_case = db.query(TestCase).filter(TestCase.name == test_case_data["name"]).first()
            if existing_case:
                logger.info(f"测试用例 {test_case_data['name']} 已存在，跳过创建")
                continue
            
            # 创建测试用例
            test_case = TestCase(
                name=test_case_data["name"],
                module=test_case_data["module"],
                description=test_case_data["description"],
                preconditions=test_case_data["preconditions"],
                test_steps=test_case_data["test_steps"],
                expected_result=test_case_data["expected_result"],
                priority=test_case_data["priority"],
                test_type=test_case_data["test_type"],
                tags=test_case_data["tags"],
                created_by_id=test_case_data["created_by_id"],
                agent_id=test_case_data["agent_id"]
            )
            
            db.add(test_case)
            logger.info(f"创建测试用例: {test_case_data['name']}")
        
        db.commit()
        logger.info("测试用例模板数据创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试用例模板数据失败: {str(e)}")
        raise
    finally:
        db.close()


def clear_test_case_templates():
    """
    清除测试用例模板数据
    """
    db = SessionLocal()
    try:
        logger.info("开始清除测试用例模板数据...")
        
        # 删除所有模板测试用例
        test_cases = db.query(TestCase).all()
        for test_case in test_cases:
            db.delete(test_case)
            logger.info(f"删除测试用例: {test_case.name}")
        
        db.commit()
        logger.info("测试用例模板数据清除成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"清除测试用例模板数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试用例初始化脚本")
    parser.add_argument("--create", action="store_true", help="创建测试用例模板数据")
    parser.add_argument("--clear", action="store_true", help="清除测试用例模板数据")
    
    args = parser.parse_args()
    
    if args.create:
        create_test_case_templates()
    elif args.clear:
        clear_test_case_templates()
    else:
        print("请指定操作: --create 或 --clear")
