# Bug 排查技能

## 触发条件
- 关键词：Bug、问题、排查、调试、debug、错误、异常、故障
- 场景：当用户遇到 Bug 需要排查时

## 核心规范

### 规范1：问题定位流程

```
1. 复现问题 → 2. 查看日志 → 3. 定位代码 → 4. 分析原因 → 5. 修复验证
```

### 规范2：后端日志查看

```bash
# 查看后端日志
cd platform-fastapi-server

# 实时查看日志
tail -f logs/app.log

# 搜索错误日志
grep -i "error" logs/app.log
grep -i "exception" logs/app.log

# 按时间范围查看
grep "2024-01-15" logs/app.log
```

```python
# 代码中添加调试日志
from core.logger import get_logger

logger = get_logger(__name__)

def some_function(data):
    logger.debug(f"输入参数: {data}")
    try:
        result = process(data)
        logger.debug(f"处理结果: {result}")
        return result
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise
```

### 规范3：前端调试

```javascript
// 浏览器控制台调试
console.log('变量值:', variable)
console.table(arrayData)  // 表格形式显示数组
console.trace()  // 打印调用栈

// Vue 组件调试
<script setup>
import { watch, onMounted } from 'vue'

// 监听数据变化
watch(() => props.data, (newVal, oldVal) => {
  console.log('数据变化:', { newVal, oldVal })
}, { deep: true })

// 生命周期调试
onMounted(() => {
  console.log('组件挂载完成')
})
</script>

// 网络请求调试
axios.interceptors.response.use(
  response => {
    console.log('响应:', response.config.url, response.data)
    return response
  },
  error => {
    console.error('请求失败:', error.config?.url, error.response?.data)
    return Promise.reject(error)
  }
)
```

### 规范4：常见问题排查

#### 接口 404
```
检查清单：
1. 后端路由是否注册 (app.py)
2. 前端请求路径是否正确
3. 代理配置是否正确 (vite.config.js)
4. 接口前缀是否匹配 (/api/)
```

#### 接口 500
```
检查清单：
1. 查看后端错误日志
2. 检查数据库连接
3. 检查参数类型是否正确
4. 检查依赖注入是否正确
```

#### 数据不显示
```
检查清单：
1. 接口是否返回数据 (Network 面板)
2. 响应格式是否正确 (code, data, msg)
3. 前端数据绑定是否正确
4. 是否有 v-if 条件阻止渲染
```

#### 权限问题
```
检查清单：
1. Token 是否有效
2. 用户是否有对应权限
3. 权限标识是否匹配
4. 前端是否正确传递 Token
```

### 规范5：数据库问题排查

```python
# 打印 SQL 语句
# config/dev_settings.py
DATABASE_URL = "mysql+pymysql://..."
ECHO_SQL = True  # 开启 SQL 打印

# 或在代码中
from sqlmodel import create_engine
engine = create_engine(DATABASE_URL, echo=True)

# 检查数据库连接
from core.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("数据库连接正常")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

### 规范6：调试工具

| 工具 | 用途 |
|------|------|
| Chrome DevTools | 前端调试、网络请求 |
| Vue DevTools | Vue 组件状态调试 |
| Postman/Apifox | API 接口测试 |
| DBeaver | 数据库查询 |
| VS Code Debugger | Python 断点调试 |

### 规范7：断点调试（Python）

```python
# 方式1：使用 breakpoint()
def some_function():
    breakpoint()  # Python 3.7+
    # 代码执行到这里会暂停

# 方式2：使用 pdb
import pdb
def some_function():
    pdb.set_trace()
    # 代码执行到这里会暂停

# pdb 常用命令
# n - 下一行
# s - 进入函数
# c - 继续执行
# p variable - 打印变量
# l - 显示当前代码
# q - 退出调试
```

### 规范8：问题报告模板

```markdown
## 问题描述
简要描述遇到的问题

## 复现步骤
1. 步骤一
2. 步骤二
3. 步骤三

## 期望结果
描述期望的正确行为

## 实际结果
描述实际发生的错误行为

## 错误信息
```
粘贴错误日志或截图
```

## 环境信息
- 浏览器：Chrome 120
- 后端版本：xxx
- 前端版本：xxx
```

## 禁止事项
- ❌ 不看日志就猜测问题
- ❌ 修改代码不测试就提交
- ❌ 在生产环境调试
- ❌ 删除有用的日志代码

## 检查清单
- [ ] 是否查看了完整的错误日志
- [ ] 是否能稳定复现问题
- [ ] 是否定位到具体代码行
- [ ] 修复后是否充分测试
