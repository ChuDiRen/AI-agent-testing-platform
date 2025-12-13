# -*- coding: utf-8 -*-
"""
初始化测试用例数据脚本
用于验证 API 和 Web 两种用例的功能

前置条件：
    1. 先在插件市场上传并安装执行引擎插件 (api_engine, web_engine)
    2. 在关键字管理页面点击"从引擎同步"同步关键字

运行方式：
    cd platform-fastapi-server
    python -m scripts.init_test_cases
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from core.database import engine
from apitest.model.ApiProjectModel import ApiProject
from apitest.model.ApiInfoCaseModel import ApiInfoCase
from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
from apitest.model.ApiKeyWordModel import ApiKeyWord
from apitest.model.ApiOperationTypeModel import OperationType
from plugin.model.PluginModel import Plugin


def check_plugins():
    """检查执行引擎插件是否已安装"""
    print("\n=== 检查执行引擎插件 ===")
    
    with Session(engine) as session:
        api_plugin = session.exec(
            select(Plugin).where(Plugin.plugin_code == "api_engine")
        ).first()
        web_plugin = session.exec(
            select(Plugin).where(Plugin.plugin_code == "web_engine")
        ).first()
        
        missing = []
        if not api_plugin:
            missing.append("api_engine (API自动化引擎)")
        else:
            print(f"  ✓ api_engine 已安装")
            
        if not web_plugin:
            missing.append("web_engine (Web自动化引擎)")
        else:
            print(f"  ✓ web_engine 已安装")
        
        if missing:
            print(f"\n  ⚠️  缺少以下插件，请先在插件市场上传安装：")
            for m in missing:
                print(f"     - {m}")
            return False
        
        return True


def get_keyword_by_func_name(session, func_name: str):
    """根据函数名获取关键字"""
    return session.exec(
        select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == func_name)
    ).first()


def init_project():
    """初始化测试项目"""
    print("\n=== 初始化测试项目 ===")
    
    with Session(engine) as session:
        existing = session.exec(
            select(ApiProject).where(ApiProject.project_name == "示例测试项目")
        ).first()
        
        if not existing:
            project = ApiProject(
                project_name="示例测试项目",
                project_desc="用于演示 API 和 Web 测试用例的示例项目",
                create_time=datetime.now(),
                modify_time=datetime.now()
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            print(f"  ✓ 创建项目: 示例测试项目 (ID: {project.id})")
            return project.id
        else:
            print(f"  - 项目已存在: 示例测试项目 (ID: {existing.id})")
            return existing.id


def init_api_test_case(project_id: int):
    """初始化 API 测试用例"""
    print("\n=== 初始化 API 测试用例 ===")
    
    with Session(engine) as session:
        # 获取关键字ID
        send_request = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "send_request")).first()
        ex_jsonData = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "ex_jsonData")).first()
        assert_text = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "assert_text_comparators")).first()
        
        # 检查是否已存在
        existing = session.exec(
            select(ApiInfoCase).where(ApiInfoCase.case_name == "API示例-获取用户信息")
        ).first()
        
        if existing:
            print(f"  - 用例已存在: API示例-获取用户信息 (ID: {existing.id})")
            return
        
        # 创建用例
        case = ApiInfoCase(
            project_id=project_id,
            case_name="API示例-获取用户信息",
            case_desc="演示 API 测试：发送请求、提取数据、断言验证",
            context_config=json.dumps({
                "BASE_URL": "https://jsonplaceholder.typicode.com",
                "USER_ID": "1"
            }, ensure_ascii=False),
            ddts=json.dumps([
                {"desc": "用户1", "USER_ID": "1"},
                {"desc": "用户2", "USER_ID": "2"}
            ], ensure_ascii=False),
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(case)
        session.flush()
        
        # 创建步骤
        steps = [
            {
                "case_info_id": case.id,
                "run_order": 1,
                "step_desc": "发送GET请求获取用户信息",
                "operation_type_id": 1,
                "keyword_id": send_request.id if send_request else None,
                "step_data": json.dumps({
                    "method": "GET",
                    "url": "{{BASE_URL}}/users/{{USER_ID}}",
                    "headers": {"Content-Type": "application/json"}
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 2,
                "step_desc": "提取用户名",
                "operation_type_id": 2,
                "keyword_id": ex_jsonData.id if ex_jsonData else None,
                "step_data": json.dumps({
                    "EXVALUE": "$.name",
                    "VARNAME": "username",
                    "INDEX": "0"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 3,
                "step_desc": "断言状态码为200",
                "operation_type_id": 3,
                "keyword_id": assert_text.id if assert_text else None,
                "step_data": json.dumps({
                    "VALUE": "{{status_code}}",
                    "EXPECTED": "200",
                    "OP_STR": "=="
                }, ensure_ascii=False)
            }
        ]
        
        for step_data in steps:
            step = ApiInfoCaseStep(**step_data, create_time=datetime.now())
            session.add(step)
        
        session.commit()
        print(f"  ✓ 创建用例: API示例-获取用户信息 (ID: {case.id})")
        print(f"    - 步骤数: {len(steps)}")


def init_web_test_case(project_id: int):
    """初始化 Web 测试用例"""
    print("\n=== 初始化 Web 测试用例 ===")
    
    with Session(engine) as session:
        # 获取关键字ID
        open_browser = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "open_browser")).first()
        navigate_to = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "navigate_to")).first()
        input_text = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "input_text")).first()
        click_element = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "click_element")).first()
        wait_for = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "wait_for_element")).first()
        assert_text = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "assert_text_contains")).first()
        close_browser = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "close_browser")).first()
        
        # 检查是否已存在
        existing = session.exec(
            select(ApiInfoCase).where(ApiInfoCase.case_name == "Web示例-百度搜索")
        ).first()
        
        if existing:
            print(f"  - 用例已存在: Web示例-百度搜索 (ID: {existing.id})")
            return
        
        # 创建用例
        case = ApiInfoCase(
            project_id=project_id,
            case_name="Web示例-百度搜索",
            case_desc="演示 Web 测试：打开浏览器、导航、输入、点击、断言",
            context_config=json.dumps({
                "SEARCH_URL": "https://www.baidu.com",
                "KEYWORD": "Playwright"
            }, ensure_ascii=False),
            ddts=json.dumps([
                {"desc": "搜索Playwright", "KEYWORD": "Playwright"},
                {"desc": "搜索Selenium", "KEYWORD": "Selenium"}
            ], ensure_ascii=False),
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(case)
        session.flush()
        
        # 创建步骤
        steps = [
            {
                "case_info_id": case.id,
                "run_order": 1,
                "step_desc": "打开Chrome浏览器",
                "operation_type_id": 10,
                "keyword_id": open_browser.id if open_browser else None,
                "step_data": json.dumps({
                    "browser": "chrome",
                    "headless": "true"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 2,
                "step_desc": "导航到百度首页",
                "operation_type_id": 10,
                "keyword_id": navigate_to.id if navigate_to else None,
                "step_data": json.dumps({
                    "url": "{{SEARCH_URL}}"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 3,
                "step_desc": "输入搜索关键词",
                "operation_type_id": 11,
                "keyword_id": input_text.id if input_text else None,
                "step_data": json.dumps({
                    "locator_type": "role",
                    "element": "textbox",
                    "text": "{{KEYWORD}}",
                    "clear": "false"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 4,
                "step_desc": "点击搜索按钮",
                "operation_type_id": 11,
                "keyword_id": click_element.id if click_element else None,
                "step_data": json.dumps({
                    "locator_type": "role",
                    "element": "button",
                    "name": "百度一下"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 5,
                "step_desc": "等待搜索结果加载",
                "operation_type_id": 12,
                "keyword_id": wait_for.id if wait_for else None,
                "step_data": json.dumps({
                    "locator_type": "id",
                    "element": "content_left",
                    "timeout": "10"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 6,
                "step_desc": "断言搜索结果包含关键词",
                "operation_type_id": 13,
                "keyword_id": assert_text.id if assert_text else None,
                "step_data": json.dumps({
                    "locator_type": "id",
                    "element": "content_left",
                    "expected_text": "{{KEYWORD}}"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 7,
                "step_desc": "关闭浏览器",
                "operation_type_id": 10,
                "keyword_id": close_browser.id if close_browser else None,
                "step_data": json.dumps({}, ensure_ascii=False)
            }
        ]
        
        for step_data in steps:
            step = ApiInfoCaseStep(**step_data, create_time=datetime.now())
            session.add(step)
        
        session.commit()
        print(f"  ✓ 创建用例: Web示例-百度搜索 (ID: {case.id})")
        print(f"    - 步骤数: {len(steps)}")


def init_ai_web_test_case(project_id: int):
    """初始化 AI Web 测试用例"""
    print("\n=== 初始化 AI Web 测试用例 ===")
    
    with Session(engine) as session:
        # 获取关键字ID - AI 用例需要使用 bu_ 系列关键字
        bu_open_browser = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "bu_open_browser")).first()
        bu_navigate = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "bu_navigate")).first()
        bu_run_task = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "bu_run_task")).first()
        bu_close_browser = session.exec(select(ApiKeyWord).where(ApiKeyWord.keyword_fun_name == "bu_close_browser")).first()
        
        # 检查是否已存在
        existing = session.exec(
            select(ApiInfoCase).where(ApiInfoCase.case_name == "AI示例-智能搜索")
        ).first()
        
        if existing:
            print(f"  - 用例已存在: AI示例-智能搜索 (ID: {existing.id})")
            return
        
        # 创建用例
        case = ApiInfoCase(
            project_id=project_id,
            case_name="AI示例-智能搜索",
            case_desc="演示 Browser-Use AI 自动化：使用自然语言描述任务",
            context_config=json.dumps({
                "SEARCH_URL": "https://www.baidu.com"
            }, ensure_ascii=False),
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(case)
        session.flush()
        
        # 创建步骤
        steps = [
            {
                "case_info_id": case.id,
                "run_order": 1,
                "step_desc": "打开浏览器",
                "operation_type_id": 14,
                "keyword_id": bu_open_browser.id if bu_open_browser else None,
                "step_data": json.dumps({
                    "browser": "chrome",
                    "headless": "true"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 2,
                "step_desc": "导航到百度",
                "operation_type_id": 14,
                "keyword_id": bu_navigate.id if bu_navigate else None,
                "step_data": json.dumps({
                    "url": "{{SEARCH_URL}}"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 3,
                "step_desc": "AI执行搜索任务",
                "operation_type_id": 14,
                "keyword_id": bu_run_task.id if bu_run_task else None,
                "step_data": json.dumps({
                    "task": "在搜索框中输入'Python自动化测试'，然后点击搜索按钮，等待结果加载完成"
                }, ensure_ascii=False)
            },
            {
                "case_info_id": case.id,
                "run_order": 4,
                "step_desc": "关闭浏览器",
                "operation_type_id": 14,
                "keyword_id": bu_close_browser.id if bu_close_browser else None,
                "step_data": json.dumps({}, ensure_ascii=False)
            }
        ]
        
        for step_data in steps:
            step = ApiInfoCaseStep(**step_data, create_time=datetime.now())
            session.add(step)
        
        session.commit()
        print(f"  ✓ 创建用例: AI示例-智能搜索 (ID: {case.id})")
        print(f"    - 步骤数: {len(steps)}")


def check_keywords():
    """检查关键字是否已同步"""
    print("\n=== 检查关键字 ===")
    
    with Session(engine) as session:
        keywords = session.exec(select(ApiKeyWord)).all()
        
        if not keywords:
            print("  ⚠️  数据库中没有关键字")
            print('     请先在关键字管理页面点击"从引擎同步"同步关键字')
            return False
        
        # 按引擎分组统计
        api_count = len([k for k in keywords if k.plugin_code == "api_engine"])
        web_count = len([k for k in keywords if k.plugin_code == "web_engine"])
        
        print(f"  ✓ 共 {len(keywords)} 个关键字")
        print(f"    - api_engine: {api_count} 个")
        print(f"    - web_engine: {web_count} 个")
        
        if api_count == 0 and web_count == 0:
            print("\n  ⚠️  关键字未关联执行引擎")
            print('     请先在关键字管理页面点击"从引擎同步"同步关键字')
            return False
        
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("  初始化测试用例数据")
    print("=" * 60)
    
    try:
        # 1. 检查插件是否已安装
        if not check_plugins():
            print("\n" + "=" * 60)
            print("  ✗ 前置条件不满足")
            print("=" * 60)
            print("\n请按以下步骤操作：")
            print("  1. 在插件市场上传并安装 api_engine 和 web_engine")
            print('  2. 在关键字管理页面点击"从引擎同步"')
            print("  3. 重新运行此脚本")
            return 1
        
        # 2. 检查关键字是否已同步
        if not check_keywords():
            print("\n" + "=" * 60)
            print("  ✗ 前置条件不满足")
            print("=" * 60)
            print("\n请按以下步骤操作：")
            print('  1. 在关键字管理页面点击"从引擎同步"')
            print("  2. 重新运行此脚本")
            return 1
        
        # 3. 初始化项目
        project_id = init_project()
        
        # 4. 初始化 API 测试用例
        init_api_test_case(project_id)
        
        # 5. 初始化 Web 测试用例
        init_web_test_case(project_id)
        
        # 6. 初始化 AI Web 测试用例
        init_ai_web_test_case(project_id)
        
        print("\n" + "=" * 60)
        print("  ✓ 初始化完成！")
        print("=" * 60)
        print("\n已创建的测试数据：")
        print("  - 1 个测试项目")
        print("  - 3 个测试用例:")
        print("    • API示例-获取用户信息 (使用 api_engine)")
        print("    • Web示例-百度搜索 (使用 web_engine)")
        print("    • AI示例-智能搜索 (使用 web_engine + AI)")
        print("\n现在可以在前端页面查看和执行这些用例了！")
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
