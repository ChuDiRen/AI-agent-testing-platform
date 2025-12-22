"""
Pytest 脚本生成器
生成 Python 格式的测试用例脚本
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseGenerator


class PytestApiGenerator(BaseGenerator):
    """API Pytest 脚本生成器"""
    
    def generate(
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
        class_name: Optional[str] = None,
        feature: str = "API测试",
        story: str = "接口测试"
    ) -> Dict[str, Any]:
        """生成 API Pytest 脚本"""
        
        # 生成类名和方法名
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_class_name(name)
        method_name = f"test_{safe_name}"
        
        # 构建脚本内容
        script = self._build_api_script(
            class_name=class_name,
            method_name=method_name,
            description=description,
            url=url,
            method=method,
            headers=headers,
            params=params,
            data=data,
            json_body=json_body,
            extracts=extracts,
            asserts=asserts,
            feature=feature,
            story=story
        )
        
        # 保存文件
        save_file = self._get_pytest_save_path(save_path, safe_name, "api-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "API Pytest 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "api",
            "format": "pytest"
        }
    
    def _build_api_script(
        self,
        class_name: str,
        method_name: str,
        description: str,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]],
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
        json_body: Optional[Dict[str, Any]],
        extracts: Optional[List[Dict[str, str]]],
        asserts: Optional[List[Dict[str, Any]]],
        feature: str,
        story: str
    ) -> str:
        """构建 API Pytest 脚本内容"""
        
        lines = [
            '"""',
            f'{description}',
            '"""',
            'import allure',
            'import pytest',
            '',
            '',
            f'@allure.feature("{feature}")',
            f'@allure.story("{story}")',
            f'class {class_name}:',
            f'    """{description}"""',
            '',
            f'    @allure.title("{description}")',
            '    @allure.severity(allure.severity_level.NORMAL)',
            '    @pytest.mark.asyncio',
            f'    async def {method_name}(self, base_url: str, api_client):',
            '        """',
            f'        测试用例：{description}',
            '        """',
        ]
        
        # 准备请求数据
        lines.append('        with allure.step("准备请求数据"):')
        lines.append(f'            url = "{url}"')
        
        if headers:
            lines.append(f'            headers = {repr(headers)}')
        else:
            lines.append('            headers = {}')
        
        if params:
            lines.append(f'            params = {repr(params)}')
        
        if data:
            lines.append(f'            data = {repr(data)}')
        
        if json_body:
            lines.append(f'            json_body = {repr(json_body)}')
        
        # 发送请求
        lines.append('')
        lines.append('        with allure.step("发送请求"):')
        
        method_lower = method.lower()
        request_args = ['url']
        
        if headers:
            request_args.append('headers=headers')
        if params:
            request_args.append('params=params')
        if data:
            request_args.append('data=data')
        if json_body:
            request_args.append('json=json_body')
        
        args_str = ', '.join(request_args)
        lines.append(f'            response = await api_client.{method_lower}({args_str})')
        lines.append('            allure.attach(response.text, "响应数据", allure.attachment_type.JSON)')
        
        # 数据提取
        if extracts:
            lines.append('')
            lines.append('        with allure.step("提取响应数据"):')
            lines.append('            import jsonpath')
            lines.append('            result = response.json()')
            for extract in extracts:
                var_name = extract.get('name', 'extracted_value')
                jsonpath_expr = extract.get('jsonpath', '$')
                index = extract.get('index', 0)
                lines.append(f'            {var_name}_list = jsonpath.jsonpath(result, "{jsonpath_expr}")')
                lines.append(f'            {var_name} = {var_name}_list[{index}] if {var_name}_list else None')
                lines.append(f'            allure.attach(str({var_name}), "{var_name}", allure.attachment_type.TEXT)')
        
        # 断言
        lines.append('')
        lines.append('        with allure.step("验证响应"):')
        
        if asserts:
            for i, assertion in enumerate(asserts):
                assert_type = assertion.get('type', 'status_code')
                
                if assert_type == 'status_code':
                    expected = assertion.get('expected', 200)
                    lines.append(f'            assert response.status_code == {expected}, f"状态码错误: {{response.status_code}}"')
                
                elif assert_type == 'contains':
                    expected = assertion.get('expected', '')
                    lines.append(f'            assert "{expected}" in response.text, "响应中未包含预期内容"')
                
                elif assert_type == 'equals':
                    value = assertion.get('value', '')
                    expected = assertion.get('expected', '')
                    lines.append(f'            assert {value} == "{expected}", "值不匹配"')
                
                elif assert_type == 'jsonpath':
                    jsonpath_expr = assertion.get('jsonpath', '$')
                    expected = assertion.get('expected', '')
                    operator = assertion.get('operator', '==')
                    lines.append('            import jsonpath')
                    lines.append('            result = response.json()')
                    lines.append(f'            values = jsonpath.jsonpath(result, "{jsonpath_expr}")')
                    lines.append(f'            assert values and values[0] {operator} {repr(expected)}, "JSONPath 断言失败"')
                
                elif assert_type == 'response_time':
                    max_ms = assertion.get('max_ms', 1000)
                    lines.append(f'            assert response.elapsed.total_seconds() * 1000 < {max_ms}, "响应时间超时"')
        else:
            # 默认断言
            lines.append('            assert response.status_code == 200, f"状态码错误: {response.status_code}"')
        
        lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        """获取 Pytest 脚本保存路径"""
        if save_path:
            return Path(save_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"test_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        """转换为 snake_case"""
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_class_name(self, name: str) -> str:
        """转换为类名（PascalCase）"""
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        
        return 'Test' + ''.join(word.capitalize() for word in words)


class PytestMobileGenerator(BaseGenerator):
    """Mobile Pytest 脚本生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        platform: str = "android",
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        class_name: Optional[str] = None,
        feature: str = "Mobile测试",
        story: str = "APP自动化"
    ) -> Dict[str, Any]:
        """生成 Mobile Pytest 脚本"""
        
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_class_name(name)
        method_name = f"test_{safe_name}"
        
        script = self._build_mobile_script(
            class_name=class_name,
            method_name=method_name,
            description=description,
            platform=platform,
            app_package=app_package,
            app_activity=app_activity,
            bundle_id=bundle_id,
            actions=actions or [],
            feature=feature,
            story=story
        )
        
        save_file = self._get_pytest_save_path(save_path, safe_name, "mobile-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "Mobile Pytest 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "mobile",
            "format": "pytest"
        }
    
    def _build_mobile_script(
        self,
        class_name: str,
        method_name: str,
        description: str,
        platform: str,
        app_package: Optional[str],
        app_activity: Optional[str],
        bundle_id: Optional[str],
        actions: List[Dict[str, Any]],
        feature: str,
        story: str
    ) -> str:
        """构建 Mobile Pytest 脚本内容"""
        
        lines = [
            '"""',
            f'{description}',
            '"""',
            'import allure',
            'import pytest',
            'from appium.webdriver.common.appiumby import AppiumBy',
            'from selenium.webdriver.support.ui import WebDriverWait',
            'from selenium.webdriver.support import expected_conditions as EC',
            '',
            '',
            f'@allure.feature("{feature}")',
            f'@allure.story("{story}")',
            f'class {class_name}:',
            f'    """{description}"""',
            '',
            f'    @allure.title("{description}")',
            '    @allure.severity(allure.severity_level.NORMAL)',
            f'    def {method_name}(self, driver):',
            '        """',
            f'        测试用例：{description}',
            f'        平台：{platform}',
        ]
        
        if platform == "android" and app_package:
            lines.append(f'        包名：{app_package}')
        if platform == "ios" and bundle_id:
            lines.append(f'        Bundle ID：{bundle_id}')
        
        lines.extend([
            '        """',
            '        wait = WebDriverWait(driver, 10)',
            '',
        ])
        
        # 执行操作
        for i, action in enumerate(actions):
            action_type = action.get('type', '')
            locator = action.get('locator', '')
            locator_type = action.get('locator_type', 'id')
            
            lines.append(f'        with allure.step("步骤{i+1}: {action_type}"):')
            
            by_map = {
                'id': 'AppiumBy.ID',
                'xpath': 'AppiumBy.XPATH',
                'accessibility_id': 'AppiumBy.ACCESSIBILITY_ID',
                'class_name': 'AppiumBy.CLASS_NAME'
            }
            by_type = by_map.get(locator_type, 'AppiumBy.ID')
            
            if action_type == 'click':
                lines.append(f'            element = wait.until(EC.element_to_be_clickable(({by_type}, "{locator}")))')
                lines.append('            element.click()')
            elif action_type == 'input':
                text = action.get('text', '')
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append(f'            element.send_keys("{text}")')
            elif action_type == 'clear':
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append('            element.clear()')
            elif action_type == 'swipe':
                direction = action.get('direction', 'up')
                lines.append('            size = driver.get_window_size()')
                lines.append('            start_x = size["width"] // 2')
                if direction == 'up':
                    lines.append('            start_y = int(size["height"] * 0.8)')
                    lines.append('            end_y = int(size["height"] * 0.2)')
                    lines.append('            driver.swipe(start_x, start_y, start_x, end_y, 500)')
                elif direction == 'down':
                    lines.append('            start_y = int(size["height"] * 0.2)')
                    lines.append('            end_y = int(size["height"] * 0.8)')
                    lines.append('            driver.swipe(start_x, start_y, start_x, end_y, 500)')
            elif action_type == 'wait':
                seconds = action.get('seconds', 1)
                lines.append('            import time')
                lines.append(f'            time.sleep({seconds})')
            elif action_type == 'screenshot':
                filename = action.get('filename', f'screenshot_{i+1}')
                lines.append('            screenshot = driver.get_screenshot_as_png()')
                lines.append(f'            allure.attach(screenshot, "{filename}", allure.attachment_type.PNG)')
            elif action_type == 'back':
                lines.append('            driver.back()')
            elif action_type == 'assert_text':
                expected = action.get('expected', '')
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append(f'            assert "{expected}" in element.text, f"文本不匹配，实际: {{element.text}}"')
            elif action_type == 'assert_element':
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append('            assert element.is_displayed(), "元素不可见"')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        if save_path:
            return Path(save_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"test_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_class_name(self, name: str) -> str:
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        return 'Test' + ''.join(word.capitalize() for word in words)


class PytestPerfGenerator(BaseGenerator):
    """Perf Pytest 脚本生成器（基于 Locust）"""
    
    def generate(
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
        class_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成 Perf Locust 脚本"""
        
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_locust_class_name(name)
        
        script = self._build_perf_script(
            class_name=class_name,
            description=description,
            host=host,
            scenarios=scenarios,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            think_time=think_time
        )
        
        save_file = self._get_pytest_save_path(save_path, safe_name, "perf-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "Perf Locust 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "perf",
            "format": "pytest",
            "run_command": f"locust -f {save_file} --host={host} -u {users} -r {spawn_rate} -t {run_time}"
        }
    
    def _build_perf_script(
        self,
        class_name: str,
        description: str,
        host: str,
        scenarios: List[Dict[str, Any]],
        users: int,
        spawn_rate: float,
        run_time: str,
        think_time: Optional[Dict[str, Any]]
    ) -> str:
        """构建 Locust 性能测试脚本"""
        
        lines = [
            '"""',
            f'{description}',
            '',
            f'运行命令: locust -f <this_file> --host={host} -u {users} -r {spawn_rate} -t {run_time}',
            '"""',
            'from locust import HttpUser, task, between',
            '',
            '',
            f'class {class_name}(HttpUser):',
            f'    """',
            f'    {description}',
            f'    ',
            f'    目标主机: {host}',
            f'    并发用户: {users}',
            f'    生成速率: {spawn_rate}/s',
            f'    运行时长: {run_time}',
            f'    """',
            '',
        ]
        
        if think_time:
            min_wait = think_time.get('min', think_time.get('seconds', 1))
            max_wait = think_time.get('max', min_wait)
            lines.append(f'    wait_time = between({min_wait}, {max_wait})')
        else:
            lines.append('    wait_time = between(1, 3)')
        
        lines.append('')
        
        for i, scenario in enumerate(scenarios):
            method = scenario.get('method', 'get').lower()
            url = scenario.get('url', '/')
            task_name = scenario.get('name', f'request_{i+1}')
            safe_task_name = self._to_snake_case(task_name)
            
            params = scenario.get('params')
            json_body = scenario.get('json') or scenario.get('json_body')
            headers = scenario.get('headers')
            check_status = scenario.get('check_status')
            
            lines.append('    @task')
            lines.append(f'    def {safe_task_name}(self):')
            lines.append(f'        """{task_name}"""')
            
            request_args = [f'"{url}"']
            request_args.append(f'name="{task_name}"')
            
            if headers:
                lines.append(f'        headers = {repr(headers)}')
                request_args.append('headers=headers')
            
            if params:
                lines.append(f'        params = {repr(params)}')
                request_args.append('params=params')
            
            if json_body:
                lines.append(f'        json_data = {repr(json_body)}')
                request_args.append('json=json_data')
            
            args_str = ', '.join(request_args)
            lines.append(f'        with self.client.{method}({args_str}, catch_response=True) as response:')
            
            if check_status:
                expected = check_status.get('expected', 200)
                lines.append(f'            if response.status_code != {expected}:')
                lines.append(f'                response.failure(f"状态码错误: {{response.status_code}}")')
            else:
                lines.append('            if response.status_code != 200:')
                lines.append('                response.failure(f"请求失败: {response.status_code}")')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        if save_path:
            return Path(save_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"locustfile_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_locust_class_name(self, name: str) -> str:
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        return ''.join(word.capitalize() for word in words) + 'User'






class PytestWebGenerator(BaseGenerator):
    """Web Pytest 脚本生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        url: str,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        class_name: Optional[str] = None,
        feature: str = "Web测试",
        story: str = "UI自动化"
    ) -> Dict[str, Any]:
        """生成 Web Pytest 脚本"""
        
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_class_name(name)
        method_name = f"test_{safe_name}"
        
        script = self._build_web_script(
            class_name=class_name,
            method_name=method_name,
            description=description,
            url=url,
            actions=actions or [],
            feature=feature,
            story=story
        )
        
        save_file = self._get_pytest_save_path(save_path, safe_name, "web-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "Web Pytest 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "web",
            "format": "pytest"
        }
    
    def _build_web_script(
        self,
        class_name: str,
        method_name: str,
        description: str,
        url: str,
        actions: List[Dict[str, Any]],
        feature: str,
        story: str
    ) -> str:
        """构建 Web Pytest 脚本内容"""
        
        lines = [
            '"""',
            f'{description}',
            '"""',
            'import allure',
            'import pytest',
            'from playwright.sync_api import Page, expect',
            '',
            '',
            f'@allure.feature("{feature}")',
            f'@allure.story("{story}")',
            f'class {class_name}:',
            f'    """{description}"""',
            '',
            f'    @allure.title("{description}")',
            '    @allure.severity(allure.severity_level.NORMAL)',
            f'    def {method_name}(self, page: Page, base_url: str):',
            '        """',
            f'        测试用例：{description}',
            '        """',
        ]
        
        # 打开页面
        lines.append('        with allure.step("打开页面"):')
        lines.append(f'            page.goto("{url}")')
        lines.append('            allure.attach(page.url, "当前URL", allure.attachment_type.TEXT)')
        
        # 执行操作
        for i, action in enumerate(actions):
            action_type = action.get('type', '')
            locator = action.get('locator', '')
            locator_type = action.get('locator_type', 'css')
            
            lines.append('')
            lines.append(f'        with allure.step("步骤{i+1}: {action_type}"):')
            
            # 构建定位器
            if locator:
                if locator_type == 'xpath':
                    locator_code = f'page.locator("xpath={locator}")'
                elif locator_type == 'id':
                    locator_code = f'page.locator("#{locator}")'
                else:
                    locator_code = f'page.locator("{locator}")'
            
            if action_type == 'click':
                lines.append(f'            {locator_code}.click()')
            
            elif action_type == 'input':
                text = action.get('text', '')
                lines.append(f'            {locator_code}.fill("{text}")')
            
            elif action_type == 'clear':
                lines.append(f'            {locator_code}.fill("")')
            
            elif action_type == 'wait':
                seconds = action.get('seconds', 1)
                lines.append(f'            page.wait_for_timeout({seconds * 1000})')
            
            elif action_type == 'screenshot':
                filename = action.get('filename', f'screenshot_{i+1}')
                lines.append(f'            screenshot = page.screenshot()')
                lines.append(f'            allure.attach(screenshot, "{filename}", allure.attachment_type.PNG)')
            
            elif action_type == 'assert_text':
                expected = action.get('expected', '')
                lines.append(f'            expect({locator_code}).to_contain_text("{expected}")')
            
            elif action_type == 'assert_title':
                expected = action.get('expected', '')
                lines.append(f'            assert "{expected}" in page.title(), "页面标题不匹配"')
            
            elif action_type == 'assert_url':
                expected = action.get('expected', '')
                match = action.get('match', 'contains')
                if match == 'equals':
                    lines.append(f'            assert page.url == "{expected}", "URL不匹配"')
                else:
                    lines.append(f'            assert "{expected}" in page.url, "URL不包含预期内容"')
            
            elif action_type == 'assert_element':
                visible = action.get('visible', True)
                if visible:
                    lines.append(f'            expect({locator_code}).to_be_visible()')
                else:
                    lines.append(f'            expect({locator_code}).not_to_be_visible()')
            
            elif action_type == 'hover':
                lines.append(f'            {locator_code}.hover()')
            
            elif action_type == 'select':
                value = action.get('value', '')
                lines.append(f'            {locator_code}.select_option("{value}")')
            
            elif action_type == 'scroll':
                direction = action.get('direction', 'down')
                distance = action.get('distance', 500)
                if direction == 'down':
                    lines.append(f'            page.mouse.wheel(0, {distance})')
                else:
                    lines.append(f'            page.mouse.wheel(0, -{distance})')
        
        lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        """获取 Pytest 脚本保存路径"""
        if save_path:
            return Path(save_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"test_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        """转换为 snake_case"""
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_class_name(self, name: str) -> str:
        """转换为类名"""
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        
        return 'Test' + ''.join(word.capitalize() for word in words)


class PytestMobileGenerator(BaseGenerator):
    """Mobile Pytest 脚本生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        platform: str = "android",
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None,
        class_name: Optional[str] = None,
        feature: str = "Mobile测试",
        story: str = "APP自动化"
    ) -> Dict[str, Any]:
        """生成 Mobile Pytest 脚本"""
        
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_class_name(name)
        method_name = f"test_{safe_name}"
        
        script = self._build_mobile_script(
            class_name=class_name,
            method_name=method_name,
            description=description,
            platform=platform,
            app_package=app_package,
            app_activity=app_activity,
            bundle_id=bundle_id,
            actions=actions or [],
            feature=feature,
            story=story
        )
        
        save_file = self._get_pytest_save_path(save_path, safe_name, "mobile-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "Mobile Pytest 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "mobile",
            "format": "pytest"
        }
    
    def _build_mobile_script(
        self,
        class_name: str,
        method_name: str,
        description: str,
        platform: str,
        app_package: Optional[str],
        app_activity: Optional[str],
        bundle_id: Optional[str],
        actions: List[Dict[str, Any]],
        feature: str,
        story: str
    ) -> str:
        """构建 Mobile Pytest 脚本内容"""
        
        lines = [
            '"""',
            f'{description}',
            '"""',
            'import allure',
            'import pytest',
            'from appium.webdriver.common.appiumby import AppiumBy',
            'from selenium.webdriver.support.ui import WebDriverWait',
            'from selenium.webdriver.support import expected_conditions as EC',
            '',
            '',
            f'@allure.feature("{feature}")',
            f'@allure.story("{story}")',
            f'class {class_name}:',
            f'    """{description}"""',
            '',
            f'    @allure.title("{description}")',
            '    @allure.severity(allure.severity_level.NORMAL)',
            f'    def {method_name}(self, driver):',
            '        """',
            f'        测试用例：{description}',
            f'        平台：{platform}',
        ]
        
        if platform == "android" and app_package:
            lines.append(f'        包名：{app_package}')
        if platform == "ios" and bundle_id:
            lines.append(f'        Bundle ID：{bundle_id}')
        
        lines.extend([
            '        """',
            '        wait = WebDriverWait(driver, 10)',
            '',
        ])
        
        # 执行操作
        for i, action in enumerate(actions):
            action_type = action.get('type', '')
            locator = action.get('locator', '')
            locator_type = action.get('locator_type', 'id')
            
            lines.append(f'        with allure.step("步骤{i+1}: {action_type}"):')
            
            by_map = {
                'id': 'AppiumBy.ID',
                'xpath': 'AppiumBy.XPATH',
                'accessibility_id': 'AppiumBy.ACCESSIBILITY_ID',
                'class_name': 'AppiumBy.CLASS_NAME'
            }
            by_type = by_map.get(locator_type, 'AppiumBy.ID')
            
            if action_type == 'click':
                lines.append(f'            element = wait.until(EC.element_to_be_clickable(({by_type}, "{locator}")))')
                lines.append('            element.click()')
            elif action_type == 'input':
                text = action.get('text', '')
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append(f'            element.send_keys("{text}")')
            elif action_type == 'clear':
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append('            element.clear()')
            elif action_type == 'swipe':
                direction = action.get('direction', 'up')
                lines.append('            size = driver.get_window_size()')
                lines.append('            start_x = size["width"] // 2')
                if direction == 'up':
                    lines.append('            start_y = int(size["height"] * 0.8)')
                    lines.append('            end_y = int(size["height"] * 0.2)')
                    lines.append('            driver.swipe(start_x, start_y, start_x, end_y, 500)')
                elif direction == 'down':
                    lines.append('            start_y = int(size["height"] * 0.2)')
                    lines.append('            end_y = int(size["height"] * 0.8)')
                    lines.append('            driver.swipe(start_x, start_y, start_x, end_y, 500)')
            elif action_type == 'wait':
                seconds = action.get('seconds', 1)
                lines.append('            import time')
                lines.append(f'            time.sleep({seconds})')
            elif action_type == 'screenshot':
                filename = action.get('filename', f'screenshot_{i+1}')
                lines.append('            screenshot = driver.get_screenshot_as_png()')
                lines.append(f'            allure.attach(screenshot, "{filename}", allure.attachment_type.PNG)')
            elif action_type == 'back':
                lines.append('            driver.back()')
            elif action_type == 'assert_text':
                expected = action.get('expected', '')
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append(f'            assert "{expected}" in element.text, f"文本不匹配，实际: {{element.text}}"')
            elif action_type == 'assert_element':
                lines.append(f'            element = wait.until(EC.presence_of_element_located(({by_type}, "{locator}")))')
                lines.append('            assert element.is_displayed(), "元素不可见"')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        if save_path:
            return Path(save_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"test_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_class_name(self, name: str) -> str:
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        return 'Test' + ''.join(word.capitalize() for word in words)


class PytestPerfGenerator(BaseGenerator):
    """Perf Pytest 脚本生成器（基于 Locust）"""
    
    def generate(
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
        class_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成 Perf Locust 脚本"""
        
        safe_name = self._to_snake_case(name)
        class_name = class_name or self._to_locust_class_name(name)
        
        script = self._build_perf_script(
            class_name=class_name,
            description=description,
            host=host,
            scenarios=scenarios,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            think_time=think_time
        )
        
        save_file = self._get_pytest_save_path(save_path, safe_name, "perf-cases_pytest")
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return {
            "success": True,
            "message": "Perf Locust 脚本已生成",
            "save_path": str(save_file),
            "script_content": script,
            "engine_type": "perf",
            "format": "pytest",
            "run_command": f"locust -f {save_file} --host={host} -u {users} -r {spawn_rate} -t {run_time}"
        }
    
    def _build_perf_script(
        self,
        class_name: str,
        description: str,
        host: str,
        scenarios: List[Dict[str, Any]],
        users: int,
        spawn_rate: float,
        run_time: str,
        think_time: Optional[Dict[str, Any]]
    ) -> str:
        """构建 Locust 性能测试脚本"""
        
        lines = [
            '"""',
            f'{description}',
            '',
            f'运行命令: locust -f <this_file> --host={host} -u {users} -r {spawn_rate} -t {run_time}',
            '"""',
            'from locust import HttpUser, task, between',
            '',
            '',
            f'class {class_name}(HttpUser):',
            f'    """',
            f'    {description}',
            f'    ',
            f'    目标主机: {host}',
            f'    并发用户: {users}',
            f'    生成速率: {spawn_rate}/s',
            f'    运行时长: {run_time}',
            f'    """',
            '',
        ]
        
        if think_time:
            min_wait = think_time.get('min', think_time.get('seconds', 1))
            max_wait = think_time.get('max', min_wait)
            lines.append(f'    wait_time = between({min_wait}, {max_wait})')
        else:
            lines.append('    wait_time = between(1, 3)')
        
        lines.append('')
        
        for i, scenario in enumerate(scenarios):
            method = scenario.get('method', 'get').lower()
            url = scenario.get('url', '/')
            task_name = scenario.get('name', f'request_{i+1}')
            safe_task_name = self._to_snake_case(task_name)
            
            params = scenario.get('params')
            json_body = scenario.get('json') or scenario.get('json_body')
            headers = scenario.get('headers')
            check_status = scenario.get('check_status')
            
            lines.append('    @task')
            lines.append(f'    def {safe_task_name}(self):')
            lines.append(f'        """{task_name}"""')
            
            request_args = [f'"{url}"']
            request_args.append(f'name="{task_name}"')
            
            if headers:
                lines.append(f'        headers = {repr(headers)}')
                request_args.append('headers=headers')
            
            if params:
                lines.append(f'        params = {repr(params)}')
                request_args.append('params=params')
            
            if json_body:
                lines.append(f'        json_data = {repr(json_body)}')
                request_args.append('json=json_data')
            
            args_str = ', '.join(request_args)
            lines.append(f'        with self.client.{method}({args_str}, catch_response=True) as response:')
            
            if check_status:
                expected = check_status.get('expected', 200)
                lines.append(f'            if response.status_code != {expected}:')
                lines.append(f'                response.failure(f"状态码错误: {{response.status_code}}")')
            else:
                lines.append('            if response.status_code != 200:')
                lines.append('                response.failure(f"请求失败: {response.status_code}")')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def _get_pytest_save_path(self, save_path: Optional[str], name: str, dir_name: str) -> Path:
        if save_path:
            return Path(save_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.examples_dir / dir_name / f"locustfile_{timestamp}_{name}.py"
    
    def _to_snake_case(self, name: str) -> str:
        result = []
        for c in name:
            if c.isalnum():
                result.append(c.lower())
            elif c in ' _-':
                result.append('_')
        return ''.join(result)[:50]
    
    def _to_locust_class_name(self, name: str) -> str:
        words = []
        current = []
        for c in name:
            if c.isalnum():
                current.append(c)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        if current:
            words.append(''.join(current))
        return ''.join(word.capitalize() for word in words) + 'User'




