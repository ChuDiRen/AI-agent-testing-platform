<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>AI模型管理</h3>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增模型
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="提供商">
          <el-select v-model="searchForm.provider" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_enabled" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="已启用" :value="true" />
            <el-option label="已禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      <!-- END 搜索表单 -->

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" style="width: 100%" max-height="500">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="model_name" label="模型名称" min-width="150" />
        <el-table-column prop="model_code" label="模型代码" min-width="150" />
        <el-table-column prop="provider" label="提供商" width="120" />
        <el-table-column prop="api_url" label="API地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_enabled" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'">
              {{ row.is_enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" icon="el-icon-edit" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" icon="el-icon-connection" @click="handleTest(row)">测试连接</el-button>
            <el-button link type="primary"
              :icon="row.is_enabled ? 'el-icon-circle-close' : 'el-icon-circle-check'"
              @click="handleToggle(row)">
              {{ row.is_enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button link type="danger" icon="el-icon-delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
      <!-- END 分页 -->
    </el-card>

    <!-- 表单对话框组件 -->
    <AiModelForm 
      v-model="dialogVisible" 
      :formData="formData"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, testConnection, toggleStatus } from './aimodel'
import AiModelForm from './AiModelForm.vue'

// 搜索表单
const searchForm = reactive({
  provider: '',
  is_enabled: ''
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

// 提供商列表
const providers = ref([])

// 对话框控制
const dialogVisible = ref(false)
const formData = ref({})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.provider && { provider: searchForm.provider }),
      ...(searchForm.is_enabled !== '' && { is_enabled: searchForm.is_enabled })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data
      pagination.total = res.data.total
      // 提取提供商列表
      const providerSet = new Set(res.data.data.map(item => item.provider))
      providers.value = Array.from(providerSet)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 提供商列表已在loadData中提取

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.provider = ''
  searchForm.is_enabled = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  formData.value = {}
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  formData.value = { ...row }
  dialogVisible.value = true
}

// 表单提交成功回调
const handleFormSuccess = () => {
  loadData()
}

// 测试连接
const handleTest = async (row) => {
  const loading = ElMessage.loading('正在测试连接...')
  try {
    const res = await testConnection(row.id)
    loading.close()
    if (res.data.code === 200) {
      ElMessage.success('连接测试成功！')
    } else {
      ElMessage.error(res.data.message || '连接测试失败')
    }
  } catch (error) {
    loading.close()
    ElMessage.error('连接测试失败')
  }
}

// 切换启用/禁用
const handleToggle = async (row) => {
  try {
    const res = await toggleStatus(row.id)
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
  ElMessageBox.confirm(`确定要删除模型"${row.model_name}"吗？`, '提示', {
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
</style>

