# Web Engine - 原生 Pytest 脚本示例

本目录包含使用原生 Python pytest 编写的 Web UI 测试示例。

## 文件说明

- `conftest.py` - Pytest 配置文件，提供 fixtures（driver, web_keywords）
- `test_web_basic.py` - 基础 Web UI 测试示例
- `test_web_advanced.py` - 高级特性示例（参数化、类、fixture 等）

## 运行方式

### 1. 运行所有测试

```bash
cd web-engine/examples/example-pytest-scripts
pytest -v -s
```

### 2. 指定浏览器运行

```bash
pytest -v -s --browser=chrome
pytest -v -s --browser=firefox
pytest -v -s --browser=edge
```

### 3. 无头模式运行

```bash
pytest -v -s --headless=true
```

### 4. 运行特定测试文件

```bash
pytest test_web_basic.py -v -s
pytest test_web_advanced.py -v -s
```

### 5. 运行特定测试函数

```bash
pytest test_web_basic.py::test_baidu_search -v -s
pytest -k "test_search" -v -s
```

### 6. 运行标记的测试

```bash
pytest -m smoke -v -s           # 运行冒烟测试
pytest -m regression -v -s      # 运行回归测试
```

### 7. 生成 Allure 报告

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

### 8. 并行执行（需要安装 pytest-xdist）

```bash
pip install pytest-xdist
pytest -n auto -v --browser=chrome
```

### 9. 失败重试（需要安装 pytest-rerunfailures）

```bash
pip install pytest-rerunfailures
pytest --reruns 2 --reruns-delay 1 -v
```

## Fixtures 说明

### driver

自动管理浏览器生命周期的 fixture。每个测试函数会自动创建和销毁浏览器。

```python
def test_example(driver):
    # driver 已经自动创建
    driver.get("https://www.example.com")
    # 测试结束后浏览器会自动关闭
```

**特性:**

- 自动创建浏览器实例
- 测试结束自动关闭浏览器
- 失败时自动截图并附加到 Allure 报告
- 支持命令行参数（--browser, --headless）

### web_keywords

提供 Web 关键字实例，可以调用所有框架提供的关键字方法。

```python
def test_example(web_keywords, driver):
    web_keywords.navigate_to(url="https://www.example.com")
    web_keywords.click_element(定位方式="id", 元素="btn")
```

## 命令行参数

- `--browser`: 浏览器类型（chrome/firefox/edge），默认 chrome
- `--headless`: 无头模式（true/false），默认 true（无头模式，用户无感知）

## 特性支持

- ✅ 参数化测试 (`@pytest.mark.parametrize`)
- ✅ Fixture 机制（自动管理浏览器）
- ✅ 测试类组织
- ✅ 测试标记 (`@pytest.mark.smoke`)
- ✅ Allure 报告集成
- ✅ 失败自动截图
- ✅ 跳过测试 (`@pytest.mark.skip`)
- ✅ 预期失败 (`@pytest.mark.xfail`)
- ✅ 多浏览器支持

## 注意事项

1. 原生 pytest 脚本不使用 g_context 全局上下文
2. 变量管理使用 Python 原生方式或 fixture
3. 可以导入使用框架的 Keywords 类
4. 支持所有 pytest 原生特性
5. driver fixture 会自动管理浏览器生命周期
6. 失败时会自动截图并附加到 Allure 报告

## 最佳实践

1. **使用 Allure 步骤记录**

   ```python
   with allure.step("打开页面"):
       web_keywords.navigate_to(url="...")
   ```

2. **使用参数化提高效率**

   ```python
   @pytest.mark.parametrize("keyword", ["Python", "Java"])
   def test_search(web_keywords, driver, keyword):
       # 测试代码
   ```

3. **使用测试类组织相关测试**

   ```python
   class TestLogin:
       def test_valid_login(self, web_keywords, driver):
           pass

       def test_invalid_login(self, web_keywords, driver):
           pass
   ```

4. **使用 fixture 复用测试逻辑**
   ```python
   @pytest.fixture
   def login_user(web_keywords, driver):
       # 登录逻辑
       yield
       # 清理逻辑
   ```
