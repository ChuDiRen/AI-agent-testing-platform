<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="测试类型">
        <el-select v-model="searchForm.test_type" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="API" value="API" />
          <el-option label="Web" value="Web" />
          <el-option label="App" value="App" />
          <el-option label="通用" value="通用" />
        </el-select>
      </el-form-item>
      <el-form-item label="模板类型">
        <el-select v-model="searchForm.template_type" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="system" value="system" />
          <el-option label="user" value="user" />
          <el-option label="assistant" value="assistant" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="已激活" :value="true" />
          <el-option label="已停用" :value="false" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="提示词模板管理"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      v-model:pagination="paginationModel"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增模板
        </el-button>
      </template>

      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="name" label="模板名称" min-width="200" />
      <el-table-column prop="template_type" label="模板类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getTemplateTypeColor(row.template_type)">
            {{ row.template_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="test_type" label="测试类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.test_type">{{ row.test_type }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="模板内容" min-width="300">
        <template #default="{ row }">
          <el-tooltip placement="top-start" :show-after="300" effect="light">
            <template #content>
              <div class="tooltip-content">{{ row.content }}</div>
            </template>
            <span class="content-text">{{ truncateContent(row.content) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '已激活' : '已停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="240" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleToggle(row)">
            {{ row.is_active ? '停用' : '激活' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 表单对话框组件 -->
    <PromptTemplateForm 
      v-model="dialogVisible" 
      :formData="formData"
      :viewMode="viewMode"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, toggleActive } from './prompttemplate'
import PromptTemplateForm from './PromptTemplateForm.vue'
import BaseSearch from '@/components/BaseSearch/index.vue'
import BaseTable from '@/components/BaseTable/index.vue'

// 搜索表单
const searchForm = reactive({
  test_type: '',
  template_type: '',
  is_active: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 分页模型（适配 BaseTable）
const paginationModel = computed({
  get: () => ({ page: pagination.page, limit: pagination.page_size }),
  set: (val) => {
    pagination.page = val.page
    pagination.page_size = val.limit
  }
})

// 对话框控制
const dialogVisible = ref(false)
const formData = ref({})
const viewMode = ref(false)

// 模板类型颜色
const getTemplateTypeColor = (type) => {
  const colorMap = {
    'system': '',
    'user': 'success',
    'assistant': 'warning',
    'analyzer': 'primary',
    'designer': 'success',
    'writer': 'warning',
    'reviewer': 'danger'
  }
  return colorMap[type] || 'info'
}

// 截断内容显示
const truncateContent = (content) => {
  if (!content) return '-'
  // 移除多余空白和换行，只显示前100个字符
  const cleaned = content.replace(/\s+/g, ' ').trim()
  if (cleaned.length <= 100) return cleaned
  return cleaned.substring(0, 100) + '...'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.test_type && { test_type: searchForm.test_type }),
      ...(searchForm.template_type && { template_type: searchForm.template_type }),
      ...(searchForm.is_active !== '' && { is_active: searchForm.is_active })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.test_type = ''
  searchForm.template_type = ''
  searchForm.is_active = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  viewMode.value = false
  formData.value = {}
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  viewMode.value = true
  formData.value = { ...row }
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  viewMode.value = false
  formData.value = { ...row }
  dialogVisible.value = true
}

// 表单提交成功回调
const handleFormSuccess = () => {
  loadData()
}

// 切换激活/停用
const handleToggle = async (row) => {
  try {
    const res = await toggleActive(row.id)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || res.data.message)
      loadData()
    } else {
      ElMessage.error(res.data.msg || res.data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除模板"${row.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteData(row.id)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}



// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.content-text {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
  cursor: pointer;
}

.tooltip-content {
  max-width: 500px;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 13px;
  line-height: 1.6;
}
</style>

