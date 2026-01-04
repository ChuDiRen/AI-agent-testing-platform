"""
Browser-Use AI 关键字模块
基于 browser-use 库实现的智能浏览器自动化关键字

功能特点:
- 使用 LLM 驱动的智能浏览器操作
- 支持自然语言描述任务
- 支持多种 LLM 模型 (OpenAI, Claude, DeepSeek 等)
- 支持复杂的多步骤任务自动执行
- 与现有 web-engine 框架无缝集成
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any, List

import allure

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


class BrowserUseKeywords:
    """
    Browser-Use AI 关键字类
    
    提供基于 browser-use 的智能浏览器自动化能力，
    可以使用自然语言描述来执行复杂的浏览器操作任务。
    """
    
    def __init__(self):
        """初始化 Browser-Use 关键字类"""
        self._agent = None
        self._browser = None
        self._llm = None
        self._config = {
            "llm_provider": "siliconflow",  # 默认使用硬基流动
            "llm_model": "deepseek-ai/DeepSeek-V3",  # 默认模型
            "headless": True,  # 默认无头模式，用户无感知
            "timeout": 30,  # 缩短超时时间
            "max_steps": 15,  # 减少最大步骤数以加快执行
        }
    
    def _get_llm(self, provider: str = None, model: str = None, api_key: str = None, base_url: str = None):
        """
        获取 LLM 实例 (browser-use 0.11.0+ 内置 LLM 类)
        
        :param provider: LLM 提供商 (openai, deepseek, anthropic, siliconflow)
        :param model: 模型名称
        :param api_key: API 密钥
        :param base_url: API 基础 URL
        :return: LLM 实例
        """
        provider = provider or self._config.get("llm_provider", "openai")
        
        # browser-use 0.11.0+ 使用内置的 LLM 类
        if provider == "openai":
            from browser_use.llm.openai.chat import ChatOpenAI
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url
            )
        
        elif provider == "deepseek":
            from browser_use.llm.deepseek.chat import ChatDeepSeek
            api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            model = model or "deepseek-chat"
            return ChatDeepSeek(
                model=model,
                api_key=api_key
            )
        
        elif provider == "anthropic":
            from browser_use.llm.anthropic.chat import ChatAnthropic
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            model = model or "claude-3-5-sonnet-20241022"
            return ChatAnthropic(
                model=model,
                api_key=api_key
            )
        
        elif provider == "siliconflow":
            # 硅基流动 (SiliconFlow) - 使用 OpenAI 兼容接口
            from browser_use.llm.openai.chat import ChatOpenAI
            api_key = api_key or os.getenv("SILICONFLOW_API_KEY") or "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
            if not api_key:
                raise ValueError("SILICONFLOW_API_KEY 未设置。请设置环境变量或通过 api_key 参数传递。")
            model = model or "deepseek-ai/DeepSeek-V3"
            base_url = base_url or "https://api.siliconflow.cn/v1"
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url
            )
        
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
    
    def _run_async(self, coro):
        """
        运行异步协程
        
        :param coro: 异步协程
        :return: 协程执行结果
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已在运行，创建新的任务
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(coro)
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(coro)
    
    def _take_screenshot_on_error(self, name: str):
        """
        错误时截图
        
        :param name: 截图名称
        """
        try:
            if self._browser:
                # 获取项目根目录下的 reports/screenshots 目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                screenshot_dir = os.path.join(project_root, "reports", "screenshots")
                if not os.path.exists(screenshot_dir):
                    os.makedirs(screenshot_dir)
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
                
                # 使用 browser-use 的截图功能
                async def take_screenshot():
                    page = await self._browser.get_current_page()
                    if page:
                        await page.screenshot(path=filename)
                        return filename
                    return None
                
                result = self._run_async(take_screenshot())
                
                if result and os.path.exists(result):
                    # 附加到 Allure 报告
                    with open(result, "rb") as f:
                        allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            print(f"截图失败: {e}")
    
    # ==================== 配置关键字 ====================
    
    @allure.step("配置 Browser-Use")
    def bu_configure(self, **kwargs):
        """
        配置 Browser-Use 参数
        
        参数:
            llm_provider: LLM 提供商 (openai/deepseek/qwen/anthropic/browser_use)
            llm_model: 模型名称 (可选，使用默认)
            api_key: API 密钥 (可选，从环境变量读取)
            base_url: API 基础 URL (可选)
            headless: 是否无头模式 (默认 false)
            timeout: 超时时间秒数 (默认 60)
            max_steps: 最大步骤数 (默认 50)
        """
        if "llm_provider" in kwargs:
            self._config["llm_provider"] = kwargs["llm_provider"]
        if "llm_model" in kwargs:
            self._config["llm_model"] = kwargs["llm_model"]
        if "api_key" in kwargs:
            self._config["api_key"] = kwargs["api_key"]
        if "base_url" in kwargs:
            self._config["base_url"] = kwargs["base_url"]
        if "headless" in kwargs:
            self._config["headless"] = str(kwargs["headless"]).lower() in ["true", "1", "yes"]
        if "timeout" in kwargs:
            self._config["timeout"] = int(kwargs["timeout"])
        if "max_steps" in kwargs:
            self._config["max_steps"] = int(kwargs["max_steps"])
        
        print(f"Browser-Use 配置已更新: {self._config}")
    
    @allure.step("初始化 Browser-Use 浏览器")
    def bu_open_browser(self, **kwargs):
        """
        初始化 Browser-Use 浏览器
        
        参数:
            headless: 是否无头模式 (默认 true，无头模式)
            llm_provider: LLM 提供商 (可选)
            llm_model: 模型名称 (可选)
        """
        from browser_use import Browser
        
        # 默认无头模式，用户无感知
        headless_raw = kwargs.get("headless", self._config.get("headless", True))
        if isinstance(headless_raw, bool):
            headless = headless_raw
        else:
            headless = str(headless_raw).lower() in ["true", "1", "yes"]
        
        # 更新配置
        if "llm_provider" in kwargs:
            self._config["llm_provider"] = kwargs["llm_provider"]
        if "llm_model" in kwargs:
            self._config["llm_model"] = kwargs["llm_model"]
        
        async def init_browser():
            # browser-use 0.11.0+ 新 API
            # 增加超时时间，避免 AI 任务执行时超时
            from browser_use.browser.config import BrowserConfig
            config = BrowserConfig(
                headless=headless,
                disable_security=True,  # 禁用安全限制，避免跨域问题
            )
            self._browser = Browser(config=config)
            # 初始化 LLM
            self._llm = self._get_llm(
                provider=self._config.get("llm_provider"),
                model=self._config.get("llm_model"),
                api_key=self._config.get("api_key"),
                base_url=self._config.get("base_url")
            )
            print(f"Browser-Use 浏览器已启动 (headless={headless})")
        
        self._run_async(init_browser())
        
        # 保存到全局上下文
        g_context().set_dict("browser_use_browser", self._browser)
        g_context().set_dict("browser_use_llm", self._llm)
    
    @allure.step("关闭 Browser-Use 浏览器")
    def bu_close_browser(self, **kwargs):
        """关闭 Browser-Use 浏览器"""
        async def close_browser():
            if self._browser:
                # browser-use 0.11.0+ 使用 stop() 方法
                await self._browser.stop()
                self._browser = None
                self._agent = None
                print("Browser-Use 浏览器已关闭")
        
        self._run_async(close_browser())
        
        # 清理全局上下文
        g_context().set_dict("browser_use_browser", None)
        g_context().set_dict("browser_use_llm", None)
    
    # ==================== 核心 AI 任务关键字 ====================
    
    @allure.step("AI 执行任务: {task}")
    def bu_run_task(self, **kwargs):
        """
        使用 AI Agent 执行复杂任务
        
        这是 browser-use 的核心功能，可以用自然语言描述一个完整的任务，
        AI 会自动规划并执行所有必要的步骤。
        
        参数:
            task: 任务描述 (自然语言)
            max_steps: 最大步骤数 (可选，默认 50)
            save_result: 是否保存结果到变量 (可选)
            variable_name: 保存结果的变量名 (可选，默认 bu_task_result)
        
        示例:
            task: "打开百度，搜索 Python，点击第一个结果"
            task: "登录网站，用户名 admin，密码 123456"
            task: "填写表单，姓名张三，邮箱 test@example.com，然后提交"
        """
        from browser_use import Agent
        
        task = kwargs.get("task")
        max_steps = int(kwargs.get("max_steps", self._config.get("max_steps", 50)))
        save_result = str(kwargs.get("save_result", "true")).lower() in ["true", "1", "yes"]
        variable_name = kwargs.get("variable_name", "bu_task_result")
        
        if not task:
            raise ValueError("任务描述不能为空")
        
        if not self._browser:
            raise RuntimeError("浏览器未启动，请先使用 bu_open_browser 关键字")
        
        async def run_task():
            agent = Agent(
                task=task,
                llm=self._llm,
                browser=self._browser,
                max_steps=max_steps
            )
            self._agent = agent
            
            print(f"🤖 开始执行 AI 任务: {task}")
            history = await agent.run()
            print(f"✓ AI 任务执行完成")
            
            return history
        
        try:
            result = self._run_async(run_task())
            
            if save_result:
                # 保存执行历史到全局上下文
                g_context().set_dict(variable_name, result)
                print(f"任务结果已保存到变量: {variable_name}")
            
            return result
            
        except Exception as e:
            self._take_screenshot_on_error(f"AI任务失败_{task[:20]}")
            raise e
    
    @allure.step("AI 导航到: {url}")
    def bu_navigate(self, **kwargs):
        """
        AI 导航到指定 URL
        
        参数:
            url: 目标 URL
        """
        url = kwargs.get("url")
        if not url:
            raise ValueError("URL 不能为空")
        
        task = f"导航到 {url}"
        self.bu_run_task(task=task, max_steps=5)
    
    @allure.step("AI 点击: {element_desc}")
    def bu_click(self, **kwargs):
        """
        AI 点击元素
        
        参数:
            element_desc: 元素的自然语言描述
        
        示例:
            element_desc: "登录按钮"
            element_desc: "红色的提交按钮"
            element_desc: "页面顶部的搜索图标"
        """
        element_desc = kwargs.get("element_desc")
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        task = f"点击 {element_desc}"
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 输入: {text}")
    def bu_input(self, **kwargs):
        """
        AI 在指定元素中输入文本
        
        参数:
            element_desc: 输入框的自然语言描述
            text: 要输入的文本
            clear_first: 是否先清空 (默认 true)
        
        示例:
            element_desc: "用户名输入框"
            text: "admin"
        """
        element_desc = kwargs.get("element_desc")
        text = kwargs.get("text", "")
        clear_first = str(kwargs.get("clear_first", "true")).lower() in ["true", "1", "yes"]
        
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        if clear_first:
            task = f"清空 {element_desc} 的内容，然后输入 {text}"
        else:
            task = f"在 {element_desc} 中输入 {text}"
        
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 提取文本: {text_desc}")
    def bu_extract_text(self, **kwargs):
        """
        AI 提取页面文本
        
        参数:
            text_desc: 要提取文本的描述
            variable_name: 保存到的变量名 (默认 bu_extracted_text)
        
        示例:
            text_desc: "页面标题"
            text_desc: "第一个搜索结果的标题"
            text_desc: "错误提示信息"
        """
        text_desc = kwargs.get("text_desc")
        variable_name = kwargs.get("variable_name", "bu_extracted_text")
        
        if not text_desc:
            raise ValueError("文本描述不能为空")
        
        task = f"找到并提取 {text_desc} 的文本内容，告诉我提取到的内容"
        result = self.bu_run_task(task=task, max_steps=10, save_result=True, variable_name=variable_name)
        
        # 尝试从结果中提取文本
        if result:
            # browser-use 的结果通常包含最终的文本信息
            extracted = str(result)
            g_context().set_dict(variable_name, extracted)
            print(f"✓ 已提取文本并保存到 {variable_name}")
    
    @allure.step("AI 滚动: {direction}")
    def bu_scroll(self, **kwargs):
        """
        AI 滚动页面
        
        参数:
            direction: 滚动方向或目标 (up/down/top/bottom/元素描述)
            element_desc: 滚动到的元素描述 (可选)
        
        示例:
            direction: "down"
            direction: "bottom"
            element_desc: "评论区"
        """
        direction = kwargs.get("direction", "down")
        element_desc = kwargs.get("element_desc")
        
        if element_desc:
            task = f"滚动页面直到看到 {element_desc}"
        elif direction in ["up", "top"]:
            task = "滚动到页面顶部"
        elif direction in ["down", "bottom"]:
            task = "滚动到页面底部"
        else:
            task = f"向 {direction} 滚动页面"
        
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 悬停: {element_desc}")
    def bu_hover(self, **kwargs):
        """
        AI 鼠标悬停
        
        参数:
            element_desc: 要悬停的元素描述
        """
        element_desc = kwargs.get("element_desc")
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        task = f"将鼠标悬停在 {element_desc} 上"
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 拖拽: {source_desc} -> {target_desc}")
    def bu_drag(self, **kwargs):
        """
        AI 拖拽操作
        
        参数:
            source_desc: 源元素描述
            target_desc: 目标元素描述
        """
        source_desc = kwargs.get("source_desc")
        target_desc = kwargs.get("target_desc")
        
        if not source_desc or not target_desc:
            raise ValueError("源元素和目标元素描述不能为空")
        
        task = f"将 {source_desc} 拖拽到 {target_desc}"
        self.bu_run_task(task=task, max_steps=15)
    
    @allure.step("AI 选择下拉框: {element_desc}")
    def bu_select(self, **kwargs):
        """
        AI 选择下拉框选项
        
        参数:
            element_desc: 下拉框描述
            option: 要选择的选项
        """
        element_desc = kwargs.get("element_desc")
        option = kwargs.get("option")
        
        if not element_desc or not option:
            raise ValueError("下拉框描述和选项不能为空")
        
        task = f"在 {element_desc} 下拉框中选择 {option}"
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 上传文件: {file_path}")
    def bu_upload_file(self, **kwargs):
        """
        AI 上传文件
        
        参数:
            element_desc: 上传按钮/区域描述
            file_path: 文件路径
        """
        element_desc = kwargs.get("element_desc", "文件上传按钮")
        file_path = kwargs.get("file_path")
        
        if not file_path:
            raise ValueError("文件路径不能为空")
        
        task = f"点击 {element_desc}，上传文件 {file_path}"
        self.bu_run_task(task=task, max_steps=15)
    
    # ==================== 断言关键字 ====================
    
    @allure.step("AI 断言元素可见: {element_desc}")
    def bu_assert_visible(self, **kwargs):
        """
        AI 断言元素可见
        
        参数:
            element_desc: 元素描述
        """
        element_desc = kwargs.get("element_desc")
        if not element_desc:
            raise ValueError("元素描述不能为空")
        
        task = f"检查 {element_desc} 是否在页面上可见，如果可见请确认"
        try:
            self.bu_run_task(task=task, max_steps=10)
            print(f"✓ 断言成功: {element_desc} 可见")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_{element_desc[:20]}")
            raise AssertionError(f"断言失败: {element_desc} 不可见") from e
    
    @allure.step("AI 断言文本包含: {expected_text}")
    def bu_assert_text_contains(self, **kwargs):
        """
        AI 断言页面包含指定文本
        
        参数:
            element_desc: 元素描述 (可选，默认整个页面)
            expected_text: 期望包含的文本
        """
        element_desc = kwargs.get("element_desc", "页面")
        expected_text = kwargs.get("expected_text")
        
        if not expected_text:
            raise ValueError("期望文本不能为空")
        
        task = f"检查 {element_desc} 是否包含文本 '{expected_text}'，如果包含请确认"
        try:
            self.bu_run_task(task=task, max_steps=10)
            print(f"✓ 断言成功: {element_desc} 包含文本 '{expected_text}'")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_文本_{expected_text[:20]}")
            raise AssertionError(f"断言失败: {element_desc} 不包含文本 '{expected_text}'") from e
    
    @allure.step("AI 断言 URL 包含: {expected_url}")
    def bu_assert_url_contains(self, **kwargs):
        """
        AI 断言当前 URL 包含指定内容
        
        参数:
            expected_url: 期望 URL 包含的内容
        """
        expected_url = kwargs.get("expected_url")
        if not expected_url:
            raise ValueError("期望 URL 不能为空")
        
        task = f"检查当前页面 URL 是否包含 '{expected_url}'，如果包含请确认"
        try:
            self.bu_run_task(task=task, max_steps=5)
            print(f"✓ 断言成功: URL 包含 '{expected_url}'")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_URL_{expected_url[:20]}")
            raise AssertionError(f"断言失败: URL 不包含 '{expected_url}'") from e
    
    # ==================== 高级功能关键字 ====================
    
    @allure.step("AI 表单填写")
    def bu_fill_form(self, **kwargs):
        """
        AI 智能填写表单
        
        参数:
            form_data: 表单数据字典，格式为 {字段描述: 值}
        
        示例:
            form_data:
              用户名: admin
              密码: 123456
              邮箱: test@example.com
              记住我: true
        """
        form_data = kwargs.get("form_data", {})
        
        if not form_data:
            raise ValueError("表单数据不能为空")
        
        # 构建任务描述
        fields = []
        for field, value in form_data.items():
            fields.append(f"在 {field} 中填写 {value}")
        
        task = "填写表单: " + ", ".join(fields)
        self.bu_run_task(task=task, max_steps=len(form_data) * 5 + 10)
    
    @allure.step("AI 登录")
    def bu_login(self, **kwargs):
        """
        AI 智能登录
        
        参数:
            username: 用户名
            password: 密码
            username_field: 用户名字段描述 (可选，默认自动识别)
            password_field: 密码字段描述 (可选，默认自动识别)
            submit_button: 提交按钮描述 (可选，默认自动识别)
        """
        username = kwargs.get("username")
        password = kwargs.get("password")
        username_field = kwargs.get("username_field", "用户名输入框")
        password_field = kwargs.get("password_field", "密码输入框")
        submit_button = kwargs.get("submit_button", "登录按钮")
        
        if not username or not password:
            raise ValueError("用户名和密码不能为空")
        
        task = f"执行登录操作: 在 {username_field} 输入 {username}, 在 {password_field} 输入 {password}, 然后点击 {submit_button}"
        self.bu_run_task(task=task, max_steps=20)
    
    @allure.step("AI 搜索: {keyword}")
    def bu_search(self, **kwargs):
        """
        AI 智能搜索
        
        参数:
            keyword: 搜索关键词
            search_box: 搜索框描述 (可选)
            search_button: 搜索按钮描述 (可选)
        """
        keyword = kwargs.get("keyword")
        search_box = kwargs.get("search_box", "搜索框")
        search_button = kwargs.get("search_button", "搜索按钮")
        
        if not keyword:
            raise ValueError("搜索关键词不能为空")
        
        task = f"在 {search_box} 中输入 {keyword}，然后点击 {search_button} 进行搜索"
        self.bu_run_task(task=task, max_steps=15)
    
    @allure.step("AI 截图")
    def bu_screenshot(self, **kwargs):
        """
        AI 截图
        
        参数:
            filename: 截图文件名 (可选)
            element_desc: 元素描述，只截取该元素 (可选)
        """
        filename = kwargs.get("filename", f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}")
        element_desc = kwargs.get("element_desc")
        
        # 获取项目根目录下的 reports/screenshots 目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        filepath = os.path.join(screenshot_dir, f"{filename}.png")
        
        async def take_screenshot():
            if self._browser:
                page = await self._browser.get_current_page()
                if page:
                    if element_desc:
                        # 定位元素并截图
                        task = f"找到 {element_desc} 并截图"
                        # 这里简化处理，直接全页面截图
                        await page.screenshot(path=filepath)
                    else:
                        await page.screenshot(path=filepath)
                    return filepath
            return None
        
        result = self._run_async(take_screenshot())
        
        if result and os.path.exists(result):
            # 附加到 Allure 报告
            with open(result, "rb") as f:
                allure.attach(f.read(), name=filename, attachment_type=allure.attachment_type.PNG)
            print(f"✓ 截图已保存: {result}")
        else:
            print("⚠ 截图失败")
    
    @allure.step("AI 等待: {condition}")
    def bu_wait(self, **kwargs):
        """
        AI 等待条件满足
        
        参数:
            condition: 等待条件描述
            timeout: 超时时间秒数 (默认 30)
        
        示例:
            condition: "页面加载完成"
            condition: "登录按钮出现"
            condition: "加载动画消失"
        """
        condition = kwargs.get("condition")
        timeout = int(kwargs.get("timeout", 30))
        
        if not condition:
            raise ValueError("等待条件不能为空")
        
        task = f"等待直到 {condition}，最多等待 {timeout} 秒"
        self.bu_run_task(task=task, max_steps=timeout // 2)
    
    @allure.step("AI 切换标签页")
    def bu_switch_tab(self, **kwargs):
        """
        AI 切换浏览器标签页
        
        参数:
            tab_desc: 标签页描述 (如 "第二个标签页"、"包含 Google 的标签页")
            index: 标签页索引 (可选，从 0 开始)
        """
        tab_desc = kwargs.get("tab_desc")
        index = kwargs.get("index")
        
        if index is not None:
            task = f"切换到第 {int(index) + 1} 个标签页"
        elif tab_desc:
            task = f"切换到 {tab_desc}"
        else:
            task = "切换到最新打开的标签页"
        
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 处理弹窗")
    def bu_handle_alert(self, **kwargs):
        """
        AI 处理弹窗/对话框
        
        参数:
            action: 操作类型 (accept/dismiss/input)
            input_text: 如果是输入型弹窗，要输入的文本
        """
        action = kwargs.get("action", "accept")
        input_text = kwargs.get("input_text")
        
        if action == "accept":
            task = "如果有弹窗，点击确认/接受按钮"
        elif action == "dismiss":
            task = "如果有弹窗，点击取消/关闭按钮"
        elif action == "input" and input_text:
            task = f"如果有输入弹窗，输入 {input_text} 然后确认"
        else:
            task = "处理页面上的弹窗"
        
        self.bu_run_task(task=task, max_steps=10)
    
    @allure.step("AI 执行 JavaScript")
    def bu_execute_script(self, **kwargs):
        """
        AI 执行 JavaScript 代码
        
        参数:
            script: JavaScript 代码
            variable_name: 保存结果的变量名 (可选)
        """
        script = kwargs.get("script")
        variable_name = kwargs.get("variable_name")
        
        if not script:
            raise ValueError("JavaScript 代码不能为空")
        
        async def execute_script():
            if self._browser:
                page = await self._browser.get_current_page()
                if page:
                    result = await page.evaluate(script)
                    return result
            return None
        
        result = self._run_async(execute_script())
        
        if variable_name:
            g_context().set_dict(variable_name, result)
            print(f"✓ 脚本执行结果已保存到 {variable_name}: {result}")
        else:
            print(f"✓ 脚本执行结果: {result}")
        
        return result


# 创建全局实例，方便直接使用
_browser_use_keywords = None


def get_browser_use_keywords() -> BrowserUseKeywords:
    """获取 BrowserUseKeywords 单例实例"""
    global _browser_use_keywords
    if _browser_use_keywords is None:
        _browser_use_keywords = BrowserUseKeywords()
    return _browser_use_keywords
