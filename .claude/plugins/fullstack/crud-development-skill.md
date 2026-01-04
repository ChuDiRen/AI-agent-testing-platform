# CRUD Development Skill

CRUD 开发技能，提供标准化的增删改查代码生成能力。

## 触发条件
- `/crud` 命令
- `/dev` 命令
- 用户请求开发 CRUD 功能

## 开发能力

参考 `@templates/code-patterns.md`：

### 后端四层架构

#### Model 层
```python
class {Module}(SQLModel, table=True):
    __tablename__ = "{module}"
    id: Optional[int] = Field(default=None, primary_key=True)
    # ... 字段定义
```

#### Schema 层
```python
class {Module}Create(BaseModel):
    # 创建请求

class {Module}Update(BaseModel):
    id: int
    # 更新请求

class {Module}Query(BaseModel):
    page: int = 1
    pageSize: int = 10
    # 查询条件
```

#### Service 层
```python
class {Module}Service:
    def query_by_page(self, page, page_size, **filters)
    def get_by_id(self, id)
    def create(self, **kwargs)
    def update(self, id, update_data)
    def delete(self, id)
```

#### Controller 层
```python
@{module}_route.post("/queryByPage")
@{module}_route.get("/queryById")
@{module}_route.post("/insert")
@{module}_route.put("/update")
@{module}_route.delete("/delete")
```

### 前端 Vue 组件

#### 列表页
- 搜索表单
- 数据表格
- 分页组件
- CRUD 操作

#### API 接口
```javascript
export const queryByPage = (data) => axios.post(...)
export const queryById = (id) => axios.get(...)
export const insert = (data) => axios.post(...)
export const update = (data) => axios.put(...)
export const deleteById = (id) => axios.delete(...)
```

## 输出要求

1. 遵循项目目录结构
2. 使用项目统一响应格式
3. 包含完整的类型注解
4. 添加必要的注释

## 与其他组件协作

- 后端开发 → 调用 `backend-architect` Agent
- 前端开发 → 调用 `frontend-developer` Agent
