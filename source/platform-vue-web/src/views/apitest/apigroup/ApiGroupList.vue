<template>
  <div class="api-group-container">
    <el-card>
      <template #header>
        <div class="header">
          <span>接口分组管理</span>
          <el-button type="primary" @click="handleAdd" v-if="hasPermission('api_group:add')">新增分组</el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="queryForm.project_id" placeholder="请选择项目" clearable>
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分组名称">
          <el-input v-model="queryForm.group_name" placeholder="分组名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="group_name" label="分组名称" show-overflow-tooltip />
        <el-table-column prop="project_name" label="所属项目" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="api_count" label="接口数量" width="100" />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleView(scope.row)" v-if="hasPermission('api_group:view')">查看</el-button>
            <el-button type="warning" size="small" @click="handleEdit(scope.row)" v-if="hasPermission('api_group:edit')">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)" v-if="hasPermission('api_group:delete')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryForm.page"
        v-model:page-size="queryForm.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="formData.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分组名称" prop="group_name">
          <el-input v-model="formData.group_name" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="父级分组" prop="parent_id">
          <el-select v-model="formData.parent_id" placeholder="请选择父级分组（可选）" clearable style="width: 100%">
            <el-option label="无" :value="null" />
            <el-option
              v-for="group in groupList"
              :key="group.id"
              :label="group.group_name"
              :value="group.id"
              :disabled="group.id === formData.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="formData.sort" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="分组详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="分组名称">{{ currentRow.group_name }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ currentRow.project_name }}</el-descriptions-item>
        <el-descriptions-item label="父级分组">{{ currentRow.parent_name || '无' }}</el-descriptions-item>
        <el-descriptions-item label="排序">{{ currentRow.sort }}</el-descriptions-item>
        <el-descriptions-item label="接口数量">{{ currentRow.api_count }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentRow.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(currentRow.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="修改时间">{{ formatDateTime(currentRow.modify_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryGroupByPage, getGroupById, createGroup, updateGroup, deleteGroup } from './apiGroup.js'
import { queryByPage as queryProjectByPage } from '../project/ApiProject.js'  // 修复：使用正确的导出名称
import { formatDateTime } from '~/utils/timeFormatter'

// 权限检查
const hasPermission = (permission) => {
  // TODO: 实现实际的权限检查逻辑
  return true
}

// 查询表单
const queryForm = ref({
  project_id: '',
  group_name: '',
  page: 1,
  pageSize: 10
})

// 表格数据
const tableData = ref([])
const total = ref(0)
const loading = ref(false)

// 项目列表
const projectList = ref([])

// 分组列表（用于父级分组选择）
const groupList = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const viewDialogVisible = ref(false)
const currentRow = ref({})

// 表单数据
const formData = ref({
  id: null,
  project_id: '',
  group_name: '',
  parent_id: null,
  sort: 0,
  description: ''
})

const formRef = ref(null)

// 表单验证规则
const formRules = {
  project_id: [{ required: true, message: '请选择所属项目', trigger: 'change' }],
  group_name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryProjectByPage({ page: 1, pageSize: 1000 })
    if (res.code === 200) {
      projectList.value = res.data.list || []
    }
  } catch (error) {
    console.error('加载项目列表失败', error)
  }
}

// 加载分组列表（用于父级选择）
const loadGroups = async () => {
  try {
    const res = await queryGroupByPage({ page: 1, pageSize: 1000 })
    if (res.code === 200) {
      groupList.value = res.data.list || []
    }
  } catch (error) {
    console.error('加载分组列表失败', error)
  }
}

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await queryGroupByPage({
      ...queryForm.value,
      project_id: queryForm.value.project_id || null
    })
    if (res.code === 200) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.msg || '查询失败')
    }
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  queryForm.value = {
    project_id: '',
    group_name: '',
    page: 1,
    pageSize: 10
  }
  handleQuery()
}

// 新增
const handleAdd = () => {
  formData.value = {
    id: null,
    project_id: '',
    group_name: '',
    parent_id: null,
    sort: 0,
    description: ''
  }
  dialogTitle.value = '新增分组'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  formData.value = { ...row }
  dialogTitle.value = '编辑分组'
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  currentRow.value = { ...row }
  viewDialogVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该分组吗？删除后分组下的接口将移至未分组。', '提示', {
      type: 'warning'
    })

    const res = await deleteGroup(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      handleQuery()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let res
        if (formData.value.id) {
          res = await updateGroup(formData.value.id, formData.value)
        } else {
          res = await createGroup(formData.value)
        }

        if (res.code === 200) {
          ElMessage.success(formData.value.id ? '修改成功' : '新增成功')
          dialogVisible.value = false
          handleQuery()
        } else {
          ElMessage.error(res.msg || '操作失败')
        }
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadProjects()
  loadGroups()
  handleQuery()
})
</script>

<style scoped lang="scss">
.api-group-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

