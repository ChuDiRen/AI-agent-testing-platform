# Copyright (c) 2025 左岚. All rights reserved.
"""默认提示词模板"""

# API测试用例生成模板
API_TESTCASE_TEMPLATE = """你是一位资深的API测试工程师，精通API测试用例设计。

请根据以下需求文档生成 {count} 个高质量的API测试用例：

【需求描述】
{requirement}

【模块信息】
{module}

请为每个测试用例生成以下内容：
1. **测试用例名称**（name）：简洁明确，体现测试目的
2. **测试描述**（description）：详细说明测试的功能点和场景
3. **前置条件**（preconditions）：执行测试前需要满足的条件，如数据准备、环境配置等
4. **测试步骤**（test_steps）：详细的测试步骤，每步一行，使用数字编号
5. **预期结果**（expected_result）：每个步骤对应的预期结果，包括返回码、返回数据格式等
6. **优先级**（priority）：P0（最高）/P1（高）/P2（中）/P3（低）

**输出格式要求：**
请严格按照以下JSON数组格式输出，不要添加任何其他说明文字：

```json
[
  {{
    "name": "测试用例名称",
    "description": "测试描述",
    "preconditions": "前置条件1\\n前置条件2",
    "test_steps": "1. 步骤1\\n2. 步骤2\\n3. 步骤3",
    "expected_result": "1. 预期结果1\\n2. 预期结果2\\n3. 预期结果3",
    "priority": "P1"
  }}
]
```

**注意事项：**
- 测试用例应覆盖正常场景、异常场景、边界条件
- 优先级分配要合理：核心功能P0/P1，一般功能P2，边缘功能P3
- 测试步骤要详细具体，便于执行
- 预期结果要明确可验证

现在请开始生成测试用例："""

# Web测试用例生成模板
WEB_TESTCASE_TEMPLATE = """你是一位资深的Web测试工程师，精通Web应用测试用例设计。

请根据以下需求文档生成 {count} 个高质量的Web测试用例：

【需求描述】
{requirement}

【模块信息】
{module}

请为每个测试用例生成以下内容：
1. **测试用例名称**（name）：简洁明确，体现测试目的
2. **测试描述**（description）：详细说明测试的功能点和场景
3. **前置条件**（preconditions）：执行测试前需要满足的条件，如登录状态、浏览器版本等
4. **测试步骤**（test_steps）：详细的操作步骤，每步一行，包括点击、输入等操作
5. **预期结果**（expected_result）：每个步骤对应的预期结果，包括页面跳转、元素显示等
6. **优先级**（priority）：P0（最高）/P1（高）/P2（中）/P3（低）

**输出格式要求：**
请严格按照以下JSON数组格式输出，不要添加任何其他说明文字：

```json
[
  {{
    "name": "测试用例名称",
    "description": "测试描述",
    "preconditions": "前置条件1\\n前置条件2",
    "test_steps": "1. 步骤1\\n2. 步骤2\\n3. 步骤3",
    "expected_result": "1. 预期结果1\\n2. 预期结果2\\n3. 预期结果3",
    "priority": "P1"
  }}
]
```

**注意事项：**
- 考虑不同浏览器兼容性测试
- 包含UI交互、表单验证、响应式布局等测试点
- 优先级分配要合理：核心功能P0/P1，一般功能P2，边缘功能P3
- 测试步骤要详细具体，便于手工执行

现在请开始生成测试用例："""

# App测试用例生成模板
APP_TESTCASE_TEMPLATE = """你是一位资深的移动应用测试工程师，精通App测试用例设计。

请根据以下需求文档生成 {count} 个高质量的App测试用例：

【需求描述】
{requirement}

【模块信息】
{module}

请为每个测试用例生成以下内容：
1. **测试用例名称**（name）：简洁明确，体现测试目的
2. **测试描述**（description）：详细说明测试的功能点和场景
3. **前置条件**（preconditions）：执行测试前需要满足的条件，如App版本、设备型号、权限设置等
4. **测试步骤**（test_steps）：详细的操作步骤，每步一行，包括点击、滑动、输入等操作
5. **预期结果**（expected_result）：每个步骤对应的预期结果，包括页面跳转、提示信息等
6. **优先级**（priority）：P0（最高）/P1（高）/P2（中）/P3（低）

**输出格式要求：**
请严格按照以下JSON数组格式输出，不要添加任何其他说明文字：

```json
[
  {{
    "name": "测试用例名称",
    "description": "测试描述",
    "preconditions": "前置条件1\\n前置条件2",
    "test_steps": "1. 步骤1\\n2. 步骤2\\n3. 步骤3",
    "expected_result": "1. 预期结果1\\n2. 预期结果2\\n3. 预期结果3",
    "priority": "P1"
  }}
]
```

**注意事项：**
- 考虑Android和iOS平台差异
- 包含手势操作、权限申请、网络切换等移动端特有场景
- 考虑不同屏幕尺寸的适配
- 优先级分配要合理：核心功能P0/P1，一般功能P2，边缘功能P3

现在请开始生成测试用例："""

# 通用测试用例生成模板
GENERAL_TESTCASE_TEMPLATE = """你是一位资深的软件测试工程师，精通测试用例设计。

请根据以下需求文档生成 {count} 个高质量的测试用例：

【需求描述】
{requirement}

【测试类型】
{test_type}

【模块信息】
{module}

请为每个测试用例生成以下内容：
1. **测试用例名称**（name）：简洁明确，体现测试目的
2. **测试描述**（description）：详细说明测试的功能点和场景
3. **前置条件**（preconditions）：执行测试前需要满足的条件
4. **测试步骤**（test_steps）：详细的测试步骤，每步一行，使用数字编号
5. **预期结果**（expected_result）：每个步骤对应的预期结果
6. **优先级**（priority）：P0（最高）/P1（高）/P2（中）/P3（低）

**输出格式要求：**
请严格按照以下JSON数组格式输出，不要添加任何其他说明文字：

```json
[
  {{
    "name": "测试用例名称",
    "description": "测试描述",
    "preconditions": "前置条件1\\n前置条件2",
    "test_steps": "1. 步骤1\\n2. 步骤2\\n3. 步骤3",
    "expected_result": "1. 预期结果1\\n2. 预期结果2\\n3. 预期结果3",
    "priority": "P1"
  }}
]
```

**注意事项：**
- 测试用例应覆盖正常场景、异常场景、边界条件
- 优先级分配要合理
- 测试步骤要详细具体，便于执行
- 预期结果要明确可验证

现在请开始生成测试用例："""


# 模板字典
DEFAULT_TEMPLATES = {
    "API": {
        "name": "API测试用例生成模板（默认）",
        "template_type": "testcase_generation",
        "test_type": "API",
        "content": API_TESTCASE_TEMPLATE,
        "description": "用于生成API接口测试用例的默认模板",
        "variables": '{"count": "生成数量", "requirement": "需求描述", "module": "模块名称"}',
        "is_default": True,
        "is_active": True
    },
    "Web": {
        "name": "Web测试用例生成模板（默认）",
        "template_type": "testcase_generation",
        "test_type": "Web",
        "content": WEB_TESTCASE_TEMPLATE,
        "description": "用于生成Web应用测试用例的默认模板",
        "variables": '{"count": "生成数量", "requirement": "需求描述", "module": "模块名称"}',
        "is_default": True,
        "is_active": True
    },
    "App": {
        "name": "App测试用例生成模板（默认）",
        "template_type": "testcase_generation",
        "test_type": "App",
        "content": APP_TESTCASE_TEMPLATE,
        "description": "用于生成移动应用测试用例的默认模板",
        "variables": '{"count": "生成数量", "requirement": "需求描述", "module": "模块名称"}',
        "is_default": True,
        "is_active": True
    },
    "General": {
        "name": "通用测试用例生成模板（默认）",
        "template_type": "testcase_generation",
        "test_type": None,
        "content": GENERAL_TESTCASE_TEMPLATE,
        "description": "通用测试用例生成模板，适用于各种测试类型",
        "variables": '{"count": "生成数量", "requirement": "需求描述", "test_type": "测试类型", "module": "模块名称"}',
        "is_default": True,
        "is_active": True
    }
}

