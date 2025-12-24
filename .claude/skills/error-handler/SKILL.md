# 异常处理技能

## 触发条件
- 关键词：异常、错误、Exception、try-catch、错误处理、异常处理
- 场景：当用户需要处理异常和错误时

## 核心规范

### 规范1：本项目异常类体系

```
core/exceptions.py
├── PlatformBaseException     # 平台基础异常类
│   ├── BusinessException     # 业务异常（可恢复）
│   │   ├── ValidationException        # 数据验证异常
│   │   ├── ResourceNotFoundException  # 资源不存在
│   │   ├── PermissionDeniedException  # 权限拒绝
│   │   └── DuplicateResourceException # 资源重复
│   └── TechnicalException    # 技术异常（系统级）
│       ├── DatabaseException          # 数据库异常
│       ├── ExternalServiceException   # 外部服务异常
│       ├── ConfigurationException     # 配置异常
│       └── QueueException             # 消息队列异常
```

### 规范2：Controller 层异常处理

```python
from core.resp_model import respModel
from core.logger import get_logger
from core.exceptions import BusinessException, ResourceNotFoundException

logger = get_logger(__name__)

@router.get("/queryById")
async def query_by_id(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = ModuleService(session)
        data = service.get_by_id(id)
        if not data:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        return respModel.ok_resp(obj=data)
    except BusinessException as e:
        logger.warning(f"业务异常: {e.message}")
        return respModel.error_resp(e.message)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误:{e}")
```

### 规范3：Service 层异常处理

```python
from core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)

class ModuleService:
    def get_by_id(self, id: int):
        data = self.session.get(Module, id)
        if not data:
            raise ResourceNotFoundException(f"记录不存在: {id}")
        return data
    
    def create(self, **kwargs):
        # 业务校验
        if not kwargs.get('name'):
            raise ValidationException("名称不能为空")
        
        try:
            data = Module(**kwargs)
            self.session.add(data)
            self.session.commit()
            return data
        except Exception as e:
            self.session.rollback()
            raise DatabaseException(f"数据库操作失败: {e}")
```

### 规范4：异常处理最佳实践

```python
# ✅ 正确：分层捕获异常
try:
    # 业务逻辑
    pass
except ValueError as e:
    # 处理特定的值错误
    raise ValidationException(str(e))
except SQLAlchemyError as e:
    # 处理数据库错误
    raise DatabaseException(str(e))
except Exception as e:
    # 处理未知错误
    logger.critical(f"未知异常: {e}", exc_info=True)
    raise

# ❌ 错误：一刀切
try:
    # 业务逻辑
    pass
except Exception as e:
    return {"error": str(e)}  # 可能暴露敏感信息
```

### 规范5：日志记录规范

```python
# 业务异常 - 警告级别
logger.warning(f"业务异常: {e.message}", exc_info=False)

# 技术异常 - 错误级别（包含堆栈）
logger.error(f"技术异常: {e.message}", exc_info=True)

# 未知异常 - 严重级别
logger.critical(f"未知异常: {str(e)}", exc_info=True)
```

### 规范6：前端错误处理

```javascript
// axios.js 拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data?.msg || '请求失败')
      }
    }
    return Promise.reject(error)
  }
)

// 组件中处理
try {
  const res = await api.create(data)
  if (res.data.code === 0) {
    ElMessage.success('操作成功')
  } else {
    ElMessage.error(res.data.msg)
  }
} catch (error) {
  ElMessage.error('操作失败')
}
```

## 禁止事项
- ❌ 捕获异常后不记录日志
- ❌ 直接返回 `str(e)` 给前端（可能暴露敏感信息）
- ❌ 使用空的 `except:` 语句
- ❌ 在 except 中吞掉异常不处理

## 检查清单
- [ ] 是否使用自定义异常类
- [ ] 是否记录完整堆栈 (exc_info=True)
- [ ] 是否对用户友好的错误消息
- [ ] 是否分层捕获异常
