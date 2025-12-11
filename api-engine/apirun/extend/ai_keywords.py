"""
AI API 测试关键字模块
基于 LLM 实现的智能 API 测试关键字

功能特点:
- 使用 LLM 驱动的智能 API 测试
- 支持自然语言描述请求和断言
- 支持多种 LLM 模型 (OpenAI, DeepSeek, 硅基流动等)
- 智能提取响应数据
- 与现有 api-engine 框架无缝集成
"""

import json
import os
import re
from typing import Optional, Dict, Any, List

import allure
import requests

# 加载 .env 文件
from pathlib import Path
try:
    from dotenv import load_dotenv
    # 查找项目根目录的 .env 文件
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已加载环境变量: {env_file}")
except ImportError:
    pass  # dotenv 未安装，跳过

from ..core.globalContext import g_context


class AIKeywords:
    """
    AI API 测试关键字类
    
    提供基于 LLM 的智能 API 测试能力，
    可以使用自然语言描述来执行 API 测试任务。
    """
    
    def __init__(self):
        """初始化 AI 关键字类"""
        self._config = {
            "llm_provider": "siliconflow",  # 默认使用硅基流动
            "llm_model": "deepseek-ai/DeepSeek-V3",  # 默认模型
            "api_key": None,
            "base_url": None,
            "timeout": 30,
            "max_tokens": 4096,
        }
        self._session = requests.Session()
    
    def _get_llm_config(self, provider: str = None) -> Dict[str, Any]:
        """
        获取 LLM 配置
        
        :param provider: LLM 提供商
        :return: 配置字典 {api_key, base_url, model}
        """
        provider = provider or self._config.get("llm_provider", "siliconflow")
        
        if provider == "openai":
            return {
                "api_key": self._config.get("api_key") or os.getenv("OPENAI_API_KEY"),
                "base_url": self._config.get("base_url") or "https://api.openai.com/v1",
                "model": self._config.get("llm_model") or "gpt-4o"
            }
        
        elif provider == "deepseek":
            return {
                "api_key": self._config.get("api_key") or os.getenv("DEEPSEEK_API_KEY"),
                "base_url": self._config.get("base_url") or "https://api.deepseek.com/v1",
                "model": self._config.get("llm_model") or "deepseek-chat"
            }
        
        elif provider == "siliconflow":
            api_key = self._config.get("api_key") or os.getenv("SILICONFLOW_API_KEY")
            if not api_key:
                raise ValueError("SILICONFLOW_API_KEY 未设置。请设置环境变量或通过 api_key 参数传递。")
            return {
                "api_key": api_key,
                "base_url": self._config.get("base_url") or "https://api.siliconflow.cn/v1",
                "model": self._config.get("llm_model") or "deepseek-ai/DeepSeek-V3"
            }
        
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用 LLM API
        
        :param prompt: 用户提示
        :param system_prompt: 系统提示
        :return: LLM 响应文本
        """
        config = self._get_llm_config()
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": config["model"],
            "messages": messages,
            "max_tokens": self._config.get("max_tokens", 4096),
            "temperature": 0.1  # 低温度，更确定性的输出
        }
        
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self._config.get("timeout", 30)
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    # ==================== 配置关键字 ====================
    
    @allure.step("配置 AI API 助手")
    def ai_configure(self, **kwargs):
        """
        配置 AI API 助手参数
        
        参数:
            llm_provider: LLM 提供商 (openai/deepseek/siliconflow)
            llm_model: 模型名称 (可选，使用默认)
            api_key: API 密钥 (可选，从环境变量读取)
            base_url: API 基础 URL (可选)
            timeout: 超时时间秒数 (默认 30)
        """
        if "llm_provider" in kwargs:
            self._config["llm_provider"] = kwargs["llm_provider"]
        if "llm_model" in kwargs:
            self._config["llm_model"] = kwargs["llm_model"]
        if "api_key" in kwargs:
            self._config["api_key"] = kwargs["api_key"]
        if "base_url" in kwargs:
            self._config["base_url"] = kwargs["base_url"]
        if "timeout" in kwargs:
            self._config["timeout"] = int(kwargs["timeout"])
        
        print(f"AI API 助手配置已更新: provider={self._config['llm_provider']}, model={self._config['llm_model']}")
    
    # ==================== 核心 AI 关键字 ====================
    
    @allure.step("AI 生成请求参数: {task}")
    def ai_generate_request(self, **kwargs):
        """
        使用 AI 根据自然语言描述生成 API 请求参数
        
        参数:
            task: 任务描述 (自然语言)
            base_url: API 基础 URL
            api_doc: API 文档描述 (可选)
            variable_name: 保存结果的变量名 (默认 ai_request_params)
        
        示例:
            task: "创建一个用户，用户名 test_user，邮箱 test@example.com"
            base_url: "https://api.example.com"
        
        返回:
            生成的请求参数字典，包含 method, url, headers, json/data 等
        """
        task = kwargs.get("task")
        base_url = kwargs.get("base_url", "")
        api_doc = kwargs.get("api_doc", "")
        variable_name = kwargs.get("variable_name", "ai_request_params")
        
        if not task:
            raise ValueError("任务描述不能为空")
        
        system_prompt = """你是一个 API 测试专家。根据用户的自然语言描述，生成对应的 HTTP 请求参数。

请严格按照以下 JSON 格式返回（不要包含任何其他文字）：
{
    "method": "GET/POST/PUT/DELETE/PATCH",
    "url": "完整的 API URL",
    "headers": {"Content-Type": "application/json", ...},
    "json": {...} 或 "data": {...} 或 "params": {...}
}

注意：
1. 根据操作类型选择合适的 HTTP 方法
2. 如果是 JSON 数据，使用 "json" 字段
3. 如果是表单数据，使用 "data" 字段
4. 如果是 URL 参数，使用 "params" 字段
5. 只返回 JSON，不要有任何解释文字"""

        prompt = f"""任务描述: {task}
API 基础 URL: {base_url}
"""
        if api_doc:
            prompt += f"\nAPI 文档:\n{api_doc}"
        
        try:
            response = self._call_llm(prompt, system_prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                request_params = json.loads(json_match.group())
            else:
                raise ValueError(f"无法解析 AI 响应: {response}")
            
            # 保存到全局上下文
            g_context().set_dict(variable_name, request_params)
            print(f"[OK] AI 生成请求参数已保存到 {variable_name}")
            print(f"  请求参数: {json.dumps(request_params, ensure_ascii=False, indent=2)}")
            
            return request_params
            
        except Exception as e:
            raise RuntimeError(f"AI 生成请求参数失败: {e}")
    
    @allure.step("AI 发送请求: {task}")
    def ai_send_request(self, **kwargs):
        """
        使用 AI 理解任务并发送 API 请求
        
        参数:
            task: 任务描述 (自然语言)
            base_url: API 基础 URL
            api_doc: API 文档描述 (可选)
            headers: 额外的请求头 (可选)
        
        示例:
            task: "获取用户列表"
            base_url: "https://api.example.com"
        """
        task = kwargs.get("task")
        base_url = kwargs.get("base_url", "")
        extra_headers = kwargs.get("headers", {})
        
        # 先生成请求参数
        request_params = self.ai_generate_request(**kwargs)
        
        # 合并额外的请求头
        if extra_headers:
            request_params["headers"] = {**request_params.get("headers", {}), **extra_headers}
        
        # 发送请求
        method = request_params.pop("method", "GET")
        url = request_params.pop("url", base_url)
        
        # 清理 None 值的参数，避免请求失败
        request_params = {k: v for k, v in request_params.items() if v is not None}
        
        print(f"[REQUEST] 发送 {method} 请求到 {url}")
        
        response = self._session.request(method=method, url=url, **request_params)
        
        # 保存响应到全局上下文
        g_context().set_dict("current_response", response)
        
        response_data = {
            "url": response.url,
            "method": method,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.text
        }
        g_context().set_dict("current_response_data", response_data)
        
        print(f"[OK] 响应状态码: {response.status_code}")
        
        return response
    
    @allure.step("AI 断言响应: {assertion}")
    def ai_assert_response(self, **kwargs):
        """
        使用 AI 根据自然语言描述验证 API 响应
        
        参数:
            assertion: 断言描述 (自然语言)
            response: 响应对象 (可选，默认使用 current_response)
        
        示例:
            assertion: "状态码应该是 200"
            assertion: "响应中应该包含 user_id 字段"
            assertion: "返回的用户列表应该不为空"
        """
        assertion = kwargs.get("assertion")
        response = kwargs.get("response") or g_context().get_dict("current_response")
        
        if not assertion:
            raise ValueError("断言描述不能为空")
        
        if response is None:
            raise RuntimeError("没有可用的响应，请先发送请求")
        
        # 准备响应信息
        try:
            response_json = response.json()
            response_body = json.dumps(response_json, ensure_ascii=False, indent=2)
        except:
            response_body = response.text
        
        system_prompt = """你是一个 API 测试断言专家。根据用户的断言描述，验证 API 响应是否符合预期。

请严格按照以下 JSON 格式返回（不要包含任何其他文字）：
{
    "passed": true/false,
    "reason": "断言通过/失败的原因"
}"""

        prompt = f"""断言描述: {assertion}

响应信息:
- 状态码: {response.status_code}
- 响应头: {dict(response.headers)}
- 响应体:
{response_body}

请验证响应是否符合断言描述。"""

        try:
            result = self._call_llm(prompt, system_prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                assertion_result = json.loads(json_match.group())
            else:
                raise ValueError(f"无法解析 AI 响应: {result}")
            
            passed = assertion_result.get("passed", False)
            reason = assertion_result.get("reason", "")
            
            if passed:
                print(f"[PASS] 断言通过: {reason}")
            else:
                print(f"[FAIL] 断言失败: {reason}")
                raise AssertionError(f"AI 断言失败: {assertion}\n原因: {reason}")
            
            return assertion_result
            
        except AssertionError:
            raise
        except Exception as e:
            raise RuntimeError(f"AI 断言执行失败: {e}")
    
    @allure.step("AI 提取数据: {extraction}")
    def ai_extract_data(self, **kwargs):
        """
        使用 AI 从响应中智能提取数据
        
        参数:
            extraction: 提取描述 (自然语言)
            response: 响应对象 (可选，默认使用 current_response)
            variable_name: 保存结果的变量名 (默认 ai_extracted_data)
        
        示例:
            extraction: "提取第一个用户的 ID"
            extraction: "提取所有用户的邮箱地址"
            extraction: "提取 token 字段的值"
        """
        extraction = kwargs.get("extraction")
        response = kwargs.get("response") or g_context().get_dict("current_response")
        variable_name = kwargs.get("variable_name", "ai_extracted_data")
        
        if not extraction:
            raise ValueError("提取描述不能为空")
        
        if response is None:
            raise RuntimeError("没有可用的响应，请先发送请求")
        
        # 准备响应信息
        try:
            response_json = response.json()
            response_body = json.dumps(response_json, ensure_ascii=False, indent=2)
        except:
            response_body = response.text
        
        system_prompt = """你是一个数据提取专家。根据用户的描述，从 API 响应中提取指定的数据。

请严格按照以下 JSON 格式返回（不要包含任何其他文字）：
{
    "extracted_data": 提取的数据（可以是字符串、数字、数组或对象）,
    "jsonpath": "对应的 JSONPath 表达式（如果适用）"
}"""

        prompt = f"""提取描述: {extraction}

响应体:
{response_body}

请提取指定的数据。"""

        try:
            result = self._call_llm(prompt, system_prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                extraction_result = json.loads(json_match.group())
            else:
                raise ValueError(f"无法解析 AI 响应: {result}")
            
            extracted_data = extraction_result.get("extracted_data")
            jsonpath_expr = extraction_result.get("jsonpath", "")
            
            # 保存到全局上下文
            g_context().set_dict(variable_name, extracted_data)
            
            print(f"[OK] 已提取数据并保存到 {variable_name}")
            print(f"  提取的数据: {extracted_data}")
            if jsonpath_expr:
                print(f"  JSONPath: {jsonpath_expr}")
            
            return extracted_data
            
        except Exception as e:
            raise RuntimeError(f"AI 数据提取失败: {e}")
    
    @allure.step("AI 生成测试用例")
    def ai_generate_test_cases(self, **kwargs):
        """
        使用 AI 根据 API 文档生成测试用例
        
        参数:
            api_doc: API 文档描述
            test_scenarios: 测试场景描述 (可选)
            variable_name: 保存结果的变量名 (默认 ai_test_cases)
        
        示例:
            api_doc: "POST /users - 创建用户，参数: name(必填), email(必填), age(可选)"
            test_scenarios: "正常创建、缺少必填参数、参数格式错误"
        """
        api_doc = kwargs.get("api_doc")
        test_scenarios = kwargs.get("test_scenarios", "正常场景、边界场景、异常场景")
        variable_name = kwargs.get("variable_name", "ai_test_cases")
        
        if not api_doc:
            raise ValueError("API 文档描述不能为空")
        
        system_prompt = """你是一个 API 测试用例设计专家。根据 API 文档生成全面的测试用例。

请严格按照以下 JSON 格式返回（不要包含任何其他文字）：
{
    "test_cases": [
        {
            "name": "测试用例名称",
            "description": "测试用例描述",
            "request": {
                "method": "HTTP方法",
                "url": "API路径",
                "headers": {},
                "json": {} 或 "data": {} 或 "params": {}
            },
            "expected": {
                "status_code": 期望状态码,
                "assertions": ["断言1", "断言2"]
            }
        }
    ]
}"""

        prompt = f"""API 文档:
{api_doc}

测试场景要求: {test_scenarios}

请生成完整的测试用例。"""

        try:
            result = self._call_llm(prompt, system_prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                test_cases_result = json.loads(json_match.group())
            else:
                raise ValueError(f"无法解析 AI 响应: {result}")
            
            test_cases = test_cases_result.get("test_cases", [])
            
            # 保存到全局上下文
            g_context().set_dict(variable_name, test_cases)
            
            print(f"[OK] 已生成 {len(test_cases)} 个测试用例并保存到 {variable_name}")
            for i, tc in enumerate(test_cases, 1):
                print(f"  {i}. {tc.get('name', '未命名')}")
            
            return test_cases
            
        except Exception as e:
            raise RuntimeError(f"AI 生成测试用例失败: {e}")
    
    @allure.step("AI 分析响应")
    def ai_analyze_response(self, **kwargs):
        """
        使用 AI 分析 API 响应，提供测试建议
        
        参数:
            response: 响应对象 (可选，默认使用 current_response)
            focus: 分析重点 (可选，如 "性能"、"安全"、"数据完整性")
        
        返回:
            分析结果和建议
        """
        response = kwargs.get("response") or g_context().get_dict("current_response")
        focus = kwargs.get("focus", "")
        
        if response is None:
            raise RuntimeError("没有可用的响应，请先发送请求")
        
        # 准备响应信息
        try:
            response_json = response.json()
            response_body = json.dumps(response_json, ensure_ascii=False, indent=2)
        except:
            response_body = response.text
        
        system_prompt = """你是一个 API 测试分析专家。分析 API 响应并提供测试建议。

请按照以下 JSON 格式返回：
{
    "summary": "响应摘要",
    "data_structure": "数据结构分析",
    "potential_issues": ["潜在问题1", "潜在问题2"],
    "test_suggestions": ["测试建议1", "测试建议2"]
}"""

        prompt = f"""请分析以下 API 响应:

状态码: {response.status_code}
响应时间: {response.elapsed.total_seconds()}秒
响应头: {dict(response.headers)}
响应体:
{response_body}
"""
        if focus:
            prompt += f"\n分析重点: {focus}"

        try:
            result = self._call_llm(prompt, system_prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"summary": result}
            
            print(f"[ANALYSIS] 响应分析:")
            print(f"  摘要: {analysis.get('summary', 'N/A')}")
            if analysis.get('potential_issues'):
                print(f"  潜在问题: {', '.join(analysis['potential_issues'])}")
            if analysis.get('test_suggestions'):
                print(f"  测试建议: {', '.join(analysis['test_suggestions'])}")
            
            return analysis
            
        except Exception as e:
            raise RuntimeError(f"AI 分析响应失败: {e}")


# 创建全局实例，方便直接使用
_ai_keywords = None


def get_ai_keywords() -> AIKeywords:
    """获取 AIKeywords 单例实例"""
    global _ai_keywords
    if _ai_keywords is None:
        _ai_keywords = AIKeywords()
    return _ai_keywords
