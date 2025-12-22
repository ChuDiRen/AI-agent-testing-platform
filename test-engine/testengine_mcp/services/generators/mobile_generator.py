"""
Mobile 测试用例生成器
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGenerator


class MobileCaseGenerator(BaseGenerator):
    """Mobile 测试用例生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        platform: str = "android",
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成 Mobile 测试用例
        
        操作类型:
        - click: 点击
        - input: 输入
        - clear: 清空
        - long_press: 长按
        - swipe: 滑动
        - tap: 点击坐标
        - wait: 等待
        - screenshot: 截图
        - back/home: 系统键
        - assert_*: 各类断言
        """
        steps = []
        
        # 1. 启动 App
        if platform.lower() == "android":
            steps.append({
                "启动App": {
                    "关键字": "start_app",
                    "app_package": app_package or "{{APP_PACKAGE}}",
                    "app_activity": app_activity or "{{APP_ACTIVITY}}"
                }
            })
        else:
            steps.append({
                "启动App": {
                    "关键字": "start_app",
                    "bundle_id": bundle_id or "{{BUNDLE_ID}}"
                }
            })
        
        # 2. 等待 App 启动
        steps.append({
            "等待App启动": {
                "关键字": "wait_time",
                "seconds": 3
            }
        })
        
        # 3. 添加用户定义的操作
        if actions:
            for i, action in enumerate(actions):
                step = self._build_action_step(action, i)
                if step:
                    steps.append(step)
        
        # 4. 关闭 App
        steps.append({
            "关闭App": {
                "关键字": "close_app"
            }
        })
        
        # 构建完整用例
        case = {
            "desc": description or name,
            "steps": steps
        }
        
        # 保存用例
        save_file = self._get_save_path(save_path, name, "mobile-cases_yaml")
        self._save_case(save_file, case)
        
        return self._build_result(
            case, save_file, "mobile", "Mobile 测试用例已生成",
            platform=platform,
            context_hint={
                "PLATFORM": platform,
                "APP_PACKAGE": app_package,
                "APP_ACTIVITY": app_activity,
                "BUNDLE_ID": bundle_id
            }
        )
    
    def _build_action_step(self, action: Dict[str, Any], index: int) -> Optional[Dict]:
        """构建 Mobile 操作步骤"""
        action_type = action.get("type", "")
        
        if action_type == "click":
            return {f"点击元素_{index+1}": {
                "关键字": "click_element",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "input":
            return {f"输入文本_{index+1}": {
                "关键字": "input_text",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", ""),
                "text": action.get("text", "")
            }}
        
        elif action_type == "clear":
            return {f"清空输入框_{index+1}": {
                "关键字": "clear_element",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "long_press":
            return {f"长按元素_{index+1}": {
                "关键字": "long_press_element",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", ""),
                "duration": action.get("duration", 2)
            }}
        
        elif action_type == "swipe":
            return {f"滑动_{index+1}": {
                "关键字": "swipe",
                "direction": action.get("direction", "up"),
                "distance": action.get("distance", 500)
            }}
        
        elif action_type == "tap":
            return {f"点击坐标_{index+1}": {
                "关键字": "tap_coordinate",
                "x": action.get("x", 0),
                "y": action.get("y", 0)
            }}
        
        elif action_type == "wait":
            return {f"等待_{index+1}": {
                "关键字": "wait_time",
                "seconds": action.get("seconds", 1)
            }}
        
        elif action_type == "wait_element":
            return {f"等待元素_{index+1}": {
                "关键字": "wait_for_element",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", ""),
                "timeout": action.get("timeout", 10)
            }}
        
        elif action_type == "screenshot":
            return {f"截图_{index+1}": {
                "关键字": "take_screenshot",
                "filename": action.get("filename", f"mobile_screenshot_{index+1}")
            }}
        
        elif action_type == "back":
            return {f"返回键_{index+1}": {
                "关键字": "press_back"
            }}
        
        elif action_type == "home":
            return {f"Home键_{index+1}": {
                "关键字": "press_home"
            }}
        
        elif action_type == "assert_text":
            return {f"断言文本_{index+1}": {
                "关键字": "assert_text_exists",
                "text": action.get("expected", "")
            }}
        
        elif action_type == "assert_element":
            return {f"断言元素存在_{index+1}": {
                "关键字": "assert_element_exists",
                "locator_type": action.get("locator_type", "id"),
                "element": action.get("locator", "")
            }}
        
        elif action_type == "assert_toast":
            return {f"断言Toast_{index+1}": {
                "关键字": "assert_toast_message",
                "expected_text": action.get("expected", "")
            }}
        
        return None
