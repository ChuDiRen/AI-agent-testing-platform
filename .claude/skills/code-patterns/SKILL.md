# 代码规范技能

## 触发条件
- 关键词：设计模式、代码规范、重构、命名、最佳实践
- 场景：当用户需要遵循代码规范或重构代码时

## 核心规范

### 规范1：命名规范

#### Python 命名
```python
# 模块名：小写下划线
api_info_service.py
user_controller.py

# 类名：大驼峰
class ApiInfoService:
class UserController:

# 函数/方法名：小写下划线
def get_by_id(self, id: int):
def query_by_page(self, page: int):

# 变量名：小写下划线
user_info = get_user()
page_size = 20

# 常量：大写下划线
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30
```

#### JavaScript/Vue 命名
```javascript
// 文件名：大驼峰（组件）或小驼峰（工具）
ApiInfoList.vue
apiInfo.js

// 组件名：大驼峰
export default {
  name: 'ApiInfoList'
}

// 变量/函数：小驼峰
const userInfo = ref(null)
const handleSubmit = () => {}

// 常量：大写下划线
const MAX_FILE_SIZE = 10 * 1024 * 1024
```

### 规范2：项目分层规范

#### 后端三层架构
```
Controller (api/)
├── 接收请求参数
├── 参数校验
├── 调用 Service
└── 返回统一响应

Service (service/)
├── 业务逻辑处理
├── 数据库操作
├── 事务管理
└── 异常处理

Model (model/)
├── 数据模型定义
├── 字段约束
└── 表关系
```

#### 前端分层
```
views/          # 页面组件（业务逻辑）
components/     # 公共组件（可复用）
composables/    # 组合式函数（逻辑复用）
utils/          # 工具函数（纯函数）
store/          # 状态管理（全局状态）
```

### 规范3：函数设计原则

```python
# ✅ 单一职责：一个函数只做一件事
def validate_user(user_data: dict) -> bool:
    """只负责验证用户数据"""
    pass

def create_user(user_data: dict) -> User:
    """只负责创建用户"""
    pass

# ❌ 违反单一职责
def validate_and_create_user(user_data: dict):
    """同时做验证和创建"""
    pass

# ✅ 参数不超过 3 个，多了用对象
def query_by_page(query: QueryParams) -> tuple:
    pass

# ❌ 参数过多
def query_by_page(page, page_size, name, status, start_time, end_time):
    pass
```

### 规范4：注释规范

```python
# 模块注释
"""
用户服务模块

提供用户相关的业务逻辑处理，包括：
- 用户查询
- 用户创建
- 用户更新
- 用户删除
"""

# 类注释
class UserService:
    """
    用户服务类
    
    Attributes:
        session: 数据库会话
    """

# 函数注释
def create_user(self, **kwargs) -> User:
    """
    创建用户
    
    Args:
        **kwargs: 用户属性，包括 name, email, phone 等
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValidationException: 参数验证失败
        DuplicateResourceException: 用户已存在
    """
```

### 规范5：错误处理规范

```python
# ✅ 正确：具体异常类型
try:
    user = service.get_by_id(id)
except ResourceNotFoundException as e:
    return respModel.error_resp("用户不存在")
except DatabaseException as e:
    logger.error(f"数据库错误: {e}", exc_info=True)
    return respModel.error_resp("系统错误")

# ❌ 错误：捕获所有异常
try:
    user = service.get_by_id(id)
except Exception as e:
    return respModel.error_resp(str(e))
```

### 规范6：代码复用

```python
# ✅ 抽取公共方法
class BaseService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, model_class, id: int):
        return self.session.get(model_class, id)
    
    def query_by_page(self, model_class, page: int, page_size: int, **filters):
        # 通用分页查询逻辑
        pass

class UserService(BaseService):
    def get_user(self, id: int):
        return self.get_by_id(User, id)
```

```vue
<!-- ✅ 抽取公共组件 -->
<template>
  <BaseTable
    :data="tableData"
    :columns="columns"
    :loading="loading"
    @edit="handleEdit"
    @delete="handleDelete"
  />
</template>
```

### 规范7：代码格式化

```bash
# Python 格式化
pip install black isort
black .
isort .

# JavaScript 格式化
npm install prettier eslint
npx prettier --write .
npx eslint --fix .
```

## 代码审查清单

| 检查项 | 说明 |
|--------|------|
| 命名 | 是否清晰表达意图 |
| 单一职责 | 函数是否只做一件事 |
| 参数数量 | 是否不超过 3 个 |
| 异常处理 | 是否捕获具体异常 |
| 注释 | 复杂逻辑是否有注释 |
| 重复代码 | 是否有可抽取的公共逻辑 |

## 禁止事项
- ❌ 魔法数字（用常量代替）
- ❌ 过长函数（超过 50 行考虑拆分）
- ❌ 深层嵌套（超过 3 层考虑重构）
- ❌ 注释掉的代码（直接删除）
