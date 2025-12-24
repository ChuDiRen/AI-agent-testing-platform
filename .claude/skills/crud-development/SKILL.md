# CRUD 开发技能

## 触发条件
- 关键词：CRUD、增删改查、列表、详情、新增、编辑、删除
- 场景：当用户需要开发标准的数据管理功能时

## 核心规范

### 规范1：后端三层架构（本项目）
```
Controller (api/) → Service (service/) → Model (model/)
```

**各层职责：**
- **Controller**: 接收请求、参数校验、调用 Service、返回响应
- **Service**: 业务逻辑处理、数据库操作
- **Model**: SQLModel 数据模型定义

### 规范2：标准 CRUD 接口（本项目风格）

| 操作 | HTTP 方法 | 路径格式 | 说明 |
|------|----------|----------|------|
| 列表 | POST | /{Module}/queryByPage | 分页查询 |
| 详情 | GET | /{Module}/queryById | 获取单条记录 |
| 新增 | POST | /{Module}/insert | 创建新记录 |
| 修改 | PUT | /{Module}/update | 更新记录 |
| 删除 | DELETE | /{Module}/delete | 删除记录 |

### 规范3：Controller 模板
```python
"""
{模块名}Controller
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..model.{Module}Model import {Module}
from ..schemas.{module}_schema import {Module}Query, {Module}Create, {Module}Update
from ..service.{module}_service import {Module}Service

module_name = "{Module}"
module_route = APIRouter(prefix=f"/{module_name}", tags=["{模块描述}"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询", dependencies=[Depends(check_permission("{module}:query"))])
async def queryByPage(query: {Module}Query, session: Session = Depends(get_session)):
    try:
        service = {Module}Service(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            # 其他筛选条件
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误:{e}")

@module_route.get("/queryById", summary="根据ID查询")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = {Module}Service(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误:{e}")

@module_route.post("/insert", summary="新增", dependencies=[Depends(check_permission("{module}:add"))])
async def insert(data: {Module}Create, session: Session = Depends(get_session)):
    try:
        service = {Module}Service(session)
        result = service.create(**data.model_dump())
        return respModel.ok_resp(msg="添加成功", dic_t={"id": result.id})
    except Exception as e:
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新", dependencies=[Depends(check_permission("{module}:edit"))])
async def update(data: {Module}Update, session: Session = Depends(get_session)):
    try:
        service = {Module}Service(session)
        update_data = data.model_dump(exclude_unset=True, exclude={"id"})
        if not service.update(data.id, update_data):
            return respModel.error_resp("数据不存在")
        return respModel.ok_resp(msg="更新成功")
    except Exception as e:
        return respModel.error_resp(f"服务器错误:{e}")

@module_route.delete("/delete", summary="删除", dependencies=[Depends(check_permission("{module}:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = {Module}Service(session)
        if not service.delete(id):
            return respModel.error_resp("数据不存在")
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        return respModel.error_resp(f"服务器错误:{e}")
```

### 规范4：Service 模板
```python
"""
{模块名}Service
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from ..model.{Module}Model import {Module}

class {Module}Service:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, **filters) -> tuple[List[{Module}], int]:
        """分页查询"""
        statement = select({Module})
        
        # 条件筛选
        for key, value in filters.items():
            if value is not None:
                statement = statement.where(getattr({Module}, key) == value)
        
        statement = statement.order_by({Module}.id.desc())
        
        # 总数
        total = len(self.session.exec(statement).all())
        
        # 分页
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[{Module}]:
        return self.session.get({Module}, id)
    
    def create(self, **kwargs) -> {Module}:
        data = {Module}(**kwargs, create_time=datetime.now())
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        data = self.get_by_id(id)
        if not data:
            return False
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        data = self.get_by_id(id)
        if not data:
            return False
        self.session.delete(data)
        self.session.commit()
        return True
```

### 规范5：前端文件结构
```
src/views/{module}/
├── {Module}List.vue          # 列表页
├── {Module}Form.vue          # 表单弹窗
├── {module}.js               # API 接口定义
└── components/               # 模块私有组件（可选）
```

### 规范6：前端 API 定义
```javascript
// {module}.js
import axios from '@/axios'

export function queryByPage(data) {
  return axios.post(`/api/{Module}/queryByPage`, data)
}

export function queryById(id) {
  return axios.get(`/api/{Module}/queryById`, { params: { id } })
}

export function insert(data) {
  return axios.post(`/api/{Module}/insert`, data)
}

export function update(data) {
  return axios.put(`/api/{Module}/update`, data)
}

export function deleteById(id) {
  return axios.delete(`/api/{Module}/delete`, { params: { id } })
}
```

## 禁止事项
- ❌ Controller 中直接写数据库操作
- ❌ 不使用 respModel 统一响应
- ❌ 不添加权限校验
- ❌ 不记录错误日志
- ❌ 硬编码分页参数

## 检查清单
- [ ] 是否遵循三层架构
- [ ] 接口是否使用 respModel 响应
- [ ] 是否有权限校验 (check_permission)
- [ ] 是否有错误处理和日志
- [ ] 前端 API 是否与后端对应
