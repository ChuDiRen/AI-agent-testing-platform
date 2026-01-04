# 代码模式模板库

本文件包含项目通用的代码模式，供 Skills/Agents/Commands 引用。

## 后端四层架构

### Controller 层
```python
# {Module}Controller.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from core.database import get_session
from core.resp_model import respModel
from ..service.{module}Service import {Module}Service
from ..schemas.{Module}Schema import {Module}Create, {Module}Update, {Module}Query

{module}_route = APIRouter(prefix="/{Module}", tags=["{Module}管理"])

@{module}_route.post("/queryByPage")
async def query_by_page(query: {Module}Query, session: Session = Depends(get_session)):
    service = {Module}Service(session)
    result, total = service.query_by_page(
        page=query.page, page_size=query.pageSize,
        **query.dict(exclude={'page', 'pageSize'}, exclude_none=True)
    )
    return respModel.ok_resp_list(lst=result, total=total)

@{module}_route.get("/queryById")
async def query_by_id(id: int, session: Session = Depends(get_session)):
    service = {Module}Service(session)
    return respModel.ok_resp(obj=service.get_by_id(id))

@{module}_route.post("/insert")
async def insert(data: {Module}Create, session: Session = Depends(get_session)):
    service = {Module}Service(session)
    return respModel.ok_resp(obj=service.create(**data.dict()))

@{module}_route.put("/update")
async def update(data: {Module}Update, session: Session = Depends(get_session)):
    service = {Module}Service(session)
    return respModel.ok_resp(obj=service.update(data.id, data.dict(exclude={'id'}, exclude_none=True)))

@{module}_route.delete("/delete")
async def delete(id: int, session: Session = Depends(get_session)):
    service = {Module}Service(session)
    service.delete(id)
    return respModel.ok_resp_text(msg="删除成功")
```

### Service 层
```python
# {module}Service.py
from sqlmodel import Session, select, func
from ..model.{module} import {Module}

class {Module}Service:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int = 1, page_size: int = 10, **filters):
        statement = select({Module})
        for key, value in filters.items():
            if value is not None and hasattr({Module}, key):
                statement = statement.where(getattr({Module}, key) == value)
        count_stmt = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(count_stmt).one()
        statement = statement.offset((page - 1) * page_size).limit(page_size)
        return self.session.exec(statement).all(), total
    
    def get_by_id(self, id: int):
        return self.session.get({Module}, id)
    
    def create(self, **kwargs):
        obj = {Module}(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def update(self, id: int, update_data: dict):
        obj = self.session.get({Module}, id)
        if obj:
            for key, value in update_data.items():
                if value is not None:
                    setattr(obj, key, value)
            self.session.commit()
            self.session.refresh(obj)
        return obj
    
    def delete(self, id: int):
        obj = self.session.get({Module}, id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
```

### Model 层
```python
# {module}.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class {Module}(SQLModel, table=True):
    __tablename__ = "{module}"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="名称")
    status: int = Field(default=1, description="状态：0-禁用，1-启用")
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)
```

### Schema 层
```python
# {Module}Schema.py
from typing import Optional
from pydantic import BaseModel

class {Module}Base(BaseModel):
    name: str
    status: Optional[int] = 1

class {Module}Create({Module}Base):
    pass

class {Module}Update({Module}Base):
    id: int

class {Module}Query(BaseModel):
    page: int = 1
    pageSize: int = 10
    name: Optional[str] = None
    status: Optional[int] = None
```

---

## 前端 Vue 3 组件

### 列表页模板
```vue
<template>
  <div class="module-list">
    <el-card>
      <!-- 搜索区域 -->
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="名称">
          <el-input v-model="searchForm.name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 操作按钮 -->
      <div class="mb-4">
        <el-button type="primary" @click="handleAdd">新增</el-button>
      </div>
      
      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @current-change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, deleteById } from './module.js'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ name: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({ ...searchForm, page: pagination.page, pageSize: pagination.pageSize })
    tableData.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; loadData() }
const handleReset = () => { Object.assign(searchForm, { name: '' }); handleSearch() }
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示')
  await deleteById(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => loadData())
</script>
```

### 表单弹窗模板
```vue
<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑' : '新增'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入名称" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="formData.status" placeholder="请选择状态">
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { insert, update, queryById } from './module.js'

const props = defineProps({
  modelValue: Boolean,
  editId: [Number, String]
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.editId)
const loading = ref(false)
const formRef = ref()

const initialForm = { name: '', status: 1 }
const formData = reactive({ ...initialForm })

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

// 编辑时加载数据
const loadData = async () => {
  if (props.editId) {
    const res = await queryById(props.editId)
    Object.assign(formData, res.data)
  }
}

// 提交表单
const handleSubmit = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    if (isEdit.value) {
      await update({ ...formData, id: props.editId })
      ElMessage.success('更新成功')
    } else {
      await insert(formData)
      ElMessage.success('新增成功')
    }
    emit('success')
    handleClose()
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
  Object.assign(formData, initialForm)
  formRef.value?.resetFields()
}

// 打开时加载数据
defineExpose({ loadData })
</script>
```

### 列表页调用表单示例
```vue
<script setup>
// 在列表页中使用表单弹窗
import { ref } from 'vue'
import ModuleForm from './ModuleForm.vue'

const formVisible = ref(false)
const editId = ref(null)

const handleAdd = () => {
  editId.value = null
  formVisible.value = true
}

const handleEdit = (row) => {
  editId.value = row.id
  formVisible.value = true
}

const handleFormSuccess = () => {
  loadData() // 刷新列表
}
</script>

<template>
  <!-- 在列表页底部添加 -->
  <ModuleForm
    v-model="formVisible"
    :edit-id="editId"
    @success="handleFormSuccess"
  />
</template>
```

---

### API 接口模板
```javascript
// {module}.js
import axios from '@/axios'

export const queryByPage = (data) => axios.post(`/api/{Module}/queryByPage`, data)
export const queryById = (id) => axios.get(`/api/{Module}/queryById`, { params: { id } })
export const insert = (data) => axios.post(`/api/{Module}/insert`, data)
export const update = (data) => axios.put(`/api/{Module}/update`, data)
export const deleteById = (id) => axios.delete(`/api/{Module}/delete`, { params: { id } })
```
