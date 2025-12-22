"""
Web 测试用例生成器
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGenerator


class WebCaseGenerator(BaseGenerator):
    """Web 测试用例生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        url: str,
        browser: str = "chromium",
        headless: bool = True,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成 Web 测试用例
        
        操作类型:
        - click: 点击元素
        - input: 输入文本
        - clear: 清空输入框
        - select: 下拉选择
        - hover: 悬停
        - wait: 等待
        - scroll: 滚动
        - screenshot: 截图
        - assert_*: 各类断言
        """
        steps = []
        
        # 1. 打开浏览器
        steps.append({
            "打开浏览器": {
                "关键字": "open_browser",
                "browser": "{{BROWSER}}",
                "headless": "{{HEADLESS}}",
                "implicit_wait": "{{IMPLICIT_WAIT}}",
                "window_size": "{{WINDOW_SIZE}}"
            }
        })
        
        # 2. 导航到目标页面
        steps.append({
            "导航到目标页面": {
                "关键字": "navigate_to",
                "url": url
            }
        })
        
        # 3. 等待页面加载
        steps.append({
            "等待页面加载": {
                "关键字": "wait_for_page_load",
                "wait_until": "load"
            }
        })
        
        # 4. 添加用户定义的操作
        if actions:
            for i, action in enumerate(actions):
                step = self._build_action_step(action, i)
                if step:
                    steps.append(step)
        
        # 5. 关闭浏览器
        steps.append({
            "关闭浏览器": {
                "关键字": "close_browser"
            }
        })
        
        # 构建完整用例
        case = {
            "desc": description or name,
            "steps": steps
        }
        
        # 保存用例
        save_file = self._get_save_path(save_path, name, "web-cases_yaml")
        self._save_case(save_file, case)
        
        return self._build_result(
            case, save_file, "web", "Web 测试用例已生成",
            context_hint={
                "BROWSER": browser,
                "HEADLESS": headless,
                "IMPLICIT_WAIT": 10,
                "WINDOW_SIZE": "1920,1080"
            }
        )
    
    def _build_action_step(self, action: Dict[str, Any], index: int) -> Optional[Dict]:
        """构建 Web 操作步骤"""
        action_type = action.get("type", "")
        
        if action_type == "click":
            return {f"点击元素_{index+1}": {
                "关键字": "click_element",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "input":
            return {f"输入文本_{index+1}": {
                "关键字": "input_text",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", ""),
                "text": action.get("text", "")
            }}
        
        elif action_type == "clear":
            return {f"清空输入框_{index+1}": {
                "关键字": "clear_element",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "select":
            return {f"下拉选择_{index+1}": {
                "关键字": "select_option",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", ""),
                "value": action.get("value", "")
            }}
        
        elif action_type == "hover":
            return {f"悬停元素_{index+1}": {
                "关键字": "hover_element",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "double_click":
            return {f"双击元素_{index+1}": {
                "关键字": "double_click_element",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "wait":
            return {f"等待_{index+1}": {
                "关键字": "wait_time",
                "seconds": action.get("seconds", 1)
            }}
        
        elif action_type == "wait_element":
            return {f"等待元素_{index+1}": {
                "关键字": "wait_for_element",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", ""),
                "state": action.get("state", "visible"),
                "timeout": action.get("timeout", 10000)
            }}
        
        elif action_type == "scroll":
            return {f"滚动页面_{index+1}": {
                "关键字": "scroll_page",
                "direction": action.get("direction", "down"),
                "distance": action.get("distance", 500)
            }}
        
        elif action_type == "screenshot":
            return {f"截图_{index+1}": {
                "关键字": "take_screenshot",
                "filename": action.get("filename", f"screenshot_{index+1}")
            }}
        
        elif action_type == "assert_text":
            return {f"断言文本_{index+1}": {
                "关键字": "assert_text_contains",
                "expected_text": action.get("expected", "")
            }}
        
        elif action_type == "assert_title":
            return {f"断言标题_{index+1}": {
                "关键字": "assert_title_contains",
                "expected_text": action.get("expected", "")
            }}
        
        elif action_type == "assert_url":
            return {f"断言URL_{index+1}": {
                "关键字": "assert_url",
                "expected_url": action.get("expected", ""),
                "match_type": action.get("match", "contains")
            }}
        
        elif action_type == "assert_element":
            keyword = "assert_element_visible" if action.get("visible", True) else "assert_element_hidden"
            return {f"断言元素存在_{index+1}": {
                "关键字": keyword,
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "assert_element_text":
            return {f"断言元素文本_{index+1}": {
                "关键字": "assert_element_text",
                "locator_type": action.get("locator_type", "css"),
                "element": action.get("locator", ""),
                "expected_text": action.get("expected", "")
            }}
        
        return None
