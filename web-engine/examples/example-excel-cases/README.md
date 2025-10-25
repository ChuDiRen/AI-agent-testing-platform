# Excel 格式测试用例示例

本目录包含 Excel 格式的 Web 自动化测试用例示例。

## Excel 用例格式说明

### 1. context.xlsx - 全局配置文件

**文件名**: `context.xlsx`

**表格列**:

| 类型 | 变量描述 | 变量值 |
|------|---------|--------|
| 变量 | BASE_URL | <https://www.baidu.com> |
| 变量 | TEST_USERNAME | testuser |
| 变量 | TEST_PASSWORD | test123456 |

**说明**:

- `类型` 列: 填写 `变量`
- `变量描述` 列: 变量名称
- `变量值` 列: 变量的值

### 2. 测试用例文件

**文件命名规则**: `数字_用例名称.xlsx`  
例如: `1_百度搜索测试.xlsx`, `2_登录功能测试.xlsx`

**表格列**:

| 编号 | 测试用例标题 | 用例等级 | 步骤描述 | 关键字 | 参数_1 | 参数_2 | 参数_3 | ... |
|-----|-------------|---------|---------|--------|--------|--------|--------|-----|

**列说明**:

- **编号**: 步骤编号（可选）
- **测试用例标题**: 测试用例的名称（必填，新用例的第一行）
- **用例等级**: P0/P1/P2 等（可选）
- **步骤描述**: 测试步骤的描述（必填）
- **关键字**: 要执行的关键字（必填）
- **参数_1, 参数_2, ...**: 关键字所需的参数（根据关键字而定）

## Excel 用例示例

### 示例 1: 百度搜索测试

**文件名**: `1_百度搜索测试.xlsx`

| 编号 | 测试用例标题 | 用例等级 | 步骤描述 | 关键字 | 参数_1 | 参数_2 | 参数_3 | 参数_4 |
|-----|-------------|---------|---------|--------|--------|--------|--------|--------|
| 1 | 百度搜索功能测试 | P0 | 打开浏览器 | open_browser | chrome | false | 10 | maximize |
| 2 |  |  | 导航到百度首页 | navigate_to | <https://www.baidu.com> |  |  |  |
| 3 |  |  | 等待搜索框出现 | wait_for_element_visible | id | kw | 15 |  |
| 4 |  |  | 输入搜索关键词 | input_text | id | kw | Selenium | true |
| 5 |  |  | 点击搜索按钮 | click_element | id | su |  |  |
| 6 |  |  | 等待搜索结果 | wait_for_element_visible | id | content_left | 15 |  |
| 7 |  |  | 断言结果包含关键词 | assert_text_contains | id | content_left | Selenium |  |
| 8 |  |  | 截图保存 | take_screenshot | search_result |  |  |  |
| 9 |  |  | 关闭浏览器 | close_browser |  |  |  |  |

**说明**:

- 第一行填写测试用例标题，后续行留空表示同一用例的不同步骤
- 参数列数量根据关键字需要的参数数量决定
- 空参数可以不填

### 示例 2: 表单填写测试

**文件名**: `2_表单填写测试.xlsx`

| 编号 | 测试用例标题 | 用例等级 | 步骤描述 | 关键字 | 参数_1 | 参数_2 | 参数_3 | 参数_4 | 参数_5 |
|-----|-------------|---------|---------|--------|--------|--------|--------|--------|--------|
| 1 | Web表单填写功能测试 | P1 | 打开浏览器 | open_browser | chrome | false | 10 | maximize |  |
| 2 |  |  | 导航到表单页面 | navigate_to | <https://www.selenium.dev/selenium/web/web-form.html> |  |  |  |  |
| 3 |  |  | 输入文本框 | input_text | id | my-text-id | Hello World | true |  |
| 4 |  |  | 输入密码 | input_text | name | my-password | test123456 | true |  |
| 5 |  |  | 选择下拉框 | select_dropdown | name | my-select | value | 2 |  |
| 6 |  |  | 点击提交按钮 | click_element | xpath | //button[@type='submit'] |  |  |  |
| 7 |  |  | 等待成功消息 | wait_for_element_visible | id | message | 15 |  |  |
| 8 |  |  | 断言成功消息可见 | assert_element_visible | id | message | 10 |  |  |
| 9 |  |  | 截图 | take_screenshot | form_submit_success |  |  |  |  |
| 10 |  |  | 关闭浏览器 | close_browser |  |  |  |  |  |

## 如何创建 Excel 用例

### 方法1: 使用 Microsoft Excel

1. 创建新的 Excel 文件
2. 按照上述格式创建表格
3. 保存为 `.xlsx` 格式
4. 文件名以数字开头，如 `1_测试用例名.xlsx`

### 方法2: 使用 WPS 表格

1. 创建新的表格文档
2. 按照上述格式填写
3. 保存为 `.xlsx` 格式

### 方法3: 使用 LibreOffice Calc

1. 创建新的电子表格
2. 按照上述格式填写
3. 另存为 Excel 2007-365 格式 (`.xlsx`)

## 运行 Excel 用例

```bash
cd web-engine

# 运行所有 Excel 用例
python -m webrun.cli --type=excel --cases=examples/example-excel-cases

# 查看测试报告
allure serve reports/allure-results
```

## 关键字参考

所有可用的关键字及其参数说明，请参考:

- `webrun/extend/keywords.yaml` - 关键字参数配置文件
- `webrun/extend/keywords.py` - 关键字实现代码
- 主 README.md - 完整的关键字文档

## 注意事项

1. **文件命名**: Excel 文件必须以数字开头，格式为 `数字_名称.xlsx`
2. **context.xlsx**: 可选的全局配置文件，用于定义公共变量
3. **参数列**: 参数列从 `参数_1` 开始，数量根据关键字需要而定
4. **用例标题**: 每个测试用例的第一行必须填写测试用例标题
5. **关键字**: 关键字必须在 `keywords.yaml` 中定义
6. **数据类型**:
   - 字符串可以直接填写
   - 数字直接填写数字
   - 列表使用 Python 格式: `['item1', 'item2']`
   - 字典使用 Python 格式: `{'key': 'value'}`
   - 布尔值使用: `true` 或 `false`

## 常见问题

### Q1: Excel 用例无法解析？

**A**: 检查文件名是否以数字开头，文件扩展名是否为 `.xlsx`

### Q2: 参数列不够用？

**A**: 可以添加更多参数列，格式为 `参数_3`, `参数_4` ... 依此类推

### Q3: 如何在 Excel 中使用变量？

**A**: 在 `context.xlsx` 中定义变量，然后在用例中使用 `${变量名}` 引用

### Q4: 关键字找不到？

**A**: 确保关键字名称与 `keywords.yaml` 中定义的完全一致（区分大小写）
