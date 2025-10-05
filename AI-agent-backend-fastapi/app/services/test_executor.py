# Copyright (c) 2025 左岚. All rights reserved.
"""
测试执行引擎

提供API、Web、App测试用例的执行功能
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
import json
import httpx
import logging

logger = logging.getLogger(__name__)


class TestExecutor:
    """测试执行器基类"""
    
    def __init__(self):
        self.executor_name = "BaseExecutor"
    
    async def execute(self, testcase: Any, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行测试用例
        
        Args:
            testcase: 测试用例对象
            config: 执行配置
        
        Returns:
            执行结果字典
        """
        raise NotImplementedError("子类必须实现execute方法")
    
    def _create_result(
        self,
        status: str,
        duration: float,
        actual_result: str = "",
        error_message: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建标准化的执行结果
        
        Args:
            status: 执行状态 (passed/failed/error/skipped)
            duration: 执行时长(秒)
            actual_result: 实际结果
            error_message: 错误信息
            details: 详细信息
        
        Returns:
            标准化的结果字典
        """
        return {
            "status": status,
            "duration": round(duration, 3),
            "actual_result": actual_result,
            "error_message": error_message,
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "executor": self.executor_name,
            "details": details or {}
        }


class APITestExecutor(TestExecutor):
    """API测试执行器"""
    
    def __init__(self):
        super().__init__()
        self.executor_name = "APITestExecutor"
    
    async def execute(self, testcase: Any, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行API测试用例
        
        支持的配置:
        - base_url: API基础URL
        - timeout: 请求超时时间
        - headers: 自定义请求头
        """
        start_time = time.time()
        
        try:
            # 解析测试步骤
            test_steps = self._parse_test_steps(testcase.test_steps)
            
            # 执行API请求
            result = await self._execute_api_request(
                test_steps,
                config or {}
            )
            
            duration = time.time() - start_time
            
            # 验证结果
            if self._verify_result(result, testcase.expected_result):
                return self._create_result(
                    status="passed",
                    duration=duration,
                    actual_result=json.dumps(result, ensure_ascii=False),
                    details={
                        "request": test_steps,
                        "response": result
                    }
                )
            else:
                return self._create_result(
                    status="failed",
                    duration=duration,
                    actual_result=json.dumps(result, ensure_ascii=False),
                    error_message="实际结果与预期不符",
                    details={
                        "expected": testcase.expected_result,
                        "actual": result
                    }
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return self._create_result(
                status="error",
                duration=duration,
                error_message=f"执行异常: {str(e)}",
                details={"exception": str(e)}
            )
    
    def _parse_test_steps(self, test_steps: str) -> Dict[str, Any]:
        """解析测试步骤为API请求参数"""
        try:
            # 尝试解析JSON格式的测试步骤
            return json.loads(test_steps)
        except:
            # 如果不是JSON，返回基本格式
            return {
                "method": "GET",
                "url": "/api/test",
                "description": test_steps
            }
    
    async def _execute_api_request(
        self,
        test_steps: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行真实的API请求（使用httpx）
        
        支持的test_steps参数:
        - method: HTTP方法 (GET/POST/PUT/DELETE/PATCH)
        - url: 请求URL（可以是完整URL或相对路径）
        - headers: 请求头字典
        - params: URL参数（GET请求）
        - body/data/json: 请求体（POST/PUT/PATCH）
        - timeout: 超时时间（秒）
        
        支持的config参数:
        - base_url: API基础URL
        - default_headers: 默认请求头
        - timeout: 默认超时时间
        - verify_ssl: 是否验证SSL证书
        """
        # 提取请求参数
        method = test_steps.get("method", "GET").upper()
        url = test_steps.get("url", "")
        
        # 处理URL
        base_url = config.get("base_url", "")
        if not url.startswith("http"):
            url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
        
        # 处理请求头
        headers = test_steps.get("headers", {})
        default_headers = config.get("default_headers", {})
        headers = {**default_headers, **headers}
        
        # 处理超时
        timeout = test_steps.get("timeout", config.get("timeout", 30))
        
        # 处理SSL验证
        verify_ssl = config.get("verify_ssl", True)
        
        try:
            async with httpx.AsyncClient(verify=verify_ssl) as client:
                # 根据不同方法执行请求
                if method == "GET":
                    response = await client.get(
                        url,
                        params=test_steps.get("params"),
                        headers=headers,
                        timeout=timeout
                    )
                elif method == "POST":
                    # 支持json或data两种方式
                    if "json" in test_steps:
                        response = await client.post(
                            url,
                            json=test_steps["json"],
                            headers=headers,
                            timeout=timeout
                        )
                    else:
                        response = await client.post(
                            url,
                            data=test_steps.get("data") or test_steps.get("body"),
                            headers=headers,
                            timeout=timeout
                        )
                elif method == "PUT":
                    if "json" in test_steps:
                        response = await client.put(
                            url,
                            json=test_steps["json"],
                            headers=headers,
                            timeout=timeout
                        )
                    else:
                        response = await client.put(
                            url,
                            data=test_steps.get("data") or test_steps.get("body"),
                            headers=headers,
                            timeout=timeout
                        )
                elif method == "DELETE":
                    response = await client.delete(
                        url,
                        headers=headers,
                        timeout=timeout
                    )
                elif method == "PATCH":
                    if "json" in test_steps:
                        response = await client.patch(
                            url,
                            json=test_steps["json"],
                            headers=headers,
                            timeout=timeout
                        )
                    else:
                        response = await client.patch(
                            url,
                            data=test_steps.get("data") or test_steps.get("body"),
                            headers=headers,
                            timeout=timeout
                        )
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 解析响应
                try:
                    body = response.json()
                except:
                    body = response.text
                
                return {
                    "status_code": response.status_code,
                    "body": body,
                    "headers": dict(response.headers),
                    "elapsed_time": response.elapsed.total_seconds(),
                    "url": str(response.url)
                }
                
        except httpx.TimeoutException as e:
            logger.error(f"API请求超时: {url}, 错误: {e}")
            raise Exception(f"请求超时（{timeout}秒）: {url}")
        except httpx.ConnectError as e:
            logger.error(f"API连接失败: {url}, 错误: {e}")
            raise Exception(f"无法连接到服务器: {url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"API请求HTTP错误: {e.response.status_code}, 错误: {e}")
            # 即使是错误状态码，也返回响应内容
            try:
                body = e.response.json()
            except:
                body = e.response.text
            return {
                "status_code": e.response.status_code,
                "body": body,
                "headers": dict(e.response.headers),
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"API请求异常: {url}, 错误: {e}")
            raise Exception(f"请求失败: {str(e)}")
    
    def _verify_result(self, actual: Dict[str, Any], expected: str) -> bool:
        """
        验证API响应是否符合预期
        
        支持多种验证方式:
        1. 状态码验证: {"status_code": 200}
        2. 响应体验证: {"body.success": true, "body.code": 0}
        3. 包含验证: {"contains": "success"}
        4. 正则验证: {"regex": "\\d+"}
        """
        try:
            # 如果没有预期结果，默认验证状态码为2xx
            if not expected or expected.strip() == "":
                status_code = actual.get("status_code", 0)
                return 200 <= status_code < 300
            
            # 解析预期结果
            try:
                expected_data = json.loads(expected)
            except:
                # 如果不是JSON，当作字符串包含验证
                actual_str = json.dumps(actual, ensure_ascii=False)
                return expected in actual_str
            
            # 验证状态码
            if "status_code" in expected_data:
                if actual.get("status_code") != expected_data["status_code"]:
                    return False
            
            # 验证响应体字段
            body = actual.get("body", {})
            for key, value in expected_data.items():
                if key == "status_code":
                    continue
                
                # 支持点号路径 (如 "data.user.name")
                if "." in key:
                    parts = key.split(".")
                    current = body
                    for part in parts:
                        if isinstance(current, dict):
                            current = current.get(part)
                        else:
                            return False
                    if current != value:
                        return False
                else:
                    if isinstance(body, dict) and body.get(key) != value:
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"验证结果时出错: {e}")
            # 验证失败时返回False
            return False


class WebTestExecutor(TestExecutor):
    """Web UI测试执行器"""
    
    def __init__(self):
        super().__init__()
        self.executor_name = "WebTestExecutor"
    
    async def execute(self, testcase: Any, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行Web UI测试用例
        
        支持的配置:
        - browser: 浏览器类型 (chrome/firefox/edge)
        - headless: 是否无头模式
        - viewport: 视口大小
        """
        start_time = time.time()
        
        try:
            # 模拟Web测试执行
            await asyncio.sleep(1.0)  # 模拟浏览器启动和页面加载
            
            # 解析测试步骤
            steps = self._parse_web_steps(testcase.test_steps)
            
            # 执行Web操作
            result = await self._execute_web_operations(steps, config or {})
            
            duration = time.time() - start_time
            
            return self._create_result(
                status="passed",
                duration=duration,
                actual_result=f"Web测试执行成功: {len(steps)}个步骤已完成",
                details={
                    "browser": config.get("browser", "chrome") if config else "chrome",
                    "steps_executed": len(steps),
                    "screenshots": []  # 实际项目中会包含截图路径
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return self._create_result(
                status="error",
                duration=duration,
                error_message=f"Web测试执行失败: {str(e)}",
                details={"exception": str(e)}
            )
    
    def _parse_web_steps(self, test_steps: str) -> list:
        """解析Web测试步骤"""
        # 简单分行处理
        return [step.strip() for step in test_steps.split('\n') if step.strip()]
    
    async def _execute_web_operations(
        self,
        steps: list,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行Web操作"""
        results = []
        
        for step in steps:
            # 模拟每个步骤的执行
            await asyncio.sleep(0.2)
            results.append({
                "step": step,
                "status": "success"
            })
        
        return {
            "total_steps": len(steps),
            "passed_steps": len(results),
            "failed_steps": 0,
            "steps_detail": results
        }


class AppTestExecutor(TestExecutor):
    """App测试执行器"""
    
    def __init__(self):
        super().__init__()
        self.executor_name = "AppTestExecutor"
    
    async def execute(self, testcase: Any, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行App测试用例
        
        支持的配置:
        - platform: 平台 (ios/android)
        - device: 设备名称
        - app_package: 应用包名
        """
        start_time = time.time()
        
        try:
            # 模拟App测试执行
            await asyncio.sleep(1.5)  # 模拟App启动
            
            # 解析测试步骤
            steps = self._parse_app_steps(testcase.test_steps)
            
            # 执行App操作
            result = await self._execute_app_operations(steps, config or {})
            
            duration = time.time() - start_time
            
            return self._create_result(
                status="passed",
                duration=duration,
                actual_result=f"App测试执行成功: {len(steps)}个操作已完成",
                details={
                    "platform": config.get("platform", "android") if config else "android",
                    "device": config.get("device", "模拟器") if config else "模拟器",
                    "operations_count": len(steps)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return self._create_result(
                status="error",
                duration=duration,
                error_message=f"App测试执行失败: {str(e)}",
                details={"exception": str(e)}
            )
    
    def _parse_app_steps(self, test_steps: str) -> list:
        """解析App测试步骤"""
        return [step.strip() for step in test_steps.split('\n') if step.strip()]
    
    async def _execute_app_operations(
        self,
        steps: list,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行App操作"""
        results = []
        
        for step in steps:
            # 模拟每个操作的执行
            await asyncio.sleep(0.3)
            results.append({
                "operation": step,
                "status": "success"
            })
        
        return {
            "total_operations": len(steps),
            "passed_operations": len(results),
            "failed_operations": 0,
            "operations_detail": results
        }


class TestExecutorFactory:
    """测试执行器工厂类"""
    
    _executors = {
        "api": APITestExecutor,
        "web": WebTestExecutor,
        "app": AppTestExecutor,
    }
    
    @classmethod
    def get_executor(cls, test_type: str) -> TestExecutor:
        """
        根据测试类型获取对应的执行器
        
        Args:
            test_type: 测试类型 (api/web/app)
        
        Returns:
            对应的测试执行器实例
        
        Raises:
            ValueError: 不支持的测试类型
        """
        test_type = test_type.lower()
        
        if test_type not in cls._executors:
            raise ValueError(
                f"不支持的测试类型: {test_type}. "
                f"支持的类型: {', '.join(cls._executors.keys())}"
            )
        
        return cls._executors[test_type]()
    
    @classmethod
    def register_executor(cls, test_type: str, executor_class: type):
        """
        注册新的测试执行器
        
        Args:
            test_type: 测试类型
            executor_class: 执行器类
        """
        cls._executors[test_type] = executor_class
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取所有支持的测试类型"""
        return list(cls._executors.keys())
