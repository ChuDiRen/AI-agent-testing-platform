# Copyright (c) 2025 左岚. All rights reserved.
"""
项目验证脚本
验证所有新增功能的导入和基本功能
"""

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    test_modules = [
        # 实体模块
        ('app.entity.agent', 'Agent'),
        ('app.entity.agent_config', 'AgentConfig'),
        ('app.entity.test_case', 'TestCase'),
        ('app.entity.test_report', 'TestReport'),
        ('app.entity.ai_model', 'AIModel'),
        
        # DTO模块
        ('app.dto.agent_dto', 'AgentCreateRequest'),
        ('app.dto.test_case_dto', 'TestCaseCreateRequest'),
        ('app.dto.test_report_dto', 'TestReportCreateRequest'),
        ('app.dto.ai_model_dto', 'AIModelCreateRequest'),
        
        # Repository模块
        ('app.repository.agent_repository', 'AgentRepository'),
        ('app.repository.agent_config_repository', 'AgentConfigRepository'),
        ('app.repository.test_case_repository', 'TestCaseRepository'),
        ('app.repository.test_report_repository', 'TestReportRepository'),
        ('app.repository.ai_model_repository', 'AIModelRepository'),
        
        # Service模块
        ('app.service.agent_service', 'AgentService'),
        ('app.service.test_case_service', 'TestCaseService'),
        ('app.service.ai_model_service', 'AIModelService'),
        ('app.service.multi_agent_service', 'MultiAgentTestCaseGenerator'),
        
        # Controller模块
        ('app.controller.agent_controller', 'router'),
        ('app.controller.test_case_controller', 'router'),
        ('app.controller.ai_generation_controller', 'router'),
    ]
    
    success_count = 0
    total_count = len(test_modules)
    
    print("=== 模块导入测试 ===")
    
    for module_name, class_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {str(e)}")
    
    print(f"\n导入测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count


def test_entity_creation():
    """测试实体创建"""
    print("\n=== 实体创建测试 ===")
    
    try:
        from app.entity.agent import Agent, AgentType, AgentStatus
        
        # 创建代理实体
        agent = Agent(
            name="Test Agent",
            type=AgentType.CHAT.value,
            description="Test Description",
            created_by_id=1
        )
        
        assert agent.name == "Test Agent"
        assert agent.type == AgentType.CHAT.value
        assert agent.status == AgentStatus.INACTIVE.value
        
        print("✅ Agent实体创建成功")
        
        # 测试代理方法
        agent.activate()
        assert agent.is_active()
        print("✅ Agent状态管理正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 实体创建测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_dto_validation():
    """测试DTO验证"""
    print("\n=== DTO验证测试 ===")
    
    try:
        from app.dto.agent_dto import AgentCreateRequest, AgentTypeEnum
        
        # 创建有效请求
        request = AgentCreateRequest(
            name="Test Agent",
            type=AgentTypeEnum.CHAT,
            description="Test Description"
        )
        
        assert request.name == "Test Agent"
        assert request.type == AgentTypeEnum.CHAT
        
        print("✅ AgentCreateRequest验证成功")
        
        return True
        
    except Exception as e:
        print(f"❌ DTO验证测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_multi_agent_generator():
    """测试多智能体生成器"""
    print("\n=== 多智能体生成器测试 ===")
    
    try:
        from app.service.multi_agent_service import MultiAgentTestCaseGenerator
        
        generator = MultiAgentTestCaseGenerator()
        
        # 测试模拟方法
        test_points = generator._simulate_requirements_analysis("测试需求文档")
        assert len(test_points) > 0
        
        test_cases = generator._simulate_test_case_design("测试需求", test_points)
        assert len(test_cases) > 0
        
        print("✅ 多智能体生成器基本功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 多智能体生成器测试失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("AI代理测试平台功能验证")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("实体创建", test_entity_creation),
        ("DTO验证", test_dto_validation),
        ("多智能体生成器", test_multi_agent_generator),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n开始测试: {test_name}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print(f"\n{'=' * 50}")
    print(f"总体测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！AI代理测试平台功能完善成功！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)