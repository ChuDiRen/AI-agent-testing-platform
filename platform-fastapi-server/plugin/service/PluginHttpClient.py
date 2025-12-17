"""
插件HTTP客户端
用于调用插件API的HTTP请求封装
"""
import logging
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)


class PluginHttpClient:
    """插件HTTP客户端"""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        初始化HTTP客户端
        
        Args:
            base_url: 插件API基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态响应
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return {
                    "success": True,
                    "status": "healthy",
                    "data": response.json()
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "status": "unhealthy",
                "error": "Health check timeout"
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "status": "unhealthy",
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def execute_test(
        self,
        test_case_id: int,
        test_case_content: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行测试
        
        Args:
            test_case_id: 测试用例ID
            test_case_content: 测试用例内容（YAML/JSON格式）
            config: 执行配置参数
        
        Returns:
            执行响应（包含task_id）
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "test_case_id": test_case_id,
                    "test_case_content": test_case_content,
                    "config": config or {}
                }
                
                response = await client.post(
                    f"{self.base_url}/execute",
                    json=payload
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "data": response.json()
                }
        
        except httpx.TimeoutException:
            logger.error(f"Execute test timeout for test_case_id={test_case_id}")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Execute test HTTP error: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f"Execute test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务状态响应
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/status/{task_id}")
                response.raise_for_status()
                
                return {
                    "success": True,
                    "data": response.json()
                }
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_test_report(self, task_id: str) -> Dict[str, Any]:
        """
        获取测试报告
        
        Args:
            task_id: 任务ID
        
        Returns:
            测试报告数据
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/report/{task_id}")
                response.raise_for_status()
                
                return {
                    "success": True,
                    "data": response.json()
                }
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            取消结果
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/cancel/{task_id}")
                response.raise_for_status()
                
                return {
                    "success": True,
                    "data": response.json()
                }
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
