"""
Mobile-Use AI 关键字模块
基于 mobile-use 库实现的智能移动端自动化关键字

功能特点:
- 使用 LLM 驱动的智能移动端操作
- 支持自然语言描述任务
- 支持多种 LLM 模型 (OpenAI, Claude, DeepSeek 等)
- 支持复杂的多步骤任务自动执行
- 支持数据抓取和结构化输出
- 与现有 mobile-engine 框架无缝集成

参考: https://github.com/minitap-ai/mobile-use
"""

import asyncio
import json
import os
import subprocess
import time
from typing import Any, Dict, Optional

import allure
from pathlib import Path

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已加载环境变量: {env_file}")
except ImportError:
    pass

from ..core.globalContext import g_context


class MobileUseKeywords:
    """
    Mobile-Use AI 关键字类
    
    提供基于 mobile-use 的智能移动端自动化能力，
    可以使用自然语言描述来执行复杂的移动端操作任务。
    """
    
    def __init__(self):
        """初始化 Mobile-Use 关键字类"""
        self._agent = None
        self._device = None
        self._llm = None
        self._config = {
            "llm_provider": "openai",
            "llm_model": "gpt-4o",
            "platform": "android",
            "device_id": None,
            "timeout": 60,
            "max_steps": 30,
            "minitap_api_key": None,
        }
    
    def _get_llm_config(self, provider: str = None, model: str = None, api_key: str = None, base_url: str = None) -> Dict[str, Any]:
        """
        获取 LLM 配置
        
        :param provider: LLM 提供商
        :param model: 模型名称
        :param api_key: API 密钥
        :param base_url: API 基础 URL
        :return: LLM 配置字典
        """
        provider = provider or self._config.get("llm_provider", "openai")
        
        config = {
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
        }
        
        if provider == "openai":
            config["api_key"] = api_key or os.getenv("OPENAI_API_KEY")
            config["model"] = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        elif provider == "deepseek":
            config["api_key"] = api_key or os.getenv("DEEPSEEK_API_KEY")
            config["model"] = model or "deepseek-chat"
            config["base_url"] = base_url or "https://api.deepseek.com/v1"
        elif provider == "anthropic":
            config["api_key"] = api_key or os.getenv("ANTHROPIC_API_KEY")
            config["model"] = model or "claude-3-5-sonnet-20241022"
        elif provider == "siliconflow":
            config["api_key"] = api_key or os.getenv("SILICONFLOW_API_KEY")
            config["model"] = model or "deepseek-ai/DeepSeek-V3"
            config["base_url"] = base_url or "https://api.siliconflow.cn/v1"
        elif provider == "qwen":
            config["api_key"] = api_key or os.getenv("DASHSCOPE_API_KEY")
            config["model"] = model or "qwen-max"
            config["base_url"] = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        return config

    def _run_async(self, coro):
        """运行异步协程"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(coro)
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def _take_screenshot_on_error(self, name: str):
        """错误时截图"""
        try:
            from ..utils.AppiumManager import AppiumManager
            driver = AppiumManager.get_driver()
            if driver:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                screenshot_dir = os.path.join(project_root, "reports", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
                filename = os.path.join(screenshot_dir, f"{safe_name}_{timestamp}.png")
                driver.get_screenshot_as_file(filename)
                
                with open(filename, "rb") as f:
                    allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            print(f"截图失败: {e}")

    # ==================== 配置关键字 ====================

    @allure.step("配置 Mobile-Use")
    def mu_configure(self, **kwargs: Any):
        """
        配置 Mobile-Use 参数
        
        参数:
            llm_provider: LLM 提供商 (openai/deepseek/anthropic/siliconflow/qwen)
            llm_model: 模型名称 (可选)
            api_key: API 密钥 (可选，从环境变量读取)
            base_url: API 基础 URL (可选)
            platform: 平台 (android/ios，默认 android)
            device_id: 设备 ID (可选)
            timeout: 超时时间秒数 (默认 60)
            max_steps: 最大步骤数 (默认 30)
            minitap_api_key: Minitap 平台 API 密钥 (可选)
        """
        if "llm_provider" in kwargs:
            self._config["llm_provider"] = kwargs["llm_provider"]
        if "llm_model" in kwargs:
            self._config["llm_model"] = kwargs["llm_model"]
        if "api_key" in kwargs:
            self._config["api_key"] = kwargs["api_key"]
        if "base_url" in kwargs:
            self._config["base_url"] = kwargs["base_url"]
        if "platform" in kwargs:
            self._config["platform"] = kwargs["platform"].lower()
        if "device_id" in kwargs:
            self._config["device_id"] = kwargs["device_id"]
        if "timeout" in kwargs:
            self._config["timeout"] = int(kwargs["timeout"])
        if "max_steps" in kwargs:
            self._config["max_steps"] = int(kwargs["max_steps"])
        if "minitap_api_key" in kwargs:
            self._config["minitap_api_key"] = kwargs["minitap_api_key"]
        
        print(f"Mobile-Use 配置已更新: {self._config}")

    @allure.step("初始化 Mobile-Use Agent")
    def mu_init_agent(self, **kwargs: Any):
        """
        初始化 Mobile-Use Agent
        
        参数:
            platform: 平台 (android/ios)
            device_id: 设备 ID (可选)
            llm_provider: LLM 提供商 (可选)
            llm_model: 模型名称 (可选)
        """
        platform = kwargs.get("platform", self._config.get("platform", "android")).lower()
        device_id = kwargs.get("device_id", self._config.get("device_id"))
        
        if "llm_provider" in kwargs:
            self._config["llm_provider"] = kwargs["llm_provider"]
        if "llm_model" in kwargs:
            self._config["llm_model"] = kwargs["llm_model"]
        
        try:
            from mobile_use import Agent, Device
            from mobile_use.llm import get_llm
            
            llm_config = self._get_llm_config(
                provider=self._config.get("llm_provider"),
                model=self._config.get("llm_model"),
                api_key=self._config.get("api_key"),
                base_url=self._config.get("base_url")
            )
            
            self._llm = get_llm(
                provider=llm_config["provider"],
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                base_url=llm_config.get("base_url")
            )
            
            self._device = Device(
                platform=platform,
                device_id=device_id
            )
            
            self._agent = Agent(
                device=self._device,
                llm=self._llm,
                max_steps=self._config.get("max_steps", 30)
            )
            
            g_context().set_dict("mobile_use_agent", self._agent)
            g_context().set_dict("mobile_use_device", self._device)
            g_context().set_dict("mobile_use_llm", self._llm)
            
            print(f"Mobile-Use Agent 已初始化 (platform={platform}, device_id={device_id})")
            
        except ImportError:
            print("⚠ mobile-use 库未安装，将使用命令行模式")
            self._config["use_cli"] = True
            g_context().set_dict("mobile_use_cli_mode", True)

    @allure.step("关闭 Mobile-Use Agent")
    def mu_close_agent(self, **kwargs: Any):
        """关闭 Mobile-Use Agent"""
        if self._agent:
            try:
                self._run_async(self._agent.close())
            except Exception:
                pass
            self._agent = None
            self._device = None
            self._llm = None
            print("Mobile-Use Agent 已关闭")
        
        g_context().set_dict("mobile_use_agent", None)
        g_context().set_dict("mobile_use_device", None)
        g_context().set_dict("mobile_use_llm", None)

    # ==================== 核心 AI 任务关键字 ====================

    @allure.step("AI 执行移动端任务: {goal}")
    def mu_run_task(self, **kwargs: Any):
        """
        使用 AI Agent 执行移动端任务
        
        这是 mobile-use 的核心功能，可以用自然语言描述一个完整的任务，
        AI 会自动规划并执行所有必要的步骤。
        
        参数:
            goal: 任务描述 (自然语言)
            output_description: 输出格式描述 (可选，用于数据抓取)
            max_steps: 最大步骤数 (可选)
            save_result: 是否保存结果到变量 (可选)
            variable_name: 保存结果的变量名 (可选，默认 mu_task_result)
        
        示例:
            goal: "打开设置，查看当前电池电量"
            goal: "打开微信，发送消息给张三，内容是'你好'"
            goal: "打开淘宝，搜索 iPhone，获取前3个商品的名称和价格"
        """
        goal = kwargs.get("goal")
        output_description = kwargs.get("output_description")
        max_steps = int(kwargs.get("max_steps", self._config.get("max_steps", 30)))
        save_result = str(kwargs.get("save_result", "true")).lower() in ["true", "1", "yes"]
        variable_name = kwargs.get("variable_name", "mu_task_result")
        
        if not goal:
            raise ValueError("任务描述 (goal) 不能为空")
        
        print(f"🤖 开始执行 AI 移动端任务: {goal}")
        
        result = None
        
        if self._config.get("use_cli"):
            result = self._run_task_cli(goal, output_description, max_steps)
        elif self._agent:
            result = self._run_task_agent(goal, output_description, max_steps)
        else:
            result = self._run_task_cli(goal, output_description, max_steps)
        
        print(f"✓ AI 移动端任务执行完成")
        
        if save_result and result:
            g_context().set_dict(variable_name, result)
            print(f"任务结果已保存到变量: {variable_name}")
        
        return result

    def _run_task_agent(self, goal: str, output_description: str = None, max_steps: int = 30):
        """使用 Agent API 执行任务"""
        async def run():
            if output_description:
                result = await self._agent.run(
                    goal=goal,
                    output_description=output_description,
                    max_steps=max_steps
                )
            else:
                result = await self._agent.run(
                    goal=goal,
                    max_steps=max_steps
                )
            return result
        
        try:
            return self._run_async(run())
        except Exception as e:
            self._take_screenshot_on_error(f"AI任务失败_{goal[:20]}")
            raise e

    def _run_task_cli(self, goal: str, output_description: str = None, max_steps: int = 30):
        """使用命令行模式执行任务"""
        try:
            cmd = ["python", "-m", "mobile_use", goal]
            
            if output_description:
                cmd.extend(["--output-description", output_description])
            
            env = os.environ.copy()
            if self._config.get("api_key"):
                env["OPENAI_API_KEY"] = self._config["api_key"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._config.get("timeout", 60),
                env=env
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"命令执行失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"命令执行超时")
            return None
        except FileNotFoundError:
            print("⚠ mobile-use 未安装或不在 PATH 中")
            return None
        except Exception as e:
            self._take_screenshot_on_error(f"CLI任务失败_{goal[:20]}")
            raise e

    @allure.step("AI 分析屏幕: {prompt}")
    def mu_analyze_screen(self, **kwargs: Any):
        """
        AI 分析当前屏幕内容
        
        参数:
            prompt: 分析提示，描述要提取的信息
            variable_name: 保存结果的变量名 (可选，默认 mu_screen_analysis)
        
        示例:
            prompt: "当前打开的是什么应用？列出所有可见的 UI 元素"
            prompt: "屏幕上有哪些按钮？"
            prompt: "当前页面的标题是什么？"
        """
        prompt = kwargs.get("prompt")
        variable_name = kwargs.get("variable_name", "mu_screen_analysis")
        
        if not prompt:
            raise ValueError("分析提示 (prompt) 不能为空")
        
        print(f"🔍 开始分析屏幕: {prompt}")
        
        result = self.mu_run_task(
            goal=f"分析当前屏幕并回答: {prompt}",
            save_result=True,
            variable_name=variable_name
        )
        
        print(f"✓ 屏幕分析完成")
        return result

    @allure.step("AI 点击: {element_desc}")
    def mu_tap(self, **kwargs: Any):
        """
        AI 点击元素
        
        参数:
            element_desc: 元素的自然语言描述
        
        示例:
            element_desc: "登录按钮"
            element_desc: "搜索框"
            element_desc: "第一个商品"
        """
        element_desc = kwargs.get("element_desc")
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        self.mu_run_task(goal=f"点击 {element_desc}", max_steps=10)

    @allure.step("AI 输入: {text}")
    def mu_input(self, **kwargs: Any):
        """
        AI 在指定元素中输入文本
        
        参数:
            element_desc: 输入框的自然语言描述
            text: 要输入的文本
            clear_first: 是否先清空 (默认 true)
        """
        element_desc = kwargs.get("element_desc")
        text = kwargs.get("text", "")
        clear_first = str(kwargs.get("clear_first", "true")).lower() in ["true", "1", "yes"]
        
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        if clear_first:
            goal = f"清空 {element_desc} 的内容，然后输入 {text}"
        else:
            goal = f"在 {element_desc} 中输入 {text}"
        
        self.mu_run_task(goal=goal, max_steps=10)

    @allure.step("AI 滑动: {direction}")
    def mu_swipe(self, **kwargs: Any):
        """
        AI 滑动屏幕
        
        参数:
            direction: 滑动方向 (up/down/left/right)
            element_desc: 滑动到的元素描述 (可选)
        """
        direction = kwargs.get("direction", "up")
        element_desc = kwargs.get("element_desc")
        
        if element_desc:
            goal = f"滑动屏幕直到看到 {element_desc}"
        else:
            direction_map = {
                "up": "向上",
                "down": "向下",
                "left": "向左",
                "right": "向右"
            }
            goal = f"{direction_map.get(direction, direction)}滑动屏幕"
        
        self.mu_run_task(goal=goal, max_steps=10)

    @allure.step("AI 返回")
    def mu_back(self, **kwargs: Any):
        """AI 返回上一页"""
        self.mu_run_task(goal="按返回键", max_steps=5)

    @allure.step("AI 回到主屏幕")
    def mu_home(self, **kwargs: Any):
        """AI 回到主屏幕"""
        self.mu_run_task(goal="按 Home 键回到主屏幕", max_steps=5)

    @allure.step("AI 打开应用: {app_name}")
    def mu_open_app(self, **kwargs: Any):
        """
        AI 打开指定应用
        
        参数:
            app_name: 应用名称
        """
        app_name = kwargs.get("app_name")
        if not app_name:
            raise ValueError("应用名称不能为空")
        
        self.mu_run_task(goal=f"打开 {app_name} 应用", max_steps=15)

    @allure.step("AI 关闭应用: {app_name}")
    def mu_close_app(self, **kwargs: Any):
        """
        AI 关闭指定应用
        
        参数:
            app_name: 应用名称 (可选，默认关闭当前应用)
        """
        app_name = kwargs.get("app_name", "当前")
        self.mu_run_task(goal=f"关闭 {app_name} 应用", max_steps=10)

    # ==================== 数据抓取关键字 ====================

    @allure.step("AI 提取数据: {data_desc}")
    def mu_extract_data(self, **kwargs: Any):
        """
        AI 从屏幕提取结构化数据
        
        参数:
            data_desc: 要提取的数据描述
            output_format: 输出格式描述 (如 "JSON 数组，包含 name 和 price 字段")
            variable_name: 保存结果的变量名 (可选)
        
        示例:
            data_desc: "获取前3个商品的名称和价格"
            output_format: "JSON 数组，每个对象包含 name 和 price 字段"
        """
        data_desc = kwargs.get("data_desc")
        output_format = kwargs.get("output_format", "JSON 格式")
        variable_name = kwargs.get("variable_name", "mu_extracted_data")
        
        if not data_desc:
            raise ValueError("数据描述不能为空")
        
        result = self.mu_run_task(
            goal=data_desc,
            output_description=output_format,
            save_result=True,
            variable_name=variable_name
        )
        
        if result:
            try:
                parsed = json.loads(result)
                g_context().set_dict(variable_name, parsed)
                return parsed
            except json.JSONDecodeError:
                return result
        
        return result

    @allure.step("AI 获取文本: {element_desc}")
    def mu_get_text(self, **kwargs: Any):
        """
        AI 获取元素文本
        
        参数:
            element_desc: 元素描述
            variable_name: 保存结果的变量名
        """
        element_desc = kwargs.get("element_desc")
        variable_name = kwargs.get("variable_name", "mu_text")
        
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        result = self.mu_run_task(
            goal=f"获取 {element_desc} 的文本内容",
            output_description="只返回文本内容，不要其他说明",
            save_result=True,
            variable_name=variable_name
        )
        
        return result

    # ==================== 断言关键字 ====================

    @allure.step("AI 断言元素可见: {element_desc}")
    def mu_assert_visible(self, **kwargs: Any):
        """
        AI 断言元素可见
        
        参数:
            element_desc: 元素描述
        """
        element_desc = kwargs.get("element_desc")
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        result = self.mu_run_task(
            goal=f"检查 {element_desc} 是否在屏幕上可见，如果可见回答 YES，否则回答 NO",
            output_description="只回答 YES 或 NO",
            max_steps=10
        )
        
        if result and "YES" in result.upper():
            print(f"✓ 断言成功: {element_desc} 可见")
        else:
            self._take_screenshot_on_error(f"断言失败_{element_desc[:20]}")
            raise AssertionError(f"断言失败: {element_desc} 不可见")

    @allure.step("AI 断言文本包含: {expected_text}")
    def mu_assert_text_contains(self, **kwargs: Any):
        """
        AI 断言屏幕包含指定文本
        
        参数:
            expected_text: 期望包含的文本
            element_desc: 元素描述 (可选，默认整个屏幕)
        """
        expected_text = kwargs.get("expected_text")
        element_desc = kwargs.get("element_desc", "屏幕")
        
        if not expected_text:
            raise ValueError("期望文本不能为空")
        
        result = self.mu_run_task(
            goal=f"检查 {element_desc} 是否包含文本 '{expected_text}'，如果包含回答 YES，否则回答 NO",
            output_description="只回答 YES 或 NO",
            max_steps=10
        )
        
        if result and "YES" in result.upper():
            print(f"✓ 断言成功: {element_desc} 包含文本 '{expected_text}'")
        else:
            self._take_screenshot_on_error(f"断言失败_文本_{expected_text[:20]}")
            raise AssertionError(f"断言失败: {element_desc} 不包含文本 '{expected_text}'")

    # ==================== 高级功能关键字 ====================

    @allure.step("AI 登录")
    def mu_login(self, **kwargs: Any):
        """
        AI 智能登录
        
        参数:
            username: 用户名
            password: 密码
            app_name: 应用名称 (可选)
        """
        username = kwargs.get("username")
        password = kwargs.get("password")
        app_name = kwargs.get("app_name")
        
        if not username or not password:
            raise ValueError("用户名和密码不能为空")
        
        if app_name:
            goal = f"打开 {app_name}，使用用户名 {username} 和密码 {password} 登录"
        else:
            goal = f"使用用户名 {username} 和密码 {password} 登录"
        
        self.mu_run_task(goal=goal, max_steps=20)

    @allure.step("AI 搜索: {keyword}")
    def mu_search(self, **kwargs: Any):
        """
        AI 智能搜索
        
        参数:
            keyword: 搜索关键词
            app_name: 应用名称 (可选)
        """
        keyword = kwargs.get("keyword")
        app_name = kwargs.get("app_name")
        
        if not keyword:
            raise ValueError("搜索关键词不能为空")
        
        if app_name:
            goal = f"在 {app_name} 中搜索 {keyword}"
        else:
            goal = f"搜索 {keyword}"
        
        self.mu_run_task(goal=goal, max_steps=15)

    @allure.step("AI 发送消息")
    def mu_send_message(self, **kwargs: Any):
        """
        AI 发送消息
        
        参数:
            recipient: 收件人
            message: 消息内容
            app_name: 应用名称 (如 微信、短信 等)
        """
        recipient = kwargs.get("recipient")
        message = kwargs.get("message")
        app_name = kwargs.get("app_name", "消息应用")
        
        if not recipient or not message:
            raise ValueError("收件人和消息内容不能为空")
        
        goal = f"打开 {app_name}，发送消息给 {recipient}，内容是: {message}"
        self.mu_run_task(goal=goal, max_steps=25)

    @allure.step("AI 截图")
    def mu_screenshot(self, **kwargs: Any):
        """
        AI 截图
        
        参数:
            filename: 截图文件名 (可选)
            description: 截图描述 (可选)
        """
        filename = kwargs.get("filename", f"mu_screenshot_{time.strftime('%Y%m%d_%H%M%S')}")
        description = kwargs.get("description", "Mobile-Use 截图")
        
        try:
            from ..utils.AppiumManager import AppiumManager
            driver = AppiumManager.get_driver()
            if driver:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                screenshot_dir = os.path.join(project_root, "reports", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                if not str(filename).endswith(".png"):
                    filename = f"{filename}.png"
                
                filepath = os.path.join(screenshot_dir, filename)
                driver.get_screenshot_as_file(filepath)
                
                with open(filepath, "rb") as f:
                    allure.attach(f.read(), name=description, attachment_type=allure.attachment_type.PNG)
                
                print(f"✓ 截图已保存: {filepath}")
                return filepath
        except Exception as e:
            print(f"截图失败: {e}")
        
        return None

    @allure.step("AI 等待: {condition}")
    def mu_wait(self, **kwargs: Any):
        """
        AI 等待条件满足
        
        参数:
            condition: 等待条件描述
            timeout: 超时时间秒数 (默认 30)
        """
        condition = kwargs.get("condition")
        timeout = int(kwargs.get("timeout", 30))
        
        if not condition:
            raise ValueError("等待条件不能为空")
        
        goal = f"等待直到 {condition}，最多等待 {timeout} 秒"
        self.mu_run_task(goal=goal, max_steps=timeout // 2)


# 创建全局实例
_mobile_use_keywords = None


def get_mobile_use_keywords() -> MobileUseKeywords:
    """获取 MobileUseKeywords 单例实例"""
    global _mobile_use_keywords
    if _mobile_use_keywords is None:
        _mobile_use_keywords = MobileUseKeywords()
    return _mobile_use_keywords
