"""
统一的用例生成服务
组合各个引擎的生成器
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from .api_generator import ApiCaseGenerator
from .web_generator import WebCaseGenerator
from .mobile_generator import MobileCaseGenerator
from .perf_generator import PerfCaseGenerator
from .pytest_generator import (
    PytestApiGenerator,
    PytestWebGenerator,
    PytestMobileGenerator,
    PytestPerfGenerator
)


class CaseGeneratorService:
    """测试用例生成服务 - 统一入口"""
    
    def __init__(self):
        # mcp 模块的根目录
        self.project_root = Path(__file__).parent.parent.parent
        # test-engine 的目录（mcp 的父目录）
        self.test_engine_root = self.project_root.parent
        self.examples_dir = self.test_engine_root / "examples"
        
        # 初始化各引擎生成器（YAML 格式）
        self._api_generator = ApiCaseGenerator(self.examples_dir)
        self._web_generator = WebCaseGenerator(self.examples_dir)
        self._mobile_generator = MobileCaseGenerator(self.examples_dir)
        self._perf_generator = PerfCaseGenerator(self.examples_dir)
        
        # 初始化 Pytest 生成器
        self._pytest_api_generator = PytestApiGenerator(self.examples_dir)
        self._pytest_web_generator = PytestWebGenerator(self.examples_dir)
        self._pytest_mobile_generator = PytestMobileGenerator(self.examples_dir)
        self._pytest_perf_generator = PytestPerfGenerator(self.examples_dir)
    
    # ==================== API 测试用例 ====================
    
    def generate_api_case(
        self,
        name: str,
        description: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        extracts: Optional[List[Dict[str, str]]] = None,
        asserts: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        format: str = "pytest",
        feature: str = "API测试",
        story: str = "接口测试"
    ) -> Dict[str, Any]:
        """
        生成 API 测试用例
        
        Args:
            format: 输出格式，"yaml" 或 "pytest"（默认）
        """
        if format == "yaml":
            return self._api_generator.generate(
                name=name,
                description=description,
                url=url,
                method=method,
                headers=headers,
                params=params,
                data=data,
                json_body=json_body,
                extracts=extracts,
                asserts=asserts,
                save_path=save_path
            )
        else:
            # 默认生成 pytest 脚本
            return self._pytest_api_generator.generate(
                name=name,
                description=description,
                url=url,
                method=method,
                headers=headers,
                params=params,
                data=data,
                json_body=json_body,
                extracts=extracts,
                asserts=asserts,
                save_path=save_path,
                feature=feature,
                story=story
            )
    
    # ==================== Web 测试用例 ====================
    
    def generate_web_case(
        self,
        name: str,
        description: str,
        url: str,
        browser: str = "chromium",
        headless: bool = True,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        format: str = "pytest",
        feature: str = "Web测试",
        story: str = "UI自动化"
    ) -> Dict[str, Any]:
        """
        生成 Web 测试用例
        
        Args:
            format: 输出格式，"yaml" 或 "pytest"（默认）
        """
        if format == "yaml":
            return self._web_generator.generate(
                name=name,
                description=description,
                url=url,
                browser=browser,
                headless=headless,
                actions=actions,
                save_path=save_path
            )
        else:
            # 默认生成 pytest 脚本
            return self._pytest_web_generator.generate(
                name=name,
                description=description,
                url=url,
                actions=actions,
                save_path=save_path,
                feature=feature,
                story=story
            )
    
    # ==================== Mobile 测试用例 ====================
    
    def generate_mobile_case(
        self,
        name: str,
        description: str,
        platform: str = "android",
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        format: str = "pytest",
        feature: str = "Mobile测试",
        story: str = "APP自动化"
    ) -> Dict[str, Any]:
        """
        生成 Mobile 测试用例
        
        Args:
            format: 输出格式，"yaml" 或 "pytest"（默认）
        """
        if format == "yaml":
            return self._mobile_generator.generate(
                name=name,
                description=description,
                platform=platform,
                app_package=app_package,
                app_activity=app_activity,
                bundle_id=bundle_id,
                actions=actions,
                save_path=save_path
            )
        else:
            # 默认生成 pytest 脚本
            return self._pytest_mobile_generator.generate(
                name=name,
                description=description,
                platform=platform,
                app_package=app_package,
                app_activity=app_activity,
                bundle_id=bundle_id,
                actions=actions,
                save_path=save_path,
                feature=feature,
                story=story
            )
    
    # ==================== 性能测试用例 ====================
    
    def generate_perf_case(
        self,
        name: str,
        description: str,
        host: str,
        scenarios: List[Dict[str, Any]],
        users: int = 10,
        spawn_rate: float = 1,
        run_time: str = "60s",
        think_time: Optional[Dict[str, Any]] = None,
        save_path: Optional[str] = None,
        format: str = "pytest"
    ) -> Dict[str, Any]:
        """
        生成性能测试用例
        
        Args:
            format: 输出格式，"yaml" 或 "pytest"（默认，生成 Locust 脚本）
        """
        if format == "yaml":
            return self._perf_generator.generate(
                name=name,
                description=description,
                host=host,
                scenarios=scenarios,
                users=users,
                spawn_rate=spawn_rate,
                run_time=run_time,
                think_time=think_time,
                save_path=save_path
            )
        else:
            # 默认生成 Locust 脚本
            return self._pytest_perf_generator.generate(
                name=name,
                description=description,
                host=host,
                scenarios=scenarios,
                users=users,
                spawn_rate=spawn_rate,
                run_time=run_time,
                think_time=think_time,
                save_path=save_path
            )
    
    # ==================== 通用方法 ====================
    
    def generate_case_from_yaml(
        self,
        yaml_content: str,
        engine_type: str = "api",
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """从 YAML 字符串直接创建测试用例文件"""
        try:
            case = yaml.safe_load(yaml_content)
            
            if not isinstance(case, dict):
                return {"success": False, "message": "YAML 格式错误：必须是字典格式"}
            
            if "steps" not in case:
                return {"success": False, "message": "YAML 格式错误：缺少 steps 字段"}
            
            engine_dirs = {
                "api": "api-cases_yaml",
                "web": "web-cases_yaml",
                "mobile": "mobile-cases_yaml",
                "perf": "perf-cases_yaml"
            }
            dir_name = engine_dirs.get(engine_type, "api-cases_yaml")
            
            desc = case.get("desc", "test_case")
            save_file = self._api_generator._get_save_path(save_path, desc, dir_name)
            
            with open(save_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            return {
                "success": True,
                "message": "测试用例已保存",
                "save_path": str(save_file),
                "case_content": case,
                "engine_type": engine_type
            }
            
        except yaml.YAMLError as e:
            return {"success": False, "message": f"YAML 解析错误: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"保存失败: {str(e)}"}


# 单例
_case_generator: Optional[CaseGeneratorService] = None


def get_case_generator() -> CaseGeneratorService:
    """获取用例生成服务单例"""
    global _case_generator
    if _case_generator is None:
        _case_generator = CaseGeneratorService()
    return _case_generator
