# 性能优化技能

## 触发条件
- 关键词：性能、优化、缓存、慢查询、响应时间、并发、内存
- 场景：当用户需要优化系统性能时

## 核心规范

### 规范1：后端性能优化

#### 数据库查询优化
```python
# ❌ 错误：N+1 查询
for item in items:
    detail = session.get(Detail, item.detail_id)  # 每次循环都查询

# ✅ 正确：批量查询
detail_ids = [item.detail_id for item in items]
details = session.exec(select(Detail).where(Detail.id.in_(detail_ids))).all()
detail_map = {d.id: d for d in details}
for item in items:
    detail = detail_map.get(item.detail_id)
```

#### 分页优化
```python
# ❌ 错误：先查全部再切片
all_data = session.exec(select(Model)).all()
total = len(all_data)
data = all_data[offset:offset+limit]

# ✅ 正确：数据库分页
from sqlmodel import func

# 分开查询总数和数据
count_stmt = select(func.count(Model.id))
total = session.exec(count_stmt).one()

data_stmt = select(Model).offset(offset).limit(limit)
data = session.exec(data_stmt).all()
```

#### 索引优化
```python
# 为常用查询字段添加索引
class ApiInfo(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True)  # 添加索引
    project_id: int = Field(index=True)  # 外键索引
    status: int = Field(index=True)
    create_time: datetime = Field(index=True)
```

### 规范2：前端性能优化

#### 组件懒加载
```javascript
// router/index.js
const routes = [
  {
    path: '/apitest',
    component: () => import('@/views/apitest/ApiInfoList.vue')  // 懒加载
  }
]
```

#### 列表虚拟滚动
```vue
<!-- 大数据量列表使用虚拟滚动 -->
<template>
  <el-table-v2
    :columns="columns"
    :data="tableData"
    :width="700"
    :height="400"
    fixed
  />
</template>
```

#### 防抖节流
```javascript
import { debounce, throttle } from 'lodash'

// 搜索防抖
const handleSearch = debounce(() => {
  loadData()
}, 300)

// 滚动节流
const handleScroll = throttle(() => {
  // 处理滚动
}, 100)
```

#### 图片懒加载
```vue
<template>
  <el-image
    :src="imageUrl"
    lazy
    :preview-src-list="[imageUrl]"
  />
</template>
```

### 规范3：接口性能优化

#### 响应数据精简
```python
# ❌ 返回所有字段
return respModel.ok_resp(obj=data.model_dump())

# ✅ 只返回需要的字段
return respModel.ok_resp(obj={
    "id": data.id,
    "name": data.name,
    "status": data.status
})
```

#### 异步处理
```python
import asyncio

# 并发请求多个服务
async def get_dashboard_data():
    results = await asyncio.gather(
        get_user_count(),
        get_api_count(),
        get_task_count()
    )
    return {
        "user_count": results[0],
        "api_count": results[1],
        "task_count": results[2]
    }
```

### 规范4：缓存策略

```python
# 简单内存缓存
from functools import lru_cache
from datetime import datetime, timedelta

# 使用 lru_cache
@lru_cache(maxsize=100)
def get_config(key: str):
    return session.exec(select(Config).where(Config.key == key)).first()

# 带过期时间的缓存
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._expires = {}
    
    def get(self, key: str):
        if key in self._cache:
            if datetime.now() < self._expires[key]:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._expires[key]
        return None
    
    def set(self, key: str, value, ttl: int = 300):
        self._cache[key] = value
        self._expires[key] = datetime.now() + timedelta(seconds=ttl)
```

### 规范5：日志与监控

```python
import time
from core.logger import get_logger

logger = get_logger(__name__)

# 接口耗时日志
@router.post("/queryByPage")
async def query_by_page(query: QueryParams):
    start_time = time.time()
    try:
        result = service.query_by_page(...)
        return respModel.ok_resp_list(lst=result, total=total)
    finally:
        elapsed = time.time() - start_time
        if elapsed > 1.0:  # 超过1秒记录警告
            logger.warning(f"慢查询: queryByPage 耗时 {elapsed:.2f}s")
```

### 规范6：性能检查清单

| 检查项 | 说明 |
|--------|------|
| 数据库索引 | 查询字段是否有索引 |
| N+1 查询 | 是否有循环查询 |
| 分页查询 | 大数据量是否分页 |
| 组件懒加载 | 路由是否懒加载 |
| 防抖节流 | 频繁操作是否防抖 |
| 接口响应 | 是否返回必要字段 |

## 禁止事项
- ❌ 不加索引的大表查询
- ❌ 循环中查询数据库
- ❌ 返回过多无用字段
- ❌ 不做分页的列表查询

## 检查清单
- [ ] 慢查询是否优化
- [ ] 是否有 N+1 问题
- [ ] 前端是否懒加载
- [ ] 是否有缓存策略
